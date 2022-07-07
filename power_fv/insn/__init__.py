from operator import attrgetter

from amaranth import *
from amaranth.asserts import AnyConst
from amaranth.hdl.ast import ValueCastable, Value


__all__ = ["InsnField", "WordInsn"]


class InsnField:
    def __init__(self, value=None):
        self.value = value

    @property
    def shape(self):
        return self._shape

    @property
    def offset(self):
        return self._offset

    @property
    def name(self):
        return self._name

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if value is not None and not isinstance(value, int):
            raise TypeError("Field value must be an integer, not {!r}"
                            .format(value))
        self._value = value

    def as_const(self):
        if self.value is not None:
            return Const(self.value, self.shape)
        else:
            return AnyConst(self.shape)


class WordInsn(ValueCastable):
    SIZE = 32

    def __init__(self):
        value_map   = {}
        field_map   = {}
        curr_offset = 0

        for field in sorted(self.fields, key=attrgetter('offset')):
            if not isinstance(field, InsnField):
                raise TypeError("Field must be an instance of InsnField, not {!r}"
                                .format(field))
            if field.name in field_map:
                raise ValueError("Duplicate field name '{}'".format(field.name))
            if curr_offset > field.offset:
                raise ValueError("Field '{}' at offset {} overlaps with its predecessor"
                                 .format(field.name, field.offset))

            # Add undefined bits located between this field and its predecessor.
            if curr_offset < field.offset:
                undef_bits = AnyConst(unsigned(field.offset - curr_offset))
                value_map[curr_offset] = undef_bits

            value_map[field.offset] = field.as_const()
            field_map[field.name  ] = field

            curr_offset = field.offset + field.shape.width

            if curr_offset > self.SIZE:
                raise ValueError

        # Add undefined bits located after the last field.
        if curr_offset < self.SIZE:
            undef_bits = AnyConst(unsigned(self.SIZE - curr_offset))
            value_map[curr_offset] = undef_bits

        self.field_map = field_map
        self.value_map = value_map

    @property
    def fields(self):
        return self._fields

    def __getattr__(self, name):
        return self[name]

    def __getitem__(self, item):
        if isinstance(item, str):
            try:
                field = self.field_map[item]
            except KeyError:
                raise AttributeError("WordInsn {!r} does not have a field '{}'"
                                     .format(self, item))
            value = self.value_map[field.offset]
            return value
        else:
            try:
                return Value.__getitem__(self, item)
            except KeyError:
                raise AttributeError("WordInsn {!r} does not have a field '{}'"
                                     .format(self, item))

    @ValueCastable.lowermethod
    def as_value(self):
        value = Cat(v for o, v in sorted(self.value_map.items(), reverse=True))
        assert len(value) == self.SIZE
        return value

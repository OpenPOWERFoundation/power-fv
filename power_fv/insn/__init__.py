from operator import attrgetter

from amaranth import *


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


class WordInsn(Record):
    SIZE = 32

    def __init__(self, name=None, src_loc_at=0):
        curr_offset = 0
        layout      = []
        pattern     = ""

        for field in sorted(self._fields, key=attrgetter("offset")):
            if not isinstance(field, InsnField):
                raise TypeError("Field must be an instance of InsnField, not {!r}"
                                .format(field))
            if curr_offset > field.offset:
                raise ValueError("Field '{}' at offset {} overlaps with its predecessor"
                                 .format(field.name, field.offset))

            # Add undefined bits located between this field and its predecessor.
            if curr_offset < field.offset:
                undef_bits = field.offset - curr_offset
                layout.append((f"_{curr_offset}", unsigned(undef_bits)))
                pattern += "-" * undef_bits

            layout.append((field.name, field.shape))
            if field.value is not None:
                pattern += "{:0{}b}".format(field.value, field.shape.width)
            else:
                pattern += "-" * field.shape.width

            curr_offset = field.offset + field.shape.width

            if curr_offset > self.SIZE:
                raise ValueError

        # Add undefined bits located after the last field.
        if curr_offset < self.SIZE:
            undef_bits = self.SIZE - curr_offset
            layout.append((f"_{curr_offset}", unsigned(undef_bits)))
            pattern += "-" * undef_bits

        self._pattern = pattern
        super().__init__(reversed(layout), name=name, src_loc_at=1 + src_loc_at)

    @property
    def pattern(self):
        return self._pattern

    def is_valid(self):
        return self.as_value().matches(self.pattern)

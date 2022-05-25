from amaranth import *
from amaranth.asserts import AnyConst
from amaranth.hdl.ast import ValueCastable


__all__ = ["Instruction_I", "Instruction_B", "Instruction_XL_bc", "Instruction_XL_crl"]


class Instruction_I(ValueCastable):
    po = None
    li = None
    aa = None
    lk = None

    def __init_subclass__(cls, *, po, aa, lk):
        cls.po = Const(po, unsigned(6))
        cls.aa = Const(aa, 1)
        cls.lk = Const(lk, 1)

    def __init__(self):
        self.li = AnyConst(signed(24))

    @ValueCastable.lowermethod
    def as_value(self):
        return Cat(self.lk, self.aa, self.li, self.po)


class Instruction_B(ValueCastable):
    po = None
    bo = None
    bi = None
    bd = None
    aa = None
    lk = None

    def __init_subclass__(cls, *, po, aa, lk):
        cls.po = Const(po, unsigned(6))
        cls.aa = Const(aa, 1)
        cls.lk = Const(lk, 1)

    def __init__(self):
        self.bo = AnyConst(unsigned( 5))
        self.bi = AnyConst(unsigned( 5))
        self.bd = AnyConst(  signed(14))

    @ValueCastable.lowermethod
    def as_value(self):
        return Cat(self.lk, self.aa, self.bd, self.bi, self.bo, self.po)


class Instruction_XL_bc(ValueCastable):
    po = None
    bo = None
    bi = None
    _0 = None
    bh = None
    xo = None
    lk = None

    def __init_subclass__(cls, *, po, xo, lk):
        cls.po = Const(po, unsigned( 6))
        cls.xo = Const(xo, unsigned(10))
        cls.lk = Const(1)

    def __init__(self):
        self.bo = AnyConst(unsigned(5))
        self.bi = AnyConst(unsigned(5))
        self._0 = AnyConst(unsigned(3))
        self.bh = AnyConst(unsigned(2))

    @ValueCastable.lowermethod
    def as_value(self):
        return Cat(self.lk, self.xo, self.bh, self._0, self.bi, self.bo, self.po)


class Instruction_XL_crl(ValueCastable):
    po = None
    bt = None
    ba = None
    bb = None
    xo = None
    _0 = None

    def __init_subclass__(cls, *, po, xo):
        cls.po = Const(po, unsigned( 6))
        cls.xo = Const(xo, unsigned(10))

    def __init__(self):
        self.bt = AnyConst(unsigned(5))
        self.ba = AnyConst(unsigned(5))
        self.bb = AnyConst(unsigned(5))
        self._0 = AnyConst(unsigned(1))

    @ValueCastable.lowermethod
    def as_value(self):
        return Cat(self._0, self.xo, self.bb, self.ba, self.bt, self.po)
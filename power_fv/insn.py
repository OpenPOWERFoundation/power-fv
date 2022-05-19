from amaranth import *
from amaranth.asserts import AnyConst
from amaranth.hdl.ast import ValueCastable


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


class Instruction_XL_b(ValueCastable):
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


class B      (Instruction_I, po=18, aa=0, lk=0): pass
class BA     (Instruction_I, po=18, aa=1, lk=0): pass
class BL     (Instruction_I, po=18, aa=0, lk=1): pass
class BLA    (Instruction_I, po=18, aa=1, lk=1): pass

class BC     (Instruction_B, po=16, aa=0, lk=0): pass
class BCA    (Instruction_B, po=16, aa=1, lk=0): pass
class BCL    (Instruction_B, po=16, aa=0, lk=1): pass
class BCLA   (Instruction_B, po=16, aa=1, lk=1): pass

class BCLR   (Instruction_XL_b, po=19, xo= 16, lk=0): pass
class BCLRL  (Instruction_XL_b, po=19, xo= 16, lk=1): pass
class BCCTR  (Instruction_XL_b, po=19, xo=528, lk=0): pass
class BCCTRL (Instruction_XL_b, po=19, xo=528, lk=1): pass
class BCTAR  (Instruction_XL_b, po=19, xo=560, lk=0): pass
class BCTARL (Instruction_XL_b, po=19, xo=560, lk=1): pass

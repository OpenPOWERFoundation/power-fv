from amaranth import *
from amaranth.asserts import AnyConst
from amaranth.hdl.ast import ValueCastable


__all__ = [
    "Instruction_I",
    "Instruction_B",
    "Instruction_D_add", "Instruction_D_cmp",
    "Instruction_DX",
    "Instruction_X_cmp",
    "Instruction_XL_bc", "Instruction_XL_crl", "Instruction_XL_crf",
    "Instruction_XFX_spr",
    "Instruction_XO",
    "Instruction_Z23_add",
]


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


class Instruction_XL_crf(ValueCastable):
    po  = None
    bf  = None
    _0  = None
    bfa = None
    _1  = None
    _2  = None
    xo  = None
    _3  = None

    def __init_subclass__(cls, *, po, xo):
        cls.po = Const(po, unsigned( 6))
        cls.xo = Const(xo, unsigned(10))

    def __init__(self):
        self.bf  = AnyConst(unsigned(3))
        self._0  = AnyConst(unsigned(2))
        self.bfa = AnyConst(unsigned(3))
        self._1  = AnyConst(unsigned(2))
        self._2  = AnyConst(unsigned(5))
        self._3  = AnyConst(unsigned(1))

    @ValueCastable.lowermethod
    def as_value(self):
        return Cat(self._3, self.xo, self._2, self._1, self.bfa, self._0, self.bf, self.po)


class Instruction_D_add(ValueCastable):
    po = None
    rt = None
    ra = None
    _i = None

    def __init_subclass__(cls, *, po):
        cls.po = Const(po, unsigned(6))

    def __init__(self):
        self.rt = AnyConst(unsigned(5))
        self.ra = AnyConst(unsigned(5))
        self._i = AnyConst(16)

    @property
    def si(self):
        return self._i.as_signed()

    def ui(self):
        return self._i.as_unsigned()

    @ValueCastable.lowermethod
    def as_value(self):
        return Cat(self._i, self.ra, self.rt, self.po)


class Instruction_D_cmp(ValueCastable):
    po = None
    bf = None
    _0 = None
    l  = None
    ra = None
    _i = None

    def __init_subclass__(cls, *, po):
        cls.po = Const(po, unsigned(6))

    def __init__(self):
        self.bf = AnyConst(unsigned(3))
        self._0 = AnyConst(unsigned(1))
        self.l  = AnyConst(unsigned(1))
        self.ra = AnyConst(unsigned(5))
        self._i = AnyConst(16)

    @property
    def si(self):
        return self._i.as_signed()

    def ui(self):
        return self._i.as_unsigned()

    @ValueCastable.lowermethod
    def as_value(self):
        return Cat(self._i, self.ra, self.l, self._0, self.bf, self.po)


class Instruction_DX(ValueCastable):
    po = None
    rt = None
    d1 = None
    d0 = None
    xo = None
    d2 = None

    def __init_subclass__(cls, *, po, xo):
        cls.po = Const(po, unsigned(6))
        cls.xo = Const(xo, unsigned(5))

    def __init__(self):
        self.rt = AnyConst(unsigned( 5))
        self.d1 = AnyConst(unsigned( 5))
        self.d0 = AnyConst(unsigned(10))
        self.d2 = AnyConst(unsigned( 1))

    @ValueCastable.lowermethod
    def as_value(self):
        return Cat(self.d2, self.xo, self.d0, self.d1, self.rt, self.po)


class Instruction_X_cmp(ValueCastable):
    po = None
    bf = None
    _0 = None
    l  = None
    ra = None
    rb = None
    xo = None
    _1 = None

    def __init_subclass__(cls, *, po, xo):
        cls.po = Const(po, unsigned( 6))
        cls.xo = Const(xo, unsigned(10))

    def __init__(self):
        self.bf = AnyConst(unsigned(3))
        self._0 = AnyConst(unsigned(1))
        self.l  = AnyConst(unsigned(1))
        self.ra = AnyConst(unsigned(5))
        self.rb = AnyConst(unsigned(5))
        self._1 = AnyConst(unsigned(1))

    @ValueCastable.lowermethod
    def as_value(self):
        return Cat(self._1, self.xo, self.rb, self.ra, self.l, self._0, self.bf, self.po)


class Instruction_XFX_spr(ValueCastable):
    po   = None
    _gpr = None
    spr  = None
    xo   = None
    _0   = None

    def __init_subclass__(cls, *, po, xo):
        cls.po = Const(po, unsigned( 6))
        cls.xo = Const(xo, unsigned(10))

    def __init__(self):
        self._gpr = AnyConst(unsigned( 5))
        self.spr  = AnyConst(unsigned(10))
        self._0   = AnyConst(unsigned( 1))

    @property
    def rs(self):
        return self._gpr

    @property
    def rt(self):
        return self._gpr

    @ValueCastable.lowermethod
    def as_value(self):
        return Cat(self._0, self.xo, self.spr, self._gpr, self.po)


class Instruction_XO(ValueCastable):
    po = None
    rt = None
    ra = None
    rb = None
    oe = None
    xo = None
    rc = None

    def __init_subclass__(cls, *, po, xo, oe=None, rc=None):
        cls.po = Const(po, unsigned(6))
        cls.xo = Const(xo, unsigned(9))
        if oe is not None:
            cls.oe = Const(oe, unsigned(1))
        if rc is not None:
            cls.rc = Const(rc, unsigned(1))

    def __init__(self):
        self.rt = AnyConst(unsigned(5))
        self.ra = AnyConst(unsigned(5))
        self.rb = AnyConst(unsigned(5))
        if self.oe is None:
            self.oe = AnyConst(unsigned(1))
        if self.rc is None:
            self.rc = AnyConst(unsigned(1))

    @ValueCastable.lowermethod
    def as_value(self):
        return Cat(self.rc, self.xo, self.oe, self.rb, self.ra, self.rt, self.po)


class Instruction_Z23_add(ValueCastable):
    po = None
    rt = None
    ra = None
    rb = None
    cy = None
    xo = None
    _0 = None

    def __init_subclass__(cls, *, po, xo, cy):
        cls.po = Const(po, unsigned(6))
        cls.cy = Const(cy, unsigned(2))
        cls.xo = Const(xo, unsigned(8))

    def __init__(self):
        self.rt = AnyConst(unsigned(5))
        self.ra = AnyConst(unsigned(5))
        self.rb = AnyConst(unsigned(5))
        self._0 = AnyConst(unsigned(1))

    @ValueCastable.lowermethod
    def as_value(self):
        return Cat(self._0, self.xo, self.cy, self.rb, self.ra, self.rt, self.po)

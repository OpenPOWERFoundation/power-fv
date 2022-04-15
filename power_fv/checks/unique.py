from amaranth import *
from amaranth.asserts import *

from .. import pfv


__all__ = ["UniquenessCheck", "UniquenessCover"]


class UniquenessCheck(Elaboratable):
    """Uniqueness check.

    Check that the core cannot retire two instructions with the same `pfv.order` identifier.
    """
    def __init__(self):
        self.pre  = Signal()
        self.post = Signal()
        self.pfv  = pfv.Interface()

    def elaborate(self, platform):
        m = Module()

        spec_order = AnyConst(self.pfv.order.shape())
        duplicate  = Signal()

        with m.If(self.pre):
            m.d.sync += [
                Assume(self.pfv.stb),
                Assume(spec_order == self.pfv.order),
                Assume(~duplicate),
            ]
        with m.Elif(self.pfv.stb & (self.pfv.order == spec_order)):
            m.d.sync += duplicate.eq(1)

        with m.If(self.post):
            m.d.sync += Assert(~duplicate)

        return m


class UniquenessCover(Elaboratable):
    def __init__(self):
        self.pre  = Signal()
        self.post = Signal()
        self.pfv  = pfv.Interface()

    def elaborate(self, platform):
        m = Module()

        insn_count = Signal(range(4))

        with m.If(self.pfv.stb):
            m.d.sync += insn_count.eq(insn_count + 1)

        cover_1 = Signal()
        cover_2 = Signal()

        m.d.comb += [
            cover_1.eq(insn_count == 1),
            cover_2.eq(insn_count == 2),

            Cover(cover_1),
            Cover(cover_2),
        ]

        return m

from amaranth import *
from amaranth.asserts import *

from .. import pfv


__all__ = ["IAForwardCheck", "IAForwardCover"]


class IAForwardCheck(Elaboratable):
    """IA forward check.

    Given two instructions retiring in order, check that the NIA of the first matches the CIA
    of the second.
    """
    def __init__(self):
        self.pre  = Signal()
        self.post = Signal()
        self.pfv  = pfv.Interface()

    def elaborate(self, platform):
        m = Module()

        pred_order = AnyConst(self.pfv.order.width)
        pred_stb   = Signal()
        pred_nia   = Signal.like(self.pfv.nia)

        with m.If(self.pfv.stb & (self.pfv.order == pred_order)):
            m.d.sync += [
                pred_stb.eq(1),
                pred_nia.eq(self.pfv.nia)
            ]

        with m.If(self.post):
            m.d.sync += [
                Assume(self.pfv.stb),
                Assume(self.pfv.order == pred_order + 1),
                Assume(self.pfv.order > 0),
                Assert(pred_stb.implies(self.pfv.cia == pred_nia)),
            ]

        return m


class IAForwardCover(Elaboratable):
    def __init__(self):
        self.pre  = Signal()
        self.post = Signal()
        self.pfv  = pfv.Interface()

    def elaborate(self, platform):
        m = Module()

        insn_count  = Signal(range(4))
        pred_branch = Signal()

        with m.If(self.pfv.stb):
            m.d.sync += [
                insn_count .eq(insn_count + 1),
                pred_branch.eq(self.pfv.nia != (self.pfv.cia + 4)),
            ]

        cover_1 = Signal()
        cover_2 = Signal()

        m.d.comb += [
            cover_1.eq((insn_count > 1) & pred_branch),
            cover_2.eq(cover_1 & self.pfv.stb),

            Cover(cover_1),
            Cover(cover_2),
        ]

        return m

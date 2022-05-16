from amaranth import *
from amaranth.asserts import *

from .. import pfv


__all__ = ["Check"]


class Check(Elaboratable):
    """IA forward check.

    Given two instructions retiring in order, check that the NIA of the first matches the CIA
    of the second.
    """
    def __init__(self):
        self.pfv  = pfv.Interface()
        self.trig = Record([
            ("pre",  1),
            ("post", 1),
        ])

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

        with m.If(self.trig.post):
            m.d.sync += [
                Assume(self.pfv.stb),
                Assume(self.pfv.order == pred_order + 1),
                Assume(self.pfv.order > 0),
                Assert(pred_stb.implies(self.pfv.cia == pred_nia)),
            ]

        return m

from amaranth import *
from amaranth.asserts import *

from .. import PowerFVCheck
from ... import pfv, tb


__all__ = ["IAForwardSpec", "IAForwardCheck"]


class IAForwardSpec(Elaboratable):
    """IA forward specification.

    Given two instructions retiring in order, the NIA of the first must match the CIA
    of the second.
    """
    def __init__(self, post):
        self.pfv  = pfv.Interface()
        self.post = tb.Trigger(cycle=post)

    def triggers(self):
        yield self.post

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

        with m.If(self.post.stb):
            m.d.sync += [
                Assume(self.pfv.stb),
                Assume(self.pfv.order == pred_order + 1),
                Assume(self.pfv.order > 0),
                Assert(pred_stb.implies(self.pfv.cia == pred_nia)),
            ]

        return m


class IAForwardCheck(PowerFVCheck, name="cons_ia_fwd"):
    def get_testbench(self, dut, post):
        tb_spec = IAForwardSpec(post)
        tb_top  = tb.Testbench(tb_spec, dut)
        return tb_top

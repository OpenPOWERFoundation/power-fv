from amaranth import *
from amaranth.asserts import *

from power_fv.check import PowerFVCheck
from power_fv.check._timer import Timer


__all__ = ["CIACheck"]


class CIACheck(PowerFVCheck, name=("cia",)):
    """CIA check.

    Given a pair of instructions retiring in order, the CIA of the second must match the NIA
    of the first.
    """

    def testbench(self):
        return CIATestbench(self)


class CIATestbench(Elaboratable):
    def __init__(self, check):
        if not isinstance(check, CIACheck):
            raise TypeError("Check must be an instance of CIACheck, not {!r}"
                            .format(check))
        self.check = check
        self.name  = "cia_tb"

    def elaborate(self, platform):
        m = Module()

        m.submodules.t_post = t_post = Timer(self.check.depth - 1)
        m.submodules.dut    = dut    = self.check.dut

        pred_stb   = Signal()
        pred_order = Signal(unsigned(64))
        pred_nia   = Signal(unsigned(64))

        m.d.comb += pred_order.eq(AnyConst(64))

        with m.If(dut.pfv.stb & (dut.pfv.order == pred_order)):
            m.d.sync += [
                pred_stb.eq(1),
                pred_nia.eq(dut.pfv.nia)
            ]

        with m.If(t_post.zero):
            m.d.comb += [
                Assume(dut.pfv.stb),
                Assume(dut.pfv.order == pred_order + 1),
                Assume(dut.pfv.order > 0),
                Assert(pred_stb.implies(dut.pfv.cia == pred_nia)),
            ]

        return m

from amaranth import *
from amaranth.asserts import *

from power_fv.check import PowerFVCheck
from power_fv.check._timer import Timer


__all__ = ["LivenessCheck"]


class LivenessCheck(PowerFVCheck, name=("liveness",)):
    """Liveness check.

    Checks that a core does not hang for the duration of the bounded-model check.
    """

    def testbench(self):
        return LivenessTestbench(self)


class LivenessTestbench(Elaboratable):
    def __init__(self, check):
        if not isinstance(check, LivenessCheck):
            raise TypeError("Check must be an instance of LivenessCheck, not {!r}"
                            .format(check))
        self.check = check
        self.name  = "liveness_tb"

    def elaborate(self, platform):
        m = Module()

        m.submodules.t_pre  = t_pre  = Timer(self.check.skip  - 1)
        m.submodules.t_post = t_post = Timer(self.check.depth - 1)
        m.submodules.dut    = dut    = self.check.dut

        curr_order   = AnyConst(dut.pfv.order.shape())
        next_order   = curr_order + 1
        next_retired = Signal()

        with m.If(Rose(t_pre.zero)):
            m.d.comb += [
                Assume(dut.pfv.stb),
                Assume(curr_order == dut.pfv.order),
            ]

        with m.Elif(t_pre.zero):
            with m.If(dut.pfv.stb & (dut.pfv.order == next_order)):
                m.d.sync += next_retired.eq(1)

        with m.If(t_post.zero):
            m.d.comb += Assert(next_retired)

        m.d.comb += Assert(~Past(t_post.zero))

        return m

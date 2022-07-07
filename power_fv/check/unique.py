from amaranth import *
from amaranth.asserts import *

from power_fv.check import PowerFVCheck
from power_fv.check._timer import Timer


__all__ = ["UniquenessCheck"]


class UniquenessCheck(PowerFVCheck, name=("unique",)):
    """Uniqueness check.

    Checks that every retired instruction is assigned an unique `pfv.order` value.
    """

    def testbench(self):
        return UniquenessTestbench(self)


class UniquenessTestbench(Elaboratable):
    def __init__(self, check):
        if not isinstance(check, UniquenessCheck):
            raise TypeError("Check must be an instance of UniquenessCheck, not {!r}"
                            .format(check))
        self.check = check
        self.name  = "unique_tb"

    def elaborate(self, platform):
        m = Module()

        m.submodules.t_pre  = t_pre  = Timer(self.check.skip  - 1)
        m.submodules.t_post = t_post = Timer(self.check.depth - 1)
        m.submodules.dut    = dut    = self.check.dut

        spec_order = AnyConst(dut.pfv.order.shape())
        duplicate  = Record([("prev", 1), ("curr", 1)])

        with m.If(Rose(t_pre.zero)):
            m.d.comb += [
                Assume(dut.pfv.stb),
                Assume(dut.pfv.order == spec_order),
                Assert(~duplicate.prev),
                Assert(~duplicate.curr),
            ]

        with m.Elif(t_pre.zero):
            with m.If(dut.pfv.stb & (dut.pfv.order == spec_order)):
                m.d.sync += duplicate.prev.eq(1)
                m.d.comb += duplicate.curr.eq(1)

        with m.If(t_post.zero):
            m.d.comb += [
                Assert(~duplicate.prev),
                Assert(~duplicate.curr),
            ]

        m.d.comb += Assert(~Past(t_post.zero))

        return m

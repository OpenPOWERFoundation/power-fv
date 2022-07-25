from amaranth import *
from amaranth.asserts import *

from power_fv.check import PowerFVCheck
from power_fv.check._timer import Timer


__all__ = ["CausalityCheck"]


class CausalityCheck(PowerFVCheck, name=("causal",)):
    """Causal consistency check.

    Checks that an instruction that writes to a GPR has completed before any subsequent
    instruction (by program order) can read it.
    """

    def testbench(self):
        return CausalityTestbench(self)


class CausalityTestbench(Elaboratable):
    def __init__(self, check):
        if not isinstance(check, CausalityCheck):
            raise TypeError("Check must be an instance of CausalityCheck, not {!r}"
                            .format(check))
        self.check = check
        self.name  = "causal_tb"

    def elaborate(self, platform):
        m = Module()

        m.submodules.t_post = t_post = Timer(self.check.depth - 1)
        m.submodules.dut    = dut    = self.check.dut

        write_order = AnyConst(dut.pfv.order.shape())
        write_index = AnyConst(unsigned(5))
        read_before = Signal()

        gpr_write = Record([("ra", 1), ("rb", 1), ("rs", 1), ("rt", 1)])
        gpr_read  = Record.like(gpr_write)

        m.d.comb += [
            gpr_write.ra.eq(dut.pfv.ra.w_stb & (dut.pfv.ra.index == write_index)),
            gpr_write.rb.eq(dut.pfv.rb.w_stb & (dut.pfv.rb.index == write_index)),
            gpr_write.rs.eq(dut.pfv.rs.w_stb & (dut.pfv.rs.index == write_index)),
            gpr_write.rt.eq(dut.pfv.rt.w_stb & (dut.pfv.rt.index == write_index)),

            gpr_read .ra.eq(dut.pfv.ra.r_stb & (dut.pfv.ra.index == write_index)),
            gpr_read .rb.eq(dut.pfv.rb.r_stb & (dut.pfv.rb.index == write_index)),
            gpr_read .rs.eq(dut.pfv.rs.r_stb & (dut.pfv.rs.index == write_index)),
            gpr_read .rt.eq(dut.pfv.rt.r_stb & (dut.pfv.rt.index == write_index)),
        ]

        with m.If(dut.pfv.stb & (dut.pfv.order > write_order) & ~dut.pfv.skip):
            with m.If(gpr_read.any()):
                m.d.sync += read_before.eq(1)

        with m.If(t_post.zero):
            m.d.comb += [
                Assume(dut.pfv.stb),
                Assume(dut.pfv.order == write_order),
                Assume(~dut.pfv.skip),
                Assume(gpr_write.any()),
                Assert(~read_before),
            ]

        m.d.comb += Assert(~Past(t_post.zero))

        return m

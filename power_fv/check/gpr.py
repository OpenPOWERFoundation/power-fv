from amaranth import *
from amaranth.lib.coding import Encoder
from amaranth.asserts import *

from power_fv.check import PowerFVCheck
from power_fv.check._timer import Timer


__all__ = ["GPRCheck"]


class GPRCheck(PowerFVCheck, name=("gpr",)):
    """GPR consistency check.

    Checks that:
      * reads from a GPR return the last value that was written to it;
      * writes to multiple GPRs by a single instruction (e.g. load with update) do not conflict
        with each other.
    """

    def testbench(self):
        return GPRTestbench(self)


class GPRTestbench(Elaboratable):
    def __init__(self, check):
        if not isinstance(check, GPRCheck):
            raise TypeError("Check must be an instance of GPRCheck, not {!r}"
                            .format(check))
        self.check = check
        self.name  = "gpr_tb"

    def elaborate(self, platform):
        m = Module()

        m.submodules.t_post = t_post = Timer(self.check.depth - 1)
        m.submodules.dut    = dut    = self.check.dut

        spec_order = AnyConst(dut.pfv.order.shape())
        spec_index = AnyConst(unsigned(5))

        gpr_write = Record([("ra", 1), ("rb", 1), ("rs", 1), ("rt", 1)])
        gpr_read  = Record.like(gpr_write)

        m.d.comb += [
            gpr_write.ra.eq(dut.pfv.ra.w_stb & (dut.pfv.ra.index == spec_index)),
            gpr_write.rb.eq(dut.pfv.rb.w_stb & (dut.pfv.rb.index == spec_index)),
            gpr_write.rs.eq(dut.pfv.rs.w_stb & (dut.pfv.rs.index == spec_index)),
            gpr_write.rt.eq(dut.pfv.rt.w_stb & (dut.pfv.rt.index == spec_index)),

            gpr_read .ra.eq(dut.pfv.ra.r_stb & (dut.pfv.ra.index == spec_index)),
            gpr_read .rb.eq(dut.pfv.rb.r_stb & (dut.pfv.rb.index == spec_index)),
            gpr_read .rs.eq(dut.pfv.rs.r_stb & (dut.pfv.rs.index == spec_index)),
            gpr_read .rt.eq(dut.pfv.rt.r_stb & (dut.pfv.rt.index == spec_index)),
        ]

        gpr_conflict = Record([("prev",  1), ("curr", 1)])
        gpr_written  = Record([("prev",  1)])
        gpr_shadow   = Record([("prev", 64)])

        m.submodules.write_enc = write_enc = Encoder(len(gpr_write))
        m.d.comb += write_enc.i.eq(gpr_write)

        with m.If(dut.pfv.stb & write_enc.i.any() & write_enc.n):
            # Write conflict: more then one bit of `gpr_write` is asserted.
            m.d.comb += gpr_conflict.curr.eq(1)
            m.d.sync += gpr_conflict.prev.eq(dut.pfv.order < spec_order)

        with m.If(dut.pfv.stb & (dut.pfv.order < spec_order) & ~dut.pfv.skip):
            with m.If(gpr_write.any()):
                m.d.sync += gpr_written.prev.eq(1)
                with m.If(gpr_write.ra):
                    m.d.sync += gpr_shadow.prev.eq(dut.pfv.ra.w_data)
                with m.If(gpr_write.rb):
                    m.d.sync += gpr_shadow.prev.eq(dut.pfv.rb.w_data)
                with m.If(gpr_write.rs):
                    m.d.sync += gpr_shadow.prev.eq(dut.pfv.rs.w_data)
                with m.If(gpr_write.rt):
                    m.d.sync += gpr_shadow.prev.eq(dut.pfv.rt.w_data)

        with m.If(t_post.zero):
            m.d.comb += [
                Assume(dut.pfv.stb),
                Assume(dut.pfv.order == spec_order),
                Assume(~dut.pfv.skip),
                Assert(~gpr_conflict.curr),
                Assert(~gpr_conflict.prev),
            ]
            with m.If(gpr_written.prev):
                with m.If(gpr_read.ra):
                    m.d.comb += Assert(dut.pfv.ra.r_data == gpr_shadow.prev)
                with m.If(gpr_read.rb):
                    m.d.comb += Assert(dut.pfv.rb.r_data == gpr_shadow.prev)
                with m.If(gpr_read.rs):
                    m.d.comb += Assert(dut.pfv.rs.r_data == gpr_shadow.prev)
                with m.If(gpr_read.rt):
                    m.d.comb += Assert(dut.pfv.rt.r_data == gpr_shadow.prev)

        m.d.comb += Assert(~Past(t_post.zero))

        return m

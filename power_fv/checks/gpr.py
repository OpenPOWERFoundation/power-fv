from amaranth import *
from amaranth.asserts import *

from .. import pfv


__all__ = ["Check"]


class Check(Elaboratable):
    """General Purpose Registers check.

    Checks that reads from GPRs are consistent with the last value that was written to them.
    Also checks that simultaneous writes to multiple GPRs by the same instruction (e.g. a load
    with update) do not target the same register.
    """
    def __init__(self):
        self.pfv  = pfv.Interface()
        self.trig = Record([
            ("pre",  1),
            ("post", 1),
        ])

    def elaborate(self, platform):
        m = Module()

        spec_order     = AnyConst(self.pfv.order.width)
        spec_gpr_index = AnyConst(5)

        gpr_ra_read    = Signal()
        gpr_ra_write   = Signal()
        gpr_rb_read    = Signal()
        gpr_rs_read    = Signal()
        gpr_rt_read    = Signal()
        gpr_rt_write   = Signal()

        gpr_conflict   = Signal()
        gpr_written    = Signal()
        gpr_shadow     = Signal(64)

        m.d.comb += [
            gpr_ra_read .eq(self.pfv.ra.r_stb & (self.pfv.ra.index == spec_gpr_index)),
            gpr_ra_write.eq(self.pfv.ra.w_stb & (self.pfv.ra.index == spec_gpr_index)),
            gpr_rb_read .eq(self.pfv.rb.r_stb & (self.pfv.rb.index == spec_gpr_index)),
            gpr_rs_read .eq(self.pfv.rs.r_stb & (self.pfv.rs.index == spec_gpr_index)),
            gpr_rt_read .eq(self.pfv.rt.r_stb & (self.pfv.rt.index == spec_gpr_index)),
            gpr_rt_write.eq(self.pfv.rt.w_stb & (self.pfv.rt.index == spec_gpr_index)),
        ]

        with m.If(self.pfv.stb & (self.pfv.order <= spec_order)):
            with m.If(gpr_ra_write & gpr_rt_write):
                m.d.sync += gpr_conflict.eq(1)
            with m.If(gpr_ra_write | gpr_rt_write):
                m.d.sync += gpr_written.eq(1)
                with m.If(gpr_ra_write):
                    m.d.sync += gpr_shadow.eq(self.pfv.ra.w_data)
                with m.Else():
                    m.d.sync += gpr_shadow.eq(self.pfv.rt.w_data)

        with m.If(self.trig.post):
            m.d.sync += [
                Assume(Past(self.pfv.stb)),
                Assume(Past(self.pfv.order) == spec_order),
                Assert(gpr_written.implies(~gpr_conflict)),
            ]
            with m.If(gpr_written & Past(gpr_ra_read)):
                m.d.sync += Assert(Past(gpr_shadow) == Past(self.pfv.ra.r_data))
            with m.If(gpr_written & Past(gpr_rb_read)):
                m.d.sync += Assert(Past(gpr_shadow) == Past(self.pfv.rb.r_data))
            with m.If(gpr_written & Past(gpr_rs_read)):
                m.d.sync += Assert(Past(gpr_shadow) == Past(self.pfv.rs.r_data))
            with m.If(gpr_written & Past(gpr_rt_read)):
                m.d.sync += Assert(Past(gpr_shadow) == Past(self.pfv.rt.r_data))

        return m

from amaranth import *
from amaranth.asserts import *

from .. import pfv


__all__ = ["Check"]


class Check(Elaboratable):
    """Special Purpose Registers check.

    Checks that reads from supported SPRs are consistent with the last value that was written to
    them.
    """
    def __init__(self):
        self.pfv  = pfv.Interface()
        self.trig = Record([
            ("pre",  1),
            ("post", 1),
        ])

    def elaborate(self, platform):
        m = Module()

        spec_order = AnyConst(self.pfv.order.width)

        lr_written  = Signal()
        lr_shadow   = Signal(64)
        ctr_written = Signal()
        ctr_shadow  = Signal(64)
        xer_written = Signal()
        xer_shadow  = Signal(64)
        tar_written = Signal()
        tar_shadow  = Signal(64)

        with m.If(self.pfv.stb & (self.pfv.order <= spec_order)):
            with m.If(self.pfv.lr.w_stb):
                m.d.sync += [
                    lr_written.eq(1),
                    lr_shadow .eq(self.pfv.lr.w_data),
                ]
            with m.If(self.pfv.ctr.w_stb):
                m.d.sync += [
                    ctr_written.eq(1),
                    ctr_shadow .eq(self.pfv.ctr.w_data),
                ]
            with m.If(self.pfv.xer.w_stb):
                m.d.sync += [
                    xer_written.eq(1),
                    xer_shadow .eq(self.pfv.xer.w_data),
                ]
            with m.If(self.pfv.tar.w_stb):
                m.d.sync += [
                    tar_written.eq(1),
                    tar_shadow .eq(self.pfv.tar.w_data),
                ]

        with m.If(self.trig.post):
            m.d.sync += [
                Assume(Past(self.pfv.stb)),
                Assume(Past(self.pfv.order) == spec_order),
            ]
            with m.If(lr_written & Past(self.pfv.lr.r_stb)):
                m.d.sync += Assert(Past(lr_shadow) == Past(self.pfv.lr.r_data))
            with m.If(ctr_written & Past(self.pfv.ctr.r_stb)):
                m.d.sync += Assert(Past(ctr_shadow) == Past(self.pfv.ctr.r_data))
            with m.If(xer_written & Past(self.pfv.xer.r_stb)):
                m.d.sync += Assert(Past(xer_shadow) == Past(self.pfv.xer.r_data))
            with m.If(tar_written & Past(self.pfv.tar.r_stb)):
                m.d.sync += Assert(Past(tar_shadow) == Past(self.pfv.tar.r_data))

        return m

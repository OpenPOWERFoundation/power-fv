from amaranth import *
from amaranth.asserts import *

from .. import pfv


__all__ = ["SPRCheck", "SPRCover"]


class SPRCheck(Elaboratable):
    """Special Purpose Registers check.

    Checks that reads from supported SPRs are consistent with the last value that was written to
    them.
    """
    def __init__(self):
        self.pre  = Signal()
        self.post = Signal()
        self.pfv  = pfv.Interface()

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

        with m.If(self.post):
            m.d.sync += [
                Assume(Past(self.pfv.stb)),
                Assume(Past(self.pfv.order) == spec_order),
            ]
            with m.If(Past(self.pfv.lr.r_stb)):
                m.d.sync += Assert(Past(lr_shadow) == Past(self.pfv.lr.r_data))
            with m.If(Past(self.pfv.ctr.r_stb)):
                m.d.sync += Assert(Past(ctr_shadow) == Past(self.pfv.ctr.r_data))
            with m.If(Past(self.pfv.xer.r_stb)):
                m.d.sync += Assert(Past(xer_shadow) == Past(self.pfv.xer.r_data))
            with m.If(Past(self.pfv.tar.r_stb)):
                m.d.sync += Assert(Past(tar_shadow) == Past(self.pfv.tar.r_data))

        return m


class SPRCover(Elaboratable):
    def __init__(self):
        self.pre  = Signal()
        self.post = Signal()
        self.pfv  = pfv.Interface()

    def elaborate(self, platform):
        m = Module()

        insn_count  = Signal(range(4))
        lr_written  = Signal()
        ctr_written = Signal()
        xer_written = Signal()
        tar_written = Signal()

        with m.If(self.pfv.stb):
            m.d.sync += [
                insn_count .eq(insn_count + 1),
                lr_written .eq(self.pfv.lr .w_stb),
                ctr_written.eq(self.pfv.ctr.w_stb),
                xer_written.eq(self.pfv.xer.w_stb),
                tar_written.eq(self.pfv.tar.w_stb),
            ]

        cover_1 = Signal()
        cover_2 = Signal()
        cover_3 = Signal()
        cover_4 = Signal()

        m.d.comb += [
            cover_1.eq((insn_count > 1) & lr_written),
            cover_2.eq((insn_count > 1) & ctr_written),
            cover_3.eq((insn_count > 1) & xer_written),
            cover_4.eq((insn_count > 1) & tar_written),

            Cover(cover_1),
            Cover(cover_2),
            Cover(cover_3),
            Cover(cover_4),
        ]

        return m

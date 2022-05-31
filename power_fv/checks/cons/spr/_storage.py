from collections import OrderedDict

from amaranth import *
from amaranth.asserts import *

from ... import PowerFVCheck
from .... import pfv, tb


__all__ = ["SPRSpec", "SPRCheck"]


class StorageSPRSpec(Elaboratable):
    """Storage SPR specification.

    Checks that reads from supported SPRs return the last value that was written to them.
    """
    def __init__(self, spr_name, spr_reset, post):
        self.spr_name  = spr_name
        self.spr_reset = spr_reset

        self.pfv  = pfv.Interface()
        self.post = tb.Trigger(cycle=post)

    def triggers(self):
        yield self.post

    @property
    def pfv_spr(self):
        return getattr(self.pfv, self.spr_name)

    def elaborate(self, platform):
        m = Module()

        spr = Record([
            ("written", 1),
            ("shadow",  self.pfv_spr.r_data.width),
        ], name=self.spr_name)

        spec_order = AnyConst(self.pfv.order.width)

        with m.If(Initial()):
            m.d.sync += Assume(spr.shadow == self.spr_reset)

        with m.If(self.pfv.stb & (self.pfv.order <= spec_order)):
            with m.If(self.pfv_spr.w_mask.any()):
                m.d.sync += [
                    spr.written.eq(1),
                    spr.shadow .eq((spr.shadow & ~self.pfv_spr.w_mask) | (self.pfv_spr.w_data & self.pfv_spr.w_mask)),
                ]

        with m.If(self.post.stb):
            m.d.sync += [
                Assume(Past(self.pfv.stb)),
                Assume(Past(self.pfv.order) == spec_order),
            ]

            with m.If(spr.written):
                p_spr_r_mask = Past(self.pfv_spr.r_mask)
                p_spr_r_data = Past(self.pfv_spr.r_data)
                p_spr_shadow = Past(spr.shadow)
                m.d.sync += Assert((p_spr_r_data & p_spr_r_mask) == (p_spr_shadow & p_spr_r_mask))

            m.d.sync += Assume(spr.written & Past(self.pfv_spr.r_mask).any()) # FIXME rm

        return m


class StorageSPRCheck(PowerFVCheck, name="_cons_spr_storage"):
    def __init_subclass__(cls, name, spr_name):
        super().__init_subclass__(name)
        cls.spr_name = spr_name

    def get_testbench(self, dut, post, spr_reset=0):
        tb_spec = StorageSPRSpec(self.spr_name, spr_reset, post)
        tb_top  = tb.Testbench(tb_spec, dut)
        return tb_top

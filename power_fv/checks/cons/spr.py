from collections import OrderedDict

from amaranth import *
from amaranth.asserts import *

from .. import PowerFVCheck
from ... import pfv, tb


__all__ = ["SPRSpec", "SPRCheck"]


class SPRSpec(Elaboratable):
    """SPR consistency specification.

    Checks that reads from supported SPRs are the last value that was written to
    them.
    """
    def __init__(self, post):
        self.pfv  = pfv.Interface()
        self.post = tb.Trigger(cycle=post)

    def triggers(self):
        yield self.post

    def elaborate(self, platform):
        m = Module()

        spr_map = OrderedDict()

        for spr_name in ("lr", "ctr", "xer", "tar"):
            spr = Record([
                ("written",  1),
                ("shadow",  64),
            ], name=spr_name)
            spr_map[spr_name] = spr

        spec_order = AnyConst(self.pfv.order.width)

        with m.If(self.pfv.stb & (self.pfv.order <= spec_order)):
            for spr_name, spr in spr_map.items():
                pfv_spr = getattr(self.pfv, spr_name)

                with m.If(pfv_spr.w_stb):
                    m.d.sync += [
                        spr.written.eq(1),
                        spr.shadow .eq(pfv_spr.w_data),
                    ]

        with m.If(self.post.stb):
            m.d.sync += [
                Assume(Past(self.pfv.stb)),
                Assume(Past(self.pfv.order) == spec_order),
            ]

            for spr_name, spr in spr_map.items():
                pfv_spr = getattr(self.pfv, spr_name)

                with m.If(spr.written & Past(pfv_spr.r_stb)):
                    m.d.sync += Assert(Past(spr.shadow) == Past(pfv_spr.r_data))

        return m


class SPRCheck(PowerFVCheck, name="cons_spr"):
    def get_testbench(self, dut, post):
        tb_spec = SPRSpec(post)
        tb_top  = tb.Testbench(tb_spec, dut)
        return tb_top

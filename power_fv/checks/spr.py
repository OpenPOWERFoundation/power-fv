from collections import OrderedDict

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

        with m.If(self.trig.post):
            m.d.sync += [
                Assume(Past(self.pfv.stb)),
                Assume(Past(self.pfv.order) == spec_order),
            ]

            for spr_name, spr in spr_map.items():
                pfv_spr = getattr(self.pfv, spr_name)

                with m.If(spr.written & Past(pfv_spr.r_stb)):
                    m.d.sync += Assert(Past(spr.shadow) == Past(pfv_spr.r_data))

        return m

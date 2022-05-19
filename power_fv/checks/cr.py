from amaranth import *
from amaranth.asserts import *

from .. import pfv


__all__ = ["Check"]


class Check(Elaboratable):
    """Condition Register check.

    Checks that reads from CR fields are consistent with the last value that was written to them.
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

        cr_map = Array(
            Record([
                ("pfv", [
                    ("r_stb",  1),
                    ("r_data", 4),
                    ("w_stb",  1),
                    ("w_data", 4),
                ]),
                ("written", 1),
                ("shadow",  4),
            ], name=f"cr_{i}") for i in range(8)
        )

        cr_written_any = 0

        for i, cr_field in enumerate(cr_map):
            m.d.comb += [
                cr_field.pfv.r_stb .eq(self.pfv.cr.r_stb[i]),
                cr_field.pfv.r_data.eq(self.pfv.cr.r_data.word_select(i, 4)),
                cr_field.pfv.w_stb .eq(self.pfv.cr.w_stb[i]),
                cr_field.pfv.w_data.eq(self.pfv.cr.w_data.word_select(i, 4)),
            ]
            cr_written_any |= cr_field.written

        with m.If(self.pfv.stb & ~self.pfv.intr & (self.pfv.order <= spec_order)):
            for cr_field in cr_map:
                with m.If(cr_field.pfv.w_stb):
                    m.d.sync += [
                        cr_field.written.eq(1),
                        cr_field.shadow .eq(cr_field.pfv.w_data),
                    ]

        with m.If(self.trig.post):
            m.d.sync += [
                Assume(Past(self.pfv.stb)),
                Assume(Past(self.pfv.order) == spec_order),
                Assume(cr_written_any),
            ]
            with m.If(~Past(self.pfv.intr)):
                for cr_field in cr_map:
                    with m.If(Past(cr_field.pfv.r_stb)):
                        m.d.sync += Assert(Past(cr_field.pfv.r_data) == Past(cr_field.shadow))

        return m

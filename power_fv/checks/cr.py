from amaranth import *
from amaranth.asserts import *

from .. import pfv


__all__ = ["CRCheck"]


class CRCheck(Elaboratable):
    """Condition Register check.

    Checks that reads from CR fields are consistent with the last value that was written to them.
    """
    def __init__(self):
        self.pre  = Signal()
        self.post = Signal()
        self.pfv  = pfv.Interface()

    def elaborate(self, platform):
        m = Module()

        spec_order = AnyConst(self.pfv.order.width)

        cr = Array(Record([
            ("written", 1),
            ("shadow",  4),
        ], name=f"cr{i}") for i in range(8))

        cr_written_any = 0

        with m.If(self.pfv.stb & (self.pfv.order <= spec_order)):
            for i, cr_field in enumerate(cr):
                pfv_cr_field = getattr(self.pfv, f"cr{i}")

                with m.If(pfv_cr_field.w_stb):
                    m.d.sync += [
                        cr_field.written.eq(1),
                        cr_field.shadow .eq(pfv_cr_field.w_data),
                    ]

                cr_written_any |= cr_field.written

        with m.If(self.post):
            m.d.sync += [
                Assume(Past(self.pfv.stb)),
                Assume(Past(self.pfv.order) == spec_order),
                Assume(cr_written_any),
            ]

            for i, cr_field in enumerate(cr):
                pfv_cr_field = getattr(self.pfv, f"cr{i}")

                with m.If(Past(pfv_cr_field.r_stb)):
                    m.d.sync += Assert(Past(pfv_cr_field.r_data) == Past(cr_field.shadow))

        return m

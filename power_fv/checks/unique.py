from amaranth import *
from amaranth.asserts import *

from .. import pfv


__all__ = ["Check"]


class Check(Elaboratable):
    """Uniqueness check.

    Check that the core cannot retire two instructions with the same `pfv.order` identifier.
    """
    def __init__(self):
        self.pfv  = pfv.Interface()
        self.trig = Record([
            ("pre",  1),
            ("post", 1),
        ])

    def elaborate(self, platform):
        m = Module()

        spec_order = AnyConst(self.pfv.order.shape())
        duplicate  = Signal()

        with m.If(self.trig.pre):
            m.d.sync += [
                Assume(self.pfv.stb),
                Assume(spec_order == self.pfv.order),
                Assume(~duplicate),
            ]
        with m.Elif(self.pfv.stb & (self.pfv.order == spec_order)):
            m.d.sync += duplicate.eq(1)

        with m.If(self.trig.post):
            m.d.sync += Assert(~duplicate)

        return m

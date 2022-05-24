from amaranth import *
from amaranth.asserts import *

from .. import PowerFVCheck
from ... import pfv, tb


__all__ = ["UniquenessSpec", "UniquenessCheck"]


class UniquenessSpec(Elaboratable):
    """Uniqueness specification.

    A core cannot retire two instructions that share the same `pfv.order` identifier.
    """
    def __init__(self, pre, post):
        self.pfv  = pfv.Interface()
        self.pre  = tb.Trigger(cycle=pre)
        self.post = tb.Trigger(cycle=post)

    def triggers(self):
        yield from (self.pre, self.post)

    def elaborate(self, platform):
        m = Module()

        spec_order = AnyConst(self.pfv.order.shape())
        duplicate  = Signal()

        with m.If(self.pre.stb):
            m.d.sync += [
                Assume(self.pfv.stb),
                Assume(spec_order == self.pfv.order),
                Assume(~duplicate),
            ]
        with m.Elif(self.pfv.stb & (self.pfv.order == spec_order)):
            m.d.sync += duplicate.eq(1)

        with m.If(self.post.stb):
            m.d.sync += Assert(~duplicate)

        return m


class UniquenessCheck(PowerFVCheck, name="cons_unique"):
    def get_testbench(self, dut, pre, post):
        tb_spec = UniquenessSpec(pre, post)
        tb_top  = tb.Testbench(tb_spec, dut)
        return tb_top

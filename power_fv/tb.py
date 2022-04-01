from amaranth import *
from amaranth.asserts import *


__all__ = ["Testbench"]


class Testbench(Elaboratable):
    def __init__(self, check, dut, *, t_post, t_pre=None, t_start=0):
        if not isinstance(t_post, int) or t_post < 0:
            raise ValueError("t_post must be a non-negative integer, not {!r}"
                             .format(t_post))
        if t_pre is None:
            t_pre = t_post
        if not isinstance(t_pre, int) or t_pre < 0:
            raise ValueError("t_pre must be a non-negative integer, not {!r}"
                             .format(t_pre))
        if t_pre > t_post:
            raise ValueError("t_pre ({}) must be lesser than or equal to t_post ({})"
                             .format(t_pre, t_post))
        if not isinstance(t_start, int) or t_start < 0:
            raise ValueError("t_start must be a non-negative integer, not {!r}"
                             .format(t_start))
        if t_start > t_pre:
            raise ValueError("t_start ({}) must be lesser than or equal to t_pre ({})"
                             .format(t_start, t_pre))

        self.t_post  = t_post
        self.t_pre   = t_pre
        self.t_start = t_start

        self.check = check
        self.dut   = dut

    def elaborate(self, platform):
        m = Module()

        timer = Signal(range(self.t_post + 1))
        with m.If(timer != self.t_post):
            m.d.sync += timer.eq(timer + 1)

        m.submodules.check = ResetInserter(timer < self.t_start)(self.check)
        m.submodules.dut   = self.dut

        m.d.comb += [
            self.check.dut .eq(self.dut.pfv),
            self.check.pre .eq(timer == self.t_pre),
            self.check.post.eq(timer == self.t_post),
        ]

        m.d.comb += Assume(ResetSignal() == Initial())

        return m

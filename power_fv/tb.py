from amaranth import *
from amaranth.asserts import *


__all__ = ["Testbench"]


def _check_triggers(t_start, t_pre, t_post):
    if not isinstance(t_start, int) or t_start <= 0:
        raise ValueError("t_start must be a positive integer, not {!r}"
                         .format(t_start))
    if not isinstance(t_post, int) or t_post < t_start:
        raise ValueError("t_post must be an integer greater than or equal to t_start ({}), not {!r}"
                         .format(t_start, t_post))
    if not isinstance(t_pre, int) or t_pre > t_post or t_pre < t_start:
        raise ValueError("t_pre must be an integer between t_start and t_post (i.e. [{},{}]), "
                         "not {!r}".format(t_start, t_post, t_pre))


class Testbench(Elaboratable):
    def __init__(self, check, dut, *, t_start=1, t_pre=None, t_post=20):
        if t_pre is None and t_post is not None:
            t_pre = t_post

        _check_triggers(t_start, t_pre, t_post)

        self.check   = check
        self.dut     = dut
        self.t_start = t_start
        self.t_pre   = t_pre
        self.t_post  = t_post

    def elaborate(self, platform):
        m = Module()

        timer = Signal(range(self.t_post + 2), reset=1)

        with m.If(timer <= self.t_post):
            m.d.sync += timer.eq(timer + 1)

        m.submodules.check = ResetInserter(timer < self.t_start)(self.check)
        m.submodules.dut   = self.dut

        m.d.comb += [
            self.check.pfv.eq(self.dut.pfv),
            self.check.trig.pre .eq(timer == self.t_pre),
            self.check.trig.post.eq(timer == self.t_post),
        ]

        m.d.comb += Assume(ResetSignal() == Initial())

        return m

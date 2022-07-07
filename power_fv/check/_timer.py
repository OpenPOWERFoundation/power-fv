from amaranth import *


__all__ = ["Timer"]


class Timer(Elaboratable):
    def __init__(self, start):
        if not isinstance(start, int) or start < 0:
            raise TypeError("Start value must be a non-negative integer, not {!r}"
                            .format(start))

        self.ctr  = Signal(range(start + 1), reset=start, reset_less=True)
        self.zero = Signal()

    def elaborate(self, platform):
        m = Module()

        with m.If(self.ctr != 0):
            m.d.sync += self.ctr.eq(self.ctr - 1)

        m.d.comb += self.zero.eq(self.ctr == 0)

        return m

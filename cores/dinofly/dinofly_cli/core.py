from amaranth import *
from amaranth.asserts import *

from dinofly.core import DinoflyCPU

from power_fv.core import PowerFVCore


__all__ = ["DinoflyWrapper"]


class DinoflyWrapper(Elaboratable):
    def __init__(self, **kwargs):
        self._cpu = DinoflyCPU(with_pfv=True)
        self.pfv  = self._cpu.pfv
        self.ibus = self._cpu.ibus

    def elaborate(self, platform):
        m = Module()

        m.submodules.cpu = self._cpu

        m.d.comb += [
            self.ibus.dat_r.eq(AnySeq(self.ibus.data_width)),
            self.ibus.ack  .eq(AnySeq(1)),
            self.ibus.err  .eq(AnySeq(1)),
        ]

        return m


class DinoflyCore(PowerFVCore):
    @classmethod
    def wrapper(cls, **kwargs):
        return DinoflyWrapper(**kwargs)

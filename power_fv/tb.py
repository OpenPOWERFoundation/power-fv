from collections import OrderedDict

from amaranth import *
from amaranth.asserts import *
from amaranth.utils import bits_for


__all__ = ["Trigger", "Testbench"]


class Trigger:
    def __init__(self, cycle, name=None, src_loc_at=0):
        if not isinstance(cycle, int) or cycle <= 0:
            raise ValueError("Clock cycle must be a positive integer, not {!r}"
                             .format(cycle))

        self.stb   = Signal(name=name, src_loc_at=1 + src_loc_at)
        self.cycle = cycle


class Testbench(Elaboratable):
    def __init__(self, spec, dut):
        self.spec = spec
        self.dut  = dut

        self._triggers  = OrderedDict()
        self._bmc_depth = None
        self._frozen    = False

        for trigger in spec.triggers():
            self.add_trigger(trigger)

    def freeze(self):
        if not self._frozen:
            self._bmc_depth = max(t.cycle for t in self.triggers()) + 1
            self._frozen    = True

    def add_trigger(self, trigger):
        if self._frozen:
            raise ValueError("Testbench is frozen.")
        if not isinstance(trigger, Trigger):
            raise TypeError("Trigger must be an instance of Trigger, not {!r}"
                            .format(trig))
        self._triggers[id(trigger)] = trigger

    def triggers(self):
        yield from self._triggers.values()

    @property
    def bmc_depth(self):
        self.freeze()
        return self._bmc_depth

    def elaborate(self, platform):
        m = Module()

        cycle = Signal(range(self.bmc_depth), reset=1)

        with m.If(cycle < self.bmc_depth - 1):
            m.d.sync += cycle.eq(cycle + 1)

        for trigger in self.triggers():
            m.d.comb += trigger.stb.eq(cycle == trigger.cycle)

        m.submodules.spec = self.spec
        m.submodules.dut  = self.dut

        m.d.comb += self.spec.pfv.eq(self.dut.pfv)

        m.d.comb += Assume(ResetSignal() == Initial())

        return m

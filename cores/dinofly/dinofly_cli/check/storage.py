from amaranth import *
from amaranth.asserts import *
from amaranth.utils import log2_int

from amaranth_soc import wishbone

from power_fv.check.storage import *

from ..core import *


__all__ = [
    "InsnStorageCheck_Dinofly", "InsnStorageTestbench_Dinofly", "InsnStorageModel_Dinofly",
    "DataStorageCheck_Dinofly", "DataStorageTestbench_Dinofly", "DataStorageModel_Dinofly",
]


class InsnStorageCheck_Dinofly(InsnStorageCheck, name=("dinofly", "storage", "insn")):
    def __init__(self, *, depth, skip, core, **kwargs):
        if not isinstance(core, DinoflyCore):
            raise TypeError("Core must be an instance of DinoflyCore, not {!r}"
                            .format(core))
        super().__init__(depth=depth, skip=skip, core=core, **kwargs)

    def testbench(self):
        return InsnStorageTestbench_Dinofly(self)


class InsnStorageTestbench_Dinofly(InsnStorageTestbench):
    def __init__(self, check):
        if not isinstance(check, InsnStorageCheck_Dinofly):
            raise TypeError("Check must be an instance of InsnStorageCheck_Dinofly, not {!r}"
                            .format(check))
        super().__init__(check)

    def storage(self):
        return InsnStorageModel_Dinofly(
            ibus_addr_width=self.check.dut.ibus.addr_width,
            ibus_data_width=self.check.dut.ibus.data_width,
            ibus_granularity=self.check.dut.ibus.granularity,
        )


class InsnStorageModel_Dinofly(InsnStorageModel, Elaboratable):
    def __init__(self, *, ibus_addr_width=30, ibus_data_width=32, ibus_granularity=8):
        self.addr  = Signal(64)
        self.data  = Signal(32)
        self._ibus = wishbone.Interface(addr_width=ibus_addr_width, data_width=ibus_data_width,
                                        granularity=ibus_granularity)

    def connect(self, dut):
        assert isinstance(dut, DinoflyWrapper)
        assert dut.ibus.addr_width  == self._ibus.addr_width
        assert dut.ibus.data_width  == self._ibus.data_width
        assert dut.ibus.granularity == self._ibus.granularity

        return self._ibus.eq(dut.ibus)

    def elaborate(self, platform):
        m = Module()

        with m.If(self._ibus.ack):
            m.d.comb += [
                Assume(self._ibus.cyc & Past(self._ibus.cyc)),
                Assume(self._ibus.stb & Past(self._ibus.stb)),
                Assume(~Past(self._ibus.ack)),
            ]

        gran_bits = log2_int(self._ibus.data_width // self._ibus.granularity)

        m.d.comb += [
            self.addr.eq(AnyConst(self._ibus.addr_width + gran_bits)),
            self.data.eq(AnyConst(32)),
        ]

        with m.If(self._ibus.cyc & self._ibus.stb & self._ibus.ack & ~ResetSignal("sync")):
            if self._ibus.data_width == 32:
                with m.If(self.addr == Cat(Const(0b00, 2), self._ibus.adr)):
                    m.d.comb += Assume(self._ibus.dat_r == self.data)
            elif self._ibus.data_width == 64:
                with m.If(self.addr == Cat(Const(0b000, 3), self._ibus.adr)):
                    m.d.comb += Assume(self._ibus.dat_r[:32] == self.data)
                with m.If(self.addr == Cat(Const(0b100, 3), self._ibus.adr)):
                    m.d.comb += Assume(self._ibus.dat_r[32:] == self.data)
            else:
                assert False

        return m


class DataStorageCheck_Dinofly(DataStorageCheck, name=("dinofly", "storage", "data")):
    def __init__(self, *, depth, skip, core, **kwargs):
        if not isinstance(core, DinoflyCore):
            raise TypeError("Core must be an instance of DinoflyCore, not {!r}"
                            .format(core))
        super().__init__(depth=depth, skip=skip, core=core, **kwargs)

    def testbench(self):
        return DataStorageTestbench_Dinofly(self)


class DataStorageTestbench_Dinofly(DataStorageTestbench):
    def __init__(self, check):
        if not isinstance(check, DataStorageCheck_Dinofly):
            raise TypeError("Check must be an instance of DataStorageCheck_Dinofly, not {!r}"
                            .format(check))
        super().__init__(check)

    def storage(self):
        return DataStorageModel_Dinofly(
            dbus_addr_width=self.check.dut.dbus.addr_width,
            dbus_data_width=self.check.dut.dbus.data_width,
            dbus_granularity=self.check.dut.dbus.granularity,
        )


class DataStorageModel_Dinofly(DataStorageModel, Elaboratable):
    def __init__(self, *, dbus_addr_width=30, dbus_data_width=32, dbus_granularity=8):
        self.addr  = Signal(64)
        self._dbus = wishbone.Interface(addr_width=dbus_addr_width, data_width=dbus_data_width,
                                        granularity=dbus_granularity)

    def connect(self, dut):
        assert isinstance(dut, DinoflyWrapper)
        assert dut.dbus.addr_width  == self._dbus.addr_width
        assert dut.dbus.data_width  == self._dbus.data_width
        assert dut.dbus.granularity == self._dbus.granularity

        return self._dbus.eq(dut.dbus)

    def elaborate(self, platform):
        m = Module()

        dbus_read  = Signal()
        dbus_write = Signal()

        m.d.comb += [
            dbus_read .eq(self._dbus.cyc & self._dbus.stb & self._dbus.ack),
            dbus_write.eq(self._dbus.cyc & self._dbus.stb & self._dbus.ack & self._dbus.we),
        ]

        with m.If(self._dbus.ack):
            m.d.comb += [
                Assume(self._dbus.cyc & Past(self._dbus.cyc)),
                Assume(self._dbus.stb & Past(self._dbus.stb)),
                Assume(~Past(self._dbus.ack)),
            ]

        gran_bits = log2_int(self._dbus.data_width // self._dbus.granularity)
        addr_hit  = Signal()
        value     = Signal(self._dbus.data_width)

        m.d.comb += [
            self.addr.eq(AnyConst(self._dbus.addr_width + gran_bits)),
            addr_hit .eq(self._dbus.adr == self.addr[gran_bits:]),
        ]

        with m.If(dbus_read & addr_hit & ~ResetSignal("sync")):
            m.d.comb += Assume(self._dbus.dat_r == value)

        with m.If(dbus_write & addr_hit):
            for i, sel_bit in enumerate(self._dbus.sel):
                with m.If(sel_bit):
                    m.d.sync += value[i*8:i*8+8].eq(self._dbus.dat_w[i*8:i*8+8])

        return m

from amaranth import *
from amaranth.asserts import *
from amaranth.utils import log2_int

from amaranth_soc import wishbone

from power_fv.check.storage import *

from ..core import *


__all__ = [
    "InsnStorageCheck_Microwatt", "InsnStorageTestbench_Microwatt", "InsnStorageModel_Microwatt",
    "DataStorageCheck_Microwatt", "DataStorageTestbench_Microwatt", "DataStorageModel_Microwatt",
]


class InsnStorageCheck_Microwatt(InsnStorageCheck, name=("microwatt", "storage", "insn")):
    def __init__(self, *, depth, skip, core, **kwargs):
        if not isinstance(core, MicrowattCore):
            raise TypeError("Core must be an instance of MicrowattCore, not {!r}"
                            .format(core))
        super().__init__(depth=depth, skip=skip, core=core, **kwargs)

    def testbench(self):
        return InsnStorageTestbench_Microwatt(self)


class InsnStorageTestbench_Microwatt(InsnStorageTestbench):
    def storage(self):
        return InsnStorageModel_Microwatt()


class InsnStorageModel_Microwatt(InsnStorageModel, Elaboratable):
    def __init__(self):
        self.addr  = Signal(64)
        self.data  = Signal(32)
        self._ibus = wishbone.Interface(addr_width=29, data_width=64, granularity=8,
                                        features=("stall",))

    def connect(self, dut):
        assert isinstance(dut, MicrowattWrapper)
        assert dut.wb_insn.addr_width  == self._ibus.addr_width
        assert dut.wb_insn.data_width  == self._ibus.data_width
        assert dut.wb_insn.granularity == self._ibus.granularity

        return self._ibus.eq(dut.wb_insn)

    def elaborate(self, platform):
        m = Module()

        with m.If(self._ibus.cyc & self._ibus.stb):
            m.d.comb += Assume(self._ibus.stall == ~self._ibus.ack)

        with m.If(self._ibus.ack):
            m.d.comb += [
                Assume(self._ibus.cyc & Past(self._ibus.cyc)),
                Assume(self._ibus.stb & Past(self._ibus.stb)),
                Assume(~Past(self._ibus.ack)),
            ]

        m.d.comb += [
            self.addr.eq(Cat(AnyConst(32), Const(0, 32))),
            self.data.eq(AnyConst(32)),
        ]

        with m.If(self._ibus.cyc & self._ibus.stb & self._ibus.ack & ~ResetSignal("sync")):
            with m.If(self.addr == Cat(Const(0b000, 3), self._ibus.adr)):
                m.d.comb += Assume(self._ibus.dat_r[:32] == self.data)
            with m.If(self.addr == Cat(Const(0b100, 3), self._ibus.adr)):
                m.d.comb += Assume(self._ibus.dat_r[32:] == self.data)

        return m


class DataStorageCheck_Microwatt(DataStorageCheck, name=("microwatt", "storage", "data")):
    def __init__(self, *, depth, skip, core, **kwargs):
        if not isinstance(core, MicrowattCore):
            raise TypeError("Core must be an instance of MicrowattCore, not {!r}"
                            .format(core))
        super().__init__(depth=depth, skip=skip, core=core, **kwargs)

    def testbench(self):
        return DataStorageTestbench_Microwatt(self)


class DataStorageTestbench_Microwatt(DataStorageTestbench):
    def storage(self):
        return DataStorageModel_Microwatt()


class DataStorageModel_Microwatt(DataStorageModel, Elaboratable):
    def __init__(self):
        self.addr  = Signal(64)
        self._dbus = wishbone.Interface(addr_width=29, data_width=64, granularity=8,
                                        features=("stall",))

    def connect(self, dut):
        assert isinstance(dut, MicrowattWrapper)
        assert dut.wb_data.addr_width  == self._dbus.addr_width
        assert dut.wb_data.data_width  == self._dbus.data_width
        assert dut.wb_data.granularity == self._dbus.granularity

        return self._dbus.eq(dut.wb_data)

    def elaborate(self, platform):
        m = Module()

        dbus_read  = Signal()
        dbus_write = Signal()

        m.d.comb += [
            dbus_read .eq(self._dbus.cyc & self._dbus.stb & self._dbus.ack),
            dbus_write.eq(self._dbus.cyc & self._dbus.stb & self._dbus.ack & self._dbus.we),
        ]

        with m.If(self._dbus.cyc & self._dbus.stb):
            m.d.comb += Assume(self._dbus.stall == ~self._dbus.ack)

        with m.If(self._dbus.ack):
            m.d.comb += [
                Assume(self._dbus.cyc & Past(self._dbus.cyc)),
                Assume(self._dbus.stb & Past(self._dbus.stb)),
                Assume(~Past(self._dbus.ack)),
            ]

        addr_lsb = log2_int(len(self._dbus.sel))
        addr_hit = Signal()
        value    = Signal(64)

        m.d.comb += [
            self.addr.eq(Cat(AnyConst(32), Const(0, 32))),
            addr_hit.eq(self._dbus.adr == self.addr[addr_lsb:32]),
        ]

        with m.If(dbus_read & addr_hit & ~ResetSignal("sync")):
            m.d.comb += Assume(self._dbus.dat_r == value)

        with m.If(dbus_write & addr_hit):
            for i, sel_bit in enumerate(self._dbus.sel):
                with m.If(sel_bit):
                    m.d.sync += value[i*8:i*8+8].eq(self._dbus.dat_w[i*8:i*8+8])

        return m

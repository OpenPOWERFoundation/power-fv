from amaranth import *
from amaranth.asserts import *
from amaranth.utils import log2_int

from amaranth_soc import wishbone

from power_fv.check.storage import DataStorageCheck, DataStorageTestbench, DataStorageModel

from ..core import *


__all__ = [
    "DataStorageCheck_Microwatt", "DataStorageTestbench_Microwatt", "DataStorageModel_Microwatt",
]


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

            Assume(self._dbus.ack.implies(Past(self._dbus.cyc) & self._dbus.cyc)),
            Assume(self._dbus.ack.implies(Past(self._dbus.stb) & self._dbus.stb)),
            Assume(self._dbus.ack.implies(~Past(self._dbus.ack))),
        ]

        with m.If(self._dbus.cyc & self._dbus.stb):
            m.d.comb += Assume(self._dbus.stall == ~self._dbus.ack)

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

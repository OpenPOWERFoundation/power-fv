from abc import ABCMeta, abstractmethod

from amaranth import *
from amaranth.asserts import *

from power_fv.check import PowerFVCheck


__all__ = [
    "InsnStorageCheck", "InsnStorageModel", "InsnStorageTestbench",
    "DataStorageCheck", "DataStorageModel", "DataStorageTestbench",
]


# TODO: add support for restricting addresses to non-cachable/write-through regions.


class InsnStorageCheck(PowerFVCheck):
    pass


class InsnStorageModel(metaclass=ABCMeta):
    @abstractmethod
    def connect(self, dut):
        raise NotImplementedError

    @abstractmethod
    def elaborate(self, platform):
        raise NotImplementedError


class InsnStorageTestbench(Elaboratable, metaclass=ABCMeta):
    def __init__(self, check):
        if not isinstance(check, InsnStorageCheck):
            raise TypeError("Check must be an instance of InsnStorageCheck, not {!r}"
                            .format(check))
        self.check = check
        self.name  = "storage_insn_tb"

    @abstractmethod
    def storage(self):
        raise NotImplementedError

    def elaborate(self, platform):
        m = Module()

        m.submodules.dut     = dut     = self.check.dut
        m.submodules.storage = storage = self.storage()

        insn_po  = Signal(6)
        prefixed = Signal()

        m.d.comb += [
            storage.connect(dut),

            insn_po .eq(dut.pfv.insn[63-5:64-0]),
            prefixed.eq(insn_po == 1),
        ]

        with m.If(dut.pfv.stb & ~dut.pfv.intr):
            with m.If(dut.pfv.cia == storage.addr):
                m.d.comb += Assert(dut.pfv.insn[32:] == storage.data)
            with m.If(prefixed & (dut.pfv.cia + 4 == storage.addr)):
                m.d.comb += Assert(dut.pfv.insn[:32] == storage.data)

        return m


class DataStorageCheck(PowerFVCheck):
    pass


class DataStorageModel(metaclass=ABCMeta):
    @abstractmethod
    def connect(self, dut):
        raise NotImplementedError

    @abstractmethod
    def elaborate(self, platform):
        raise NotImplementedError


class DataStorageTestbench(Elaboratable, metaclass=ABCMeta):
    def __init__(self, check):
        if not isinstance(check, DataStorageCheck):
            raise TypeError("Check must be an instance of DataStorageCheck, not {!r}"
                            .format(check))
        self.check = check
        self.name  = "storage_data_tb"

    @abstractmethod
    def storage(self):
        raise NotImplementedError

    def elaborate(self, platform):
        m = Module()

        m.submodules.dut     = dut     = self.check.dut
        m.submodules.storage = storage = self.storage()

        written = Signal(64 // 8)
        shadow  = Signal(64)

        m.d.comb += storage.connect(dut)

        with m.If(dut.pfv.stb & dut.pfv.skip):
            m.d.comb += [
                Assert(~dut.pfv.mem.r_mask.any()),
                Assert(~dut.pfv.mem.w_mask.any()),
            ]

        with m.If(dut.pfv.stb & (dut.pfv.mem.addr == storage.addr)):
            for i, byte_written in enumerate(written):
                byte_shadow = shadow[i*8:i*8+8]
                byte_w_stb  = dut.pfv.mem.w_mask[i]
                byte_w_data = dut.pfv.mem.w_data[i*8:i*8+8]
                byte_r_stb  = dut.pfv.mem.r_mask[i]
                byte_r_data = dut.pfv.mem.r_data[i*8:i*8+8]

                with m.If(byte_w_stb):
                    m.d.sync += [
                        byte_written.eq(1),
                        byte_shadow .eq(byte_w_data),
                    ]

                with m.If(byte_r_stb & byte_written):
                    m.d.comb += Assert(byte_r_data == byte_shadow)

        return m


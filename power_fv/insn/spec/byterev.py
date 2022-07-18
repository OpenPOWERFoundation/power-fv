from amaranth import *

from power_fv import pfv
from power_fv.insn.const import *

from . import InsnSpec
from .utils import iea, byte_reversed


__all__ = ["ByteReverseSpec"]


class ByteReverseSpec(InsnSpec, Elaboratable):
    def __init__(self, insn):
        self.pfv  = pfv.Interface()
        self.insn = insn

    def elaborate(self, platform):
        m = Module()

        m.d.comb += [
            self.pfv.stb .eq(1),
            self.pfv.insn.eq(Cat(Const(0, 32), self.insn.as_value())),
            self.pfv.intr.eq(0),
            self.pfv.nia .eq(iea(self.pfv.cia + 4, self.pfv.msr.r_data.sf)),
            self.pfv.msr.r_mask.sf.eq(1),
        ]

        m.d.comb += [
            self.pfv.rs.index.eq(self.insn.RS),
            self.pfv.rs.r_stb.eq(1),
            self.pfv.ra.index.eq(self.insn.RA),
            self.pfv.ra.w_stb.eq(1),
        ]

        if isinstance(self.insn, BRH):
            for i in range(64//16):
                rs_hword = self.pfv.rs.r_data.word_select(i, width=16)
                ra_hword = self.pfv.ra.w_data.word_select(i, width=16)
                m.d.comb += ra_hword.eq(byte_reversed(rs_hword, en=1))

        elif isinstance(self.insn, BRW):
            for i in range(64//32):
                rs_word = self.pfv.rs.r_data.word_select(i, width=32)
                ra_word = self.pfv.ra.w_data.word_select(i, width=32)
                m.d.comb += ra_word.eq(byte_reversed(rs_word, en=1))

        else:
            assert False

        return m

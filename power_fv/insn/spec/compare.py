from amaranth import *

from power_fv import pfv
from power_fv.insn.const import *

from . import InsnSpec
from .utils import iea


__all__ = ["CompareSpec"]


class CompareSpec(InsnSpec, Elaboratable):
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
            self.pfv.xer.r_mask.so.eq(1),
        ]

        src_a  = Signal(64)
        src_b  = Signal(64)
        result = Record([
            ("lt",  1),
            ("gt",  1),
            ("eq_", 1),
            ("so",  1),
        ])

        # Operand A : (RA) or [(RA)(32:63) sign-extended or zero-extended]

        m.d.comb += [
            self.pfv.ra.index.eq(self.insn.RA),
            self.pfv.ra.r_stb.eq(1),
        ]

        if isinstance(self.insn, (CMPI, CMP)):
            with m.If(self.insn.L):
                m.d.comb += src_a.eq(self.pfv.ra.r_data)
            with m.Else():
                m.d.comb += src_a.eq(self.pfv.ra.r_data[:32].as_signed())
        elif isinstance(self.insn, (CMPL, CMPLI)):
            with m.If(self.insn.L):
                m.d.comb += src_a.eq(self.pfv.ra.r_data)
            with m.Else():
                m.d.comb += src_a.eq(self.pfv.ra.r_data[:32].as_unsigned())
        else:
            assert False

        # Operand B : SI or UI or (RB) or [(RB)(32:63) sign-extended or zero-extended]

        if isinstance(self.insn, (CMP, CMPL)):
            m.d.comb += [
                self.pfv.rb.index.eq(self.insn.RB),
                self.pfv.rb.r_stb.eq(1),
            ]

        if isinstance(self.insn, CMPI):
            m.d.comb += src_b.eq(self.insn.SI)
        elif isinstance(self.insn, CMPLI):
            m.d.comb += src_b.eq(self.insn.UI)
        elif isinstance(self.insn, CMP):
            with m.If(self.insn.L):
                m.d.comb += src_b.eq(self.pfv.rb.r_data)
            with m.Else():
                m.d.comb += src_b.eq(self.pfv.rb.r_data[:32].as_signed())
        elif isinstance(self.insn, CMPL):
            with m.If(self.insn.L):
                m.d.comb += src_b.eq(self.pfv.rb.r_data)
            with m.Else():
                m.d.comb += src_b.eq(self.pfv.rb.r_data[:32].as_unsigned())
        else:
            assert False

        # Result

        if isinstance(self.insn, (CMPI, CMP)):
            m.d.comb += result.lt.eq(src_a.as_signed() < src_b.as_signed())
        elif isinstance(self.insn, (CMPLI, CMPL)):
            m.d.comb += result.lt.eq(src_a.as_unsigned() < src_b.as_unsigned())
        else:
            assert False

        m.d.comb += [
            result.gt .eq(~(result.lt | result.eq_)),
            result.eq_.eq(src_a == src_b),
            result.so .eq(self.pfv.xer.r_data.so),
        ]

        m.d.comb += [
            self.pfv.cr.w_mask[::-1].word_select(self.insn.BF, width=4).eq(0b1111),
            self.pfv.cr.w_data[::-1].word_select(self.insn.BF, width=4).eq(result),
        ]

        return m

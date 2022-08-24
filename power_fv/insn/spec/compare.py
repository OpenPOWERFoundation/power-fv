from amaranth import *

from power_fv import pfv
from power_fv.insn.const import *

from . import InsnSpec
from .utils import iea


__all__ = ["CompareSpec"]


class CompareSpec(InsnSpec, Elaboratable):
    def elaborate(self, platform):
        m = Module()

        m.d.comb += [
            self.insn    .eq(self.pfv.insn[32:]),
            self.pfv.stb .eq(self.insn.is_valid() & ~self.pfv.insn[:32].any()),
            self.pfv.intr.eq(0),
            self.pfv.nia .eq(iea(self.pfv.cia + 4, self.pfv.msr.r_data.sf)),
            self.pfv.msr.r_mask.sf.eq(1),
            self.pfv.xer.r_mask.so.eq(1),
        ]

        src_a  = Signal(64)
        src_b  = Signal(64)
        result = Record([
            ("so",  1),
            ("eq_", 1),
            ("gt",  1),
            ("lt",  1),
        ])

        # Operand A : (RA) or EXTS((RA)(32:63)) or EXTZ((RA)(32:63)) or EXTZ((RA)(56:63))

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
        elif isinstance(self.insn, (CMPRB, CMPEQB)):
            m.d.comb += src_a.eq(self.pfv.ra.r_data[:8].as_unsigned())
        else:
            assert False

        # Operand B : SI or UI or (RB) or EXTS((RB)(32:63)) or EXTZ((RB)(32:63))

        if isinstance(self.insn, (CMP, CMPL, CMPRB, CMPEQB)):
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
        elif isinstance(self.insn, CMPRB):
            m.d.comb += src_b.eq(self.pfv.rb.r_data[:32].as_unsigned())
        elif isinstance(self.insn, CMPEQB):
            m.d.comb += src_b.eq(self.pfv.rb.r_data)
        else:
            assert False

        # Result

        if isinstance(self.insn, (CMPI, CMP, CMPLI, CMPL)):
            if isinstance(self.insn, (CMPI, CMP)):
                m.d.comb += result.lt.eq(src_a.as_signed() < src_b.as_signed())
            if isinstance(self.insn, (CMPLI, CMPL)):
                m.d.comb += result.lt.eq(src_a.as_unsigned() < src_b.as_unsigned())

            m.d.comb += [
                result.gt .eq(~(result.lt | result.eq_)),
                result.eq_.eq(src_a == src_b),
                result.so .eq(self.pfv.xer.r_data.so),
            ]

        elif isinstance(self.insn, CMPRB):
            src1     = Signal(unsigned(8))
            src21hi  = Signal(unsigned(8))
            src21lo  = Signal(unsigned(8))
            src22hi  = Signal(unsigned(8))
            src22lo  = Signal(unsigned(8))
            in_range = Signal()

            m.d.comb += [
                src1.eq(src_a[:8]),
                Cat(src22lo, src22hi, src21lo, src21hi).eq(src_b[:32]),
            ]

            with m.If(~self.insn.L):
                m.d.comb += in_range.eq( (src22lo <= src1) & (src1 <= src22hi))
            with m.Else():
                m.d.comb += in_range.eq( (src21lo <= src1) & (src1 <= src21hi)
                                       | (src22lo <= src1) & (src1 <= src22hi))

            m.d.comb += result.eq(Cat(Const(0, 2), in_range, Const(0, 1)))

        elif isinstance(self.insn, CMPEQB):
            _match = 0
            for i in range(64//8):
                _match |= (src_a == src_b.word_select(i, width=8))

            m.d.comb += result.eq(Cat(Const(0, 2), _match, Const(0, 1)))

        else:
            assert False

        m.d.comb += [
            self.pfv.cr.w_mask.word_select(7-self.insn.BF, width=4).eq(0xf),
            self.pfv.cr.w_data.word_select(7-self.insn.BF, width=4).eq(result),
        ]

        return m

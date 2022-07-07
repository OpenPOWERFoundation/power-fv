from amaranth import *

from power_fv import pfv
from power_fv.insn.const import *

from . import InsnSpec
from .utils import iea


__all__ = ["CRSpec"]


class CRSpec(InsnSpec, Elaboratable):
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

        if isinstance(self.insn, (
            CRAND, CROR  , CRNAND, CRXOR,
            CRNOR, CRANDC, CREQV , CRORC,
            )):
            src_a  = Signal()
            src_b  = Signal()
            result = Signal()

            m.d.comb += [
                self.pfv.cr.r_mask[::-1].bit_select(self.insn.BA, width=1).eq(1),
                self.pfv.cr.r_mask[::-1].bit_select(self.insn.BB, width=1).eq(1),

                src_a.eq(self.pfv.cr.r_data[::-1].bit_select(self.insn.BA, width=1)),
                src_b.eq(self.pfv.cr.r_data[::-1].bit_select(self.insn.BB, width=1)),
            ]

            if isinstance(self.insn, CRAND):
                m.d.comb += result.eq(src_a & src_b)
            if isinstance(self.insn, CROR):
                m.d.comb += result.eq(src_a | src_b)
            if isinstance(self.insn, CRNAND):
                m.d.comb += result.eq(~(src_a & src_b))
            if isinstance(self.insn, CRXOR):
                m.d.comb += result.eq(src_a ^ src_b)
            if isinstance(self.insn, CRNOR):
                m.d.comb += result.eq(~(src_a | src_b))
            if isinstance(self.insn, CRANDC):
                m.d.comb += result.eq(src_a & ~src_b)
            if isinstance(self.insn, CREQV):
                m.d.comb += result.eq(src_a == src_b)
            if isinstance(self.insn, CRORC):
                m.d.comb += result.eq(src_a | ~src_b)

            m.d.comb += [
                self.pfv.cr.w_mask[::-1].bit_select(self.insn.BT, width=1).eq(1),
                self.pfv.cr.w_data[::-1].bit_select(self.insn.BT, width=1).eq(result),
            ]

        elif isinstance(self.insn, MCRF):
            field = Signal(4)

            m.d.comb += [
                field.eq(self.pfv.cr.r_data[::-1].word_select(self.insn.BFA, width=4)),

                self.pfv.cr.r_mask[::-1].word_select(self.insn.BFA, width=4).eq(0b1111),
                self.pfv.cr.w_mask[::-1].word_select(self.insn.BF,  width=4).eq(0b1111),
                self.pfv.cr.w_data[::-1].word_select(self.insn.BF,  width=4).eq(field),
            ]

        else:
            assert False

        return m

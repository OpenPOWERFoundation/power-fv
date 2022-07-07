from amaranth import *

from power_fv import pfv
from power_fv.insn.const import *

from . import InsnSpec
from .utils import iea


__all__ = ["BranchSpec"]


class BranchSpec(InsnSpec, Elaboratable):
    def __init__(self, insn):
        self.pfv  = pfv.Interface()
        self.insn = insn

    def elaborate(self, platform):
        m = Module()

        m.d.comb += [
            self.pfv.stb .eq(1),
            self.pfv.insn.eq(Cat(Const(0, 32), self.insn.as_value())),
            self.pfv.msr.r_mask.sf.eq(1),
        ]

        # Raise an interrupt if the BO field is invalid.

        if isinstance(self.insn, (
            BC   , BCA   , BCL  , BCLA  ,
            BCLR , BCLRL , BCTAR, BCTARL,
            BCCTR, BCCTRL,
            )):
            bo_valid_patterns = [
                "001--",
                "011--",
                "1-1--",
            ]
            # BO(2)=0 ("decrement and test CTR") is illegal for bcctr/bcctrl.
            if not isinstance(self.insn, (BCCTR, BCCTRL)):
                bo_valid_patterns += [
                    "0000-",
                    "0001-",
                    "0100-",
                    "0101-",
                    "1-00-",
                    "1-01-",
                ]
            m.d.comb += self.pfv.intr.eq(~self.insn.BO.matches(*bo_valid_patterns))

        else:
            m.d.comb += self.pfv.intr.eq(0)

        # Read MSR.SF

        m.d.comb += self.pfv.msr.r_mask.sf.eq(1)

        # Is this branch taken ?

        taken    = Signal()

        cond_bit = Signal()
        cond_ok  = Signal()
        ctr_any  = Signal()
        ctr_ok   = Signal()

        if isinstance(self.insn, (B, BA, BL, BLA)):
            m.d.comb += taken.eq(1)

        elif isinstance(self.insn, (
            BC   , BCA   , BCL  , BCLA  ,
            BCLR , BCLRL , BCTAR, BCTARL,
            BCCTR, BCCTRL,
            )):

            # If BO(0) = 0, test CR(BI)
            with m.If(self.insn.BO[4 - 0]):
                m.d.comb += cond_ok.eq(1)
            with m.Else():
                m.d.comb += [
                    self.pfv.cr.r_mask[::-1].bit_select(self.insn.BI, width=1).eq(1),

                    cond_bit.eq(self.pfv.cr.r_data[::-1].bit_select(self.insn.BI, width=1)),
                    cond_ok .eq(cond_bit == self.insn.BO[4 - 1]),
                ]

            if isinstance(self.insn, (BCCTR, BCCTRL)):
                m.d.comb += taken.eq(cond_ok)
            else:
                # If BO(2) = 0, decrement CTR then test its value.
                with m.If(self.insn.BO[4 - 2]):
                    m.d.comb += ctr_ok.eq(1)
                with m.Else():
                    m.d.comb += [
                        self.pfv.ctr.r_mask.eq(Repl(1, 64)),
                        self.pfv.ctr.w_mask.eq(Repl(1, 64)),
                        self.pfv.ctr.w_data.eq(self.pfv.ctr.r_data - 1),

                        ctr_any.eq(iea(self.pfv.ctr.w_data, self.pfv.msr.r_data.sf).any()),
                        ctr_ok .eq(ctr_any ^ self.insn.BO[4 - 3]),
                    ]
                m.d.comb += taken.eq(cond_ok & ctr_ok)

        else:
            assert False

        # Compute the target address

        target   = Signal(unsigned(64))
        base     = Signal(unsigned(64))
        offset   = Signal(  signed(62))

        # base : CIA if AA=0, 0 otherwise

        if isinstance(self.insn, (B, BL, BC, BCL)):
            m.d.comb += base.eq(self.pfv.cia)
        elif isinstance(self.insn, (
            BA  , BLA  , BCA  , BCLA  ,
            BCLR, BCLRL, BCCTR, BCCTRL, BCTAR, BCTARL,
            )):
            m.d.comb += base.eq(0)
        else:
            assert False

        # offset : LI or BD or LR>>2 or CTR>>2 or TAR>>2

        if isinstance(self.insn, (B, BA, BL, BLA)):
            m.d.comb += offset.eq(self.insn.LI)
        elif isinstance(self.insn, (BC, BCA, BCL, BCLA)):
            m.d.comb += offset.eq(self.insn.BD)
        elif isinstance(self.insn, (BCLR, BCLRL)):
            m.d.comb += [
                self.pfv.lr.r_mask[2:].eq(Repl(1, 62)),
                offset.eq(self.pfv.lr.r_data[2:]),
            ]
        elif isinstance(self.insn, (BCCTR, BCCTRL)):
            m.d.comb += [
                self.pfv.ctr.r_mask[2:].eq(Repl(1, 62)),
                offset.eq(self.pfv.ctr.r_data[2:]),
            ]
        elif isinstance(self.insn, (BCTAR, BCTARL)):
            m.d.comb += [
                self.pfv.tar.r_mask[2:].eq(Repl(1, 62)),
                offset.eq(self.pfv.tar.r_data[2:]),
            ]
        else:
            assert False

        # target : base + offset<<2

        m.d.comb += target.eq(base + Cat(Const(0, 2), offset))

        # Update NIA

        with m.If(taken):
            m.d.comb += self.pfv.nia.eq(iea(target, self.pfv.msr.r_data.sf))
        with m.Else():
            m.d.comb += self.pfv.nia.eq(iea(self.pfv.cia + 4, self.pfv.msr.r_data.sf))

        # Write the return address to LR if LK=1

        if isinstance(self.insn, (
            BL   , BLA   , BCL   , BCLA,
            BCLRL, BCCTRL, BCTARL,
            )):
            m.d.comb += [
                self.pfv.lr.w_mask.eq(Repl(1, 64)),
                self.pfv.lr.w_data.eq(iea(self.pfv.cia + 4, self.pfv.msr.r_data.sf)),
            ]

        return m

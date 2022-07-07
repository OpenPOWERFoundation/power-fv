from amaranth import *

from power_fv import pfv
from power_fv.insn.const import *
from power_fv.reg import xer_layout

from . import InsnSpec
from .utils import iea


__all__ = ["SPRMoveSpec"]


class SPRMoveSpec(InsnSpec, Elaboratable):
    def __init__(self, insn):
        self.pfv = pfv.Interface()
        self.insn = insn

    def elaborate(self, platform):
        m = Module()

        m.d.comb += [
            self.pfv.stb .eq(1),
            self.pfv.insn.eq(Cat(Const(0, 32), self.insn.as_value())),
            self.pfv.nia .eq(iea(self.pfv.cia + 4, self.pfv.msr.r_data.sf)),
            self.pfv.msr.r_mask.sf.eq(1),
            self.pfv.msr.r_mask.pr.eq(1),
        ]

        # If SPR(0) = 1, this instruction is privileged.

        spr_privileged = Signal()
        spr_access_err = Signal()

        m.d.comb += [
            spr_privileged.eq(self.insn.SPR[9 - 0]),
            spr_access_err.eq(spr_privileged & self.pfv.msr.r_data.pr),
            self.pfv.intr.eq(spr_access_err),
        ]

        def mXspr_spec(pfv_spr, mtspr_cls, mfspr_cls, reserved_mask):
            if isinstance(self.insn, mtspr_cls):
                # Copy (RS) to SPR.
                m.d.comb += [
                    self.pfv.rs.index.eq(self.insn.RS),
                    self.pfv.rs.r_stb.eq(1),
                    pfv_spr.w_mask.eq(~reserved_mask),
                    pfv_spr.w_data.eq(self.pfv.rs.r_data & ~reserved_mask),
                ]

            if isinstance(self.insn, mfspr_cls):
                # Copy SPR to (RT).
                m.d.comb += [
                    self.pfv.rt.index.eq(self.insn.RT),
                    self.pfv.rt.w_stb.eq(1),
                    pfv_spr.r_mask.eq(~reserved_mask),
                ]
                # In problem state, reading reserved bits returns 0.
                with m.If(self.pfv.msr.r_data.pr):
                    m.d.comb += self.pfv.rt.w_data.eq(pfv_spr.r_data & ~reserved_mask)
                with m.Else():
                    m.d.comb += self.pfv.rt.w_data.eq(pfv_spr.r_data)

        if isinstance(self.insn, (MTXER, MFXER)):
            xer_reserved_mask = Record(xer_layout)
            m.d.comb += [
                xer_reserved_mask._56.eq(Repl(1,  1)),
                xer_reserved_mask._46.eq(Repl(1,  2)),
                xer_reserved_mask._35.eq(Repl(1,  9)),
                xer_reserved_mask._0 .eq(Repl(1, 32)),
            ]
            mXspr_spec(self.pfv.xer, MTXER, MFXER, xer_reserved_mask)

        elif isinstance(self.insn, (MTLR, MFLR)):
            mXspr_spec(self.pfv.lr, MTLR, MFLR, Const(0, 64))

        elif isinstance(self.insn, (MTCTR, MFCTR)):
            mXspr_spec(self.pfv.ctr, MTCTR, MFCTR, Const(0, 64))

        elif isinstance(self.insn, (MTSRR0, MFSRR0)):
            mXspr_spec(self.pfv.srr0, MTSRR0, MFSRR0, Const(0, 64))

        elif isinstance(self.insn, (MTSRR1, MFSRR1)):
            # SRR1 bits should be treated as reserved if their corresponding MSR bits are also
            # reserved; which is implementation-specific.
            # We treat all bits as defined for now, but this may cause false positives.
            srr1_reserved_mask = Const(0, 64)
            mXspr_spec(self.pfv.srr1, MTSRR1, MFSRR1, srr1_reserved_mask)

        elif isinstance(self.insn, (MTTAR, MFTAR)):
            mXspr_spec(self.pfv.tar, MTTAR, MFTAR, Const(0, 64))

        else:
            assert False

        return m

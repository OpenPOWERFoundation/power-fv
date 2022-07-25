from amaranth import *

from power_fv import pfv
from power_fv.insn.const import *
from power_fv.intr import *

from . import InsnSpec
from .utils import iea, msr_to_srr1


__all__ = ["SystemCallSpec"]


class SystemCallSpec(InsnSpec, Elaboratable):
    def elaborate(self, platform):
        m = Module()

        m.d.comb += [
            self.pfv.stb .eq(1),
            self.pfv.insn.eq(Cat(Const(0, 32), self.insn.as_value())),
        ]

        if isinstance(self.insn, SC):
            m.d.comb += [
                self.pfv.intr.eq(1),
                self.pfv.nia .eq(INTR_SYSTEM_CALL.vector_addr),
                INTR_SYSTEM_CALL.write_msr(self.pfv.msr),

                self.pfv.msr .r_mask.sf.eq(1),
                self.pfv.srr0.w_mask.eq(Repl(1, 64)),
                self.pfv.srr0.w_data.eq(iea(self.pfv.cia + 4, self.pfv.msr.r_data.sf)),

                self.pfv.srr1.w_mask[63-36:64-33].eq(Repl(1, 4)),
                self.pfv.srr1.w_data[63-36:64-33].eq(0),
                self.pfv.srr1.w_mask[63-47:64-42].eq(Repl(1, 6)),
                self.pfv.srr1.w_data[63-47:64-42].eq(0),

                msr_to_srr1(self.pfv.msr, self.pfv.srr1,  0, 32),
                msr_to_srr1(self.pfv.msr, self.pfv.srr1, 37, 41),
                msr_to_srr1(self.pfv.msr, self.pfv.srr1, 48, 63),
            ]
        else:
            assert False

        return m

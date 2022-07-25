from amaranth import *

from power_fv import pfv
from power_fv.insn.const import *
from power_fv.intr import *

from . import InsnSpec
from .utils import iea, msr_to_srr1


__all__ = ["TrapSpec"]


class TrapSpec(InsnSpec, Elaboratable):
    def elaborate(self, platform):
        m = Module()

        m.d.comb += [
            self.pfv.stb .eq(1),
            self.pfv.insn.eq(Cat(Const(0, 32), self.insn.as_value())),
        ]

        src_a = Signal(signed(64))
        src_b = Signal(signed(64))
        cond  = Record([("gtu", 1), ("ltu", 1), ("eq_", 1), ("gts", 1), ("lts", 1)])
        trap  = Record.like(cond)

        # Operand A : EXTS((RA)(32:63))

        m.d.comb += [
            self.pfv.ra.index.eq(self.insn.RA),
            self.pfv.ra.r_stb.eq(1),
            src_a.eq(self.pfv.ra.r_data[:32].as_signed()),
        ]

        # Operand B : EXTS(SI) or EXTS((RB)(32:63))

        if isinstance(self.insn, TWI):
            m.d.comb += src_b.eq(self.insn.SI)
        elif isinstance(self.insn, TW):
            m.d.comb += [
                self.pfv.rb.index.eq(self.insn.RB),
                self.pfv.rb.r_stb.eq(1),
                src_b.eq(self.pfv.rb.r_data[:32].as_signed()),
            ]
        else:
            assert False

        # Compare operands

        m.d.comb += [
            cond.eq(self.insn.TO),

            trap.lts.eq(cond.lts & (src_a < src_b)),
            trap.gts.eq(cond.gts & (src_a > src_b)),
            trap.eq_.eq(cond.eq_ & (src_a == src_b)),
            trap.ltu.eq(cond.ltu & (src_a.as_unsigned() < src_b.as_unsigned())),
            trap.gtu.eq(cond.gtu & (src_a.as_unsigned() > src_b.as_unsigned())),
        ]

        # Trap if a condition is met

        m.d.comb += self.pfv.msr.r_mask.sf.eq(1)

        with m.If(trap.any()):
            m.d.comb += [
                self.pfv.intr.eq(1),
                self.pfv.nia .eq(INTR_PROGRAM.vector_addr),
                INTR_PROGRAM.write_msr(self.pfv.msr),

                self.pfv.srr0.w_mask.eq(Repl(1, 64)),
                self.pfv.srr0.w_data.eq(iea(self.pfv.cia, self.pfv.msr.r_data.sf)),

                self.pfv.srr1.w_mask[63-36:64-33].eq(0xf),
                self.pfv.srr1.w_data[63-36:64-33].eq(0x0),

                self.pfv.srr1.w_mask[63-42].eq(1),
                self.pfv.srr1.w_data[63-42].eq(0),
                self.pfv.srr1.w_mask[63-46:64-43].eq(Repl(1, 4)),
                self.pfv.srr1.w_data[63-46:64-43].eq(0b0001), # Trap type
                self.pfv.srr1.w_mask[63-47].eq(1),
                self.pfv.srr1.w_data[63-47].eq(0),

                msr_to_srr1(self.pfv.msr, self.pfv.srr1,  0, 32),
                msr_to_srr1(self.pfv.msr, self.pfv.srr1, 37, 41),
                msr_to_srr1(self.pfv.msr, self.pfv.srr1, 48, 63),
            ]
        with m.Else():
            m.d.comb += self.pfv.nia.eq(iea(self.pfv.cia + 4, self.pfv.msr.r_data.sf))

        return m

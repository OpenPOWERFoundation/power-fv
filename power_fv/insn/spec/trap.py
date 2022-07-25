from amaranth import *

from power_fv import pfv
from power_fv.insn.const import *

from . import InsnSpec
from .utils import iea


__all__ = ["TrapSpec"]


class TrapSpec(InsnSpec, Elaboratable):
    def elaborate(self, platform):
        m = Module()

        m.d.comb += [
            self.pfv.stb .eq(1),
            self.pfv.insn.eq(Cat(Const(0, 32), self.insn.as_value())),
            self.pfv.nia .eq(iea(self.pfv.cia + 4, self.pfv.msr.r_data.sf)),
            self.pfv.msr.r_mask.sf.eq(1),
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

        # Compare operands, then trap if a condition is met.

        m.d.comb += [
            cond.eq(self.insn.TO),

            trap.lts.eq(cond.lts & (src_a < src_b)),
            trap.gts.eq(cond.gts & (src_a > src_b)),
            trap.eq_.eq(cond.eq_ & (src_a == src_b)),
            trap.ltu.eq(cond.ltu & (src_a.as_unsigned() < src_b.as_unsigned())),
            trap.gtu.eq(cond.gtu & (src_a.as_unsigned() > src_b.as_unsigned())),

            self.pfv.intr.eq(trap.any()),
        ]

        return m

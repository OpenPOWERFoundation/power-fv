from amaranth import *

from power_fv import pfv
from power_fv.insn.const import *
from power_fv.intr import *
from power_fv.reg import msr_layout

from . import InsnSpec
from .utils import iea, msr_to_srr1


__all__ = ["MSRMoveSpec"]


class MSRMoveSpec(InsnSpec, Elaboratable):
    def elaborate(self, platform):
        m = Module()

        m.d.comb += [
            self.insn    .eq(self.pfv.insn[32:]),
            self.pfv.stb .eq(self.insn.is_valid() & ~self.pfv.insn[:32].any()),
            self.pfv.msr.r_mask.sf.eq(1),
            self.pfv.msr.r_mask.pr.eq(1)
        ]

        # Raise a Program Interrupt if executing from Problem State

        with m.If(self.pfv.msr.r_data.pr):
            m.d.comb += [
                self.pfv.intr.eq(1),
                self.pfv.nia .eq(INTR_PROGRAM.vector_addr),
                INTR_PROGRAM.write_msr(self.pfv.msr),

                self.pfv.srr0.w_mask.eq(Repl(1, 64)),
                self.pfv.srr0.w_data.eq(iea(self.pfv.cia, self.pfv.msr.r_data.sf)),

                self.pfv.srr1.w_mask[63-36:64-33].eq(Repl(1, 4)),
                self.pfv.srr1.w_data[63-36:64-33].eq(0),
                self.pfv.srr1.w_mask[63-42].eq(1),
                self.pfv.srr1.w_data[63-42].eq(0),
                self.pfv.srr1.w_mask[63-46:64-43].eq(Repl(1, 4)),
                self.pfv.srr1.w_data[63-46:64-43].eq(0b0010), # Privileged Instruction type
                self.pfv.srr1.w_mask[63-47].eq(1),
                self.pfv.srr1.w_data[63-47].eq(0),

                msr_to_srr1(self.pfv.msr, self.pfv.srr1,  0, 32),
                msr_to_srr1(self.pfv.msr, self.pfv.srr1, 37, 41),
                msr_to_srr1(self.pfv.msr, self.pfv.srr1, 48, 63),
            ]

        with m.Else():
            rs_as_msr  = Record(msr_layout)
            ultravisor = Signal()

            if isinstance(self.insn, MTMSR):
                m.d.comb += [
                    self.pfv.rs.index .eq(self.insn.RS),
                    self.pfv.rs.r_stb .eq(1),

                    self.pfv.msr.r_mask.s .eq(1),
                    self.pfv.msr.r_mask.hv.eq(1),

                    rs_as_msr .eq(self.pfv.rs.r_data),
                    ultravisor.eq(self.pfv.msr.r_data.s & self.pfv.msr.r_data.hv & ~rs_as_msr.pr),
                ]

                with m.If(self.insn.L):
                    # Write bits 48 62
                    m.d.comb += [
                        self.pfv.msr.w_mask.ee.eq(1),
                        self.pfv.msr.w_data.ee.eq(rs_as_msr.ee),
                        self.pfv.msr.w_mask.ri.eq(1),
                        self.pfv.msr.w_data.ri.eq(rs_as_msr.ri),
                    ]
                with m.Else():
                    # Write bits:
                    m.d.comb += [
                        # 48 58 59
                        self.pfv.msr.w_mask.ee .eq(1),
                        self.pfv.msr.w_data.ee .eq(rs_as_msr.ee | rs_as_msr.pr),
                        self.pfv.msr.w_mask.ir .eq(1),
                        self.pfv.msr.w_data.ir .eq((rs_as_msr.ir | rs_as_msr.pr) & ~ultravisor),
                        self.pfv.msr.w_mask.dr .eq(1),
                        self.pfv.msr.w_data.dr .eq((rs_as_msr.dr | rs_as_msr.pr) & ~ultravisor),
                        # 32:40
                        self.pfv.msr.w_mask._32.eq(Repl(1, 6)),
                        self.pfv.msr.w_data._32.eq(rs_as_msr._32),
                        self.pfv.msr.w_mask.vec.eq(1),
                        self.pfv.msr.w_data.vec.eq(rs_as_msr.vec),
                        self.pfv.msr.w_mask._39.eq(1),
                        self.pfv.msr.w_data._39.eq(rs_as_msr._39),
                        self.pfv.msr.w_mask.vsx.eq(1),
                        self.pfv.msr.w_data.vsx.eq(rs_as_msr.vsx),
                        # 42:47
                        self.pfv.msr.w_mask._42.eq(Repl(1, 6)),
                        self.pfv.msr.w_data._42.eq(rs_as_msr._42),
                        # 49:50
                        self.pfv.msr.w_mask.pr .eq(1),
                        self.pfv.msr.w_data.pr .eq(rs_as_msr.pr),
                        self.pfv.msr.w_mask.fp .eq(1),
                        self.pfv.msr.w_data.fp .eq(rs_as_msr.fp),
                        # 52:57
                        self.pfv.msr.w_mask.fe0.eq(1),
                        self.pfv.msr.w_data.fe0.eq(rs_as_msr.fe0),
                        self.pfv.msr.w_mask.te .eq(Repl(1, 2)),
                        self.pfv.msr.w_data.te .eq(rs_as_msr.te),
                        self.pfv.msr.w_mask.fe1.eq(1),
                        self.pfv.msr.w_data.fe1.eq(rs_as_msr.fe1),
                        self.pfv.msr.w_mask._56.eq(Repl(1, 2)),
                        self.pfv.msr.w_data._56.eq(rs_as_msr._56),
                        # 60:62
                        self.pfv.msr.w_mask._60.eq(1),
                        self.pfv.msr.w_data._60.eq(rs_as_msr._60),
                        self.pfv.msr.w_mask.pmm.eq(1),
                        self.pfv.msr.w_data.pmm.eq(rs_as_msr.pmm),
                        self.pfv.msr.w_mask.ri .eq(1),
                        self.pfv.msr.w_data.ri .eq(rs_as_msr.ri),
                    ]

            elif isinstance(self.insn, MFMSR):
                m.d.comb += [
                    self.pfv.msr.r_mask.eq(Repl(1, 64)),

                    self.pfv.rt.index .eq(self.insn.RT),
                    self.pfv.rt.w_stb .eq(1),
                    self.pfv.rt.w_data.eq(self.pfv.msr.r_data),
                ]

            else:
                assert False

            # Update NIA

            m.d.comb += self.pfv.nia.eq(iea(self.pfv.cia + 4, self.pfv.msr.r_data.sf))

        return m

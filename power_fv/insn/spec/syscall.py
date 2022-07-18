from amaranth import *

from power_fv import pfv
from power_fv.insn.const import *

from . import InsnSpec
from .utils import iea


__all__ = ["SystemCallSpec"]


class SystemCallSpec(InsnSpec, Elaboratable):
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

        if isinstance(self.insn, SC):
            def _msr_to_srr1(start, stop):
                stmts = [
                    self.pfv.msr .r_mask[63-stop:64-start].eq(Repl(1, stop-start+1)),
                    self.pfv.srr1.w_mask[63-stop:64-start].eq(Repl(1, stop-start+1)),
                    self.pfv.srr1.w_data[63-stop:64-start].eq(self.pfv.msr.r_data[63-stop:64-start]),
                ]
                return stmts

            m.d.comb += [
                self.pfv.srr0.w_mask.eq(Repl(1, 64)),
                self.pfv.srr0.w_data.eq(iea(self.pfv.cia + 4, self.pfv.msr.r_data.sf)),

                self.pfv.srr1.w_mask[63-36:64-33].eq(Repl(1, 4)),
                self.pfv.srr1.w_data[63-36:64-33].eq(0),
                self.pfv.srr1.w_mask[63-47:64-42].eq(Repl(1, 6)),
                self.pfv.srr1.w_data[63-47:64-42].eq(0),

                _msr_to_srr1( 0, 32),
                _msr_to_srr1(37, 41),
                _msr_to_srr1(48, 63),

                self.pfv.intr.eq(1),
                self.pfv.nia .eq(0xc00),
            ]

        else:
            assert False

        return m

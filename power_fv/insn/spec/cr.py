from amaranth import *
from amaranth.asserts import Assume
from amaranth.lib.coding import Encoder

from power_fv import pfv
from power_fv.insn.const import *
from power_fv.build.sby import SymbiYosysPlatform

from . import InsnSpec
from .utils import iea


__all__ = ["CRLogicalSpec", "CRMoveSpec"]


class CRLogicalSpec(InsnSpec, Elaboratable):
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
                self.pfv.cr.r_mask.bit_select(31-self.insn.BA, width=1).eq(1),
                self.pfv.cr.r_mask.bit_select(31-self.insn.BB, width=1).eq(1),

                src_a.eq(self.pfv.cr.r_data.bit_select(31-self.insn.BA, width=1)),
                src_b.eq(self.pfv.cr.r_data.bit_select(31-self.insn.BB, width=1)),
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
                self.pfv.cr.w_mask.bit_select(31-self.insn.BT, width=1).eq(1),
                self.pfv.cr.w_data.bit_select(31-self.insn.BT, width=1).eq(result),
            ]

        else:
            assert False

        return m


class CRMoveSpec(InsnSpec, Elaboratable):
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

        if isinstance(self.insn, MCRF):
            crf = Signal(4)
            m.d.comb += [
                self.pfv.cr.r_mask.word_select(7-self.insn.BFA, width=4).eq(0xf),
                crf.eq(self.pfv.cr.r_data.word_select(7-self.insn.BFA, width=4)),

                self.pfv.cr.w_mask.word_select(7-self.insn.BF,  width=4).eq(0xf),
                self.pfv.cr.w_data.word_select(7-self.insn.BF,  width=4).eq(crf),
            ]

        elif isinstance(self.insn, MCRXRX):
            crf = Record([("ca32", 1), ("ca", 1), ("ov32", 1), ("ov", 1)])

            m.d.comb += [
                self.pfv.xer.r_mask.ov  .eq(1),
                self.pfv.xer.r_mask.ov32.eq(1),
                self.pfv.xer.r_mask.ca  .eq(1),
                self.pfv.xer.r_mask.ca32.eq(1),

                crf.ov  .eq(self.pfv.xer.r_data.ov),
                crf.ov32.eq(self.pfv.xer.r_data.ov32),
                crf.ca  .eq(self.pfv.xer.r_data.ca),
                crf.ca32.eq(self.pfv.xer.r_data.ca32),

                self.pfv.cr.w_mask.word_select(7-self.insn.BF, width=4).eq(0xf),
                self.pfv.cr.w_data.word_select(7-self.insn.BF, width=4).eq(crf),
            ]

        elif isinstance(self.insn, MTOCRF):
            crf = Signal(4)

            m.submodules.fxm_enc = fxm_enc = Encoder(width=8)
            m.d.comb += [
                fxm_enc.i.eq(self.insn.FXM),

                self.pfv.rs.index.eq(self.insn.RS),
                self.pfv.rs.r_stb.eq(1),
                crf.eq(self.pfv.rs.r_data.word_select(fxm_enc.o, width=4)),

                self.pfv.cr.w_mask.word_select(fxm_enc.o, width=4).eq(0xf),
                self.pfv.cr.w_data.word_select(fxm_enc.o, width=4).eq(crf),
            ]

            # Unless exactly one FXM bit is set to 1, CR contents are undefined.
            if isinstance(platform, SymbiYosysPlatform):
                m.d.comb += Assume(~fxm_enc.n)

        elif isinstance(self.insn, MTCRF):
            m.d.comb += [
                self.pfv.rs.index.eq(self.insn.RS),
                self.pfv.rs.r_stb.eq(1),

                self.pfv.cr.w_mask.eq(Cat(Repl(b, 4) for b in self.insn.FXM)),
                self.pfv.cr.w_data.eq(self.pfv.rs.r_data[:32]),
            ]

        elif isinstance(self.insn, MFOCRF):
            crf = Signal(4)

            m.submodules.fxm_enc = fxm_enc = Encoder(width=8)
            m.d.comb += [
                fxm_enc.i.eq(self.insn.FXM),

                self.pfv.cr.r_mask.word_select(fxm_enc.o, width=4).eq(Mux(fxm_enc.n, 0x0, 0xf)),
                crf.eq(self.pfv.cr.r_data.word_select(fxm_enc.o, width=4)),

                self.pfv.rt.index.eq(self.insn.RT),
                self.pfv.rt.w_stb.eq(1),
                self.pfv.rt.w_data.word_select(fxm_enc.o, width=4).eq(crf),
            ]

            # Unless exactly one FXM bit is set to 1, RT contents are undefined.
            if isinstance(platform, SymbiYosysPlatform):
                m.d.comb += Assume(~fxm_enc.n)

        elif isinstance(self.insn, MFCR):
            m.d.comb += [
                self.pfv.cr.r_mask.eq(Repl(1, 32)),
                self.pfv.rt.index .eq(self.insn.RT),
                self.pfv.rt.w_stb .eq(1),
                self.pfv.rt.w_data.eq(self.pfv.cr.r_data),
            ]

        elif isinstance(self.insn, SETB):
            crf = Signal(4)
            m.d.comb += [
                self.pfv.cr.r_mask.word_select(7-self.insn.BFA, width=4).eq(0xf),
                crf.eq(self.pfv.cr.r_data.word_select(7-self.insn.BFA, width=4)),

                self.pfv.rt.index.eq(self.insn.RT),
                self.pfv.rt.w_stb.eq(1),
                self.pfv.rt.w_data.eq(Mux(crf[3-0], Repl(1, 64), crf[3-1])),
            ]

        elif isinstance(self.insn, (SETBC, SETBCR, SETNBC, SETNBCR)):
            crb = Signal()

            m.d.comb += [
                self.pfv.cr.r_mask.bit_select(31-self.insn.BI, width=1).eq(1),
                crb.eq(self.pfv.cr.r_data.bit_select(31-self.insn.BI, width=1)),

                self.pfv.rt.index.eq(self.insn.RT),
                self.pfv.rt.w_stb.eq(1),
            ]

            if isinstance(self.insn, SETBC):
                m.d.comb += self.pfv.rt.w_data.eq(crb)
            if isinstance(self.insn, SETBCR):
                m.d.comb += self.pfv.rt.w_data.eq(~crb)
            if isinstance(self.insn, SETNBC):
                m.d.comb += self.pfv.rt.w_data.eq(Mux(crb, -1, 0))
            if isinstance(self.insn, SETNBCR):
                m.d.comb += self.pfv.rt.w_data.eq(Mux(crb, 0, -1))

        else:
            assert False

        return m

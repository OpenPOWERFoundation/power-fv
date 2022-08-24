from amaranth import *
from amaranth.asserts import Assume

from power_fv import pfv
from power_fv.insn.const import *

from . import InsnSpec
from .utils import iea


__all__ = ["MultiplySpec", "DivideSpec"]


class MultiplySpec(InsnSpec, Elaboratable):
    def elaborate(self, platform):
        m = Module()

        m.d.comb += [
            self.insn    .eq(self.pfv.insn[32:]),
            self.pfv.stb .eq(self.insn.is_valid() & ~self.pfv.insn[:32].any()),
            self.pfv.intr.eq(0),
            self.pfv.nia .eq(iea(self.pfv.cia + 4, self.pfv.msr.r_data.sf)),
            self.pfv.msr.r_mask.sf.eq(1),
        ]

        src_a   = Signal(64)
        src_b   = Signal(64)
        result  = Signal(64)
        ov_32   = Signal()

        # Operand A : (RA) or EXTS((RA)(32:63)) or EXTZ((RA)(32:63))

        m.d.comb += [
            self.pfv.ra.index.eq(self.insn.RA),
            self.pfv.ra.r_stb.eq(1),
        ]

        if isinstance(self.insn, MULLI):
            m.d.comb += src_a.eq(self.pfv.ra.r_data)
        elif isinstance(self.insn, (
            MULLW , MULLW_ , MULLWO, MULLWO_,
            MULHW, MULHW_,
            )):
            m.d.comb += src_a.eq(self.pfv.ra.r_data[:32].as_signed())
        elif isinstance(self.insn, (MULHWU, MULHWU_)):
            m.d.comb += src_a.eq(self.pfv.ra.r_data[:32].as_unsigned())
        else:
            assert False

        # Operand B : EXTS(SI) or EXTS((RB)(32:63)) or EXTZ((RB)(32:63))

        if isinstance(self.insn, MULLI):
            m.d.comb += src_b.eq(self.insn.SI)
        elif isinstance(self.insn, (
            MULLW, MULLW_, MULLWO, MULLWO_,
            MULHW, MULHW_,
            )):
            m.d.comb += [
                self.pfv.rb.index .eq(self.insn.RB),
                self.pfv.rb.r_stb.eq(1),
                src_b.eq(self.pfv.rb.r_data[:32].as_signed()),
            ]
        elif isinstance(self.insn, (MULHWU, MULHWU_)):
            m.d.comb += [
                self.pfv.rb.index.eq(self.insn.RB),
                self.pfv.rb.r_stb.eq(1),
                src_b.eq(self.pfv.rb.r_data[:32].as_unsigned())
            ]
        else:
            assert False

        if self.pfv.muldiv_altops:
            altop_res  = Signal(64)
            altop_mask = Signal(64)
            ca_32      = Signal()

            if isinstance(self.insn, MULLI):
                m.d.comb += altop_mask.eq(0xef31a883837039a0)
            elif isinstance(self.insn, (MULLW, MULLW_)):
                m.d.comb += altop_mask.eq(0x4931591f31f56de1)
            elif isinstance(self.insn, (MULLWO, MULLWO_)):
                m.d.comb += altop_mask.eq(0x37291ea821fbaf9d)
            elif isinstance(self.insn, (MULHW, MULHW_)):
                m.d.comb += altop_mask.eq(0x3426dcf55920989c)
            elif isinstance(self.insn, (MULHWU, MULHWU_)):
                m.d.comb += altop_mask.eq(0x491edb8a5f695d49)
            else:
                assert False

            # Result : (Operand A + Operand B) ^ Altop Mask

            m.d.comb += [
                altop_res.eq(src_a + src_b),
                ca_32.eq(altop_res[32] ^ src_a[32] ^ src_b[32]),
                ov_32.eq((ca_32 ^ altop_res[31]) & ~(src_a[31] ^ src_b[31])),

                result.eq(altop_res ^ altop_mask),
            ]

        else:
            raise NotImplementedError

        # Write the result to RT

        m.d.comb += [
            self.pfv.rt.index .eq(self.insn.RT),
            self.pfv.rt.w_stb .eq(1),
            self.pfv.rt.w_data.eq(result),
        ]

        # Set XER.{SO,OV,OV32} if the result overflows 32 bits

        if isinstance(self.insn, (MULLWO, MULLWO_)):
            m.d.comb += [
                self.pfv.xer.w_mask.ov  .eq(1),
                self.pfv.xer.w_data.ov  .eq(ov_32),
                self.pfv.xer.w_mask.ov32.eq(1),
                self.pfv.xer.w_data.ov32.eq(ov_32),
            ]
            with m.If(ov_32):
                m.d.comb += [
                    self.pfv.xer.w_mask.so.eq(1),
                    self.pfv.xer.w_data.so.eq(1),
                ]

        # Write CR0

        if isinstance(self.insn, (MULLW_, MULLWO_, MULHW_, MULHWU_)):
            cr0_w_mask = Record([("so", 1), ("eq_", 1), ("gt", 1), ("lt", 1)])
            cr0_w_data = Record([("so", 1), ("eq_", 1), ("gt", 1), ("lt", 1)])

            m.d.comb += [
                self.pfv.xer.r_mask.so.eq(1),

                cr0_w_mask    .eq(0b1111),
                cr0_w_data.so .eq(Mux(self.pfv.xer.w_mask.so, self.pfv.xer.w_data.so, self.pfv.xer.r_data.so)),
                cr0_w_data.eq_.eq(~Mux(self.pfv.msr.r_data.sf, result[:64].any(), result[:32].any())),
                cr0_w_data.gt .eq(~(cr0_w_data.lt | cr0_w_data.eq_)),
                cr0_w_data.lt .eq(Mux(self.pfv.msr.r_data.sf, result[63], result[31])),

                self.pfv.cr.w_mask.cr0.eq(cr0_w_mask),
                self.pfv.cr.w_data.cr0.eq(cr0_w_data),
            ]

        return m


class DivideSpec(InsnSpec, Elaboratable):
    def elaborate(self, platform):
        m = Module()

        m.d.comb += [
            self.insn    .eq(self.pfv.insn[32:]),
            self.pfv.stb .eq(self.insn.is_valid() & ~self.pfv.insn[:32].any()),
            self.pfv.intr.eq(0),
            self.pfv.nia .eq(iea(self.pfv.cia + 4, self.pfv.msr.r_data.sf)),
            self.pfv.msr.r_mask.sf.eq(1),
        ]

        dividend = Signal(64)
        divisor  = Signal(64)
        result   = Signal(64)
        ov_32    = Signal()

        # Dividend : (RA)(32:63) or (RA)(32:63)<<32

        m.d.comb += [
            self.pfv.ra.index.eq(self.insn.RA),
            self.pfv.ra.r_stb.eq(1),
        ]

        if isinstance(self.insn, (DIVW, DIVW_, DIVWO, DIVWO_, MODSW)):
            m.d.comb += dividend.eq(self.pfv.ra.r_data[:32].as_signed())
        elif isinstance(self.insn, (DIVWU, DIVWU_, DIVWUO, DIVWUO_, MODUW)):
            m.d.comb += dividend.eq(self.pfv.ra.r_data[:32].as_unsigned())
        elif isinstance(self.insn, (
            DIVWE , DIVWE_ , DIVWEO , DIVWEO_ ,
            DIVWEU, DIVWEU_, DIVWEUO, DIVWEUO_,
            )):
            m.d.comb += dividend.eq(Cat(Const(0, 32), self.pfv.ra.r_data[:32]))
        else:
            assert False

        # Divisor : (RB)(32:63)

        m.d.comb += [
            self.pfv.rb.index.eq(self.insn.RB),
            self.pfv.rb.r_stb.eq(1),
        ]

        if isinstance(self.insn, (
            DIVW , DIVW_ , DIVWO , DIVWO_ ,
            DIVWE, DIVWE_, DIVWEO, DIVWEO_,
            MODSW,
            )):
            m.d.comb += divisor.eq(self.pfv.rb.r_data[:32].as_signed())
        elif isinstance(self.insn, (
            DIVWU , DIVWU_ , DIVWUO , DIVWUO_ ,
            DIVWEU, DIVWEU_, DIVWEUO, DIVWEUO_,
            MODUW ,
            )):
            m.d.comb += divisor.eq(self.pfv.rb.r_data[:32].as_unsigned())
        else:
            assert False

        if self.pfv.muldiv_altops:
            altop_mask = Signal(64)
            altop_res  = Signal(signed(64))
            ca_32      = Signal()

            if isinstance(self.insn, (DIVW, DIVW_)):
                m.d.comb += altop_mask.eq(0x75a5d4895a3e15ba)
            elif isinstance(self.insn, (DIVWO, DIVWO_)):
                m.d.comb += altop_mask.eq(0x7098f59fd4822d48)
            elif isinstance(self.insn, (DIVWU, DIVWU_)):
                m.d.comb += altop_mask.eq(0x769c76af68d11402)
            elif isinstance(self.insn, (DIVWUO, DIVWUO_)):
                m.d.comb += altop_mask.eq(0x6ec48c33b1fe6a8f)
            elif isinstance(self.insn, (DIVWE, DIVWE_)):
                m.d.comb += altop_mask.eq(0xdfd9d577965d84d2)
            elif isinstance(self.insn, (DIVWEO, DIVWEO_)):
                m.d.comb += altop_mask.eq(0x88ec39a41f3b07fd)
            elif isinstance(self.insn, (DIVWEU, DIVWEU_)):
                m.d.comb += altop_mask.eq(0x8fc71f88b966fcf0)
            elif isinstance(self.insn, (DIVWEUO, DIVWEUO_)):
                m.d.comb += altop_mask.eq(0x893cca367133b0d3)
            elif isinstance(self.insn, MODSW):
                m.d.comb += altop_mask.eq(0x5ba1758b11ae4e43)
            elif isinstance(self.insn, MODUW):
                m.d.comb += altop_mask.eq(0x1feb9d95f9f0cea5)
            else:
                assert False

            # Result : (Dividend - Divisor) ^ Altop Mask

            m.d.comb += [
                altop_res.eq(dividend.as_signed() - divisor.as_signed()),
                ca_32.eq(altop_res[32] ^ dividend[32] ^ divisor[32]),
                ov_32.eq((ca_32 ^ altop_res[31]) & ~(dividend[31] ^ divisor[31])),

                result.eq(altop_res ^ altop_mask),
            ]

        else:
            raise NotImplementedError

        # Write the result to RT

        m.d.comb += [
            self.pfv.rt.index .eq(self.insn.RT),
            self.pfv.rt.w_stb .eq(1),
            self.pfv.rt.w_data.eq(result),
        ]

        # Set XER.{SO,OV,OV32} if the result overflows 32 bits

        if isinstance(self.insn, (
            DIVWO , DIVWO_ , DIVWUO , DIVWUO_ ,
            DIVWEO, DIVWEO_, DIVWEUO, DIVWEUO_,
            )):
            m.d.comb += [
                self.pfv.xer.w_mask.ov  .eq(1),
                self.pfv.xer.w_data.ov  .eq(ov_32),
                self.pfv.xer.w_mask.ov32.eq(1),
                self.pfv.xer.w_data.ov32.eq(ov_32),
            ]
            with m.If(ov_32):
                m.d.comb += [
                    self.pfv.xer.w_mask.so.eq(1),
                    self.pfv.xer.w_data.so.eq(1),
                ]

        # Write CR0

        if isinstance(self.insn, (
            DIVW_ , DIVWO_ , DIVWU_ , DIVWUO_ ,
            DIVWE_, DIVWEO_, DIVWEU_, DIVWEUO_,
            )):
            cr0_w_mask = Record([("so", 1), ("eq_", 1), ("gt", 1), ("lt", 1)])
            cr0_w_data = Record([("so", 1), ("eq_", 1), ("gt", 1), ("lt", 1)])

            m.d.comb += [
                self.pfv.xer.r_mask.so.eq(1),

                cr0_w_mask    .eq(0b1111),
                cr0_w_data.so .eq(Mux(self.pfv.xer.w_mask.so, self.pfv.xer.w_data.so, self.pfv.xer.r_data.so)),
                cr0_w_data.eq_.eq(~Mux(self.pfv.msr.r_data.sf, result[:64].any(), result[:32].any())),
                cr0_w_data.gt .eq(~(cr0_w_data.lt | cr0_w_data.eq_)),
                cr0_w_data.lt .eq(Mux(self.pfv.msr.r_data.sf, result[63], result[31])),

                self.pfv.cr.w_mask.cr0.eq(cr0_w_mask),
                self.pfv.cr.w_data.cr0.eq(cr0_w_data),
            ]

        return m

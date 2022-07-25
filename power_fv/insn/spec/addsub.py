from amaranth import *

from power_fv import pfv
from power_fv.insn.const import *

from . import InsnSpec
from .utils import iea


__all__ = ["AddSubSpec"]


class AddSubSpec(InsnSpec, Elaboratable):
    def elaborate(self, platform):
        m = Module()

        m.d.comb += [
            self.pfv.stb .eq(1),
            self.pfv.insn.eq(Cat(Const(0, 32), self.insn.as_value())),
            self.pfv.intr.eq(0),
            self.pfv.nia .eq(iea(self.pfv.cia + 4, self.pfv.msr.r_data.sf)),
            self.pfv.msr.r_mask.sf.eq(1),
        ]

        src_a  = Signal(signed(64))
        src_b  = Signal(signed(64))
        src_c  = Signal()
        result = Signal(unsigned(65))

        ca_64  = Signal()
        ca_32  = Signal()
        ov_64  = Signal()
        ov_32  = Signal()

        # Operand A : (RA) or 0 or NIA or ~(RA)

        if isinstance(self.insn, (ADDI, ADDIS)):
            m.d.comb += [
                self.pfv.ra.index.eq(self.insn.RA),
                self.pfv.ra.r_stb.eq(self.insn.RA != 0),
                src_a.eq(Mux(self.insn.RA != 0, self.pfv.ra.r_data, 0)),
            ]

        elif isinstance(self.insn, ADDPCIS):
            m.d.comb += src_a.eq(self.pfv.nia)

        elif isinstance(self.insn, (
            ADD  , ADD_  , ADDO  , ADDO_  ,
            ADDIC, ADDIC_,
            ADDC , ADDC_ , ADDCO , ADDCO_ ,
            ADDE , ADDE_ , ADDEO , ADDEO_ ,
            ADDME, ADDME_, ADDMEO, ADDMEO_,
            ADDZE, ADDZE_, ADDZEO, ADDZEO_,
            ADDEX,
            )):
            m.d.comb += [
                self.pfv.ra.index.eq(self.insn.RA),
                self.pfv.ra.r_stb.eq(1),
                src_a.eq(self.pfv.ra.r_data),
            ]

        elif isinstance(self.insn, (
            SUBF  , SUBF_  , SUBFO  , SUBFO_  ,
            SUBFIC,
            SUBFC , SUBFC_ , SUBFCO , SUBFCO_ ,
            SUBFE , SUBFE_ , SUBFEO , SUBFEO_ ,
            SUBFME, SUBFME_, SUBFMEO, SUBFMEO_,
            SUBFZE, SUBFZE_, SUBFZEO, SUBFZEO_,
            NEG   , NEG_   , NEGO   , NEGO_   ,
            )):
            m.d.comb += [
                self.pfv.ra.index.eq(self.insn.RA),
                self.pfv.ra.r_stb.eq(1),
                src_a.eq(~self.pfv.ra.r_data),
            ]

        else:
            assert False

        # Operand B : SI or SI<<16 or D<<16 or (RB) or -1 or 0

        if isinstance(self.insn, (ADDI, ADDIC, ADDIC_, SUBFIC)):
            m.d.comb += src_b.eq(self.insn.SI)

        elif isinstance(self.insn, ADDIS):
            m.d.comb += src_b.eq(Cat(Const(0, 16), self.insn.SI).as_signed())

        elif isinstance(self.insn, ADDPCIS):
            imm_d = Signal(signed(16))
            m.d.comb += [
                imm_d.eq(Cat(self.insn.d2, self.insn.d1, self.insn.d0)),
                src_b.eq(Cat(Const(0, 16), imm_d).as_signed()),
            ]

        elif isinstance(self.insn, (
            ADD  , ADD_  , ADDO  , ADDO_  ,
            SUBF , SUBF_ , SUBFO , SUBFO_ ,
            ADDC , ADDC_ , ADDCO , ADDCO_ ,
            ADDE , ADDE_ , ADDEO , ADDEO_ ,
            SUBFC, SUBFC_, SUBFCO, SUBFCO_,
            SUBFE, SUBFE_, SUBFEO, SUBFEO_,
            ADDEX,
            )):
            m.d.comb += [
                self.pfv.rb.index.eq(self.insn.RB),
                self.pfv.rb.r_stb.eq(1),
                src_b.eq(self.pfv.rb.r_data),
            ]

        elif isinstance(self.insn, (
            ADDME , ADDME_ , ADDMEO , ADDMEO_ ,
            SUBFME, SUBFME_, SUBFMEO, SUBFMEO_,
            )):
            m.d.comb += src_b.eq(-1)

        elif isinstance(self.insn, (
            ADDZE , ADDZE_ , ADDZEO , ADDZEO_ ,
            SUBFZE, SUBFZE_, SUBFZEO, SUBFZEO_,
            NEG   , NEG_   , NEGO   , NEGO_   ,
            )):
            m.d.comb += src_b.eq(0)

        else:
            assert False

        # Operand C : 0 or 1 or XER.CA or XER.OV

        if isinstance(self.insn, (
            ADDI , ADDIS , ADDPCIS,
            ADD  , ADD_  , ADDO   , ADDO_ ,
            ADDIC, ADDIC_,
            ADDC , ADDC_ , ADDCO  , ADDCO_,
            )):
            m.d.comb += src_c.eq(0)

        elif isinstance(self.insn, (
            SUBF  , SUBF_ , SUBFO , SUBFO_ ,
            SUBFIC,
            SUBFC , SUBFC_, SUBFCO, SUBFCO_,
            NEG   , NEG_  , NEGO  , NEGO_  ,
            )):
            m.d.comb += src_c.eq(1)

        elif isinstance(self.insn, (
            ADDE  , ADDE_  , ADDEO  , ADDEO_  ,
            SUBFE , SUBFE_ , SUBFEO , SUBFEO_ ,
            ADDME , ADDME_ , ADDMEO , ADDMEO_ ,
            ADDZE , ADDZE_ , ADDZEO , ADDZEO_ ,
            SUBFME, SUBFME_, SUBFMEO, SUBFMEO_,
            SUBFZE, SUBFZE_, SUBFZEO, SUBFZEO_,
            )):
            m.d.comb += [
                self.pfv.xer.r_mask.ca.eq(1),
                src_c.eq(self.pfv.xer.r_data.ca),
            ]

        elif isinstance(self.insn, ADDEX):
            m.d.comb += [
                self.pfv.xer.r_mask.ov.eq(1),
                src_c.eq(self.pfv.xer.r_data.ov),
            ]

        else:
            assert False

        # Result : Operand A + Operand B + Operand C

        src_a_zext = Signal(unsigned(65))
        src_b_zext = Signal(unsigned(65))
        result     = Signal(unsigned(65))

        m.d.comb += [
            src_a_zext.eq(src_a.as_unsigned()),
            src_b_zext.eq(src_b.as_unsigned()),
            result.eq(src_a_zext + src_b_zext + src_c),

            ca_64.eq(result[64]),
            ca_32.eq(result[32] ^ src_a[32] ^ src_b[32]),
            ov_64.eq((ca_64 ^ result[63]) & ~(src_a[63] ^ src_b[63])),
            ov_32.eq((ca_32 ^ result[31]) & ~(src_a[31] ^ src_b[31])),

            self.pfv.rt.index .eq(self.insn.RT),
            self.pfv.rt.w_stb .eq(1),
            self.pfv.rt.w_data.eq(result[:64]),
        ]

        # Read XER.SO (to update CR0)

        if isinstance(self.insn, (
            ADD_   , ADDO_   , ADDIC_ ,
            SUBF_  , SUBFO_  ,
            ADDC_  , ADDCO_  , ADDE_  , ADDEO_  ,
            SUBFC_ , SUBFCO_ , SUBFE_ , SUBFEO_ ,
            ADDME_ , ADDMEO_ , ADDZE_ , ADDZEO_ ,
            SUBFME_, SUBFMEO_, SUBFZE_, SUBFZEO_,
            NEG_   , NEGO_   ,
            )):
            m.d.comb += self.pfv.xer.r_mask.so.eq(1)

        # Write XER.SO, XER.OV and XER.OV32

        if isinstance(self.insn, (
            ADDO  , ADDO_  , SUBFO  , SUBFO_  ,
            ADDCO , ADDCO_ , SUBFCO , SUBFCO_ ,
            ADDEO , ADDEO_ , SUBFEO , SUBFEO_ ,
            ADDMEO, ADDMEO_, SUBFMEO, SUBFMEO_,
            ADDZEO, ADDZEO_, SUBFZEO, SUBFZEO_,
            NEGO  , NEGO_  ,
            )):
            m.d.comb += [
                self.pfv.xer.w_mask.ov  .eq(1),
                self.pfv.xer.w_data.ov  .eq(Mux(self.pfv.msr.r_data.sf, ov_64, ov_32)),
                self.pfv.xer.w_mask.ov32.eq(1),
                self.pfv.xer.w_data.ov32.eq(ov_32),
            ]
            with m.If(self.pfv.xer.w_data.ov):
                m.d.comb += [
                    self.pfv.xer.w_mask.so.eq(1),
                    self.pfv.xer.w_data.so.eq(1),
                ]

        elif isinstance(self.insn, ADDEX):
            m.d.comb += [
                self.pfv.xer.w_mask.ov  .eq(1),
                self.pfv.xer.w_data.ov  .eq(Mux(self.pfv.msr.r_data.sf, ca_64, ca_32)),
                self.pfv.xer.w_mask.ov32.eq(1),
                self.pfv.xer.w_data.ov32.eq(ca_32),
            ]

        # Write XER.CA and XER.CA32

        if isinstance(self.insn, (
            ADDIC , ADDIC_ , SUBFIC ,
            ADDC  , ADDC_  , ADDCO  , ADDCO_  ,
            SUBFC , SUBFC_ , SUBFCO , SUBFCO_ ,
            ADDE  , ADDE_  , ADDEO  , ADDEO_  ,
            SUBFE , SUBFE_ , SUBFEO , SUBFEO_ ,
            ADDME , ADDME_ , ADDMEO , ADDMEO_ ,
            SUBFME, SUBFME_, SUBFMEO, SUBFMEO_,
            ADDZE , ADDZE_ , ADDZEO , ADDZEO_ ,
            SUBFZE, SUBFZE_, SUBFZEO, SUBFZEO_,
            )):
            m.d.comb += [
                self.pfv.xer.w_mask.ca  .eq(1),
                self.pfv.xer.w_data.ca  .eq(Mux(self.pfv.msr.r_data.sf, ca_64, ca_32)),
                self.pfv.xer.w_mask.ca32.eq(1),
                self.pfv.xer.w_data.ca32.eq(ca_32),
            ]

        # Write CR0

        if isinstance(self.insn, (
            ADD_   , ADDO_   , ADDIC_ ,
            SUBF_  , SUBFO_  ,
            ADDC_  , ADDCO_  , ADDE_  , ADDEO_  ,
            SUBFC_ , SUBFCO_ , SUBFE_ , SUBFEO_ ,
            ADDME_ , ADDMEO_ , ADDZE_ , ADDZEO_ ,
            SUBFME_, SUBFMEO_, SUBFZE_, SUBFZEO_,
            NEG_   , NEGO_   ,
            )):
            cr0_w_mask = Record([("so", 1), ("eq_", 1), ("gt", 1), ("lt", 1)])
            cr0_w_data = Record([("so", 1), ("eq_", 1), ("gt", 1), ("lt", 1)])

            m.d.comb += [
                cr0_w_mask    .eq(0b1111),
                cr0_w_data.so .eq(Mux(self.pfv.xer.w_mask.so, self.pfv.xer.w_data.so, self.pfv.xer.r_data.so)),
                cr0_w_data.eq_.eq(~Mux(self.pfv.msr.r_data.sf, result[:64].any(), result[:32].any())),
                cr0_w_data.gt .eq(~(cr0_w_data.lt | cr0_w_data.eq_)),
                cr0_w_data.lt .eq(Mux(self.pfv.msr.r_data.sf, result[63], result[31])),

                self.pfv.cr.w_mask.cr0.eq(cr0_w_mask),
                self.pfv.cr.w_data.cr0.eq(cr0_w_data),
            ]

        return m

from amaranth import *
from amaranth.asserts import *

from .. import PowerFVCheck
from ... import pfv, tb

from ._fmt  import *
from ._insn import *


__all__ = ["AddSubtractSpec", "AddSubtractCheck"]


class AddSubtractSpec(Elaboratable):
    def __init__(self, insn_cls, post):
        self.insn_cls = insn_cls
        self.pfv      = pfv.Interface()
        self.post     = tb.Trigger(cycle=post)

    def triggers(self):
        yield self.post

    def elaborate(self, platform):
        m = Module()

        spec_insn = self.insn_cls()

        with m.If(self.post.stb):
            m.d.sync += [
                Assume(self.pfv.stb),
                Assume(self.pfv.insn[32:] == spec_insn),
            ]

        spec_ra_r_stb   = Signal()
        spec_rb_r_stb   = Signal()
        spec_rt_w_stb   = Signal()
        spec_rt_w_data  = Signal(64)
        spec_cr_w_stb   = Signal( 8)
        spec_cr_w_data  = Signal(32)
        spec_msr_r_mask = Signal(64)
        spec_xer_r_mask = Signal(64)
        spec_xer_w_mask = Signal(64)
        spec_xer_w_data = Signal(64)

        src_a  = Signal(signed(64))
        src_b  = Signal(signed(64))
        src_c  = Signal()
        result = Signal(unsigned(65))

        ca_64  = Signal()
        ca_32  = Signal()
        ov_64  = Signal()
        ov_32  = Signal()

        # Operand A : (RA) or 0 or NIA or ~(RA)

        if isinstance(spec_insn, (ADDI, ADDIS)):
            m.d.comb += [
                spec_ra_r_stb.eq(spec_insn.ra != 0),
                src_a.eq(Mux(spec_insn.ra != 0, self.pfv.ra.r_data, 0)),
            ]
        elif isinstance(spec_insn, ADDPCIS):
            m.d.comb += [
                spec_ra_r_stb.eq(0),
                src_a.eq(self.pfv.nia),
            ]
        elif isinstance(spec_insn, (
            ADD  , ADD_  , ADDO  , ADDO_  ,
            ADDIC, ADDIC_,
            ADDC , ADDC_ , ADDCO , ADDCO_ ,
            ADDE , ADDE_ , ADDEO , ADDEO_ ,
            ADDME, ADDME_, ADDMEO, ADDMEO_,
            ADDZE, ADDZE_, ADDZEO, ADDZEO_,
            ADDEX,
            )):
            m.d.comb += [
                spec_ra_r_stb.eq(1),
                src_a.eq(self.pfv.ra.r_data),
            ]
        elif isinstance(spec_insn, (
            SUBF  , SUBF_  , SUBFO  , SUBFO_  ,
            SUBFIC,
            SUBFC , SUBFC_ , SUBFCO , SUBFCO_ ,
            SUBFE , SUBFE_ , SUBFEO , SUBFEO_ ,
            SUBFME, SUBFME_, SUBFMEO, SUBFMEO_,
            SUBFZE, SUBFZE_, SUBFZEO, SUBFZEO_,
            NEG   , NEG_   , NEGO   , NEGO_   ,
            )):
            m.d.comb += [
                spec_ra_r_stb.eq(1),
                src_a.eq(~self.pfv.ra.r_data),
            ]
        else:
            assert False

        # Operand B : SI or SI<<16 or D<<16 or (RB) or -1 or 0

        if isinstance(spec_insn, (ADDI, ADDIC, ADDIC_, SUBFIC)):
            m.d.comb += [
                spec_rb_r_stb.eq(0),
                src_b.eq(spec_insn.si),
            ]
        elif isinstance(spec_insn, ADDIS):
            m.d.comb += [
                spec_rb_r_stb.eq(0),
                src_b.eq(Cat(Const(0, 16), spec_insn.si).as_signed()),
            ]
        elif isinstance(spec_insn, ADDPCIS):
            imm_d = Signal(signed(16))
            m.d.comb += [
                spec_rb_r_stb.eq(0),
                imm_d.eq(Cat(spec_insn.d2, spec_insn.d1, spec_insn.d0)),
                src_b.eq(Cat(Const(0, 16), imm_d).as_signed()),
            ]
        elif isinstance(spec_insn, (
            ADD  , ADD_  , ADDO  , ADDO_  ,
            SUBF , SUBF_ , SUBFO , SUBFO_ ,
            ADDC , ADDC_ , ADDCO , ADDCO_ ,
            ADDE , ADDE_ , ADDEO , ADDEO_ ,
            SUBFC, SUBFC_, SUBFCO, SUBFCO_,
            SUBFE, SUBFE_, SUBFEO, SUBFEO_,
            ADDEX,
            )):
            m.d.comb += [
                spec_rb_r_stb.eq(1),
                src_b.eq(self.pfv.rb.r_data),
            ]
        elif isinstance(spec_insn, (
            ADDME , ADDME_ , ADDMEO , ADDMEO_ ,
            SUBFME, SUBFME_, SUBFMEO, SUBFMEO_,
            )):
            m.d.comb += [
                spec_rb_r_stb.eq(0),
                src_b.eq(-1),
            ]
        elif isinstance(spec_insn, (
            ADDZE , ADDZE_ , ADDZEO , ADDZEO_ ,
            SUBFZE, SUBFZE_, SUBFZEO, SUBFZEO_,
            NEG   , NEG_   , NEGO   , NEGO_   ,
            )):
            m.d.comb += [
                spec_rb_r_stb.eq(0),
                src_b.eq(0),
            ]
        else:
            assert False

        # Operand C : 0 or 1 or XER.CA or XER.OV

        if isinstance(spec_insn, (
            ADDI , ADDIS , ADDPCIS,
            ADD  , ADD_  , ADDO   , ADDO_ ,
            ADDIC, ADDIC_,
            ADDC , ADDC_ , ADDCO  , ADDCO_,
            )):
            m.d.comb += src_c.eq(0)
        elif isinstance(spec_insn, (
            SUBF  , SUBF_ , SUBFO , SUBFO_ ,
            SUBFIC,
            SUBFC , SUBFC_, SUBFCO, SUBFCO_,
            NEG   , NEG_  , NEGO  , NEGO_  ,
            )):
            m.d.comb += src_c.eq(1)
        elif isinstance(spec_insn, (
            ADDE  , ADDE_  , ADDEO  , ADDEO_  ,
            SUBFE , SUBFE_ , SUBFEO , SUBFEO_ ,
            ADDME , ADDME_ , ADDMEO , ADDMEO_ ,
            ADDZE , ADDZE_ , ADDZEO , ADDZEO_ ,
            SUBFME, SUBFME_, SUBFMEO, SUBFMEO_,
            SUBFZE, SUBFZE_, SUBFZEO, SUBFZEO_,
            )):
            m.d.comb += [
                spec_xer_r_mask[63 - 34].eq(1), # XER.CA
                src_c.eq(self.pfv.xer.r_data[63 - 34]),
            ]
        elif isinstance(spec_insn, ADDEX):
            m.d.comb += [
                spec_xer_r_mask[63 - 33].eq(1), # XER.OV
                src_c.eq(self.pfv.xer.r_data[63 - 33]),
            ]
        else:
            assert False

        # Result : Operand A + Operand B + Operand C

        tmp_a = Signal(unsigned(65))
        tmp_b = Signal(unsigned(65))

        m.d.comb += [
            tmp_a .eq(src_a.as_unsigned()),
            tmp_b .eq(src_b.as_unsigned()),
            result.eq(tmp_a + tmp_b + src_c),

            ca_64.eq(result[64]),
            ca_32.eq(result[32] ^ src_a[32] ^ src_b[32]),
            ov_64.eq((ca_64 ^ result[63]) & ~(src_a[63] ^ src_b[63])),
            ov_32.eq((ca_32 ^ result[31]) & ~(src_a[31] ^ src_b[31])),
        ]

        # GPRs

        m.d.comb += [
            spec_rt_w_stb .eq(1),
            spec_rt_w_data.eq(result[:64]),
        ]

        with m.If(self.post.stb & ~self.pfv.intr):
            m.d.sync += [
                Assert(spec_ra_r_stb.implies(self.pfv.ra.r_stb)),
                Assert(spec_rb_r_stb.implies(self.pfv.rb.r_stb)),
                Assert(self.pfv.rt.w_stb == spec_rt_w_stb),
                Assert(spec_rt_w_stb.implies(self.pfv.rt.w_data == spec_rt_w_data)),
            ]

        # MSR

        msr_r_sf = Signal()

        m.d.comb += [
            spec_msr_r_mask[63 - 0].eq(1),
            msr_r_sf.eq(self.pfv.msr.r_data[63 - 0]),
        ]

        with m.If(self.post.stb & ~self.pfv.intr):
            m.d.sync += Assert((self.pfv.msr.r_mask & spec_msr_r_mask) == spec_msr_r_mask)

        # XER

        xer_r_so   = Signal()
        xer_w_so   = Signal()
        xer_w_ov   = Signal()
        xer_w_ca   = Signal()
        xer_w_ov32 = Signal()
        xer_w_ca32 = Signal()

        m.d.comb += [
            xer_r_so  .eq(self.pfv.xer.r_data[63 - 32]),
            xer_w_so  .eq(xer_w_ov),
            xer_w_ov  .eq(Mux(msr_r_sf, ov_64, ov_32)),
            xer_w_ca  .eq(Mux(msr_r_sf, ca_64, ca_32)),
            xer_w_ov32.eq(ov_32),
            xer_w_ca32.eq(ca_32),
        ]

        if isinstance(spec_insn, (
            ADD_   , ADDO_   , ADDIC_ ,
            SUBF_  , SUBFO_  ,
            ADDC_  , ADDCO_  , ADDE_  , ADDEO_  ,
            SUBFC_ , SUBFCO_ , SUBFE_ , SUBFEO_ ,
            ADDME_ , ADDMEO_ , ADDZE_ , ADDZEO_ ,
            SUBFME_, SUBFMEO_, SUBFZE_, SUBFZEO_,
            NEG_   , NEGO_   ,
            )):
            # Read XER.SO (to update CR0)
            m.d.comb += spec_xer_r_mask[63 - 32].eq(1)

        if isinstance(spec_insn, (
            ADDO  , ADDO_  , SUBFO  , SUBFO_  ,
            ADDCO , ADDCO_ , SUBFCO , SUBFCO_ ,
            ADDEO , ADDEO_ , SUBFEO , SUBFEO_ ,
            ADDMEO, ADDMEO_, SUBFMEO, SUBFMEO_,
            ADDZEO, ADDZEO_, SUBFZEO, SUBFZEO_,
            NEGO  , NEGO_  ,
            )):
            # Set XER.SO
            m.d.comb += [
                spec_xer_w_mask[63 - 32].eq(xer_w_so),
                spec_xer_w_data[63 - 32].eq(xer_w_so),
            ]

        if isinstance(spec_insn, (
            ADDO  , ADDO_  , SUBFO  , SUBFO_  ,
            ADDCO , ADDCO_ , SUBFCO , SUBFCO_ ,
            ADDEO , ADDEO_ , SUBFEO , SUBFEO_ ,
            ADDMEO, ADDMEO_, SUBFMEO, SUBFMEO_,
            ADDZEO, ADDZEO_, SUBFZEO, SUBFZEO_,
            ADDEX ,
            NEGO  , NEGO_  ,
            )):
            # Write XER.OV and XER.OV32
            m.d.comb += [
                spec_xer_w_mask[63 - 33].eq(1),
                spec_xer_w_data[63 - 33].eq(xer_w_ov),
                spec_xer_w_mask[63 - 44].eq(1),
                spec_xer_w_data[63 - 44].eq(xer_w_ov32),
            ]

        if isinstance(spec_insn, (
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
            # Write XER.CA and XER.CA32
            m.d.comb += [
                spec_xer_w_mask[63 - 34].eq(1),
                spec_xer_w_data[63 - 34].eq(xer_w_ca),
                spec_xer_w_mask[63 - 45].eq(1),
                spec_xer_w_data[63 - 45].eq(xer_w_ca32),
            ]

        keep_xer_w_mask = Signal(64)
        keep_xer_w_data = Signal(64)

        m.d.comb += [
            keep_xer_w_mask.eq(self.pfv.xer.w_mask & ~spec_xer_w_mask),
            keep_xer_w_data.eq(self.pfv.xer.r_data &  keep_xer_w_mask),
        ]

        with m.If(self.post.stb & ~self.pfv.intr):
            m.d.sync += [
                Assert((self.pfv.xer.r_mask & spec_xer_r_mask) == spec_xer_r_mask),
                Assert((self.pfv.xer.w_mask & spec_xer_w_mask) == spec_xer_w_mask),
                Assert((self.pfv.xer.w_data & spec_xer_w_mask) == spec_xer_w_data),
                Assert((self.pfv.xer.r_mask & keep_xer_w_mask) == keep_xer_w_mask),
                Assert((self.pfv.xer.w_data & keep_xer_w_mask) == keep_xer_w_data),
            ]

        # CR

        cr0_w_lt = Signal()
        cr0_w_gt = Signal()
        cr0_w_eq = Signal()
        cr0_w_so = Signal()

        m.d.comb += [
            cr0_w_lt.eq(Mux(msr_r_sf, result[63], result[31])),
            cr0_w_gt.eq(~(cr0_w_lt | cr0_w_eq)),
            cr0_w_eq.eq(~Mux(msr_r_sf, result[:64].any(), result[:32].any())),
            cr0_w_so.eq(Mux(spec_xer_w_mask[63 - 32], xer_w_so, xer_r_so)),
        ]

        if isinstance(spec_insn, (
            ADD_   , ADDO_   , ADDIC_ ,
            SUBF_  , SUBFO_  ,
            ADDC_  , ADDCO_  , ADDE_  , ADDEO_  ,
            SUBFC_ , SUBFCO_ , SUBFE_ , SUBFEO_ ,
            ADDME_ , ADDMEO_ , ADDZE_ , ADDZEO_ ,
            SUBFME_, SUBFMEO_, SUBFZE_, SUBFZEO_,
            NEG_   , NEGO_   ,
            )):
            # Write CR0
            m.d.comb += [
                spec_cr_w_stb [ 7 - 0].eq(1),
                spec_cr_w_data[31 - 0].eq(cr0_w_lt),
                spec_cr_w_data[31 - 1].eq(cr0_w_gt),
                spec_cr_w_data[31 - 2].eq(cr0_w_eq),
                spec_cr_w_data[31 - 3].eq(cr0_w_so),
            ]

        spec_cr_w_mask = Signal(32)
        m.d.comb += spec_cr_w_mask.eq(Cat(Repl(s, 4) for s in spec_cr_w_stb))

        with m.If(self.post.stb & ~self.pfv.intr):
            m.d.sync += [
                Assert(self.pfv.cr.w_stb == spec_cr_w_stb),
                Assert((self.pfv.cr.w_data & spec_cr_w_mask) == spec_cr_w_data),
            ]

        return m


class AddSubtractCheck(PowerFVCheck, name="_insn_addsub"):
    def __init_subclass__(cls, name, insn_cls):
        super().__init_subclass__(name)
        cls.insn_cls = insn_cls

    def get_testbench(self, dut, post):
        tb_spec = AddSubtractSpec(self.insn_cls, post)
        tb_top  = tb.Testbench(tb_spec, dut)
        return tb_top

from amaranth import *
from amaranth.asserts import *

from .. import PowerFVCheck
from ... import pfv, tb
from ...utils import iea_mask

from ._fmt  import *
from ._insn import *


__all__ = ["BranchSpec", "BranchCheck"]


class BranchSpec(Elaboratable):
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
                Assert(self.pfv.msr.w_mask[63 - 0]), # MSR.SF
            ]

        msr_w_sf = Signal()
        m.d.comb += msr_w_sf.eq(self.pfv.msr.w_data[63 - 0])

        if isinstance(spec_insn, (Instruction_B, Instruction_XL_bc)):
            bo_valid_patterns = [
                "001--",
                "011--",
                "1-1--",
            ]
            if not isinstance(spec_insn, (BCCTR, BCCTRL)):
                # bcctr/bcctrl forms with BO(2)=0 ("decrement and test CTR") are illegal.
                bo_valid_patterns += [
                    "0000-",
                    "0001-",
                    "0100-",
                    "0101-",
                    "1-00-",
                    "1-01-",
                ]

            bo_invalid = Signal()
            m.d.comb += bo_invalid.eq(~spec_insn.bo.matches(*bo_valid_patterns))

            with m.If(self.post.stb):
                m.d.sync += Assert(bo_invalid.implies(self.pfv.intr))

        # NIA

        spec_nia = Signal(unsigned(64))
        taken    = Signal()
        offset   = Signal(signed(62))
        target   = Signal(signed(64))

        if isinstance(spec_insn, Instruction_I):
            m.d.comb += [
                taken .eq(1),
                offset.eq(spec_insn.li)
            ]

        elif isinstance(spec_insn, (Instruction_B, Instruction_XL_bc)):
            cond_bit = Signal()
            ctr_any  = Signal()
            cond_ok  = Signal()
            ctr_ok   = Signal()

            m.d.comb += [
                cond_bit.eq(self.pfv.cr.r_data[::-1].bit_select(spec_insn.bi, width=1)),
                ctr_any .eq( self.pfv.ctr.w_data[:32].any() |
                            (self.pfv.ctr.w_data[32:].any() & msr_w_sf)),
                cond_ok .eq(spec_insn.bo[4-0] | (spec_insn.bo[4-1] == cond_bit)),
                ctr_ok  .eq(spec_insn.bo[4-2] | (ctr_any ^ spec_insn.bo[4-3])),
            ]

            if isinstance(spec_insn, (BCCTR, BCCTRL)):
                m.d.comb += taken.eq(cond_ok)
            else:
                m.d.comb += taken.eq(cond_ok & ctr_ok)

            if isinstance(spec_insn, Instruction_B):
                m.d.comb += offset.eq(spec_insn.bd)
            elif isinstance(spec_insn, (BCLR, BCLRL)):
                m.d.comb += offset.eq(self.pfv.lr .r_data[2:])
            elif isinstance(spec_insn, (BCCTR, BCCTRL)):
                m.d.comb += offset.eq(self.pfv.ctr.r_data[2:])
            elif isinstance(spec_insn, (BCTAR, BCTARL)):
                m.d.comb += offset.eq(self.pfv.tar.r_data[2:])
            else:
                assert False

        else:
            assert False

        with m.If(taken):
            if isinstance(spec_insn, (Instruction_I, Instruction_B)) and spec_insn.aa.value == 0:
                m.d.comb += target.eq(self.pfv.cia + (offset << 2))
            else:
                m.d.comb += target.eq(offset << 2)
        with m.Else():
            m.d.comb += target.eq(self.pfv.cia + 4)

        m.d.comb += spec_nia.eq(iea_mask(target, msr_w_sf))

        with m.If(self.post.stb & ~self.pfv.intr):
            m.d.sync += Assert(self.pfv.nia == spec_nia)

        # CR

        spec_cr_r_stb = Signal(8)

        if isinstance(spec_insn, Instruction_I):
            m.d.comb += spec_cr_r_stb.eq(0)
        elif isinstance(spec_insn, (Instruction_B, Instruction_XL_bc)):
            m.d.comb += spec_cr_r_stb[::-1].bit_select(spec_insn.bi[2:], width=1).eq(1)
        else:
            assert False

        with m.If(self.post.stb & ~self.pfv.intr):
            for i, spec_cr_r_stb_bit in enumerate(spec_cr_r_stb):
                pfv_cr_r_stb_bit = self.pfv.cr.r_stb[i]
                m.d.sync += Assert(spec_cr_r_stb_bit.implies(pfv_cr_r_stb_bit))

        # LR

        spec_lr_r_stb  = Signal()
        spec_lr_w_stb  = Signal()

        spec_lr_r_mask = Signal(64)
        spec_lr_w_mask = Signal(64)
        spec_lr_w_data = Signal(64)

        if isinstance(spec_insn, (Instruction_I, Instruction_B)):
            m.d.comb += spec_lr_r_stb.eq(0)
        elif isinstance(spec_insn, (Instruction_XL_bc)):
            if isinstance(spec_insn, (BCLR, BCLRL)):
                m.d.comb += spec_lr_r_stb.eq(1)
            else:
                m.d.comb += spec_lr_r_stb.eq(0)
        else:
            assert False

        m.d.comb += spec_lr_w_stb.eq(spec_insn.lk)

        cia_4 = Signal(unsigned(64))
        m.d.comb += cia_4.eq(self.pfv.cia + 4)

        m.d.comb += [
            spec_lr_r_mask.eq(Repl(spec_lr_r_stb, 64)),
            spec_lr_w_mask.eq(Repl(spec_lr_w_stb, 64)),
            spec_lr_w_data.eq(iea_mask(cia_4, msr_w_sf)),
        ]

        with m.If(self.post.stb & ~self.pfv.intr):
            m.d.sync += [
                Assert((self.pfv.lr.r_mask & spec_lr_r_mask) == spec_lr_r_mask),
                Assert(self.pfv.lr.w_mask == spec_lr_w_mask),
                Assert((self.pfv.lr.w_data & spec_lr_w_mask) == (spec_lr_w_data & spec_lr_w_mask)),
            ]

        # CTR

        spec_ctr_r_stb  = Signal()
        spec_ctr_w_stb  = Signal()

        spec_ctr_r_mask = Signal(64)
        spec_ctr_w_mask = Signal(64)
        spec_ctr_w_data = Signal(64)

        if isinstance(spec_insn, Instruction_I):
            m.d.comb += spec_ctr_r_stb.eq(0)
        elif isinstance(spec_insn, Instruction_B):
            m.d.comb += spec_ctr_r_stb.eq(~spec_insn.bo[4-2])
        elif isinstance(spec_insn, Instruction_XL_bc):
            if isinstance(spec_insn, (BCCTR, BCCTRL)):
                m.d.comb += spec_ctr_r_stb.eq(1)
            else:
                m.d.comb += spec_ctr_r_stb.eq(~spec_insn.bo[4-2])
        else:
            assert False

        if isinstance(spec_insn, Instruction_I):
            m.d.comb += spec_ctr_w_stb.eq(0)
        elif isinstance(spec_insn, Instruction_B):
            m.d.comb += spec_ctr_w_stb.eq(~spec_insn.bo[4-2])
        elif isinstance(spec_insn, Instruction_XL_bc):
            if isinstance(spec_insn, (BCCTR, BCCTRL)):
                m.d.comb += spec_ctr_w_stb.eq(0)
            else:
                m.d.comb += spec_ctr_w_stb.eq(~spec_insn.bo[4-2])
        else:
            assert False

        m.d.comb += [
            spec_ctr_r_mask.eq(Repl(spec_ctr_r_stb, 64)),
            spec_ctr_w_mask.eq(Repl(spec_ctr_w_stb, 64)),
            spec_ctr_w_data.eq(self.pfv.ctr.r_data - 1),
        ]

        with m.If(self.post.stb & ~self.pfv.intr):
            m.d.sync += [
                Assert((self.pfv.ctr.r_mask & spec_ctr_r_mask) == spec_ctr_r_mask),
                Assert(self.pfv.ctr.w_mask == spec_ctr_w_mask),
                Assert((self.pfv.ctr.w_data & spec_ctr_w_mask) == (spec_ctr_w_data & spec_ctr_w_mask)),
            ]

        # TAR

        spec_tar_r_stb  = Signal()
        spec_tar_r_mask = Signal(64)

        if isinstance(spec_insn, (Instruction_I, Instruction_B)):
            m.d.comb += spec_tar_r_stb.eq(0)
        elif isinstance(spec_insn, (Instruction_XL_bc)):
            if isinstance(spec_insn, (BCTAR, BCTARL)):
                m.d.comb += spec_tar_r_stb.eq(1)
            else:
                m.d.comb += spec_tar_r_stb.eq(0)
        else:
            assert False

        m.d.comb += spec_tar_r_mask.eq(Repl(spec_tar_r_stb, 64))

        with m.If(self.post.stb & ~self.pfv.intr):
            m.d.sync += Assert((self.pfv.tar.r_mask & spec_tar_r_mask) == spec_tar_r_mask)

        return m


class BranchCheck(PowerFVCheck, name="_insn_branch"):
    def __init_subclass__(cls, name, insn_cls):
        super().__init_subclass__(name)
        cls.insn_cls = insn_cls

    def get_testbench(self, dut, post):
        tb_spec = BranchSpec(self.insn_cls, post)
        tb_top  = tb.Testbench(tb_spec, dut)
        return tb_top

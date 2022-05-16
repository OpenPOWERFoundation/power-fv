from amaranth import *
from amaranth.asserts import *

from .. import pfv
from ..insn import *


__all__ = ["Check"]


class Check(Elaboratable):
    _insn_cls = None

    def __init_subclass__(cls, *, insn_cls):
        cls._insn_cls = insn_cls

    def __init__(self):
        self.pfv  = pfv.Interface()
        self.trig = Record([
            ("pre",  1),
            ("post", 1),
        ])

    def elaborate(self, platform):
        m = Module()

        # TODO:
        # - support MSR (stop assuming 64-bit mode)
        # - support interrupts (detect illegal forms)

        spec_insn = self._insn_cls()

        with m.If(self.trig.post):
            m.d.sync += [
                Assume(self.pfv.stb),
                Assume(self.pfv.insn[32:] == spec_insn),
            ]

        if isinstance(spec_insn, (Instruction_B, Instruction_XL_b)):
            bo_valid_patterns = [
                "0000-",
                "0001-",
                "001--",
                "0100-",
                "0101-",
                "011--",
                "1-00-",
                "1-01-"
            ]
            if not isinstance(spec_insn, Instruction_B):
                # "Branch always" mnemonics are undefined for B-form conditional branches.
                # (Appendix C.2.2, Book I)
                bo_valid_patterns.append("1-1--")

            bo_valid = Signal()
            m.d.comb += bo_valid.eq(spec_insn.bo.matches(*bo_valid_patterns))

            # FIXME(microwatt,interrupts): turn this into an assert
            with m.If(self.trig.post):
                m.d.sync += Assume(bo_valid | self.pfv.intr)

        # NIA

        spec_nia = Signal(unsigned(64))
        taken    = Signal()
        offset   = Signal(signed(62))

        if isinstance(spec_insn, Instruction_I):
            m.d.comb += [
                taken .eq(1),
                offset.eq(spec_insn.li)
            ]

        elif isinstance(spec_insn, (Instruction_B, Instruction_XL_b)):
            cond_bit = Signal()
            ctr_any  = Signal()
            cond_ok  = Signal()
            ctr_ok   = Signal()

            m.d.comb += [
                cond_bit.eq(self.pfv.cr.r_data[::-1].bit_select(spec_insn.bi, width=1)),
                ctr_any .eq(self.pfv.ctr.w_data.any()),
                cond_ok .eq(spec_insn.bo[4] | (spec_insn.bo[3] == cond_bit)),
                ctr_ok  .eq(spec_insn.bo[2] | (ctr_any ^ spec_insn.bo[1])),
            ]

            if isinstance(spec_insn, Instruction_XL_b) and spec_insn.xo.value == 528: # bcctr/bcctrl
                m.d.comb += taken.eq(cond_ok)
            else:
                m.d.comb += taken.eq(cond_ok & ctr_ok)

            if isinstance(spec_insn, Instruction_B):
                m.d.comb += offset.eq(spec_insn.bd)
            elif spec_insn.xo.value ==  16: # bclr/bclrl
                m.d.comb += offset.eq(self.pfv.lr .r_data[:61])
            elif spec_insn.xo.value == 528: # bcctr/bcctrl
                m.d.comb += offset.eq(self.pfv.ctr.r_data[:61])
            elif spec_insn.xo.value == 560: # bctar/bctarl
                m.d.comb += offset.eq(self.pfv.tar.r_data[:61])
            else:
                assert False

        else:
            assert False

        with m.If(taken):
            if isinstance(spec_insn, (Instruction_I, Instruction_B)) and spec_insn.aa.value == 0:
                m.d.comb += spec_nia.eq(self.pfv.cia + (offset << 2))
            else:
                m.d.comb += spec_nia.eq(offset << 2)
        with m.Else():
            m.d.comb += spec_nia.eq(self.pfv.cia + 4)

        with m.If(self.trig.post & ~self.pfv.intr):
            m.d.sync += Assert(self.pfv.nia == spec_nia)

        # CR

        spec_cr_r_stb = Signal(8)

        if isinstance(spec_insn, Instruction_I):
            m.d.comb += spec_cr_r_stb.eq(0)
        elif isinstance(spec_insn, (Instruction_B, Instruction_XL_b)):
            m.d.comb += spec_cr_r_stb[::-1].bit_select(spec_insn.bi[2:], width=1).eq(1)
        else:
            assert False

        with m.If(self.trig.post & ~self.pfv.intr):
            for i, spec_cr_r_stb_bit in enumerate(spec_cr_r_stb):
                pfv_cr_r_stb_bit = self.pfv.cr.r_stb[i]
                m.d.sync += Assert(spec_cr_r_stb_bit.implies(pfv_cr_r_stb_bit))

        # LR

        spec_lr_r_stb  = Signal()
        spec_lr_w_stb  = Signal()
        spec_lr_w_data = Signal(64)

        if isinstance(spec_insn, (Instruction_I, Instruction_B)):
            m.d.comb += spec_lr_r_stb.eq(0)
        elif isinstance(spec_insn, (Instruction_XL_b)):
            m.d.comb += spec_lr_r_stb.eq(spec_insn.xo == 16) # bclr/bclrl
        else:
            assert False

        m.d.comb += [
            spec_lr_w_stb .eq(spec_insn.lk),
            spec_lr_w_data.eq(self.pfv.cia + 4),
        ]

        with m.If(self.trig.post & ~self.pfv.intr):
            m.d.sync += [
                Assert(self.pfv.lr.r_stb == spec_lr_r_stb),
                Assert(self.pfv.lr.w_stb == spec_lr_w_stb),
                Assert(self.pfv.lr.w_stb.implies(self.pfv.lr.w_data == spec_lr_w_data)),
            ]

        # CTR

        spec_ctr_r_stb  = Signal()
        spec_ctr_w_stb  = Signal()
        spec_ctr_w_data = Signal(64)

        if isinstance(spec_insn, Instruction_I):
            m.d.comb += spec_ctr_r_stb.eq(0)
        elif isinstance(spec_insn, Instruction_B):
            m.d.comb += spec_ctr_r_stb.eq(~spec_insn.bo[2])
        elif isinstance(spec_insn, (Instruction_B, Instruction_XL_b)):
            m.d.comb += spec_ctr_r_stb.eq(1)
        else:
            assert False

        if isinstance(spec_insn, Instruction_I):
            m.d.comb += spec_ctr_w_stb.eq(0)
        elif isinstance(spec_insn, Instruction_B):
            m.d.comb += spec_ctr_w_stb.eq(~spec_insn.bo[2])
        elif isinstance(spec_insn, Instruction_XL_b):
            if spec_insn.xo.value == 528: # bcctr/bcctrl
                m.d.comb += spec_ctr_w_stb.eq(0)
            else:
                m.d.comb += spec_ctr_w_stb.eq(~spec_insn.bo[2])
        else:
            assert False

        m.d.comb += spec_ctr_w_data.eq(self.pfv.ctr.r_data - 1)

        with m.If(self.trig.post & ~self.pfv.intr):
            m.d.sync += [
                Assert(self.pfv.ctr.r_stb == spec_ctr_r_stb),
                Assert(self.pfv.ctr.w_stb == spec_ctr_w_stb),
                Assert(self.pfv.ctr.w_stb.implies(self.pfv.ctr.w_data == spec_ctr_w_data)),
            ]

        # TAR

        spec_tar_r_stb = Signal()

        if isinstance(spec_insn, (Instruction_I, Instruction_B)):
            m.d.comb += spec_tar_r_stb.eq(0)
        elif isinstance(spec_insn, (Instruction_XL_b)):
            m.d.comb += spec_tar_r_stb.eq(spec_insn.xo == 560) # bctar/bctarl
        else:
            assert False

        with m.If(self.trig.post & ~self.pfv.intr):
            m.d.sync += [
                Assert(self.pfv.tar.r_stb == spec_tar_r_stb),
            ]

        return m

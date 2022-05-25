from amaranth import *
from amaranth.asserts import *

from .. import PowerFVCheck
from ... import pfv, tb

from ._fmt  import *
from ._insn import *


__all__ = ["CRSpec", "CRCheck"]


class CRSpec(Elaboratable):
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

        # CR

        spec_cr_r_stb  = Signal( 8)
        spec_cr_w_stb  = Signal( 8)
        spec_cr_w_data = Signal(32)

        if isinstance(spec_insn, (Instruction_XL_crl)):

            ba_r_field = Signal(4)
            bb_r_field = Signal(4)
            bt_r_field = Signal(4)
            ba_r_bit   = Signal()
            bb_r_bit   = Signal()
            bt_w_bit   = Signal()

            m.d.comb += [
                ba_r_field.eq(self.pfv.cr.r_data[::-1].word_select(spec_insn.ba[2:], width=4)),
                bb_r_field.eq(self.pfv.cr.r_data[::-1].word_select(spec_insn.bb[2:], width=4)),
                bt_r_field.eq(self.pfv.cr.r_data[::-1].word_select(spec_insn.bt[2:], width=4)),

                ba_r_bit.eq(ba_r_field.bit_select(spec_insn.ba[:2], width=1)),
                bb_r_bit.eq(bb_r_field.bit_select(spec_insn.bb[:2], width=1)),
            ]

            if isinstance(spec_insn, CRAND):
                m.d.comb += bt_w_bit.eq(ba_r_bit & bb_r_bit)
            elif isinstance(spec_insn, CROR):
                m.d.comb += bt_w_bit.eq(ba_r_bit | bb_r_bit)
            elif isinstance(spec_insn, CRNAND):
                m.d.comb += bt_w_bit.eq(~(ba_r_bit & bb_r_bit))
            elif isinstance(spec_insn, CRXOR):
                m.d.comb += bt_w_bit.eq(ba_r_bit ^ bb_r_bit)
            elif isinstance(spec_insn, CRNOR):
                m.d.comb += bt_w_bit.eq(~(ba_r_bit | bb_r_bit))
            elif isinstance(spec_insn, CRANDC):
                m.d.comb += bt_w_bit.eq(ba_r_bit & ~bb_r_bit)
            elif isinstance(spec_insn, CREQV):
                m.d.comb += bt_w_bit.eq(ba_r_bit == bb_r_bit)
            elif isinstance(spec_insn, CRORC):
                m.d.comb += bt_w_bit.eq(ba_r_bit | ~bb_r_bit)
            else:
                assert False

            spec_bt_w_field = Signal(4)

            for i, spec_bt_w_bit in enumerate(spec_bt_w_field):
                bt_r_bit = bt_r_field[i]
                with m.If(spec_insn.bt[:2] == i):
                    m.d.comb += spec_bt_w_bit.eq(bt_w_bit)
                with m.Else():
                    m.d.comb += spec_bt_w_bit.eq(bt_r_bit)

            m.d.comb += [
                spec_cr_r_stb[::-1].bit_select(spec_insn.ba[2:], width=1).eq(1),
                spec_cr_r_stb[::-1].bit_select(spec_insn.bb[2:], width=1).eq(1),
                spec_cr_w_stb[::-1].bit_select(spec_insn.bt[2:], width=1).eq(1),
                spec_cr_w_data[::-1].eq(Repl(spec_bt_w_field, 8))
            ]
        else:
            assert False

        with m.If(self.post.stb & ~self.pfv.intr):
            for i in range(8):
                spec_cr_w_field = spec_cr_w_data    .word_select(i, width=4)
                pfv_cr_w_field  = self.pfv.cr.w_data.word_select(i, width=4)

                m.d.sync += [
                    Assert(spec_cr_r_stb[i].implies(self.pfv.cr.r_stb[i])),
                    Assert(self.pfv.cr.w_stb[i] == spec_cr_w_stb[i]),
                    Assert(spec_cr_w_stb[i].implies(pfv_cr_w_field == spec_cr_w_field)),
                ]

        return m


class CRCheck(PowerFVCheck, name="_insn_cr"):
    def __init_subclass__(cls, name, insn_cls):
        super().__init_subclass__(name)
        cls.insn_cls = insn_cls

    def get_testbench(self, dut, post):
        tb_spec = CRSpec(self.insn_cls, post)
        tb_top  = tb.Testbench(tb_spec, dut)
        return tb_top

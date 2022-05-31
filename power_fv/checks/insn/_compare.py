from amaranth import *
from amaranth.asserts import *

from .. import PowerFVCheck
from ... import pfv, tb

from ._fmt  import *
from ._insn import *


__all__ = ["CompareSpec", "CompareCheck"]


class CompareSpec(Elaboratable):
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

        # GPRs

        spec_ra_r_stb = Signal()
        spec_rb_r_stb = Signal()

        if isinstance(spec_insn, (CMPI, CMPLI, CMP, CMPL)):
            m.d.comb += spec_ra_r_stb.eq(1)
        else:
            assert False

        if isinstance(spec_insn, (CMPI, CMPLI)):
            m.d.comb += spec_rb_r_stb.eq(0)
        elif isinstance(spec_insn, (CMP, CMPL)):
            m.d.comb += spec_rb_r_stb.eq(1)
        else:
            assert False

        with m.If(self.post.stb & ~self.pfv.intr):
            m.d.sync += [
                Assert(self.pfv.ra.r_stb == spec_ra_r_stb),
                Assert(self.pfv.rb.r_stb == spec_rb_r_stb),
            ]

        # CR

        spec_cr_w_stb  = Signal(8)
        spec_cr_w_data = Signal(32)

        a = Signal(signed(64))
        b = Signal(signed(64))
        c = Record([("lt", 1), ("gt", 1), ("eq_", 1), ("so", 1)])

        if isinstance(spec_insn, (CMPI, CMP)):
            with m.If(spec_insn.l):
                m.d.comb += a.eq(self.pfv.ra.r_data)
            with m.Else():
                m.d.comb += a.eq(self.pfv.ra.r_data[:32].as_signed())
        elif isinstance(spec_insn, (CMPL, CMPLI)):
            with m.If(spec_insn.l):
                m.d.comb += a.eq(self.pfv.ra.r_data)
            with m.Else():
                m.d.comb += a.eq(self.pfv.ra.r_data[:32].as_unsigned())
        else:
            assert False

        if isinstance(spec_insn, CMPI):
            m.d.comb += b.eq(spec_insn.si)
        elif isinstance(spec_insn, CMPLI):
            m.d.comb += b.eq(spec_insn.ui)
        elif isinstance(spec_insn, CMP):
            with m.If(spec_insn.l):
                m.d.comb += b.eq(self.pfv.rb.r_data)
            with m.Else():
                m.d.comb += b.eq(self.pfv.rb.r_data[:32].as_signed())
        elif isinstance(spec_insn, CMPL):
            with m.If(spec_insn.l):
                m.d.comb += b.eq(self.pfv.rb.r_data)
            with m.Else():
                m.d.comb += b.eq(self.pfv.rb.r_data[:32].as_unsigned())
        else:
            assert False

        if isinstance(spec_insn, (CMPI, CMP)):
            m.d.comb += [
                c.lt.eq(a.as_signed() < b.as_signed()),
                c.gt.eq(a.as_signed() > b.as_signed()),
            ]
        elif isinstance(spec_insn, (CMPLI, CMPL)):
            m.d.comb += [
                c.lt.eq(a.as_unsigned() < b.as_unsigned()),
                c.gt.eq(a.as_unsigned() > b.as_unsigned()),
            ]
        else:
            assert False

        m.d.comb += [
            c.eq_.eq(a == b),
            c.so .eq(self.pfv.xer.r_data[63 - 32]), # XER.SO
        ]

        m.d.comb += [
            spec_cr_w_stb[::-1].bit_select(spec_insn.bf, width=1).eq(1),
            spec_cr_w_data[::-1].eq(Repl(c, 8)),
        ]

        with m.If(self.post.stb & ~self.pfv.intr):
            for i in range(8):
                spec_cr_w_field = spec_cr_w_data    .word_select(i, width=4)
                pfv_cr_w_field  = self.pfv.cr.w_data.word_select(i, width=4)

                m.d.sync += [
                    Assert(self.pfv.cr.w_stb[i] == spec_cr_w_stb[i]),
                    Assert(spec_cr_w_stb[i].implies(pfv_cr_w_field == spec_cr_w_field)),
                ]

        # XER

        spec_xer_r_mask = Signal(64)

        if isinstance(spec_insn, (CMPI, CMPLI, CMP, CMPL)):
            m.d.comb += spec_xer_r_mask[63 - 32].eq(1) # XER.SO
        else:
            assert False

        with m.If(self.post.stb & ~self.pfv.intr):
            m.d.sync += Assert((self.pfv.xer.r_mask & spec_xer_r_mask) == spec_xer_r_mask)

        return m


class CompareCheck(PowerFVCheck, name="_insn_compare"):
    def __init_subclass__(cls, name, insn_cls):
        super().__init_subclass__(name)
        cls.insn_cls = insn_cls

    def get_testbench(self, dut, post):
        tb_spec = CompareSpec(self.insn_cls, post)
        tb_top  = tb.Testbench(tb_spec, dut)
        return tb_top

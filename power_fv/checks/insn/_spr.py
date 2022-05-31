from amaranth import *
from amaranth.asserts import *

from .. import PowerFVCheck
from ... import pfv, tb

from ._fmt  import *
from ._insn import *


__all__ = ["SPRMoveSpec", "SPRMoveCheck"]


class SPRMoveSpec(Elaboratable):
    def __init__(self, insn_cls, post):
        self.insn_cls = insn_cls
        self.pfv      = pfv.Interface()
        self.post     = tb.Trigger(cycle=post)

    def triggers(self):
        yield self.post

    # TODO:
    # - don't hardcode SPRs, let cores declare what they support.
    # - access restrictions (i.e. R/W, privileged)

    def elaborate(self, platform):
        m = Module()

        spec_insn = self.insn_cls()

        with m.If(self.post.stb):
            m.d.sync += [
                Assume(self.pfv.stb),
                Assume(self.pfv.insn[32:] == spec_insn),
            ]

        spr = Record([
            ("num",       10),
            ("reserved",   1),
            ("undefined",  1),
            ("pfv", [
                ("r_mask", 64),
                ("r_data", 64),
                ("w_mask", 64),
                ("w_data", 64),
            ]),
        ])

        if isinstance(spec_insn, (MTSPR, MFSPR)):
            m.d.comb += spr.num.eq(Cat(spec_insn.spr[5:10], spec_insn.spr[0:5]))
        else:
            assert False

        with m.Switch(spr.num):
            for num in range(808, 812):
                with m.Case(num):
                    m.d.comb += spr.reserved.eq(1)

            pfv_sprs = [
                (  1,  self.pfv.xer ),
                (  8,  self.pfv.lr  ),
                (  9,  self.pfv.ctr ),
                ( 26,  self.pfv.srr0),
                ( 27,  self.pfv.srr1),
                (815,  self.pfv.tar ),
            ]

            for num, pfv_spr in pfv_sprs:
                with m.Case(num):
                    m.d.comb += [
                        spr.pfv.r_mask.eq(pfv_spr.r_mask),
                        spr.pfv.r_data.eq(pfv_spr.r_data),
                        spr.pfv.w_mask.eq(pfv_spr.w_mask),
                        spr.pfv.w_data.eq(pfv_spr.w_data),
                    ]

            with m.Default():
                m.d.comb += spr.undefined.eq(1)

        with m.If(self.post.stb):
            # TODO: turn into assert
            m.d.sync += Assume(spr.undefined.implies(self.pfv.intr))

        # # MSR
        # pfv_msr_pr = Signal()
        # m.d.comb += pfv_msr_pr.eq(self.pfv.msr.r_data[63 - 49])

        # with m.If(self.post.stb):
        #     m.d.sync += Assert(self.pfv.msr.r_mask[63 - 49])

        # GPR

        spec_rs_r_stb  = Signal()
        spec_rt_w_stb  = Signal()
        # spec_rt_w_mask = Signal(64)
        spec_rt_w_data = Signal(64)

        if isinstance(spec_insn, MTSPR):
            m.d.comb += [
                spec_rs_r_stb.eq(~spr.reserved),
                spec_rt_w_stb.eq(0),
            ]

        elif isinstance(spec_insn, MFSPR):
            m.d.comb += [
                spec_rs_r_stb .eq(0),
                spec_rt_w_stb .eq(~spr.reserved),
                spec_rt_w_data.eq(spr.pfv.r_data),
            ]

            # # In problem state, reserved fields must return 0, so we include them in the mask.
            # # In privileged state, reserved fields may return anything.
            # with m.If(pfv_msr_pr):
            #     m.d.comb += spec_rt_w_mask.eq(Repl(1, 64))
            # with m.Else():
            #     m.d.comb += spec_rt_w_mask.eq(spr.pfv.r_mask)

        else:
            assert False

        with m.If(self.post.stb & ~self.pfv.intr):
            m.d.sync += [
                Assert(spec_rs_r_stb.implies(self.pfv.rs.r_stb)),
                Assert(self.pfv.rt.w_stb == spec_rt_w_stb),
                Assert(spec_rt_w_stb.implies(self.pfv.rt.w_data == (spr.pfv.r_data & spr.pfv.r_mask))),
            ]
            # with m.If(spec_rt_w_stb):
                # for i in range(64):
                    # with m.If(spr.pfv.w_mask[i]):
                        # m.d.sync += Assert(self.pfv.rt.w_data[i] == spec_rt_w_data[i])

        # SPR

        spec_spr_w_stb  = Signal()
        spec_spr_w_data = Signal(64)

        if isinstance(spec_insn, MTSPR):
            m.d.comb += [
                spec_spr_w_stb .eq(1),
                spec_spr_w_data.eq(self.pfv.rs.r_data),
            ]
        elif isinstance(spec_insn, MFSPR):
            m.d.comb += spec_spr_w_stb.eq(0)
        else:
            assert False

        with m.If(self.post.stb & ~self.pfv.intr):
            m.d.sync += [
                Assert(spec_spr_w_stb == spr.pfv.w_mask.any()),
                Assert((spr.pfv.w_data & spr.pfv.w_mask) == (spec_spr_w_data & spr.pfv.w_mask)),
            ]

        return m


class SPRMoveCheck(PowerFVCheck, name="_insn_spr"):
    def __init_subclass__(cls, name, insn_cls):
        super().__init_subclass__(name)
        cls.insn_cls = insn_cls

    def get_testbench(self, dut, post):
        tb_spec = SPRMoveSpec(self.insn_cls, post)
        tb_top  = tb.Testbench(tb_spec, dut)
        return tb_top

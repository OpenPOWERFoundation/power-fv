from amaranth import *
from amaranth.asserts import *

from power_fv import pfv


__all__ = ["MicrowattWrapper"]


class MicrowattWrapper(Elaboratable):
    def __init__(self):
        self.pfv = pfv.Interface()

    def elaborate(self, platform):
        m = Module()

        wb_insn_dat_r  = AnySeq(64)
        wb_insn_ack    = AnySeq( 1)
        wb_insn_stall  = AnySeq( 1)
        wb_insn_adr    = Signal(29, attrs={"keep": True})
        wb_insn_dat_w  = Signal(64, attrs={"keep": True})
        wb_insn_sel    = Signal( 8, attrs={"keep": True})
        wb_insn_cyc    = Signal(    attrs={"keep": True})
        wb_insn_stb    = Signal(    attrs={"keep": True})
        wb_insn_we     = Signal(    attrs={"keep": True})

        wb_data_dat_r  = AnySeq(64)
        wb_data_ack    = AnySeq( 1)
        wb_data_stall  = AnySeq( 1)
        wb_data_adr    = Signal(29, attrs={"keep": True})
        wb_data_dat_w  = Signal(64, attrs={"keep": True})
        wb_data_sel    = Signal( 8, attrs={"keep": True})
        wb_data_cyc    = Signal( 1, attrs={"keep": True})
        wb_data_stb    = Signal( 1, attrs={"keep": True})
        wb_data_we     = Signal( 1, attrs={"keep": True})

        wb_snoop_adr   = AnySeq(29)
        wb_snoop_dat_w = AnySeq(64)
        wb_snoop_sel   = AnySeq( 8)
        wb_snoop_cyc   = AnySeq( 1)
        wb_snoop_stb   = AnySeq( 1)
        wb_snoop_we    = AnySeq( 1)

        dmi_addr       = AnySeq( 4)
        dmi_din        = AnySeq(64)
        dmi_req        = AnySeq( 1)
        dmi_wr         = AnySeq( 1)
        dmi_dout       = Signal(64, attrs={"keep": True})
        dmi_ack        = Signal(    attrs={"keep": True})

        terminated     = Signal(    attrs={"keep": True})

        # FIXME: ghdl-yosys-plugin doesn't yet support setting parameters (see issue 136).
        # As a workaround, use our own toplevel entity.
        m.submodules.toplevel = Instance("toplevel",
            ("i", "clk",       ClockSignal("sync")),
            ("i", "rst",       ResetSignal("sync")),
            ("i", "alt_reset", Const(0)),
            ("i", "ext_irq",   Const(0)),

            ("i", "wishbone_insn_in.dat",   wb_insn_dat_r),
            ("i", "wishbone_insn_in.ack",   wb_insn_ack),
            ("i", "wishbone_insn_in.stall", wb_insn_stall),
            ("o", "wishbone_insn_out.adr",  wb_insn_adr),
            ("o", "wishbone_insn_out.dat",  wb_insn_dat_w),
            ("o", "wishbone_insn_out.sel",  wb_insn_sel),
            ("o", "wishbone_insn_out.cyc",  wb_insn_cyc),
            ("o", "wishbone_insn_out.stb",  wb_insn_stb),
            ("o", "wishbone_insn_out.we",   wb_insn_we),

            ("i", "wishbone_data_in.dat",   wb_data_dat_r),
            ("i", "wishbone_data_in.ack",   wb_data_ack),
            ("i", "wishbone_data_in.stall", wb_data_stall),
            ("o", "wishbone_data_out.adr",  wb_data_adr),
            ("o", "wishbone_data_out.dat",  wb_data_dat_w),
            ("o", "wishbone_data_out.sel",  wb_data_sel),
            ("o", "wishbone_data_out.cyc",  wb_data_cyc),
            ("o", "wishbone_data_out.stb",  wb_data_stb),
            ("o", "wishbone_data_out.we",   wb_data_we),

            ("i", "wb_snoop_in.adr", wb_snoop_adr),
            ("i", "wb_snoop_in.dat", wb_snoop_dat_w),
            ("i", "wb_snoop_in.sel", wb_snoop_sel),
            ("i", "wb_snoop_in.cyc", wb_snoop_cyc),
            ("i", "wb_snoop_in.stb", wb_snoop_stb),
            ("i", "wb_snoop_in.we",  wb_snoop_we),

            ("i", "dmi_addr", dmi_addr),
            ("i", "dmi_din",  dmi_din),
            ("o", "dmi_dout", dmi_dout),
            ("i", "dmi_req",  dmi_req),
            ("i", "dmi_wr",   dmi_wr),
            ("o", "dmi_ack",  dmi_ack),

            ("o", "terminated_out", terminated),

            ("o", "pfv_stb",        self.pfv.stb),
            ("o", "pfv_insn",       self.pfv.insn),
            ("o", "pfv_order",      self.pfv.order),
            ("o", "pfv_intr",       self.pfv.intr),
            ("o", "pfv_cia",        self.pfv.cia),
            ("o", "pfv_nia",        self.pfv.nia),

            ("o", "pfv_ra_index",   self.pfv.ra.index),
            ("o", "pfv_ra_r_stb",   self.pfv.ra.r_stb),
            ("o", "pfv_ra_r_data",  self.pfv.ra.r_data),
            ("o", "pfv_ra_w_stb",   self.pfv.ra.w_stb),
            ("o", "pfv_ra_w_data",  self.pfv.ra.w_data),

            ("o", "pfv_rb_index",   self.pfv.rb.index),
            ("o", "pfv_rb_r_stb",   self.pfv.rb.r_stb),
            ("o", "pfv_rb_r_data",  self.pfv.rb.r_data),

            ("o", "pfv_rs_index",   self.pfv.rs.index),
            ("o", "pfv_rs_r_stb",   self.pfv.rs.r_stb),
            ("o", "pfv_rs_r_data",  self.pfv.rs.r_data),

            ("o", "pfv_rt_index",   self.pfv.rt.index),
            ("o", "pfv_rt_r_stb",   self.pfv.rt.r_stb),
            ("o", "pfv_rt_r_data",  self.pfv.rt.r_data),
            ("o", "pfv_rt_w_stb",   self.pfv.rt.w_stb),
            ("o", "pfv_rt_w_data",  self.pfv.rt.w_data),

            ("o", "pfv_cr_r_stb",  self.pfv.cr.r_stb),
            ("o", "pfv_cr_r_data", self.pfv.cr.r_data),
            ("o", "pfv_cr_w_stb",  self.pfv.cr.w_stb),
            ("o", "pfv_cr_w_data", self.pfv.cr.w_data),

            ("o", "pfv_msr_r_mask", self.pfv.msr.r_mask),
            ("o", "pfv_msr_r_data", self.pfv.msr.r_data),
            ("o", "pfv_msr_w_mask", self.pfv.msr.w_mask),
            ("o", "pfv_msr_w_data", self.pfv.msr.w_data),

            ("o", "pfv_lr_r_mask",  self.pfv.lr.r_mask),
            ("o", "pfv_lr_r_data",  self.pfv.lr.r_data),
            ("o", "pfv_lr_w_mask",  self.pfv.lr.w_mask),
            ("o", "pfv_lr_w_data",  self.pfv.lr.w_data),

            ("o", "pfv_ctr_r_mask", self.pfv.ctr.r_mask),
            ("o", "pfv_ctr_r_data", self.pfv.ctr.r_data),
            ("o", "pfv_ctr_w_mask", self.pfv.ctr.w_mask),
            ("o", "pfv_ctr_w_data", self.pfv.ctr.w_data),

            ("o", "pfv_xer_r_mask", self.pfv.xer.r_mask),
            ("o", "pfv_xer_r_data", self.pfv.xer.r_data),
            ("o", "pfv_xer_w_mask", self.pfv.xer.w_mask),
            ("o", "pfv_xer_w_data", self.pfv.xer.w_data),

            ("o", "pfv_tar_r_mask", self.pfv.tar.r_mask),
            ("o", "pfv_tar_r_data", self.pfv.tar.r_data),
            ("o", "pfv_tar_w_mask", self.pfv.tar.w_mask),
            ("o", "pfv_tar_w_data", self.pfv.tar.w_data),

            ("o", "pfv_srr0_r_mask", self.pfv.srr0.r_mask),
            ("o", "pfv_srr0_r_data", self.pfv.srr0.r_data),
            ("o", "pfv_srr0_w_mask", self.pfv.srr0.w_mask),
            ("o", "pfv_srr0_w_data", self.pfv.srr0.w_data),

            ("o", "pfv_srr1_r_mask", self.pfv.srr1.r_mask),
            ("o", "pfv_srr1_r_data", self.pfv.srr1.r_data),
            ("o", "pfv_srr1_w_mask", self.pfv.srr1.w_mask),
            ("o", "pfv_srr1_w_data", self.pfv.srr1.w_data),
        )

        with m.If(Initial()):
            m.d.comb += Assume(~self.pfv.stb)

        m.d.comb += [
            Assume(~dmi_req),
            Assume(~terminated),
        ]

        return m

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

            ("o", "pfv_out.stb",   self.pfv.stb),
            ("o", "pfv_out.insn",  self.pfv.insn),
            ("o", "pfv_out.order", self.pfv.order),
        )

        with m.If(Initial()):
            m.d.comb += Assume(~self.pfv.stb)

        return m

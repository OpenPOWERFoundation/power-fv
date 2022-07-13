import os
import pathlib
import textwrap

from amaranth import *
from amaranth.asserts import *
from amaranth_soc import wishbone

from power_fv import pfv
from power_fv.core import PowerFVCore


__all__ = ["MicrowattWrapper", "MicrowattCore"]


class MicrowattWrapper(Elaboratable):
    @classmethod
    def add_check_arguments(cls, parser):
        group = parser.add_argument_group(title="microwatt options")
        group.add_argument(
            "--ex1-bypass", choices=("true","false"), default="true",
            help="(default: %(default)s)")
        group.add_argument(
            "--has-btc", choices=("true","false"), default="true",
            help="(default: %(default)s)")
        group.add_argument(
            "--icache-num-lines", type=int, default=2,
            help="(default: %(default)s)")
        group.add_argument(
            "--icache-num-ways", type=int, default=1,
            help="(default: %(default)s)")
        group.add_argument(
            "--icache-tlb-size", type=int, default=1,
            help="(default: %(default)s)")
        group.add_argument(
            "--dcache-num-lines", type=int, default=2,
            help="(default: %(default)s)")
        group.add_argument(
            "--dcache-num-ways", type=int, default=1,
            help="(default: %(default)s)")
        group.add_argument(
            "--dcache-tlb-set-size", type=int, default=1,
            help="(default: %(default)s)")
        group.add_argument(
            "--dcache-tlb-num-ways", type=int, default=1,
            help="(default: %(default)s)")

    # ghdl-yosys-plugin doesn't yet support setting instance parameters from outside VHDL
    # (see upstream issue 136).
    # As a workaround, we use a template to generate a VHDL toplevel at build-time, which
    # is instantiated in .elaborate().

    MICROWATT_TOPLEVEL = textwrap.dedent(r"""
        library ieee;
        use ieee.std_logic_1164.all;
        use ieee.numeric_std.all;

        library work;
        use work.common.all;
        use work.wishbone_types.all;
        use work.powerfv_types.all;

        entity toplevel is
            port (
                clk : in std_ulogic;
                rst : in std_ulogic;

                -- Alternate reset (0xffff0000) for use by DRAM init fw
                alt_reset : in std_ulogic;

                -- Wishbone interface
                wishbone_insn_in  : in wishbone_slave_out;
                wishbone_insn_out : out wishbone_master_out;
                wishbone_data_in  : in wishbone_slave_out;
                wishbone_data_out : out wishbone_master_out;
                wb_snoop_in       : in wishbone_master_out;

                dmi_addr : in std_ulogic_vector(3 downto 0);
                dmi_din	 : in std_ulogic_vector(63 downto 0);
                dmi_dout : out std_ulogic_vector(63 downto 0);
                dmi_req  : in std_ulogic;
                dmi_wr	 : in std_ulogic;
                dmi_ack  : out std_ulogic;

                ext_irq : in std_ulogic;

                terminated_out : out std_logic;

                pfv_out : out pfv_t
                );
        end entity toplevel;

        architecture behave of toplevel is
            signal pfv : pfv_t;
        begin
            core: entity work.core
                generic map (
                    SIM                 => false,
                    DISABLE_FLATTEN     => false,
                    EX1_BYPASS          => {ex1_bypass},
                    HAS_FPU             => false,
                    HAS_BTC             => {has_btc},
                    HAS_SHORT_MULT      => false,
                    HAS_POWERFV         => true,
                    LOG_LENGTH          => 0,
                    ICACHE_NUM_LINES    => {icache_num_lines},
                    ICACHE_NUM_WAYS     => {icache_num_ways},
                    ICACHE_TLB_SIZE     => {icache_tlb_size},
                    DCACHE_NUM_LINES    => {dcache_num_lines},
                    DCACHE_NUM_WAYS     => {dcache_num_ways},
                    DCACHE_TLB_SET_SIZE => {dcache_tlb_set_size},
                    DCACHE_TLB_NUM_WAYS => {dcache_tlb_num_ways}
                    )
                port map (
                    clk               => clk,
                    rst               => rst,
                    alt_reset         => alt_reset,
                    wishbone_insn_in  => wishbone_insn_in,
                    wishbone_insn_out => wishbone_insn_out,
                    wishbone_data_in  => wishbone_data_in,
                    wishbone_data_out => wishbone_data_out,
                    wb_snoop_in       => wb_snoop_in,
                    dmi_addr          => dmi_addr,
                    dmi_din           => dmi_din,
                    dmi_dout          => dmi_dout,
                    dmi_req           => dmi_req,
                    dmi_wr            => dmi_wr,
                    dmi_ack           => dmi_ack,
                    ext_irq           => ext_irq,
                    terminated_out    => terminated_out,
                    pfv_out           => pfv_out
                );
        end architecture behave;
    """)

    def __init__(self, **kwargs):
        self.pfv     = pfv.Interface()
        self.wb_insn = wishbone.Interface(addr_width=29, data_width=64, granularity=8,
                                          features=("stall",))
        self.wb_data = wishbone.Interface(addr_width=29, data_width=64, granularity=8,
                                          features=("stall",))

        def keep_wb_fanout(wb_bus):
            for field_name in ("adr", "dat_w", "sel", "cyc", "stb", "we"):
                wb_bus[field_name].attrs["keep"] = True

        keep_wb_fanout(self.wb_insn)
        keep_wb_fanout(self.wb_data)

        self._toplevel_src = self.MICROWATT_TOPLEVEL.format(**kwargs)

    def elaborate(self, platform):
        m = Module()

        wb_snoop   = wishbone.Interface(addr_width=29, data_width=64, granularity=8)
        dmi        = Record([
            ("addr", unsigned( 4)),
            ("din",  unsigned(64)),
            ("dout", unsigned(64)),
            ("req",  unsigned( 1)),
            ("wr",   unsigned( 1)),
            ("ack",  unsigned( 1)),
        ])
        terminated = Signal(attrs={"keep": True})

        dmi.dout.attrs["keep"] = True
        dmi.ack .attrs["keep"] = True

        m.d.comb += [
            self.wb_insn.dat_r.eq(AnySeq(64)),
            self.wb_insn.ack  .eq(AnySeq( 1)),
            self.wb_insn.stall.eq(AnySeq( 1)),

            self.wb_data.dat_r.eq(AnySeq(64)),
            self.wb_data.ack  .eq(AnySeq( 1)),
            self.wb_data.stall.eq(AnySeq( 1)),

            wb_snoop.adr  .eq(AnySeq(29)),
            wb_snoop.dat_w.eq(AnySeq(64)),
            wb_snoop.sel  .eq(AnySeq( 8)),
            wb_snoop.cyc  .eq(AnySeq( 1)),
            wb_snoop.stb  .eq(AnySeq( 1)),
            wb_snoop.we   .eq(AnySeq( 1)),

            dmi.addr.eq(AnySeq( 4)),
            dmi.din .eq(AnySeq(64)),
            dmi.req .eq(AnySeq( 1)),
            dmi.wr  .eq(AnySeq( 1)),
        ]

        m.submodules.dut = Instance("toplevel",
            ("i", "clk",       ClockSignal()),
            ("i", "rst",       ResetSignal()),
            ("i", "alt_reset", Const(0)),
            ("i", "ext_irq",   Const(0)),

            ("i", "wishbone_insn_in.dat"  , self.wb_insn.dat_r),
            ("i", "wishbone_insn_in.ack"  , self.wb_insn.ack  ),
            ("i", "wishbone_insn_in.stall", self.wb_insn.stall),
            ("o", "wishbone_insn_out.adr" , self.wb_insn.adr  ),
            ("o", "wishbone_insn_out.dat" , self.wb_insn.dat_w),
            ("o", "wishbone_insn_out.sel" , self.wb_insn.sel  ),
            ("o", "wishbone_insn_out.cyc" , self.wb_insn.cyc  ),
            ("o", "wishbone_insn_out.stb" , self.wb_insn.stb  ),
            ("o", "wishbone_insn_out.we"  , self.wb_insn.we   ),

            ("i", "wishbone_data_in.dat"  , self.wb_data.dat_r),
            ("i", "wishbone_data_in.ack"  , self.wb_data.ack  ),
            ("i", "wishbone_data_in.stall", self.wb_data.stall),
            ("o", "wishbone_data_out.adr" , self.wb_data.adr  ),
            ("o", "wishbone_data_out.dat" , self.wb_data.dat_w),
            ("o", "wishbone_data_out.sel" , self.wb_data.sel  ),
            ("o", "wishbone_data_out.cyc" , self.wb_data.cyc  ),
            ("o", "wishbone_data_out.stb" , self.wb_data.stb  ),
            ("o", "wishbone_data_out.we"  , self.wb_data.we   ),

            ("i", "wb_snoop_in.adr", wb_snoop.adr  ),
            ("i", "wb_snoop_in.dat", wb_snoop.dat_w),
            ("i", "wb_snoop_in.sel", wb_snoop.sel  ),
            ("i", "wb_snoop_in.cyc", wb_snoop.cyc  ),
            ("i", "wb_snoop_in.stb", wb_snoop.stb  ),
            ("i", "wb_snoop_in.we" , wb_snoop.we   ),

            ("i", "dmi_addr", dmi.addr),
            ("i", "dmi_din" , dmi.din ),
            ("o", "dmi_dout", dmi.dout),
            ("i", "dmi_req" , dmi.req ),
            ("i", "dmi_wr"  , dmi.wr  ),
            ("o", "dmi_ack" , dmi.ack ),

            ("o", "terminated_out", terminated),

            ("o", "pfv_out.stb"  , self.pfv.stb  ),
            ("o", "pfv_out.insn" , self.pfv.insn ),
            ("o", "pfv_out.order", self.pfv.order),
            ("o", "pfv_out.intr" , self.pfv.intr ),
            ("o", "pfv_out.cia"  , self.pfv.cia  ),
            ("o", "pfv_out.nia"  , self.pfv.nia  ),
            ("o", "pfv_out.ra"   , self.pfv.ra   ),
            ("o", "pfv_out.rb"   , self.pfv.rb   ),
            ("o", "pfv_out.rs"   , self.pfv.rs   ),
            ("o", "pfv_out.rt"   , self.pfv.rt   ),
            ("o", "pfv_out.mem"  , self.pfv.mem  ),
            ("o", "pfv_out.cr"   , self.pfv.cr   ),
            ("o", "pfv_out.msr"  , self.pfv.msr  ),
            ("o", "pfv_out.lr"   , self.pfv.lr   ),
            ("o", "pfv_out.ctr"  , self.pfv.ctr  ),
            ("o", "pfv_out.tar"  , self.pfv.tar  ),
            ("o", "pfv_out.xer"  , self.pfv.xer  ),
            ("o", "pfv_out.srr0" , self.pfv.srr0 ),
            ("o", "pfv_out.srr1" , self.pfv.srr1 ),
        )

        m.d.comb += [
            Assume(~dmi.req),
            Assume(~terminated),
        ]

        return m


class MicrowattCore(PowerFVCore):
    MICROWATT_FILES = (
        "cache_ram.vhdl",
        "common.vhdl",
        "control.vhdl",
        "core_debug.vhdl",
        "core.vhdl",
        "countbits.vhdl",
        "cr_file.vhdl",
        "crhelpers.vhdl",
        "dcache.vhdl",
        "decode1.vhdl",
        "decode2.vhdl",
        "decode_types.vhdl",
        "divider.vhdl",
        "execute1.vhdl",
        "fetch1.vhdl",
        "fpu.vhdl",
        "helpers.vhdl",
        "icache.vhdl",
        "insn_helpers.vhdl",
        "loadstore1.vhdl",
        "logical.vhdl",
        "mmu.vhdl",
        "multiply.vhdl",
        "nonrandom.vhdl",
        "plru.vhdl",
        "pmu.vhdl",
        "powerfv_types.vhdl",
        "powerfv.vhdl",
        "ppc_fx_insns.vhdl",
        "register_file.vhdl",
        "rotator.vhdl",
        "utils.vhdl",
        "wishbone_types.vhdl",
        "writeback.vhdl",
    )

    @classmethod
    def add_check_arguments(cls, parser):
        super().add_check_arguments(parser)
        MicrowattWrapper.add_check_arguments(parser)

    @classmethod
    def wrapper(cls, **kwargs):
        return MicrowattWrapper(**kwargs)

    @classmethod
    def add_build_arguments(cls, parser):
        super().add_build_arguments(parser)
        group = parser.add_argument_group(title="microwatt options")
        group.add_argument(
            "--src-dir", type=pathlib.Path, default=pathlib.Path("./src"),
            help="microwatt directory (default: %(default)s)")
        group.add_argument(
            "--ghdl-opts", type=str, default="--std=08",
            help="ghdl options (default: '%(default)s')")

    @classmethod
    def add_files(cls, platform, wrapper, *, src_dir, **kwargs):
        assert isinstance(wrapper, MicrowattWrapper)

        for filename in cls.MICROWATT_FILES:
            contents = open(os.path.join(src_dir, filename), "r")
            platform.add_file(filename, contents)

        top_filename = "top-powerfv.vhdl"
        top_contents = wrapper._toplevel_src
        platform.add_file(top_filename, top_contents)

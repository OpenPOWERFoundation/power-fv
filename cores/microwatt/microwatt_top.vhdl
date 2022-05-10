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
	alt_reset    : in std_ulogic;

	-- Wishbone interface
        wishbone_insn_in  : in wishbone_slave_out;
        wishbone_insn_out : out wishbone_master_out;

        wishbone_data_in  : in wishbone_slave_out;
        wishbone_data_out : out wishbone_master_out;

        wb_snoop_in     : in wishbone_master_out;

	dmi_addr	: in std_ulogic_vector(3 downto 0);
	dmi_din	        : in std_ulogic_vector(63 downto 0);
	dmi_dout	: out std_ulogic_vector(63 downto 0);
	dmi_req	        : in std_ulogic;
	dmi_wr		: in std_ulogic;
	dmi_ack	        : out std_ulogic;

	ext_irq		: in std_ulogic;

	terminated_out  : out std_logic;

        pfv_stb        : out std_ulogic;
        pfv_insn       : out std_ulogic_vector(63 downto 0);
        pfv_order      : out std_ulogic_vector(63 downto 0);
        pfv_intr       : out std_ulogic;
        pfv_cia        : out std_ulogic_vector(63 downto 0);
        pfv_nia        : out std_ulogic_vector(63 downto 0);

        pfv_ra_index   : out std_ulogic_vector( 4 downto 0);
        pfv_ra_r_stb   : out std_ulogic;
        pfv_ra_r_data  : out std_ulogic_vector(63 downto 0);
        pfv_ra_w_stb   : out std_ulogic;
        pfv_ra_w_data  : out std_ulogic_vector(63 downto 0);
        pfv_rb_index   : out std_ulogic_vector( 4 downto 0);
        pfv_rb_r_stb   : out std_ulogic;
        pfv_rb_r_data  : out std_ulogic_vector(63 downto 0);
        pfv_rs_index   : out std_ulogic_vector( 4 downto 0);
        pfv_rs_r_stb   : out std_ulogic;
        pfv_rs_r_data  : out std_ulogic_vector(63 downto 0);
        pfv_rt_index   : out std_ulogic_vector( 4 downto 0);
        pfv_rt_r_stb   : out std_ulogic;
        pfv_rt_r_data  : out std_ulogic_vector(63 downto 0);
        pfv_rt_w_stb   : out std_ulogic;
        pfv_rt_w_data  : out std_ulogic_vector(63 downto 0);

        pfv_cr0_r_stb  : out std_ulogic;
        pfv_cr0_r_data : out std_ulogic_vector(3 downto 0);
        pfv_cr0_w_stb  : out std_ulogic;
        pfv_cr0_w_data : out std_ulogic_vector(3 downto 0);
        pfv_cr1_r_stb  : out std_ulogic;
        pfv_cr1_r_data : out std_ulogic_vector(3 downto 0);
        pfv_cr1_w_stb  : out std_ulogic;
        pfv_cr1_w_data : out std_ulogic_vector(3 downto 0);
        pfv_cr2_r_stb  : out std_ulogic;
        pfv_cr2_r_data : out std_ulogic_vector(3 downto 0);
        pfv_cr2_w_stb  : out std_ulogic;
        pfv_cr2_w_data : out std_ulogic_vector(3 downto 0);
        pfv_cr3_r_stb  : out std_ulogic;
        pfv_cr3_r_data : out std_ulogic_vector(3 downto 0);
        pfv_cr3_w_stb  : out std_ulogic;
        pfv_cr3_w_data : out std_ulogic_vector(3 downto 0);
        pfv_cr4_r_stb  : out std_ulogic;
        pfv_cr4_r_data : out std_ulogic_vector(3 downto 0);
        pfv_cr4_w_stb  : out std_ulogic;
        pfv_cr4_w_data : out std_ulogic_vector(3 downto 0);
        pfv_cr5_r_stb  : out std_ulogic;
        pfv_cr5_r_data : out std_ulogic_vector(3 downto 0);
        pfv_cr5_w_stb  : out std_ulogic;
        pfv_cr5_w_data : out std_ulogic_vector(3 downto 0);
        pfv_cr6_r_stb  : out std_ulogic;
        pfv_cr6_r_data : out std_ulogic_vector(3 downto 0);
        pfv_cr6_w_stb  : out std_ulogic;
        pfv_cr6_w_data : out std_ulogic_vector(3 downto 0);
        pfv_cr7_r_stb  : out std_ulogic;
        pfv_cr7_r_data : out std_ulogic_vector(3 downto 0);
        pfv_cr7_w_stb  : out std_ulogic;
        pfv_cr7_w_data : out std_ulogic_vector(3 downto 0)
        );
end entity toplevel;

architecture behave of toplevel is
    signal pfv : pfv_t;
begin
    core: entity work.core
        generic map (
            SIM                 => false,
            DISABLE_FLATTEN     => false,
            EX1_BYPASS          => true,
            HAS_FPU             => false,
            HAS_BTC             => true,
            HAS_SHORT_MULT      => false,
            HAS_POWERFV         => true,
            LOG_LENGTH          => 0,
            ICACHE_NUM_LINES    => 2,
            ICACHE_NUM_WAYS     => 1,
            ICACHE_TLB_SIZE     => 1,
            DCACHE_NUM_LINES    => 2,
            DCACHE_NUM_WAYS     => 1,
            DCACHE_TLB_SET_SIZE => 1,
            DCACHE_TLB_NUM_WAYS => 1
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
            pfv_out           => pfv
        );

        pfv_stb        <= pfv.stb;
        pfv_insn       <= pfv.insn;
        pfv_order      <= pfv.order;
        pfv_intr       <= pfv.intr;
        pfv_cia        <= pfv.cia;
        pfv_nia        <= pfv.nia;

        pfv_ra_index   <= pfv.ra.index;
        pfv_ra_r_stb   <= pfv.ra.r_stb;
        pfv_ra_r_data  <= pfv.ra.r_data;
        pfv_ra_w_stb   <= pfv.ra.w_stb;
        pfv_ra_w_data  <= pfv.ra.w_data;
        pfv_rb_index   <= pfv.rb.index;
        pfv_rb_r_stb   <= pfv.rb.r_stb;
        pfv_rb_r_data  <= pfv.rb.r_data;
        pfv_rs_index   <= pfv.rs.index;
        pfv_rs_r_stb   <= pfv.rs.r_stb;
        pfv_rs_r_data  <= pfv.rs.r_data;
        pfv_rt_index   <= pfv.rt.index;
        pfv_rt_r_stb   <= pfv.rt.r_stb;
        pfv_rt_r_data  <= pfv.rt.r_data;
        pfv_rt_w_stb   <= pfv.rt.w_stb;
        pfv_rt_w_data  <= pfv.rt.w_data;

        pfv_cr0_r_stb  <= pfv.cr(0).r_stb;
        pfv_cr0_r_data <= pfv.cr(0).r_data;
        pfv_cr0_w_stb  <= pfv.cr(0).w_stb;
        pfv_cr0_w_data <= pfv.cr(0).w_data;
        pfv_cr1_r_stb  <= pfv.cr(1).r_stb;
        pfv_cr1_r_data <= pfv.cr(1).r_data;
        pfv_cr1_w_stb  <= pfv.cr(1).w_stb;
        pfv_cr1_w_data <= pfv.cr(1).w_data;
        pfv_cr2_r_stb  <= pfv.cr(2).r_stb;
        pfv_cr2_r_data <= pfv.cr(2).r_data;
        pfv_cr2_w_stb  <= pfv.cr(2).w_stb;
        pfv_cr2_w_data <= pfv.cr(2).w_data;
        pfv_cr3_r_stb  <= pfv.cr(3).r_stb;
        pfv_cr3_r_data <= pfv.cr(3).r_data;
        pfv_cr3_w_stb  <= pfv.cr(3).w_stb;
        pfv_cr3_w_data <= pfv.cr(3).w_data;
        pfv_cr4_r_stb  <= pfv.cr(4).r_stb;
        pfv_cr4_r_data <= pfv.cr(4).r_data;
        pfv_cr4_w_stb  <= pfv.cr(4).w_stb;
        pfv_cr4_w_data <= pfv.cr(4).w_data;
        pfv_cr5_r_stb  <= pfv.cr(5).r_stb;
        pfv_cr5_r_data <= pfv.cr(5).r_data;
        pfv_cr5_w_stb  <= pfv.cr(5).w_stb;
        pfv_cr5_w_data <= pfv.cr(5).w_data;
        pfv_cr6_r_stb  <= pfv.cr(6).r_stb;
        pfv_cr6_r_data <= pfv.cr(6).r_data;
        pfv_cr6_w_stb  <= pfv.cr(6).w_stb;
        pfv_cr6_w_data <= pfv.cr(6).w_data;
        pfv_cr7_r_stb  <= pfv.cr(7).r_stb;
        pfv_cr7_r_data <= pfv.cr(7).r_data;
        pfv_cr7_w_stb  <= pfv.cr(7).w_stb;
        pfv_cr7_w_data <= pfv.cr(7).w_data;

end architecture behave;

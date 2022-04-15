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

	terminated_out   : out std_logic;

        pfv_out : out pfv_t
        );
end entity toplevel;

architecture behave of toplevel is
begin
    core: entity work.core
        generic map (
            SIM                 => false,
            DISABLE_FLATTEN     => true,
            EX1_BYPASS          => false,
            HAS_FPU             => false,
            HAS_BTC             => false,
            HAS_SHORT_MULT      => false
            --LOG_LENGTH          => 0,
            --ICACHE_NUM_LINES    => 0,
            --ICACHE_NUM_WAYS     => 0,
            --ICACHE_TLB_SIZE     => 0,
            --DCACHE_NUM_LINES    => 0,
            --DCACHE_NUM_WAYS     => 0,
            --DCACHE_TLB_SET_SIZE => 0,
            --DCACHE_TLB_NUM_WAYS => 0
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

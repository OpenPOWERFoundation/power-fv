import power_fv as pfv

from amaranth import *
from amaranth.asserts import *

from _wrapper import MicrowattWrapper


class SmokeCheck(Elaboratable):
    def __init__(self):
        self.dut  = pfv.Interface()
        self.pre  = Signal()
        self.post = Signal()

    def elaborate(self, platform):
        m = Module()
        with m.If(self.post):
            m.d.comb += Assume(self.dut.stb)
        return m


if __name__ == "__main__":
    dut   = MicrowattWrapper()
    check = SmokeCheck()
    tb    = pfv.Testbench(check, dut, t_post=0)
    plat  = pfv.SymbiYosysPlatform()

    microwatt_files = [
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
        "ppc_fx_insns.vhdl",
        "register_file.vhdl",
        "rotator.vhdl",
        "utils.vhdl",
        "wishbone_types.vhdl",
        "writeback.vhdl",
    ]
    import os
    for filename in microwatt_files:
        file = open(os.path.join(os.curdir, "microwatt", filename), "r")
        plat.add_file(filename, file.read())

    plat.build(tb, name="smoke_tb",
        sby_depth=2, sby_skip=1,
        ghdl_top="core", ghdl_opts="--std=08 --no-formal",
        # TODO: investigate why combinatorial loops appear with `prep -flatten -nordff`
        prep_opts="-nordff",
    )

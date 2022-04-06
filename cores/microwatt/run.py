import argparse
import os

from amaranth import *
from amaranth.asserts import *

from power_fv import pfv
from power_fv.tb import Testbench
from power_fv.build import SymbiYosysPlatform

from _wrapper import MicrowattWrapper


class SmokeCheck(Elaboratable):
    def __init__(self, mode="bmc"):
        self.mode = mode
        self.pre  = Signal()
        self.post = Signal()
        self.pfv  = pfv.Interface()

    def elaborate(self, platform):
        m = Module()

        if self.mode == "bmc":
            with m.If(self.pre):
                m.d.comb += Assume(self.pfv.stb)

        if self.mode == "cover":
            m.d.comb += Cover(self.pfv.stb)

        return m


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", help="mode", type=str, choices=("cover", "bmc"), default="bmc")
    parser.add_argument("--pre",  help="pre-condition step, in clock cycles (default: 10)",  type=int, default=10)
    parser.add_argument("--post", help="post-condition step, in clock cycles (default: 10)", type=int, default=10)

    args = parser.parse_args()

    microwatt   = MicrowattWrapper()
    smoke_check = SmokeCheck(mode=args.mode)
    smoke_tb    = Testbench(smoke_check, microwatt, t_pre=args.pre, t_post=args.post)
    platform    = SymbiYosysPlatform()

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

    for filename in microwatt_files:
        file = open(os.path.join(os.curdir, "microwatt", filename), "r")
        platform.add_file(filename, file.read())

    platform.add_file("microwatt_top.vhdl", open(os.path.join(os.curdir, "microwatt_top.vhdl"), "r"))

    platform.build(smoke_tb, name="smoke_tb", build_dir="build/smoke",
        ghdl_opts="--std=08 --no-formal",
        # TODO: investigate why combinatorial loops appear with `prep -flatten -nordff`
        prep_opts="-nordff",
    )

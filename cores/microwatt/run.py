import argparse
import os

from amaranth import *
from amaranth.asserts import *

from power_fv import pfv
from power_fv.checks import *
from power_fv.tb import Testbench
from power_fv.build import SymbiYosysPlatform

from _wrapper import MicrowattWrapper


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("check", help="check", type=str, choices=("unique", "ia_fwd"))
    parser.add_argument("--mode", help="mode", type=str, choices=("cover", "bmc"), default="bmc")
    parser.add_argument("--pre",  help="pre-condition step, in clock cycles (default: 15)",  type=int, default=15)
    parser.add_argument("--post", help="post-condition step, in clock cycles (default: 15)", type=int, default=15)

    args = parser.parse_args()

    check = None
    if args.check == "unique":
        check = UniquenessCheck() if args.mode == "bmc" else UniquenessCover()
    if args.check == "ia_fwd":
        check = IAForwardCheck() if args.mode == "bmc" else IAForwardCover()

    cpu       = MicrowattWrapper()
    testbench = Testbench(check, cpu, t_pre=args.pre, t_post=args.post)
    platform  = SymbiYosysPlatform()

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

        "powerfv_types.vhdl",
        "powerfv.vhdl",
    ]

    for filename in microwatt_files:
        file = open(os.path.join(os.curdir, "microwatt", filename), "r")
        platform.add_file(filename, file.read())

    platform.add_file("microwatt_top.vhdl", open(os.path.join(os.curdir, "microwatt_top.vhdl"), "r"))

    platform.build(testbench,
        name      = f"{args.check}_{args.mode}_tb",
        build_dir = f"build/{args.check}_{args.mode}",
        mode      = args.mode,
        ghdl_opts = "--std=08",
        # TODO: investigate why combinatorial loops appear with `prep -flatten -nordff`
        prep_opts = "-nordff",
    )

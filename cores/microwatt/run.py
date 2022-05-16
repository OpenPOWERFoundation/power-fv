import argparse
import importlib
import os
import multiprocessing

from amaranth import *

from power_fv.tb import Testbench
from power_fv.build import SymbiYosysPlatform

from _wrapper import MicrowattWrapper


def microwatt_files():
    _filenames = (
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

    for filename in _filenames:
        contents = open(os.path.join(os.curdir, "microwatt", filename), "r").read()
        yield filename, contents

    top_filename = "microwatt_top.vhdl"
    top_contents = open(os.path.join(os.curdir, top_filename), "r").read()
    yield top_filename, top_contents


def run_check(module_name, pre, post):
    module = importlib.import_module(f".{module_name}", package="power_fv.checks")
    check  = module.Check()
    cpu    = MicrowattWrapper()
    top    = Testbench(check, cpu, t_pre=pre, t_post=post)

    platform = SymbiYosysPlatform()
    for filename, contents in microwatt_files():
        platform.add_file(filename, contents)

    top_name  = "{}_tb".format(module_name)
    build_dir = "build/{}".format(top_name)

    platform.build(
        top       = top,
        name      = top_name,
        build_dir = build_dir,
        mode      = "bmc",
        ghdl_opts = "--std=08",
        prep_opts = "-nordff",
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-j", "--jobs",
        help="Number of worker processes (default: os.cpu_count())",
        type=int,
        default=os.cpu_count(),
    )

    args = parser.parse_args()

    checks = [
        # name           pre   post
        ("unique",       12,   15),
        ("ia_fwd",       None, 15),
        ("gpr",          None, 15),
        ("cr",           None, 15),
        ("spr",          None, 15),
    ]

    with multiprocessing.Pool(processes=args.jobs) as pool:
        pool.starmap(run_check, checks)

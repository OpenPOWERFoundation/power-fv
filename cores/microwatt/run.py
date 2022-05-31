import argparse
import os
import multiprocessing

from amaranth import *

from power_fv.checks import *
from power_fv.checks.all import *
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


def run_check(*args):
    check_name, tb_args = args

    check = PowerFVCheck.registry[check_name]()
    dut   = MicrowattWrapper()
    tb    = check.get_testbench(dut, **tb_args)

    platform = SymbiYosysPlatform()
    for filename, contents in microwatt_files():
        platform.add_file(filename, contents)

    tb_name   = "{}_tb".format(check_name)
    build_dir = "build/{}".format(tb_name)

    platform.build(
        top       = tb,
        name      = tb_name,
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
        ("cons_unique",  {"post": 15, "pre": 12}),
        ("cons_ia_fwd",  {"post": 15}),
        ("cons_gpr",     {"post": 15}),
        ("cons_cr",      {"post": 15}),
        ("cons_lr",      {"post": 15}),
        ("cons_ctr",     {"post": 15}),
        ("cons_xer",     {"post": 15}),
        ("cons_tar",     {"post": 15}),
        ("cons_srr0",    {"post": 15}),
        ("cons_srr1",    {"post": 15}),

        ("insn_b",       {"post": 15}),
        ("insn_ba",      {"post": 15}),
        ("insn_bl",      {"post": 15}),
        ("insn_bla",     {"post": 15}),
        ("insn_bc",      {"post": 15}),
        ("insn_bca",     {"post": 15}),
        ("insn_bcl",     {"post": 15}),
        ("insn_bcla",    {"post": 15}),
        ("insn_bclr",    {"post": 15}),
        ("insn_bclrl",   {"post": 15}),
        ("insn_bcctr",   {"post": 15}),
        ("insn_bcctrl",  {"post": 15}),
        ("insn_bctar",   {"post": 15}),
        ("insn_bctarl",  {"post": 15}),

        ("insn_crand",   {"post": 15}),
        ("insn_cror",    {"post": 15}),
        ("insn_crnand",  {"post": 15}),
        ("insn_crxor",   {"post": 15}),
        ("insn_crnor",   {"post": 15}),
        ("insn_crandc",  {"post": 15}),
        ("insn_creqv",   {"post": 15}),
        ("insn_crorc",   {"post": 15}),
        ("insn_mcrf",    {"post": 15}),
    ]

    with multiprocessing.Pool(processes=args.jobs) as pool:
        pool.starmap(run_check, checks)

import argparse
import json
import pathlib

from amaranth import *
from amaranth.sim import *

from power_fv.test.model import Model


__all__ = ["simulate"]


def simulate(tests, *, vcd_file, mem_size=64):
    dut = Model(mem_size=mem_size, mem_aligned=True, muldiv_altops=True)
    sim = Simulator(dut)

    def read_reg(name):
        name = name.lower()
        assert name != "mem"
        if name.startswith("g"):
            return dut.ctx.gpr[int(name[1:])]
        elif hasattr(dut.ctx, name):
            reg = getattr(dut.ctx, name)
            return reg.as_value()
        else:
            return None # unimplemented

    def write_reg(name, value):
        name  = name.lower()
        value = int(value, base=16)
        assert name != "mem"
        if name.startswith("g"):
            return dut.ctx.gpr[int(name[1:])].eq(value)
        elif hasattr(dut.ctx, name):
            reg = getattr(dut.ctx, name)
            return reg.eq(value)
        else:
            return Delay() # unimplemented

    def process():
        for test in tests:
            print("Running test {}...".format(test["name"]))

            # Initialize context

            if "inits" in test:
                for reg in test["inits"]["regs"]:
                    yield write_reg(reg["name"], reg["val"])

                if test["inits"]["mem"]:
                    raise NotImplementedError

                yield Delay()

            # Execute ops

            for op in test["ops"]:
                print(">", " ".join(op["text"]))

                # Check EA

                dut_ea = yield read_reg("IAR")
                tst_ea = int(op["ea"], base=16)
                if dut_ea != tst_ea:
                    raise ValueError("EA mismatch: expected {}, got {}"
                                     .format(op["ea"], dut_ea))

                # Check reads

                for reg in op["regReads"]:
                    dut_val = yield read_reg(reg["name"])
                    tst_val = int(reg["val"], base=16)
                    if dut_val is None:
                        continue
                    if dut_val != tst_val:
                        raise ValueError("Read {} mismatch: expected {:#x}, got {:#x}"
                                         .format(reg["name"], tst_val, dut_val))

                if op["memReads"]:
                    raise NotImplementedError

                # Execute instruction

                tst_opcode = Const(int(op["opcode"], base=16), 32)
                # FIXME(ASAP): OPV testcases use LE=1, but we only support BE; let's try anyway
                yield dut.insn.eq(Cat(tst_opcode.word_select(i, 8) for i in reversed(range(4))) << 32)
                # yield dut.insn.eq(tst_opcode << 32)
                yield dut.stb.eq(1)
                yield Delay()

                if (yield dut.err.insn):
                    raise ValueError("Unknown/conflicting opcode: {:#x}"
                                     .format(tst_opcode))

                yield Tick()
                yield Delay()

                # Check writes

                for reg in op["regWrites"]:
                    dut_val = yield read_reg(reg["name"])
                    tst_val = int(reg["val"], base=16)
                    if dut_val is None:
                        continue
                    if dut_val != tst_val:
                        raise ValueError("Write {} mismatch: expected {:#x}, got {:#x}"
                                         .format(reg["name"], tst_val, dut_val))

                if op["memWrites"]:
                    raise NotImplementedError

            # Check results

            if "results" in test:
                for reg in test["results"]["regs"]:
                    dut_val = yield read_reg(reg["name"])
                    tst_val = int(reg["val"], base=16)
                    if dut_val is None:
                        continue
                    if dut_val != tst_val:
                        raise ValueError("Result {} mismatch: expected {:#x}, got {:#x}"
                                         .format(reg["name"], tst_val, dut_val))

                if test["results"]["mem"]:
                    raise NotImplementedError

            yield dut.stb.eq(0)
            yield Delay()

    sim.add_clock(1e-6)
    sim.add_sync_process(process)

    with sim.write_vcd(vcd_file):
        sim.run()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=pathlib.Path)
    parser.add_argument("-o", "--output", type=argparse.FileType("w"))
    args = parser.parse_args()

    with open(args.input, "r") as f:
        tests = json.loads(f.read())

    simulate(tests, vcd_file=args.output)

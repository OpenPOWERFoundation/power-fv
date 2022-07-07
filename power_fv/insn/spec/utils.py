from amaranth import *
from amaranth.utils import bits_for


__all__ = ["iea"]


def iea(addr, msr_sf):
    "Instruction Effective Address. In 32-bit mode (MSR.SF = 0), bits 0:31 are ignored."
    addr, msr_sf = Value.cast(addr), Value.cast(msr_sf)
    assert len(msr_sf) == 1
    mask = Cat(Repl(1, 32), Repl(msr_sf, 32))
    return addr & mask

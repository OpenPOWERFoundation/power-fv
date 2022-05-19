from amaranth import *
from amaranth.utils import bits_for


__all__ = ["iea_mask"]


def iea_mask(addr, msr_sf):
    "Instruction effective address mask. In 32-bit mode (MSR.SF = 0), the upper 32 bits are cleared."
    addr, msr_sf = Value.cast(addr), Value.cast(msr_sf)
    assert len(msr_sf) == 1
    mask = Cat(Repl(1, 32), Repl(msr_sf, 32))
    return addr & mask

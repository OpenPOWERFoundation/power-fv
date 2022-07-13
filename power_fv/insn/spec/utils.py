from amaranth import *


__all__ = ["iea", "byte_reversed"]


def iea(addr, msr_sf):
    "Instruction Effective Address. In 32-bit mode (MSR.SF = 0), bits 0:31 are ignored."
    addr, msr_sf = Value.cast(addr), Value.cast(msr_sf)
    assert len(msr_sf) == 1
    mask = Cat(Repl(1, 32), Repl(msr_sf, 32))
    return addr & mask


def byte_reversed(src, en=0):
    src, en = Value.cast(src), Value.cast(en)
    assert len(src) in {8, 16, 32, 64}
    res = Cat(src.word_select(i, width=8) for i in reversed(range(len(src) // 8)))
    return Mux(en, res, src)

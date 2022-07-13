from amaranth import *
from amaranth.utils import log2_int

from power_fv import pfv
from power_fv.insn.const import *

from . import InsnSpec
from .utils import iea, byte_reversed


__all__ = ["LoadStoreSpec"]


class LoadStoreSpec(InsnSpec, Elaboratable):
    def __init__(self, insn, *, dword_aligned=False):
        self.pfv  = pfv.Interface()
        self.insn = insn
        self.dword_aligned = dword_aligned

    def elaborate(self, platform):
        m = Module()

        m.d.comb += [
            self.pfv.stb .eq(1),
            self.pfv.insn.eq(Cat(Const(0, 32), self.insn.as_value())),
            self.pfv.nia .eq(iea(self.pfv.cia + 4, self.pfv.msr.r_data.sf)),
            self.pfv.msr.r_mask.sf.eq(1),
        ]

        # EA (effective address) = ea_base + ea_offset

        ea        = Signal(64)
        ea_base   = Signal(64)
        ea_offset = Signal(64)

        # ea_base : (RA|0) or (RA)

        m.d.comb += self.pfv.ra.index.eq(self.insn.RA)

        if isinstance(self.insn, (
            LBZ, LBZX, LHZ, LHZX, LHA, LHAX, LWZ, LWZX,
            STB, STBX, STH, STHX, STW, STWX,
            LWBRX, STHBRX, STWBRX
            )):
            m.d.comb += [
                self.pfv.ra.r_stb.eq(self.insn.RA != 0),
                ea_base.eq(Mux(self.insn.RA != 0, self.pfv.ra.r_data, 0)),
            ]
        elif isinstance(self.insn, (
            LBZU, LBZUX, LHZU, LHZUX, LHAU, LHAUX, LWZU, LWZUX,
            STBU, STBUX, STHU, STHUX, STWU, STWUX
            )):
            m.d.comb += [
                self.pfv.ra.r_stb.eq(1),
                ea_base.eq(self.pfv.ra.r_data),
            ]
        else:
            assert False

        # ea_offset : EXTS(D) or (RB)

        if isinstance(self.insn, (
            LBZ, LBZU, LHZ, LHZU, LHA, LHAU, LWZ, LWZU,
            STB, STBU, STH, STHU, STW, STWU,
            )):
            m.d.comb += ea_offset.eq(self.insn.D.as_signed())
        elif isinstance(self.insn, (
            LBZX, LBZUX, LHZX, LHZUX, LHAX, LHAUX, LWZX, LWZUX,
            STBX, STBUX, STHX, STHUX, STWX, STWUX,
            LWBRX, STHBRX, STWBRX,
            )):
            m.d.comb += [
                self.pfv.rb.index.eq(self.insn.RB),
                self.pfv.rb.r_stb.eq(1),
                ea_offset.eq(self.pfv.rb.r_data)
            ]
        else:
            assert False

        m.d.comb += ea.eq(iea(ea_base + ea_offset, self.pfv.msr.r_data.sf))

        # If `dword_aligned` is set, `pfv.mem.addr` points to the dword containing EA.
        # If `dword_aligned` is unset, `pfv.mem.addr` is equal to EA.

        byte_offset = Signal(3)
        half_offset = Signal(2)
        word_offset = Signal(1)

        m.d.comb += self.pfv.mem.addr[3:].eq(ea[3:])

        if self.dword_aligned:
            m.d.comb += [
                self.pfv.mem.addr[:3].eq(0),
                byte_offset.eq(ea[:3]),
            ]
        else:
            m.d.comb += [
                self.pfv.mem.addr[:3].eq(ea[:3]),
                byte_offset.eq(0),
            ]

        m.d.comb += [
            half_offset.eq(byte_offset[1:]),
            word_offset.eq(byte_offset[2:]),
        ]

        msr_le = self.pfv.msr.r_data.le
        m.d.comb += self.pfv.msr.r_mask.le.eq(1)

        # Load: read from memory, then write the result to RT.

        if isinstance(self.insn, (
            LBZ, LBZX, LBZU, LBZUX,
            LHZ, LHZX, LHZU, LHZUX,
            LHA, LHAX, LHAU, LHAUX,
            LWZ, LWZX, LWZU, LWZUX,
            LWBRX,
            )):
            load_byte   = Signal( 8)
            load_half   = Signal(16)
            load_word   = Signal(32)
            load_result = Signal(64)

            m.d.comb += [
                load_byte.eq(self.pfv.mem.r_data.word_select(byte_offset, width= 8)),
                load_half.eq(self.pfv.mem.r_data.word_select(half_offset, width=16)),
                load_word.eq(self.pfv.mem.r_data.word_select(word_offset, width=32)),
            ]

            if isinstance(self.insn, (LBZ, LBZX, LBZU, LBZUX)):
                m.d.comb += [
                    self.pfv.mem.r_mask.word_select(byte_offset, width=1).eq(0x1),
                    load_result.eq(load_byte.as_unsigned()),
                ]
            elif isinstance(self.insn, (LHZ, LHZX, LHZU, LHZUX)):
                m.d.comb += [
                    self.pfv.mem.r_mask.word_select(half_offset, width=2).eq(0x3),
                    load_result.eq(byte_reversed(load_half, ~msr_le).as_unsigned()),
                ]
            elif isinstance(self.insn, (LHA, LHAX, LHAU, LHAUX)):
                m.d.comb += [
                    self.pfv.mem.r_mask.word_select(half_offset, width=2).eq(0x3),
                    load_result.eq(byte_reversed(load_half, ~msr_le).as_signed())
                ]
            elif isinstance(self.insn, (LWZ, LWZX, LWZU, LWZUX)):
                m.d.comb += [
                    self.pfv.mem.r_mask.word_select(word_offset, width=4).eq(0xf),
                    load_result.eq(byte_reversed(load_word, ~msr_le).as_unsigned()),
                ]
            elif isinstance(self.insn, LWBRX):
                m.d.comb += [
                    self.pfv.mem.r_mask.word_select(word_offset, width=4).eq(0xf),
                    load_result.eq(byte_reversed(load_word, msr_le).as_unsigned()),
                ]
            else:
                assert False

            m.d.comb += [
                self.pfv.rt.index .eq(self.insn.RT),
                self.pfv.rt.w_stb .eq(1),
                self.pfv.rt.w_data.eq(load_result),
            ]

        # Store: read from RS, then write the result to memory.

        elif isinstance(self.insn, (
            STB, STBX, STBU, STBUX,
            STH, STHX, STHU, STHUX,
            STW, STWX, STWU, STWUX,
            STHBRX, STWBRX,
            )):
            store_byte = Signal(64)
            store_half = Signal(64)
            store_word = Signal(64)

            m.d.comb += [
                self.pfv.rs.index.eq(self.insn.RS),
                self.pfv.rs.r_stb.eq(1),

                store_byte.eq(Repl(self.pfv.rs.r_data[: 8], count=8)),
                store_half.eq(Repl(self.pfv.rs.r_data[:16], count=4)),
                store_word.eq(Repl(self.pfv.rs.r_data[:32], count=2)),
            ]

            if isinstance(self.insn, (STB, STBX, STBU, STBUX)):
                m.d.comb += [
                    self.pfv.mem.w_mask.word_select(byte_offset, width=1).eq(0x1),
                    self.pfv.mem.w_data.eq(store_byte),
                ]
            elif isinstance(self.insn, (STH, STHX, STHU, STHUX)):
                m.d.comb += [
                    self.pfv.mem.w_mask.word_select(half_offset, width=2).eq(0x3),
                    self.pfv.mem.w_data.eq(byte_reversed(store_half, ~msr_le)),
                ]
            elif isinstance(self.insn, (STW, STWX, STWU, STWUX)):
                m.d.comb += [
                    self.pfv.mem.w_mask.word_select(word_offset, width=4).eq(0xf),
                    self.pfv.mem.w_data.eq(byte_reversed(store_word, ~msr_le)),
                ]
            elif isinstance(self.insn, STHBRX):
                m.d.comb += [
                    self.pfv.mem.w_mask.word_select(half_offset, width=2).eq(0x3),
                    self.pfv.mem.w_data.eq(byte_reversed(store_half, msr_le)),
                ]
            elif isinstance(self.insn, STWBRX):
                m.d.comb += [
                    self.pfv.mem.w_mask.word_select(word_offset, width=4).eq(0xf),
                    self.pfv.mem.w_data.eq(byte_reversed(store_word, msr_le)),
                ]
            else:
                assert False

        else:
            assert False

        # Load/store with update: write EA to RA.

        if isinstance(self.insn, (
            LBZU, LBZUX, LHZU, LHZUX, LHAU, LHAUX, LWZU, LWZUX,
            STBU, STBUX, STHU, STHUX, STWU, STWUX,
            )):
            m.d.comb += [
                self.pfv.ra.w_stb .eq(1),
                self.pfv.ra.w_data.eq(ea),
            ]

        # Interrupt causes

        intr = Record([
            ("misaligned",  1),
            ("update_zero", 1),
            ("update_rt",   1),
        ])

        if isinstance(self.insn, (
            LBZ, LBZX, LBZU, LBZUX,
            STB, STBX, STBU, STBUX,
            )):
            m.d.comb += intr.misaligned.eq(0)
        elif isinstance(self.insn, (
            LHZ, LHZX, LHZU, LHZUX, LHA, LHAX, LHAU, LHAUX,
            STH, STHX, STHU, STHUX,
            STHBRX,
            )):
            m.d.comb += intr.misaligned.eq(byte_offset[0])
        elif isinstance(self.insn, (
            LWZ, LWZX, LWZU, LWZUX,
            STW, STWX, STWU, STWUX,
            LWBRX, STWBRX,
            )):
            m.d.comb += intr.misaligned.eq(byte_offset[:1].any())
        else:
            assert False

        if isinstance(self.insn, (
            LBZU, LBZUX, LHZU, LHZUX, LHAU, LHAUX, LWZU, LWZUX,
            STBU, STBUX, STHU, STHUX, STWU, STWUX,
            )):
            m.d.comb += intr.update_zero.eq(self.insn.RA == 0)
        else:
            m.d.comb += intr.update_zero.eq(0)

        if isinstance(self.insn, (
            LBZU, LBZUX, LHZU, LHZUX, LHAU, LHAUX, LWZU, LWZUX,
            )):
            m.d.comb += intr.update_rt.eq(self.insn.RA == self.insn.RT)
        else:
            m.d.comb += intr.update_rt.eq(0)

        m.d.comb += self.pfv.intr.eq(intr.any())

        return m

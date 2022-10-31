from amaranth import *
from amaranth.utils import log2_int

from power_fv import pfv
from power_fv.insn.const import *
from power_fv.intr import *

from . import InsnSpec
from .utils import iea, byte_reversed, msr_to_srr1


__all__ = ["LoadStoreSpec"]


class LoadStoreSpec(InsnSpec, Elaboratable):
    def elaborate(self, platform):
        m = Module()

        m.d.comb += [
            self.insn    .eq(self.pfv.insn[32:]),
            self.pfv.stb .eq(self.insn.is_valid() & ~self.pfv.insn[:32].any()),
            self.pfv.msr.r_mask.sf.eq(1),
        ]

        # Raise an interrupt if RA is invalid

        illegal_insn = Record([
            ("ra_zero", 1),
            ("ra_rt"  , 1),
        ])

        if isinstance(self.insn, (
            LBZU, LBZUX, LHZU, LHZUX, LHAU, LHAUX, LWZU, LWZUX,
            STBU, STBUX, STHU, STHUX, STWU, STWUX,
            )):
            m.d.comb += illegal_insn.ra_zero.eq(self.insn.RA == 0)
        if isinstance(self.insn, (
            LBZU, LBZUX, LHZU, LHZUX, LHAU, LHAUX, LWZU, LWZUX,
            )):
            m.d.comb += illegal_insn.ra_rt.eq(self.insn.RA == self.insn.RT)

        with m.If(illegal_insn.any()):
            if self.pfv.illegal_insn_heai:
                raise NotImplementedError

            m.d.comb += [
                self.pfv.intr.eq(1),
                self.pfv.nia .eq(INTR_PROGRAM.vector_addr),
                INTR_PROGRAM.write_msr(self.pfv.msr),

                self.pfv.srr0.w_mask.eq(Repl(1, 64)),
                self.pfv.srr0.w_data.eq(iea(self.pfv.cia, self.pfv.msr.r_data.sf)),

                self.pfv.srr1.w_mask[63-36:64-33].eq(Repl(1, 4)),
                self.pfv.srr1.w_data[63-36:64-33].eq(0),
                self.pfv.srr1.w_mask[63-42].eq(1),
                self.pfv.srr1.w_data[63-42].eq(0),
                self.pfv.srr1.w_mask[63-46:64-43].eq(Repl(1, 4)),
                self.pfv.srr1.w_data[63-46:64-43].eq(0b0100), # Illegal Instruction type (deprecated)
                self.pfv.srr1.w_mask[63-47].eq(1),
                self.pfv.srr1.w_data[63-47].eq(0),

                msr_to_srr1(self.pfv.msr, self.pfv.srr1,  0, 32),
                msr_to_srr1(self.pfv.msr, self.pfv.srr1, 37, 41),
                msr_to_srr1(self.pfv.msr, self.pfv.srr1, 48, 63),
            ]

        with m.Else():
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

            # The value of `pfv.mem.addr` must be equal to EA, rounded down to a multiple of
            # ``2 ** pfv.mem_alignment``.

            m.d.comb += [
                self.pfv.mem.addr[self.pfv.mem_alignment:].eq(ea[self.pfv.mem_alignment:]),
                self.pfv.mem.addr[:self.pfv.mem_alignment].eq(0),
            ]

            # Raise an Alignment Interrupt if EA is misaligned to the size of the storage operand
            # and to ``2 ** pfv.mem_alignment``.

            byte_offset = Signal(3)
            half_offset = Signal(2)
            word_offset = Signal(1)

            m.d.comb += [
                byte_offset.eq(ea[:self.pfv.mem_alignment]),
                half_offset.eq(byte_offset[1:]),
                word_offset.eq(byte_offset[2:]),
            ]

            ea_misaligned = Signal()

            if isinstance(self.insn, (
                LBZ, LBZX, LBZU, LBZUX,
                STB, STBX, STBU, STBUX,
                )):
                m.d.comb += ea_misaligned.eq(0)
            elif isinstance(self.insn, (
                LHZ, LHZX, LHZU, LHZUX, LHA, LHAX, LHAU, LHAUX,
                STH, STHX, STHU, STHUX,
                STHBRX,
                )):
                m.d.comb += ea_misaligned.eq(byte_offset[0])
            elif isinstance(self.insn, (
                LWZ, LWZX, LWZU, LWZUX,
                STW, STWX, STWU, STWUX,
                LWBRX, STWBRX,
                )):
                m.d.comb += ea_misaligned.eq(byte_offset[:1].any())
            else:
                assert False

            with m.If(ea_misaligned):
                m.d.comb += [
                    self.pfv.intr.eq(1),
                    self.pfv.nia .eq(INTR_ALIGNMENT.vector_addr),
                    INTR_ALIGNMENT.write_msr(self.pfv.msr),

                    self.pfv.srr0.w_mask.eq(Repl(1, 64)),
                    self.pfv.srr0.w_data.eq(iea(self.pfv.cia, self.pfv.msr.r_data.sf)),

                    self.pfv.srr1.w_mask[63-36:64-33].eq(Repl(1, 4)),
                    self.pfv.srr1.w_mask[63-36:64-33].eq(0),
                    self.pfv.srr1.w_mask[63-47:64-42].eq(Repl(1, 6)),
                    self.pfv.srr1.w_mask[63-47:64-42].eq(0),

                    msr_to_srr1(self.pfv.msr, self.pfv.srr1,  0, 32),
                    msr_to_srr1(self.pfv.msr, self.pfv.srr1, 37, 41),
                    msr_to_srr1(self.pfv.msr, self.pfv.srr1, 48, 63),
                ]

            with m.Else():
                m.d.comb += self.pfv.msr.r_mask.le.eq(1)
                msr_le = self.pfv.msr.r_data.le

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

            # Update NIA

            m.d.comb += self.pfv.nia.eq(iea(self.pfv.cia + 4, self.pfv.msr.r_data.sf))

        return m

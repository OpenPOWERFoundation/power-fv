from amaranth import *
from amaranth.lib.coding import Encoder

from power_fv import pfv
from power_fv.insn.const import *

from . import InsnSpec
from .utils import iea


__all__ = ["LogicalSpec"]


class _CountTrailingZeros(Elaboratable):
    def __init__(self, width):
        self.width = width
        self.i = Signal(width)
        self.o = Signal(range(width + 1))

    def elaborate(self, platform):
        m = Module()
        m.submodules.lsb_enc = lsb_enc = Encoder(self.width)
        m.d.comb += [
            lsb_enc.i.eq(self.i & -self.i),
            self.o.eq(Mux(lsb_enc.n, self.width, lsb_enc.o)),
        ]
        return m


class LogicalSpec(InsnSpec, Elaboratable):
    def elaborate(self, platform):
        m = Module()

        m.d.comb += [
            self.pfv.stb .eq(1),
            self.pfv.insn.eq(Cat(Const(0, 32), self.insn.as_value())),
            self.pfv.intr.eq(0),
            self.pfv.nia .eq(iea(self.pfv.cia + 4, self.pfv.msr.r_data.sf)),
            self.pfv.msr.r_mask.sf.eq(1),
        ]

        src_a = Signal(unsigned(64))
        src_b = Signal(unsigned(64))

        # Operand A : (RS)

        m.d.comb += [
            self.pfv.rs.index.eq(self.insn.RS),
            self.pfv.rs.r_stb.eq(1),
            src_a.eq(self.pfv.rs.r_data),
        ]

        # Operand B : EXTZ(UI) or EXTZ(UI<<16) or (RB)

        if isinstance(self.insn, (ANDI_, ORI, XORI)):
            m.d.comb += src_b.eq(self.insn.UI)
        elif isinstance(self.insn, (ANDIS_, ORIS, XORIS)):
            m.d.comb += src_b.eq(Cat(Const(0, 16), self.insn.UI).as_unsigned())
        elif isinstance(self.insn, (
            AND , AND_, XOR , XOR_ , NAND, NAND_,
            OR  , OR_ , ORC , ORC_ , NOR , NOR_ ,
            EQV , EQV_, ANDC, ANDC_,
            CMPB,
            )):
            m.d.comb += [
                self.pfv.rb.index.eq(self.insn.RB),
                self.pfv.rb.r_stb.eq(1),
                src_b.eq(self.pfv.rb.r_data),
            ]
        elif isinstance(self.insn, (
            EXTSB  , EXTSB_ , EXTSH , EXTSH_ ,
            CNTLZW , CNTLZW_, CNTTZW, CNTTZW_,
            POPCNTB, POPCNTW, PRTYW ,
            )):
            pass
        else:
            assert False

        result = Signal(64)

        if isinstance(self.insn, (ANDI_, ANDIS_, AND, AND_)):
            m.d.comb += result.eq(src_a & src_b)
        elif isinstance(self.insn, (ORI, ORIS, OR, OR_)):
            m.d.comb += result.eq(src_a | src_b)
        elif isinstance(self.insn, (XORI, XORIS, XOR, XOR_)):
            m.d.comb += result.eq(src_a ^ src_b)
        elif isinstance(self.insn, (NAND, NAND_)):
            m.d.comb += result.eq(~(src_a & src_b))
        elif isinstance(self.insn, (ORC, ORC_)):
            m.d.comb += result.eq(src_a | ~src_b)
        elif isinstance(self.insn, (NOR, NOR_)):
            m.d.comb += result.eq(~(src_a | src_b))
        elif isinstance(self.insn, (EQV, EQV_)):
            m.d.comb += result.eq(~(src_a ^ src_b))
        elif isinstance(self.insn, (ANDC, ANDC_)):
            m.d.comb += result.eq(src_a & ~src_b)

        elif isinstance(self.insn, (EXTSB, EXTSB_)):
            m.d.comb += result.eq(src_a[: 8].as_signed())
        elif isinstance(self.insn, (EXTSH, EXTSH_)):
            m.d.comb += result.eq(src_a[:16].as_signed())

        elif isinstance(self.insn, CMPB):
            for i in range(64//8):
                a_byte = src_a .word_select(i, width=8)
                b_byte = src_b .word_select(i, width=8)
                r_byte = result.word_select(i, width=8)
                m.d.comb += r_byte.eq(Mux(a_byte == b_byte, 0xff, 0x00))

        elif isinstance(self.insn, (CNTLZW, CNTLZW_, CNTTZW, CNTTZW_)):
            m.submodules.cnttz = cnttz = _CountTrailingZeros(width=32)
            if isinstance(self.insn, (CNTTZW, CNTTZW_)):
                m.d.comb += cnttz.i.eq(src_a[:32])
            if isinstance(self.insn, (CNTLZW, CNTLZW_)):
                m.d.comb += cnttz.i.eq(Cat(reversed(src_a[:32])))
            m.d.comb += result.eq(cnttz.o)

        elif isinstance(self.insn, POPCNTB):
            for i in range(64//8):
                a_byte = src_a .word_select(i, width=8)
                r_byte = result.word_select(i, width=8)
                m.d.comb += r_byte.eq(sum(a_bit for a_bit in a_byte))

        elif isinstance(self.insn, POPCNTW):
            for i in range(64//32):
                a_word = src_a .word_select(i, width=32)
                r_word = result.word_select(i, width=32)
                m.d.comb += r_word.eq(sum(a_bit for a_bit in a_word))

        elif isinstance(self.insn, PRTYW):
            prty_lo = 0
            prty_hi = 0
            for i in range(32//8):
                prty_lo ^= src_a[i*8]
                prty_hi ^= src_a[i*8 + 32]
            m.d.comb += result.eq(Cat(prty_lo, Const(0, 31), prty_hi, Const(0, 31)))

        else:
            assert False

        # Write result to RA

        m.d.comb += [
            self.pfv.ra.index .eq(self.insn.RA),
            self.pfv.ra.w_stb .eq(1),
            self.pfv.ra.w_data.eq(result),
        ]

        # Write CR0

        if isinstance(self.insn, (
            ANDI_, ANDIS_, AND_, XOR_, NAND_, OR_, ORC_, NOR_, EQV_, ANDC_,
            EXTSB_, EXTSH_, CNTLZW_, CNTTZW_,
            )):
            cr0_w_mask = Record([("so", 1), ("eq_", 1), ("gt", 1), ("lt", 1)])
            cr0_w_data = Record([("so", 1), ("eq_", 1), ("gt", 1), ("lt", 1)])

            m.d.comb += [
                self.pfv.xer.r_mask.so.eq(1),

                cr0_w_mask    .eq(0b1111),
                cr0_w_data.so .eq(self.pfv.xer.r_data.so),
                cr0_w_data.eq_.eq(~Mux(self.pfv.msr.r_data.sf, result[:64].any(), result[:32].any())),
                cr0_w_data.gt .eq(~(cr0_w_data.lt | cr0_w_data.eq_)),
                cr0_w_data.lt .eq(Mux(self.pfv.msr.r_data.sf, result[63], result[31])),

                self.pfv.cr.w_mask.cr0.eq(cr0_w_mask),
                self.pfv.cr.w_data.cr0.eq(cr0_w_data),
            ]

        return m

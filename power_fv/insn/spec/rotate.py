from amaranth import *

from power_fv import pfv
from power_fv.insn.const import *
from power_fv.intr import *

from . import InsnSpec
from .utils import iea, msr_to_srr1


__all__ = ["RotateShiftSpec"]


class RotateShiftSpec(InsnSpec, Elaboratable):
    def elaborate(self, platform):
        m = Module()

        m.d.comb += [
            self.insn   .eq(self.pfv.insn[32:]),
            self.pfv.stb.eq(self.insn.is_valid() & ~self.pfv.insn[:32].any()),
            self.pfv.msr.r_mask.sf.eq(1),
        ]

        # Raise an interrupt if MB or ME are invalid

        illegal_insn = Record([
            ("mask", 1),
        ])

        if isinstance(self.insn, (RLWINM, RLWINM_, RLWNM, RLWNM_, RLWIMI, RLWIMI_)):
            m.d.comb += illegal_insn.mask.eq((self.insn.MB >= 32) | (self.insn.ME >= 32))

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
            src    = Signal(unsigned(64))
            shamt  = Signal(unsigned( 6))
            rotl   = Signal(unsigned(64))
            mask   = Signal(unsigned(64))
            result = Signal(unsigned(64))

            # Source operand : (RS)(32:63)||(RS)(32:63)

            m.d.comb += [
                self.pfv.rs.index.eq(self.insn.RS),
                self.pfv.rs.r_stb.eq(1),
                src.eq(self.pfv.rs.r_data),
            ]

            # Shift amount : SH or (RB)(59:63)

            if isinstance(self.insn, (RLWINM, RLWINM_, RLWIMI, RLWIMI_, SRAWI, SRAWI_)):
                m.d.comb += shamt.eq(self.insn.SH)
            elif isinstance(self.insn, (RLWNM, RLWNM_, SLW, SLW_, SRW, SRW_, SRAW, SRAW_)):
                m.d.comb += [
                    self.pfv.rb.index.eq(self.insn.RB),
                    self.pfv.rb.r_stb.eq(1),
                    shamt.eq(self.pfv.rb.r_data[:6]),
                ]
            else:
                assert False

            # Mask

            def _mask(mstart, mstop):
                mask     =  ((1 << 64-mstart) - 1) & ~((1 << 63-mstop ) - 1)
                mask_inv = ~((1 << 63-mstop ) - 1) |  ((1 << 64-mstart) - 1)
                return Mux(mstart <= mstop, mask, mask_inv)

            if isinstance(self.insn, (RLWINM, RLWINM_, RLWNM, RLWNM_, RLWIMI, RLWIMI_)):
                m.d.comb += mask.eq(_mask(self.insn.MB+32, self.insn.ME+32))
            elif isinstance(self.insn, (SLW, SLW_)):
                m.d.comb += mask.eq(Mux(shamt[5], 0, _mask(32, 63-shamt)))
            elif isinstance(self.insn, (SRW, SRW_, SRAW, SRAW_)):
                m.d.comb += mask.eq(Mux(shamt[5], 0, _mask(shamt+32, 63)))
            elif isinstance(self.insn, (SRAWI, SRAWI_)):
                m.d.comb += mask.eq(_mask(shamt+32, 63))
            else:
                assert False

            # Rotation

            def _rotl32(src, n):
                v = Repl(src[:32], 2)
                return ((v << n) | (v >> 64-n)) & Repl(1, 64)

            if isinstance(self.insn, (
                RLWINM, RLWINM_, RLWNM, RLWNM_, RLWIMI, RLWIMI_,
                SLW, SLW_,
                )):
                m.d.comb += rotl.eq(_rotl32(src, shamt))
            elif isinstance(self.insn, (SRW, SRW_, SRAWI, SRAWI_, SRAW, SRAW_)):
                m.d.comb += rotl.eq(_rotl32(src, 64-shamt))
            else:
                assert False

            # Write result to RA

            m.d.comb += [
                self.pfv.ra.index .eq(self.insn.RA),
                self.pfv.ra.w_stb .eq(1),
                self.pfv.ra.w_data.eq(result),
            ]

            if isinstance(self.insn, (RLWINM, RLWINM_, RLWNM, RLWNM_, SLW, SLW_, SRW, SRW_)):
                m.d.comb += result.eq(rotl & mask)
            elif isinstance(self.insn, (RLWIMI, RLWIMI_)):
                m.d.comb += self.pfv.ra.r_stb.eq(1)
                m.d.comb += result.eq(rotl & mask | self.pfv.ra.r_data & ~mask)
            elif isinstance(self.insn, (SRAWI, SRAWI_, SRAW, SRAW_)):
                m.d.comb += result.eq(rotl & mask | Repl(src[31], 64) & ~mask)
            else:
                assert False

            # Write CR0

            if isinstance(self.insn, (
                RLWINM_, RLWNM_, RLWIMI_, SLW_, SRW_, SRAWI_, SRAW_,
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

            # Write XER

            if isinstance(self.insn, (SRAWI, SRAWI_, SRAW, SRAW_)):
                carry = Signal()

                m.d.comb += [
                    carry.eq(src[31] & (rotl & ~mask)[:32].any()),

                    self.pfv.xer.w_mask.ca  .eq(1),
                    self.pfv.xer.w_data.ca  .eq(carry),
                    self.pfv.xer.w_mask.ca32.eq(1),
                    self.pfv.xer.w_data.ca32.eq(carry),
                ]

            # Update NIA

            m.d.comb += self.pfv.nia.eq(iea(self.pfv.cia + 4, self.pfv.msr.r_data.sf))

        return m

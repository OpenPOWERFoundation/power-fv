from amaranth import *

from power_fv import pfv
from power_fv.insn.const import *

from . import InsnSpec
from .utils import iea


__all__ = ["BCDAssistSpec"]


class BCDAssistSpec(InsnSpec, Elaboratable):
    def elaborate(self, platform):
        m = Module()

        m.d.comb += [
            self.pfv.stb .eq(1),
            self.pfv.insn.eq(Cat(Const(0, 32), self.insn.as_value())),
            self.pfv.intr.eq(0),
            self.pfv.nia .eq(iea(self.pfv.cia + 4, self.pfv.msr.r_data.sf)),
            self.pfv.msr.r_mask.sf.eq(1),
        ]

        bcd_layout = [(f, 1) for f in reversed("abcdefghijkm")]
        dpd_layout = [(f, 1) for f in reversed("pqrstuvwxy")]

        def _bcd_to_dpd(bcd, dpd):
            # (see PowerISA v3.1, Book I, Appendix B.1)
            stmts = [
                dpd.p.eq((bcd.f & bcd.a & bcd.i & ~bcd.e) | (bcd.j & bcd.a & ~bcd.i) | (bcd.b & ~bcd.a)),
                dpd.q.eq((bcd.g & bcd.a & bcd.i & ~bcd.e) | (bcd.k & bcd.a & ~bcd.i) | (bcd.c & ~bcd.a)),
                dpd.r.eq(bcd.d),

                dpd.s.eq((bcd.j & ~bcd.a & bcd.e & ~bcd.i) | (bcd.f & ~bcd.i & ~bcd.e) | (bcd.f & ~bcd.a & ~bcd.e) | (bcd.e & bcd.i)),
                dpd.t.eq((bcd.k & ~bcd.a & bcd.e & ~bcd.i) | (bcd.g & ~bcd.i & ~bcd.e) | (bcd.g & ~bcd.a & ~bcd.e) | (bcd.a & bcd.i)),
                dpd.u.eq(bcd.h),

                dpd.v.eq(bcd.a | bcd.e | bcd.i),

                dpd.w.eq((~bcd.e & bcd.j & ~bcd.i) | (bcd.e & bcd.i) | bcd.a),
                dpd.x.eq((~bcd.a & bcd.k & ~bcd.i) | (bcd.a & bcd.i) | bcd.e),
                dpd.y.eq(bcd.m),
            ]
            return stmts

        def _dpd_to_bcd(dpd, bcd):
            # (see PowerISA v3.1, Book I, Appendix B.2)
            stmts = [
                bcd.a.eq((~dpd.s & dpd.v & dpd.w) | (dpd.t & dpd.v & dpd.w & dpd.s) | (dpd.v & dpd.w & ~dpd.x)),
                bcd.b.eq((dpd.p & dpd.s & dpd.x & ~dpd.t) | (dpd.p & ~dpd.w) | (dpd.p & ~dpd.v)),
                bcd.c.eq((dpd.q & dpd.s & dpd.x & ~dpd.t) | (dpd.q & ~dpd.w) | (dpd.q & ~dpd.v)),
                bcd.d.eq(dpd.r),

                bcd.e.eq((dpd.v & ~dpd.w & dpd.x) | (dpd.s & dpd.v & dpd.w & dpd.x) | (~dpd.t & dpd.v & dpd.x & dpd.w)),
                bcd.f.eq((dpd.p & dpd.t & dpd.v & dpd.w & dpd.x & ~dpd.s) | (dpd.s & ~dpd.x & dpd.v) | (dpd.s & ~dpd.v)),
                bcd.g.eq((dpd.q & dpd.t & dpd.w & dpd.v & dpd.x & ~dpd.s) | (dpd.t & ~dpd.x & dpd.v) | (dpd.t & ~dpd.v)),
                bcd.h.eq(dpd.u),

                bcd.i.eq((dpd.t & dpd.v & dpd.w & dpd.x) | (dpd.s & dpd.v & dpd.w & dpd.x) | (dpd.v & ~dpd.w & ~dpd.x)),
                bcd.j.eq((dpd.p & ~dpd.s & ~dpd.t & dpd.w & dpd.v) | (dpd.s & dpd.v & ~dpd.w & dpd.x) | (dpd.p & dpd.w & ~dpd.x & dpd.v) | (dpd.w & ~dpd.v)),
                bcd.k.eq((dpd.q & ~dpd.s & ~dpd.t & dpd.v & dpd.w) | (dpd.t & dpd.v & ~dpd.w & dpd.x) | (dpd.q & dpd.v & dpd.w & ~dpd.x) | (dpd.x & ~dpd.v)),
                bcd.m.eq(dpd.y),
            ]
            return stmts

        if isinstance(self.insn, CDTBCD):
            dpd_0 = Record([("lo", dpd_layout), ("hi", dpd_layout)])
            bcd_0 = Record([("lo", bcd_layout), ("hi", bcd_layout)])
            dpd_1 = Record([("lo", dpd_layout), ("hi", dpd_layout)])
            bcd_1 = Record([("lo", bcd_layout), ("hi", bcd_layout)])

            m.d.comb += [
                self.pfv.rs.index.eq(self.insn.RS),
                self.pfv.rs.r_stb.eq(1),
                dpd_0.eq(self.pfv.rs.r_data[63-31:64-12]),
                dpd_1.eq(self.pfv.rs.r_data[63-63:64-44]),

                _dpd_to_bcd(dpd_0.lo, bcd_0.lo),
                _dpd_to_bcd(dpd_0.hi, bcd_0.hi),
                _dpd_to_bcd(dpd_1.lo, bcd_1.lo),
                _dpd_to_bcd(dpd_1.hi, bcd_1.hi),

                self.pfv.ra.index .eq(self.insn.RA),
                self.pfv.ra.w_stb .eq(1),
                self.pfv.ra.w_data[63-31:64- 8].eq(bcd_0),
                self.pfv.ra.w_data[63-63:64-40].eq(bcd_1),
            ]

        elif isinstance(self.insn, CBCDTD):
            bcd_0 = Record([("lo", bcd_layout), ("hi", bcd_layout)])
            dpd_0 = Record([("lo", dpd_layout), ("hi", dpd_layout)])
            bcd_1 = Record([("lo", bcd_layout), ("hi", bcd_layout)])
            dpd_1 = Record([("lo", dpd_layout), ("hi", dpd_layout)])

            m.d.comb += [
                self.pfv.rs.index.eq(self.insn.RS),
                self.pfv.rs.r_stb.eq(1),
                bcd_0.eq(self.pfv.rs.r_data[63-31:64- 8]),
                bcd_1.eq(self.pfv.rs.r_data[63-63:64-40]),

                _bcd_to_dpd(bcd_0.lo, dpd_0.lo),
                _bcd_to_dpd(bcd_0.hi, dpd_0.hi),
                _bcd_to_dpd(bcd_1.lo, dpd_1.lo),
                _bcd_to_dpd(bcd_1.hi, dpd_1.hi),

                self.pfv.ra.index.eq(self.insn.RA),
                self.pfv.ra.w_stb.eq(1),
                self.pfv.ra.w_data[63-31:64-12].eq(dpd_0),
                self.pfv.ra.w_data[63-63:64-44].eq(dpd_1),
            ]

        elif isinstance(self.insn, ADDG6S):
            src_a   = Signal(unsigned(65))
            src_b   = Signal(unsigned(65))
            result  = Signal(unsigned(65))
            cout_6s = Signal(unsigned(64))

            m.d.comb += [
                self.pfv.ra.index.eq(self.insn.RA),
                self.pfv.ra.r_stb.eq(1),
                self.pfv.rb.index.eq(self.insn.RB),
                self.pfv.rb.r_stb.eq(1),

                src_a .eq(self.pfv.ra.r_data),
                src_b .eq(self.pfv.rb.r_data),
                result.eq(src_a + src_b),
            ]

            for i in range(64//4):
                a_bit = src_a [i*4 + 4]
                b_bit = src_b [i*4 + 4]
                r_bit = result[i*4 + 4]
                c_nib = cout_6s.word_select(i, width=4)
                m.d.comb += c_nib.eq(Mux(a_bit ^ b_bit ^ r_bit, 0x0, 0x6))

            m.d.comb += [
                self.pfv.rt.index .eq(self.insn.RT),
                self.pfv.rt.w_stb .eq(1),
                self.pfv.rt.w_data.eq(cout_6s),
            ]

        else:
            assert False

        return m

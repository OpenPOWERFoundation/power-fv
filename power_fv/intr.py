__all__ = [
    "Interrupt",
    "INTR_ALIGNMENT",
    "INTR_PROGRAM",
    "INTR_SYSTEM_CALL",
]


class Interrupt:
    def __init__(self, vector_addr, ir, dr, ee, ri, me, hv, s):
        self.vector_addr = vector_addr
        self.ir  = ir
        self.dr  = dr
        self.ee  = ee
        self.ri  = ri
        self.me  = me
        self.hv  = hv
        self.s   = s

    def write_msr(self, msr):
        def _write_field(field, value):
            stmts = []
            if value is not None:
                stmts.append(getattr(msr.w_mask, field).eq(-1))
                stmts.append(getattr(msr.w_data, field).eq(value))
            return stmts

        # See PowerISA v3.1, Book III, Section 7.5, Figure 67
        stmts = [
            _write_field("ir" , self.ir),
            _write_field("dr" , self.dr),
            _write_field("fe0", 0),
            _write_field("fe1", 0),
            _write_field("ee" , self.ee),
            _write_field("ri" , self.ri),
            _write_field("me" , self.me),
            _write_field("hv" , self.hv),
            _write_field("s"  , self.s),

            _write_field("pr" , 0),
            _write_field("pmm", 0),
            _write_field("te" , 0),
            _write_field("fp" , 0),
            _write_field("vec", 0),
            _write_field("vsx", 0),
            _write_field("sf" , 1),

            msr.w_mask[63- 5].eq(1),
            msr.w_data[63- 5].eq(0),
            msr.w_mask[63-31].eq(1),
            msr.w_data[63-31].eq(0),
        ]
        return stmts


# TODO: Support MSR.{IR,DR,HV,S,LE} bits, which depend on context (e.g. LPCR)

INTR_ALIGNMENT   = Interrupt(0x600, ir=None, dr=None, ee=0, ri=0, me=None, hv=None, s=None)
INTR_PROGRAM     = Interrupt(0x700, ir=None, dr=None, ee=0, ri=0, me=None, hv=None, s=None)
INTR_SYSTEM_CALL = Interrupt(0xC00, ir=None, dr=None, ee=0, ri=0, me=None, hv=None, s=None)

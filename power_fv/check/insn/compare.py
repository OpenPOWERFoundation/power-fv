from power_fv.insn import const
from power_fv.insn.spec.compare import CompareSpec
from power_fv.check.insn import InsnCheck


__all__ = [
    "CMPI", "CMPLI", "CMP", "CMPL", "CMPRB", "CMPEQB",
]


class CMPI   (InsnCheck, spec_cls=CompareSpec, insn_cls=const.CMPI  ): pass
class CMPLI  (InsnCheck, spec_cls=CompareSpec, insn_cls=const.CMPLI ): pass
class CMP    (InsnCheck, spec_cls=CompareSpec, insn_cls=const.CMP   ): pass
class CMPL   (InsnCheck, spec_cls=CompareSpec, insn_cls=const.CMPL  ): pass
class CMPRB  (InsnCheck, spec_cls=CompareSpec, insn_cls=const.CMPRB ): pass
class CMPEQB (InsnCheck, spec_cls=CompareSpec, insn_cls=const.CMPEQB): pass

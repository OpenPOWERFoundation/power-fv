from power_fv.insn import const
from power_fv.insn.spec.cr import CRSpec
from power_fv.check.insn import InsnCheck


__all__ = [
    "CRAND", "CROR", "CRNAND", "CRXOR", "CRNOR", "CRANDC", "CREQV", "CRORC",
    "MCRF" ,
]


class CRAND  (InsnCheck, spec_cls=CRSpec, insn_cls=const.CRAND ): pass
class CROR   (InsnCheck, spec_cls=CRSpec, insn_cls=const.CROR  ): pass
class CRNAND (InsnCheck, spec_cls=CRSpec, insn_cls=const.CRNAND): pass
class CRXOR  (InsnCheck, spec_cls=CRSpec, insn_cls=const.CRXOR ): pass
class CRNOR  (InsnCheck, spec_cls=CRSpec, insn_cls=const.CRNOR ): pass
class CRANDC (InsnCheck, spec_cls=CRSpec, insn_cls=const.CRANDC): pass
class CREQV  (InsnCheck, spec_cls=CRSpec, insn_cls=const.CREQV ): pass
class CRORC  (InsnCheck, spec_cls=CRSpec, insn_cls=const.CRORC ): pass
class MCRF   (InsnCheck, spec_cls=CRSpec, insn_cls=const.MCRF  ): pass

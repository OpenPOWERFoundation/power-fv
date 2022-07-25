from power_fv.insn import const
from power_fv.insn.spec.cr import CRLogicalSpec, CRMoveSpec
from power_fv.check.insn import InsnCheck


__all__ = [
    "CRAND", "CROR", "CRNAND", "CRXOR", "CRNOR", "CRANDC", "CREQV", "CRORC",
    "MCRF", "MCRXRX", "MTCRF", "MFOCRF", "MFCR",
    "SETB", "SETBC", "SETBCR", "SETNBC", "SETNBCR",
]


class CRAND  (InsnCheck, spec_cls=CRLogicalSpec, insn_cls=const.CRAND ): pass
class CROR   (InsnCheck, spec_cls=CRLogicalSpec, insn_cls=const.CROR  ): pass
class CRNAND (InsnCheck, spec_cls=CRLogicalSpec, insn_cls=const.CRNAND): pass
class CRXOR  (InsnCheck, spec_cls=CRLogicalSpec, insn_cls=const.CRXOR ): pass
class CRNOR  (InsnCheck, spec_cls=CRLogicalSpec, insn_cls=const.CRNOR ): pass
class CRANDC (InsnCheck, spec_cls=CRLogicalSpec, insn_cls=const.CRANDC): pass
class CREQV  (InsnCheck, spec_cls=CRLogicalSpec, insn_cls=const.CREQV ): pass
class CRORC  (InsnCheck, spec_cls=CRLogicalSpec, insn_cls=const.CRORC ): pass

class MCRF   (InsnCheck, spec_cls=CRMoveSpec, insn_cls=const.MCRF  ): pass
class MCRXRX (InsnCheck, spec_cls=CRMoveSpec, insn_cls=const.MCRXRX): pass
class MTOCRF (InsnCheck, spec_cls=CRMoveSpec, insn_cls=const.MTOCRF): pass
class MTCRF  (InsnCheck, spec_cls=CRMoveSpec, insn_cls=const.MTCRF ): pass
class MFOCRF (InsnCheck, spec_cls=CRMoveSpec, insn_cls=const.MFOCRF): pass
class MFCR   (InsnCheck, spec_cls=CRMoveSpec, insn_cls=const.MFCR  ): pass

class SETB   (InsnCheck, spec_cls=CRMoveSpec, insn_cls=const.SETB   ): pass
class SETBC  (InsnCheck, spec_cls=CRMoveSpec, insn_cls=const.SETBC  ): pass
class SETBCR (InsnCheck, spec_cls=CRMoveSpec, insn_cls=const.SETBCR ): pass
class SETNBC (InsnCheck, spec_cls=CRMoveSpec, insn_cls=const.SETNBC ): pass
class SETNBCR(InsnCheck, spec_cls=CRMoveSpec, insn_cls=const.SETNBCR): pass

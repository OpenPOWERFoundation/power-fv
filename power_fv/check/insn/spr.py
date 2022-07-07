from power_fv.insn import const
from power_fv.insn.spec.spr import SPRMoveSpec
from power_fv.check.insn import InsnCheck


__all__ = [
    "MTXER" , "MFXER" ,
    "MTLR"  , "MFLR"  ,
    "MTCTR" , "MFCTR" ,
    "MTSRR0", "MFSRR0",
    "MTSRR1", "MFSRR1",
    "MTTAR" , "MFTAR" ,
]


class MTXER (InsnCheck, spec_cls=SPRMoveSpec, insn_cls=const.MTXER ): pass
class MFXER (InsnCheck, spec_cls=SPRMoveSpec, insn_cls=const.MFXER ): pass
class MTLR  (InsnCheck, spec_cls=SPRMoveSpec, insn_cls=const.MTLR  ): pass
class MFLR  (InsnCheck, spec_cls=SPRMoveSpec, insn_cls=const.MFLR  ): pass
class MTCTR (InsnCheck, spec_cls=SPRMoveSpec, insn_cls=const.MTCTR ): pass
class MFCTR (InsnCheck, spec_cls=SPRMoveSpec, insn_cls=const.MFCTR ): pass
class MTSRR0(InsnCheck, spec_cls=SPRMoveSpec, insn_cls=const.MTSRR0): pass
class MFSRR0(InsnCheck, spec_cls=SPRMoveSpec, insn_cls=const.MFSRR0): pass
class MTSRR1(InsnCheck, spec_cls=SPRMoveSpec, insn_cls=const.MTSRR1): pass
class MFSRR1(InsnCheck, spec_cls=SPRMoveSpec, insn_cls=const.MFSRR1): pass
class MTTAR (InsnCheck, spec_cls=SPRMoveSpec, insn_cls=const.MTTAR ): pass
class MFTAR (InsnCheck, spec_cls=SPRMoveSpec, insn_cls=const.MFTAR ): pass

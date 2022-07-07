from power_fv.insn import const
from power_fv.insn.spec.branch import BranchSpec
from power_fv.check.insn import InsnCheck


__all__ = [
    "B" , "BA" , "BL" , "BLA" ,
    "BC", "BCA", "BCL", "BCLA",
    "BCLR" , "BCLRL" ,
    "BCCTR", "BCCTRL",
    "BCTAR", "BCTARL",
]


class B     (InsnCheck, spec_cls=BranchSpec, insn_cls=const.B   ): pass
class BA    (InsnCheck, spec_cls=BranchSpec, insn_cls=const.BA  ): pass
class BL    (InsnCheck, spec_cls=BranchSpec, insn_cls=const.BL  ): pass
class BLA   (InsnCheck, spec_cls=BranchSpec, insn_cls=const.BLA ): pass

class BC    (InsnCheck, spec_cls=BranchSpec, insn_cls=const.BC  ): pass
class BCA   (InsnCheck, spec_cls=BranchSpec, insn_cls=const.BCA ): pass
class BCL   (InsnCheck, spec_cls=BranchSpec, insn_cls=const.BCL ): pass
class BCLA  (InsnCheck, spec_cls=BranchSpec, insn_cls=const.BCLA): pass

class BCLR  (InsnCheck, spec_cls=BranchSpec, insn_cls=const.BCLR  ): pass
class BCLRL (InsnCheck, spec_cls=BranchSpec, insn_cls=const.BCLRL ): pass
class BCCTR (InsnCheck, spec_cls=BranchSpec, insn_cls=const.BCCTR ): pass
class BCCTRL(InsnCheck, spec_cls=BranchSpec, insn_cls=const.BCCTRL): pass
class BCTAR (InsnCheck, spec_cls=BranchSpec, insn_cls=const.BCTAR ): pass
class BCTARL(InsnCheck, spec_cls=BranchSpec, insn_cls=const.BCTARL): pass

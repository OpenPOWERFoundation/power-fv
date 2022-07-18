from power_fv.insn import const
from power_fv.insn.spec.rotate import RotateShiftSpec
from power_fv.check.insn import InsnCheck


__all__ = [
    "RLWINM", "RLWINM_", "RLWNM", "RLWNM_", "RLWIMI", "RLWIMI_",
    "SLW"   , "SLW_"   ,
    "SRW"   , "SRW_"   , "SRAWI", "SRAWI_", "SRAW"  , "SRAW_"  ,
]


class RLWINM (InsnCheck, spec_cls=RotateShiftSpec, insn_cls=const.RLWINM ): pass
class RLWINM_(InsnCheck, spec_cls=RotateShiftSpec, insn_cls=const.RLWINM_): pass
class RLWNM  (InsnCheck, spec_cls=RotateShiftSpec, insn_cls=const.RLWNM  ): pass
class RLWNM_ (InsnCheck, spec_cls=RotateShiftSpec, insn_cls=const.RLWNM_ ): pass
class RLWIMI (InsnCheck, spec_cls=RotateShiftSpec, insn_cls=const.RLWIMI ): pass
class RLWIMI_(InsnCheck, spec_cls=RotateShiftSpec, insn_cls=const.RLWIMI_): pass
class SLW    (InsnCheck, spec_cls=RotateShiftSpec, insn_cls=const.SLW    ): pass
class SLW_   (InsnCheck, spec_cls=RotateShiftSpec, insn_cls=const.SLW_   ): pass
class SRW    (InsnCheck, spec_cls=RotateShiftSpec, insn_cls=const.SRW    ): pass
class SRW_   (InsnCheck, spec_cls=RotateShiftSpec, insn_cls=const.SRW_   ): pass
class SRAWI  (InsnCheck, spec_cls=RotateShiftSpec, insn_cls=const.SRAWI  ): pass
class SRAWI_ (InsnCheck, spec_cls=RotateShiftSpec, insn_cls=const.SRAWI_ ): pass
class SRAW   (InsnCheck, spec_cls=RotateShiftSpec, insn_cls=const.SRAW   ): pass
class SRAW_  (InsnCheck, spec_cls=RotateShiftSpec, insn_cls=const.SRAW_  ): pass

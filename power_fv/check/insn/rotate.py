from power_fv.insn import const
from power_fv.insn.spec.rotate import RotateShiftSpec
from power_fv.check.insn import InsnCheck


__all__ = [
    "RLWINM", "RLWINM_", "RLWNM" , "RLWNM_" , "RLWIMI", "RLWIMI_",
    "RLDICL", "RLDICL_", "RLDICR", "RLDICR_", "RLDIC" , "RLDIC_" ,
    "RLDCL" , "RLDCL_" , "RLDCR" , "RLDCR_" , "RLDIMI", "RLDIMI_",
    "SLW"   , "SLW_"   , "SLD"   , "SLD_"   ,
    "SRW"   , "SRW_"   , "SRAWI" , "SRAWI_" , "SRAW"  , "SRAW_"  ,
    "SRD"   , "SRD_"   , "SRADI" , "SRADI_" , "SRAD"  , "SRAD_"  ,
]


class RLWINM (InsnCheck, spec_cls=RotateShiftSpec, insn_cls=const.RLWINM ): pass
class RLWINM_(InsnCheck, spec_cls=RotateShiftSpec, insn_cls=const.RLWINM_): pass
class RLWNM  (InsnCheck, spec_cls=RotateShiftSpec, insn_cls=const.RLWNM  ): pass
class RLWNM_ (InsnCheck, spec_cls=RotateShiftSpec, insn_cls=const.RLWNM_ ): pass
class RLWIMI (InsnCheck, spec_cls=RotateShiftSpec, insn_cls=const.RLWIMI ): pass
class RLWIMI_(InsnCheck, spec_cls=RotateShiftSpec, insn_cls=const.RLWIMI_): pass
class RLDICL (InsnCheck, spec_cls=RotateShiftSpec, insn_cls=const.RLDICL ): pass
class RLDICL_(InsnCheck, spec_cls=RotateShiftSpec, insn_cls=const.RLDICL_): pass
class RLDICR (InsnCheck, spec_cls=RotateShiftSpec, insn_cls=const.RLDICR ): pass
class RLDICR_(InsnCheck, spec_cls=RotateShiftSpec, insn_cls=const.RLDICR_): pass
class RLDIC  (InsnCheck, spec_cls=RotateShiftSpec, insn_cls=const.RLDIC  ): pass
class RLDIC_ (InsnCheck, spec_cls=RotateShiftSpec, insn_cls=const.RLDIC_ ): pass
class RLDCL  (InsnCheck, spec_cls=RotateShiftSpec, insn_cls=const.RLDCL  ): pass
class RLDCL_ (InsnCheck, spec_cls=RotateShiftSpec, insn_cls=const.RLDCL_ ): pass
class RLDCR  (InsnCheck, spec_cls=RotateShiftSpec, insn_cls=const.RLDCR  ): pass
class RLDCR_ (InsnCheck, spec_cls=RotateShiftSpec, insn_cls=const.RLDCR_ ): pass
class RLDIMI (InsnCheck, spec_cls=RotateShiftSpec, insn_cls=const.RLDIMI ): pass
class RLDIMI_(InsnCheck, spec_cls=RotateShiftSpec, insn_cls=const.RLDIMI_): pass
class SLW    (InsnCheck, spec_cls=RotateShiftSpec, insn_cls=const.SLW    ): pass
class SLW_   (InsnCheck, spec_cls=RotateShiftSpec, insn_cls=const.SLW_   ): pass
class SLD    (InsnCheck, spec_cls=RotateShiftSpec, insn_cls=const.SLD    ): pass
class SLD_   (InsnCheck, spec_cls=RotateShiftSpec, insn_cls=const.SLD_   ): pass
class SRW    (InsnCheck, spec_cls=RotateShiftSpec, insn_cls=const.SRW    ): pass
class SRW_   (InsnCheck, spec_cls=RotateShiftSpec, insn_cls=const.SRW_   ): pass
class SRAWI  (InsnCheck, spec_cls=RotateShiftSpec, insn_cls=const.SRAWI  ): pass
class SRAWI_ (InsnCheck, spec_cls=RotateShiftSpec, insn_cls=const.SRAWI_ ): pass
class SRAW   (InsnCheck, spec_cls=RotateShiftSpec, insn_cls=const.SRAW   ): pass
class SRAW_  (InsnCheck, spec_cls=RotateShiftSpec, insn_cls=const.SRAW_  ): pass
class SRD    (InsnCheck, spec_cls=RotateShiftSpec, insn_cls=const.SRD    ): pass
class SRD_   (InsnCheck, spec_cls=RotateShiftSpec, insn_cls=const.SRD_   ): pass
class SRADI  (InsnCheck, spec_cls=RotateShiftSpec, insn_cls=const.SRADI  ): pass
class SRADI_ (InsnCheck, spec_cls=RotateShiftSpec, insn_cls=const.SRADI_ ): pass
class SRAD   (InsnCheck, spec_cls=RotateShiftSpec, insn_cls=const.SRAD   ): pass
class SRAD_  (InsnCheck, spec_cls=RotateShiftSpec, insn_cls=const.SRAD_  ): pass

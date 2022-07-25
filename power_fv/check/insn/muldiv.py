from power_fv.insn import const
from power_fv.insn.spec.muldiv import MultiplySpec, DivideSpec
from power_fv.check.insn import InsnCheck


__all__ = [
    "MULLI" ,
    "MULLW" , "MULLW_" , "MULLWO" , "MULLWO_" ,
    "MULHW" , "MULHW_" , "MULHWU" , "MULHWU_" ,
    "DIVW"  , "DIVW_"  , "DIVWO"  , "DIVWO_"  ,
    "DIVWU" , "DIVWU_" , "DIVWUO" , "DIVWUO_" ,
    "DIVWE" , "DIVWE_" , "DIVWEO" , "DIVWEO_" ,
    "DIVWEU", "DIVWEU_", "DIVWEUO", "DIVWEUO_",
    "MODSW" , "MODUW"  ,
]


class MULLI   (InsnCheck, spec_cls=MultiplySpec, insn_cls=const.MULLI  ): pass
class MULLW   (InsnCheck, spec_cls=MultiplySpec, insn_cls=const.MULLW  ): pass
class MULLW_  (InsnCheck, spec_cls=MultiplySpec, insn_cls=const.MULLW_ ): pass
class MULLWO  (InsnCheck, spec_cls=MultiplySpec, insn_cls=const.MULLWO ): pass
class MULLWO_ (InsnCheck, spec_cls=MultiplySpec, insn_cls=const.MULLWO_): pass
class MULHW   (InsnCheck, spec_cls=MultiplySpec, insn_cls=const.MULHW  ): pass
class MULHW_  (InsnCheck, spec_cls=MultiplySpec, insn_cls=const.MULHW_ ): pass
class MULHWU  (InsnCheck, spec_cls=MultiplySpec, insn_cls=const.MULHWU ): pass
class MULHWU_ (InsnCheck, spec_cls=MultiplySpec, insn_cls=const.MULHWU_): pass

class DIVW    (InsnCheck, spec_cls=DivideSpec, insn_cls=const.DIVW    ): pass
class DIVW_   (InsnCheck, spec_cls=DivideSpec, insn_cls=const.DIVW_   ): pass
class DIVWO   (InsnCheck, spec_cls=DivideSpec, insn_cls=const.DIVWO   ): pass
class DIVWO_  (InsnCheck, spec_cls=DivideSpec, insn_cls=const.DIVWO_  ): pass
class DIVWU   (InsnCheck, spec_cls=DivideSpec, insn_cls=const.DIVWU   ): pass
class DIVWU_  (InsnCheck, spec_cls=DivideSpec, insn_cls=const.DIVWU_  ): pass
class DIVWUO  (InsnCheck, spec_cls=DivideSpec, insn_cls=const.DIVWUO  ): pass
class DIVWUO_ (InsnCheck, spec_cls=DivideSpec, insn_cls=const.DIVWUO_ ): pass
class DIVWE   (InsnCheck, spec_cls=DivideSpec, insn_cls=const.DIVWE   ): pass
class DIVWE_  (InsnCheck, spec_cls=DivideSpec, insn_cls=const.DIVWE_  ): pass
class DIVWEO  (InsnCheck, spec_cls=DivideSpec, insn_cls=const.DIVWEO  ): pass
class DIVWEO_ (InsnCheck, spec_cls=DivideSpec, insn_cls=const.DIVWEO_ ): pass
class DIVWEU  (InsnCheck, spec_cls=DivideSpec, insn_cls=const.DIVWEU  ): pass
class DIVWEU_ (InsnCheck, spec_cls=DivideSpec, insn_cls=const.DIVWEU_ ): pass
class DIVWEUO (InsnCheck, spec_cls=DivideSpec, insn_cls=const.DIVWEUO ): pass
class DIVWEUO_(InsnCheck, spec_cls=DivideSpec, insn_cls=const.DIVWEUO_): pass

class MODSW   (InsnCheck, spec_cls=DivideSpec, insn_cls=const.MODSW): pass
class MODUW   (InsnCheck, spec_cls=DivideSpec, insn_cls=const.MODUW): pass

from power_fv.insn import const
from power_fv.insn.spec.addsub import AddSubSpec
from power_fv.check.insn import InsnCheck


__all__ = [
    "ADDI"  , "ADDIS"  , "ADDPCIS",
    "ADD"   , "ADD_"   , "ADDO"   , "ADDO_"   , "ADDIC" , "ADDIC_",
    "SUBF"  , "SUBF_"  , "SUBFO"  , "SUBFO_"  , "SUBFIC",
    "ADDC"  , "ADDC_"  , "ADDCO"  , "ADDCO_"  ,
    "ADDE"  , "ADDE_"  , "ADDEO"  , "ADDEO_"  ,
    "SUBFC" , "SUBFC_" , "SUBFCO" , "SUBFCO_" ,
    "SUBFE" , "SUBFE_" , "SUBFEO" , "SUBFEO_" ,
    "ADDME" , "ADDME_" , "ADDMEO" , "ADDMEO_" ,
    "ADDZE" , "ADDZE_" , "ADDZEO" , "ADDZEO_" ,
    "SUBFME", "SUBFME_", "SUBFMEO", "SUBFMEO_",
    "SUBFZE", "SUBFZE_", "SUBFZEO", "SUBFZEO_",
    "ADDEX" ,
    "NEG"   , "NEG_"   , "NEGO"   , "NEGO_"   ,
]


class ADDI    (InsnCheck, spec_cls=AddSubSpec, insn_cls=const.ADDI    ): pass
class ADDIS   (InsnCheck, spec_cls=AddSubSpec, insn_cls=const.ADDIS   ): pass
class ADDPCIS (InsnCheck, spec_cls=AddSubSpec, insn_cls=const.ADDPCIS ): pass
class ADD     (InsnCheck, spec_cls=AddSubSpec, insn_cls=const.ADD     ): pass
class ADD_    (InsnCheck, spec_cls=AddSubSpec, insn_cls=const.ADD_    ): pass
class ADDO    (InsnCheck, spec_cls=AddSubSpec, insn_cls=const.ADDO    ): pass
class ADDO_   (InsnCheck, spec_cls=AddSubSpec, insn_cls=const.ADDO_   ): pass
class ADDIC   (InsnCheck, spec_cls=AddSubSpec, insn_cls=const.ADDIC   ): pass
class ADDIC_  (InsnCheck, spec_cls=AddSubSpec, insn_cls=const.ADDIC_  ): pass
class SUBF    (InsnCheck, spec_cls=AddSubSpec, insn_cls=const.SUBF    ): pass
class SUBF_   (InsnCheck, spec_cls=AddSubSpec, insn_cls=const.SUBF_   ): pass
class SUBFO   (InsnCheck, spec_cls=AddSubSpec, insn_cls=const.SUBFO   ): pass
class SUBFO_  (InsnCheck, spec_cls=AddSubSpec, insn_cls=const.SUBFO_  ): pass
class SUBFIC  (InsnCheck, spec_cls=AddSubSpec, insn_cls=const.SUBFIC  ): pass
class ADDC    (InsnCheck, spec_cls=AddSubSpec, insn_cls=const.ADDC    ): pass
class ADDC_   (InsnCheck, spec_cls=AddSubSpec, insn_cls=const.ADDC_   ): pass
class ADDCO   (InsnCheck, spec_cls=AddSubSpec, insn_cls=const.ADDCO   ): pass
class ADDCO_  (InsnCheck, spec_cls=AddSubSpec, insn_cls=const.ADDCO_  ): pass
class ADDE    (InsnCheck, spec_cls=AddSubSpec, insn_cls=const.ADDE    ): pass
class ADDE_   (InsnCheck, spec_cls=AddSubSpec, insn_cls=const.ADDE_   ): pass
class ADDEO   (InsnCheck, spec_cls=AddSubSpec, insn_cls=const.ADDEO   ): pass
class ADDEO_  (InsnCheck, spec_cls=AddSubSpec, insn_cls=const.ADDEO_  ): pass
class SUBFC   (InsnCheck, spec_cls=AddSubSpec, insn_cls=const.SUBFC   ): pass
class SUBFC_  (InsnCheck, spec_cls=AddSubSpec, insn_cls=const.SUBFC_  ): pass
class SUBFCO  (InsnCheck, spec_cls=AddSubSpec, insn_cls=const.SUBFCO  ): pass
class SUBFCO_ (InsnCheck, spec_cls=AddSubSpec, insn_cls=const.SUBFCO_ ): pass
class SUBFE   (InsnCheck, spec_cls=AddSubSpec, insn_cls=const.SUBFE   ): pass
class SUBFE_  (InsnCheck, spec_cls=AddSubSpec, insn_cls=const.SUBFE_  ): pass
class SUBFEO  (InsnCheck, spec_cls=AddSubSpec, insn_cls=const.SUBFEO  ): pass
class SUBFEO_ (InsnCheck, spec_cls=AddSubSpec, insn_cls=const.SUBFEO_ ): pass
class ADDME   (InsnCheck, spec_cls=AddSubSpec, insn_cls=const.ADDME   ): pass
class ADDME_  (InsnCheck, spec_cls=AddSubSpec, insn_cls=const.ADDME_  ): pass
class ADDMEO  (InsnCheck, spec_cls=AddSubSpec, insn_cls=const.ADDMEO  ): pass
class ADDMEO_ (InsnCheck, spec_cls=AddSubSpec, insn_cls=const.ADDMEO_ ): pass
class ADDZE   (InsnCheck, spec_cls=AddSubSpec, insn_cls=const.ADDZE   ): pass
class ADDZE_  (InsnCheck, spec_cls=AddSubSpec, insn_cls=const.ADDZE_  ): pass
class ADDZEO  (InsnCheck, spec_cls=AddSubSpec, insn_cls=const.ADDZEO  ): pass
class ADDZEO_ (InsnCheck, spec_cls=AddSubSpec, insn_cls=const.ADDZEO_ ): pass
class SUBFME  (InsnCheck, spec_cls=AddSubSpec, insn_cls=const.SUBFME  ): pass
class SUBFME_ (InsnCheck, spec_cls=AddSubSpec, insn_cls=const.SUBFME_ ): pass
class SUBFMEO (InsnCheck, spec_cls=AddSubSpec, insn_cls=const.SUBFMEO ): pass
class SUBFMEO_(InsnCheck, spec_cls=AddSubSpec, insn_cls=const.SUBFMEO_): pass
class SUBFZE  (InsnCheck, spec_cls=AddSubSpec, insn_cls=const.SUBFZE  ): pass
class SUBFZE_ (InsnCheck, spec_cls=AddSubSpec, insn_cls=const.SUBFZE_ ): pass
class SUBFZEO (InsnCheck, spec_cls=AddSubSpec, insn_cls=const.SUBFZEO ): pass
class SUBFZEO_(InsnCheck, spec_cls=AddSubSpec, insn_cls=const.SUBFZEO_): pass
class ADDEX   (InsnCheck, spec_cls=AddSubSpec, insn_cls=const.ADDEX   ): pass
class NEG     (InsnCheck, spec_cls=AddSubSpec, insn_cls=const.NEG     ): pass
class NEG_    (InsnCheck, spec_cls=AddSubSpec, insn_cls=const.NEG_    ): pass
class NEGO    (InsnCheck, spec_cls=AddSubSpec, insn_cls=const.NEGO    ): pass
class NEGO_   (InsnCheck, spec_cls=AddSubSpec, insn_cls=const.NEGO_   ): pass

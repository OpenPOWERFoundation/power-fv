from power_fv.insn import const
from power_fv.insn.spec.logical import LogicalSpec
from power_fv.check.insn import InsnCheck


__all__ = [
    "ANDI_"  , "ANDIS_" , "ORI"   , "ORIS"   , "XORI", "XORIS",
    "AND"    , "AND_"   , "XOR"   , "XOR_"   , "NAND", "NAND_",
    "OR"     , "OR_"    , "ORC"   , "ORC_"   , "NOR" , "NOR_" ,
    "EQV"    , "EQV_"   , "ANDC"  , "ANDC_"  ,
    "EXTSB"  , "EXTSB_" , "EXTSH" , "EXTSH_" ,
    "CMPB"   ,
    "CNTLZW" , "CNTLZW_", "CNTTZW", "CNTTZW_",
    "POPCNTB", "POPCNTW",
    "PRTYW"  ,
]


class ANDI_  (InsnCheck, spec_cls=LogicalSpec, insn_cls=const.ANDI_  ): pass
class ANDIS_ (InsnCheck, spec_cls=LogicalSpec, insn_cls=const.ANDIS_ ): pass
class ORI    (InsnCheck, spec_cls=LogicalSpec, insn_cls=const.ORI    ): pass
class ORIS   (InsnCheck, spec_cls=LogicalSpec, insn_cls=const.ORIS   ): pass
class XORI   (InsnCheck, spec_cls=LogicalSpec, insn_cls=const.XORI   ): pass
class XORIS  (InsnCheck, spec_cls=LogicalSpec, insn_cls=const.XORIS  ): pass
class AND    (InsnCheck, spec_cls=LogicalSpec, insn_cls=const.AND    ): pass
class AND_   (InsnCheck, spec_cls=LogicalSpec, insn_cls=const.AND_   ): pass
class XOR    (InsnCheck, spec_cls=LogicalSpec, insn_cls=const.XOR    ): pass
class XOR_   (InsnCheck, spec_cls=LogicalSpec, insn_cls=const.XOR_   ): pass
class NAND   (InsnCheck, spec_cls=LogicalSpec, insn_cls=const.NAND   ): pass
class NAND_  (InsnCheck, spec_cls=LogicalSpec, insn_cls=const.NAND_  ): pass
class OR     (InsnCheck, spec_cls=LogicalSpec, insn_cls=const.OR     ): pass
class OR_    (InsnCheck, spec_cls=LogicalSpec, insn_cls=const.OR_    ): pass
class ORC    (InsnCheck, spec_cls=LogicalSpec, insn_cls=const.ORC    ): pass
class ORC_   (InsnCheck, spec_cls=LogicalSpec, insn_cls=const.ORC_   ): pass
class NOR    (InsnCheck, spec_cls=LogicalSpec, insn_cls=const.NOR    ): pass
class NOR_   (InsnCheck, spec_cls=LogicalSpec, insn_cls=const.NOR_   ): pass
class EQV    (InsnCheck, spec_cls=LogicalSpec, insn_cls=const.EQV    ): pass
class EQV_   (InsnCheck, spec_cls=LogicalSpec, insn_cls=const.EQV_   ): pass
class ANDC   (InsnCheck, spec_cls=LogicalSpec, insn_cls=const.ANDC   ): pass
class ANDC_  (InsnCheck, spec_cls=LogicalSpec, insn_cls=const.ANDC_  ): pass

class EXTSB  (InsnCheck, spec_cls=LogicalSpec, insn_cls=const.EXTSB  ): pass
class EXTSB_ (InsnCheck, spec_cls=LogicalSpec, insn_cls=const.EXTSB_ ): pass
class EXTSH  (InsnCheck, spec_cls=LogicalSpec, insn_cls=const.EXTSH  ): pass
class EXTSH_ (InsnCheck, spec_cls=LogicalSpec, insn_cls=const.EXTSH_ ): pass
class CMPB   (InsnCheck, spec_cls=LogicalSpec, insn_cls=const.CMPB   ): pass
class CNTLZW (InsnCheck, spec_cls=LogicalSpec, insn_cls=const.CNTLZW ): pass
class CNTLZW_(InsnCheck, spec_cls=LogicalSpec, insn_cls=const.CNTLZW_): pass
class CNTTZW (InsnCheck, spec_cls=LogicalSpec, insn_cls=const.CNTTZW ): pass
class CNTTZW_(InsnCheck, spec_cls=LogicalSpec, insn_cls=const.CNTTZW_): pass
class POPCNTB(InsnCheck, spec_cls=LogicalSpec, insn_cls=const.POPCNTB): pass
class POPCNTW(InsnCheck, spec_cls=LogicalSpec, insn_cls=const.POPCNTW): pass
class PRTYW  (InsnCheck, spec_cls=LogicalSpec, insn_cls=const.PRTYW  ): pass

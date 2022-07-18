from power_fv.insn import const
from power_fv.insn.spec.bcd import BCDAssistSpec
from power_fv.check.insn import InsnCheck


__all__ = ["CDTBCD", "CBCDTD", "ADDG6S"]


class CDTBCD (InsnCheck, spec_cls=BCDAssistSpec, insn_cls=const.CDTBCD): pass
class CBCDTD (InsnCheck, spec_cls=BCDAssistSpec, insn_cls=const.CBCDTD): pass
class ADDG6S (InsnCheck, spec_cls=BCDAssistSpec, insn_cls=const.ADDG6S): pass

from power_fv.insn import const
from power_fv.insn.spec.msr import MSRMoveSpec
from power_fv.check.insn import InsnCheck


__all__ = [
    "MTMSR", "MFMSR",
]


class MTMSR(InsnCheck, spec_cls=MSRMoveSpec, insn_cls=const.MTMSR): pass
class MFMSR(InsnCheck, spec_cls=MSRMoveSpec, insn_cls=const.MFMSR): pass

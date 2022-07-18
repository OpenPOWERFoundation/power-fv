from power_fv.insn import const
from power_fv.insn.spec.syscall import SystemCallSpec
from power_fv.check.insn import InsnCheck


__all__ = ["SC"]


class SC(InsnCheck, spec_cls=SystemCallSpec, insn_cls=const.SC): pass

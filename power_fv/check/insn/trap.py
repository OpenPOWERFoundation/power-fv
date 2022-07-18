from power_fv.insn import const
from power_fv.insn.spec.trap import TrapSpec
from power_fv.check.insn import InsnCheck


__all__ = ["TWI", "TW"]


class TWI(InsnCheck, spec_cls=TrapSpec, insn_cls=const.TWI): pass
class TW (InsnCheck, spec_cls=TrapSpec, insn_cls=const.TW ): pass

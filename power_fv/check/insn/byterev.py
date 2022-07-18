from power_fv.insn import const
from power_fv.insn.spec.byterev import ByteReverseSpec
from power_fv.check.insn import InsnCheck


__all__ = ["BRH", "BRW"]


class BRH(InsnCheck, spec_cls=ByteReverseSpec, insn_cls=const.BRH): pass
class BRW(InsnCheck, spec_cls=ByteReverseSpec, insn_cls=const.BRW): pass

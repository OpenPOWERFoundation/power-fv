from power_fv.insn import const
from power_fv.insn.spec.loadstore import LoadStoreSpec
from power_fv.check.insn import InsnCheck


__all__ = [
    "LBZ", "LBZX", "LBZU", "LBZUX",
    "LHZ", "LHZX", "LHZU", "LHZUX", "LHA", "LHAX", "LHAU", "LHAUX",
    "LWZ", "LWZU", "LWZX", "LWZUX",
    "STB", "STBX", "STBU", "STBUX",
    "STH", "STHU", "STHX", "STHUX",
    "STW", "STWX", "STWX", "STWUX",
    "LWBRX", "STHBRX", "STWBRX",
]


class LBZ   (InsnCheck, spec_cls=LoadStoreSpec, insn_cls=const.LBZ  ): pass
class LBZX  (InsnCheck, spec_cls=LoadStoreSpec, insn_cls=const.LBZX ): pass
class LBZU  (InsnCheck, spec_cls=LoadStoreSpec, insn_cls=const.LBZU ): pass
class LBZUX (InsnCheck, spec_cls=LoadStoreSpec, insn_cls=const.LBZUX): pass
class LHZ   (InsnCheck, spec_cls=LoadStoreSpec, insn_cls=const.LHZ  ): pass
class LHZX  (InsnCheck, spec_cls=LoadStoreSpec, insn_cls=const.LHZX ): pass
class LHZU  (InsnCheck, spec_cls=LoadStoreSpec, insn_cls=const.LHZU ): pass
class LHZUX (InsnCheck, spec_cls=LoadStoreSpec, insn_cls=const.LHZUX): pass
class LHA   (InsnCheck, spec_cls=LoadStoreSpec, insn_cls=const.LHA  ): pass
class LHAX  (InsnCheck, spec_cls=LoadStoreSpec, insn_cls=const.LHAX ): pass
class LHAU  (InsnCheck, spec_cls=LoadStoreSpec, insn_cls=const.LHAU ): pass
class LHAUX (InsnCheck, spec_cls=LoadStoreSpec, insn_cls=const.LHAUX): pass
class LWZ   (InsnCheck, spec_cls=LoadStoreSpec, insn_cls=const.LWZ  ): pass
class LWZX  (InsnCheck, spec_cls=LoadStoreSpec, insn_cls=const.LWZX ): pass
class LWZU  (InsnCheck, spec_cls=LoadStoreSpec, insn_cls=const.LWZU ): pass
class LWZUX (InsnCheck, spec_cls=LoadStoreSpec, insn_cls=const.LWZUX): pass

class STB   (InsnCheck, spec_cls=LoadStoreSpec, insn_cls=const.STB  ): pass
class STBX  (InsnCheck, spec_cls=LoadStoreSpec, insn_cls=const.STBX ): pass
class STBU  (InsnCheck, spec_cls=LoadStoreSpec, insn_cls=const.STBU ): pass
class STBUX (InsnCheck, spec_cls=LoadStoreSpec, insn_cls=const.STBUX): pass
class STH   (InsnCheck, spec_cls=LoadStoreSpec, insn_cls=const.STH  ): pass
class STHX  (InsnCheck, spec_cls=LoadStoreSpec, insn_cls=const.STHX ): pass
class STHU  (InsnCheck, spec_cls=LoadStoreSpec, insn_cls=const.STHU ): pass
class STHUX (InsnCheck, spec_cls=LoadStoreSpec, insn_cls=const.STHUX): pass
class STW   (InsnCheck, spec_cls=LoadStoreSpec, insn_cls=const.STW  ): pass
class STWX  (InsnCheck, spec_cls=LoadStoreSpec, insn_cls=const.STWX ): pass
class STWU  (InsnCheck, spec_cls=LoadStoreSpec, insn_cls=const.STWU ): pass
class STWUX (InsnCheck, spec_cls=LoadStoreSpec, insn_cls=const.STWUX): pass

class LWBRX (InsnCheck, spec_cls=LoadStoreSpec, insn_cls=const.LWBRX ): pass
class STHBRX(InsnCheck, spec_cls=LoadStoreSpec, insn_cls=const.STHBRX): pass
class STWBRX(InsnCheck, spec_cls=LoadStoreSpec, insn_cls=const.STWBRX): pass

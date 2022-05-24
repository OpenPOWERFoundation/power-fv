from . import _insn
from ._branch import BranchCheck

# Branches

class B      (BranchCheck, name="insn_b",      insn_cls=_insn.B,    ): pass
class BA     (BranchCheck, name="insn_ba",     insn_cls=_insn.BA    ): pass
class BL     (BranchCheck, name="insn_bl",     insn_cls=_insn.BL    ): pass
class BLA    (BranchCheck, name="insn_bla",    insn_cls=_insn.BLA   ): pass

class BC     (BranchCheck, name="insn_bc",     insn_cls=_insn.BC    ): pass
class BCA    (BranchCheck, name="insn_bca",    insn_cls=_insn.BCA   ): pass
class BCL    (BranchCheck, name="insn_bcl",    insn_cls=_insn.BCL   ): pass
class BCLA   (BranchCheck, name="insn_bcla",   insn_cls=_insn.BCLA  ): pass

class BCLR   (BranchCheck, name="insn_bclr",   insn_cls=_insn.BCLR  ): pass
class BCLRL  (BranchCheck, name="insn_bclrl",  insn_cls=_insn.BCLRL ): pass
class BCCTR  (BranchCheck, name="insn_bcctr",  insn_cls=_insn.BCCTR ): pass
class BCCTRL (BranchCheck, name="insn_bcctrl", insn_cls=_insn.BCCTRL): pass
class BCTAR  (BranchCheck, name="insn_bctar",  insn_cls=_insn.BCTAR ): pass
class BCTARL (BranchCheck, name="insn_bctarl", insn_cls=_insn.BCTARL): pass

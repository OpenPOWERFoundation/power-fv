from . import _insn
from ._branch import BranchCheck
from ._cr import CRCheck
from ._compare import CompareCheck
from ._spr import SPRMoveCheck


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

# CR

class CRAND  (CRCheck, name="insn_crand",  insn_cls=_insn.CRAND ): pass
class CROR   (CRCheck, name="insn_cror",   insn_cls=_insn.CROR  ): pass
class CRNAND (CRCheck, name="insn_crnand", insn_cls=_insn.CRNAND): pass
class CRXOR  (CRCheck, name="insn_crxor",  insn_cls=_insn.CRXOR ): pass
class CRNOR  (CRCheck, name="insn_crnor",  insn_cls=_insn.CRNOR ): pass
class CRANDC (CRCheck, name="insn_crandc", insn_cls=_insn.CRANDC): pass
class CREQV  (CRCheck, name="insn_creqv",  insn_cls=_insn.CREQV ): pass
class CRORC  (CRCheck, name="insn_crorc",  insn_cls=_insn.CRORC ): pass

class MCRF   (CRCheck, name="insn_mcrf",   insn_cls=_insn.MCRF  ): pass

# Compare

class CMPI   (CompareCheck, name="insn_cmpi",   insn_cls=_insn.CMPI  ): pass
class CMPLI  (CompareCheck, name="insn_cmpli",  insn_cls=_insn.CMPLI ): pass
class CMP    (CompareCheck, name="insn_cmp",    insn_cls=_insn.CMP   ): pass
class CMPL   (CompareCheck, name="insn_cmpl",   insn_cls=_insn.CMPL  ): pass

# Move To/From SPR

class MTSPR (SPRMoveCheck, name="insn_mtspr", insn_cls=_insn.MTSPR): pass
class MFSPR (SPRMoveCheck, name="insn_mfspr", insn_cls=_insn.MFSPR): pass

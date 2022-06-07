from . import _insn
from ._branch import BranchCheck
from ._cr import CRCheck
from ._addsub import AddSubtractCheck
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

# Add / Subtract from

class ADDI     (AddSubtractCheck, name="insn_addi",     insn_cls=_insn.ADDI    ): pass
class ADDIS    (AddSubtractCheck, name="insn_addis",    insn_cls=_insn.ADDIS   ): pass
class ADDPCIS  (AddSubtractCheck, name="insn_addpcis",  insn_cls=_insn.ADDPCIS ): pass
class ADD      (AddSubtractCheck, name="insn_add",      insn_cls=_insn.ADD     ): pass
class ADD_     (AddSubtractCheck, name="insn_add.",     insn_cls=_insn.ADD_    ): pass
class ADDO     (AddSubtractCheck, name="insn_addo",     insn_cls=_insn.ADDO    ): pass
class ADDO_    (AddSubtractCheck, name="insn_addo.",    insn_cls=_insn.ADDO_   ): pass
class ADDIC    (AddSubtractCheck, name="insn_addic",    insn_cls=_insn.ADDIC   ): pass
class ADDIC_   (AddSubtractCheck, name="insn_addic.",   insn_cls=_insn.ADDIC_  ): pass
class SUBF     (AddSubtractCheck, name="insn_subf",     insn_cls=_insn.SUBF    ): pass
class SUBF_    (AddSubtractCheck, name="insn_subf.",    insn_cls=_insn.SUBF_   ): pass
class SUBFO    (AddSubtractCheck, name="insn_subfo",    insn_cls=_insn.SUBFO   ): pass
class SUBFO_   (AddSubtractCheck, name="insn_subfo.",   insn_cls=_insn.SUBFO_  ): pass
class SUBFIC   (AddSubtractCheck, name="insn_subfic",   insn_cls=_insn.SUBFIC  ): pass
class ADDC     (AddSubtractCheck, name="insn_addc",     insn_cls=_insn.ADDC    ): pass
class ADDC_    (AddSubtractCheck, name="insn_addc.",    insn_cls=_insn.ADDC_   ): pass
class ADDCO    (AddSubtractCheck, name="insn_addco",    insn_cls=_insn.ADDCO   ): pass
class ADDCO_   (AddSubtractCheck, name="insn_addco.",   insn_cls=_insn.ADDCO_  ): pass
class ADDE     (AddSubtractCheck, name="insn_adde",     insn_cls=_insn.ADDE    ): pass
class ADDE_    (AddSubtractCheck, name="insn_adde.",    insn_cls=_insn.ADDE_   ): pass
class ADDEO    (AddSubtractCheck, name="insn_addeo",    insn_cls=_insn.ADDEO   ): pass
class ADDEO_   (AddSubtractCheck, name="insn_addeo.",   insn_cls=_insn.ADDEO_  ): pass
class SUBFC    (AddSubtractCheck, name="insn_subfc",    insn_cls=_insn.SUBFC   ): pass
class SUBFC_   (AddSubtractCheck, name="insn_subfc.",   insn_cls=_insn.SUBFC_  ): pass
class SUBFCO   (AddSubtractCheck, name="insn_subfco",   insn_cls=_insn.SUBFCO  ): pass
class SUBFCO_  (AddSubtractCheck, name="insn_subfco.",  insn_cls=_insn.SUBFCO_ ): pass
class SUBFE    (AddSubtractCheck, name="insn_subfe",    insn_cls=_insn.SUBFE   ): pass
class SUBFE_   (AddSubtractCheck, name="insn_subfe.",   insn_cls=_insn.SUBFE_  ): pass
class SUBFEO   (AddSubtractCheck, name="insn_subfeo",   insn_cls=_insn.SUBFEO  ): pass
class SUBFEO_  (AddSubtractCheck, name="insn_subfeo.",  insn_cls=_insn.SUBFEO_ ): pass
class ADDME    (AddSubtractCheck, name="insn_addme",    insn_cls=_insn.ADDME   ): pass
class ADDME_   (AddSubtractCheck, name="insn_addme.",   insn_cls=_insn.ADDME_  ): pass
class ADDMEO   (AddSubtractCheck, name="insn_addmeo",   insn_cls=_insn.ADDMEO  ): pass
class ADDMEO_  (AddSubtractCheck, name="insn_addmeo.",  insn_cls=_insn.ADDMEO_ ): pass
class ADDZE    (AddSubtractCheck, name="insn_addze",    insn_cls=_insn.ADDZE   ): pass
class ADDZE_   (AddSubtractCheck, name="insn_addze.",   insn_cls=_insn.ADDZE_  ): pass
class ADDZEO   (AddSubtractCheck, name="insn_addzeo",   insn_cls=_insn.ADDZEO  ): pass
class ADDZEO_  (AddSubtractCheck, name="insn_addzeo.",  insn_cls=_insn.ADDZEO_ ): pass
class SUBFME   (AddSubtractCheck, name="insn_subfme",   insn_cls=_insn.SUBFME  ): pass
class SUBFME_  (AddSubtractCheck, name="insn_subfme.",  insn_cls=_insn.SUBFME_ ): pass
class SUBFMEO  (AddSubtractCheck, name="insn_subfmeo",  insn_cls=_insn.SUBFMEO ): pass
class SUBFMEO_ (AddSubtractCheck, name="insn_subfmeo.", insn_cls=_insn.SUBFMEO_): pass
class SUBFZE   (AddSubtractCheck, name="insn_subfze",   insn_cls=_insn.SUBFZE  ): pass
class SUBFZE_  (AddSubtractCheck, name="insn_subfze.",  insn_cls=_insn.SUBFZE_ ): pass
class SUBFZEO  (AddSubtractCheck, name="insn_subfzeo",  insn_cls=_insn.SUBFZEO ): pass
class SUBFZEO_ (AddSubtractCheck, name="insn_subfzeo.", insn_cls=_insn.SUBFZEO_): pass
class ADDEX    (AddSubtractCheck, name="insn_addex",    insn_cls=_insn.ADDEX   ): pass
class NEG      (AddSubtractCheck, name="insn_neg",      insn_cls=_insn.NEG     ): pass
class NEG_     (AddSubtractCheck, name="insn_neg.",     insn_cls=_insn.NEG_    ): pass
class NEGO     (AddSubtractCheck, name="insn_nego",     insn_cls=_insn.NEGO    ): pass
class NEGO_    (AddSubtractCheck, name="insn_nego.",    insn_cls=_insn.NEGO_   ): pass

# Compare

class CMPI   (CompareCheck, name="insn_cmpi",   insn_cls=_insn.CMPI  ): pass
class CMPLI  (CompareCheck, name="insn_cmpli",  insn_cls=_insn.CMPLI ): pass
class CMP    (CompareCheck, name="insn_cmp",    insn_cls=_insn.CMP   ): pass
class CMPL   (CompareCheck, name="insn_cmpl",   insn_cls=_insn.CMPL  ): pass

# Move To/From SPR

class MTSPR (SPRMoveCheck, name="insn_mtspr", insn_cls=_insn.MTSPR): pass
class MFSPR (SPRMoveCheck, name="insn_mfspr", insn_cls=_insn.MFSPR): pass

from . import _fmt

# Branches

class B      (_fmt.Instruction_I, po=18, aa=0, lk=0): pass
class BA     (_fmt.Instruction_I, po=18, aa=1, lk=0): pass
class BL     (_fmt.Instruction_I, po=18, aa=0, lk=1): pass
class BLA    (_fmt.Instruction_I, po=18, aa=1, lk=1): pass

class BC     (_fmt.Instruction_B, po=16, aa=0, lk=0): pass
class BCA    (_fmt.Instruction_B, po=16, aa=1, lk=0): pass
class BCL    (_fmt.Instruction_B, po=16, aa=0, lk=1): pass
class BCLA   (_fmt.Instruction_B, po=16, aa=1, lk=1): pass

class BCLR   (_fmt.Instruction_XL_bc, po=19, xo= 16, lk=0): pass
class BCLRL  (_fmt.Instruction_XL_bc, po=19, xo= 16, lk=1): pass
class BCCTR  (_fmt.Instruction_XL_bc, po=19, xo=528, lk=0): pass
class BCCTRL (_fmt.Instruction_XL_bc, po=19, xo=528, lk=1): pass
class BCTAR  (_fmt.Instruction_XL_bc, po=19, xo=560, lk=0): pass
class BCTARL (_fmt.Instruction_XL_bc, po=19, xo=560, lk=1): pass

# CR

class CRAND  (_fmt.Instruction_XL_crl, po=19, xo=257): pass
class CROR   (_fmt.Instruction_XL_crl, po=19, xo=449): pass
class CRNAND (_fmt.Instruction_XL_crl, po=19, xo=225): pass
class CRXOR  (_fmt.Instruction_XL_crl, po=19, xo=193): pass
class CRNOR  (_fmt.Instruction_XL_crl, po=19, xo= 33): pass
class CRANDC (_fmt.Instruction_XL_crl, po=19, xo=129): pass
class CREQV  (_fmt.Instruction_XL_crl, po=19, xo=289): pass
class CRORC  (_fmt.Instruction_XL_crl, po=19, xo=417): pass

class MCRF   (_fmt.Instruction_XL_crf, po=19, xo=0): pass

# Add / Subtract from

class ADDI     (_fmt.Instruction_D_add,   po=14): pass
class ADDIS    (_fmt.Instruction_D_add,   po=15): pass
class ADDPCIS  (_fmt.Instruction_DX,      po=19, xo=  2): pass
class ADD      (_fmt.Instruction_XO,      po=31, xo=266, oe=0, rc=0): pass
class ADD_     (_fmt.Instruction_XO,      po=31, xo=266, oe=0, rc=1): pass
class ADDO     (_fmt.Instruction_XO,      po=31, xo=266, oe=1, rc=0): pass
class ADDO_    (_fmt.Instruction_XO,      po=31, xo=266, oe=1, rc=1): pass
class ADDIC    (_fmt.Instruction_D_add,   po=12): pass
class ADDIC_   (_fmt.Instruction_D_add,   po=13): pass
class SUBF     (_fmt.Instruction_XO,      po=31, xo= 40, oe=0, rc=0): pass
class SUBF_    (_fmt.Instruction_XO,      po=31, xo= 40, oe=0, rc=1): pass
class SUBFO    (_fmt.Instruction_XO,      po=31, xo= 40, oe=1, rc=0): pass
class SUBFO_   (_fmt.Instruction_XO,      po=31, xo= 40, oe=1, rc=1): pass
class SUBFIC   (_fmt.Instruction_D_add,   po= 8): pass
class ADDC     (_fmt.Instruction_XO,      po=31, xo= 10, oe=0, rc=0): pass
class ADDC_    (_fmt.Instruction_XO,      po=31, xo= 10, oe=0, rc=1): pass
class ADDCO    (_fmt.Instruction_XO,      po=31, xo= 10, oe=1, rc=0): pass
class ADDCO_   (_fmt.Instruction_XO,      po=31, xo= 10, oe=1, rc=1): pass
class ADDE     (_fmt.Instruction_XO,      po=31, xo=138, oe=0, rc=0): pass
class ADDE_    (_fmt.Instruction_XO,      po=31, xo=138, oe=0, rc=1): pass
class ADDEO    (_fmt.Instruction_XO,      po=31, xo=138, oe=1, rc=0): pass
class ADDEO_   (_fmt.Instruction_XO,      po=31, xo=138, oe=1, rc=1): pass
class SUBFC    (_fmt.Instruction_XO,      po=31, xo=  8, oe=0, rc=0): pass
class SUBFC_   (_fmt.Instruction_XO,      po=31, xo=  8, oe=0, rc=1): pass
class SUBFCO   (_fmt.Instruction_XO,      po=31, xo=  8, oe=1, rc=0): pass
class SUBFCO_  (_fmt.Instruction_XO,      po=31, xo=  8, oe=1, rc=1): pass
class SUBFE    (_fmt.Instruction_XO,      po=31, xo=136, oe=0, rc=0): pass
class SUBFE_   (_fmt.Instruction_XO,      po=31, xo=136, oe=0, rc=1): pass
class SUBFEO   (_fmt.Instruction_XO,      po=31, xo=136, oe=1, rc=0): pass
class SUBFEO_  (_fmt.Instruction_XO,      po=31, xo=136, oe=1, rc=1): pass
class ADDME    (_fmt.Instruction_XO,      po=31, xo=234, oe=0, rc=0): pass
class ADDME_   (_fmt.Instruction_XO,      po=31, xo=234, oe=0, rc=1): pass
class ADDMEO   (_fmt.Instruction_XO,      po=31, xo=234, oe=1, rc=0): pass
class ADDMEO_  (_fmt.Instruction_XO,      po=31, xo=234, oe=1, rc=1): pass
class ADDZE    (_fmt.Instruction_XO,      po=31, xo=202, oe=0, rc=0): pass
class ADDZE_   (_fmt.Instruction_XO,      po=31, xo=202, oe=0, rc=1): pass
class ADDZEO   (_fmt.Instruction_XO,      po=31, xo=202, oe=1, rc=0): pass
class ADDZEO_  (_fmt.Instruction_XO,      po=31, xo=202, oe=1, rc=1): pass
class SUBFME   (_fmt.Instruction_XO,      po=31, xo=232, oe=0, rc=0): pass
class SUBFME_  (_fmt.Instruction_XO,      po=31, xo=232, oe=0, rc=1): pass
class SUBFMEO  (_fmt.Instruction_XO,      po=31, xo=232, oe=1, rc=0): pass
class SUBFMEO_ (_fmt.Instruction_XO,      po=31, xo=232, oe=1, rc=1): pass
class SUBFZE   (_fmt.Instruction_XO,      po=31, xo=200, oe=0, rc=0): pass
class SUBFZE_  (_fmt.Instruction_XO,      po=31, xo=200, oe=0, rc=1): pass
class SUBFZEO  (_fmt.Instruction_XO,      po=31, xo=200, oe=1, rc=0): pass
class SUBFZEO_ (_fmt.Instruction_XO,      po=31, xo=200, oe=1, rc=1): pass
class ADDEX    (_fmt.Instruction_Z23_add, po=31, xo=170, cy=0): pass
class NEG      (_fmt.Instruction_XO,      po=31, xo=104, oe=0, rc=0): pass
class NEG_     (_fmt.Instruction_XO,      po=31, xo=104, oe=0, rc=1): pass
class NEGO     (_fmt.Instruction_XO,      po=31, xo=104, oe=1, rc=0): pass
class NEGO_    (_fmt.Instruction_XO,      po=31, xo=104, oe=1, rc=1): pass

# Compare

class CMPI   (_fmt.Instruction_D_cmp, po=11): pass
class CMPLI  (_fmt.Instruction_D_cmp, po=10): pass
class CMP    (_fmt.Instruction_X_cmp, po=31, xo=  0): pass
class CMPL   (_fmt.Instruction_X_cmp, po=31, xo= 32): pass

# Move To/From SPR

class MTSPR  (_fmt.Instruction_XFX_spr, po=31, xo=467): pass
class MFSPR  (_fmt.Instruction_XFX_spr, po=31, xo=339): pass

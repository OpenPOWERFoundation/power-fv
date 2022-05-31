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

# Compare

class CMPI   (_fmt.Instruction_D_cmp, po=11): pass
class CMPLI  (_fmt.Instruction_D_cmp, po=10): pass
class CMP    (_fmt.Instruction_X_cmp, po=31, xo=  0): pass
class CMPL   (_fmt.Instruction_X_cmp, po=31, xo= 32): pass

# Move To/From SPR

class MTSPR  (_fmt.Instruction_XFX_spr, po=31, xo=467): pass
class MFSPR  (_fmt.Instruction_XFX_spr, po=31, xo=339): pass

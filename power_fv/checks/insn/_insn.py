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

from amaranth import signed, unsigned

from . import InsnField


class AA    (InsnField): _shape = unsigned( 1); _offset = 30; _name = "AA"
class BA    (InsnField): _shape = unsigned( 5); _offset = 11; _name = "BA"
class BB    (InsnField): _shape = unsigned( 5); _offset = 16; _name = "BB"
class BD    (InsnField): _shape =   signed(14); _offset = 16; _name = "BD"
class BF    (InsnField): _shape = unsigned( 3); _offset =  6; _name = "BF"
class BFA   (InsnField): _shape = unsigned( 3); _offset = 11; _name = "BFA"
class BH    (InsnField): _shape = unsigned( 2); _offset = 19; _name = "BH"
class BI    (InsnField): _shape = unsigned( 5); _offset = 11; _name = "BI"
class BO    (InsnField): _shape = unsigned( 5); _offset =  6; _name = "BO"
class BT    (InsnField): _shape = unsigned( 5); _offset =  6; _name = "BT"
class CY    (InsnField): _shape = unsigned( 2); _offset = 21; _name = "CY"
class D     (InsnField): _shape =   signed(16); _offset = 16; _name = "D"
class d0    (InsnField): _shape =   signed(10); _offset = 16; _name = "d0"
class d1    (InsnField): _shape =   signed( 5); _offset = 11; _name = "d1"
class d2    (InsnField): _shape =   signed( 1); _offset = 31; _name = "d2"
class FXM   (InsnField): _shape = unsigned( 8); _offset = 12; _name = "FXM"
class LEV   (InsnField): _shape = unsigned( 7); _offset = 20; _name = "LEV"
class L_D10 (InsnField): _shape = unsigned( 1); _offset = 10; _name = "L"
class L_X10 (InsnField): _shape = unsigned( 1); _offset = 10; _name = "L"
class L_X15 (InsnField): _shape = unsigned( 1); _offset = 15; _name = "L"
class LI    (InsnField): _shape =   signed(24); _offset =  6; _name = "LI"
class LK    (InsnField): _shape = unsigned( 1); _offset = 31; _name = "LK"
class OE    (InsnField): _shape = unsigned( 1); _offset = 21; _name = "OE"
class PO    (InsnField): _shape = unsigned( 6); _offset =  0; _name = "PO"
class MB    (InsnField): _shape = unsigned( 5); _offset = 21; _name = "MB"
class ME    (InsnField): _shape = unsigned( 5); _offset = 26; _name = "ME"
class RA    (InsnField): _shape = unsigned( 5); _offset = 11; _name = "RA"
class RB    (InsnField): _shape = unsigned( 5); _offset = 16; _name = "RB"
class Rc    (InsnField): _shape = unsigned( 1); _offset = 31; _name = "Rc"
class RS    (InsnField): _shape = unsigned( 5); _offset =  6; _name = "RS"
class RT    (InsnField): _shape = unsigned( 5); _offset =  6; _name = "RT"
class SC_30 (InsnField): _shape = unsigned( 1); _offset = 30; _name = "_30"
class SC_31 (InsnField): _shape = unsigned( 1); _offset = 31; _name = "_31"
class SI    (InsnField): _shape =   signed(16); _offset = 16; _name = "SI"
class SH    (InsnField): _shape = unsigned( 5); _offset = 16; _name = "SH"
class TO    (InsnField): _shape = unsigned( 5); _offset =  6; _name = "TO"
class UI    (InsnField): _shape = unsigned(16); _offset = 16; _name = "UI"
class XFX_11(InsnField): _shape = unsigned( 1); _offset = 11; _name = "_11"
class XO    (InsnField): _shape = unsigned( 9); _offset = 22; _name = "XO"
class XO_DX (InsnField): _shape = unsigned( 5); _offset = 26; _name = "XO"
class XO_X  (InsnField): _shape = unsigned(10); _offset = 21; _name = "XO"
class XO_XFX(InsnField): _shape = unsigned(10); _offset = 21; _name = "XO"
class XO_XL (InsnField): _shape = unsigned(10); _offset = 21; _name = "XO"
class XO_Z23(InsnField): _shape = unsigned( 8); _offset = 23; _name = "XO"


class SPR(InsnField):
    _shape  = unsigned(10)
    _offset = 11
    _name   = "SPR"

    def __init__(self, value=None):
        super().__init__(value)
        if self.value is not None:
            self.value = (self.value & 0x1f) << 5 | (self.value >> 5)

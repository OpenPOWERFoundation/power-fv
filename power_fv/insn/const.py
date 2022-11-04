from . import WordInsn
import power_fv.insn.field as f


# Branches

class B       (WordInsn): _fields = (f.PO(18), f.LI(), f.AA(0), f.LK(0))
class BA      (WordInsn): _fields = (f.PO(18), f.LI(), f.AA(1), f.LK(0))
class BL      (WordInsn): _fields = (f.PO(18), f.LI(), f.AA(0), f.LK(1))
class BLA     (WordInsn): _fields = (f.PO(18), f.LI(), f.AA(1), f.LK(1))

class BC      (WordInsn): _fields = (f.PO(16), f.BO(), f.BI(), f.BD(), f.AA(0), f.LK(0))
class BCA     (WordInsn): _fields = (f.PO(16), f.BO(), f.BI(), f.BD(), f.AA(1), f.LK(0))
class BCL     (WordInsn): _fields = (f.PO(16), f.BO(), f.BI(), f.BD(), f.AA(0), f.LK(1))
class BCLA    (WordInsn): _fields = (f.PO(16), f.BO(), f.BI(), f.BD(), f.AA(1), f.LK(1))

class BCLR    (WordInsn): _fields = (f.PO(19), f.BO(), f.BI(), f.BH(), f.XO_XL( 16), f.LK(0))
class BCLRL   (WordInsn): _fields = (f.PO(19), f.BO(), f.BI(), f.BH(), f.XO_XL( 16), f.LK(1))
class BCCTR   (WordInsn): _fields = (f.PO(19), f.BO(), f.BI(), f.BH(), f.XO_XL(528), f.LK(0))
class BCCTRL  (WordInsn): _fields = (f.PO(19), f.BO(), f.BI(), f.BH(), f.XO_XL(528), f.LK(1))
class BCTAR   (WordInsn): _fields = (f.PO(19), f.BO(), f.BI(), f.BH(), f.XO_XL(560), f.LK(0))
class BCTARL  (WordInsn): _fields = (f.PO(19), f.BO(), f.BI(), f.BH(), f.XO_XL(560), f.LK(1))

# System Call

class SC      (WordInsn): _fields = (f.PO(17), f.LEV(), f.SC_30(1))
class SCV     (WordInsn): _fields = (f.PO(17), f.LEV(), f.SC_30(0), f.SC_31(1))

# Condition Register

class CRAND   (WordInsn): _fields = (f.PO(19), f.BT(), f.BA(), f.BB(), f.XO_XL(257))
class CROR    (WordInsn): _fields = (f.PO(19), f.BT(), f.BA(), f.BB(), f.XO_XL(449))
class CRNAND  (WordInsn): _fields = (f.PO(19), f.BT(), f.BA(), f.BB(), f.XO_XL(225))
class CRXOR   (WordInsn): _fields = (f.PO(19), f.BT(), f.BA(), f.BB(), f.XO_XL(193))
class CRNOR   (WordInsn): _fields = (f.PO(19), f.BT(), f.BA(), f.BB(), f.XO_XL( 33))
class CRANDC  (WordInsn): _fields = (f.PO(19), f.BT(), f.BA(), f.BB(), f.XO_XL(129))
class CREQV   (WordInsn): _fields = (f.PO(19), f.BT(), f.BA(), f.BB(), f.XO_XL(289))
class CRORC   (WordInsn): _fields = (f.PO(19), f.BT(), f.BA(), f.BB(), f.XO_XL(417))

class MCRF    (WordInsn): _fields = (f.PO(19), f.BF(), f.BFA(),              f.XO_XL (  0))
class MCRXRX  (WordInsn): _fields = (f.PO(31), f.BF(),                       f.XO_X  (576))
class MTOCRF  (WordInsn): _fields = (f.PO(31), f.RS(), f.XFX_11(1), f.FXM(), f.XO_XFX(144))
class MTCRF   (WordInsn): _fields = (f.PO(31), f.RS(), f.XFX_11(0), f.FXM(), f.XO_XFX(144))
class MFOCRF  (WordInsn): _fields = (f.PO(31), f.RT(), f.XFX_11(1), f.FXM(), f.XO_XFX( 19))
class MFCR    (WordInsn): _fields = (f.PO(31), f.RT(), f.XFX_11(0),          f.XO_XFX( 19))

class SETB    (WordInsn): _fields = (f.PO(31), f.RT(), f.BFA(), f.XO_X(128))
class SETBC   (WordInsn): _fields = (f.PO(31), f.RT(), f.BI(),  f.XO_X(384))
class SETBCR  (WordInsn): _fields = (f.PO(31), f.RT(), f.BI(),  f.XO_X(416))
class SETNBC  (WordInsn): _fields = (f.PO(31), f.RT(), f.BI(),  f.XO_X(448))
class SETNBCR (WordInsn): _fields = (f.PO(31), f.RT(), f.BI(),  f.XO_X(480))

# Load

class LBZ     (WordInsn): _fields = (f.PO(34), f.RT(), f.RA(), f.D())
class LBZX    (WordInsn): _fields = (f.PO(31), f.RT(), f.RA(), f.RB(), f.XO_X( 87))
class LBZU    (WordInsn): _fields = (f.PO(35), f.RT(), f.RA(), f.D())
class LBZUX   (WordInsn): _fields = (f.PO(31), f.RT(), f.RA(), f.RB(), f.XO_X(119))
class LHZ     (WordInsn): _fields = (f.PO(40), f.RT(), f.RA(), f.D())
class LHZX    (WordInsn): _fields = (f.PO(31), f.RT(), f.RA(), f.RB(), f.XO_X(279))
class LHZU    (WordInsn): _fields = (f.PO(41), f.RT(), f.RA(), f.D())
class LHZUX   (WordInsn): _fields = (f.PO(31), f.RT(), f.RA(), f.RB(), f.XO_X(311))
class LHA     (WordInsn): _fields = (f.PO(42), f.RT(), f.RA(), f.D())
class LHAX    (WordInsn): _fields = (f.PO(31), f.RT(), f.RA(), f.RB(), f.XO_X(343))
class LHAU    (WordInsn): _fields = (f.PO(43), f.RT(), f.RA(), f.D())
class LHAUX   (WordInsn): _fields = (f.PO(31), f.RT(), f.RA(), f.RB(), f.XO_X(375))
class LWZ     (WordInsn): _fields = (f.PO(32), f.RT(), f.RA(), f.D())
class LWZX    (WordInsn): _fields = (f.PO(31), f.RT(), f.RA(), f.RB(), f.XO_X( 23))
class LWZU    (WordInsn): _fields = (f.PO(33), f.RT(), f.RA(), f.D())
class LWZUX   (WordInsn): _fields = (f.PO(31), f.RT(), f.RA(), f.RB(), f.XO_X( 55))

class LWBRX   (WordInsn): _fields = (f.PO(31), f.RT(), f.RA(), f.RB(), f.XO_X(534))

# Store

class STB     (WordInsn): _fields = (f.PO(38), f.RS(), f.RA(), f.D())
class STBX    (WordInsn): _fields = (f.PO(31), f.RS(), f.RA(), f.RB(), f.XO_X(215))
class STBU    (WordInsn): _fields = (f.PO(39), f.RS(), f.RA(), f.D())
class STBUX   (WordInsn): _fields = (f.PO(31), f.RS(), f.RA(), f.RB(), f.XO_X(247))
class STH     (WordInsn): _fields = (f.PO(44), f.RS(), f.RA(), f.D())
class STHX    (WordInsn): _fields = (f.PO(31), f.RS(), f.RA(), f.RB(), f.XO_X(407))
class STHU    (WordInsn): _fields = (f.PO(45), f.RS(), f.RA(), f.D())
class STHUX   (WordInsn): _fields = (f.PO(31), f.RS(), f.RA(), f.RB(), f.XO_X(439))
class STW     (WordInsn): _fields = (f.PO(36), f.RS(), f.RA(), f.D())
class STWX    (WordInsn): _fields = (f.PO(31), f.RS(), f.RA(), f.RB(), f.XO_X(151))
class STWU    (WordInsn): _fields = (f.PO(37), f.RS(), f.RA(), f.D())
class STWUX   (WordInsn): _fields = (f.PO(31), f.RS(), f.RA(), f.RB(), f.XO_X(183))

class STHBRX  (WordInsn): _fields = (f.PO(31), f.RS(), f.RA(), f.RB(), f.XO_X(918))
class STWBRX  (WordInsn): _fields = (f.PO(31), f.RS(), f.RA(), f.RB(), f.XO_X(662))

# Add / Subtract From

class ADDI    (WordInsn): _fields = (f.PO(14), f.RT(), f.RA(), f.SI())
class ADDIS   (WordInsn): _fields = (f.PO(15), f.RT(), f.RA(), f.SI())
class ADDPCIS (WordInsn): _fields = (f.PO(19), f.RT(), f.d1(), f.d0(), f.XO_DX(2), f.d2())
class ADD     (WordInsn): _fields = (f.PO(31), f.RT(), f.RA(), f.RB(), f.OE(0), f.XO(266), f.Rc(0))
class ADD_    (WordInsn): _fields = (f.PO(31), f.RT(), f.RA(), f.RB(), f.OE(0), f.XO(266), f.Rc(1))
class ADDO    (WordInsn): _fields = (f.PO(31), f.RT(), f.RA(), f.RB(), f.OE(1), f.XO(266), f.Rc(0))
class ADDO_   (WordInsn): _fields = (f.PO(31), f.RT(), f.RA(), f.RB(), f.OE(1), f.XO(266), f.Rc(1))
class ADDIC   (WordInsn): _fields = (f.PO(12), f.RT(), f.RA(), f.SI())
class ADDIC_  (WordInsn): _fields = (f.PO(13), f.RT(), f.RA(), f.SI())
class SUBF    (WordInsn): _fields = (f.PO(31), f.RT(), f.RA(), f.RB(), f.OE(0), f.XO( 40), f.Rc(0))
class SUBF_   (WordInsn): _fields = (f.PO(31), f.RT(), f.RA(), f.RB(), f.OE(0), f.XO( 40), f.Rc(1))
class SUBFO   (WordInsn): _fields = (f.PO(31), f.RT(), f.RA(), f.RB(), f.OE(1), f.XO( 40), f.Rc(0))
class SUBFO_  (WordInsn): _fields = (f.PO(31), f.RT(), f.RA(), f.RB(), f.OE(1), f.XO( 40), f.Rc(1))
class SUBFIC  (WordInsn): _fields = (f.PO( 8), f.RT(), f.RA(), f.SI())
class ADDC    (WordInsn): _fields = (f.PO(31), f.RT(), f.RA(), f.RB(), f.OE(0), f.XO( 10), f.Rc(0))
class ADDC_   (WordInsn): _fields = (f.PO(31), f.RT(), f.RA(), f.RB(), f.OE(0), f.XO( 10), f.Rc(1))
class ADDCO   (WordInsn): _fields = (f.PO(31), f.RT(), f.RA(), f.RB(), f.OE(1), f.XO( 10), f.Rc(0))
class ADDCO_  (WordInsn): _fields = (f.PO(31), f.RT(), f.RA(), f.RB(), f.OE(1), f.XO( 10), f.Rc(1))
class ADDE    (WordInsn): _fields = (f.PO(31), f.RT(), f.RA(), f.RB(), f.OE(0), f.XO(138), f.Rc(0))
class ADDE_   (WordInsn): _fields = (f.PO(31), f.RT(), f.RA(), f.RB(), f.OE(0), f.XO(138), f.Rc(1))
class ADDEO   (WordInsn): _fields = (f.PO(31), f.RT(), f.RA(), f.RB(), f.OE(1), f.XO(138), f.Rc(0))
class ADDEO_  (WordInsn): _fields = (f.PO(31), f.RT(), f.RA(), f.RB(), f.OE(1), f.XO(138), f.Rc(1))
class SUBFC   (WordInsn): _fields = (f.PO(31), f.RT(), f.RA(), f.RB(), f.OE(0), f.XO(  8), f.Rc(0))
class SUBFC_  (WordInsn): _fields = (f.PO(31), f.RT(), f.RA(), f.RB(), f.OE(0), f.XO(  8), f.Rc(1))
class SUBFCO  (WordInsn): _fields = (f.PO(31), f.RT(), f.RA(), f.RB(), f.OE(1), f.XO(  8), f.Rc(0))
class SUBFCO_ (WordInsn): _fields = (f.PO(31), f.RT(), f.RA(), f.RB(), f.OE(1), f.XO(  8), f.Rc(1))
class SUBFE   (WordInsn): _fields = (f.PO(31), f.RT(), f.RA(), f.RB(), f.OE(0), f.XO(136), f.Rc(0))
class SUBFE_  (WordInsn): _fields = (f.PO(31), f.RT(), f.RA(), f.RB(), f.OE(0), f.XO(136), f.Rc(1))
class SUBFEO  (WordInsn): _fields = (f.PO(31), f.RT(), f.RA(), f.RB(), f.OE(1), f.XO(136), f.Rc(0))
class SUBFEO_ (WordInsn): _fields = (f.PO(31), f.RT(), f.RA(), f.RB(), f.OE(1), f.XO(136), f.Rc(1))
class ADDME   (WordInsn): _fields = (f.PO(31), f.RT(), f.RA(), f.RB(), f.OE(0), f.XO(234), f.Rc(0))
class ADDME_  (WordInsn): _fields = (f.PO(31), f.RT(), f.RA(), f.RB(), f.OE(0), f.XO(234), f.Rc(1))
class ADDMEO  (WordInsn): _fields = (f.PO(31), f.RT(), f.RA(), f.RB(), f.OE(1), f.XO(234), f.Rc(0))
class ADDMEO_ (WordInsn): _fields = (f.PO(31), f.RT(), f.RA(), f.RB(), f.OE(1), f.XO(234), f.Rc(1))
class ADDZE   (WordInsn): _fields = (f.PO(31), f.RT(), f.RA(), f.RB(), f.OE(0), f.XO(202), f.Rc(0))
class ADDZE_  (WordInsn): _fields = (f.PO(31), f.RT(), f.RA(), f.RB(), f.OE(0), f.XO(202), f.Rc(1))
class ADDZEO  (WordInsn): _fields = (f.PO(31), f.RT(), f.RA(), f.RB(), f.OE(1), f.XO(202), f.Rc(0))
class ADDZEO_ (WordInsn): _fields = (f.PO(31), f.RT(), f.RA(), f.RB(), f.OE(1), f.XO(202), f.Rc(1))
class SUBFME  (WordInsn): _fields = (f.PO(31), f.RT(), f.RA(), f.RB(), f.OE(0), f.XO(232), f.Rc(0))
class SUBFME_ (WordInsn): _fields = (f.PO(31), f.RT(), f.RA(), f.RB(), f.OE(0), f.XO(232), f.Rc(1))
class SUBFMEO (WordInsn): _fields = (f.PO(31), f.RT(), f.RA(), f.RB(), f.OE(1), f.XO(232), f.Rc(0))
class SUBFMEO_(WordInsn): _fields = (f.PO(31), f.RT(), f.RA(), f.RB(), f.OE(1), f.XO(232), f.Rc(1))
class SUBFZE  (WordInsn): _fields = (f.PO(31), f.RT(), f.RA(), f.RB(), f.OE(0), f.XO(200), f.Rc(0))
class SUBFZE_ (WordInsn): _fields = (f.PO(31), f.RT(), f.RA(), f.RB(), f.OE(0), f.XO(200), f.Rc(1))
class SUBFZEO (WordInsn): _fields = (f.PO(31), f.RT(), f.RA(), f.RB(), f.OE(1), f.XO(200), f.Rc(0))
class SUBFZEO_(WordInsn): _fields = (f.PO(31), f.RT(), f.RA(), f.RB(), f.OE(1), f.XO(200), f.Rc(1))
class ADDEX   (WordInsn): _fields = (f.PO(31), f.RT(), f.RA(), f.RB(), f.CY(0), f.XO_Z23(170))
class NEG     (WordInsn): _fields = (f.PO(31), f.RT(), f.RA(), f.RB(), f.OE(0), f.XO(104), f.Rc(0))
class NEG_    (WordInsn): _fields = (f.PO(31), f.RT(), f.RA(), f.RB(), f.OE(0), f.XO(104), f.Rc(1))
class NEGO    (WordInsn): _fields = (f.PO(31), f.RT(), f.RA(), f.RB(), f.OE(1), f.XO(104), f.Rc(0))
class NEGO_   (WordInsn): _fields = (f.PO(31), f.RT(), f.RA(), f.RB(), f.OE(1), f.XO(104), f.Rc(1))

# Multiply / Divide / Modulo

class MULLI   (WordInsn): _fields = (f.PO( 7), f.RT(), f.RA(), f.SI())
class MULLW   (WordInsn): _fields = (f.PO(31), f.RT(), f.RA(), f.RB(), f.OE(0), f.XO(235), f.Rc(0))
class MULLW_  (WordInsn): _fields = (f.PO(31), f.RT(), f.RA(), f.RB(), f.OE(0), f.XO(235), f.Rc(1))
class MULLWO  (WordInsn): _fields = (f.PO(31), f.RT(), f.RA(), f.RB(), f.OE(1), f.XO(235), f.Rc(0))
class MULLWO_ (WordInsn): _fields = (f.PO(31), f.RT(), f.RA(), f.RB(), f.OE(1), f.XO(235), f.Rc(1))
class MULHW   (WordInsn): _fields = (f.PO(31), f.RT(), f.RA(), f.RB(),          f.XO( 75), f.Rc(0))
class MULHW_  (WordInsn): _fields = (f.PO(31), f.RT(), f.RA(), f.RB(),          f.XO( 75), f.Rc(1))
class MULHWU  (WordInsn): _fields = (f.PO(31), f.RT(), f.RA(), f.RB(),          f.XO( 11), f.Rc(0))
class MULHWU_ (WordInsn): _fields = (f.PO(31), f.RT(), f.RA(), f.RB(),          f.XO( 11), f.Rc(1))

class DIVW    (WordInsn): _fields = (f.PO(31), f.RT(), f.RA(), f.RB(), f.OE(0), f.XO(491), f.Rc(0))
class DIVW_   (WordInsn): _fields = (f.PO(31), f.RT(), f.RA(), f.RB(), f.OE(0), f.XO(491), f.Rc(1))
class DIVWO   (WordInsn): _fields = (f.PO(31), f.RT(), f.RA(), f.RB(), f.OE(1), f.XO(491), f.Rc(0))
class DIVWO_  (WordInsn): _fields = (f.PO(31), f.RT(), f.RA(), f.RB(), f.OE(1), f.XO(491), f.Rc(1))
class DIVWU   (WordInsn): _fields = (f.PO(31), f.RT(), f.RA(), f.RB(), f.OE(0), f.XO(459), f.Rc(0))
class DIVWU_  (WordInsn): _fields = (f.PO(31), f.RT(), f.RA(), f.RB(), f.OE(0), f.XO(459), f.Rc(1))
class DIVWUO  (WordInsn): _fields = (f.PO(31), f.RT(), f.RA(), f.RB(), f.OE(1), f.XO(459), f.Rc(0))
class DIVWUO_ (WordInsn): _fields = (f.PO(31), f.RT(), f.RA(), f.RB(), f.OE(1), f.XO(459), f.Rc(1))
class DIVWE   (WordInsn): _fields = (f.PO(31), f.RT(), f.RA(), f.RB(), f.OE(0), f.XO(427), f.Rc(0))
class DIVWE_  (WordInsn): _fields = (f.PO(31), f.RT(), f.RA(), f.RB(), f.OE(0), f.XO(427), f.Rc(1))
class DIVWEO  (WordInsn): _fields = (f.PO(31), f.RT(), f.RA(), f.RB(), f.OE(1), f.XO(427), f.Rc(0))
class DIVWEO_ (WordInsn): _fields = (f.PO(31), f.RT(), f.RA(), f.RB(), f.OE(1), f.XO(427), f.Rc(1))
class DIVWEU  (WordInsn): _fields = (f.PO(31), f.RT(), f.RA(), f.RB(), f.OE(0), f.XO(395), f.Rc(0))
class DIVWEU_ (WordInsn): _fields = (f.PO(31), f.RT(), f.RA(), f.RB(), f.OE(0), f.XO(395), f.Rc(1))
class DIVWEUO (WordInsn): _fields = (f.PO(31), f.RT(), f.RA(), f.RB(), f.OE(1), f.XO(395), f.Rc(0))
class DIVWEUO_(WordInsn): _fields = (f.PO(31), f.RT(), f.RA(), f.RB(), f.OE(1), f.XO(395), f.Rc(1))

class MODSW   (WordInsn): _fields = (f.PO(31), f.RT(), f.RA(), f.RB(), f.XO_X(779))
class MODUW   (WordInsn): _fields = (f.PO(31), f.RT(), f.RA(), f.RB(), f.XO_X(267))

# Compare

class CMPI    (WordInsn): _fields = (f.PO(11), f.BF(), f.L_D10(), f.RA(), f.SI())
class CMPLI   (WordInsn): _fields = (f.PO(10), f.BF(), f.L_D10(), f.RA(), f.UI())
class CMP     (WordInsn): _fields = (f.PO(31), f.BF(), f.L_X10(), f.RA(), f.RB(), f.XO_X(  0))
class CMPL    (WordInsn): _fields = (f.PO(31), f.BF(), f.L_X10(), f.RA(), f.RB(), f.XO_X( 32))
class CMPRB   (WordInsn): _fields = (f.PO(31), f.BF(), f.L_X10(), f.RA(), f.RB(), f.XO_X(192))
class CMPEQB  (WordInsn): _fields = (f.PO(31), f.BF(), f.L_X10(), f.RA(), f.RB(), f.XO_X(224))

# Trap

class TWI     (WordInsn): _fields = (f.PO( 3), f.TO(), f.RA(), f.SI())
class TW      (WordInsn): _fields = (f.PO(31), f.TO(), f.RA(), f.RB(), f.XO_X(4))

# Logical

class ANDI_   (WordInsn): _fields = (f.PO(28), f.RS(), f.RA(), f.UI())
class ANDIS_  (WordInsn): _fields = (f.PO(29), f.RS(), f.RA(), f.UI())
class ORI     (WordInsn): _fields = (f.PO(24), f.RS(), f.RA(), f.UI())
class ORIS    (WordInsn): _fields = (f.PO(25), f.RS(), f.RA(), f.UI())
class XORI    (WordInsn): _fields = (f.PO(26), f.RS(), f.RA(), f.UI())
class XORIS   (WordInsn): _fields = (f.PO(27), f.RS(), f.RA(), f.UI())
class AND     (WordInsn): _fields = (f.PO(31), f.RS(), f.RA(), f.RB(), f.XO_X( 28), f.Rc(0))
class AND_    (WordInsn): _fields = (f.PO(31), f.RS(), f.RA(), f.RB(), f.XO_X( 28), f.Rc(1))
class XOR     (WordInsn): _fields = (f.PO(31), f.RS(), f.RA(), f.RB(), f.XO_X(316), f.Rc(0))
class XOR_    (WordInsn): _fields = (f.PO(31), f.RS(), f.RA(), f.RB(), f.XO_X(316), f.Rc(1))
class NAND    (WordInsn): _fields = (f.PO(31), f.RS(), f.RA(), f.RB(), f.XO_X(476), f.Rc(0))
class NAND_   (WordInsn): _fields = (f.PO(31), f.RS(), f.RA(), f.RB(), f.XO_X(476), f.Rc(1))
class OR      (WordInsn): _fields = (f.PO(31), f.RS(), f.RA(), f.RB(), f.XO_X(444), f.Rc(0))
class OR_     (WordInsn): _fields = (f.PO(31), f.RS(), f.RA(), f.RB(), f.XO_X(444), f.Rc(1))
class ORC     (WordInsn): _fields = (f.PO(31), f.RS(), f.RA(), f.RB(), f.XO_X(412), f.Rc(0))
class ORC_    (WordInsn): _fields = (f.PO(31), f.RS(), f.RA(), f.RB(), f.XO_X(412), f.Rc(1))
class NOR     (WordInsn): _fields = (f.PO(31), f.RS(), f.RA(), f.RB(), f.XO_X(124), f.Rc(0))
class NOR_    (WordInsn): _fields = (f.PO(31), f.RS(), f.RA(), f.RB(), f.XO_X(124), f.Rc(1))
class EQV     (WordInsn): _fields = (f.PO(31), f.RS(), f.RA(), f.RB(), f.XO_X(284), f.Rc(0))
class EQV_    (WordInsn): _fields = (f.PO(31), f.RS(), f.RA(), f.RB(), f.XO_X(284), f.Rc(1))
class ANDC    (WordInsn): _fields = (f.PO(31), f.RS(), f.RA(), f.RB(), f.XO_X( 60), f.Rc(0))
class ANDC_   (WordInsn): _fields = (f.PO(31), f.RS(), f.RA(), f.RB(), f.XO_X( 60), f.Rc(1))

class EXTSB   (WordInsn): _fields = (f.PO(31), f.RS(), f.RA(),         f.XO_X(954), f.Rc(0))
class EXTSB_  (WordInsn): _fields = (f.PO(31), f.RS(), f.RA(),         f.XO_X(954), f.Rc(1))
class EXTSH   (WordInsn): _fields = (f.PO(31), f.RS(), f.RA(),         f.XO_X(922), f.Rc(0))
class EXTSH_  (WordInsn): _fields = (f.PO(31), f.RS(), f.RA(),         f.XO_X(922), f.Rc(1))
class CMPB    (WordInsn): _fields = (f.PO(31), f.RS(), f.RA(), f.RB(), f.XO_X(508))
class CNTLZW  (WordInsn): _fields = (f.PO(31), f.RS(), f.RA(),         f.XO_X( 26), f.Rc(0))
class CNTLZW_ (WordInsn): _fields = (f.PO(31), f.RS(), f.RA(),         f.XO_X( 26), f.Rc(1))
class CNTTZW  (WordInsn): _fields = (f.PO(31), f.RS(), f.RA(),         f.XO_X(538), f.Rc(0))
class CNTTZW_ (WordInsn): _fields = (f.PO(31), f.RS(), f.RA(),         f.XO_X(538), f.Rc(1))
class POPCNTB (WordInsn): _fields = (f.PO(31), f.RS(), f.RA(),         f.XO_X(122))
class POPCNTW (WordInsn): _fields = (f.PO(31), f.RS(), f.RA(),         f.XO_X(378))
class PRTYW   (WordInsn): _fields = (f.PO(31), f.RS(), f.RA(),         f.XO_X(154))

# Rotate / Shift

class RLWINM  (WordInsn): _fields = (f.PO(21), f.RS(), f.RA(), f.SH(), f.MB(), f.ME(), f.Rc(0))
class RLWINM_ (WordInsn): _fields = (f.PO(21), f.RS(), f.RA(), f.SH(), f.MB(), f.ME(), f.Rc(1))
class RLWNM   (WordInsn): _fields = (f.PO(23), f.RS(), f.RA(), f.RB(), f.MB(), f.ME(), f.Rc(0))
class RLWNM_  (WordInsn): _fields = (f.PO(23), f.RS(), f.RA(), f.RB(), f.MB(), f.ME(), f.Rc(1))
class RLWIMI  (WordInsn): _fields = (f.PO(20), f.RS(), f.RA(), f.SH(), f.MB(), f.ME(), f.Rc(0))
class RLWIMI_ (WordInsn): _fields = (f.PO(20), f.RS(), f.RA(), f.SH(), f.MB(), f.ME(), f.Rc(1))

class SLW     (WordInsn): _fields = (f.PO(31), f.RS(), f.RA(), f.RB(), f.XO_X( 24), f.Rc(0))
class SLW_    (WordInsn): _fields = (f.PO(31), f.RS(), f.RA(), f.RB(), f.XO_X( 24), f.Rc(1))
class SRW     (WordInsn): _fields = (f.PO(31), f.RS(), f.RA(), f.RB(), f.XO_X(536), f.Rc(0))
class SRW_    (WordInsn): _fields = (f.PO(31), f.RS(), f.RA(), f.RB(), f.XO_X(536), f.Rc(1))
class SRAWI   (WordInsn): _fields = (f.PO(31), f.RS(), f.RA(), f.SH(), f.XO_X(824), f.Rc(0))
class SRAWI_  (WordInsn): _fields = (f.PO(31), f.RS(), f.RA(), f.SH(), f.XO_X(824), f.Rc(1))
class SRAW    (WordInsn): _fields = (f.PO(31), f.RS(), f.RA(), f.RB(), f.XO_X(792), f.Rc(0))
class SRAW_   (WordInsn): _fields = (f.PO(31), f.RS(), f.RA(), f.RB(), f.XO_X(792), f.Rc(1))

# BCD Assist

class CDTBCD  (WordInsn): _fields = (f.PO(31), f.RS(), f.RA(),         f.XO_X(282))
class CBCDTD  (WordInsn): _fields = (f.PO(31), f.RS(), f.RA(),         f.XO_X(314))
class ADDG6S  (WordInsn): _fields = (f.PO(31), f.RT(), f.RA(), f.RB(), f.XO(74))

# Byte-Reverse

class BRH     (WordInsn): _fields = (f.PO(31), f.RS(), f.RA(),         f.XO_X(219))
class BRW     (WordInsn): _fields = (f.PO(31), f.RS(), f.RA(),         f.XO_X(155))

# Move To/From System Register

class MTMSR   (WordInsn): _fields = (f.PO(31), f.RS(), f.L_X15(), f.XO_X(146))
class MFMSR   (WordInsn): _fields = (f.PO(31), f.RT(),            f.XO_X( 83))

class MTXER   (WordInsn): _fields = (f.PO(31), f.RS(), f.SPR(  1), f.XO_XFX(467))
class MFXER   (WordInsn): _fields = (f.PO(31), f.RT(), f.SPR(  1), f.XO_XFX(339))
class MTLR    (WordInsn): _fields = (f.PO(31), f.RS(), f.SPR(  8), f.XO_XFX(467))
class MFLR    (WordInsn): _fields = (f.PO(31), f.RT(), f.SPR(  8), f.XO_XFX(339))
class MTCTR   (WordInsn): _fields = (f.PO(31), f.RS(), f.SPR(  9), f.XO_XFX(467))
class MFCTR   (WordInsn): _fields = (f.PO(31), f.RT(), f.SPR(  9), f.XO_XFX(339))
class MTSRR0  (WordInsn): _fields = (f.PO(31), f.RS(), f.SPR( 26), f.XO_XFX(467))
class MFSRR0  (WordInsn): _fields = (f.PO(31), f.RT(), f.SPR( 26), f.XO_XFX(339))
class MTSRR1  (WordInsn): _fields = (f.PO(31), f.RS(), f.SPR( 27), f.XO_XFX(467))
class MFSRR1  (WordInsn): _fields = (f.PO(31), f.RT(), f.SPR( 27), f.XO_XFX(339))
class MTTAR   (WordInsn): _fields = (f.PO(31), f.RS(), f.SPR(814), f.XO_XFX(467))
class MFTAR   (WordInsn): _fields = (f.PO(31), f.RT(), f.SPR(814), f.XO_XFX(339))

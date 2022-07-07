from amaranth import *


__all__ = [
    "_ea_layout",
    "cr_layout", "msr_layout",
    "lr_layout", "ctr_layout", "tar_layout",
    "xer_layout",
    "srr0_layout", "srr1_layout",
]


# used for registers that hold an effective address
_ea_layout = [
    ("_62", unsigned( 2)),
    ("ea" , unsigned(62)),
]


cr_layout  = [
    (f"cr{i}", unsigned(4)) for i in reversed(range(8))
]


msr_layout = [
    ("le" , unsigned( 1)),
    ("ri" , unsigned( 1)),
    ("pmm", unsigned( 1)),
    ("_60", unsigned( 1)),
    ("dr" , unsigned( 1)),
    ("ir" , unsigned( 1)),
    ("_56", unsigned( 2)),
    ("fe1", unsigned( 1)),
    ("te" , unsigned( 2)),
    ("fe0", unsigned( 1)),
    ("me" , unsigned( 1)),
    ("fp" , unsigned( 1)),
    ("pr" , unsigned( 1)),
    ("ee" , unsigned( 1)),
    ("_42", unsigned( 6)),
    ("s"  , unsigned( 1)),
    ("vsx", unsigned( 1)),
    ("_39", unsigned( 1)),
    ("vec", unsigned( 1)),
    ("_32", unsigned( 6)),
    ("_6" , unsigned(26)),
    ("_5" , unsigned( 1)),
    ("_4" , unsigned( 1)),
    ("hv" , unsigned( 1)),
    ("_1" , unsigned( 2)),
    ("sf" , unsigned( 1)),
]


lr_layout   = [("lr" , unsigned(64))]
ctr_layout  = [("ctr", unsigned(64))]
tar_layout  = _ea_layout


xer_layout = [
    ("_57" , unsigned( 7)), # size of Load/Store String Indexed transfers
    ("_56" , unsigned( 1)), # reserved
    ("_48" , unsigned( 8)), # reserved, but software can r/w it
    ("_46" , unsigned( 2)), # reserved
    ("ca32", unsigned( 1)),
    ("ov32", unsigned( 1)),
    ("_35" , unsigned( 9)), # reserved
    ("ca"  , unsigned( 1)),
    ("ov"  , unsigned( 1)),
    ("so"  , unsigned( 1)),
    ("_0"  , unsigned(32)), # reserved
]


srr0_layout = _ea_layout
srr1_layout = msr_layout

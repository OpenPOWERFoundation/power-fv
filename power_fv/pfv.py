from amaranth import *
from amaranth.utils import log2_int

from power_fv.reg import *


__all__ = [
    "gprf_port_layout", "reg_port_layout", "mem_port_layout",
    "Interface",
]


def gprf_port_layout():
    return [
        ("index" ,  unsigned( 5)),
        ("r_stb" ,  unsigned( 1)),
        ("r_data",  unsigned(64)),
        ("w_stb",   unsigned( 1)),
        ("w_data",  unsigned(64)),
    ]


def reg_port_layout(reg_layout):
    return [
        ("r_mask",  reg_layout),
        ("r_data",  reg_layout),
        ("w_mask",  reg_layout),
        ("w_data",  reg_layout),
    ]


def mem_port_layout(access):
    if access not in ("r", "rw"):
        raise ValueError("Access mode must be \"r\" or \"rw\", not {!r}"
                        .format(access))

    granularity = 8
    data_width  = 64
    mask_width  = data_width // granularity
    addr_width  = 64 - log2_int(data_width // granularity)

    access_layout = [
        ("mask", unsigned(mask_width)),
        ("data", unsigned(data_width)),
    ]

    layout = [("addr", unsigned(addr_width))]
    if "r" in access:
        layout += [("r", access_layout)]
    if "w" in access:
        layout += [("w", access_layout)]
    return layout


class Interface(Record):
    """Power-FV interface.

    The interface between the formal testbench and the processor-under-test.

    Attributes
    ----------
    stb : Signal
        Instruction strobe. Asserted when the processor retires an instruction. Other signals are
        only valid when ``stb`` is asserted.
    """
    def __init__(self, *, name=None, src_loc_at=0):
        layout = [
            ("stb"  , unsigned( 1)),
            ("insn" , unsigned(64)),
            ("order", unsigned(64)),
            ("intr" , unsigned( 1)),
            ("cia"  , unsigned(64)),
            ("nia"  , unsigned(64)),

            ("ra", gprf_port_layout()),
            ("rb", gprf_port_layout()),
            ("rs", gprf_port_layout()),
            ("rt", gprf_port_layout()),

            ("cr"  , reg_port_layout(  cr_layout)),
            ("msr" , reg_port_layout( msr_layout)),
            ("lr"  , reg_port_layout(  lr_layout)),
            ("ctr" , reg_port_layout( ctr_layout)),
            ("tar" , reg_port_layout( tar_layout)),
            ("xer" , reg_port_layout( xer_layout)),
            ("srr0", reg_port_layout(srr0_layout)),
            ("srr1", reg_port_layout(srr1_layout)),

            ("insn_mem", mem_port_layout(access="r" )),
            ("data_mem", mem_port_layout(access="rw")),
        ]
        super().__init__(layout, name=name, src_loc_at=1 + src_loc_at)

from amaranth import *
from amaranth.utils import log2_int

from power_fv.reg import *


__all__ = [
    "gpr_port_layout", "mem_port_layout", "reg_port_layout",
    "Interface",
]


def gpr_port_layout():
    """GPR port layout.

    Fields
    ------

    index : unsigned(5)
        GPR index.
    r_stb : unsigned(1)
        Read strobe.
    r_data : unsigned(64)
        Read data. Valid if `r_stb` is asserted.
    w_stb : unsigned(1)
        Write strobe.
    w_data : unsigned(64)
        Write data. Valid if `w_stb` is asserted.
    """
    return [
        ("index" ,  unsigned( 5)),
        ("r_stb" ,  unsigned( 1)),
        ("r_data",  unsigned(64)),
        ("w_stb",   unsigned( 1)),
        ("w_data",  unsigned(64)),
    ]


def mem_port_layout():
    """Memory port layout.

    Fields
    ------

    addr : unsigned(64)
        Memory address.
    r_mask : unsigned(8)
        Read mask. Each asserted bit corresponds to a valid byte in `r_data`.
    r_data : unsigned(64)
        Read data.
    w_mask : unsigned(8)
        Write mask. Each asserted bit corresponds to a valid byte in `w_data`.
    w_data : unsigned(64)
        Write data.
    """
    return [
        ("addr",   unsigned(64)),
        ("r_mask", unsigned( 8)),
        ("r_data", unsigned(64)),
        ("w_mask", unsigned( 8)),
        ("w_data", unsigned(64)),
    ]


def reg_port_layout(reg_layout):
    """Register port layout.

    Parameters
    ----------
    reg_layout : list(str, Shape)
        Register layout. See :mod:`power_fv.reg`.

    Fields
    ------

    r_mask : ``reg_layout``
        Read mask. Each asserted bit corresponds to a valid bit in `r_data`.
    r_data : ``reg_layout``
        Read data.
    w_mask : ``reg_layout``
        Write mask. Each asserted bit corresponds to a valid bit in `w_data`.
    w_data : ``reg_layout``
        Write data.
    """
    return [
        ("r_mask", reg_layout),
        ("r_data", reg_layout),
        ("w_mask", reg_layout),
        ("w_data", reg_layout),
    ]


class Interface(Record):
    """POWER-FV interface.

    The interface between a CPU core and a POWER-FV testbench. It describes the context and side-
    effects of every instruction retired by the core. A testbench can monitor this interface to
    observe program execution.

    While this interface is meant to be used as an output-only stream from core to testbench, it
    is also used internally as a bidirectional interface, where fields related to context (such
    as read data) and side-effects (such as the NIA) have opposite directions.

    Parameters
    ----------
    The following parameters describe implementation-specific behavior. They do not affect the
    layout of this interface.

    mem_aligned : bool
        If ``True``, an Alignment interrupt is expected if the effective address of a Load/Store
        operation is not aligned to its operand; ``mem.addr`` is also expected to be aligned to
        8 bytes. If ``False``, ``mem.addr`` is expected to point to the least- or most-significant
        byte of the storage operand, depending on the current endian mode.
    illegal_insn_heai : bool
        If ``True``, an illegal instruction triggers an Hypervisor Emulation Assistance interrupt.
        Otherwise, it triggers an Illegal Instruction type Program interrupt (which was removed in
        V2.06, as noted in §7.5.9, Book III).
    muldiv_altops : bool
        If ``True``, fixed-point Multiply/Divide/Modulo operations are replaced with alternative
        operations, which are meant to be considerably simpler to verify by a bounded model check.
        The control logic of the CPU core can still be verified, if the relevant execution unit is
        replaced by a compatible blackbox.

        +--------------+--------------------------------------------+
        | Instruction  | Alternative operation                      |
        +==============+============================================+
        | MULLI        | r := (RA) + EXTS(SI)                       |
        |              | m := 0xEF31A883837039A0                    |
        |              | (RT) := r XOR m                            |
        +--------------+--------------------------------------------+
        | MULLW[O][.]  | r := EXTS((RA)[32:63]) + EXTS((RB)[32:63]) |
        |              | m := 0x4931591F31F56DE1                    |
        |              | (RT) := r XOR m                            |
        +--------------+--------------------------------------------+
        | MULHW[.]     | r := EXTS((RA)[32:63]) + EXTS((RB)[32:63]) |
        |              | m := 0x3426DCF55920989C                    |
        |              | (RT) := r XOR m                            |
        +--------------+--------------------------------------------+
        | MULHWU[.]    | r := EXTZ((RA)[32:63]) + EXTZ((RB)[32:63]) |
        |              | m := 0x491EDB8A5F695D49                    |
        |              | (RT) := r XOR m                            |
        +--------------+--------------------------------------------+
        | DIVW[O][.]   | r := EXTS((RA)[32:63]) - EXTS((RB)[32:63]) |
        |              | m := 0x75A5D4895A3E15BA                    |
        |              | (RT) := r XOR m                            |
        +--------------+--------------------------------------------+
        | DIVWU[O][.]  | r := EXTZ((RA)[32:63]) - EXTZ((RB)[32:63]) |
        |              | m := 0x769C76AF68D11402                    |
        |              | (RT) := r XOR m                            |
        +--------------+--------------------------------------------+
        | DIVWE[O][.]  | r := EXTS((RA)[32:63]) - EXTS((RB)[32:63]) |
        |              | m := 0xDFD9D577965D84D2                    |
        |              | (RT) := r XOR m                            |
        +--------------+--------------------------------------------+
        | DIVWEU[O][.] | r := EXTZ((RA)[32:63]) - EXTZ((RB)[32:63]) |
        |              | m := 0x8FC71F88B966FCF0                    |
        |              | (RT) := r XOR m                            |
        +--------------+--------------------------------------------+
        | MODSW        | r := EXTS((RA)[32:63]) - EXTS((RB)[32:63]) |
        |              | m := 0x5BA1758B11AE4E43                    |
        |              | (RT) := r XOR m                            |
        +--------------+--------------------------------------------+
        | MODUW        | r := EXTZ((RA)[32:63]) - EXTZ((RB)[32:63]) |
        |              | m := 0x1FEB9D95F9F0CEA5                    |
        |              | (RT) := r XOR m                            |
        +--------------+--------------------------------------------+

        If the original operation updates CR0 or XER bits as a side-effect, then its alternative
        updates them too, using `r` as the result (instead of the value written to RT).

    Attributes
    ----------
    stb : Signal
        Instruction strobe. Asserted by the core to declare a retired instruction. Other fields of
        this interface are only valid if this signal is asserted.
    insn : Signal(64)
        Instruction value. Word instructions are placed on the high-order 32 bits. Prefixed
        instructions have their prefix on the low-order 32 bits.
    order : Signal(64)
        Instruction index. Each retired instruction has an unique index representing its position
        in program order, starting from 0. Consecutive instructions have consecutive indexes.
    intr : Signal
        Interrupt. Asserted if an interrupt was triggered during the execution of this instruction.
    cia : Signal(64)
        Current Instruction Address.
    nia : Signal(64)
        Next Instruction Address.
    skip : Signal
        Skipped instruction. Asserted to indicate an instruction that wasn't executed. This can
        happen in implementation-specific cases such as no-ops.
    ra : Record(:func:`gpr_port_layout`)
        GPR access from field RA.
    rb : Record(:func:`gpr_port_layout`)
        GPR access from field RB.
    rs : Record(:func:`gpr_port_layout`)
        GPR access from field RS.
    rt : Record(:func:`gpr_port_layout`)
        GPR access from field RT.
    mem : Record(:func:`mem_port_layout`)
        Memory access.
    cr : Record(:func:`reg_port_layout`)
        Condition Register access.
    msr : Record(:func:`reg_port_layout`)
        Machine State Register access.
    lr : Record(:func:`reg_port_layout`)
        Link Register access.
    ctr : Record(:func:`reg_port_layout`)
        Count Register access.
    tar : Record(:func:`reg_port_layout`)
        Target Address Register access.
    xer : Record(:func:`reg_port_layout`)
        Exception Register access.
    srr0 : Record(:func:`reg_port_layout`)
        Save/Restore Register 0 access.
    srr1 : Record(:func:`reg_port_layout`)
        Save/Restore Register 1 access.
    """
    def __init__(self, *, mem_aligned=False, illegal_insn_heai=False, muldiv_altops=False,
                 name=None, src_loc_at=0):
        self.mem_aligned       = bool(mem_aligned)
        self.illegal_insn_heai = bool(illegal_insn_heai)
        self.muldiv_altops     = bool(muldiv_altops)

        layout = [
            ("stb"  , unsigned( 1)),
            ("insn" , unsigned(64)),
            ("order", unsigned(64)),
            ("intr" , unsigned( 1)),
            ("cia"  , unsigned(64)),
            ("nia"  , unsigned(64)),
            ("skip" , unsigned( 1)),

            ("ra", gpr_port_layout()),
            ("rb", gpr_port_layout()),
            ("rs", gpr_port_layout()),
            ("rt", gpr_port_layout()),

            ("mem", mem_port_layout()),

            ("cr"  , reg_port_layout(  cr_layout)),
            ("msr" , reg_port_layout( msr_layout)),
            ("lr"  , reg_port_layout(  lr_layout)),
            ("ctr" , reg_port_layout( ctr_layout)),
            ("tar" , reg_port_layout( tar_layout)),
            ("xer" , reg_port_layout( xer_layout)),
            ("srr0", reg_port_layout(srr0_layout)),
            ("srr1", reg_port_layout(srr1_layout)),
        ]
        super().__init__(layout, name=name, src_loc_at=1 + src_loc_at)

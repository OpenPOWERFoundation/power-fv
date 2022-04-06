from amaranth import *


__all__ = ["Interface"]


class Interface(Record):
    """POWER-FV interface.

    The interface between the formal testbench and the processor-under-test.

    Attributes
    ----------
    stb : Signal
        Instruction strobe. Asserted when the processor retires an instruction. Other signals are
        only valid when ``stb`` is asserted.
    """
    def __init__(self, *, name=None, src_loc_at=0):
        layout = [
            ("stb", 1),
        ]
        super().__init__(layout, name=name, src_loc_at=1 + src_loc_at)

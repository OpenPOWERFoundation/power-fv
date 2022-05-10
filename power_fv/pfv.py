from amaranth import *
from amaranth.utils import log2_int


__all__ = ["Interface"]


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
            ("stb",    1),
            ("insn",  64),
            ("order", 64),
            ("intr",   1),
        ]

        # IA

        layout += [
            ("cia", 64),
            ("nia", 64),
        ]

        # GPRs

        def gprf_port(access):
            assert access in ("r", "w", "rw")
            layout = [("index", 5)]
            if "r" in access:
                layout += [
                    ("r_stb",   1),
                    ("r_data", 64),
                ]
            if "w" in access:
                layout += [
                    ("w_stb",   1),
                    ("w_data", 64),
                ]
            return layout

        layout += [
            ("ra", gprf_port("rw")),
            ("rb", gprf_port("r")),
            ("rs", gprf_port("r")),
            ("rt", gprf_port("rw")),
        ]

        # CR

        layout += [
            (f"cr{i}", [
                ("r_stb",  1),
                ("r_data", 4),
                ("w_stb",  1),
                ("w_data", 4),
            ]) for i in range(8)
        ]

        # SPRs

        layout += [
            (spr_name, [
                ("r_stb",   1),
                ("r_data", 64),
                ("w_stb",   1),
                ("w_data", 64),
            ]) for spr_name in (
                "lr",
                "ctr",
                "tar",
                "xer",
            )
        ]

        # Storage

        def mem_port(access, *, depth_log2=64, width=64, granularity=8):
            assert access in ("r", "rw")
            assert depth_log2 in (32, 64)
            assert width in (32, 64)
            assert granularity in (8, 16, 32, 64)
            assert width >= granularity
            granularity_bits = max(1, log2_int(width // granularity))
            layout = [
                ("addr",   depth_log2 - granularity_bits),
                ("r_stb",  granularity_bits),
                ("r_data", width),
            ]
            if "w" in access:
                layout += [
                    ("w_stb",  granularity_bits),
                    ("w_data", width),
                ]
            return layout

        layout += [
            ("insn_mem", mem_port("r")),
            ("data_mem", mem_port("rw")),
        ]

        super().__init__(layout, name=name, src_loc_at=1 + src_loc_at)

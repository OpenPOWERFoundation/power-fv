from pathlib import PurePath
from power_fv.session import PowerFVSession

from .core import MicrowattCore
from .check.storage import *


class MicrowattSession(PowerFVSession, core_cls=MicrowattCore):
    pass


if __name__ == "__main__":
    PROG = "python -m {}".format(PurePath(__file__).parent.name)
    MicrowattSession().main(prog=PROG)

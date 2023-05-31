from pathlib import PurePath
from power_fv.session import PowerFVSession

from .core import DinoflyCore
from .check.storage import *


class DinoflySession(PowerFVSession, core_cls=DinoflyCore):
    pass


if __name__ == "__main__":
    PROG = "python -m {}".format(PurePath(__file__).parent.name)
    DinoflySession().main(prog=PROG)

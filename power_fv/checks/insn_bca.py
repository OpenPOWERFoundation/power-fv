from . import _branch
from .. import insn


__all__ = ["Check"]


class Check(_branch.Check, insn_cls=insn.BCA):
    pass

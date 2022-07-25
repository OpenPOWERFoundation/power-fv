from abc import ABCMeta, abstractmethod

from power_fv import pfv
from power_fv.insn import WordInsn


__all__ = ["InsnSpec"]


class InsnSpec(metaclass=ABCMeta):
    def __init__(self, insn, **kwargs):
        if not isinstance(insn, WordInsn):
            raise TypeError("Instruction must be an instance of WordInsn, not {!r}"
                            .format(insn))

        self.insn = insn
        self.pfv  = pfv.Interface(**kwargs)

    @abstractmethod
    def elaborate(self, platform):
        raise NotImplementedError

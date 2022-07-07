from abc import ABCMeta, abstractmethod

from power_fv.insn import WordInsn


__all__ = ["InsnSpec"]


class InsnSpec(metaclass=ABCMeta):
    def __init__(self, insn):
        self.pfv  = pfv.Interface()
        self.insn = insn

    @property
    def insn(self):
        return self._insn

    @insn.setter
    def insn(self, insn):
        if not isinstance(insn, WordInsn):
            raise TypeError("Instruction must be an instance of WordInsn, not {!r}"
                            .format(insn))
        self._insn = insn

    @abstractmethod
    def elaborate(self, platform):
        raise NotImplementedError

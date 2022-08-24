import inspect

from amaranth import *
from amaranth.lib.coding import Encoder

from power_fv import pfv
from power_fv.check.insn import InsnCheck
from power_fv.check.insn import all as all_checks
from power_fv.reg import *


__all__ = ["Context", "Model"]


def _all_specs(**kwargs):
    for name, obj in inspect.getmembers(all_checks):
        if inspect.isclass(obj) and issubclass(obj, InsnCheck):
            insn = obj.insn_cls(name=name.lower())
            spec = obj.spec_cls(insn, **kwargs)
            yield spec


class Context(Elaboratable):
    def __init__(self, *, mem_size, **kwargs):
        self.gpr  = Array(Signal(64, name=f"G{i}") for i in range(32))
        self.mem  = Array(Signal(64, name=f"M{i}") for i in range(mem_size*8//64))
        self.iar  = Record( _ea_layout)
        self.cr   = Record(  cr_layout)
        self.msr  = Record( msr_layout)
        self.lr   = Record(  lr_layout)
        self.ctr  = Record( ctr_layout)
        self.tar  = Record( tar_layout)
        self.xer  = Record( xer_layout)
        self.srr0 = Record(srr0_layout)
        self.srr1 = Record(srr1_layout)

        self.pfv  = pfv.Interface(**kwargs)

    def connect_outputs(self, spec):
        stmts = []

        stmts += [spec.pfv.cia.eq(self.pfv.cia)]

        for field in ("ra", "rb", "rs", "rt",
                      "mem",
                      "cr", "msr", "lr", "ctr", "tar", "xer", "srr0", "srr1"):
            self_field = getattr(self.pfv, field)
            spec_field = getattr(spec.pfv, field)
            stmts += [spec_field.r_data.eq(self_field.r_data)]

        return stmts

    def connect_inputs(self, spec):
        stmts = []

        stmts += [self.pfv.nia.eq(spec.pfv.nia)]

        for gpr_field in ("ra", "rb", "rs", "rt"):
            self_field = getattr(self.pfv, gpr_field)
            spec_field = getattr(spec.pfv, gpr_field)
            stmts += [
                self_field.index .eq(spec_field.index ),
                self_field.r_stb .eq(spec_field.r_stb ),
                self_field.w_stb .eq(spec_field.w_stb ),
                self_field.w_data.eq(spec_field.w_data),
            ]

        stmts += [
            self.pfv.mem.addr  .eq(spec.pfv.mem.addr),
            self.pfv.mem.r_mask.eq(spec.pfv.mem.r_mask),
            self.pfv.mem.w_mask.eq(spec.pfv.mem.w_mask),
            self.pfv.mem.w_data.eq(spec.pfv.mem.w_data),
        ]

        for reg_field in ("cr", "msr", "lr", "ctr", "tar", "xer", "srr0", "srr1"):
            self_field = getattr(self.pfv, reg_field)
            spec_field = getattr(spec.pfv, reg_field)
            stmts += [
                self_field.r_mask.eq(spec_field.r_mask),
                self_field.w_mask.eq(spec_field.w_mask),
                self_field.w_data.eq(spec_field.w_data),
            ]

        return stmts

    def elaborate(self, platform):
        m = Module()

        m.d.comb += [
            self.pfv.cia.eq(self.iar),

            self.pfv.ra .r_data.eq(self.gpr[self.pfv.ra.index]),
            self.pfv.rb .r_data.eq(self.gpr[self.pfv.rb.index]),
            self.pfv.rs .r_data.eq(self.gpr[self.pfv.rs.index]),
            self.pfv.rt .r_data.eq(self.gpr[self.pfv.rt.index]),
            self.pfv.mem.r_data.eq(self.mem[self.pfv.mem.addr]),

            self.pfv.cr  .r_data.eq(self.cr  ),
            self.pfv.msr .r_data.eq(self.msr ),
            self.pfv.lr  .r_data.eq(self.lr  ),
            self.pfv.ctr .r_data.eq(self.ctr ),
            self.pfv.tar .r_data.eq(self.tar ),
            self.pfv.xer .r_data.eq(self.xer ),
            self.pfv.srr0.r_data.eq(self.srr0),
            self.pfv.srr1.r_data.eq(self.srr1),
        ]

        with m.If(self.pfv.stb):
            m.d.sync += self.iar.eq(self.pfv.nia)

            for gpr_field in ("ra", "rb", "rs", "rt"):
                port = getattr(self.pfv, gpr_field)
                with m.If(port.w_stb):
                    m.d.sync += self.gpr[port.index].eq(port.w_data)

            mem_value = self.mem[self.pfv.mem.addr]
            m.d.sync += mem_value.eq(self.pfv.mem.w_data & self.pfv.mem.w_mask | mem_value & ~self.pfv.mem.w_mask)

            for reg_field in ("cr", "msr", "lr", "ctr", "tar", "xer", "srr0", "srr1"):
                port   = getattr(self.pfv, reg_field)
                shadow = getattr(self,     reg_field)
                m.d.sync += shadow.eq(port.w_data & port.w_mask | shadow & ~port.w_mask)

        return m


class Model(Elaboratable):
    def __init__(self, *, mem_size, **kwargs):
        self.specs = list(_all_specs(**kwargs))
        self.ctx   = Context(mem_size=mem_size)

        self.stb   = Signal()
        self.insn  = Signal(64)
        self.err   = Record([("insn", 1)])

    def elaborate(self, platform):
        m = Module()

        # - `self.insn` is wired to the `pfv.insn` input of each spec. If the spec recognizes an
        #   instruction encoding, it asserts its `pfv.stb` output.
        # - If the instruction is recognized by exactly one spec, then the context is updated
        #   according to its execution side-effects. Otherwise, `self.err.insn` is asserted.

        m.submodules.ctx = self.ctx
        m.submodules.enc = enc = Encoder(width=len(self.specs))

        for j, spec in enumerate(self.specs):
            m.submodules[f"spec_{spec.insn.name}"] = spec
            m.d.comb += [
                spec.pfv.insn.eq(self.insn),
                self.ctx.connect_outputs(spec),
            ]
            m.d.comb += enc.i[j].eq(spec.pfv.stb)

        m.d.comb += [
            self.ctx.pfv.insn.eq(self.insn),
            self.ctx.pfv.stb .eq(self.stb & ~enc.n),
        ]

        with m.Switch(enc.o):
            for j, spec in enumerate(self.specs):
                with m.Case(j):
                    m.d.comb += self.ctx.connect_inputs(spec)

            with m.Default():
                m.d.comb += self.err.insn.eq(1)

        return m

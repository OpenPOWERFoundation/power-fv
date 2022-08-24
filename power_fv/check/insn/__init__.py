from amaranth import *
from amaranth.asserts import *

from power_fv.pfv import mem_port_layout
from power_fv.check import PowerFVCheck, PowerFVCheckMeta
from power_fv.check._timer import Timer


__all__ = ["InsnCheckMeta", "InsnCheck", "InsnTestbench"]


class InsnCheckMeta(PowerFVCheckMeta):
    def __new__(metacls, clsname, bases, namespace, spec_cls=None, insn_cls=None, **kwargs):
        if insn_cls is not None:
            name = ("insn", insn_cls.__name__.lower())
        else:
            name = None

        cls = PowerFVCheckMeta.__new__(metacls, clsname, bases, namespace, name=name, **kwargs)
        if spec_cls is not None:
            cls.spec_cls = spec_cls
        if insn_cls is not None:
            cls.insn_cls = insn_cls
        return cls


class InsnCheck(PowerFVCheck, metaclass=InsnCheckMeta):
    def __init__(self, *, depth, skip, core, **kwargs):
        super().__init__(depth=depth, skip=skip, core=core, **kwargs)
        self.insn = self.insn_cls()
        self.spec = self.spec_cls(self.insn, mem_aligned=self.dut.pfv.mem_aligned, muldiv_altops=self.dut.pfv.muldiv_altops)

    def testbench(self):
        return InsnTestbench(self)


class InsnTestbench(Elaboratable):
    def __init__(self, check):
        if not isinstance(check, InsnCheck):
            raise TypeError("Check must be an instance of InsnCheck, not {!r}"
                            .format(check))
        self.check = check
        self.name  = "{}_tb".format("_".join(check.name))

    def elaborate(self, platform):
        m = Module()

        m.submodules.t_post = t_post = Timer(self.check.depth - 1)
        m.submodules.dut    = dut    = self.check.dut
        m.submodules.spec   = spec   = self.check.spec

        m.d.comb  += [
            spec.pfv.insn .eq(AnyConst(spec.pfv.insn.shape())),
            spec.pfv.order.eq(dut.pfv.order),
            spec.pfv.cia  .eq(dut.pfv.cia),

            Assume(spec.pfv.stb),
        ]

        with m.If(t_post.zero):
            m.d.comb += [
                Assume(dut.pfv.stb),
                Assume(dut.pfv.insn == spec.pfv.insn),
                Assume(~dut.pfv.skip),
                Assert(dut.pfv.intr == spec.pfv.intr),
            ]

        with m.If(t_post.zero):
            m.d.comb += Assert(dut.pfv.nia == spec.pfv.nia)

        m.submodules.ra = ra = _GPRFileTest(self.check, port="ra")
        m.submodules.rb = rb = _GPRFileTest(self.check, port="rb")
        m.submodules.rs = rs = _GPRFileTest(self.check, port="rs")
        m.submodules.rt = rt = _GPRFileTest(self.check, port="rt")

        m.d.comb += [
            spec.pfv.ra.r_data.eq(dut.pfv.ra.r_data),
            spec.pfv.rb.r_data.eq(dut.pfv.rb.r_data),
            spec.pfv.rs.r_data.eq(dut.pfv.rs.r_data),
            spec.pfv.rt.r_data.eq(dut.pfv.rt.r_data),
        ]

        with m.If(t_post.zero):
            m.d.comb += [
                Assert(ra.valid.all()),
                Assert(rb.valid.all()),
                Assert(rs.valid.all()),
                Assert(rt.valid.all()),
            ]

        m.submodules.mem = mem = _MemPortTest(self.check)

        m.d.comb += spec.pfv.mem.r_data.eq(dut.pfv.mem.r_data)

        with m.If(t_post.zero):
            m.d.comb += Assert(mem.valid.all())

        m.submodules.cr   = cr   = _SysRegTest(self.check, reg="cr"  )
        m.submodules.msr  = msr  = _SysRegTest(self.check, reg="msr" )
        m.submodules.lr   = lr   = _SysRegTest(self.check, reg="lr"  )
        m.submodules.ctr  = ctr  = _SysRegTest(self.check, reg="ctr" )
        m.submodules.tar  = tar  = _SysRegTest(self.check, reg="tar" )
        m.submodules.xer  = xer  = _SysRegTest(self.check, reg="xer" )
        m.submodules.srr0 = srr0 = _SysRegTest(self.check, reg="srr0")
        m.submodules.srr1 = srr1 = _SysRegTest(self.check, reg="srr1")

        m.d.comb += [
            spec.pfv.cr  .r_data.eq(dut.pfv.cr  .r_data),
            spec.pfv.msr .r_data.eq(dut.pfv.msr .r_data),
            spec.pfv.lr  .r_data.eq(dut.pfv.lr  .r_data),
            spec.pfv.ctr .r_data.eq(dut.pfv.ctr .r_data),
            spec.pfv.tar .r_data.eq(dut.pfv.tar .r_data),
            spec.pfv.xer .r_data.eq(dut.pfv.xer .r_data),
            spec.pfv.srr0.r_data.eq(dut.pfv.srr0.r_data),
            spec.pfv.srr1.r_data.eq(dut.pfv.srr1.r_data),
        ]

        with m.If(t_post.zero):
            m.d.comb += [
                Assert(cr  .valid.all()),
                Assert(msr .valid.all()),
                Assert(lr  .valid.all()),
                Assert(ctr .valid.all()),
                Assert(tar .valid.all()),
                Assert(xer .valid.all()),
                Assert(srr0.valid.all()),
                Assert(srr1.valid.all()),
            ]

        m.d.comb += Assert(~Past(t_post.zero))

        return m


class _GPRFileTest(Elaboratable):
    def __init__(self, check, *, port):
        self._dut  = getattr(check.dut .pfv, port)
        self._spec = getattr(check.spec.pfv, port)

        self.valid = Record([
            ("read" , [("index", 1), ("r_stb", 1)]),
            ("write", [("index", 1), ("w_stb", 1), ("w_data", 1)]),
        ])

    def elaborate(self, platform):
        m = Module()

        dut  = Record.like(self._dut )
        spec = Record.like(self._spec)

        m.d.comb += [
            dut .eq(self._dut ),
            spec.eq(self._spec),

            # If the spec reads from a GPR, the DUT must read it too.
            self.valid.read.index.eq(spec.r_stb.implies(dut.index == spec.index)),
            self.valid.read.r_stb.eq(spec.r_stb.implies(dut.r_stb)),

            # The DUT and the spec must write the same value to the same GPR.
            self.valid.write.index .eq(spec.w_stb.implies(dut.index == spec.index)),
            self.valid.write.w_stb .eq(spec.w_stb == dut.w_stb),
            self.valid.write.w_data.eq(spec.w_stb.implies(dut.w_data == spec.w_data)),
        ]

        return m


class _MemPortTest(Elaboratable):
    def __init__(self, check):
        self._dut  = check.dut .pfv.mem
        self._spec = check.spec.pfv.mem

        self.valid = Record([
            ("read",  [("addr", 1), ("r_mask", 1)]),
            ("write", [("addr", 1), ("w_mask", 1), ("w_data", 1)]),
        ])

    def elaborate(self, platform):
        m = Module()

        dut  = Record(mem_port_layout())
        spec = Record(mem_port_layout())

        def contains(a, mask, b):
            mask_8 = Cat(Repl(bit, 8) for bit in mask)
            return a & mask_8 == b & mask_8

        m.d.comb += [
            dut .eq(self._dut),
            spec.eq(self._spec),

            # The DUT and the spec must read from the same bits at the same address.
            self.valid.read.addr  .eq(spec.r_mask.any().implies(dut.addr == spec.addr)),
            self.valid.read.r_mask.eq(spec.r_mask == dut.r_mask),

            # The DUT and the spec must write the same value to the same bits at the same address.
            self.valid.write.addr  .eq(spec.w_mask.any().implies(dut.addr == spec.addr)),
            self.valid.write.w_mask.eq(spec.w_mask == dut.w_mask),
            self.valid.write.w_data.eq(contains(dut.w_data, spec.w_mask, spec.w_data)),
        ]

        return m


class _SysRegTest(Elaboratable):
    def __init__(self, check, *, reg):
        self._dut  = getattr(check.dut .pfv, reg)
        self._spec = getattr(check.spec.pfv, reg)

        self.valid = Record([
            ("read" , [("r_mask", 1)]),
            ("write", [("w_mask", 1), ("w_data", 1), ("r_mask", 1), ("r_data", 1)]),
        ])

    def elaborate(self, platform):
        m = Module()

        dut  = Record([
            ("r_mask", len(self._dut.r_mask)),
            ("r_data", len(self._dut.r_data)),
            ("w_mask", len(self._dut.w_mask)),
            ("w_data", len(self._dut.w_data)),
        ])
        spec = Record.like(dut)
        keep = Record([
            ("w_mask", len(self._dut.w_mask)),
        ])

        def contains(a, mask, b=None):
            if b is None:
                b = mask
            return a & mask == b & mask

        m.d.comb += [
            dut .eq(self._dut ),
            spec.eq(self._spec),

            # The DUT and the spec must read from the same bits.
            self.valid.read.r_mask.eq(contains(dut.r_mask, spec.r_mask)),

            # The DUT and the spec must write the same values to the same bits.
            self.valid.write.w_mask.eq(contains(dut.w_mask, spec.w_mask)),
            self.valid.write.w_data.eq(contains(dut.w_data, spec.w_mask, spec.w_data)),

            # The DUT may write to more bits than the spec iff their values are preserved.
            keep.w_mask.eq(dut.w_mask & ~spec.w_mask),
            self.valid.write.r_mask.eq(contains(dut.r_mask, keep.w_mask)),
            self.valid.write.r_data.eq(contains(dut.r_data, keep.w_mask, dut.w_data)),
        ]

        return m

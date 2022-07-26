import json

from abc import ABCMeta, abstractmethod
from pathlib import Path

from power_fv.build import sby


__all__ = ["PowerFVCheck"]


class PowerFVCheckMeta(ABCMeta):
    all_checks = {}

    def __new__(metacls, clsname, bases, namespace, name=None, **kwargs):
        if name is not None:
            if name in metacls.all_checks:
                raise NameError("Check {!r} already exists".format(name))
            namespace["name"] = name

        cls = ABCMeta.__new__(metacls, clsname, bases, namespace, **kwargs)
        if name is not None:
            metacls.all_checks[name] = cls
            cls.name = name
        return cls

    @classmethod
    def find(cls, name, *, sep=":"):
        name = tuple(name.split(sep))
        for check_name, check_cls in cls.all_checks.items():
            assert isinstance(check_name, tuple)
            if len(name) > len(check_name):
                continue
            if name == check_name[:len(name)]:
                yield sep.join(check_name), check_cls


class PowerFVCheck(metaclass=PowerFVCheckMeta):
    @classmethod
    def add_check_arguments(cls, parser):
        parser.add_argument(
            "name", metavar="NAME", type=str, help="name of the check")
        parser.add_argument(
            "--depth", type=int, default=15,
            help="depth of the BMC, in clock cycles (default: %(default)s)")
        parser.add_argument(
            "--skip", type=int, default=None,
            help="skip the specified number of clock cycles (default: DEPTH-1))")
        parser.add_argument(
            "--cover", action="store_true",
            help="generate the shortest trace to reach every Cover() statement")

    @classmethod
    def add_build_arguments(cls, parser):
        parser.add_argument(
            "--build-dir", type=Path, default=Path("./build"),
            help="output directory (default: %(default)s)")
        parser.add_argument(
            "--connect-to", type=json.loads, required=False,
            help="execute the build plan on a remote server using SSH "
                 "(JSON string of arguments passed to paramiko's SSHClient.connect)")

    def __init__(self, *, depth, skip, cover, core, **kwargs):
        self.depth = depth
        self.skip  = skip if skip is not None else depth - 1
        self.cover = bool(cover)
        self.core  = core
        self.dut   = core.wrapper(**kwargs)

    @abstractmethod
    def testbench(self):
        raise NotImplementedError

    def build(self, *, build_dir, connect_to=None, **kwargs):
        platform = sby.SymbiYosysPlatform()
        self.core.add_files(platform, self.dut, **kwargs)

        top = self.testbench()
        build_dir = str(build_dir / top.name)
        overrides = {key: str(value) for key, value in kwargs.items()}
        overrides["depth"] = str(self.depth)
        overrides["skip"] = str(self.skip)
        overrides["mode"] = "cover" if self.cover else "bmc"

        plan = platform.build(top, name=top.name, build_dir=build_dir, do_build=False, **overrides)

        if connect_to is not None:
            products = plan.execute_remote_ssh(connect_to=connect_to, root=build_dir)
        else:
            products = plan.execute_local(build_dir)

        return products

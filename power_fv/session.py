import argparse
import os
import multiprocessing
import sys

from power_fv.build import sby
from power_fv.core import PowerFVCore
from power_fv.check import PowerFVCheck
from power_fv.check.all import *

from pprint import pprint


__all__ = ["PowerFVSession"]


class PowerFVCommandExit(Exception):
    pass

class PowerFVCommandError(Exception):
    pass


class _ArgumentParser(argparse.ArgumentParser):
    def exit(self, status=0, message=None):
        raise PowerFVCommandExit()

    def error(self, message):
        raise PowerFVCommandError()


class PowerFVSession:
    def __init_subclass__(cls, *, core_cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if not issubclass(core_cls, PowerFVCore):
            raise TypeError("Core class must be a subclass of PowerFVCore, not {!r}"
                            .format(core_cls))
        cls.core_cls = core_cls

    def __init__(self, prog=None):
        self.parser     = _ArgumentParser(prog=prog, add_help=False)
        self.subparsers = self.parser.add_subparsers(help="commands")
        self.namespace  = dict()

        self.add_help_subparser()
        self.add_check_subparser()
        self.add_dump_subparser()
        self.add_expand_subparser()
        self.add_build_subparser()
        self.add_exit_subparser()

    def main(self):
        parser = argparse.ArgumentParser(prog=self.parser.prog)
        group  = parser.add_mutually_exclusive_group()
        group.add_argument(
            "-i", dest="interact", action="store_true",
            help="run commands interactively")
        group.add_argument(
            "-c", dest="cmdfile", type=argparse.FileType("r"), default=None,
            help="run commands from CMDFILE")

        args = parser.parse_args()
        try:
            self._loop(args)
        except EOFError:
            pass

    def _loop(self, args):
        if args.cmdfile is None:
            _readline = lambda: input("powerfv> ")
        else:
            _readline = args.cmdfile.readline

        while True:
            line = _readline().rstrip("\n")
            if not line or line.startswith("#"):
                continue
            self._eval(line.split())

    def _eval(self, args=None):
        try:
            args = self.parser.parse_args(args)
            assert hasattr(args, "_cmd")
            cmd = args._cmd
            del args._cmd
            cmd(**vars(args))
        except PowerFVCommandExit:
            pass
        except PowerFVCommandError:
            self.help()

    # Subparsers

    def add_help_subparser(self):
        parser = self.subparsers.add_parser("help", help="show this help message")
        parser.set_defaults(_cmd=self.help)

    def add_check_subparser(self):
        parser = self.subparsers.add_parser("check", help="add checks to this session")
        parser.set_defaults(_cmd=self.check)

        PowerFVCheck .add_check_arguments(parser)
        self.core_cls.add_check_arguments(parser)

    def add_dump_subparser(self):
        parser = self.subparsers.add_parser("dump", help="inspect check parameters")
        parser.set_defaults(_cmd=self.dump)

    def add_expand_subparser(self):
        parser = self.subparsers.add_parser("expand", help="expand check parameters")
        parser.set_defaults(_cmd=self.expand)

    def add_build_subparser(self):
        parser = self.subparsers.add_parser("build", help="execute the build plan")
        parser.set_defaults(_cmd=self.build)

        parser.add_argument(
            "-j", "--jobs", type=int, default=os.cpu_count(),
            help="number of worker processes (default: %(default)s)")

        PowerFVCheck .add_build_arguments(parser)
        self.core_cls.add_build_arguments(parser)

    def add_exit_subparser(self):
        parser = self.subparsers.add_parser("exit", help="exit")
        parser.set_defaults(_cmd=self.exit)

    # Commands

    def help(self, **kwargs):
        self.parser.print_help()

    def check(self, *, name, **kwargs):
        self.namespace[name] = dict(**kwargs)

    def dump(self, **kwargs):
        pprint(self.namespace, sort_dicts=False)

    def expand(self, **kwargs):
        new_namespace = dict()

        for check_name, check_args in self.namespace.items():
            matches = list(PowerFVCheck.find(*check_name.split(":")))
            if not matches:
                raise NameError("Unknown check {!r}".format(check_name))
            for match_name, match_cls in matches:
                new_namespace[":".join(match_name)] = check_args

        self.namespace = new_namespace

    @staticmethod
    def _build_check(core_cls, check_name, check_args, build_args):
        check_cls = PowerFVCheck.all_checks[tuple(check_name.split(":"))]
        core  = core_cls()
        check = check_cls(core=core, **check_args)
        check.build(**build_args)

    def build(self, *, jobs, **kwargs):
        self.expand()

        map_func = PowerFVSession._build_check
        map_args = []

        for check_name, check_args in self.namespace.items():
            map_args.append((self.core_cls, check_name, check_args, kwargs))

        with multiprocessing.Pool(jobs) as pool:
            pool.starmap(map_func, map_args)

    def exit(self, **kwargs):
        print("exiting")
        sys.exit()

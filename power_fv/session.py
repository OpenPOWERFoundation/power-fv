import argparse
import json
import readline
import multiprocessing

from pathlib import Path
from time import strftime, localtime
from operator import itemgetter

from power_fv.build import sby
from power_fv.core import PowerFVCore
from power_fv.check import PowerFVCheck
from power_fv.check.all import *

from pprint import pprint


__all__ = ["PowerFVSession"]


class PowerFVCommandExit(Exception):
    pass


class _ArgumentParser(argparse.ArgumentParser):
    def exit(self, status=0, message=None):
        raise PowerFVCommandExit()


class PowerFVSession:
    def __init_subclass__(cls, *, core_cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if not issubclass(core_cls, PowerFVCore):
            raise TypeError("Core class must be a subclass of PowerFVCore, not {!r}"
                            .format(core_cls))
        cls.core_cls = core_cls

    def __init__(self, prog=None):
        self.parser     = _ArgumentParser(prog="", add_help=False)
        self.subparsers = self.parser.add_subparsers(help="commands")
        self._checks    = dict()

        self.add_help_subparser()
        self.add_check_subparser()
        self.add_dump_subparser()
        self.add_build_subparser()

    def main(self, prog):
        parser = argparse.ArgumentParser(prog=prog)
        group  = parser.add_mutually_exclusive_group()
        group.add_argument(
            "-i", dest="interact", action="store_true",
            help="run commands interactively")
        group.add_argument(
            "-c", dest="cmdfile", type=argparse.FileType("r"), default=None,
            help="run commands from CMDFILE")

        args = parser.parse_args()
        self._loop(args)

    def _loop(self, args):
        while True:
            if args.cmdfile is None:
                try:
                    line = input("powerfv> ")
                except EOFError:
                    break
            else:
                line = args.cmdfile.readline()
                if not line:
                    break

            line = line.strip()
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

    # Subparsers

    def add_help_subparser(self):
        parser = self.subparsers.add_parser("help", help="show this help message")
        parser.set_defaults(_cmd=self.help)

    def add_check_subparser(self):
        parser = self.subparsers.add_parser("check", help="add checks to this session")
        parser.set_defaults(_cmd=self.check)

        PowerFVCheck .add_check_arguments(parser)
        self.core_cls.add_check_arguments(parser)

        parser.add_argument(
            "--exclude", type=str, default="",
            help="exclude a comma-separated list of checks from the selection")

    def add_dump_subparser(self):
        parser = self.subparsers.add_parser("dump", help="inspect check parameters")
        parser.set_defaults(_cmd=self.dump)

    def add_build_subparser(self):
        parser = self.subparsers.add_parser("build", help="execute the build plan")
        parser.set_defaults(_cmd=self.build)

        parser.add_argument(
            "-j", "--jobs", type=int, default=multiprocessing.cpu_count(),
            help="number of worker processes (default: %(default)s)")
        parser.add_argument(
            "--result-dir", type=Path, default=None,
            help="result directory (default: result-$(date +%%Y%%m%%d_%%H%%M%%S))")
        parser.add_argument(
            "--build-dir", type=Path, default=Path("./build"),
            help="output directory (default: %(default)s)")
        parser.add_argument(
            "--connect-to", type=json.loads, required=False,
            help="execute the build plan on a remote server using SSH "
                 "(JSON string of arguments passed to paramiko's SSHClient.connect)")

        self.core_cls.add_build_arguments(parser)

    # Commands

    def help(self, **kwargs):
        self.parser.print_help()

    def check(self, *, name, exclude, **kwargs):
        exclude    = [f"{name}:{subname}" for subname in exclude.split(",")]
        matches    = list(PowerFVCheck.find(name))
        new_checks = dict()

        for check_name, check_cls in matches:
            if check_name in exclude:
                continue
            new_checks[check_name] = dict(**kwargs)

        self._checks.update(new_checks)

    def dump(self, **kwargs):
        pprint(self._checks, sort_dicts=False)

    @staticmethod
    def _build_worker(check_name, plan, root, connect_to):
        if connect_to is not None:
            products = plan.execute_remote_ssh(connect_to=connect_to, root=root)
        else:
            products = plan.execute_local(root)
        return check_name, products

    def build(self, *, jobs, result_dir, build_dir, connect_to, **kwargs):
        worker_inputs  = []
        worker_outputs = None

        # Create the result directory.

        if result_dir is None:
            result_dir = Path("./result-{}".format(strftime("%Y%m%d_%H%M%S", localtime())))
        else:
            result_dir = Path(result_dir)

        Path.mkdir(result_dir, exist_ok=False)

        # Create build plans for scheduled checks.

        def prepare_check(check_name, check_args):
            check_cls = PowerFVCheck.all_checks[tuple(check_name.split(":"))]
            check = check_cls(core=self.core_cls(), **check_args)
            return check.build(do_build=False, **kwargs)

        for check_name, check_args in self._checks.items():
            plan    = prepare_check(check_name, check_args)
            tb_name = "{}_tb".format(check_name.replace(":", "_"))
            tb_root = str(build_dir / tb_name)
            worker_inputs.append((tb_name, plan, tb_root, connect_to))

            # Save an archive of the build files to the result directory.
            plan.archive(result_dir / f"{tb_name}.zip")

        # Execute build plans.

        if connect_to is not None:
            # BuildPlan.execute_remote_ssh() will fail if the parent of its root directory doesn't
            # exist. In our case, checks are built in subdirectories of `build_dir`, so we need to
            # create it beforehand.
            from paramiko import SSHClient
            with SSHClient() as client:
                client.load_system_host_keys()
                client.connect(**connect_to)
                with client.open_sftp() as sftp:
                    try:
                        sftp.mkdir(str(build_dir))
                    except IOError as e:
                        if e.errno:
                            raise e

        with multiprocessing.Pool(jobs) as pool:
            worker_outputs = pool.starmap(PowerFVSession._build_worker, worker_inputs)

        # Write the results.

        def write_result(tb_name, products):
            status = "unknown"
            for filename in ("PASS", "FAIL"):
                try:
                    products.get(f"{tb_name}/{filename}")
                    status = filename.lower()
                except:
                    pass

            with open(result_dir / "status.txt", "a") as statusfile:
                statusfile.write(f"{tb_name} {status}\n")

            if status == "fail":
                with open(result_dir / f"{tb_name}.log", "w") as logfile:
                    logfile.write(products.get(f"{tb_name}/engine_0/logfile.txt", "t"))
                with open(result_dir / f"{tb_name}.vcd", "w") as vcdfile:
                    vcdfile.write(products.get(f"{tb_name}/engine_0/trace.vcd", "t"))

        for tb_name, products in sorted(worker_outputs, key=itemgetter(0)):
            write_result(tb_name, products)

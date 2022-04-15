## Additional prerequisites

- [ghdl](https://github.com/ghdl/ghdl) with the LLVM or GCC backend
- [ghdl-yosys-plugin](https://github.com/ghdl/ghdl-yosys-plugin)


Get Microwatt:

```
git clone git@git.openpower.foundation:jfng/microwatt -b powerfv
```

## Usage

```
# Enter virtual environment
poetry shell

python ./run.py --help

# Exit virtual environment
exit
```

## Example

Let's try the [uniqueness check](https://git.openpower.foundation/cores/power-fv/src/branch/main/power_fv/checks/unique.py) on Microwatt.

First, we find the minimal number of clock cycles needed to observe at least two retired instructions:

```
python run.py unique --mode=cover --post=15
```
```
SBY 15:28:31 [unique_cover_tb] engine_0: ##   0:00:29  Reached cover statement at /home/jf/src/power-fv/power_fv/checks/unique.py:64 ($12) in step 10.
SBY 15:28:31 [unique_cover_tb] engine_0: ##   0:00:29  Writing trace to VCD file: engine_0/trace0.vcd
SBY 15:28:53 [unique_cover_tb] engine_0: ##   0:00:51  Writing trace to Verilog testbench: engine_0/trace0_tb.v
SBY 15:28:53 [unique_cover_tb] engine_0: ##   0:00:51  Writing trace to constraints file: engine_0/trace0.smtc
SBY 15:28:53 [unique_cover_tb] engine_0: ##   0:00:51  Checking cover reachability in step 10..
SBY 15:28:55 [unique_cover_tb] engine_0: ##   0:00:52  Checking cover reachability in step 11..
SBY 15:29:09 [unique_cover_tb] engine_0: ##   0:01:07  Reached cover statement at /home/jf/src/power-fv/power_fv/checks/unique.py:65 ($15) in step 11.
SBY 15:29:09 [unique_cover_tb] engine_0: ##   0:01:07  Writing trace to VCD file: engine_0/trace1.vcd
SBY 15:29:33 [unique_cover_tb] engine_0: ##   0:01:31  Writing trace to Verilog testbench: engine_0/trace1_tb.v
SBY 15:29:33 [unique_cover_tb] engine_0: ##   0:01:31  Writing trace to constraints file: engine_0/trace1.smtc
```

It takes at least 10 clock cycles to observe one retired instruction, and at least 11 for two instructions.

In BMC mode, let's set the pre-condition trigger to 10 cycles, and the post-condition to 12. We should really use higher values to cover a larger state space, but we just want to minimize execution time for this demo.

```
python ./run.py unique --mode=bmc --pre=10 --post=12
```
```
SBY 16:14:26 [unique_bmc_tb] engine_0: starting process "cd unique_bmc_tb; yosys-smtbmc --presat --unroll --noprogress -t 12:13  --append 0 --dump-vcd engine_0/trace.vcd --dump-vlogtb engine_0/trace_tb.v --dump-smtc engine_0/trace.smtc model/design_smt2.smt2"
SBY 16:14:26 [unique_bmc_tb] engine_0: ##   0:00:00  Solver: yices
SBY 16:14:37 [unique_bmc_tb] engine_0: ##   0:00:11  Skipping step 0..
# ...
SBY 16:14:42 [unique_bmc_tb] engine_0: ##   0:00:16  Skipping step 11..
SBY 16:14:43 [unique_bmc_tb] engine_0: ##   0:00:16  Checking assumptions in step 12..
SBY 16:15:12 [unique_bmc_tb] engine_0: ##   0:00:46  Checking assertions in step 12..
SBY 16:15:13 [unique_bmc_tb] engine_0: ##   0:00:46  Status: passed
SBY 16:15:13 [unique_bmc_tb] engine_0: finished (returncode=0)
SBY 16:15:13 [unique_bmc_tb] engine_0: Status returned by engine: pass
SBY 16:15:13 [unique_bmc_tb] summary: Elapsed clock time [H:MM:SS (secs)]: 0:01:07 (67)
SBY 16:15:13 [unique_bmc_tb] summary: Elapsed process time [H:MM:SS (secs)]: 0:01:09 (69)
SBY 16:15:13 [unique_bmc_tb] summary: engine_0 (smtbmc) returned pass
SBY 16:15:13 [unique_bmc_tb] DONE (PASS, rc=0)
```

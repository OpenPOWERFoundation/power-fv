## Additional prerequisites

- [ghdl](https://github.com/ghdl/ghdl) with the LLVM or GCC backend
- [ghdl-yosys-plugin](https://github.com/ghdl/ghdl-yosys-plugin)


```
git clone https://github.com/antonblanchard/microwatt
cd microwatt;
git apply ../0001-WIP.patch
cd -
```

## Usage

```
# Enter virtual environment
poetry shell # Activate virtual environment

python ./run.py --help

# Exit virtual environment
exit
```

## Example

In `run.py`, we check that Microwatt is able to retire one instruction.

Let's find the minimal number of clock cycles to reach this state:

```
python run.py --mode=cover --pre=20 --post=20
```
```
SBY 13:58:23 [smoke_tb] engine_0: ##   0:00:29  Reached cover statement at /home/jf/src/power-fv/cores/microwatt/./run.py:29 ($1) in step 9.
SBY 13:58:23 [smoke_tb] engine_0: ##   0:00:29  Writing trace to VCD file: engine_0/trace0.vcd
```

In BMC mode, the pre-condition will indeed be unreachable at step 8:

```
python ./run.py --mode=bmc --pre=8 --post=8
```
```
SBY 14:08:17 [smoke_tb] engine_0: ##   0:00:14  Checking assumptions in step 8..
SBY 14:08:20 [smoke_tb] engine_0: ##   0:00:17  Assumptions are unsatisfiable!
SBY 14:08:20 [smoke_tb] engine_0: ##   0:00:17  Status: PREUNSAT
SBY 14:08:20 [smoke_tb] engine_0: finished (returncode=1)
SBY 14:08:20 [smoke_tb] engine_0: Status returned by engine: ERROR
```

But it will be reachable at step 9:

```
python ./run.py --mode=bmc --pre=9 --post=9
```
```
SBY 14:11:13 [smoke_tb] engine_0: ##   0:00:15  Checking assumptions in step 9..
SBY 14:11:25 [smoke_tb] engine_0: ##   0:00:27  Checking assertions in step 9..
SBY 14:11:26 [smoke_tb] engine_0: ##   0:00:27  Status: passed
```

## Additional prerequisites

- [ghdl](https://github.com/ghdl/ghdl) with the LLVM or GCC backend
- [ghdl-yosys-plugin](https://github.com/ghdl/ghdl-yosys-plugin)


Get Microwatt:

```
git clone git@git.openpower.foundation:jfng/microwatt -b powerfv
```

## Usage

### Enter/exit the Python virtualenv

```
poetry shell

python ./run.py --help

exit
```

### Run the checks locally

```
python run.py --jobs=$(nproc)
```

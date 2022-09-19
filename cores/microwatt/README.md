## Additional prerequisites

- [ghdl](https://github.com/ghdl/ghdl) with the LLVM or GCC backend
- [ghdl-yosys-plugin](https://github.com/ghdl/ghdl-yosys-plugin)


A version of Microwatt with POWER-FV support is available here:

```
git clone git@git.openpower.foundation:jfng/microwatt -b powerfv src
```

## Usage

### Enter/exit the Python virtualenv

```
poetry shell

python -m microwatt_cli -h

exit
```

### Run commands from a file

```
python -m microwatt_cli -c checks.pfv
```

### Run commands interactively

```
python -m microwatt_cli -i
```

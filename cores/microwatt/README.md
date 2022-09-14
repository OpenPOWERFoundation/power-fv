## Additional prerequisites

- [ghdl](https://github.com/ghdl/ghdl) with the LLVM or GCC backend
- [ghdl-yosys-plugin](https://github.com/ghdl/ghdl-yosys-plugin)


POWER-FV support for Microwatt can be previewed on the following fork:

```
git clone git@git.openpower.foundation:jfng/microwatt -b powerfv src
```

## Usage

### Enter/exit the Python virtualenv

```
poetry shell

python -m microwatt -h

exit
```

### Run commands from a file

```
python -m microwatt -c checks.pfv
```

### Run commands interactively

```
python -m microwatt -i
```

## Additional prerequisites

- [ghdl](https://github.com/ghdl/ghdl) with the LLVM or GCC backend
- [ghdl-yosys-plugin](https://github.com/ghdl/ghdl-yosys-plugin)


Get Microwatt:

```
git clone git@git.openpower.foundation:jfng/microwatt -b powerfv src
```

## Usage

### Enter/exit the Python virtualenv

```
poetry shell

python microwatt.py -h

exit
```

### Run commands from a file

```
python microwatt.py -c checks.pfv
```

### Run commands interactively

```
python microwatt.py -i
```

# POWER-FV – Assertion-based formal verification library for OpenPOWER processors

## Disclaimer

*This project is currently in an experimental state. In particular:
- it has only been tried on the Microwatt CPU
- it assumes an in-order scalar core
- its instruction coverage is limited to the Scalar Fixed-point Compliancy Subset
- the correctness of its own specifications hasn't yet been verified*

## Overview

POWER-FV is a formal verification library that can be used to check the compliance of a processor with the OpenPOWER ISA. It provides an interface to trace the execution of a processor, which is monitored by a testbench and compared against a given specification.

Testbenches and behavioral models are implemented in Python using [Amaranth HDL](https://github.com/amaranth-lang/amaranth), and [SymbiYosys](https://github.com/YosysHQ/sby) for its formal verification flow. Processor cores may use any HDL supported by Yosys.

POWER-FV's design is heavily inspired by the [riscv-formal](https://github.com/YosysHQ/riscv-formal) framework, developed by Claire Wolf (YosysHQ).

## Prerequisites

- Python 3.8+
- [Yosys](https://github.com/YosysHQ/yosys)
- [SymbiYosys (sby)](https://github.com/YosysHQ/sby)

If VHDL support is needed:
- [GHDL](https://github.com/ghdl/ghdl)
- [ghdl-yosys-plugin](https://github.com/ghdl/ghdl-yosys-plugin)

The [OSS CAD Suite](github.com/YosysHQ/oss-cad-suite-build) can provide pre-built binaries of these tools.

## Installation

```python3
pip3 install poetry --user
poetry install
```

## Examples

See the `cores` folder for usage examples.

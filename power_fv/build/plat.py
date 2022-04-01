from amaranth import *
from amaranth.build import *


__all__ = ["SymbiYosysPlatform"]


class SymbiYosysPlatform(TemplatedPlatform):
    """
    Required tools:
        * ``yosys``
        * ``sby``

    Required tools for VHDL support:
        * ``ghdl``
        * ``ghdl-yosys-plugin``

    Available overrides:
        * ``sby_opts``: adds extra options for sby (default: "-f").
        * ``sby_depth``: depth of the bounded model check in sby script.
        * ``sby_skip``: number of skipped time steps in sby script.
        * ``read_verilog_opts``: adds options for the ``read_verilog`` Yosys command.
        * ``ghdl_opts``: adds options for the ``ghdl`` Yosys command.
        * ``ghdl_top``: Top-level unit for the ``ghdl`` Yosys command (default: "top").
        * ``prep_opts``: adds options for the ``prep`` Yosys command (default: "-flatten -nordff").
        * ``chformal``: adds options for the ``chformal`` Yosys command (default: "-early").
        * ``script_before_read``: inserts commands before reading input files in Yosys script.
        * ``script_after_read``: inserts command after reading input files in Yosys script.

    Build products:
        (TODO)
    """
    toolchain = "oss-cad-suite"

    required_tools = [
        "yosys",
        "sby",
    ]
    file_templates = {
        **TemplatedPlatform.build_script_templates,
        "{{name}}.il": r"""
            # {{autogenerated}}
            {{emit_rtlil()}}
        """,
        "{{name}}.sby": r"""
            # {{autogenerated}}
            [options]
            mode bmc
            expect pass,fail
            append 0
            depth {{get_override("sby_depth")}}
            skip {{get_override("sby_skip")}}

            [engines]
            smtbmc

            [files]
            {% for file in platform.iter_files(".il", ".v", ".sv", ".vhdl") -%}
                {{file}}
            {% endfor %}
            {{name}}.il

            [script]
            {% if platform.iter_files(".vhdl")|first is defined -%}
                plugin -i ghdl
            {% endif %}
            {{get_override("script_before_read")|default("# (script_before_read placeholder)")}}
            {% for file in platform.iter_files(".il") -%}
                read_ilang {{file}}
            {% endfor %}
            {% for file in platform.iter_files(".v", ".sv") -%}
                read_verilog {{get_override("read_verilog_opts")|default("-sv")}} {{file}}
            {% endfor %}
            {% if platform.iter_files(".vhdl")|first is defined -%}
                ghdl {{get_override("ghdl_opts")|options}} {{platform.iter_files(".vhdl")|join(" ")}} -e {{get_override("ghdl_top")|default("top")}}
            {% endif %}
            read_ilang {{name}}.il
            delete w:$verilog_initial_trigger
            {{get_override("script_after_read")|default("# (script_after_read placeholder)")}}
            write_ilang debug.il
            prep {{get_override("prep_opts")|default("-flatten -nordff")}} -top {{name}}
            chformal {{get_override("chformal_opts")|default("-early")}}
        """,
    }
    command_templates = [
        r"""
            {{invoke_tool("sby")}}
                --yosys={{invoke_tool("yosys")}}
                {{get_override("sby_opts")|default("-f")}}
                {{name}}.sby
        """,
    ]

    default_clk = "clk"
    default_rst = "rst"
    resources   = [
        Resource("clk", 0, Pins("clk", dir="i"), Clock(1e6)),
        Resource("rst", 0, Pins("rst", dir="i")),
    ]
    connectors  = []

    def create_missing_domain(self, name):
        if name == "sync":
            m = Module()
            clk_i = self.request(self.default_clk).i
            rst_i = self.request(self.default_rst).i
            m.domains.sync = ClockDomain("sync")
            m.d.comb += [
                ClockSignal("sync").eq(clk_i),
                ResetSignal("sync").eq(rst_i),
            ]
            return m

    def build(self, elaboratable, *, sby_depth, sby_skip, **kwargs):
        return super().build(elaboratable, sby_depth=sby_depth, sby_skip=sby_skip, **kwargs)

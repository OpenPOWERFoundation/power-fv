class PowerFVCheck:
    registry = {}
    name     = None

    def __init_subclass__(cls, name):
        if name in cls.registry:
            raise ValueError("Check name {!r} is already registered".format(name))
        cls.registry[name] = cls
        cls.name = name

    def get_testbench(self, dut, *args, **kwargs):
        raise NotImplementedError

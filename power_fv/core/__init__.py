__all__ = ["PowerFVCore"]


class PowerFVCore:
    @classmethod
    def add_check_arguments(cls, parser):
        pass

    @classmethod
    def wrapper(cls, **kwargs):
        raise NotImplementedError

    @classmethod
    def add_build_arguments(cls, parser):
        pass

    @classmethod
    def add_files(cls, platform, wrapper, *, src_dir, **kwargs):
        pass

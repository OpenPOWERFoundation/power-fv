__all__ = ["PowerFVCore"]


class PowerFVCore:
    @classmethod
    def add_check_arguments(cls, parser):
        """Add arguments to the :class:`PowerFVCheck` constructor.

        Parameters
        ----------
        parser : :class:`argparse.ArgumentParser`
            Argument parser passed from :meth:`PowerFVSession.add_check_subparser`.
        """
        pass

    @classmethod
    def wrapper(cls, **kwargs):
        """Instantiate a wrapper of the processor.

        This method is called by the :class:`PowerFVCheck` constructor. The wrapper must have
        a :class:`pfv.Interface` as its ``"pfv"`` attribute.

        Parameters
        ----------
        **kwargs :
            Implementation-specific arguments, defined in :meth:`PowerFVCore.add_check_arguments`.

        Return value
        ------------
        An instance of :class:`amaranth.hdl.ir.Elaboratable`.
        """
        raise NotImplementedError

    @classmethod
    def add_build_arguments(cls, parser):
        """Add arguments to :meth:`PowerFVCheck.build`.

        Parameters
        ----------
        parser : :class:`argparse.ArgumentParser`
            Argument parser passed from :meth:`PowerFVSession.add_build_subparser`.
        """
        pass

    @classmethod
    def add_files(cls, platform, wrapper, **kwargs):
        """Add source files to the build plan.

        Parameters
        ----------
        platform : :class:`sby.SymbiYosysPlatform`
            Target platform. Files can be added with :meth:`amaranth.build.plat.Platform.add_file`.
        wrapper : :class:`Elaboratable`
            Top-level wrapper. See :meth:`PowerFVCore.wrapper`.
        **kwargs :
            Implementation-specific arguments, defined in :meth:`PowerFVCore.add_build_arguments`.
        """
        pass

# !/usr/bin/python
# -*- coding: utf-8 -*-

"""This module provides basic classes used for configuration of other objects."""

from abc import ABC


class BibliometaConfiguration(ABC):
    """The abstract :class:`~bibliometa.configuration.BibliometaConfiguration` defines a configuration object
    for use as basis for Bibliometa classes. Configuration values can be accessed using dot notation (e.g.,
    self.config.name).
    """

    def __init__(self, d, **kwargs):
        """Construct a new :class:`~bibliometa.configuration.BibliometaConfiguration`.

        :param d: Dictionary with configuration key--values pairs. This dictionary will be loaded as
            initial configuration when a new instance of :class:`~bibliometa.configuration.BibliometaConfiguration`
            is constructed.
        :type d: `dict`
        :param kwargs: Arbitrary keyword arguments that are used as configuration keys and values.
            For example, `verbose=True` will make available a configuration key `verbose` with the value
            `True` (i.e., `self.config.verbose` will then return `True`). Configuration can be set during
            initialization as well as after constructing a class instance by calling the `set_config` method.
        """
        self.config = Config(d)
        self.set_config()  # initialize config id
        if kwargs:
            self.set_config(**kwargs)

    def __repr__(self):
        return str(self.config)

    def __str__(self):
        return str(self.config)

    def set_config(self, **kwargs):
        """Set configuration for key-value pairs given in kwargs.

        :return: The calling instance
        :rtype: `bibliometa.configuration.BibliometaConfiguration`
        """
        # update kwargs
        self.config.__dict__.update((k, v) for k, v in kwargs.items())
        # update config_id
        try:
            self.config.__dict__["config_id"] = f"{str(self.config.n)}_" \
                                                f"{str(self.config.e)}_" \
                                                f"{str(self.config.sim)}_" \
                                                f"{str(self.config.t)}"
        except Exception:
            pass

        return self

    def get_config(self, *args):
        """Get configuration. If no args given, the full configuration is returned.
        Otherwise, only the configuration parameters given in args are returned.

        :return: The calling instance if no args given, else a Config object
        :rtype: `bibliometa.configuration.BibliometaConfiguration` or
            `bibliometa.configuration.Config`
        """
        # update config_id
        try:
            self.config.__dict__["config_id"] = f"{str(self.config.n)}_" \
                                                f"{str(self.config.e)}_" \
                                                f"{str(self.config.sim)}_" \
                                                f"{str(self.config.t)}"
        except Exception:
            pass

        if args:
            _cfg = Config({k: self.config.__dict__[k] for k in args})
            return _cfg
        else:
            return self


class Config:
    """The :class:`~bibliometa.configuration.Config` defines a configuration object whose values can be
    accessed using dot notation (e.g., self.config.name).
    """

    def __init__(self, d):
        """Construct a new :class:`~bibliometa.configuration.Config`."""
        self.__dict__.update((k, v) for k, v in d.items())

    def __repr__(self):
        return '\n'.join(str(v) for v in self.__dict__.items())

    def __str__(self):
        return '\n'.join(str(v) for v in self.__dict__.items())

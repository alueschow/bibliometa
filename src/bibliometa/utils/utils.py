#!/usr/bin/python
# -*- coding: utf-8 -*-

"""This module provides utility classes and functions whose usage is not limited to a specific context."""

import json
import os
import sys

from loguru import logger

from bibliometa.config import LOGGING_FILENAME, LOGGING_FORMAT


class MainUtils:
    """The :class:`~bibliometa.utils.utils.MainUtils` provides generic utilities.
    """

    @staticmethod
    def get_file_info(path, suffix=""):
        """Get filename, suffix and file extension from a path.

        :param path: Path to a file
        :type path: `str`
        :param suffix: Suffix that should be added to a filename (optional)
        :type suffix: `str`
        :return: Filename, suffix and file extension
        :rtype: tuple of `str`
        """
        filename, ext = os.path.splitext(path)
        dirname = os.path.dirname(path)
        if not os.path.exists(dirname):
            os.makedirs(dirname)

        s = MainUtils._get_suffix(suffix)

        return filename, s, ext

    @staticmethod
    def _get_suffix(s):
        """Create a filename suffix by adding an underscore before parameter `s`.

        :param s: Suffix that will be preceded by an underscore
        :type s: `str`
        :return: "_" + suffix, if suffix length > 0
        :rtype: `str`
        """
        suffix = ""
        if len(str(s)) > 0:
            suffix = "_" + str(s)
        return suffix

    @staticmethod
    def get_factor(size):
        """Calculate factor to keep max value of progress bar below 100.

        :param size: Number of total values
        :type size: `int`
        :return: Factor by which number of values needs to be divided
        :rtype: `int`
        """
        factor = 1
        while size > 100:
            size = int(size / 10)
            factor *= 10
        return factor


class DictUtils:
    """The :class:`~bibliometa.utils.utils.DictUtils` provides generic utilities."""

    # Default values
    _ENCODING = "utf-8"

    @staticmethod
    def remove_keys(i, o, k, encoding=_ENCODING):
        """Remove all keys from a given dict i (in a JSON file) if not in k and save the remaining dict as JSON in o.

        :param i: Path to input JSON file
        :type i: `str`
        :param o: Path to output JSON file
        :type o: `str`
        :param k: List of keys to be removed
        :type k: `list`
        :param encoding: File encoding
        :type encoding: `str`
        """
        # Set up logging
        logger.remove()
        logger.add(LOGGING_FILENAME, format=LOGGING_FORMAT, level="DEBUG")
        logger.add(sys.stderr, level="INFO")

        with open(i, "r", encoding=encoding) as f:
            in_data = json.load(f)

        out_data = dict()
        for key in in_data.keys():
            if key in list(k):
                out_data[key] = in_data[key]

        with open(o, 'w', encoding=encoding) as f:
            json.dump(out_data, f, indent=4)
            logger.info(f"Keys from {i} were removed (except keys in {k}). New dictionary was written to {o}.")

    @staticmethod
    def remove_empty_entries(d):
        """Remove keys from dict d that have no values.

        :param d: A dictionary
        :type d: `dict`
        :return: Input dictionary without empty entries.
        :rtype: `dict`
        """
        if isinstance(d, dict):
            return {
                k: v
                for k, v in ((k, DictUtils.remove_empty_entries(v)) for k, v in d.items())
                if v
            }
        if isinstance(d, list):
            return [v for v in map(DictUtils.remove_empty_entries, d) if v]
        return d

    @staticmethod
    def merge(a, b):
        """Merge two dictionaries.

        :param a: A dictionary
        :type a: `dict`
        :param b: Another dictionary
        :type b: `dict`
        :raise: KeyError if a key is found in both dictionaries
        :return: Dictionary a merged with b
        :rtype: `dict`
        """
        intersection = set(a.keys()).intersection(set(b.keys()))
        if len(intersection) > 0:
            raise KeyError(f"Duplicate key found: {intersection}.")
        else:
            a.update(b)
            return a

    @staticmethod
    def get_top_keys(d, k):
        """Get keys with highest values from a dictionary.

        :param d: A dictionary
        :type d: `dict`
        :param k: Top k elements that will be returned
        :type k: `int`
        :return: List of tuples (value, key) for top k keys
        :rtype: `list`
        """
        items = sorted(d.items(), reverse=True, key=lambda x: x[1])
        return map(lambda x: x[0], items[:k])

    @staticmethod
    def sort_by_key(d):
        """Sort a dictionary alphabetically by its keys.

        :param d: A dictionary
        :type d: `dict`
        :return: The sorted dictionary
        :rtype: `dict`
        """
        return dict(sorted(d.items(), key=lambda x: str(x[0])))

    @staticmethod
    def save_to_json(d, f, encoding=_ENCODING):
        """Save a dictionary to a JSON file.

        :param d: A dictionary
        :type d: `dict`
        :param f: Path to file
        :type f: `str`
        :param encoding: File encoding
        :type encoding: `str`
        :raise FileNotFoundError: If f does not point to a file
        """
        try:
            with open(f, 'w', encoding=encoding) as file:
                json.dump(d, file, indent=4)
        except FileNotFoundError as e:
            raise e

    @staticmethod
    def read_from_json(f, encoding=_ENCODING):
        """Read a dictionary from a JSON file.

        :param f: Path to file
        :type f: `str`
        :param encoding: File encoding
        :type encoding: `str`
        :return: Dictionary loaded from JSON file
        :rtype: `dict`
        :raise FileNotFoundError: If f does not point to a file
        """
        try:
            with open(f, "r", encoding=encoding) as file:
                return json.load(file)
        except FileNotFoundError as e:
            raise e

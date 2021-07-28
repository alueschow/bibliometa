# !/usr/bin/python
# -*- coding: utf-8 -*-

"""This module provides the :class:`~bibliometa.conversion.CSV2JSON`."""

import json
import re
import sys

import pandas as pd
from json import JSONDecodeError
from loguru import logger
from tqdm.auto import tqdm

from bibliometa.configuration import BibliometaConfiguration
from bibliometa.config import LOGGING_FORMAT, CSV_JSON_CONVERSION_CONFIG_DEFAULT
from bibliometa.utils.utils import MainUtils, DictUtils


class CSV2JSON(BibliometaConfiguration):
    """The :class:`~bibliometa.conversion.CSV2JSON` allows to configure and run the conversion from an
    input CSV file to a JSON file containing only those information from the CSV file needed for further analysis.

    It extends the abstract :class:`~bibliometa.configuration.BibliometaConfiguration` class.
    """

    def __init__(self, **kwargs):
        """Construct a new :class:`~bibliometa.conversion.CSV2JSON`.

        :param kwargs: Arbitrary keyword arguments that are used as configuration keys and values.
            For example, `verbose=True` will make available a configuration key `verbose` with the value
            `True` (i.e., `self.config.verbose` will then return `True`). Configuration can be set during
            initialization as well as after constructing a class instance by calling the `set_config` method
            on a :class:`~bibliometa.conversion.CSV2JSON` object.
        """
        # TODO: Are the super parameters needed? What do they do?
        # super(CSV2JSON, self).__init__(CSV_JSON_CONVERSION_CONFIG_DEFAULT)
        super().__init__(CSV_JSON_CONVERSION_CONFIG_DEFAULT, **kwargs)

    def _update_config(self):
        """Update configuration with class-specific values and check for configuration correctness.

        :raise ValueError: If `self.config.step` <= 0
        """
        if self.config.step <= 0:
            raise ValueError("Wrong configuration! 'step' must be set to a value > 0.")

    def _save_results(self, _dict, file):
        """Save results to JSON file.

        :param _dict: Dictionary containing results
        :type _dict: `dict`
        :param file: Path to JSON file
        :type file: `str`
        """
        try:
            with open(file, "r", encoding=self.config.encoding) as f:
                try:
                    _d = json.load(f)
                except JSONDecodeError:
                    _d = {}
        except FileNotFoundError:
            _d = {}  # file does not exists in fist iteration, skip
        with open(file, "w", encoding=self.config.encoding) as f:
            # merge existing file and new results
            _dict = DictUtils.merge(_dict, _d)
            json.dump(_dict, f, indent=4)
        return _dict

    def start(self):
        """Start the conversion.

        :raises FileNotFoundError: If file given in `self.config.i` can not be found.
        """

        def _is_in(a, b):
            """Check if b is a value in the range of a.

            :param a: A list of `int` values with either length 1 or 2
            :type a: `list`
            :param b: An integer value, e.g., a year
            :type b: `int`
            :return: `True` if b is in the range of a, `False` otherwise
            :rtype: `bool`

            .. important::
                If parameter `a` is of length 1, this function returns `True` if `b` is either the same as
                `a[0]` or within the interval defined by `self.config.interval_lower` and
                `self.config.interval_upper`. For example, if `a[0]` is 1750 and both `self.config.interval_lower`
                and `self.config.interval_upper` are set to 10, this function returns `True` if `b` has a value
                between 1740 and 1760 (inclusive).
            """
            if len(a) == 1:
                return (b - self.config.interval_lower) <= a[0] <= (b + self.config.interval_upper)
            if len(a) == 2:
                return a[0] <= b <= a[1]
            return False

        def _get_era(d):
            # TODO: Rework this code
            """Extract start and end year from a `str` variable.

            :param d: String with year information
            :type d: `str`
            :return: List of years in `d` or None
            :rtype: `list`, `None`
            """
            # TODO: optimize date parsing (preferably already in input data)
            if self.config.subfield_sep + self.config.datefield[1] in d:
                splitted = d.split(self.config.subfield_sep)

                if splitted[0][4] in self.config.date_indicator:
                    # TODO: handle B.C. dates
                    try:
                        if splitted[3].count("a") > 0 and splitted[3].count("b") == 0:  # ignore B.C. dates
                            # remove first character (i.e., subfield indicator)
                            d_split = re.split('[au]', splitted[3][1:])
                            d_split = [int(x) for x in d_split if len(x.strip()) > 0]
                            return d_split
                        else:
                            return None
                    except Exception:
                        return None

        # set up logging
        logger.remove()
        logger.add(self.config.log, format=LOGGING_FORMAT, level=self.config.log_level_file)
        if self.config.verbose:
            logger.add(sys.stderr, level=self.config.log_level_std)
        logger.info("Start conversion from CSV to JSON.")

        # update configuration
        self._update_config()

        # read CSV file
        try:
            with open(self.config.i, "r", encoding=self.config.encoding) as f:
                df = pd.read_csv(f, sep=self.config.csv_sep)
                df.fillna('', inplace=True)
                logger.info(f"Size of import data: {df.shape[0]} data sets")
        except FileNotFoundError as e:
            raise e

        # calculate size of progress bar
        factor = MainUtils.get_factor(df.shape[0])
        progress_bar_max = int(df.shape[0] / factor)

        # start row-by-row conversion for each defined year
        # TODO: Allow for a conversion that is not based on single years (e.g., using the full input data set)
        # TODO: Log that the conversion process for year XY starts
        year = self.config.from_
        while year <= self.config.to:
            # year is added as suffix to the path from self.config.o
            filename, suffix, ext = MainUtils.get_file_info(self.config.o, suffix=year)
            file = filename + suffix + ext
            with tqdm(total=progress_bar_max) as progressbar:
                _dict = {}  # results dictionary
                for index, row in df.iterrows():
                    row_id = row['id']
                    _dict[row_id] = {}
                    # iterate over all fields defined in configuration
                    for fields in self.config.fields:
                        content_field = fields["content"][0]
                        content_subfield = fields["content"][1]
                        # get dates from row
                        dates = [_get_era(d.strip()) for d in str(row[
                                                                      self.config.datefield[0]
                                                                      + self.config.subfield_sep
                                                                      + self.config.datefield[1]
                                                                      ]).split(self.config.split_char)
                                 if len(d.strip()) > 0 and _get_era(d.strip())]

                        # check if at least one date is in desired period/year
                        # if yes, get content and add to results dictionary where appropriate
                        for date in dates:
                            if _is_in(date, year):
                                contents = [c.strip() for c in str(row[
                                                                       content_field
                                                                       + self.config.subfield_sep
                                                                       + content_subfield
                                                                       ]).split(self.config.split_char)
                                            if len(c.strip()) > 0]
                                types = [t.strip() for t in str(row[
                                                                    fields["type"][0]
                                                                    + self.config.subfield_sep
                                                                    + fields["type"][1]
                                                                    ]).split(self.config.split_char)
                                         if len(t.strip()) > 0]

                                # get only content from desired type(s)
                                content = [c for (c, t) in zip(contents, types) if t in fields["categories"]]

                                if len(content) > 0:
                                    _dict[row_id][content_field] = {content_subfield: content}
                                    break

                    # after each row, remove empty values from dictionary
                    _dict = {k: v for k, v in _dict.items() if len(v.keys()) > 0}

                    # update progress bar and save results dictionary
                    if index % factor == 0 and int(index / factor) != progress_bar_max:
                        progressbar.update()
                        self._save_results(_dict, file)
                        _dict = {}

                # at this point, all rows were processed
                # close progress bar and save final results dictionary as JSON
                progressbar.close()
                _dict = self._save_results(_dict, file)

                logger.info(f"Size of output data for year {year} "
                            f"(+{self.config.interval_lower}/-{self.config.interval_upper} years): "
                            f"{len(_dict.keys())} data sets "
                            f"({round(len(_dict.keys()) * 100 / df.shape[0], 2)} %) "
                            )

                # increase while loop condition
                year = year + self.config.step

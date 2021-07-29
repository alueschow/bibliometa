# !/usr/bin/python
# -*- coding: utf-8 -*-

"""This module provides a class for converting a JSON file to an edge list."""

import sys

from loguru import logger
from tqdm.auto import tqdm

from bibliometa.configuration import BibliometaConfiguration
from bibliometa.config import LOGGING_FORMAT, JSON_EDGELIST_CONVERSION_CONFIG_DEFAULT
from bibliometa.graph.similarity import Similarity
from bibliometa.utils.archives import tar
from bibliometa.utils.utils import MainUtils, DictUtils


class JSON2EdgeList(BibliometaConfiguration):
    """The :class:`~bibliometa.graph.conversion.JSON2EdgeList` allows to configure and run the conversion from an
    input JSON file to an edge list graph representation.

    It extends the abstract :class:`~bibliometa.configuration.BibliometaConfiguration` class.
    """

    def __init__(self, **kwargs):
        """Construct a new :class:`~bibliometa.graph.conversion.JSON2EdgeList`.

        :param kwargs: Arbitrary keyword arguments that are used as configuration keys and values.
            For example, `verbose=True` will make available a configuration key `verbose` with the value
            `True` (i.e., `self.config.verbose` will then return `True`). Configuration can be set during
            initialization as well as after constructing a class instance by calling the `set_config` method
            on a :class:`~bibliometa.graph.conversion.JSON2EdgeList` object.
        """
        super().__init__(JSON_EDGELIST_CONVERSION_CONFIG_DEFAULT, **kwargs)

    def start(self, n=5):
        """Start the conversion.

        :param n: Number that indicates how many elements will be shown in data preview when verbose == True
        :type n: `int`
        :raises FileNotFoundError: If file given in `self.config.i` can not be found.
        """
        # set up logging
        logger.remove()
        logger.add(self.config.log, format=LOGGING_FORMAT, level=self.config.log_level_file)
        if self.config.verbose:
            logger.add(sys.stderr, level=self.config.log_level_std)
        logger.info("Start JSON2EdgeList conversion.")

        # read JSON file
        try:
            data = DictUtils.read_from_json(self.config.i, encoding=self.config.encoding)
        except FileNotFoundError as e:
            raise e

        # Create graph corpus if necessary
        if self.config.create_corpus:
            corpus = GraphCorpus.create(data, self.config)
        else:
            # load graph corpus from existing file
            try:
                filename, suffix, ext = MainUtils.get_file_info(self.config.corpus, suffix=self.config.name)
                corpus = DictUtils.read_from_json(filename + suffix + ext, encoding=self.config.encoding)
            except FileNotFoundError as e:
                raise FileNotFoundError(
                    f"""{e}. You may have to create a corpus first (set 'create_corpus' in configuration to True)."""
                )

        # show n entries from corpus if verbose == True
        if self.config.verbose:
            print(dict(list(corpus.items())[:n]))

        # Calculate similarity
        logger.info("Start similarity calculation.")
        Similarity.calculate(corpus, self.config)
        logger.info("Similarity calculation ended.")

        # put similarity files into tar.gz archive
        if self.config.archive:
            if self.config.archive_ext == ".tar.gz":
                logger.info(f"Putting similarity files into '{self.config.archive_ext}' archives.")
                filename, suffix, ext = MainUtils.get_file_info(self.config.o, suffix=self.config.name)
                tar(
                    filename + suffix + ext,
                    filename + suffix + self.config.archive_ext
                )
                logger.info(f"Similarity '{self.config.archive_ext}' archive can now be found in "
                            f"{filename + suffix + self.config.archive_ext}."
                            )
            else:
                raise ValueError("Archive extensions other than 'tar.gz' are not implemented yet!")


class GraphCorpus:
    """The :class:`~bibliometa.graph.conversion.GraphCorpus` provides a static function to create a graph corpus
    in JSON format. It is needed in the conversion from JSON to an edge list representation.
    """

    @staticmethod
    def create(data, config):
        """Create a graph corpus.

        :param data: Dictionary containing data  sets
        :type data: `dict`
        :param config: Configuration object
        :type config: `bibliometa.configuration.Config`
        :return: Graph corpus
        :rtype: `dict`
        :raise FileNotFoundError: If graph corpus can not be written to file
        """

        def _create_swap():
            """Create a corpus where unique values from the input data become the keys
            and keys from the input data become the values.

            :return: Graph corpus
            :rtype: `dict`
            """
            _corpus = {}
            _unique_values = []

            # Collect unique data values as corpus keys,
            # consider only those fields that are defined in the configuration
            for key in data.keys():
                for field, subfield in config.fields:
                    if field in data[key].keys():
                        if subfield in data[key][field].keys():
                            values = data[key][field][subfield]
                            for value in values:
                                if len(value.strip()) > 0:
                                    _unique_values.append(value.strip())
            _unique_values = list(set(_unique_values))

            # Fill graph corpus
            with tqdm(total=len(_unique_values)) as progressbar:
                for value in _unique_values:
                    _corpus[value] = []
                    for key in data.keys():
                        for field, subfield in config.fields:
                            if field in data[key].keys():
                                if subfield in data[key][field].keys():
                                    sf_values = data[key][field][subfield]
                                    for sf_value in sf_values:
                                        if sf_value.strip() == value:
                                            _corpus[value].append(key)
                                            _corpus[value] = list(set(_corpus[value]))
                    progressbar.update()

            logger.debug(f"Corpus keys: {len(_corpus.keys())}")

            progressbar.close()

            return _corpus

        def _create_original():
            """Create a corpus where keys and values from the input data also become keys
            and values in the graph corpus.

            :return: Graph corpus
            :rtype: `dict`
            """
            _corpus = {}
            _unique_values = []

            # use keys from import file as corpus keys
            for key in data.keys():
                _corpus[key] = []
                for field, subfield in config.fields:
                    if field in data[key].keys():
                        if subfield in data[key][field].keys():
                            values = data[key][field][subfield]
                            for value in values:
                                if len(value.strip()) > 0:
                                    _unique_values.append(value.strip())
                                    _corpus[key].append(value.strip())
                                    _corpus[key] = list(set(_corpus[key]))

                # remove empty dictionary items
                if len(_corpus[key]) == 0:
                    del _corpus[key]

            _unique_values = set(_unique_values)
            logger.debug(f"Corpus keys: {len(_corpus.keys())}")
            logger.debug(f"Unique values: {len(_unique_values)}")

            return _corpus

        # class action starts here
        corpus = _create_swap() if config.swap else _create_original()

        # Write corpus to file
        try:
            filename, suffix, ext = MainUtils.get_file_info(config.corpus, suffix=config.name)
            DictUtils.save_to_json(corpus, filename + suffix + ext, encoding=config.encoding)
            logger.info(f"Corpus written to file {filename + suffix + ext}.")
        except FileNotFoundError as e:
            raise e

        return corpus

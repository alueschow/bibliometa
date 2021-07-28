# !/usr/bin/python
# -*- coding: utf-8 -*-

"""This module provides a class for similarity function definitions and similarity calculations."""

import csv
import itertools
from collections import OrderedDict

from loguru import logger
from scipy.special import binom
from tqdm.auto import tqdm

from bibliometa.utils.utils import MainUtils


class Similarity:
    """The :class:`~bibliometa.graph.similarity.Similarity` provides functions to define and calculate
    different types of similarity.
    """

    @staticmethod
    def calculate(corpus, config):
        """Calculate similarity between data sets.

        :param corpus: Graph corpus that contains the data on which similarity calculation will be based
        :type corpus: `dict`
        :param config: Configuration object
        :type config: `bibliometa.configuration.Config`
        """
        results = []
        record_count = 0

        # calculate size of progress bar
        combinations = binom(len(list(corpus.keys())), 2)
        factor = MainUtils.get_factor(combinations)
        progress_max_value = int(combinations / factor)

        # Calculate similarity for each node--node pair in the corpus
        with tqdm(total=progress_max_value) as progressbar:
            for key1, key2 in itertools.combinations(corpus, 2):
                similarity_dict = Similarity._get_similarity(
                    set(corpus[key1]), set(corpus[key2]), config.sim_functions
                )
                # consider this combination only if at least one similarity function returned a value > 0
                if any(x > 0 for x in list(similarity_dict.values())):
                    _tmp_results = [record_count, key1, key2] + [similarity_dict[s] for s in similarity_dict.keys()]
                    results.append(_tmp_results)

                # get progress
                record_count += 1
                if record_count % factor == 0:
                    progressbar.update()

            progressbar.close()

            # TODO: implement chunks for larger data sets? If yes, also implement saving temporary results/progress
            progress = 1.0
            Similarity._write_results_and_progress(results, config, progress)

    @staticmethod
    def _get_similarity(a, b, sim_functions):
        """Get similarity between a and b for different similarity functions. Get arguments that need to
        be passed to similarity functions from configuration, where necessary.

        :param a: Set of values for item a
        :type a: `set`
        :param b: Set of values for item b
        :type b: `set`
        :param sim_functions: Similarity functions
        :type sim_functions: `list` of `dict`
        :return: OrderedDict with similarity functions as keys and their values
        :rtype: `OrderedDict`
        """
        d = OrderedDict()

        # default arguments for similarity functions
        f = None  # function that calculates similarity value
        t = 0  # threshold for similarity value

        # iterate over similarity functions, get arguments and call the function
        for sim_func in sim_functions:
            if "args" in sim_func.keys():
                if "f" in sim_func["args"]:
                    f = sim_func["args"]["f"]
                if "t" in sim_func["args"]:
                    t = sim_func["args"]["t"]

            d[sim_func["name"]] = sim_func["function"](
                a, b, f, t
            )

        return d

    @staticmethod
    def _write_results_and_progress(results, config, progress):
        """Write (temporary) results and progress to the appropriate files.

        :param results: List of similarity results for node-node pairs
        :type results: `list`
        :param config: Configuration object
        :type config: `bibliometa.configuration.Config`
        :param progress: Progress values
        :type progress: `float`
        """
        filename, suffix, ext = MainUtils.get_file_info(config.o, suffix=config.name)
        with open(filename + suffix + ext, "w", newline="") as f:
            wr = csv.writer(f, delimiter=config.csv_sep)
            wr.writerows(results)
        logger.info(f"(Temporary) Results written to file {filename + suffix + ext}.")

        filename, suffix, ext = MainUtils.get_file_info(config.log, suffix=config.name)
        with open(filename + suffix + "_progress" + ext, "w", newline="") as f:
            f.write(str(progress))
        logger.info(f"Progress written to file {filename + suffix + ext}.")

    class Functions:
        """This class contains predefined similarity functions.
        """

        @staticmethod
        def mint(a, b, f, t=0):
            """a and b are considered similar if the size of their intersection is greater than or
            equal to t.

            :param a: Set of values for item a
            :type a: `set`
            :param b: Set of values for item b
            :type b: `set`
            :param f: This value (or the result of this function) will be returned if similarity between
                a and b >= t
            :type f: function or `int`
            :param t: Threshold
            :type t: `int`
            :return: Similarity value
            :rtype: `float` or `int`
            :raise ValueError: If f is neither a function nor an `int` or `float`
            """
            if callable(f):
                return f(a, b) if len(list(a.intersection(b))) >= t else 0
            elif isinstance(f, int) or isinstance(f, float):
                return f if len(list(a.intersection(b))) >= t else 0
            else:
                raise ValueError("Parameter 'f' is neither function nor int or float!")

        @staticmethod
        def jaccard(a, b, f, t=0):
            """The Jaccard Index. a and b are considered similar if the size of their intersection divided by their
            union is greater than or equal to t.

            :param a: Set of values for item a
            :type a: `set`
            :param b: Set of values for item b
            :type b: `set`
            :param f: This value (or the result of this function) will be returned if similarity between
                a and b >= t
            :type f: function or `int`
            :param t: Threshold
            :type t: `int`
            :return: Similarity value
            :rtype: `float` or `int`
            :raise ValueError: If f is neither a function nor an `int` or `float`
            """
            intersection = len(list(a.intersection(b)))
            union = (len(list(a)) + len(list(b))) - intersection
            jacc = float(intersection) / union
            if callable(f):
                return f(jacc) if union > t else 0
            elif isinstance(f, int) or isinstance(f, float):
                return jacc if union > t else 0
            else:
                raise ValueError("Parameter 'f' is neither function nor int or float!")

        @staticmethod
        def overlap(a, b, f, t=0):
            """The overlap score. a and b are considered similar if the size of their intersection divided by the
            minimum set length of a and b is greater than or equal to t.

            :param a: Set of values for item a
            :type a: `set`
            :param b: Set of values for item b
            :type b: `set`
            :param f: This value (or the result of this function) will be returned if similarity between
                a and b >= t
            :type f: function or `int`
            :param t: Threshold
            :type t: `int`
            :return: Similarity value
            :rtype: `float` or `int`
            :raise ValueError: If f is neither a function nor an `int` or `float`
            """
            intersection = len(list(a.intersection(b)))
            ovlp = float(intersection) / min(len(list(a)), len(list(b)))
            if callable(f):
                return f(ovlp) if min(len(list(a)), len(list(b))) > t else 0
            elif isinstance(f, int) or isinstance(f, float):
                return ovlp if min(len(list(a)), len(list(b))) > t else 0
            else:
                raise ValueError("Parameter 'f' is neither function nor int or float!")

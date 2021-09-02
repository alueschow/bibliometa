# !/usr/bin/python
# -*- coding: utf-8 -*-

"""This module provides functions for analysing graphs."""

import collections
import os
import sys

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from loguru import logger
from tqdm.auto import tqdm

from bibliometa.config import LOGGING_FORMAT, GRAPH_ANALYSIS_CONFIG_DEFAULT
from bibliometa.configuration import BibliometaConfiguration
from bibliometa.graph.utils import load_graph, save_file
from bibliometa.utils.utils import DictUtils, MainUtils


class GraphAnalysis(BibliometaConfiguration):
    """The :class:`~bibliometa.graph.analysis.GraphAnalysis` allows to configure and run the graph analysis of
    a graph corpus.

    It extends the abstract :class:`~bibliometa.configuration.BibliometaConfiguration` class.
    """

    def __init__(self, **kwargs):
        """Construct a new :class:`~bibliometa.graph.analysis.GraphAnalysis`.

        :param **kwargs: Arbitrary keyword arguments that are used as configuration keys and values.
            For example, `verbose=True` will make available a configuration key `verbose` with the value
            `True` (i.e., `self.config.verbose` will then return `True`). Configuration can be set during
            initialization as well as after constructing a class instance by calling the `set_config` method
            on a :class:`~bibliometa.graph.analysis.GraphAnalysis` object.
        """
        super().__init__(GRAPH_ANALYSIS_CONFIG_DEFAULT, **kwargs)

    def _update_config(self):
        """Update configuration with class-specific values and check for configuration correctness.

        :raise ValueError: If no `self.config.sim_functions` are given.
        """
        self.set_config(config_id=f"{self.config.n}_{self.config.e}_{self.config.sim}_{self.config.t}")

        if len(self.config.sim_functions) == 0 or len(self.config.sim) == 0:
            raise ValueError("No similarity function(s) given! At least one similarity function must be provided.")

        try:
            if not os.path.exists(os.path.dirname(self.config.img)):
                os.makedirs(os.path.dirname(self.config.img))
        except Exception:
            pass
        try:
            if not os.path.exists(os.path.dirname(self.config.graphml)):
                os.makedirs(os.path.dirname(self.config.graphml))
        except Exception:
            pass

        if self.config.create_graphml and not self.config.graphml:
            raise ValueError("Configuration parameter 'graphml' must be set if parameter 'create' is set to True,"
                             "otherwise no GraphML file can be created!")

        self._results = []

        # Load graph from GraphML file, if existent; otherwise create GraphML file from similarity file
        self.g = load_graph(self.config)

    def start(self):
        """Start the analysis."""
        # Set up logging
        filename, suffix, ext = MainUtils.get_file_info(
            self.config.log, suffix=self.config.name
        )
        logger.remove()
        logger.add(filename + suffix + ext, format=LOGGING_FORMAT, level=self.config.log_level_file)
        if self.config.verbose:
            logger.add(sys.stderr, level=self.config.log_level_std)

        self._update_config()
        logger.info(f"Start graph analysis for configuration {self.config.config_id}.")

        filename, suffix, ext = MainUtils.get_file_info(
            self.config.o, suffix=self.config.name
        )

        with tqdm(total=len(self.config.types)) as progressbar:
            # Calculate basic metrics
            if "node_count" in self.config.types:
                nodes = self._node_count()
                nodes_str = f"Nodes: {nodes}"
                self._results.append(nodes_str)
                logger.info(nodes_str)

                save_file(filename + suffix + ext, self._results)
                progressbar.update()

            if "edge_count" in self.config.types:
                edges = self._edge_count()
                edges_str = f"Edges: {edges}"
                self._results.append(edges_str)
                logger.info(edges_str)

                save_file(filename + suffix + ext, self._results)
                progressbar.update()

            if "component_count" in self.config.types:
                components = self._component_count()
                components_str = f"Components: {components}"
                self._results.append(components_str)
                logger.info(components_str)

                save_file(filename + suffix + ext, self._results)
                progressbar.update()

            if "max_component" in self.config.types:
                max_component = self._max_component()
                max_component_str = f"Size of largest component: {max_component}"
                self._results.append(max_component_str)
                logger.info(max_component_str)

                save_file(filename + suffix + ext, self._results)
                progressbar.update()

            if "avg_degree" in self.config.types:
                avg_degree = self._avg_degree()
                avg_degree_str = f"Average Degree: {avg_degree}"
                self._results.append(avg_degree_str)
                logger.info(avg_degree_str)

                save_file(filename + suffix + ext, self._results)
                progressbar.update()

            # Plot degree distribution
            if "degree_distribution" in self.config.types:
                logger.info("Start plotting degree distributions.")
                self._degree_distribution(weight='weight')
                logger.info("Finished plotting degree distributions.")

                save_file(filename + suffix + ext, self._results)
                progressbar.update()

            # Top degree centrality nodes
            if "top_dc_nodes" in self.config.types:
                logger.info("Getting top Degree Centrality nodes.")
                self._top_dc_nodes()
                save_file(filename + suffix + ext, self._results)
                progressbar.update()

            # Degree Centrality distributions
            if "degree_centrality_distribution" in self.config.types:
                logger.info("Calculating Degree Centrality distributions.")
                dc_values = self._degree_centrality()
                avg_dc_str = f"Average degree centrality: {np.mean(list(dc_values))}"
                self._results.append(avg_dc_str)
                logger.info(avg_dc_str)
                min_dc_str = f"Minimum degree centrality: {np.min(list(dc_values))}"
                self._results.append(min_dc_str)
                logger.info(min_dc_str)
                max_dc_str = f"Maximum degree centrality: {np.max(list(dc_values))}"
                self._results.append(max_dc_str)
                logger.info(max_dc_str)
                stdev_dc_str = f"Stdev degree centrality: {np.std(list(dc_values))}"
                self._results.append(stdev_dc_str)
                logger.info(stdev_dc_str)

                save_file(filename + suffix + ext, self._results)
                progressbar.update()

            # Local cluster coefficient
            if "local_cluster_coefficient" in self.config.types:
                logger.info("Calculating local cluster coefficients.")
                if self.config.weighted:
                    lcc_values = self._local_cluster_coefficient(weight='weight')
                else:
                    lcc_values = self._local_cluster_coefficient()
                avg_lcc_str = f"Average local cluster coefficient: {np.mean(list(lcc_values))}"
                self._results.append(avg_lcc_str)
                logger.info(avg_lcc_str)
                min_lcc_str = f"Minimum local cluster coefficient: {np.min(list(lcc_values))}"
                self._results.append(min_lcc_str)
                logger.info(min_lcc_str)
                max_lcc_str = f"Maximum local cluster coefficient: {np.max(list(lcc_values))}"
                self._results.append(max_lcc_str)
                logger.info(max_lcc_str)
                stdev_lcc_str = f"Stdev local cluster coefficient: {np.std(list(lcc_values))}"
                self._results.append(stdev_lcc_str)
                logger.info(stdev_lcc_str)

                save_file(filename + suffix + ext, self._results)
                progressbar.update()

            # Density
            if "density" in self.config.types:
                density_str = f"Density: {self._density()}"
                self._results.append(density_str)
                logger.info(density_str)

                save_file(filename + suffix + ext, self._results)
                progressbar.update()

            # Diameter
            if "diameter" in self.config.types:
                diameter_str = f"Diameter: {self._diameter()}"
                self._results.append(diameter_str)
                logger.info(diameter_str)

                save_file(filename + suffix + ext, self._results)
                progressbar.update()

            # Average shortest path
            if "average_shortest_path" in self.config.types:
                avg_shortest_path_str = f"Average shortest path: {self._avg_shortest_path()}"
                self._results.append(avg_shortest_path_str)
                logger.info(avg_shortest_path_str)

                save_file(filename + suffix + ext, self._results)
                progressbar.update()

            # Global clustering coefficient
            if "global_clustering_coefficient" in self.config.types:
                global_cc_str = f"Global clustering coefficient: {self._global_cluster_coefficient()}"
                self._results.append(global_cc_str)
                logger.info(global_cc_str)

                save_file(filename + suffix + ext, self._results)
                progressbar.update()

            # Graph clique number
            if "graph_clique_number" in self.config.types:
                clique_number_str = f"Graph clique number: {self._clique_number()}"
                self._results.append(clique_number_str)
                logger.info(clique_number_str)

                save_file(filename + suffix + ext, self._results)
                progressbar.update()

            # Graph number of cliques
            if "number_of_cliques" in self.config.types:
                nr_of_cliques_str = f"Number of cliques: {self._nr_of_cliques()}"
                self._results.append(nr_of_cliques_str)
                logger.info(nr_of_cliques_str)

                save_file(filename + suffix + ext, self._results)
                progressbar.update()

    def _node_count(self):
        """Return node count.

        :return: Node count
        :rtype: `int`
        """
        return len(list(self.g.nodes))

    def _edge_count(self):
        """Return edge count.

        :return: Edge count
        :rtype: `int`
        """
        return len(list(self.g.edges))

    def _component_count(self):
        """Return component count.

        :return: Component count
        :rtype: `int`
        """
        return len(list(nx.connected_components(self.g)))

    def _max_component(self, return_component=False):
        """Return largest component size or largest component.

        :param return_component: Whether component should be returned instead of only the size
        :type return_component: `bool`
        :return: Largest component size or largest component itself
        :rtype: `set` or `int`
        """
        if return_component:
            return max(nx.connected_components(self.g), key=len)
        else:
            return len(list(max(nx.connected_components(self.g), key=len)))

    def _avg_degree(self):
        """Return average node degree.

        :return: Average node degree
        :rtype: `float`
        """
        return float(self.g.size()) / self.g.order()

    def _degree_distribution(self, weight=None):
        """Calculate, plot and save degree distributions.

        :param weight: Edge attribute that contains weight information
        :type weight: `str`
        """
        degreeview = self.g.degree(weight=weight)
        degree_sequence = sorted([d for n, d in degreeview], reverse=True)
        degree_count = collections.Counter(degree_sequence)
        deg, cnt = zip(*degree_count.items())
        deg = [int(x) for x in deg]  # convert to integer values

        plt.rc('axes', titlesize=14)
        plt.rc('axes', labelsize=14)
        plt.rc('xtick', labelsize=14)
        plt.rc('ytick', labelsize=14)

        # Relative density
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.hist(degree_sequence, bins=range(0, int(max(degree_sequence))),
                density=True, histtype='bar', rwidth=0.8, color="orange")
        ax.set_yscale('log')
        ax.set_xscale('log')
        ax.set_xlabel('Knotengrad')
        ax.set_ylabel('Relative Dichte')
        filename, suffix, ext = MainUtils.get_file_info(
            self.config.img + self.config.config_id + "_degree_density.png", suffix=self.config.name
        )
        plt.savefig(filename + suffix + ext)
        if self.config.verbose:
            plt.show()
        plt.close()

        # Histogram
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(deg, cnt, color="orange")
        ax.set_ylabel("Anzahl an Knoten")
        ax.set_xlabel("Knotengrad")
        ax.set_xticks([d + 0.4 for d in deg])
        ax.set_xticklabels(deg)
        filename, suffix, ext = MainUtils.get_file_info(
            self.config.img + self.config.config_id + "_degree_histogram.png", suffix=self.config.name
        )
        plt.savefig(filename + suffix + ext)
        if self.config.verbose:
            plt.show()
        plt.close()

        # Degree distribution logarithmic scale
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.grid(True)
        ax.set_xlabel('Knotengrad')
        ax.set_ylabel('Anzahl an Knoten')
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.plot(deg, cnt, 'o', color="orange")
        filename, suffix, ext = MainUtils.get_file_info(
            self.config.img + self.config.config_id + "_degree_distribution_log-log.png", suffix=self.config.name
        )
        plt.savefig(filename + suffix + ext)
        if self.config.verbose:
            plt.show()
        plt.close()

        # Degree distribution (normal scale)
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.grid(True)
        # Count value occurrence
        _values = {}
        for d in degreeview:
            if d[1] in _values.keys():
                _values[d[1]] += 1
            else:
                _values[d[1]] = 1
        # Create histogram
        values = sorted(set(_values.keys()))
        hist = [_values[x] for x in values]
        ax.plot(values, hist, 'o', color='orange')
        ax.set_xlabel('Knotengrad')
        ax.set_ylabel('Anzahl an Knoten')
        filename, suffix, ext = MainUtils.get_file_info(
            self.config.img + self.config.config_id + "_degree_distribution.png", suffix=self.config.name
        )
        plt.savefig(filename + suffix + ext)
        if self.config.verbose:
            plt.show()
        plt.close()

    def _top_dc_nodes(self, k=5):
        """"Get top k Degree Centrality nodes.

        :param k: Number of nodes that will be collected
        :type k: `int`
        """
        top_dc = DictUtils.get_top_keys(nx.degree_centrality(self.g), 100)
        nodes = []

        count = 0
        for node_id in top_dc:
            logger.info(f"Top {count} Degree Centrality node: {self.g.degree[node_id]}, {node_id}")
            nodes.append((self.g.degree[node_id], node_id))
            count += 1
            if count == k:
                break

        self._results.append(f"Top degree centrality nodes: {nodes}")

        filename, suffix, ext = MainUtils.get_file_info(
            self.config.o, suffix=self.config.name
        )
        save_file(filename + suffix + ext, self._results)

    def _degree_centrality(self):
        """Calculate, plot and save Degree Centrality distributions.

        :return: Degree Centralities and their occurrence
        :rtype: `tuple`
        """
        sequence = sorted([round(d, 4) for n, d in nx.degree_centrality(self.g).items()], reverse=True)
        count = collections.Counter(sequence)
        dc, _ = zip(*count.items())

        plt.xlabel('Degree Centrality')
        plt.ylabel('Relative Häufigkeit')
        hist, bins = np.histogram(dc, bins=len(dc) if len(dc) < 40 else 40, density=True)
        # Normalize y axis to [0,1]
        plt.bar(bins[:-1], hist.astype(np.float32) / hist.sum(), width=(bins[1] - bins[0]) * 0.8, color='orange')
        filename, suffix, ext = MainUtils.get_file_info(
            self.config.img + self.config.config_id + "_degree_centrality.png", suffix=self.config.name
        )
        plt.savefig(filename + suffix + ext)
        if self.config.verbose:
            plt.show()
        plt.close()

        return dc

    def _local_cluster_coefficient(self, weight=None):
        """Calculate, plot and save local cluster coefficients.

        :param weight: Edge attribute that contains weight information
        :type weight: `str`
        :return: Local cluster coefficients and their occurrence
        :rtype: `tuple`
        """
        sequence = sorted([round(d, 4) for n, d in nx.algorithms.cluster.clustering(self.g, weight=weight).items()],
                          reverse=True)
        count = collections.Counter(sequence)
        cc, _ = zip(*count.items())

        plt.xlabel('Lokaler Cluster-Koeffizient')
        plt.ylabel('Relative Häufigkeit')
        hist, bins = np.histogram(cc, bins=len(cc) if len(cc) < 40 else 40, density=True)
        # Normalize y axis to [0,1]
        plt.bar(bins[:-1], hist.astype(np.float32) / hist.sum(), width=(bins[1] - bins[0]) * 0.8, color='orange')
        filename, suffix, ext = MainUtils.get_file_info(
            self.config.img + self.config.config_id + "_local_cluster_coefficient.png", suffix=self.config.name
        )
        plt.savefig(filename + suffix + ext)
        if self.config.verbose:
            plt.show()
        plt.close()

        return cc

    def _density(self):
        """Return graph density.

        :return: Graph density
        :rtype: `float`
        """
        return nx.density(self.g)

    def _diameter(self):
        """Return graph diameter.

        :return: Graph diameter
        :rtype: `int`
        """
        if nx.is_connected(self.g):
            return nx.algorithms.diameter(self.g)
        else:
            return nx.algorithms.diameter(self.g.subgraph(self._max_component(return_component=True)))

    def _avg_shortest_path(self):
        """Return average shortest path.

        :return: Average shortest path
        :rtype: `float`
        """
        if nx.is_connected(self.g):
            return nx.average_shortest_path_length(self.g, weight='weight')
        else:
            return nx.average_shortest_path_length(self.g.subgraph(self._max_component(return_component=True)),
                                                   weight='weight')

    def _global_cluster_coefficient(self):
        """Return global cluster coefficient.

        :return: Global cluster coefficient
        :rtype: `float`
        """
        return nx.average_clustering(self.g)

    def _clique_number(self):
        """Return clique number (i.e., size of largest clique).

        :return: Size of largest clique
        :rtype: `int`
        """
        return nx.graph_clique_number(self.g)

    def _nr_of_cliques(self):
        """Return number of cliques.

        :return: Number of cliques
        :rtype: `int`
        """
        return nx.graph_number_of_cliques(self.g)

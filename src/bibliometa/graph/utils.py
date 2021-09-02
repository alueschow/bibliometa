#!/usr/bin/python
# -*- coding: utf-8 -*-

"""This module provides utility functions for graphs."""

import json
import os

from operator import itemgetter

import networkx as nx
import pandas as pd

from loguru import logger

from bibliometa.utils.utils import MainUtils

_ENCODING = "utf-8"


def load_graph(config, reload=False):
    """Load a graph from a GraphML or similarity file.

    :param config: Configuration object
    :type config: `bibliometa.configuration.Config`
    :param reload: If graph will be loaded directly from similarity file
    :type reload: `bool`
    :return: Graph
    :rtype: `networkx.Graph`
    """
    # get reload configuration parameter if available
    try:
        reload = config.reload
    except Exception:
        pass

    if not reload:
        if config.graphml:
            if config.graphml.endswith(".graphml"):
                _path = config.graphml
            else:
                filename, suffix, ext = MainUtils.get_file_info(
                    config.graphml + config.config_id + ".graphml", suffix=config.name
                )
                _path = filename + ext + suffix
        else:
            raise ValueError("Configuration parameter 'graphml' is not defined!")
        try:
            logger.info(f"Import from .graphml file {_path}.")
            graph = nx.read_graphml(_path)
            logger.info("Import finished.")
        except FileNotFoundError:
            raise FileNotFoundError(f"GraphML file at {_path} can not be found. If using JSON2EdgeList, "
                                    "do you need to set config.reload to True?")
    else:
        logger.info(f"Create graph from information in file {config.i}.")
        graph = read_file(config, config.encoding)
        logger.info("Graph creation finished.")

    return graph


def read_file(config, encoding=_ENCODING):
    """Create graph by reading in a similarity file.

    :param config: Configuration object
    :type config: `bibliometa.configuration.Config`
    :param encoding: File encoding
    :type encoding: `str`
    :return: Graph
    :rtype: `networkx.Graph`
    """
    g = nx.Graph()

    count = 0
    for df in pd.read_csv(config.i, chunksize=config.chunksize, sep=config.csv_sep, index_col=0, low_memory=False,
                          compression='gzip', encoding=encoding, header=0,
                          usecols=[0, 1, 2, config.sim_functions.index(config.sim) + 3],
                          names=['id', 'nodea', 'nodeb', 'sim']):
        count += 1
        logger.info("Import datasets ...")  # (up to {count * config.chunksize / 1000000} million) ...")
        for i in [tuple(itemgetter(0, 1, 2)(x)) for x in df.values]:
            if i[2] > config.t:
                try:
                    g.add_weighted_edges_from([i])
                except Exception as e:
                    logger.warning(
                        f"can not add weighted edge from {[i]} in chunk {count * config.chunksize}, error {e}"
                    )
    logger.info("Import finished!")

    if config.create_graphml:
        if config.graphml.endswith(".graphml"):
            _path = config.graphml
        else:
            filename, suffix, ext = MainUtils.get_file_info(
                config.graphml + config.config_id + ".graphml", suffix=config.name
            )
            _path = filename + ext + suffix

        dirname = os.path.dirname(_path)
        if not os.path.exists(dirname):
            os.makedirs(dirname)

        logger.info("Saving graph as .graphml file ...")
        nx.write_graphml(g, _path, encoding=encoding)
        logger.info("Saved .graphml file successfully.")

    return g


def save_file(path, results, encoding=_ENCODING):
    """Save results in a text file.

    :param path: Path to output file
    :type path: `str`
    :param results: List containing results from graph analysis
    :type results: `list`
    :param encoding: Encoding of file
    :type encoding: `str`
    """
    dirname = os.path.dirname(path)
    if not os.path.exists(dirname):
        os.makedirs(dirname)

    with open(path, 'w', encoding=encoding) as f:
        f.write("\n".join(results))


def get_nodes(graph, config, encoding=_ENCODING):
    """Get nodes and their degrees from a graph.

    :param graph: Graph object
    :type graph: `networkx.Graph`
    :param config: Configuration object
    :type config: `bibliometa.configuration.Config`
    :param encoding: File encoding
    :type encoding: `str`
    :return: Dictionary of nodes with their degrees
    :rtype: `dict`
    """
    nodes = {n: graph.degree[n] for n in graph.nodes()}
    nodes = dict(sorted(nodes.items(), key=lambda item: item[1], reverse=True))

    _path = f"{config.degrees}degrees_{config.name}.json"
    if not os.path.exists(os.path.dirname(_path)):
        os.makedirs(os.path.dirname(_path))
    with open(_path, "w", encoding=encoding) as f:
        json.dump(nodes, f, indent=4)

    return nodes


def add_nodes_from_graph_corpus(graph, corpus, singletons=False, encoding=_ENCODING):
    """Add nodes from a graph corpus file to a graph if not yet existent.

    :param graph: Graph object
    :type graph: `nx.Graph`
    :param corpus: Path to graph corpus file
    :type corpus: `str`
    :param singletons: If *only* those nodes with no edges will be returned
    :type singletons: `bool`
    :param encoding: File encoding
    :type encoding: `str`
    :return: Updated Graph object
    :rtype: `nx.Graph`
    """
    with open(corpus, "r", encoding=encoding) as f:
        data = json.load(f)

    if singletons:
        g = nx.Graph()
        for k in data.keys():
            if k not in graph.nodes:
                g.add_node(k, size=len(data[k]))
        return g
    else:
        for k in data.keys():
            if k not in graph.nodes:
                graph.add_node(k, size=len(data[k]))

        return graph


def update_graph(graph, df, col):
    """Remove nodes from graph that do not appear in column col in DataFrame df.

    :param graph: Graph object
    :type graph: `networkx.Graph`
    :param df: DataFrame
    :type df: `pandas.DataFrame`
    :param col: Column in DataFrame
    :type col: `str`
    :return: Updated Graph object
    :rtype: `networkx.Graph`
    """
    remove_list = []

    logger.debug(f"Number of nodes in the graph (before update): {len(graph.nodes)}")

    for n in graph.nodes:
        if n not in df[col].tolist():
            remove_list.append(n)

    for n in remove_list:
        try:
            graph.remove_node(n)
        except Exception:
            pass

    logger.debug(f"Number of nodes in the graph (after update): {len(graph.nodes)}")

    for n in graph.nodes:
        logger.debug(n)

    return graph


def get_subgraph(graph):
    """Get largest connected component from graph.

    :param graph: Graph object
    :type graph: `networkx.Graph`
    :return: Largest component
    :rtype: `networkx.Graph`
    """
    subgraphs = [graph.subgraph(c).copy() if graph.subgraph(c) else nx.Graph() for c in nx.connected_components(graph)]
    # TODO: Falls len(subgraphs) > 0: abfangen (keine Übereinstimmung zwischen coordinates[geo_col] und nodes ...)

    maxlen = 0
    largest = subgraphs[0]
    for x in subgraphs:
        if len(x.nodes) > maxlen:
            largest = x
            maxlen = len(x.nodes)

    logger.debug(f"{len(subgraphs)} components found, only use largest component with size {len(largest.nodes)}.")

    return largest


def get_graph_attributes(graph):
    """Get degrees, labels and sizes for a graph.

    :param graph: Graph object
    :type graph: `networkx.Graph`
    :return: Dictionary with degrees, labels, sizes
    :rtype: `dict`
    """
    degrees = nx.degree(graph)

    # set default node size
    for n in graph.nodes:
        if "size" not in graph.nodes[n].keys():
            graph.nodes[n]["size"] = 1

    labels = {n: n for n in graph.nodes}
    sizes = [10 * degrees[n] if degrees[n] > 0 else graph.nodes[n]["size"] for n in graph.nodes]

    return {"degrees": degrees,
            "labels": labels,
            "sizes": sizes}


def create_pos(graph, df, keys_labels, extent, verbose):
    """Create dictionary with node positions.

    :param graph: Graph object
    :type graph: `networkx.Graph`
    :param df: DataFrame with geographical information
    :type df: `pandas.DataFrame`
    :param keys_labels: Column in DataFrame
    :type keys_labels: `str`
    :param extent: Extent of map
    :type extent: `list`
    :param verbose: Verbose parameter
    :type verbose: `bool`
    :return: Dictionary of positions
    :rtype: `dict`
    """
    pos = {}
    remove = []

    for n in graph.nodes:
        lat = df[df[keys_labels] == n]["lat"].to_string(index=False)
        lng = df[df[keys_labels] == n]["lng"].to_string(index=False)
        if isinstance(extent, list):
            if extent[0] < float(lng) < extent[1] and extent[2] < float(lat) < extent[3]:
                pos[n] = (float(lng), float(lat))
            else:
                remove.append(n)
        else:
            pos[n] = (float(lng), float(lat))

    logger.debug(f"Positions: {pos}")
    if verbose:
        print(pos)

    return pos, remove

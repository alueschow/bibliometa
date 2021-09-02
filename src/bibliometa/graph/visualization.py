# !/usr/bin/python
# -*- coding: utf-8 -*-

"""This module provides classes and functions to visualize network data on geographical maps."""

import os
import sys

import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader
import geopandas as gpd
import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd

from loguru import logger
from matplotlib.pyplot import text
from shapely.geometry import Point

from bibliometa.config import LOGGING_FORMAT, GRAPH_VISUALISATION_MAP_CONFIG_DEFAULT
from bibliometa.configuration import BibliometaConfiguration
from bibliometa.graph.utils import load_graph, update_graph, get_nodes, get_subgraph, \
    get_graph_attributes, create_pos, add_nodes_from_graph_corpus


class Map(BibliometaConfiguration):
    """The :class:`~bibliometa.graph.visualization.Map` provides functions to visualize geographical network data on
    a map.
    """

    def __init__(self, **kwargs):
        """Construct a new :class:`~bibliometa.graph.visualization.Map`."""
        super().__init__(GRAPH_VISUALISATION_MAP_CONFIG_DEFAULT, **kwargs)

    def _update_config(self):
        """Update configuration with class-specific values and check for configuration correctness."""
        self._shp = MapUtils.read_shp(self.config.shapefile, self.config.shapefile_color, self.config.verbose)
        self._shapes = list(shpreader.Reader(self.config.shapefile).geometries())

        self._df = MapUtils.convert_to_gdf(self.config.coordinates, self.config.crs, self.config.coordinates_sep)

        self.graph = load_graph(self.config, reload=False)

        # create dictionary of nodes and their node degrees
        self._nodes = get_nodes(self.graph, self.config, encoding=self.config.encoding)

        if not os.path.exists(self.config.o):
            os.makedirs(self.config.o)
        if not os.path.exists(self.config.graphml):
            os.makedirs(self.config.graphml)

    def start(self):
        """Start visualization."""
        # Set up logging
        logger.remove()
        logger.add(self.config.log, format=LOGGING_FORMAT, level=self.config.log_level_file)
        if self.config.verbose:
            logger.add(sys.stderr, level=self.config.log_level_std)
        logger.info("Start network creation.")

        self._update_config()

        # plot all cities from city file as scatter plot
        if "scatter" in self.config.types:
            logger.info("Creating scatterplot.")
            Plotting.scatter(self._df, self.config)

        # plot all cities from city file on map
        if "cities" in self.config.types:
            logger.info("Plotting all cities.")
            Plotting.cities(self._df, self._shp, self.config)

        # plot nodes on map
        if "degrees" in self.config.types:
            logger.info("Plotting node degrees.")
            Plotting.degrees(self._df, self._shp, self._nodes, self.config)

        # add nodes with degree == 0 if desired
        if self.config.all_nodes:
            self.graph = add_nodes_from_graph_corpus(self.graph,
                                                     self.config.graph_corpus,
                                                     self.config.singletons,
                                                     encoding=self.config.encoding)

        # remove unneeded nodes from the graph
        update_graph(self.graph, self._df, self.config.keys_labels[0])

        # get largest component as subgraph and plot on map
        if "map" in self.config.types:
            logger.info("Plotting network on map.")
            if not self.config.components:
                subgraph = get_subgraph(self.graph)
            else:
                subgraph = self.graph
            pos, remove = create_pos(subgraph,
                                     self._df,
                                     self.config.keys_labels[0],
                                     self.config.map_extent,
                                     self.config.verbose)
            subgraph.remove_nodes_from(remove)
            attributes = get_graph_attributes(subgraph)
            Plotting.graph_on_map(self._shapes,
                                  subgraph,
                                  attributes,
                                  pos,
                                  self._df,
                                  self.config)

        logger.info("Network creation finished.")
        logger.info(f"Logfile written to {self.config.log}")


class Plotting:
    """The :class:`~bibliometa.graph.visualization.Plotting` provides functions to plot network data."""

    @staticmethod
    def scatter(df, config):
        """Create scatter plot.

        :param df: DataFrame with 'lng' and 'lat' column
        :type df: `pandas.DataFrame`
        :param config: Configuration object
        :type config: `bibliometa.configuration.Config`
        """
        plot = plt.scatter(x=df['lng'], y=df['lat'])
        if config.verbose:
            plt.show()

        for ext in config.o_formats:
            _path = f"{config.o}scatter/{config.name}.{ext}"
            dirname = os.path.dirname(_path)
            if not os.path.exists(dirname):
                os.makedirs(dirname)
            fig = plot.get_figure()
            fig.savefig(_path, bbox_inches='tight')

        plt.clf()
        plt.close('all')

    @staticmethod
    def cities(df, shp, config):
        """Plot cities on a certain map.

        :param df: DataFrame with city information
        :type df: `pandas.DataFrame`
        :param shp: Shapefile
        :type shp: GeoDataFrame
        :param config: Configuration object
        :type config: `bibliometa.configuration.Config`
        """
        plot = df.plot(ax=shp.plot(figsize=config.figsize, marker='o', color=config.shapefile_color, markersize=45),
                       aspect=1)
        if config.verbose:
            plt.show()

        for ext in config.o_formats:
            _path = f"{config.o}cities/{config.name}.{ext}"
            dirname = os.path.dirname(_path)
            if not os.path.exists(dirname):
                os.makedirs(dirname)
            fig = plot.get_figure()
            fig.savefig(_path, bbox_inches='tight')

        plt.clf()
        plt.close('all')

    @staticmethod
    def degrees(df, shp, nodes, config):
        """Plot graph with node degrees.

        :param df: DataFrame with city information
        :type df: `pandas.DataFrame`
        :param nodes: Graph nodes with their degrees
        :type nodes: `dict`
        :param shp: Shapefile
        :type shp: GeoDataFrame
        :param config: Configuration object
        :type config: `bibliometa.configuration.Config`
        """
        fig, ax = plt.subplots(figsize=config.figsize)
        shp.plot(ax=ax, alpha=0.6, color=config.shapefile_color)
        for city in nodes.keys():
            if city in df[config.keys_labels[1]].tolist():
                df[df[config.keys_labels[1]] == city].plot(ax=ax, markersize=nodes[city],
                                                           color=config.degree_node_color, marker="o")
        for x, y, label in zip(df.geometry.x, df.geometry.y, df.city):
            if label in nodes.keys():
                ax.annotate(label, xy=(x, y), xytext=(3, 3), textcoords="offset points")
        if config.verbose:
            plt.show()

        for ext in config.o_formats:
            _path = f"{config.o}degrees/{config.name}.{ext}"
            dirname = os.path.dirname(_path)
            if not os.path.exists(dirname):
                os.makedirs(dirname)
            fig.savefig(_path, bbox_inches='tight')

        plt.clf()
        plt.close('all')

    @staticmethod
    def graph_on_map(shapes, subgraph, attributes, pos, df, config):
        """Plot graph on a map.

        :param shapes: An iterator of shapely geometries from a shapefile
        :type shapes: `list`
        :param subgraph: Largest component of graph
        :type subgraph: `networkx.Graph`
        :param attributes: Dictionary of graph degrees, labels and sizes
        :type attributes:  `dict`
        :param pos: Dictionary of node positions
        :type pos: `dict`
        :param df: DataFrame with coordinates
        :type df: `pandas.DataFrame`
        :param config: Configuration object
        :type config: `bibliometa.configuration.Config`
        """
        crs = ccrs.PlateCarree()
        fig, ax = plt.subplots(1, 1, figsize=config.figsize,
                               subplot_kw=dict(projection=crs))

        ax.add_geometries(shapes, crs, edgecolor='black', facecolor=config.shapefile_color, alpha=0.2)

        ax.coastlines()
        if config.map_extent == "global":
            ax.set_global()
        else:
            ax.set_extent(config.map_extent)

        nx.draw_networkx(subgraph,
                         ax=ax,
                         # font_size=24,
                         alpha=.5,
                         width=config.edge_width,
                         # width=[subgraph[u][v]['weight'] * 0.1 for u, v in subgraph.edges],  # TODO: Implement
                         node_size=attributes["sizes"],
                         labels=attributes["labels"],  # TODO: Does this have an effect?
                         pos=pos,
                         with_labels=False,
                         # node_color=altitude,
                         # cmap=plt.cm.autumn
                         )

        # add labels
        for node, (x, y) in pos.items():
            fs = config.fontsize
            try:
                if attributes["degrees"][node] > config.fontsize:
                    fs = attributes["degrees"][node]
                if config.max_fontsize and fs > config.max_fontsize:
                    fs = config.max_fontsize
                label = df[df[config.keys_labels[0]] == node].iloc[0, df.columns.get_loc(config.keys_labels[1])]
                text(x, y, label, fontsize=fs, ha='center', va='center')
            except Exception:
                pass

        if config.verbose:
            plt.show()

        for ext in config.o_formats:
            _path = f"{config.o}network/{config.name}.{ext}"
            dirname = os.path.dirname(_path)
            if not os.path.exists(dirname):
                os.makedirs(dirname)
            fig.savefig(_path, bbox_inches='tight')

        plt.clf()
        plt.close('all')


class MapUtils:
    """The :class:`~bibliometa.graph.visualization.MapUtils` provides utilities for the
    :class:`~bibliometa.graph.visualization.Map` class.
     """

    @staticmethod
    def read_shp(f, color="grey", verbose=False):
        """Read shapefile.

        :param f: Path to shapefile
        :type f: `str`
        :param color: Color of shapefile background
        :type color: `str`
        :param verbose: Verbose parameter
        :type verbose: `bool`
        :return: Shapefile
        :rtype: GeoDataFrame
        """
        shp = gpd.read_file(f)
        # if verbose:
        # fig, ax = plt.subplots(figsize=(15, 15))
        # shp.plot(ax=ax, alpha=0.6, color=color)
        # plt.show()

        return shp

    @staticmethod
    def convert_to_gdf(csv_input, crs, csv_sep):
        """Convert long/lat to Point objects.

        :param csv_input: Path to CSV input file with long/lat information
        :type csv_input: `str`
        :param crs: Coordinate Reference System
        :type crs: `str`
        :param csv_sep: CSV separator in input file
        :type csv_sep: `str`
        """
        orig_df = pd.read_csv(csv_input, sep=csv_sep)
        df = orig_df.copy()
        try:
            geometry = [Point(xy) for xy in zip(df["lng"], df["lat"])]
            df = gpd.GeoDataFrame(df, crs=crs, geometry=geometry)
            logger.info(f"Successfully converted import data from {csv_input} to GeoDataFrame.")
            logger.debug(f"Imported city data:\n{orig_df.head()}")
            logger.debug(f"GeoDataFrame:\n{df.head()}")
            return df
        except Exception as e:
            raise ValueError(f"Could not convert import data from {csv_input} to GeoDataFrame. Exception: {e}")

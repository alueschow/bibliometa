#!/usr/bin/python
# -*- coding: utf-8 -*-

"""This file provides constants used throughout other modules."""

LOGGING_FILENAME = "./logs/{time}.log"
LOGGING_FORMAT = "{time} {level} {message}"

CSV_JSON_CONVERSION_CONFIG_DEFAULT = {
    "i": None,  # input CSV file
    "o": None,  # path to file name where JSON will be saved
    "from_": None,  # starting year
    "to": None,  # end year
    "step": 10,  # interval between two years
    "fields": [  # fields that will be extracted from the CSV file; mandatory
        {"content": ("515", "a"),
         "type": ("515", "0"),
         "categories": ["actv"]},
        {"content": ("350", "a"),
         "type": ("350", "0"),
         "categories": ["acti"]},
    ],
    "subfield_sep": "$",  # separator that splits fields and their subfields
    "split_char": " ### ",  # character used to split multiple values in a cell
    "csv_sep": "\t",  # CSV separator
    "datefield": ("340", "x"),  # field and subfield of date field used; mandatory
    "date_indicator": ["0", "1"],  # 0 == biographical | 1 == activity
    "interval_lower": 10,  # mandatory if not all data sets have a start and end year
    "interval_upper": 10,  # mandatory if not all data sets have a start and end year
    "log": None,  # path to log file
    "log_level_std": "INFO",  # log severity level on standard output
    "log_level_file": "DEBUG",  # log severity level in log file
    "verbose": False,  # if additional information is shown during program execution
    "encoding": "utf-8"  # file encoding used
    # columns in input CSV must be in the form "field + subfield separator + subfield";
    # multiple values in a cell must be delimited by "split_char";
    # each content column needs a type column where each entry in the content column
    # has a related entry in the type column;
    # only those types defined under the "categories" key are considered
}

JSON_EDGELIST_CONVERSION_CONFIG_DEFAULT = {
    "i": None,  # input JSON file; mandatory
    "o": None,  # output similarity file; mandatory
    "create_corpus": False,  # if a graph corpus will be created
    "corpus": None,  # path to graph corpus file
    "name": "",  # unique name for single conversion step (needed when script is called from a loop)
    "fields": None,  # fields and subfields to consider; mandatory
    "swap": False,  # whether keys from input file become values in output file
    "sim_functions": None,  # similarity functions
    "archive": True,  # whether output similarity file is put into an archive
    "archive_ext": ".tar.gz",  # file extension of output archive
    "csv_sep": "\t",  # CSV separator
    "log": None,  # path to log file
    "log_level_std": "INFO",  # log severity level on standard output
    "log_level_file": "DEBUG",  # log severity level in log file
    "verbose": False,  # if additional information is shown during program execution
    "encoding": "utf-8"  # file encoding used
}

GRAPH_ANALYSIS_CONFIG_DEFAULT = {
    "i": None,  # input similarity file
    "o": None,  # path where output text file with graph analysis are stored; mandatory
    "types": ["node_count",
              "edge_count",
              "component_count",
              "max_component",
              "avg_degree",
              "degree_distribution",
              "top_dc_nodes",
              "degree_centrality_distribution",
              "local_cluster_coefficient",
              "density",
              "diameter",
              "average_shortest_path",
              "global_clustering_coefficient",
              "graph_clique_number",
              "number_of_cliques"],  # types of graph analysis conducted; by default, all available analyses are used
    "img": None,  # path where output images are stored; mandatory
    "create_graphml": False,  # if GraphML file should be created when creating graph from similarity file
    "graphml": None,  # path where GraphML input/output files are stored; mandatory
    "n": None,  # name of nodes; mandatory
    "e": None,  # name of edges; mandatory
    "sim": None,  # name of similarity function; mandatory
    "sim_functions": [],  # list of similarity functions in the same order as given in the input file; mandatory
    "weighted": False,  # if similarity functions creates weighted edges
    "t": 0,  # threshold for similarity function
    "reload": True,  # if creating graph from similarity file is enforced, even if GraphML file is already available
    "name": "",  # string that uniquely identifies a run if graph analysis is conducted in a loop
    "chunksize": 1000000,  # edges that will be loaded per chunk
    "csv_sep": "\t",  # CSV separator
    "log": None,  # path to log file
    "log_level_std": "INFO",  # log severity level on standard output
    "log_level_file": "DEBUG",  # log severity level in log file
    "verbose": False,  # if additional information is shown during program execution
    "encoding": "utf-8"  # file encoding used
}

GRAPH_VISUALISATION_MAP_CONFIG_DEFAULT = {
    "graphml": None,  # input GraphML file
    "o": None,  # output folder for image files
    "o_formats": ("pdf", "svg"),  # output formats that will be created
    "degrees": None,  # output folder where node degree information is saved
    "types": None,  # types of visualization; may be "scatter", "cities", "degrees", and/or "map"
    "shapefile": "../data/shapefiles/DEU_adm1/DEU_adm1.shp",  # input shapefile
    "shapefile_color": "grey",  # shapefile color
    "degree_node_color": "black",  # color of nodes in degree images
    "coordinates": "../data/german_cities.csv",  # CSV file with coordinates information
    "coordinates_sep": ",",  # CSV separator in coordinates input file
    "keys_labels": ("id", "city"),  # ID and label column in coordinates GeoDataFrame
    "crs": "epsg:4326",  # Coordinate Reference System used
    "map_extent": "global",  # may be "global" or a list of 4 values
    "components": True,  # whether all components are used, otherwise only largest
    "all_nodes": True,  # whether also nodes without edges are used
    "graph_corpus": None,  # path to graph corpus, mandatory if all_nodes == True
    "singletons": False,  # if only nodes without edges are used; only used if all_nodes == True
    "name": None,  # identifier for a visualization run that is appended to output images filenames; mandatory
    "figsize": (55, 55),  # size of output figures
    "fontsize": 12,  # font size in figures
    "max_fontsize": 24,
    "edge_width": .25,
    "log": None,  # path to log file
    "log_level_std": "INFO",  # log severity level on standard output
    "log_level_file": "DEBUG",  # log severity level in log file
    "verbose": False,  # if additional information is shown during program execution
    "encoding": "utf-8",  # file encoding used
}

# Bibliometa

[![Documentation Status](https://readthedocs.org/projects/bibliometa/badge/?version=latest)](https://bibliometa.readthedocs.io/en/latest/?badge=latest)
[![PyPI version](https://badge.fury.io/py/bibliometa.svg)](https://badge.fury.io/py/bibliometa)

Bibliometa is a python library for manipulating, converting and analysing bibliographic metadata, with a focus on graph analysis.

*Homepage*: https://bibliometa.readthedocs.io

*Repository*: https://github.com/alueschow/bibliometa

*Package*: https://pypi.org/project/bibliometa/

*License*: MIT

-----

## Installation
* Use pip: ```pip install bibliometa```
+ **Note**: You may need to install the following packages on your machine in advance (e.g. via `apt-get`) to be able to use Bibliometa:
  - libproj-dev
  - proj-data
  - proj-bin
  - libgeos-dev

## Development
* Clone this repository: ```git clone https://github.com/alueschow/bibliometa.git```
* Run ```poetry install``` to install all necessary dependencies
+ After development, run ```poetry export --without-hashes -f requirements.txt --output requirements.txt ``` to create a _requirements.txt_ file with all dependencies. This file is needed to create the documentation on [ReadTheDocs](https://readthedocs.org/).
*  Run ```poetry run sphinx-apidoc -f -o source ../src/bibliometa``` and then ```poetry run make html``` from within the _docs_ folder to create a local documentation using [Sphinx](https://www.sphinx-doc.org/en/master/).

## Tutorial
A tutorial that makes use of the Bibliometa package can be found on GitHub: https://github.com/alueschow/cerl-thesaurus-networks

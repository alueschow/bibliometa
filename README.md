# Bibliometa

[![Documentation Status](https://readthedocs.org/projects/bibliometa/badge/?version=latest)](https://bibliometa.readthedocs.io/en/latest/?badge=latest)
[![PyPI version](https://badge.fury.io/py/bibliometa.svg)](https://badge.fury.io/py/bibliometa)

Bibliometa is a python library for manipulating, converting and analysing bibliographic metadata, with a focus on graph analysis.

*Repository*: https://github.com/alueschow/bibliometa

*Package*: https://pypi.org/project/bibliometa/

*License*: MIT

-----

## Installation
* Use pip: ```pip install bibliometa```

## Development
* Clone this repository: ```git clone https://github.com/alueschow/bibliometa.git```
* Run ```poetry install``` to install all necessary dependencies
+ After development, run ```poetry export --without-hashes -f requirements.txt --output requirements.txt ``` to create a _requirements.txt_ file with all dependencies. This file is needed to create the documentation on [ReadTheDocs](https://readthedocs.org/).
*  Run ```poetry run sphinx-apidoc -f -o source ../src/bibliometa``` and then ```poetry run make html``` from within the _docs_ folder to create a local documentation using [Sphinx](https://www.sphinx-doc.org/en/master/).

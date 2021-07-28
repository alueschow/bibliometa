# !/usr/bin/python
# -*- coding: utf-8 -*-

"""This module provides utilities to handle tar files."""

import os
import tarfile


def tar(path, name):
    """Put contents from `path` to tar.gz archive in `name`."""
    if os.path.isfile(path):
        with tarfile.open(name, "w:gz") as tar_file:
            tar_file.add(path, arcname=os.path.basename(path))
            return tar_file
    elif os.path.isdir(path):
        with tarfile.open(name, "w:gz") as tar_file:
            for root, dirs, files in os.walk(path):
                for file in files:
                    tar_file.add(os.path.join(root, file))
        return tar_file
    else:
        raise ValueError("Path is neither file nor directory!")

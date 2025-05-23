"""Hierarchical ARBitrary Data Storage.

An API and local filesystem-based implementation for managing hierarchical
data sets in Python.
* Datasets are arranged inside of a Database.
* Each Dataset can have multiple children Dataset's and only one parent. The
parent may be another Dataset or the Database.
* A Dataset inherits the data from its parent recursively.
* A Dataset can directly store JSON data.
* Each Dataset can have zero or more Datapoints.

The API is intentionally sparse with only the absolute basic interfaces defined.
Additionally, no guarantees are made about the implementation of the interface beyond
those explicitly stated in the docstring of the API. For example, thread safety is
not guaranteed for any implementation and indeed does not exist for the basic filesystem
implementation.
"""

from .api import AbstractDatabase, AbstractDatapoint, AbstractDataset

__all__ = ["AbstractDatabase", "AbstractDatapoint", "AbstractDataset"]

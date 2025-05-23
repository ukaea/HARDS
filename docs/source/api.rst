The API
=======

.. contents:: Page Contents
    :depth: 2

HARDS defines its API both in code and text (docstrings).

The code defines the objects and interfaces required to implement the tree-like
structure seen in the introduction. The types of arguments and return values provides some information
about the API and the types of data it can handle. However, the docstrings will provide important
implementation details, caveats, and important constraints on the functionality and valid data types.

Models
-------
HARDS provides three classes that model how data is stored and related.

The **database** class handles the accessing of top-level datasets and--by extension--manages the
physical location of all data (e.g. filesystem, web server).

The **dataset** class handels the accessing of related datapoints and datasets (called sub-datasets).
A dataset can manage many datapoints and many datasets but only has one parent--either another dataset
or the database.

Finally, a **datapoint** is a class that models a single unit of data. It has no children and is the child
of a single dataset, although it will be available to all children of its parent.

An example of this model is found in the prologue of :doc:`index`: numerical optimisation of
magnetic coils. The top-level datasets here are the initial Monte Carlo samples of a given version of the
simulator. The sub-datasets are the results of intelligent sampling algorithms that use the
available data to train decision-making models.


Data and Files
--------------
**Datasets** and **datapoints** can have data and files attached to them.

Data is JSON serialisable and will often be a key-value store (dictionary) of data.
Data attached to a dataset should be considered metadata that is relevant to all of the datapoints--however
this merely a suggestion.
Implementations of HARDS may place additional constraints on the type of data that is legal.
For example, they may enforce a key-value store with no nested structures.

Files can be of any format and contain any data. They are copied into the database and can only be modified
by re-adding a file with the same name. Files are made accessible back to the user
via a ``pathlib.Path`` object (again, this is read-only).


Parallel Workflows
------------------
HARDS API makes no prescriptions to handle concurrent or parallel workflows safely.
Generally, a parallel or concurrent workflow should not rely on changes made in another.
Some implementations may not immediately commit changes to the data or new files to the database which
could lead to one thread using outdated data/files.
Similarly, the creation of a dataset or datapoints may not be immediately actioned within the
database--especially in implementations that are non-local.

Therefore, it is good practice to create the dataset in a single thread before spawning parallel processes.
Each of these parallel processes can be responsible for creating its own datapoints and updating their
data and files.
When the parallel processes are finished, analysis of the data can then occur on a single thread because all
of the data should have been safely stored.



API Documentation
-----------------
.. automodule:: hards.api
   :members:
   :inherited-members:
   :show-inheritance:

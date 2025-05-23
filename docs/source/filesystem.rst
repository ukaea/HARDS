The Filesystem Implementation
=============================
.. contents:: Page Contents
    :depth: 2

The 'filesystem implementation' implements :doc:`api` in its entirety, using the ``json`` and ``pathlib``
standard libraries to store data on the local filesystem.

Examples
--------
Several examples notebooks are included to illustrate the basics of using the HARDS
filesystem implementation.
The final example is a complete example of the HARDS workflow for managing experimental data.

.. toctree::
   :maxdepth: 2

   examples/

Code Documentation
------------------
.. automodule:: hards.filesystem
   :members:
   :inherited-members:
   :show-inheritance:
   :exclude-members: FilesystemError

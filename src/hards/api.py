"""The abstract API for managing hierarchical datasets in Python."""

import abc
import string
from collections.abc import Sequence
from pathlib import Path
from typing import Any, Optional

__all__ = ["AbstractDatabase", "AbstractDatapoint", "AbstractDataset"]

VALID_NAME_CHARACTERS = set(string.ascii_letters + string.digits + "._-")
"""A string of valid characters to be used in names of datasets, datapoints, and
files.
"""


class HARDSError(Exception):
    """Parent exception for any custom exceptions in the HARDS package."""


class DoesNotExistError(HARDSError):
    """An error for when an object is requested that does not exist."""


class AlreadyExistsError(HARDSError):
    """An error for when an object is created with the same name as one that exists."""


class InvalidNameError(HARDSError):
    """An error for attempting to create an object whose name contains invalid chars."""


class _AbstractHasChildrenDatasetsMixin(abc.ABC):
    """An abstract mixin for classes that have datasets as children."""

    @property
    @abc.abstractmethod
    def children(self) -> Sequence[str]:
        """The names of the object's current children (datasets)."""

    @abc.abstractmethod
    def get_dataset(self, name: str) -> "AbstractDataset":
        """Return a dataset that is a child of this object.

        Parameters
        ----------
        name : str
            The name of the dataset to get

        Returns
        -------
        AbstractDataset
            The dataset with the given name.

        Raises
        ------
        DoesNotExistError
            If a dataset with the given name does not exist.

        """

    @abc.abstractmethod
    def has_dataset(self, name: str) -> bool:
        """Indicate if the object has a child dataset with the given name.

        Parameters
        ----------
        name : str
            The name of the dataset to check exists.

        Returns
        -------
        bool
            True if dataset exists, else False.

        """

    @abc.abstractmethod
    def create_dataset(self, name: str) -> "AbstractDataset":
        """Create a dataset as a child of this object.

        Parameters
        ----------
        name : str
            The name of the new dataset.

        Returns
        -------
        AbstractDataset
            The new dataset object.

        Raises
        ------
        AlreadyExistsError
            If a database with the same name already exists.
        InvalidNameError
            If the dataset name contains invalid character.

        """
        invalid_chars = set(name) - VALID_NAME_CHARACTERS
        if len(invalid_chars) > 0:
            error_msg = f"Dataset name contains invalid characters: {invalid_chars}"
            raise InvalidNameError(error_msg)

    def recursively_get_dataset(self, name: str) -> "AbstractDataset":
        """Recursively follow a tree of datasets and return the final dataset.

        Parameters
        ----------
        name : str
            The name of the datasets to follow and the dataset to return of the form
            `<intermediate dataset>/<intermediate dataset>/<...>/<dataset of interest>`

        Returns
        -------
        AbstractDataset
            The dataset object.

        Raises
        ------
        DoesNotExistError
            If any of the intermediate datasets do not exist.

        """
        dataset_names = name.strip("/").split("/")
        next_dataset_name = dataset_names[0]

        if len(dataset_names) == 1:
            return self.get_dataset(next_dataset_name)

        return self.get_dataset(next_dataset_name).recursively_get_dataset(
            "/".join(dataset_names[1:])
        )

    def recursively_get_datapoint(self, name: str) -> "AbstractDatapoint":
        """Recurisvely follow a tree of datasets and return a datapoint.

        Parameters
        ----------
        name : str
            The name of the datasets to follow and the datapoint to return of the form
            `<intermediate dataset>/<intermediate dataset>/<...>/<datapoint>`.

        Returns
        -------
        AbstractDatapoint
            The datapoint object.

        Raises
        ------
        DoesNotExistError
            If any of the intermediate datasets or the datapoint does not exist.

        """
        name_list = name.split("/")
        dataset = self.recursively_get_dataset("/".join(name_list[:-1]))

        return dataset.get_datapoint(name_list[-1])


class _AbstractHasDataAndFilesMixin(abc.ABC):
    """An abstract mixin for classes that can contain data and files.

    The data must be a key-value pair store (dictionary) that is JSON serialisable.
    """

    @property
    @abc.abstractmethod
    def data(self) -> dict[str, Any]: ...

    @abc.abstractmethod
    def add_data(self, new_data: dict[str, Any]) -> None:
        """Add new data to the object.

        Adding new data does not remove old data unless a key already exists,
        in which case the old data of that key is overwritten by the newer data.

        Parameters
        ----------
        new_data : dict[str, Any]
            New data, in key-value form, to be added to this objects data store.

        """

    @property
    @abc.abstractmethod
    def files(self) -> Sequence[str]:
        """The list of file names (including extensions)."""

    @abc.abstractmethod
    def get_file(self, name: str) -> Path:
        """Return the path to the file with the given name.

        Parameters
        ----------
        name : str
            The name of the file (including its extension)

        Returns
        -------
        Path
            The path to the file (read-only).

        Raises
        ------
        DoesNotExistError
            If a file with the given name does not exist.

        """

    @abc.abstractmethod
    def has_file(self, name: str) -> bool:
        """Return a bool indicating whether the file with the given name exists.

        The name must include the file extension.
        """

    @abc.abstractmethod
    def add_file(self, file: Path, *, name: str | None = None) -> None:
        """Add a file to be managed by this object.

        Files are copied into the database and should be treated therein as read-only.
        They can be 'modified' by re-adding an updated file with the same name.

        Parameters
        ----------
        file : Path
            A path to the file to add to this object.
        name : str | None, optional
            Give the file a new name (include the extension).

        Raises
        ------
        DoesNotExistError
            If the file does not exist or is not a file (e.g. it is a directory).

        InvalidNameError
            If the filename contains invalid characters. The filename may not be checked
            if a name is not explicitly provided.

        """
        if name is not None:
            invalid_chars = set(name) - VALID_NAME_CHARACTERS
            if len(invalid_chars) > 0:
                error_msg = f"Filename contains invalid characters: {invalid_chars}"
                raise InvalidNameError(error_msg)


class _TreeNode(abc.ABC):
    """Abstract base class for all 'nodes' in the HARDS tree."""

    @property
    def is_database(self) -> bool:
        """True if the object is the database (root node).

        False by default.
        """
        return False

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """The objects name."""

    @property
    @abc.abstractmethod
    def parent(self) -> Optional["_TreeNode"]:
        """The object's parent."""

    def database(self) -> "_TreeNode":
        """Recursively find the database."""
        return self.parent.database()

    def path_to_database(self) -> list[str]:
        """Return the names of this object and the intermediates to the database."""
        names = []
        node = self

        while not node.is_database:
            names.append(node.name)
            node = node.parent

        return names[::-1]

    def fullname(self) -> str:
        """Return full name of the object.

        This is the name that, when calling a recursive get method on the database
        would return a new instantiation of this object.
        """
        return "/".join(self.path_to_database())


class AbstractDatabase(_TreeNode, _AbstractHasChildrenDatasetsMixin):
    """Abstract base class for a Database.

    A database defines the root node of the hierarchical data management tree.
    """

    @property
    def is_database(self) -> bool:
        """Returns true because this object does represent a database."""
        return True

    @property
    def parent(self) -> Optional["_TreeNode"]:
        """The object's parent."""
        return None

    def database(self) -> "AbstractDatabase":
        """Return the database (this object)."""
        return self


class AbstractDataset(
    _TreeNode,
    _AbstractHasChildrenDatasetsMixin,
    _AbstractHasDataAndFilesMixin,
):
    """Abstract base class for a Dataset.

    A dataset contains (meta)data and several datapoints that form the dataset.

    Datasets have a parent from whom they inherit additional datapoints (except for when
    the parent is the Database). It follows that Datasets can have many children which
    share their data.
    """

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """The objects name."""

    @property
    @abc.abstractmethod
    def datapoints(self) -> Sequence[str]:
        """The names of the Dataset's current datapoints."""

    @abc.abstractmethod
    def get_datapoint(self, name: str) -> "AbstractDatapoint":
        """Get the datapoint with a given name.

        Parameters
        ----------
        name : str
            The name of the datapoint.

        Returns
        -------
        AbstractDatapoint
            The datapoint object.

        Raises
        ------
        DoesNotExistError
            If the datapoint does not exist.

        """

    @abc.abstractmethod
    def has_datapoint(self, name: str) -> bool:
        """Indicate if the object has a datapoint with the given name."""

    @abc.abstractmethod
    def create_datapoint(self, name: str) -> "AbstractDatapoint":
        """Create and return a datapoint with a given name.

        Parameters
        ----------
        name : str
            The name of the new datapoint.

        Returns
        -------
        AbstractDatapoint
            The new object.

        Raises
        ------
        AlreadyExistsError
            If a datapoint with the same name exists.
        InvalidNameError
            If the datapoint name contains invalid characters.

        """
        invalid_chars = set(name) - VALID_NAME_CHARACTERS
        if len(invalid_chars) > 0:
            error_msg = f"Datapoint name contains invalid characters: {invalid_chars}"
            raise InvalidNameError(error_msg)

    def recursively_get_datapoints(
        self, *, reconstruct: bool = True, parents: bool = True
    ) -> list["AbstractDatapoint"]:
        """Get all datapoints of this dataset and its parents (iff parents is True).

        Follows the parents until the database, collecting their datapoints.

        Parameters
        ----------
        reconstruct : bool
            Reconstruct the entire tree above this object and re-calls this method on
            a new instance of this dataset. This mitigates the situation where this
            datasets parent has been modified in another instance. This makes this
            method safe in single-threaded synchronous applications but makes no
            guarantees about parallel or asynchronous applications.

        parents : bool
            If False, only the datapoints for this dataset are returned. Ie this method
            acts as a safe way to get the instantiated datapoints of this dataset only.

        Notes
        -----
        Reconstruction does not guarantee the safety of this method. See the relevant
        documentation sections for considerations.

        """
        if reconstruct:
            db = self.database()
            path_to_db = self.path_to_database()
            this_dataset = db.recursively_get_dataset("/".join(path_to_db))
            return this_dataset.recursively_get_datapoints(
                reconstruct=False, parents=parents
            )

        datapoints = [self.get_datapoint(name) for name in self.datapoints]

        if not parents:
            return datapoints

        if self.parent.is_database:
            return datapoints

        # safe is False here because the first time the method is called with
        # safe the entire tree is reconstructed and is therefore safe.
        return datapoints + self.parent.recursively_get_datapoints(
            reconstruct=False, parents=parents
        )


class AbstractDatapoint(_TreeNode, _AbstractHasDataAndFilesMixin):
    """Abstract base class for a Datapoint."""

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """The objects name."""

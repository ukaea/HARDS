"""A filesystem implementation of the abstract hierarchical data management API.

Generally the only object that should be instantiated by the user is the
FilesystemDatabase. Databases and datapoints should be instantiated by calling methods
on the database (and subsequently databases) which will handle other object
instantiations.
"""

import json
import shutil
from pathlib import Path
from typing import Any, Union

from .api import (
    AbstractDatabase,
    AbstractDatapoint,
    AbstractDataset,
    AlreadyExistsError,
    DoesNotExistError,
    HARDSError,
)

_CHILDREN_DIRECTORY_NAME = "children"
_DATAPOINTS_DIRECTORY_NAME = "datapoints"
_DATA_FILE_NAME = "data.json"
_FILES_DIRECTORY_NAME = "files"


def _error_msg_missing(
    location: Path,
    missing: str,
    class_name: str,
    missing_type: str = "directory",
) -> str:
    return (
        f"{location} does not contain a '{missing}' {missing_type} "
        f"which is required for it to be a '{class_name}'."
    )


class FilesystemError(HARDSError):
    """An error arising from the filesystem implementation of the abstract API."""


class _FilesystemHasChildrenMixin:
    def _load_children(self, location: Path) -> None:
        self._children_location = location / _CHILDREN_DIRECTORY_NAME
        # check that this directory is a database
        if not self._children_location.exists():
            error_msg = _error_msg_missing(
                location,
                _CHILDREN_DIRECTORY_NAME,
                self.__class__.__name__,
            )
            raise FilesystemError(error_msg)

        self._children = [
            directory.stem for directory in self._children_location.glob("*/")
        ]

    @property
    def children(self) -> list[str]:
        return self._children

    def has_dataset(self, name: str) -> bool:
        return name in self._children

    def get_dataset(self, name: str) -> "FilesystemDataset":
        """Return a dataset that is a child of this object.

        Parameters
        ----------
        name : str
            The name of the dataset to get

        Returns
        -------
        FilesystemDataset
            The dataset with the given name.

        Raises
        ------
        DoesNotExistError
            If a dataset with the given name does not exist.

        """
        dataset_location = self._children_location / name

        if not dataset_location.exists():
            error_msg = f"Database does not contain dataset {name}"
            raise DoesNotExistError(error_msg)

        return FilesystemDataset(dataset_location, self)

    def create_dataset(self, name: str) -> "FilesystemDataset":
        """Create a dataset as a child of this object.

        Parameters
        ----------
        name : str
            The name of the new dataset.

        Returns
        -------
        FilesystemDataset
            The new dataset object.

        Raises
        ------
        AlreadyExistsError
            If a database with the same name already exists.
        InvalidNameError
            If the dataset name contains invalid character.

        """
        super().create_dataset(name)
        dataset_location = self._children_location / name

        if dataset_location.exists():
            error_msg = f"Dataset {name} already exists."
            raise AlreadyExistsError(error_msg)

        dataset_location.mkdir()

        children_location = dataset_location / _CHILDREN_DIRECTORY_NAME
        datapoints_location = dataset_location / _DATAPOINTS_DIRECTORY_NAME
        files_location = dataset_location / _FILES_DIRECTORY_NAME
        datafile_location = dataset_location / _DATA_FILE_NAME

        children_location.mkdir()
        datapoints_location.mkdir()
        files_location.mkdir()

        with datafile_location.open("w") as f:
            json.dump({}, f)

        self._children.append(name)

        return FilesystemDataset(dataset_location, self)


class _FilesystemHasDataMixin:
    def _load_data(self, location: Path) -> None:
        self._data_file = location / _DATA_FILE_NAME
        if not self._data_file.exists():
            error_msg = _error_msg_missing(
                location,
                _DATA_FILE_NAME,
                self.__class__.__name__,
                "file",
            )
            raise FilesystemError(error_msg)

        with self._data_file.open("r") as f:
            self._data = json.load(f)

    @property
    def data(self) -> dict[str, Any]:
        return self._data

    def add_data(self, new_data: dict[str, Any]) -> None:
        self._data = {**self._data, **new_data}

        with self._data_file.open("w") as f:
            json.dump(self._data, f)


class _FilesystemHasFilesMixin:
    def _load_files(self, location: Path) -> None:
        self._files_location = location / _FILES_DIRECTORY_NAME

        if not self._files_location.exists():
            error_msg = _error_msg_missing(
                location,
                _FILES_DIRECTORY_NAME,
                self.__class__.__name__,
            )
            raise FilesystemError(error_msg)

        self._files = [directory.name for directory in self._files_location.glob("*")]

    @property
    def files(self) -> list[str]:
        return self._files

    def has_file(self, name: str) -> bool:
        return name in self._files

    def get_file(self, name: str) -> Path:
        location = self._files_location / name

        if not location.exists():
            error_msg = f"Object does not manage a file {name}"
            raise DoesNotExistError(error_msg)

        return location

    def add_file(self, file: Path, *, name: str | None = None) -> None:
        super().add_file(file, name=name)
        if not file.exists() or not file.is_file:
            error_msg = (
                f"File at location {file} does not exist"
                "(it could exist but not be a file)."
            )
            raise DoesNotExistError(error_msg)

        new_name = name or file.name
        destination = self._files_location / new_name

        shutil.copy2(file, destination, follow_symlinks=True)
        Path(destination).chmod(0o400)
        self._files.append(new_name)


class FilesystemDatabase(
    _FilesystemHasChildrenMixin,
    AbstractDatabase,
):
    """Database represented by a directory on the filesystem."""

    @classmethod
    def create_database(cls, location: Path) -> "FilesystemDatabase":
        """Create a database at the given location in the filesystem.

        Parameters
        ----------
        location : Path
            The location to create the directory that will represent the database.

        Returns
        -------
        FilesystemDatabase
            The new database object.

        """
        location.mkdir(parents=True)

        children_dir = location / _CHILDREN_DIRECTORY_NAME
        children_dir.mkdir()

        return cls(location)

    def __init__(self, location: Path) -> None:
        """Initialise a filesystem database.

        Parameters
        ----------
        location : Path
            The location of the directory that represents the database.

        """
        self._load_children(location)
        self._location = location

    @property
    def name(self) -> str:  # noqa: D102
        return self._location.stem


class FilesystemDataset(
    _FilesystemHasFilesMixin,
    _FilesystemHasDataMixin,
    _FilesystemHasChildrenMixin,
    AbstractDataset,
):
    """Dataset represented by a directory on the filesystem."""

    def __init__(
        self,
        location: Path,
        parent: Union[FilesystemDatabase, "FilesystemDataset"],
    ) -> None:
        """Initialise a filesystem dataset.

        Parameters
        ----------
        location : Path
            The location of the directory that represents the dataset.
        parent : FilesystemDatabase | FilesystemDataset
            The parent object of this dataset.

        """
        self._load_files(location)
        self._load_data(location)
        self._load_children(location)

        self._location = location
        self._parent = parent

        self._datapoints_location = location / _DATAPOINTS_DIRECTORY_NAME

        if not self._datapoints_location.exists():
            error_msg = _error_msg_missing(
                location,
                _DATAPOINTS_DIRECTORY_NAME,
                self.__class__.__name__,
            )
            raise FilesystemError(error_msg)

        self._datapoints = [
            directory.stem for directory in self._datapoints_location.glob("*/")
        ]

    @property
    def parent(self) -> Union[FilesystemDatabase, "FilesystemDataset"]:
        """Return the parent of the Datset."""
        return self._parent

    @property
    def name(self) -> str:  # noqa: D102
        return self._location.stem

    @property
    def datapoints(self) -> list[str]:  # noqa: D102
        return self._datapoints

    def has_datapoint(self, name: str) -> bool:  # noqa: D102
        return name in self._datapoints

    def get_datapoint(self, name: str) -> "FilesystemDatapoint":
        """Get the datapoint with a given name.

        Parameters
        ----------
        name : str
            The name of the datapoint.

        Returns
        -------
        FilesystemDatapoint
            The datapoint object.

        Raises
        ------
        DoesNotExistError
            If the datapoint does not exist.

        """
        datapoint_location = self._datapoints_location / name

        if not datapoint_location.exists():
            error_msg = f"Dataset does not contain datapoint {name}"
            raise DoesNotExistError(error_msg)

        return FilesystemDatapoint(datapoint_location, self)

    def create_datapoint(self, name: str) -> "FilesystemDatapoint":
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
        super().create_datapoint(name)
        datapoint_location = self._datapoints_location / name

        if datapoint_location.exists():
            error_msg = f"Datapoint {name} already exists."
            raise AlreadyExistsError(error_msg)

        datapoint_location.mkdir()

        files_location = datapoint_location / _FILES_DIRECTORY_NAME
        files_location.mkdir()

        datafile_location = datapoint_location / _DATA_FILE_NAME
        with datafile_location.open("w") as f:
            json.dump({}, f)

        self._datapoints.append(name)

        return FilesystemDatapoint(datapoint_location, self)


class FilesystemDatapoint(
    _FilesystemHasFilesMixin, _FilesystemHasDataMixin, AbstractDatapoint
):
    """Datapoint represented by a directory on the filesystem."""

    def __init__(self, location: Path, parent: FilesystemDataset) -> None:
        """Initialise a filesystem datapoint.

        Parameters
        ----------
        location : Path
            The location of the directory that represents the datapoint.
        parent : FilesystemDataset
            The parent object of this datapoint.

        """
        self._load_files(location)
        self._load_data(location)

        self._location = location
        self._parent = parent

    @property
    def name(self) -> str:
        """The name of the datapoint."""
        return self._location.stem

    @property
    def parent(self) -> FilesystemDataset:
        """The parent Dataset of this Datapoint."""
        return self._parent

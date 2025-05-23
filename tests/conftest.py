"""Configures pytest and provides fixtures to the entire test suite."""

import shutil
from pathlib import Path

import pytest

from hards.filesystem import FilesystemDatabase, FilesystemDataset


@pytest.fixture
def data_assets(tmp_path) -> Path:
    """Copy the `data_assets` folder into a temporary directory and return the path."""
    data_assets_dir = Path(__file__).parent / "data_assets"

    return shutil.copytree(data_assets_dir, tmp_path / "data_assets")


@pytest.fixture
def filesystem_db(tmp_path) -> FilesystemDatabase:
    return FilesystemDatabase.create_database(tmp_path / "test_db")


@pytest.fixture
def filesystem_dataset(filesystem_db) -> FilesystemDataset:
    return filesystem_db.create_dataset("test_dataset")

"""Tests for the `FilesystemDatabase` class."""

import pytest

from hards.filesystem import AlreadyExistsError, DoesNotExistError, FilesystemDatabase


def test_directories_created(tmp_path):
    # don't use the fixture here because we essentially test what it does
    db_location = tmp_path / "test_db"
    db_children_location = db_location / "children"

    db = FilesystemDatabase.create_database(db_location)

    assert db_location.exists()
    assert db_children_location.exists()
    assert db._location.exists()
    assert db._location == db_location
    assert db._children_location.exists()
    assert db._children_location == db_children_location


def test_new_database_empty(filesystem_db):
    assert len(filesystem_db.children) == 0
    assert len(filesystem_db._children) == 0


def test_error_on_dataset_not_existing(filesystem_db):
    with pytest.raises(DoesNotExistError):
        filesystem_db.get_dataset("test_dataset")


def test_error_on_dataset_existing(filesystem_db):
    filesystem_db.create_dataset("test_dataset")
    with pytest.raises(AlreadyExistsError):
        filesystem_db.create_dataset("test_dataset")


def test_creating_dataset(filesystem_db):
    assert not filesystem_db.has_dataset("test_dataset")

    dataset = filesystem_db.create_dataset("test_dataset")

    assert filesystem_db.has_dataset("test_dataset")
    assert len(filesystem_db.children) == 1
    assert filesystem_db.get_dataset("test_dataset")._location == dataset._location

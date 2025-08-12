"""Tests for the `FilesystemDataset` class."""

import pytest

from hards.api import InvalidNameError


def test_created_correctly(filesystem_db):
    # do not use the dataset fixture becase we test it will work properly
    dataset = filesystem_db.create_dataset("test_dataset")
    dataset_location = filesystem_db._location / "children/test_dataset"
    dataset_children_location = dataset_location / "children"
    dataset_datapoints_location = dataset_location / "datapoints"
    dataset_datafile_location = dataset_location / "data.json"
    dataset_files_location = dataset_location / "files"

    assert dataset_location.exists()
    assert dataset._location.exists()
    assert dataset_location == dataset._location
    assert dataset_children_location.exists()
    assert dataset_datapoints_location.exists()
    assert dataset_datafile_location.exists()
    assert dataset_files_location.exists()
    assert dataset.parent is filesystem_db
    assert len(dataset.children) == 0
    assert len(dataset.datapoints) == 0
    assert len(dataset.files) == 0
    assert dataset.data == {}
    assert not dataset.has_dataset("random_dataset")
    assert not dataset.has_datapoint("random_datapoint")


def test_child_dataset(filesystem_dataset):
    child_dataset = filesystem_dataset.create_dataset("test_sub_dataset")

    assert len(filesystem_dataset.children) == 1
    assert child_dataset._location.exists()
    assert child_dataset.parent is filesystem_dataset


def test_dataset_data(filesystem_dataset):
    filesystem_dataset.add_data({"test_data": 1})

    assert len(filesystem_dataset.data) == 1
    assert filesystem_dataset.data["test_data"] == 1


def test_dataset_additional_data(filesystem_dataset):
    filesystem_dataset.add_data({"test_data": 1})
    filesystem_dataset.add_data({"more_test_data": "abcd"})

    assert len(filesystem_dataset.data) == 2
    assert filesystem_dataset.data["test_data"] == 1
    assert filesystem_dataset.data["more_test_data"] == "abcd"


def test_dataset_files(filesystem_dataset, data_assets):
    filesystem_dataset.add_file(data_assets / "example_file.dat")

    assert len(filesystem_dataset.files) == 1
    assert "example_file.dat" in filesystem_dataset.files
    assert filesystem_dataset.has_file("example_file.dat")
    with filesystem_dataset.get_file("example_file.dat").open() as f:
        assert f.read() == "file data!\n"


def test_dataset_files_overwrite(filesystem_dataset, data_assets):
    filesystem_dataset.add_file(data_assets / "example_file.dat")
    filesystem_dataset.add_file(data_assets / "example_file.dat")
    assert filesystem_dataset.has_file("example_file.dat")


def test_dataset_files_permissions(filesystem_dataset, data_assets):
    filesystem_dataset.add_file(data_assets / "example_file.dat", permissions=0o400)
    assert filesystem_dataset.has_file("example_file.dat")

    with pytest.raises(PermissionError):
        filesystem_dataset.add_file(data_assets / "example_file.dat")


def test_dataset_same_from_scratch(filesystem_dataset):
    filesystem_dataset.add_data({"test_data_1": 2e4, "test_data_2": 1.4})

    db = filesystem_dataset.database()
    alt_dataset = db.get_dataset("test_dataset")

    assert alt_dataset._location == filesystem_dataset._location
    assert alt_dataset.data == filesystem_dataset.data


def test_error_on_invalid_dataset_name(filesystem_db):
    with pytest.raises(InvalidNameError):
        filesystem_db.create_dataset("file*")


def test_error_on_invalid_file_name(filesystem_dataset, data_assets):
    with pytest.raises(InvalidNameError):
        filesystem_dataset.add_file(
            data_assets / "example_file.dat", name="invalid(filename).txt"
        )

"""Tests for the `FilesystemDatapoint` class."""

import pytest

from hards.api import InvalidNameError


def test_datapoint_created(filesystem_dataset):
    datapoint = filesystem_dataset.create_datapoint("datapoint1")

    assert datapoint.parent is filesystem_dataset
    assert datapoint.database() is filesystem_dataset.database()
    assert datapoint._files_location.exists()
    assert len(datapoint.data) == 0


def test_path_to_database(filesystem_dataset):
    child_dataset = filesystem_dataset.create_dataset("child_dataset")
    datapoint = child_dataset.create_datapoint("datapoint")

    assert datapoint.path_to_database() == [
        "test_dataset",
        "child_dataset",
        "datapoint",
    ]


def test_error_on_invalid_datapoint_name(filesystem_dataset):
    with pytest.raises(InvalidNameError):
        filesystem_dataset.create_datapoint("d&tapoint")

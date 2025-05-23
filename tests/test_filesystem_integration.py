"""Test the integration of the filesystem database management."""


def test_recursive_datapoints(filesystem_dataset):
    child_dataset = filesystem_dataset.create_dataset("child_dataset")

    filesystem_dataset.create_datapoint("datapoint1")
    filesystem_dataset.create_datapoint("datapoint2")

    assert len(filesystem_dataset.datapoints) == 2

    child_dataset.create_datapoint("datapoint3")
    child_dataset.create_datapoint("datapoint4")
    child_dataset.create_datapoint("datapoint5")

    assert len(child_dataset.datapoints) == 3

    assert len(filesystem_dataset.recursively_get_datapoints()) == 2
    assert len(child_dataset.recursively_get_datapoints()) == 5


def test_recursive_datapoint(filesystem_dataset):
    child_dataset = filesystem_dataset.create_dataset("child_dataset")
    datapoint = child_dataset.create_datapoint("datapoint1")

    assert (
        child_dataset.database()
        .recursively_get_datapoint("test_dataset/child_dataset/datapoint1")
        ._location
        == datapoint._location
    )
    assert (
        child_dataset.database()
        .recursively_get_datapoint(datapoint.fullname())
        ._location
        == datapoint._location
    )


def test_recursive_dataset(filesystem_db):
    dataset = filesystem_db.create_dataset("test_dataset")
    sub_dataset = dataset.create_dataset("test_sub_dataset")
    sub_sub_dataset = sub_dataset.create_dataset("test_sub2_dataset")

    assert (
        filesystem_db.recursively_get_dataset("test_dataset")._location
        == filesystem_db.get_dataset("test_dataset")._location
    )

    assert (
        filesystem_db.recursively_get_dataset("test_dataset/")._location
        == filesystem_db.get_dataset("test_dataset")._location
    )

    assert (
        filesystem_db.recursively_get_dataset("test_dataset//")._location
        == filesystem_db.get_dataset("test_dataset")._location
    )

    assert (
        sub_sub_dataset._location
        == filesystem_db.recursively_get_dataset(
            "test_dataset/test_sub_dataset/test_sub2_dataset"
        )._location
    )


def test_recursive_datapoint_is_safe(filesystem_db):
    dataset = filesystem_db.create_dataset("test_dataset")
    sub_dataset = dataset.create_dataset("sub_test_dataset")
    sub_sub_dataset = sub_dataset.create_dataset("sub_sub_test_dataset")

    assert len(sub_sub_dataset.recursively_get_datapoints()) == 0
    assert len(sub_sub_dataset.path_to_database()) == 3

    alternative_sub_dataset = filesystem_db.recursively_get_dataset(
        "/".join(sub_dataset.path_to_database())
    )
    assert alternative_sub_dataset._location == sub_dataset._location

    # create a datapoint in the second instance that should be invisible
    alternative_sub_dataset.create_datapoint("3_but_isnt_seen")

    # now create some datapoints in the main tree
    dataset.create_datapoint("1")
    dataset.create_datapoint("2")
    sub_dataset.create_datapoint("4")
    sub_dataset.create_datapoint("5")
    sub_sub_dataset.create_datapoint("6")

    assert (
        len(dataset.recursively_get_datapoints(reconstruct=True))
        == len(dataset.recursively_get_datapoints(reconstruct=False))
        == 2
    )
    # should be 5
    assert len(sub_dataset.recursively_get_datapoints(reconstruct=False)) == 4
    # should be 6
    assert len(sub_sub_dataset.recursively_get_datapoints(reconstruct=False)) == 5

    # now lets check that the safe methods catch the correct number
    assert len(sub_dataset.recursively_get_datapoints(reconstruct=True)) == 5
    assert len(sub_sub_dataset.recursively_get_datapoints(reconstruct=True)) == 6

    # final check that doing this also works on the alternative instance of the dataset
    assert (
        len(alternative_sub_dataset.recursively_get_datapoints(reconstruct=False)) == 1
    )
    assert (
        len(alternative_sub_dataset.recursively_get_datapoints(reconstruct=True)) == 5
    )

    # check when parents is False
    assert (
        len(sub_sub_dataset.recursively_get_datapoints(reconstruct=True, parents=False))
        == 1
    )

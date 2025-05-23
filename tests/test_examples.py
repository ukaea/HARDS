"""Run example notebooks to ensure they never break."""

from pathlib import Path

import pytest
from testbook import testbook

EXAMPLE_NOTEBOOKS = list((Path(__file__).parent / "../examples").glob("*.ipynb"))


@pytest.mark.parametrize(
    "notebook", EXAMPLE_NOTEBOOKS, ids=[i.stem for i in EXAMPLE_NOTEBOOKS]
)
def test_example_notebooks(notebook):
    with testbook(notebook, execute=True, timeout=60):
        # no assertions because we just check the files run without error
        pass

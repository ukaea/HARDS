# Hierarchical ARbitrary Data Storage: HARDS
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Testing Workflow](https://github.com/ukaea/HARDS/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/ukaea/HARDS/actions/workflows/tests.yml)


An API and corresponding simple filesystem implementation for managing hierarchical datasets in Python.


## Installation
HARDS can be installed using `pip` by running:
```shell
pip install hards
```

Developers may wish to install HARDS from source:
```shell
git clone https://github.com/ukaea/HARDS.git
cd HARDS
pip install .
```

This makes the `hards` package (and its modules) available for importing into other Python libraries/scripts.

## Examples
Examples of using `hards` can be found in the `examples` directory. To run the notebooks, install HARDS from source and ensure the `examples` dependencies are installed in your Python environment by running:
```shell
pip install .'[examples]'
```
in the root project directory.

## Development
Development dependencies can be installed by running the following inside of the root project directory:
```shell
pip install .'[dev]'
```

You can then test the code by running:
```shell
pytest
```

You can lint and format the code by running:
```shell
ruff check
ruff format
```

Before commiting any changes, you should install the `pre-commit` hook by running:
```shell
pre-commit install
```
which will then ensure the code passes the lint and format checks before allowing the commit.

## Acknowledgements
This work was funded by the EPSRC Energy Programme [grant number EP/W006839/1]. To obtain further information, please contact [PublicationsManager@ukaea.uk](mailto:PublicationsManager@ukaea.uk).

## License
HARDS is provided under the MIT license, please see the LICENSE file for full details.

Copyright (c) 2025 UK Atomic Energy Authority

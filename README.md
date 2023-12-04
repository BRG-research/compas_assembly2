# COMPAS ASSEMBLY2


## Example



```python

from compas.geometry import Point
from compas_assembly2 import Element
from compas_assembly2 import Model


if __name__ == "__main__":
    # create model
    model = Model()

    # add group nodes - a typical tree node with a name and geometry
    car = model.add_group(name="car", geometry=None)  # type: ignore
    wheel = car.add_group(name="wheel", geometry=Point(0, 0, 0))  # type: ignore

    # add element nodes - a "special" tree node with a name and element
    spoke1 = wheel.add_element(name="spoke1", element=Element.from_frame(1, 10, 1))  # type: ignore
    spoke2 = wheel.add_element(name="spoke2", element=Element.from_frame(5, 10, 1))  # type: ignore
    spoke3 = wheel.add_element(name="spoke3", element=Element.from_frame(10, 10, 1))  # type: ignore

    # add interactions
    model.add_interaction(spoke1, spoke2)
    model.add_interaction(spoke1, spoke3)
    model.add_interaction(spoke2, spoke3)

    # print the model to preview the tree structure
    model.print()

```

## Getting started with this project

### Setup code editor

1. Open project folder in VS Code
2. Select python environment for the project
3. First time using VS Code and on Windows? Make sure select the correct terminal profile: `Ctrl+Shift+P`, `Terminal: Select Default Profile` and select `Command Prompt`.

> All terminal commands in the following sections can be run from the VS Code integrated terminal. 


### First steps with git

1. Go to the `Source control` tab
2. Make an initial commit with all newly created files


### First steps with code

1. Install the newly created project 

        pip install -e .

2. Install it on Rhino

        python -m compas_rhino.install


### Code conventions

Code convention follows [PEP8](https://pep8.org/) style guidelines and line length of 120 characters.

1. Check adherence to style guidelines

        invoke lint

2. Format code automatically

        invoke format


### Documentation

Documentation is generated automatically out of docstrings and [RST](https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html) files in this repository

1. Generate the docs

        invoke docs

2. Check links in docs are valid

        invoke linkcheck

3. Open docs in your browser (file explorer -> `dist/docs/index.html`)


### Testing

Tests are written using the [pytest](https://docs.pytest.org/) framework

1. Run all tests from terminal

        invoke test

2. Or run them from VS Code from the `Testing` tab


### Developing Grasshopper components

We use [Grasshopper Componentizer](https://github.com/compas-dev/compas-actions.ghpython_components) to develop Python components that can be stored and edited on git.

1. Build components

        invoke build-ghuser-components

2. Install components on Rhino

        python -m compas_rhino.install


### Publish release

Releases follow the [semver](https://semver.org/spec/v2.0.0.html) versioning convention.

1. Create a new release

        invoke release major


<!-- 
![build](https://github.com/compas-dev/compas_cgal/workflows/build/badge.svg)
[![GitHub - License](https://img.shields.io/github/license/compas-dev/compas_cgal.svg)](https://github.com/compas-dev/compas_cgal)
[![Conda - Latest Release](https://anaconda.org/conda-forge/compas_cgal/badges/version.svg)](https://anaconda.org/conda-forge/compas_cgal)
[![Conda - Platform](https://img.shields.io/conda/pn/conda-forge/compas_cgal)](https://anaconda.org/conda-forge/compas_cgal)

This package provides Python bindings for specific algorithms of CGAL.
The bindings are generated with PyBind11 and data is exchanged using NumPy arrays.

More information is available in the docs:
<https://compas.dev/compas_cgal/>

## Installation

`compas_cgal` is available via `conda-forge` for Windows, OSX, and Linux,
and can be installed using `conda`.

```bash
conda create -n cgal -c conda-forge compas compas_cgal --yes
```

## Dev Install

Create a development environment with the required dependencies using `conda`
and compile and install an editable version of `compas_cgal` using `setuptools`.

**Windows**:

```bash
conda create -n cgal-dev python=3.8 mpir mpfr boost-cpp eigen=3.3 cgal-cpp=5.2 pybind11 compas compas_view2 --yes
conda activate cgal-dev
git clone https://github.com/compas-dev/compas_cgal
cd compas_cgal
pip install -e .
```

**Mac**:

```bash
conda create -n cgal-dev python=3.8 gmp mpfr boost-cpp eigen=3.3 cgal-cpp=5.2 pybind11 compas compas_view2 --yes
conda activate cgal-dev
git clone https://github.com/compas-dev/compas_cgal
cd compas_cgal
pip install -e .
```

> Note that the version of eigen is important and should be `3.3`.

To add a new c++ module to the Python wrapper, or to exclude some of the existing modules during development
you can modify the list of extension modules in `setup.py`.

```python
ext_modules = [
    Extension(
        'compas_cgal._cgal',
        sorted([
            'src/compas_cgal.cpp',
            'src/compas.cpp',
            'src/meshing.cpp',
            'src/booleans.cpp',
            'src/slicer.cpp',
            'src/intersections.cpp',
            'src/measure.cpp',
        ]),
        include_dirs=[
            './include',
            get_eigen_include(),
            get_pybind_include()
        ],
        library_dirs=[
            get_library_dirs(),
        ],
        libraries=['mpfr', 'gmp'],
        language='c++'
    ),
]
```

## Usage

The provided functionality can be used directly from the `compas_cgal` package
or from `compas.geometry` through the plugin mechanism in COMPAS.

For examples, see <https://compas.dev/compas_cgal/latest/examples.html>.

## License

`compas_cgal` is released under the LGPL 3.0 to be compatible with the license of CGAL. -->

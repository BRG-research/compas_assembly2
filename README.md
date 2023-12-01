# compas_assembly2

This package use compas>=2.0.0a1.

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

## TODO

- [ ] Create different Element classes e.g. Beam, Plate, Block, Glulam, etc. Use OCC for curved geometries
- [ ] Fast Tree search that is native to Python
- [ ] Go over the other assembly data-structure.

A data structure is needed to represent a model consisting of structural elements like blocks, beams, nodes, and plates, as well as fabrication elements for subtractive and additive processes. This data structure should also facilitate the computation and storage of adjacency and joinery information, as well as interfaces between these elements. Additionally, it should allow for the transfer of data between the model, structural simulation, and fabrication processes.

* BOOK-KEEPING OBJECTS IN AN ORDERED COLLECTION WITH SELECTION LOGIC In many packages elements, joints are stored in a simple list without any functionality that could help assembly data-structure. The list itself can be changed to something else, e.g. an OrderedList since for example we never randomly fabricate elements, but start from the first item and gradually iterate, these indices can serve as element tags too. A collection can have grouping functionality and selection methods for retrieving objects based on element or joint attributes. For example, we want to output an element fabrication toolpath, structural data or highlight objects by type such as Blocks or Beams.

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

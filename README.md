# compas_assembly2

## TODO


- [ ] Assembly.py review the "add_element_by_index" method. Example, elements are added not by element index, but assemblies can be created by b) adding assemblies within the assembly, c) manually grouping when first grandchilds are created and then childs can be added, then parents, so it is a reversed scheme.
- [ ] Create different Element classes e.g. Beam, Plate, Block, Glulam, etc. Use OCC for curved geometries
- [ ] Element.py - Interface detection using compas_assembly shapely library for outlines for complex
- [ ] Element.py - Interace detection using Line and Polyline proximity for simplex
- [ ] Fast Tree search that is native to Python
- [ ] Test and Viewer - Insertion vectors
- [ ] Assembly.py - start drafting the assembly data-strcuture, by including the collide method that otput collision pairs, for simple implementation use 2xfor loop, once you find fast tree, you will be able to enhance (do not forget serialozation)
- [ ] implmement other assemblies to check how well the data structure is currently been developed.
- [ ] test_6_block_flat_arch_plates_boxes.py example shows clearly the need of grouping into boxes e.g. (0,0) (0,1) ..., there can be in a viewer selection by group depending on an index -> hierarchy 0, 1, 2 that shows the partitioning thing, there can be groups of boxes too.

A data structure is needed to represent a model consisting of structural elements like blocks, beams, nodes, and plates, as well as fabrication elements for subtractive and additive processes. This data structure should also facilitate the computation and storage of adjacency and joinery information, as well as interfaces between these elements. Additionally, it should allow for the transfer of data between the model, structural simulation, and fabrication processes.

* BOOK-KEEPING OBJECTS IN AN ORDERED COLLECTION WITH SELECTION LOGIC In many packages elements, joints are stored in a simple list without any functionality that could help assembly data-structure. The list itself can be changed to something else, e.g. an OrderedList since for example we never randomly fabricate elements, but start from the first item and gradually iterate, these indices can serve as element tags too. A collection can have grouping functionality and selection methods for retrieving objects based on element or joint attributes. For example, we want to output an element fabrication toolpath, structural data or highlight objects by type such as Blocks or Beams.

![Untitled Diagram drawio](https://github.com/BRG-research/compas_assembly2/assets/18013985/fc6ddbbd-8b30-49be-aa69-705e9e1eee0e)


![image](https://github.com/BRG-research/compas_assembly2/assets/18013985/ef00db99-6557-4fe5-a1cd-39caad9bd7ca)

![image](https://github.com/BRG-research/compas_assembly2/assets/18013985/0ce85ba1-2c01-40d5-8a5b-40f017bd787b)


## TODO

- [ ] Start developing fabrication class from "fabrication"


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

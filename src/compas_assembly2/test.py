from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas.geometry import Point, Frame, Box  # noqa: F401
from compas.datastructures import Mesh  # noqa: F401
from compas_assembly2 import Element
from compas_assembly2 import Model, GroupNode, ElementNode
from compas.data.json import json_dump, json_load


def create_model():

    # create model
    model = Model()

    # add group nodes - a typical tree node with a name and geometry
    car = model.add_group(name="car", geometry=None)  # type: ignore
    wheel = car.add_group(name="wheel", geometry=Point(0, 0, 0))  # type: ignore

    # add element nodes - a "special" tree node with a name and element
    wheel.add_element(name="spoke1", element=Element.from_frame(1, 10, 1))  # type: ignore
    wheel.add_element(name="spoke2", element=Element.from_frame(5, 10, 1))  # type: ignore

    # print the model to preview the tree structure
    model.print()

    # output
    return model


def create_model_with_interactions():

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

    # output
    return model


def create_model_without_hierarchy():

    # create model
    model = Model()

    # add element nodes - a "special" tree node with a name and element
    spoke1 = model.add_element(name="spoke1", element=Element.from_frame(1, 10, 1))  # type: ignore
    spoke2 = model.add_element(name="spoke2", element=Element.from_frame(5, 10, 1))  # type: ignore
    spoke3 = model.add_element(name="spoke3", element=Element.from_frame(10, 10, 1))  # type: ignore

    # add interactions
    model.add_interaction(spoke1, spoke2)
    model.add_interaction(spoke1, spoke3)
    model.add_interaction(spoke2, spoke3)

    # print the model to preview the tree structure
    model.hierarchy.print()
    # model.print()

    # output
    return model


def create_model_tree_operators():

    # ==========================================================================
    # create some elemnts elements
    # ==========================================================================
    elements = []
    for i in range(20):
        element = Element(
            name="beam", geometry=Mesh.from_shape(Box(i + 1, 1, 1, Frame.worldXY())), geometry_simplified=Point(i, 0, 0)
        )
        elements.append(element)

    # ==========================================================================
    # model with a tree structure
    # ==========================================================================
    # create two models - with a tree structure, with a flat structure just with elements
    model = Model()

    # create a few nodes and add them to the model
    structure = model.add_group(name="structure")  # type: ignore

    timber = structure.add_group(name="timber")  # type: ignore
    for i in range(5):
        timber.add_element(element=elements[i])

    concrete = structure.add_group(name="concrete")  # type: ignore
    for i in range(5, 10):
        concrete.add_element(element=elements[i])

    model.add_interaction(elements[0], elements[1])
    model.add_interaction(elements[0], elements[9])
    model.add_interaction(elements[3], elements[9])
    # model.print()

    # ==========================================================================
    # simple model without hierarchy
    # ==========================================================================
    model_simple = Model()
    model_simple.add_element(name="beam", element=elements[0])
    model_simple.add_element(name="beam_bam", element=elements[1])
    model_simple.add_element(name="beam", element=elements[2])
    model_simple.add_interaction(elements[0], elements[1])
    model_simple.add_interaction(elements[0], elements[2])
    # model_simple.print()

    # ==========================================================================
    # getters - root node
    # ==========================================================================
    # print(model["structure"])  # returns a Node of a name "structure"
    # print(model[0])  # returns a Node of a name "structure"
    # print(model[elements[5].guid])
    # print(model[elements[5]])
    # print(model_simple["beam"])  # returns a Node of a name "beam"
    # print(model_simple[0])  # returns a Node of a name "beam"
    # print(model_simple[elements[0].guid])  # returns the parent Node of the ElmentNode that has this element
    # print(model_simple[elements[0]])  # returns the parent Node of the ElmentNode that has this element

    # ==========================================================================
    # getters - other nodes
    # ==========================================================================
    # print(model["structure"]["concrete"])  # returns a Node of a name "timber"
    # print(model[0][1])  # returns a Node of a name "timber"
    # print(model[0][elements[4].guid])  # when quering with guid, the parent of guid is returned
    # print(model[0][elements[4]])  # when quering with guid, the parent of guid is returned, not the element guid¨!

    # ==========================================================================
    # setters - root node
    # ==========================================================================
    new_node = GroupNode("steel")
    for i in range(10, 12):
        new_node.add_element(element=elements[i])

    # model[0] = new_node
    # model["structure"] = new_node
    # model[elements[3]] = elements[10]
    # print(elements[3], elements[10])
    # model[elements[3].guid] = elements[10]
    # model_simple.print()
    # model_simple["beam_bam"] = new_node
    # model_simple[1] = new_node
    # model_simple[elements[0].guid] = elements[10]
    # model_simple[elements[2]] = elements[10]
    # model_simple.print()
    # model.print()

    # ==========================================================================
    # setters - other nodes
    # ==========================================================================
    # model[0][1] = new_node
    # model["structure"]["concrete"] = new_node
    # model[0][elements[4].guid] = elements[10]
    # model[0][1][elements[7]] = elements[10]

    # ==========================================================================
    # get and set Node element by index
    # ==========================================================================
    # model.add_interaction(e0, e1)
    # model.print_interactions()
    # model.hierarchy["structure"]["timber"].set_element(0, e8)
    # model.print_interactions()

    # ==========================================================================
    # of course, there are methods starting with get and set
    # ==========================================================================¨
    model.set_element_by_element(elements[0], elements[10])
    model.get_node_by_element(elements[10])
    model.get_child_by_index(0)
    model.get_child_by_name("concrete")
    return model


def copy_model():
    # ==========================================================================
    # create elements and a Node and a ElementTree and a Model
    # ==========================================================================
    e0 = Element(name="beam", geometry_simplified=Point(0, 0, 0))
    e1 = Element(name="beam", geometry_simplified=Point(0, 5, 0))
    e2 = Element(name="block", geometry_simplified=Point(0, 0, 0))
    e3 = Element(name="block", geometry_simplified=Point(0, 5, 0))

    model = Model()  # the root of hierarchy automatically initializes the root node as <my_model>
    truss1 = model.add_group("truss1")
    truss2 = model.add_group("truss2")
    truss1.add_element(e0)
    truss1.add_element(e1)
    truss2.add_element(e2)
    truss2.add_element(e3)

    model.add_interaction(e0, e1)

    print("BEFORE COPY")
    model.print()
    model.print_interactions()
    # ==========================================================================
    # copy the model
    # ==========================================================================
    print("AFTER COPY")
    model_copy = model.copy()
    model_copy.print()
    model_copy.print_interactions()


def serialize_element():
    # ==========================================================================
    # create elements and a Node
    # ==========================================================================
    e = Element(name="beam", geometry_simplified=Point(0, 0, 0))
    # ==========================================================================
    # serialize the model_node
    # =========================================================================
    print(e)
    json_dump(e, "src/compas_assembly2/data_sets/model/model_how_to_use_it_element.json", pretty=True)
    json_load("src/compas_assembly2/data_sets/model/model_how_to_use_it_element.json")
    print(e)


def serialize_model_node():
    # ==========================================================================
    # create elements and a Node
    # ==========================================================================
    group_node = GroupNode(name="timber1", geometry=Point(0, 0, 0))

    # ==========================================================================
    # serialize the model_node
    # =========================================================================
    json_dump(group_node, "src/compas_assembly2/data_sets/model/model_how_to_use_it_model_node.json", pretty=True)

    # ==========================================================================
    # deserialize the model_node
    # ==========================================================================
    model_node_deserialized = json_load("src/compas_assembly2/data_sets/model/model_how_to_use_it_model_node.json")

    # ==========================================================================
    # print the contents of the deserialized model_node
    # ==========================================================================
    print("model_node:              ", group_node)
    print("model_node_deserialized: ", model_node_deserialized)

    # ==========================================================================
    # create elements and a Node
    # ==========================================================================
    element_node = ElementNode(name="spoke1", element=Element.from_frame(1, 10, 1))  # type: ignore

    # ==========================================================================
    # serialize the model_node
    # =========================================================================
    json_dump(element_node, "src/compas_assembly2/data_sets/model/model_how_to_use_it_model_node.json", pretty=True)

    # ==========================================================================
    # deserialize the model_node
    # ==========================================================================
    element_node_deserialized = json_load("src/compas_assembly2/data_sets/model/model_how_to_use_it_model_node.json")

    # ==========================================================================
    # print the contents of the deserialized model_node
    # ==========================================================================
    print("element_node:              ", element_node, element_node.element.geometry)
    print("element_node_deserialized: ", element_node_deserialized, element_node_deserialized.element.geometry)


def serialize_model_tree():

    # ==========================================================================
    # create model
    # ==========================================================================
    model = create_model()

    # ==========================================================================
    # serialize the model_tree
    # ==========================================================================
    json_dump(model.hierarchy, "src/compas_assembly2/data_sets/model/model_how_to_use_it_model_tree.json", pretty=True)

    # ==========================================================================
    # deserialize the model_tree
    # ==========================================================================
    model_tree_deserialized = json_load("src/compas_assembly2/data_sets/model/model_how_to_use_it_model_tree.json")

    # ==========================================================================
    # print the contents of the deserialized model_tree
    # ==========================================================================
    model.hierarchy.print()
    model_tree_deserialized.print()  # type: ignore


def serialize_model():
    # ==========================================================================
    # create model
    # ==========================================================================
    model = create_model()

    # ==========================================================================
    # serialize the model_tree
    # ==========================================================================
    json_dump(model, "src/compas_assembly2/data_sets/model/model_how_to_use_it_model.json", pretty=True)

    # ==========================================================================
    # deserialize the model_tree
    # ==========================================================================
    model_deserialized = json_load("src/compas_assembly2/data_sets/model/model_how_to_use_it_model.json")

    # ==========================================================================
    # print the contents of the deserialized model_tree
    # ==========================================================================
    model.print()
    model_deserialized.print()


def merge_models():
    # ==========================================================================
    # create elements
    # ==========================================================================
    e0 = Element(name="beam", geometry_simplified=Point(0, 0, 0))
    e1 = Element(name="beam", geometry_simplified=Point(0, 5, 0))
    e2 = Element(name="plate", geometry_simplified=Point(0, 0, 0))
    e3 = Element(name="plate", geometry_simplified=Point(0, 0, 0))
    e4 = Element(name="block", geometry_simplified=Point(0, 5, 0))
    e5 = Element(name="block", geometry_simplified=Point(0, 0, 0))
    e6 = Element(name="block", geometry_simplified=Point(0, 0, 0))

    # ==========================================================================
    # create Model1
    # ==========================================================================
    model1 = Model()  # the root of hierarchy automatically initializes the root node as <my_model>
    structure1 = model1.add_group("structure1")  # type: ignore
    timber1 = structure1.add_group("timber1")  # type: ignore
    timber1.add_element(e0)
    timber1.add_element(e1)
    concrete1 = structure1.add_group("concrete1")  # type: ignore
    concrete1.add_element(e2)
    model1.add_interaction(e0, e1)
    model1.add_interaction(e0, e2)

    # ==========================================================================
    # create Model2
    # ==========================================================================
    model2 = Model()  # the root of hierarchy automatically initializes the root node as <my_model>
    structure1_ = model2.add_group("structure2")  # type: ignore
    timber2_ = structure1_.add_group("timber2")  # type: ignore
    timber2_.add_element(e0)
    timber2_.add_element(e1)
    timber2_.add_element(e3)
    timber2_.add_element(e4)
    timber2_.add_element(e5)
    timber2_.add_element(e6)
    concrete1_ = structure1_.add_group("concrete2")  # type: ignore
    concrete1_.add_element(e2)
    model1.add_interaction(e0, e1)
    model1.add_interaction(e0, e2)

    # ==========================================================================
    # merge models
    # ==========================================================================
    model1.print()
    model2.print()
    model1.merge(model2)

    # ==========================================================================
    # print and output the result
    # ==========================================================================
    model1.print()
    return model1


def flatten_model():
    model = create_model_with_interactions()
    model.print()
    model.flatten()
    model.print()


def graft_model():
    model = create_model_with_interactions()
    model.graft()
    model.print()


def prune_model():
    model = merge_models()
    model.prune(1)
    model.print()


if __name__ == "__main__":
    # model = create_model()
    model = create_model_with_interactions()
    # model = create_model_without_hierarchy()
    # model = create_model_tree_operators()

    # copy_model()

    # serialize_element()
    # serialize_model_node()
    # serialize_model_tree()
    # ^^serialize_model()

    # merge_models()
    # flatten_model()
    # graft_model()
    # prune_model()

    pass

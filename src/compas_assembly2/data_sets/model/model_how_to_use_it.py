from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas.geometry import Point  # noqa: F401
from compas_assembly2 import Tree, TreeNode
from compas_assembly2 import Element
from compas_assembly2 import Model, Node, ElementTree
from compas.data.json import json_dump, json_load


def create_tree():
    tree = Tree()
    root = TreeNode("root")
    branch = TreeNode("branch")
    leaf1 = TreeNode("leaf1")
    leaf2 = TreeNode("leaf2")
    tree.add(root)
    root.add(branch)
    branch.add(leaf1)
    branch.add(leaf2)
    print(tree, tree.__class__.__name__)
    tree.print()
    return tree


def create_model():

    # --------------------------------------------------------------------------
    # create model
    # --------------------------------------------------------------------------
    model = Model()

    # --------------------------------------------------------------------------
    # create nodes
    # --------------------------------------------------------------------------
    branch = Node("structure")
    sub_branch_0 = Node("timber")
    sub_branch_1 = Node("concrete")

    # --------------------------------------------------------------------------
    # add nodes to model
    # --------------------------------------------------------------------------
    model.add_node(branch)
    branch.add_node(sub_branch_0)
    branch.add_node(sub_branch_1)

    # --------------------------------------------------------------------------
    # print the model
    # --------------------------------------------------------------------------
    model.print()

    # --------------------------------------------------------------------------
    # output
    # --------------------------------------------------------------------------
    return model


def insert_nodes():
    # --------------------------------------------------------------------------
    # create model
    # --------------------------------------------------------------------------
    tree = Model()

    # --------------------------------------------------------------------------
    # create and add a node
    # --------------------------------------------------------------------------
    tree.add_node(Node("structure"))  # type: ignore

    # --------------------------------------------------------------------------
    # insert a node using a paths -> a list of nodes names
    # --------------------------------------------------------------------------
    tree.insert_node(Node("timber"), path=["structure"])  # type: ignore
    tree.insert_node(Node("concrete"), path=["structure"])  # type: ignore
    tree.insert_node(Node("steel"), path=["structure"])  # type: ignore

    # --------------------------------------------------------------------------
    # print the model
    # --------------------------------------------------------------------------
    tree.print()

    # --------------------------------------------------------------------------
    # output
    # --------------------------------------------------------------------------
    return tree


def insert_element():
    # --------------------------------------------------------------------------
    # create elements
    # --------------------------------------------------------------------------
    e0 = Element(name="beam", geometry_simplified=Point(0, 0, 0))
    e1 = Element(name="plate", geometry_simplified=Point(0, 1, 0))
    e2 = Element(name="block", geometry_simplified=Point(0, 2, 0))
    e3 = Element(name="beam", geometry_simplified=Point(0, 3, 0))
    e4 = Element(name="beam", geometry_simplified=Point(0, 4, 0))

    # --------------------------------------------------------------------------
    # create model
    # --------------------------------------------------------------------------
    tree = Model()

    # --------------------------------------------------------------------------
    # create and add a node
    # --------------------------------------------------------------------------
    tree.add_node(Node("structure"))  # type: ignore

    # --------------------------------------------------------------------------
    # insert a node using a paths -> a list of nodes names
    # --------------------------------------------------------------------------
    tree.insert_node(Node("timber", elements=[e0, e1, e3, e4]), path=["structure"])  # type: ignore
    tree.insert_node(Node("concrete"), path=["structure"])  # type: ignore
    tree.insert_node(Node("steel"), path=["structure"])  # type: ignore

    # --------------------------------------------------------------------------
    # print the model
    # --------------------------------------------------------------------------
    tree.insert_element(e2, path=["structure", "concrete"], duplicate=False)  # type: ignore
    tree.print()

    # --------------------------------------------------------------------------
    # output
    # --------------------------------------------------------------------------
    return tree


def create_model_tree_operators():
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
    e7 = Element(name="block", geometry_simplified=Point(0, 0, 0))
    e8 = Element(name="glulam", geometry_simplified=Point(0, 0, 0))

    # ==========================================================================
    # create Model
    # ==========================================================================
    model = Model()  # the root of hierarchy automatically initializes the root node as <my_model>
    model.add_node(Node("structure"))
    model.hierarchy["structure"].add_node(Node("timber", elements=[e0, e1, e2, e3]))
    model.hierarchy["structure"].add_node(Node("concrete", elements=[e4, e5, e6]))

    # ==========================================================================
    # get Node by index
    # ==========================================================================
    print(model.hierarchy["structure"])

    # ==========================================================================
    # set Node by index
    # ==========================================================================
    model.hierarchy["structure"]["concrete"] = Node("concrete2", elements=[e4, e4, e4, e4, e4])

    # ==========================================================================
    # get and set Node element by index
    # ==========================================================================
    model.add_interaction(e0, e1)
    model.print_interactions()
    model.hierarchy["structure"]["timber"].set_element(0, e8)
    model.print_interactions()

    # ==========================================================================
    # get and set a Node element by index, you can also using call operator
    # ==========================================================================
    model.hierarchy["structure"]["timber"].get_element(0)  # type: ignore
    model.hierarchy["structure"]["timber"].set_element(1, e7)

    # ==========================================================================
    # print the result
    # ==========================================================================
    model.hierarchy.print()
    return model


def create_model_tree_and_elements():
    # ==========================================================================
    # create Model
    # ==========================================================================
    model = Model()  # the root of hierarchy automatically initializes the root node as <my_model>

    # ==========================================================================
    # add nodes
    # ==========================================================================
    model.add_node(Node("structure"))  # type: ignore

    model["structure"].add(
        Node(
            "timber",
            elements=[
                Element(name="beam", geometry_simplified=Point(0, 0, 0)),
                Element(name="beam", geometry_simplified=Point(0, 5, 0)),
                Element(name="plate", geometry_simplified=Point(0, 0, 0)),
                Element(name="plate", geometry_simplified=Point(0, 0, 0)),
            ],
        )
    )  # type: ignore

    model["structure"].add(
        Node(
            "concrete",
            elements=[
                Element(name="block", geometry_simplified=Point(0, 5, 0)),
                Element(name="block", geometry_simplified=Point(0, 0, 0)),
                Element(name="block", geometry_simplified=Point(0, 0, 0)),
            ],
        )
    )  # type: ignore

    # ==========================================================================
    # print the tree
    # ==========================================================================
    model.hierarchy.print()

    # ==========================================================================
    # return the model
    # ==========================================================================
    return model


def merge_models_same_structure():
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
    model1.add_node(Node("structure1"))  # type: ignore
    model1["structure1"].add_node(Node("timber1", elements=[e0, e1]))  # type: ignore
    model1["structure1"].add_node(Node("concrete1", elements=[e2]))  # type: ignore
    model1.add_interaction(e0, e1)
    model1.add_interaction(e0, e2)

    # ==========================================================================
    # create Model2
    # ==========================================================================
    model2 = Model()  # the root of hierarchy automatically initializes the root node as <my_model>
    model2.add_node(Node("structure1"))  # type: ignore
    model2["structure1"].add_node(Node("timber1", elements=[e3, e4]))  # type: ignore
    model2["structure1"].add_node(Node("concrete1", elements=[e5, e6]))  # type: ignore
    model2.add_interaction(e3, e4)
    model2.add_interaction(e3, e5)
    model2.add_interaction(e5, e6)

    # ==========================================================================
    # merge models
    # ==========================================================================
    model1.merge(model2)

    # ==========================================================================
    # print and output the result
    # ==========================================================================
    model1.print()
    return model1


def merge_models_different_structure():
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
    model1.hierarchy.add_node(Node("structure1"))  # type: ignore
    model1.hierarchy["structure1"].add_node(Node("timber1", elements=[e0, e1]))  # type: ignore
    model1.hierarchy["structure1"].add_node(Node("concrete1", elements=[e2]))  # type: ignore
    model1.add_interaction(e0, e1)
    model1.add_interaction(e0, e2)

    # ==========================================================================
    # create Model2
    # ==========================================================================
    model2 = Model()  # the root of hierarchy automatically initializes the root node as <my_model>
    model2.add_node(Node("structure2"))  # type: ignore
    model2.hierarchy["structure2"].add_node(Node("timber2", elements=[e3, e4]))  # type: ignore
    model2.hierarchy["structure2"].add_node(Node("concrete2", elements=[e5, e6]))  # type: ignore
    model2.add_interaction(e3, e4)
    model2.add_interaction(e3, e5)
    model2.add_interaction(e5, e6)

    # ==========================================================================
    # merge models
    # ==========================================================================
    model1.merge(model2)

    # ==========================================================================
    # print and output the result
    # ==========================================================================
    model1.print()
    return model1


def merge_models_similar_structure():
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
    model1.add_node(Node("structure1"))  # type: ignore
    model1.hierarchy["structure1"].add_node(Node("timber1", elements=[e0, e1]))  # type: ignore
    model1.hierarchy["structure1"].add_node(Node("concrete1", elements=[e2]))  # type: ignore
    model1.add_interaction(e0, e1)
    model1.add_interaction(e0, e2)

    # ==========================================================================
    # create Model2
    # ==========================================================================
    model2 = Model()  # the root of hierarchy automatically initializes the root node as <my_model>
    model2.add_node(Node("structure1"))  # type: ignore
    model2.hierarchy["structure1"].add_node(Node("timber1", elements=[e3, e4]))  # type: ignore
    model2.hierarchy["structure1"].add_node(Node("concrete2", elements=[e5, e6]))  # type: ignore
    model2.add_interaction(e3, e4)
    model2.add_interaction(e3, e5)
    model2.add_interaction(e5, e6)

    # ==========================================================================
    # merge models
    # ==========================================================================
    model1.merge(model2)

    # ==========================================================================
    # print and output the result
    # ==========================================================================
    model1.print()
    return model1


def copy_model():
    # ==========================================================================
    # create elements and a Node and a ElementTree and a Model
    # ==========================================================================
    e0 = Element(name="beam", geometry_simplified=Point(0, 0, 0))
    e1 = Element(name="beam", geometry_simplified=Point(0, 5, 0))
    e2 = Element(name="block", geometry_simplified=Point(0, 0, 0))
    e3 = Element(name="block", geometry_simplified=Point(0, 5, 0))

    model_node_0 = Node("timber1", elements=[e0, e1])
    model_node_1 = Node("timber2", elements=[e2, e3])

    model = Model()  # the root of hierarchy automatically initializes the root node as <my_model>
    model.add_node(model_node_0)
    model.add_node(model_node_1)
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
    e0 = Element(name="beam", geometry_simplified=Point(0, 0, 0))
    e1 = Element(name="beam", geometry_simplified=Point(0, 5, 0))

    model_node = Node("timber1", elements=[e0, e1])

    # ==========================================================================
    # serialize the model_node
    # =========================================================================
    json_dump(model_node, "src/compas_assembly2/data_sets/model/model_how_to_use_it_model_node.json", pretty=True)

    # ==========================================================================
    # deserialize the model_node
    # ==========================================================================
    model_node_deserialized = json_load("src/compas_assembly2/data_sets/model/model_how_to_use_it_model_node.json")

    # ==========================================================================
    # print the contents of the deserialized model_node
    # ==========================================================================
    for element in model_node.elements:
        print(element)
    for element in model_node_deserialized.elements:
        print(element)
    print(model_node_deserialized)


def serialize_model_tree():
    # ==========================================================================
    # create elements and Nodes
    # ==========================================================================
    e0 = Element(name="beam", geometry_simplified=Point(0, 0, 0))
    e1 = Element(name="beam", geometry_simplified=Point(0, 5, 0))
    e2 = Element(name="block", geometry_simplified=Point(0, 0, 0))
    e3 = Element(name="block", geometry_simplified=Point(0, 5, 0))

    model_node_0 = Node("timber1", elements=[e0, e1])
    model_node_1 = Node("timber2", elements=[e2, e3])

    # ==========================================================================
    # add nodes to the model_tree
    # ==========================================================================
    model_tree = ElementTree()
    model_tree.add_node(model_node_0)
    model_tree.add_node(model_node_1)

    # ==========================================================================
    # serialize the model_tree
    # ==========================================================================
    json_dump(model_tree, "src/compas_assembly2/data_sets/model/model_how_to_use_it_model_tree.json", pretty=True)

    # ==========================================================================
    # deserialize the model_tree
    # ==========================================================================
    model_tree_deserialized = json_load("src/compas_assembly2/data_sets/model/model_how_to_use_it_model_tree.json")

    # ==========================================================================
    # print the contents of the deserialized model_tree
    # ==========================================================================
    model_tree_deserialized.print()


def serialize_model():
    # ==========================================================================
    # create elements
    # ==========================================================================
    e0 = Element(name="beam", geometry_simplified=Point(0, 0, 0))
    e1 = Element(name="beam", geometry_simplified=Point(0, 5, 0))
    e2 = Element(name="block", geometry_simplified=Point(0, 0, 0))
    e3 = Element(name="block", geometry_simplified=Point(0, 5, 0))

    # ==========================================================================
    # create Nodes
    # ==========================================================================
    model_node_0 = Node("timber1", elements=[e0, e1])
    model_node_1 = Node("timber2", elements=[e2, e3])

    # ==========================================================================
    # create Model and add Nodes to it
    # ==========================================================================
    model = Model()
    model.add_node(model_node_0)
    model.add_node(model_node_1)

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
    model_deserialized.print()


if __name__ == "__main__":
    # tree = create_tree()
    # model_tree = create_model()
    # model_tree = insert_nodes()
    # model_tree = insert_element()
    # model_tree = create_model_tree_operators()
    # model_tree = create_model_tree_and_elements()
    # merge_models_same_structure()
    # merge_models_different_structure()
    # merge_models_similar_structure()
    # copy_model()
    # serialize_element()
    # serialize_model_node()
    # serialize_model_tree()
    # serialize_model()
    pass

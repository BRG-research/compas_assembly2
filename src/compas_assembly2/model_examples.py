from compas.geometry import Point  # noqa: F401
from compas_assembly2 import Element, Tree, TreeNode
from compas_assembly2 import Model, ModelNode, ModelTree


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


def create_model_tree():
    tree = Model()
    root = ModelNode("root")
    branch = ModelNode("structure")
    leaf1 = ModelNode("timber")
    leaf2 = ModelNode("concrete")
    tree._hierarchy.add(root)
    root.add(branch)
    branch.add(leaf1)
    branch.add(leaf2)
    tree.print()
    return tree


def create_model_tree_children():
    tree = Model("root")
    tree._hierarchy.root.add(ModelNode("structure"))  # type: ignore
    tree._hierarchy.root.children[0].add(ModelNode("timber"))  # type: ignore
    tree._hierarchy.root.children[0].add(ModelNode("concrete"))  # type: ignore
    tree.print()
    return tree


def create_model_tree_operators():
    # ==========================================================================
    # create elements
    # ==========================================================================
    e0 = Element(name="beam", simplex=Point(0, 0, 0))
    e1 = Element(name="beam", simplex=Point(0, 5, 0))
    e2 = Element(name="plate", simplex=Point(0, 0, 0))
    e3 = Element(name="plate", simplex=Point(0, 0, 0))

    e4 = Element(name="block", simplex=Point(0, 5, 0))
    e5 = Element(name="block", simplex=Point(0, 0, 0))
    e6 = Element(name="block", simplex=Point(0, 0, 0))
    e7 = Element(name="block", simplex=Point(0, 0, 0))
    e8 = Element(name="glulam", simplex=Point(0, 0, 0))

    # ==========================================================================
    # create Model
    # ==========================================================================
    model = Model("my_model")  # the root of hierarchy automatically initializes the root node as <my_model>
    model._hierarchy.add(ModelNode("structure"))
    model._hierarchy[0].add(ModelNode("timber", elements=[e0, e1, e2, e3]))
    model._hierarchy[0].add(ModelNode("concrete", elements=[e4, e5, e6]))

    # # ==========================================================================
    # # get ModelNode by index
    # # ==========================================================================
    # model._hierarchy[0]

    # # # ==========================================================================
    # # # set ModelNode by index
    # # # ==========================================================================
    model._hierarchy[0][0] = ModelNode("concrete2", elements=[e2, e2, e2, e2, e2])

    # # ==========================================================================
    # # get and set ModelNode element by index
    # # ==========================================================================
    model.hierarchy[0][0].set_element(0, e8)
    print(model)

    # ==========================================================================
    # get aModelNode element by index, you can also using call operator
    # ==========================================================================
    model.hierarchy[0][0](0)  # type: ignore

    # ==========================================================================
    # set aModelNode element by index, you can also using call operator
    # ==========================================================================
    model.hierarchy.print()
    model.hierarchy[0][0](1, e7)

    model.hierarchy.print()
    return model


def create_model_tree_and_elements():
    # ==========================================================================
    # create elements
    # ==========================================================================
    e0 = Element(name="beam", simplex=Point(0, 0, 0))
    e1 = Element(name="beam", simplex=Point(0, 5, 0))
    e2 = Element(name="plate", simplex=Point(0, 0, 0))
    e3 = Element(name="plate", simplex=Point(0, 0, 0))

    e4 = Element(name="block", simplex=Point(0, 5, 0))
    e5 = Element(name="block", simplex=Point(0, 0, 0))
    e6 = Element(name="block", simplex=Point(0, 0, 0))

    # ==========================================================================
    # create Model
    # ==========================================================================
    model = Model("my_model")  # the root of hierarchy automatically initializes the root node as <my_model>
    model._hierarchy._root.add(ModelNode("structure"))  # type: ignore
    model._hierarchy._root.children[0].add(ModelNode("timber", elements=[e0, e1, e2, e3]))  # type: ignore
    model._hierarchy._root.children[0].add(ModelNode("concrete", elements=[e4, e5, e6]))  # type: ignore
    model._hierarchy.print()
    return model


def merge_models_same_structure():
    # ==========================================================================
    # create elements
    # ==========================================================================
    e0 = Element(name="beam", simplex=Point(0, 0, 0))
    e1 = Element(name="beam", simplex=Point(0, 5, 0))
    e2 = Element(name="plate", simplex=Point(0, 0, 0))
    e3 = Element(name="plate", simplex=Point(0, 0, 0))

    e4 = Element(name="block", simplex=Point(0, 5, 0))
    e5 = Element(name="block", simplex=Point(0, 0, 0))
    e6 = Element(name="block", simplex=Point(0, 0, 0))

    # ==========================================================================
    # create Model1
    # ==========================================================================
    model1 = Model("my_model1")  # the root of hierarchy automatically initializes the root node as <my_model>
    model1._hierarchy._root.add(ModelNode("structure1"))  # type: ignore
    model1._hierarchy._root.children[0].add(ModelNode("timber1", elements=[e0, e1]))  # type: ignore
    model1._hierarchy._root.children[0].add(ModelNode("concrete1", elements=[e2]))  # type: ignore
    model1.add_interaction(e0, e1)
    model1.add_interaction(e0, e2)
    # model1.print_elements()
    # model1.print_interactions()

    # ==========================================================================
    # create Model2
    # ==========================================================================
    model2 = Model("my_model2")  # the root of hierarchy automatically initializes the root node as <my_model>
    model2._hierarchy._root.add(ModelNode("structure1"))  # type: ignore
    model2._hierarchy._root.children[0].add(ModelNode("timber1", elements=[e3, e4]))  # type: ignore
    model2._hierarchy._root.children[0].add(ModelNode("concrete1", elements=[e5, e6]))  # type: ignore
    model2.add_interaction(e3, e4)
    model2.add_interaction(e3, e5)
    model2.add_interaction(e5, e6)
    # model2.print_elements()
    # model2.print_interactions()

    # ==========================================================================
    # merge models
    # ==========================================================================
    model1.merge(model2)

    model1.print()
    return model1


def merge_models_different_structure():
    # ==========================================================================
    # create elements
    # ==========================================================================
    e0 = Element(name="beam", simplex=Point(0, 0, 0))
    e1 = Element(name="beam", simplex=Point(0, 5, 0))
    e2 = Element(name="plate", simplex=Point(0, 0, 0))
    e3 = Element(name="plate", simplex=Point(0, 0, 0))

    e4 = Element(name="block", simplex=Point(0, 5, 0))
    e5 = Element(name="block", simplex=Point(0, 0, 0))
    e6 = Element(name="block", simplex=Point(0, 0, 0))

    # ==========================================================================
    # create Model1
    # ==========================================================================
    model1 = Model("my_model1")  # the root of hierarchy automatically initializes the root node as <my_model>
    model1._hierarchy._root.add(ModelNode("structure1"))  # type: ignore
    model1._hierarchy._root.children[0].add(ModelNode("timber1", elements=[e0, e1]))  # type: ignore
    model1._hierarchy._root.children[0].add(ModelNode("concrete1", elements=[e2]))  # type: ignore
    model1.add_interaction(e0, e1)
    model1.add_interaction(e0, e2)
    # model1.print_elements()
    # model1.print_interactions()

    # ==========================================================================
    # create Model2
    # ==========================================================================
    model2 = Model("my_model2")  # the root of hierarchy automatically initializes the root node as <my_model>
    model2._hierarchy._root.add(ModelNode("structure2"))  # type: ignore
    model2._hierarchy._root.children[0].add(ModelNode("timber2", elements=[e3, e4]))  # type: ignore
    model2._hierarchy._root.children[0].add(ModelNode("concrete2", elements=[e5, e6]))  # type: ignore
    model2.add_interaction(e3, e4)
    model2.add_interaction(e3, e5)
    model2.add_interaction(e5, e6)
    # model2.print_elements()
    # model2.print_interactions()

    # ==========================================================================
    # merge models
    # ==========================================================================
    model1.merge(model2)

    model1.print()
    return model1


def merge_models_similar_structure():
    # ==========================================================================
    # create elements
    # ==========================================================================
    e0 = Element(name="beam", simplex=Point(0, 0, 0))
    e1 = Element(name="beam", simplex=Point(0, 5, 0))
    e2 = Element(name="plate", simplex=Point(0, 0, 0))
    e3 = Element(name="plate", simplex=Point(0, 0, 0))

    e4 = Element(name="block", simplex=Point(0, 5, 0))
    e5 = Element(name="block", simplex=Point(0, 0, 0))
    e6 = Element(name="block", simplex=Point(0, 0, 0))

    # ==========================================================================
    # create Model1
    # ==========================================================================
    model1 = Model("my_model1")  # the root of hierarchy automatically initializes the root node as <my_model>
    model1._hierarchy._root.add(ModelNode("structure1"))  # type: ignore
    model1._hierarchy._root.children[0].add(ModelNode("timber1", elements=[e0, e1]))  # type: ignore
    model1._hierarchy._root.children[0].add(ModelNode("concrete1", elements=[e2]))  # type: ignore
    model1.add_interaction(e0, e1)
    model1.add_interaction(e0, e2)
    # model1.print_elements()
    # model1.print_interactions()

    # ==========================================================================
    # create Model2
    # ==========================================================================
    model2 = Model("my_model2")  # the root of hierarchy automatically initializes the root node as <my_model>
    model2._hierarchy._root.add(ModelNode("structure1"))  # type: ignore
    model2._hierarchy._root.children[0].add(ModelNode("timber1", elements=[e3, e4]))  # type: ignore
    model2._hierarchy._root.children[0].add(ModelNode("concrete2", elements=[e5, e6]))  # type: ignore
    model2.add_interaction(e3, e4)
    model2.add_interaction(e3, e5)
    model2.add_interaction(e5, e6)
    # model2.print_elements()
    # model2.print_interactions()

    # ==========================================================================
    # merge models
    # ==========================================================================
    model1.merge(model2)

    model1.print()
    return model1


def copy_model():
    # ==========================================================================
    # create elements and a ModelNode and a ModelTree and a Model
    # ==========================================================================
    e0 = Element(name="beam", simplex=Point(0, 0, 0))
    e1 = Element(name="beam", simplex=Point(0, 5, 0))
    e2 = Element(name="block", simplex=Point(0, 0, 0))
    e3 = Element(name="block", simplex=Point(0, 5, 0))

    model_node_0 = ModelNode("timber1", elements=[e0, e1])
    model_node_1 = ModelNode("timber2", elements=[e2, e3])

    model = Model("my_model")  # the root of hierarchy automatically initializes the root node as <my_model>
    model._hierarchy.add(model_node_0)
    model._hierarchy.add(model_node_1)

    print("BEFORE COPY")
    model.print()

    # ==========================================================================
    # copy the model
    # ==========================================================================
    print("AFTER COPY")
    model_copy = model.copy()
    model_copy.print()


def when_elements_are_removed_or_replaced_the_graph_nodes_must_be_updated():
    pass


def serialize_model_node():
    # ==========================================================================
    # create elements and a ModelNode
    # ==========================================================================
    e0 = Element(name="beam", simplex=Point(0, 0, 0))
    e1 = Element(name="beam", simplex=Point(0, 5, 0))

    model_node = ModelNode("timber1", elements=[e0, e1])

    # ==========================================================================
    # serialize the model_node
    # ==========================================================================
    model_node.serialize("model_node")

    # ==========================================================================
    # deserialize the model_node
    # ==========================================================================
    model_node_deserialized = model_node.deserialize("model_node")

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
    # create elements and a ModelNode and a ModelTree
    # ==========================================================================
    e0 = Element(name="beam", simplex=Point(0, 0, 0))
    e1 = Element(name="beam", simplex=Point(0, 5, 0))
    e2 = Element(name="block", simplex=Point(0, 0, 0))
    e3 = Element(name="block", simplex=Point(0, 5, 0))

    model_node_0 = ModelNode("timber1", elements=[e0, e1])
    model_node_1 = ModelNode("timber2", elements=[e2, e3])

    model_tree = ModelTree(model=None, name="my_model")
    model_tree.add(model_node_0)
    model_tree.add(model_node_1)

    # ==========================================================================
    # serialize the model_tree
    # ==========================================================================
    model_tree.serialize("model_tree")

    # ==========================================================================
    # deserialize the model_tree
    # ==========================================================================
    model_tree_deserialized = model_tree.deserialize("model_tree")

    # ==========================================================================
    # print the contents of the deserialized model_tree
    # ==========================================================================
    model_tree_deserialized.print()


def serialize_model():
    # ==========================================================================
    # create elements and a ModelNode and a ModelTree and a Model
    # ==========================================================================
    e0 = Element(name="beam", simplex=Point(0, 0, 0))
    e1 = Element(name="beam", simplex=Point(0, 5, 0))
    e2 = Element(name="block", simplex=Point(0, 0, 0))
    e3 = Element(name="block", simplex=Point(0, 5, 0))

    model_node_0 = ModelNode("timber1", elements=[e0, e1])
    model_node_1 = ModelNode("timber2", elements=[e2, e3])

    model = Model("my_model")  # the root of hierarchy automatically initializes the root node as <my_model>
    model._hierarchy.add(model_node_0)
    model._hierarchy.add(model_node_1)

    # ==========================================================================
    # serialize the model_tree
    # ==========================================================================
    model.serialize("model")

    # ==========================================================================
    # deserialize the model_tree
    # ==========================================================================
    model_deserialized = model.deserialize("model")

    # ==========================================================================
    # print the contents of the deserialized model_tree
    # ==========================================================================
    model_deserialized.print()


if __name__ == "__main__":
    # tree = create_tree()
    # model_tree = create_model_tree()
    # model_tree = create_model_tree_children()
    # model_tree = create_model_tree_operators()
    # merge_models_same_structure()
    # merge_models_different_structure()
    # merge_models_similar_structure()
    # serialize_model_node()
    # serialize_model_tree()
    # serialize_model()
    copy_model()

from compas.geometry import Point  # noqa: F401
from compas_assembly2 import Element, Tree, TreeNode
from compas_assembly2 import Model, ModelNode


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

    # ==========================================================================
    # get ModelNode by index
    # ==========================================================================
    model._hierarchy[0]

    # # ==========================================================================
    # # set ModelNode by index
    # # ==========================================================================
    model._hierarchy[0][0] = ModelNode("concrete2", elements=[e2, e2, e2, e2, e2])

    # ==========================================================================
    # get and set ModelNode element by index
    # ==========================================================================
    model.hierarchy[0][0].set_element(0, e8)

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


def merge_several_models():
    pass


if __name__ == "__main__":
    # tree = create_tree()
    # model_tree = create_model_tree()
    # model_tree = create_model_tree_children()
    model_tree = create_model_tree_operators()
    # model_tree.interactions.number_of_edges()
    # print(model_tree)

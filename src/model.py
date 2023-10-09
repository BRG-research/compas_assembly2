from tree import TreeNode, Tree
from compas_assembly2.sortedlist import SortedList
from collections import OrderedDict
from compas.datastructures import Graph
from compas.geometry import bounding_box, Point, Line, Frame, Transformation, Rotation, Translation  # noqa: F401
from compas_assembly2 import Element
import copy


class ModelNode(TreeNode):
    def __init__(self, name=None, elements=None, attributes=None):
        super(ModelNode, self).__init__(name=name, attributes=attributes)
        self._children = SortedList()  # a sorted list of TreeNode objects instead of set()
        self._elements = elements  # attributes of the node

    def __lt__(self, other):
        """Less than operator for sorting assemblies by name.
        It is implemented for SortedList to work properly.

        """
        if isinstance(self.name, str) and isinstance(other.name, str):
            return self.name < other.name
        elif isinstance(self.name, int) and isinstance(other.name, int):
            # returns false to add element to the end of the list
            return self.name < other.name
        else:
            return False


class Model(Tree):
    def __init__(self, name="", attributes=None):
        super(Tree, self).__init__()
        self._elements = OrderedDict()  # a flat collection of elements - dict{GUID, Element}
        self._nodes = SortedList()  # hierarchical relationships between elements
        self._interactions = Graph()  # abstract linkage or connection between elements

        # --------------------------------------------------------------------------
        # simplifying the root node creation
        # --------------------------------------------------------------------------

        # add_root method is called so that the user would not need to call add root each time
        if name != "":
            message = (
                "\n---------------------------------------------------------------------------------------------------"
            )
            message += "\n NOTE: the root node is added to the Model by the first user input: <name>"
            message += (
                "\n       if you do not want to specify the name, create a ModelNode, then run .add_root() method"
            )
            message += (
                "\n---------------------------------------------------------------------------------------------------"
            )
            print(message)
            self.add_root(ModelNode(name=name))
            self.name = "model"
        else:
            message = (
                "\n---------------------------------------------------------------------------------------------------"
            )
            message += "\nWARNING: Create root by first defining a ModelNode and then calling the .add_root() method"
            message += (
                "\n---------------------------------------------------------------------------------------------------"
            )


def create_tree_with_root():
    tree = Model("my_model_tree")
    # root = ModelNode("root")
    # tree.add_root(root)
    # print
    print(tree)
    tree.print()
    return tree


def create_tree_with_root_and_branches():
    tree = Model("my_model_tree")
    branch = ModelNode("branch")
    tree.root.add(branch)
    # print
    print(tree)
    tree.print()
    return tree


def create_tree_with_root_and_branches_and_leaves():
    tree = Model("my_model_tree")
    branch = ModelNode("branch")
    leaf1 = ModelNode("leaf1")
    leaf2 = ModelNode("leaf2")
    # tree.add_root(root)
    tree.root.add(branch)
    branch.add(leaf1)
    branch.add(leaf2)
    # print
    print(tree)
    tree.print()
    return tree


if __name__ == "__main__":
    # create_tree_with_root()
    # create_tree_with_root_and_branches()
    create_tree_with_root_and_branches_and_leaves()
    pass

from tree import TreeNode, Tree
from compas_assembly2.sortedlist import SortedList
from collections import OrderedDict
from compas.datastructures import Graph
from compas.geometry import bounding_box, Point, Line, Frame, Transformation, Rotation, Translation  # noqa: F401
from compas_assembly2 import Element


class ModelNode(TreeNode):
    def __init__(self, name=None, elements=[], attributes=None):
        super(ModelNode, self).__init__(name=name, attributes=attributes)
        self._children = SortedList()  # a sorted list of TreeNode objects instead of set()
        self._elements = elements  # attributes of the node

    def __repr__(self):
        return "ModeNode {}".format(self.name)

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

    def __getitem__(self, index):
        # --------------------------------------------------------------------------
        # sanity checks
        # --------------------------------------------------------------------------
        if not isinstance(index, int):
            raise TypeError("The index is not integer.")

        # --------------------------------------------------------------------------
        # return the child
        # --------------------------------------------------------------------------
        return self._children[index]

    def __setitem__(self, index, model_node):
        # --------------------------------------------------------------------------
        # sanity checks
        # --------------------------------------------------------------------------
        if not isinstance(model_node, ModelNode):
            raise TypeError("The node is not a ModelNode object.")

        # --------------------------------------------------------------------------
        # change the node of the tree and update the node's tree and parent
        # --------------------------------------------------------------------------
        self._children[index] = model_node
        self._children[index]._tree = self._tree
        self._children[index]._parent = self

    def add(self, node):
        """
        Add a child node to this node.
        WARNING: this function is overridden to use SortedList instead of set().

        Returns
        -------
        None

        """
        if not isinstance(node, ModelNode):
            raise TypeError("The node is not a TreeNode object.")
        if node not in self._children:
            self._children.add(node)
            # for element in node._elements:
            #     self._tree._elements[str(element.guid)] = element
        node._parent = self


class Model(Tree):
    def __init__(self, name="root", attributes=None):
        super(Model, self).__init__(name=name, attributes=attributes)
        self._elements = OrderedDict()  # a flat collection of elements - dict{GUID, Element}
        self._root = None  # hierarchical relationships between elements
        self._interactions = Graph()  # abstract linkage or connection between elements
        # --------------------------------------------------------------------------
        # create root directly in the constructor
        # --------------------------------------------------------------------------
        if name != "":
            self.add(ModelNode(name=name))

    def __getitem__(self, index):
        # --------------------------------------------------------------------------
        # sanity checks
        # --------------------------------------------------------------------------
        if not isinstance(index, int):
            raise TypeError("The index is not integer.")

        # --------------------------------------------------------------------------
        # return the node
        # --------------------------------------------------------------------------
        return self._root._children[index]

    def __setitem__(self, index, model_node):

        # --------------------------------------------------------------------------
        # sanity checks
        # --------------------------------------------------------------------------
        if not isinstance(model_node, ModelNode):
            raise TypeError("The node is not a ModelNode object.")

        # --------------------------------------------------------------------------
        # change the node of the tree and update the node's tree and parent
        # --------------------------------------------------------------------------
        self._root._children.add(model_node)
        self._nodes[index]._tree = self
        self._nodes[index]._parent = self

        # --------------------------------------------------------------------------
        # if index is 0, then set all properties related to the root node
        # --------------------------------------------------------------------------
        if index == 0:
            self._root._children = self._nodes[index]

    def add(
        self,
        node,
        parent=None,
    ):
        """
        Add a node to the tree.

        """
        if not isinstance(node, TreeNode):
            raise TypeError("The node is not a TreeNode object.")

        if node.parent:
            raise ValueError("The node already has a parent, remove it from that parent first.")

        if parent is None:
            # add the node as a root node
            if self.root is not None:
                self._root.add(node)
                node._tree = self._root
                return
                raise ValueError("The tree already has a root node, remove it first.")

            self._root = node
            node._tree = self

        else:
            # add the node as a child of the parent node
            if not isinstance(parent, TreeNode):
                raise TypeError("The parent node is not a TreeNode object.")

            if parent.tree is not self:
                raise ValueError("The parent node is not part of this tree.")

            parent.add(node)

    def __repr__(self):
        return "Model with {} nodes".format(len(list(self.nodes)))

    def print(self):
        """Print the spatial hierarchy of the tree."""

        def _print(node, depth=0):
            print(
                "  " * depth
                + str(node)
                + " "
                + str(len(node._elements))
                + " | Root: "
                + node.tree.__class__.__name__
                + " "
                + str(node.tree.name)
            )
            for e in node._elements:
                print("  " * (depth + 1) + str(e))
            for child in node.children:
                _print(child, depth + 1)

        _print(self.root)


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
    print("_" * 100)
    tree.print()
    return tree


def create_model_tree():
    tree = Model()
    root = ModelNode("root")
    branch = ModelNode("structure")
    leaf1 = ModelNode("timber")
    leaf2 = ModelNode("concrete")
    tree.add(root)
    root.add(branch)
    branch.add(leaf1)
    branch.add(leaf2)
    tree.print()
    return tree


def create_model_tree_children():
    tree = Model("root")
    tree.root.add(ModelNode("structure"))
    tree.root.children[0].add(ModelNode("timber"))
    tree.root.children[0].add(ModelNode("concrete"))
    tree.print()
    return tree


def create_model_tree_operators():
    tree = Model("root")
    tree.add(ModelNode("structure"))
    tree[0].add(ModelNode("timber"))
    tree[0].add(ModelNode("concrete"))
    tree.print()
    return tree


def create_model_tree_and_elements_operators():
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
    tree = Model("root")
    tree.add(ModelNode("structure"))
    tree[0].add(ModelNode("timber", elements=[e0, e1, e2, e3]))
    tree[0].add(ModelNode("concrete", elements=[e4, e5, e6]))
    tree.print()
    return tree


if __name__ == "__main__":
    # tree = create_tree()
    model_tree = create_model_tree_and_elements_operators()
    # print(model_tree[0]._tree)
    # print(model_tree[0]._tree)

    # model_tree = create_model_tree()

    # model_tree = create_model_tree_operators()
    # tree = create_tree_via_getter()
    pass

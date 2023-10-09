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
        if not isinstance(node, TreeNode):
            raise TypeError("The node is not a TreeNode object.")
        if node not in self._children:
            self._children.add(node)
        node._parent = self

class Model(Tree):
    def __init__(self, name="", attributes=None):
        super(Model, self).__init__(name=name, attributes=attributes)
        self.name = name  # Set the 'name' as an instance variable
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
        print("__________get__item_______")
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

    def add(self, node, parent=None):
        """
        Add a node to the tree.

        Parameters
        ----------
        node : :class:`~compas.datastructures.TreeNode`
            The node to add.
        parent : :class:`~compas.datastructures.TreeNode`, optional
            The parent node of the node to add.
            Default is ``None``, in which case the node is added as a root node.

        Returns
        -------
        None

        Raises
        ------
        TypeError
            If the node is not a :class:`~compas.datastructures.TreeNode` object.
            If the supplied parent node is not a :class:`~compas.datastructures.TreeNode` object.
        ValueError
            If the node is already part of another tree.
            If the supplied parent node is not part of this tree.
            If the tree already has a root node, when trying to add a root node.

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


def create_model_tree():
    tree = Model()
    root = ModelNode("root")
    branch = ModelNode("branch")
    leaf1 = ModelNode("leaf1")
    leaf2 = ModelNode("leaf2")
    tree.add(root)
    root.add(branch)
    branch.add(leaf1)
    branch.add(leaf2)
    print(tree, tree.__class__.__name__)
    print("_" * 100)
    tree.print()


def create_model_tree_operators():
    tree = Model("root")
    tree.add(ModelNode("structure"))
    tree[0].add(ModelNode("timber"))
    tree[0].add(ModelNode("concrete"))
    print(tree, tree.__class__.__name__)
    print("_" * 100)
    tree.print()


if __name__ == "__main__":
    # tree = create_tree()
    model_tree = create_model_tree_operators()
    # tree = create_tree_via_getter()
    pass

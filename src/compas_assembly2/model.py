from compas_assembly2.sortedlist import SortedList
from collections import OrderedDict
from compas.datastructures import Graph
from compas.geometry import bounding_box, Point, Line, Frame, Transformation, Rotation, Translation  # noqa: F401
from compas_assembly2 import Element, Tree, TreeNode
from compas.geometry import Line


class ModelNode(TreeNode):
    def __init__(self, name=None, elements=None, attributes=None):
        super(ModelNode, self).__init__(name=name, attributes=attributes)
        self._children = SortedList()  # a sorted list of TreeNode objects instead of set()
        self._elements = []  # attributes of the node

        # --------------------------------------------------------------------------
        # user input - add elements to the current node and base tree model, if it exists
        # --------------------------------------------------------------------------
        self.add_elements(elements)

    @property
    def elements(self):
        return self._elements

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

    # ==========================================================================
    # element properties and methods - self._elements = OrderedDict()
    # ==========================================================================
    def add_elements(self, elements):
        """add elements to the model (current node list and root dict)"""

        if elements is not None:
            for element in elements:
                self.add_element(element)

    def add_element(self, element):
        """add an element to the model (current node list and root dict)"""

        if element is not None:
            # add elements to the current node
            self._elements.append(element)

            # if the node is part of a tree, then add elements to the base dictionary of Model class
            if self.tree:
                # update the root class
                self.tree._model._elements[element.guid] = element

                # add node to the graph
                self.tree._model._interactions.add_node(element.guid)

    # ==========================================================================
    # interactions properties and methods - self._interactions = Graph()
    # ==========================================================================

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

            # add elements from current node to the base dictionary of Model class
            root = self.tree
            for e in node._elements:
                root._model.elements[e.guid] = e

        node._parent = self


class ModelTree(Tree):
    def __init__(self, model, name="root", elements=None, attributes=None):

        super(ModelTree, self).__init__(name=name, attributes=attributes)

        # --------------------------------------------------------------------------
        # initialize the main properties of the model
        # --------------------------------------------------------------------------
        self._root = None  # the root of the tree
        self._model = model  # variable that points to the model class

        # --------------------------------------------------------------------------
        # process the user input
        # --------------------------------------------------------------------------
        self.add(ModelNode(name=name))  # the name can be empty
        self._model.add_elements(elements)  # elements is a list of Element objects

    # ==========================================================================
    # hierarchy properties and methods
    # ==========================================================================

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

            # WARNING: custom implementation, add the node as a root node
            if self.root is not None:
                self._root.add(node)
                node._tree = self._root

                for e in node.elements:
                    self.root.elements[e.guid] = e

                return node
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
            return node

    def add_by_paths(self, element, path_names=[], duplicate=False):
        # add element to the dictionary
        self._model.elements[element.guid] = element
        branch = self.root

        node = None
        for path_name in path_names:

            # check if there are branches with the same name

            found = False
            for b in branch._children:
                if b.name == str(path_name):
                    node = b
                    found = True
                    break

            if found is False:
                node = ModelNode(name=str(path_name), elements=[])
                branch.add(node)

            branch = node
        print("added element to node: ", node.name, " ", len(node.elements))
        node._elements.append(element)
        node.tree.elements[element.guid] = element

    def __repr__(self):
        return "ModelTree with {} nodes".format(len(list(self.nodes)))

    def print(self):
        """Print the spatial hierarchy of the tree."""

        def _print(node, depth=0):

            # print current data
            print("-" * 100)
            message = (
                "    " * depth
                + str(node)
                + " "
                + "["
                + str(len(node._elements))
                + "]"
                + " | Parent: "
                + str(node.parent)
                + " "
                + " | Root: "
                + node.tree.__class__.__name__
                + " "
                + str(node.tree.name)
            )

            if depth == 0:
                message += " | Dict Elements: " + "{" + str(len(node.tree._model._elements)) + "}"

            print(message)

            # print elements
            for e in node._elements:
                print("    " * (depth + 1) + str(e))

            # recursively print
            for child in node.children:
                _print(child, depth + 1)

        _print(self.root)

    # ==========================================================================
    # add linkages
    # ==========================================================================
    def add_interaction(self, element0, element1):
        """add an interaction between two elements"""

        if element0 is not None and element1 is not None:
            self._interactions.add_edge(element0.guid, element1.guid)

    def get_interactions(self):
        """get all interactions between elements"""
        return list(self._interactions.edges())

    def get_interactions_as_readable_info(self):
        """elements are stored in guid which is not readable,
        instead output this information as minimal information about an object"""

        # create dictionary of elements ids
        dict_guid_and_index = {}
        counter = 0
        for key in self._elements:
            dict_guid_and_index[key] = counter
            counter = counter + 1

        edges = self.get_interactions()
        readable_edges = []
        for i in range(len(edges)):
            a = edges[i][0]
            b = edges[i][1]
            obj0 = self._elements[a].name + " " + str(dict_guid_and_index[a])
            obj1 = self._elements[b].name + " " + str(dict_guid_and_index[b])
            readable_edges.append((obj0, obj1))
        return readable_edges

    def get_interactions_as_lines(self):
        """get all interactions between elements as lines"""
        lines = []
        edges = self.get_interactions()
        for i in range(len(edges)):
            a = edges[i][0]
            b = edges[i][1]
            point0 = self._elements[a].aabb_center()
            point1 = self._elements[b].aabb_center()
            line = Line(point0, point1)
            lines.append(line)
        return lines


class Model:
    def __init__(self, name="root", elements=None, attributes=None):

        # --------------------------------------------------------------------------
        # initialize the main properties of the model
        # --------------------------------------------------------------------------
        self._hierarchy = ModelTree(self, name)  # hierarchical relationships between elements
        self._elements = OrderedDict()  # a flat collection of elements - dict{GUID, Element}
        self._interactions = Graph()  # abstract linkage or connection between elements and nodes

        # --------------------------------------------------------------------------
        # process the user input
        # --------------------------------------------------------------------------
        self.add_elements(elements)  # elements is a list of Element objects

    # ==========================================================================
    # element properties and methods - self._elements = OrderedDict()
    # ==========================================================================

    @property
    def elements(self):
        return self._elements

    def add_elements(self, elements):
        """add elements to the model
        to get the elements from the model use the.elements property"""

        if elements is not None:
            for element in elements:
                self.add_element(element)

    def add_element(self, element):
        """add an element to the model
        to get the elements from the model use the.elements property"""

        if element is not None:
            self.elements[element.guid] = element
            self._interactions.add_node(element.guid)

    # ==========================================================================
    # interactions properties and methods - self._interactions = Graph()
    # ==========================================================================

    # ==========================================================================
    # interactions properties and methods
    # ==========================================================================

    def __getitem__(self, index):
        # --------------------------------------------------------------------------
        # sanity checks
        # --------------------------------------------------------------------------
        if not isinstance(index, int):
            raise TypeError("The index is not integer.")

        # --------------------------------------------------------------------------
        # return the node
        # --------------------------------------------------------------------------
        return self._hierarchy._root

    def __setitem__(self, index, model_node):

        # --------------------------------------------------------------------------
        # sanity checks
        # --------------------------------------------------------------------------
        if not isinstance(model_node, ModelNode):
            raise TypeError("The node is not a ModelNode object.")

        # --------------------------------------------------------------------------
        # change the node of the tree and update the node's tree and parent
        # --------------------------------------------------------------------------
        self._hierarchy._root._children.add(model_node)
        self._hierarchy._nodes[index]._tree = self
        self._hierarchy._nodes[index]._parent = self

        # --------------------------------------------------------------------------
        # if index is 0, then set all properties related to the root node
        # --------------------------------------------------------------------------
        if index == 0:
            self._hierarchy._root._children = self._nodes[index]

    def __repr__(self):
        return "Model" + " with {} elements".format(len(list(self.elements)))

    def print(self):
        """Print the spatial hierarchy of the tree."""

        def _print(node, depth=0):

            # print current data
            print("-" * 100)
            message = (
                "    " * depth
                + str(node)
                + " "
                + "["
                + str(len(node._elements))
                + "]"
                + " | Parent: "
                + str(node.parent)
                + " "
                + " | Root: "
                + node.tree.__class__.__name__
                + " "
                + str(node.tree.name)
            )

            if depth == 0:
                message += " | Dict Elements: " + "{" + str(len(node.tree._elements)) + "}"

            print(message)

            # print elements
            for e in node._elements:
                print("    " * (depth + 1) + str(e))

            # recursively print
            for child in node.children:
                _print(child, depth + 1)

        _print(self._hierarchy.root)

    # ==========================================================================
    # add linkages
    # ==========================================================================
    def add_interaction(self, element0, element1):
        """add an interaction between two elements"""

        if element0 is not None and element1 is not None:
            self._interactions.add_edge(element0.guid, element1.guid)

    def get_interactions(self):
        """get all interactions between elements"""
        return list(self._interactions.edges())

    def get_interactions_as_readable_info(self):
        """elements are stored in guid which is not readable,
        instead output this information as minimal information about an object"""

        # create dictionary of elements ids
        dict_guid_and_index = {}
        counter = 0
        for key in self._elements:
            dict_guid_and_index[key] = counter
            counter = counter + 1

        edges = self.get_interactions()
        readable_edges = []
        for i in range(len(edges)):
            a = edges[i][0]
            b = edges[i][1]
            obj0 = self._elements[a].name + " " + str(dict_guid_and_index[a])
            obj1 = self._elements[b].name + " " + str(dict_guid_and_index[b])
            readable_edges.append((obj0, obj1))
        return readable_edges

    def get_interactions_as_lines(self):
        """get all interactions between elements as lines"""
        lines = []
        edges = self.get_interactions()
        for i in range(len(edges)):
            a = edges[i][0]
            b = edges[i][1]
            point0 = self._elements[a].aabb_center()
            point1 = self._elements[b].aabb_center()
            line = Line(point0, point1)
            lines.append(line)
        return lines


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
    tree._hierarchy.root.add(ModelNode("structure"))
    tree._hierarchy.root.children[0].add(ModelNode("timber"))
    tree._hierarchy.root.children[0].add(ModelNode("concrete"))
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

    # ==========================================================================
    # create Model
    # ==========================================================================
    model = Model("my_model")  # the root of hierarchy automatically initializes the root node as <my_model>
    model._hierarchy.add(ModelNode("structure"))
    model._hierarchy[0].add(ModelNode("timber", elements=[e0, e1, e2, e3]))
    model._hierarchy[0].add(ModelNode("concrete", elements=[e4, e5, e6]))
    model._hierarchy.print()
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
    model._hierarchy._root.add(ModelNode("structure"))
    model._hierarchy._root.children[0].add(ModelNode("timber", elements=[e0, e1, e2, e3]))
    model._hierarchy._root.children[0].add(ModelNode("concrete", elements=[e4, e5, e6]))
    model._hierarchy.print()
    return model


if __name__ == "__main__":
    # tree = create_tree()
    # model_tree = create_model_tree()
    # model_tree = create_model_tree_children()
    model_tree = create_model_tree_operators()
    # model_tree = create_model_tree_and_elements()
    pass

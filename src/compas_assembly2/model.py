from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from collections import OrderedDict
from compas.datastructures import Graph
from compas.geometry import Line, Polygon, distance_point_point  # noqa: F401
from compas_assembly2 import Element  # noqa: F401
from compas_assembly2 import Algorithms  # noqa: F401
from compas.data import Data
from compas.datastructures import Mesh
import uuid


class Node(Data):
    """A node of a tree data structure.

    Parameters
    ----------
    name : str, optional
        The name of the tree ndoe.
    attributes : dict[str, Any], optional
        User-defined attributes of the datastructure.

    Attributes
    ----------
    name : str
        The name of the datastructure.
    attributes : dict[str, Any]
        User-defined attributes of the datastructure.
    parent : :class:`~compas.datastructures.Node`
        The parent node of the tree node.
    children : list[:class:`~compas.datastructures.Node`]
        The children of the tree node.
    tree : :class:`~compas.datastructures.Tree`
        The tree to which the node belongs.
    is_root : bool
        True if the node is the root node of the tree.
    is_leaf : bool
        True if the node is a leaf node of the tree.
    is_branch : bool
        True if the node is a branch node of the tree.
    acestors : generator[:class:`~compas.datastructures.Node`]
        A generator of the acestors of the tree node.
    descendants : generator[:class:`~compas.datastructures.Node`]
        A generator of the descendants of the tree node, using a depth-first preorder traversal.

    """

    DATASCHEMA = {
        "type": "object",
        "$recursiveAnchor": True,
        "properties": {
            "name": {"type": "string"},
            "my_object": {"type": "object"},
            "attributes": {"type": "object"},
            "children": {"type": "array", "items": {"$recursiveRef": "#"}},
        },
        "required": ["name", "my_object", "attributes", "children"],
    }

    def __init__(self, name=None, my_object=None, attributes=None):
        super(Node, self).__init__(name=name)
        self._my_object = my_object  # added by Petras
        self.attributes = attributes or {}
        self._parent = None
        self._children = []
        self._tree = None

    def __repr__(self):
        return "<Node {}>".format(self.name)

    @property
    def is_root(self):
        return self._parent is None

    @property
    def is_leaf(self):
        return not self._children

    @property
    def is_branch(self):
        return not self.is_root and not self.is_leaf

    @property
    def parent(self):
        return self._parent

    @property
    def children(self):
        return self._children

    @property
    def tree(self):
        if self.is_root:
            return self._tree
        else:
            return self.parent.tree

    @property  # added by Petras
    def my_object(self):
        return self._my_object

    @property
    def data(self):
        return {
            "name": self.name,
            "my_object": self.my_object,
            "attributes": self.attributes,
            "children": [child.data for child in self.children],
        }

    @classmethod
    def from_data(cls, data):
        node = cls(data["name"], data["my_object"], data["attributes"])  # added by Petras
        if data["children"] is not None:
            for child in data["children"]:
                node.add(cls.from_data(child))
        return node

    def add(self, node):
        """
        Add a child node to this node.

        Parameters
        ----------
        node : :class:`~compas.datastructures.Node`
            The node to add.

        Returns
        -------
        None

        Raises
        ------
        TypeError
            If the node is not a :class:`~compas.datastructures.Node` object.

        """
        if not isinstance(node, Node):
            raise TypeError("The node is not a Node object.")
        if node not in self._children:
            self._children.append(node)
        node._parent = self

    def remove(self, node):
        """
        Remove a child node from this node.

        Parameters
        ----------
        node : :class:`~compas.datastructures.Node`
            The node to remove.

        Returns
        -------
        None

        """
        self._children.remove(node)
        node._parent = None

    @property
    def ancestors(self):
        this = self
        while this:
            yield this
            this = this.parent

    @property
    def descendants(self):
        for child in self.children:
            yield child
            for descendant in child.descendants:
                yield descendant

    def traverse(self, strategy="depthfirst", order="preorder"):
        """
        Traverse the tree from this node.

        Parameters
        ----------
        strategy : {"depthfirst", "breadthfirst"}, optional
            The traversal strategy.
            Default is ``"depthfirst"``.

        order : {"preorder", "postorder"}, optional
            The traversal order. This parameter is only used for depth-first traversal.
            Default is ``"preorder"``.

        Yields
        ------
        :class:`~compas.datastructures.Node`
            The next node in the traversal.

        Raises
        ------
        ValueError
            If the strategy is not ``"depthfirst"`` or ``"breadthfirst"``.
            If the order is not ``"preorder"`` or ``"postorder"``.

        """
        if strategy == "depthfirst":
            if order == "preorder":
                yield self
                for child in self.children:
                    for node in child.traverse(strategy, order):
                        yield node
            elif order == "postorder":
                for child in self.children:
                    for node in child.traverse(strategy, order):
                        yield node
                yield self
            else:
                raise ValueError("Unknown traversal order: {}".format(order))
        elif strategy == "breadthfirst":
            queue = [self]
            while queue:
                node = queue.pop(0)
                yield node
                queue.extend(node.children)
        else:
            raise ValueError("Unknown traversal strategy: {}".format(strategy))


class Tree(Data):
    """A hierarchical data structure that organizes elements into parent-child relationships.
    The tree starts from a unique root node, and every node (excluding the root) has exactly one parent.

    Parameters
    ----------
    name : str, optional
        The name of the datastructure.
    attributes : dict[str, Any], optional
        User-defined attributes of the datastructure.

    Attributes
    ----------
    name : str
        The name of the datastructure.
    attributes : dict[str, Any]
        User-defined attributes of the datastructure.
    root : :class:`~compas.datastructures.Node`
        The root node of the tree.
    nodes : generator[:class:`~compas.datastructures.Node`]
        The nodes of the tree.
    leaves : generator[:class:`~compas.datastructures.Node`]
        A generator of the leaves of the tree.

    Examples
    --------
    >>> tree = Tree(name='tree')
    >>> root = Node('root')
    >>> branch = Node('branch')
    >>> leaf1 = Node('leaf1')
    >>> leaf2 = Node('leaf2')
    >>> tree.add(root)
    >>> root.add(branch)
    >>> branch.add(leaf1)
    >>> branch.add(leaf2)
    >>> print(tree)
    <Tree with 4 nodes>
    >>> tree.print()
    <Node root>
        <Node branch>
            <Node leaf1>
            <Node leaf2>

    """

    DATASCHEMA = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "root": Node.DATASCHEMA,
            "attributes": {"type": "object"},
        },
        "required": ["name", "root", "attributes"],
    }

    def __init__(self, name=None, attributes=None):
        super(Tree, self).__init__(name=name)
        self.attributes = attributes or {}
        self._root = None

    @property
    def data(self):
        return {
            "name": self.name,
            "object": self.object,
            "attributes": self.attributes,
            "children": [child.data for child in self.children],
        }

    @classmethod
    def from_data(cls, data):
        tree = cls(data["name"], data["attributes"])
        root = Node.from_data(data["root"])
        tree.add(root)
        return tree

    @property
    def root(self):
        return self._root

    def add(self, node, parent=None):
        """
        Add a node to the tree.

        Parameters
        ----------
        node : :class:`~compas.datastructures.Node`
            The node to add.
        parent : :class:`~compas.datastructures.Node`, optional
            The parent node of the node to add.
            Default is ``None``, in which case the node is added as a root node.

        Returns
        -------
        None

        Raises
        ------
        TypeError
            If the node is not a :class:`~compas.datastructures.Node` object.
            If the supplied parent node is not a :class:`~compas.datastructures.Node` object.
        ValueError
            If the node is already part of another tree.
            If the supplied parent node is not part of this tree.
            If the tree already has a root node, when trying to add a root node.

        """
        if not isinstance(node, Node):
            raise TypeError("The node is not a Node object.")

        if node.parent:
            raise ValueError("The node already has a parent, remove it from that parent first.")

        if parent is None:
            # add the node as a root node
            if self.root is not None:
                raise ValueError("The tree already has a root node, remove it first.")

            self._root = node
            node._tree = self

        else:
            # add the node as a child of the parent node
            if not isinstance(parent, Node):
                raise TypeError("The parent node is not a Node object.")

            if parent.tree is not self:
                raise ValueError("The parent node is not part of this tree.")

            parent.add(node)

    @property
    def nodes(self):
        if self.root:
            for node in self.root.traverse():
                yield node

    def remove(self, node):
        """
        Remove a node from the tree.

        Parameters
        ----------
        node : :class:`~compas.datastructures.Node`
            The node to remove.

        Returns
        -------
        None

        """
        if node == self.root:
            self._root = None
            node._tree = None
        else:
            node.parent.remove(node)

    @property
    def leaves(self):
        for node in self.nodes:
            if node.is_leaf:
                yield node

    def traverse(self, strategy="depthfirst", order="preorder"):
        """
        Traverse the tree from the root node.

        Parameters
        ----------
        strategy : {"depthfirst", "breadthfirst"}, optional
            The traversal strategy.
            Default is ``"depthfirst"``.

        order : {"preorder", "postorder"}, optional
            The traversal order. This parameter is only used for depth-first traversal.
            Default is ``"preorder"``.

        Yields
        ------
        :class:`~compas.datastructures.Node`
            The next node in the traversal.

        Raises
        ------
        ValueError
            If the strategy is not ``"depthfirst"`` or ``"breadthfirst"``.
            If the order is not ``"preorder"`` or ``"postorder"``.

        """
        if self.root:
            for node in self.root.traverse(strategy=strategy, order=order):
                yield node

    def get_node_by_name(self, name):
        """
        Get a node by its name.

        Parameters
        ----------
        name : str
            The name of the node.

        Returns
        -------
        :class:`~compas.datastructures.Node`
            The node.

        """
        for node in self.nodes:
            if node.name == name:
                return node

    def get_nodes_by_name(self, name):
        """
        Get all nodes by their name.

        Parameters
        ----------
        name : str
            The name of the node.

        Returns
        -------
        list[:class:`~compas.datastructures.Node`]
            The nodes.

        """
        nodes = []
        for node in self.nodes:
            if node.name == name:
                nodes.append(node)
        return nodes

    def __repr__(self):
        return "<Tree with {} nodes>".format(len(list(self.nodes)))

    def print(self):
        """Print the spatial hierarchy of the tree."""

        def _print(node, depth=0):
            print("  " * depth + str(node))
            for child in node.children:
                _print(child, depth + 1)

        _print(self.root)


class ElementTree(Tree):
    """
    A class representing a tree structure for a model.

    The ElementTree class extends the Tree class and is used to create a hierarchical tree structure for a model,
    which can contain Node elements.

    Parameters:
        model (Model): The model to associate with the tree.
        name (str): The name of the tree. Default is "root".
        elements (list): A list of Element objects to initialize the model with. Default is None.
        attributes (dict): Additional attributes for the tree. Default is None.

    Attributes:
        _root (Node): The root Node of the tree.
        _model (Model): A variable that points to the model class.

    Methods:
        - __init__(self, model, name="root", elements=None, attributes=None): Initializes a new ElementTree instance.

    Example Usage:
        # Create a model tree associated with a model
        model_tree = ElementTree(model_instance, name="custom_tree")
    """

    def __init__(self, model=None, name="root", attributes=None):
        """
        Initialize a new ElementTree instance.

        Parameters:
            model (Model): The model to associate with the tree.
            name (str): The name of the tree. Default is "root".
            elements (list): A list of Element objects to initialize the model with. Default is None.
            attributes (dict): Additional attributes for the tree. Default is None.
        """
        super(ElementTree, self).__init__(name=name, attributes=attributes)

        # --------------------------------------------------------------------------
        # initialize the main properties of the model
        # --------------------------------------------------------------------------
        self.name = name  # the name of the tree
        self._model = model  # variable that points to the model class
        self._root = GroupNode(name="root", geometry=None, attributes=None, parent=None, tree=self)

        # --------------------------------------------------------------------------
        # process the user input
        # --------------------------------------------------------------------------
        # root_node = GroupNode(name="root", geometry=None, attributes=None, parent=None)
        # print("root_node", root_node, "parent", root_node.parent)
        self.composition = Composition(self._root, self.model)

    # ==========================================================================
    # Serialization
    # ==========================================================================
    @property
    def data(self):

        # serialize the nodes
        nodes = []
        for child in self.root.children:  # type: ignore
            nodes.append(child.data)

        # output the dictionary
        return {
            "name": self.name,
            "nodes": nodes,  # type: ignore
            "attributes": self.attributes,
        }

    @classmethod
    def from_data(cls, data):

        model_tree = cls(model=None, name=data["name"], attributes=data["attributes"])
        nodes = []

        for node in data["nodes"]:
            if isinstance(node["my_object"], Element):
                nodes.append(ElementNode.from_data(node))
            else:
                nodes.append(GroupNode.from_data(node))

        for node in nodes:
            # set the base tree and the default parent as the model_tree root
            node._tree = model_tree
            node._parent = model_tree._root
            # then add the node to the model_tree
            model_tree._add_node(node)
        return model_tree

    # ==========================================================================
    # Properites
    # ==========================================================================
    @property
    def root(self):
        return self._root

    @property
    def model(self):
        return self._model

    @property
    def number_of_elements(self):
        # iterate all children and count ElementNode
        count = 0

        def _count_elements(node, count):
            for child in node.children:
                if isinstance(child, ElementNode):
                    count += 1
                else:
                    count = _count_elements(child, count)
            return count

        count = _count_elements(self.root, count)
        return count

    # ==========================================================================
    # hierarchy methods: add Node, add_by_path
    # ==========================================================================

    def add_group(self, name=None, geometry=None, attributes=None):
        self.composition.add_group(name=name, geometry=geometry, attributes=attributes)

    def add_element(self, name=None, element=None, attributes=None):
        self.composition.add_element(name=name, element=element, attributes=attributes)

    def _add_node(self, node):
        self.composition.add_node(node)

    # ==========================================================================
    # print statements
    # ==========================================================================

    def __repr__(self):
        """
        Return a string representation of the ElementTree.

        Returns:
            str: A string representation of the ElementTree, including the number of nodes.

        Example Usage:
            # Get a string representation of the ElementTree
            tree_repr = repr(model_tree)
        """
        return "ElementTree with {} nodes".format(len(list(self.nodes)))

    def __str__(self):
        return self.__repr__()

    def print(self):
        """
        Print the spatial hierarchy of the tree for debugging and visualization.

        This method prints information about the tree's spatial hierarchy, including nodes, elements,
        parent-child relationships, and other relevant details.

        """

        def _print(node, depth=0):

            # parent_name = "None" if node.parent is None else node.parent.name
            parent_name = "None" if node.parent is None else node.parent.name

            # print current data
            print("-" * 100)
            message = "    " * depth + str(node) + " " + "| Parent: " + parent_name + " | Root: " + node.tree.name

            if depth == 0:
                message += " | Elements: " + "{" + str(node.tree.number_of_elements) + "}"

            print(message)

            # recursively print
            if node.children is not None:
                for child in node.children:
                    _print(child, depth + 1)

        _print(self.root)

    # ==========================================================================
    # add linkages
    # ==========================================================================
    def add_interaction(self, element0, element1):
        self._model.add_interaction(element0, element1)

    def get_interactions(self):
        return self._model.get_interactions()

    def get_interactions_as_readable_info(self):
        return self._model.get_interactions_as_readable_info()

    def get_interactions_as_lines(self):
        return self._model.get_interactions_as_lines()

    # ==========================================================================
    # operators
    # ==========================================================================

    def __getitem__(self, index_string_guid_element):
        return self.composition.__getitem__(index_string_guid_element)

    def __setitem__(self, index_string_guid_element, node_or_element):
        self.composition.__setitem__(index_string_guid_element, node_or_element)


class GroupNode(Node):
    def __init__(self, name=None, geometry=None, attributes=None, parent=None, tree=None):
        """
        Initialize a Node.

        Parameters
        ----------
        name : str, optional
            A name or identifier for the node.

        elements : list, optional
            A list of attributes or elements to be associated with the node.

        attributes : dict, optional
            A dictionary of additional attributes to be associated with the node.

        """
        super().__init__(name=name, my_object=geometry, attributes=attributes)
        self.name = name if name else str(self.guid)
        self._parent = parent

        if tree is not None:
            self._tree = tree
        elif parent is not None:
            self._tree = parent._tree
        # --------------------------------------------------------------------------
        # user input - add elements to the current node and base tree model, if it exists
        # --------------------------------------------------------------------------
        reference_to_the_model = (
            None if self._tree is None else self._tree._model
        )  # for cases when the node is initialized separately
        self.composition = Composition(self, reference_to_the_model)

    # ==========================================================================
    # Serialization
    # ==========================================================================
    @property
    def data(self):
        return {
            "name": self.name,
            "attributes": self.attributes,
            "children": [child.data for child in self.children],
            "my_object": self._my_object,
        }

    @classmethod
    def from_data(cls, data):
        my_object = data["my_object"]
        node = cls(name=data["name"], geometry=my_object, attributes=data["attributes"])
        if data["children"] is not None:
            for child in data["children"]:
                node.add(cls.from_data(child))

        return node

    # ==========================================================================
    # properties
    # ==========================================================================

    @property
    def geometry(self):
        """
        Get the list of elements or attributes associated with the Node.

        Returns
        -------
        list
            A list of elements or attributes linked to the Node.
        """
        return self._my_object

    @property
    def children(self):
        """
        Get the child nodes of the Node.

        Returns
        -------
        SortedList
            A sorted list of child nodes (Node objects) linked to the current Node.
        """
        return self._children

    def clear_children(self):
        if self.composition.base_node._children:
            self.composition.base_node._children.clear()

    # ==========================================================================
    # less than to add elements to the SortedList
    # ==========================================================================

    def __contains__(self, item):
        for child in self._children:
            if child.name == item.name:
                return True
        return False

    # ==========================================================================
    # operators
    # ==========================================================================

    def __getitem__(self, index_string_guid_element):
        return self.composition.__getitem__(index_string_guid_element)

    def __setitem__(self, index_string_guid_element, node_or_element):
        self.composition.__setitem__(index_string_guid_element, node_or_element)

    def change_base_tree(self, new_tree):
        """
        Change the base tree of the current node.

        Parameters:
            new_tree (ElementTree): The new ElementTree object to set as the base tree.

        Example Usage:
            # Change the base tree of the current node
            node.change_base_tree(new_tree)
        """
        self._tree = new_tree
        for child in self._children:
            child.change_base_tree(new_tree)

    # ==========================================================================
    # interactions properties and methods - self._interactions = Graph()
    # ==========================================================================
    def add_group(self, name=None, geometry=None, attributes=None, parent=None):
        parent = parent if parent else self
        node = self.composition.add_group(name=name, geometry=geometry, attributes=attributes, parent=parent)
        return node

    def add_element(self, name=None, element=None, attributes=None, parent=None):
        parent = parent if parent else self
        return self.composition.add_element(name=name, element=element, attributes=attributes, parent=parent)

    # ==========================================================================
    # print
    # ==========================================================================

    def __repr__(self):
        """
        Return a string representation of the Node.

        Returns:
            str: A string representation of the Node, including its name and the number of elements.

        Example Usage:
            # Get a string representation of the Node
            node_repr = repr(model_node)
        """
        return "<{}> {}, <geometry> {}".format(self.__class__.__name__, self.name, self.geometry)

    def __str__(self):
        return self.__repr__()


class ElementNode(Node):
    def __init__(self, name=None, element=None, attributes=None, parent=None):
        """
        Initialize a Node.

        Parameters
        ----------
        name : str, optional
            A name or identifier for the node.

        elements : list, optional
            A list of attributes or elements to be associated with the node.

        attributes : dict, optional
            A dictionary of additional attributes to be associated with the node.

        """
        super().__init__(name=name, my_object=element, attributes=attributes)
        self.name = name if name else str(self.guid)
        self._children = None  # make the leaf
        self._parent = parent
        if parent is not None:
            self._tree = parent._tree
        # --------------------------------------------------------------------------
        reference_to_the_model = None if self._tree is None else self._tree._model
        self.composition = Composition(self, reference_to_the_model)

    # ==========================================================================
    # Serialization
    # ==========================================================================
    @property
    def data(self):
        return {
            "name": self.name,
            "attributes": self.attributes,
            "children": None,
            "my_object": self.element,
        }

    @classmethod
    def from_data(cls, data):
        element = data["my_object"]
        node = cls(name=data["name"], element=element, attributes=data["attributes"])
        node._children = None
        return node

    # ==========================================================================
    # properties
    # ==========================================================================

    @property
    def element(self):
        return self._my_object

    # ==========================================================================
    # less than to add elements to the SortedList
    # ==========================================================================

    def equals(self, other):
        """
        Less than operator for sorting assemblies by name.

        This method is implemented for SortedList to work properly when sorting
        Nodes by name. It compares the names of two Nodes and returns
        True if the name of 'self' is less than the name of 'other'.

        Parameters
        ----------
        other : Node
            Another Node object to compare against.

        Returns
        -------
        bool
            True if the name of 'self' is less than the name of 'other'; False otherwise.
        """
        if self.element.guid == other.element.guid:  # type: ignore
            return True
        else:
            return False

    # ==========================================================================
    # operators
    # ==========================================================================

    # ==========================================================================
    # print
    # ==========================================================================

    def __repr__(self):
        """
        Return a string representation of the Node.

        Returns:
            str: A string representation of the Node, including its name and the number of elements.

        Example Usage:
            # Get a string representation of the Node
            node_repr = repr(model_node)
        """
        return "<{}> {}, <element> {}".format(self.__class__.__name__, self.name, self.element)

    def __str__(self):
        return self.__repr__()


class Composition:
    def __init__(self, base_node, model):
        self.base_node = base_node
        self.model = model

    def contains_node(self, node_name):
        for child in self.base_node._children:  # type: ignore
            if child.name == node_name:
                return True
        return False

    def add_element(self, name=None, element=None, attributes=None, copy_element=False, parent=None):

        # incase user does not specify explicitly name, ane just pass the element as a single argument
        if isinstance(name, Element):
            element = name
            name = element.guid

        element.parent = parent if parent else self.base_node
        if element is not None:
            element_copy = element.copy() if copy_element else element
            name = name if name else str(element_copy.guid)

            # if the node is part of a tree, then add elements to the base dictionary of Model class
            if self.base_node._tree:
                # update the root class
                self.base_node._tree._model._elements[str(element_copy.guid)] = element_copy

                # add the node to the graph
                self.base_node._tree._model.add_interaction_node(element_copy)

            element_node = ElementNode(name=name, element=element_copy, attributes=attributes, parent=parent)
            self.add_node(element_node)
            return element_node  # element_copy
        return None

    def add_group(self, name=None, geometry=None, attributes=None, parent=None):
        parent = parent if parent else self.base_node
        node = GroupNode(name=name, geometry=geometry, attributes=attributes, parent=parent)
        self.add_node(node)
        return node

    def add_node(self, node):

        # if not isinstance(node, Node):
        #     raise TypeError("The node is not a Node object.")

        # if node.parent:
        #     raise ValueError("The node already has a parent, remove it from that parent first.")

        # if parent is None:
        #     # add the node as a root node
        #     if self.root is not None:
        #         raise ValueError("The tree already has a root node, remove it first.")

        #     self._root = node
        #     node._tree = self

        # else:
        #     # add the node as a child of the parent node
        #     if not isinstance(parent, Node):
        #         raise TypeError("The parent node is not a Node object.")

        #     if parent.tree is not self:
        #         raise ValueError("The parent node is not part of this tree.")

        #     parent.add(node)
        if not isinstance(node, Node):
            raise TypeError("The node is not a Node object.")
        if node not in self.base_node._children:
            self.base_node._children.append(node)
            # print("____", self.base_node, type(self.base_node))
            # print("____", self.base_node._tree)
            if self.base_node._tree is not None:
                if self.base_node._tree._model is not None:
                    # add elements from the current node to the base dictionary of Model class
                    if self.base_node.children is not None and isinstance(node.my_object, ElementNode):
                        self.base_node._tree._model.elements[str(self.element.guid)] = self.element  # type: ignore
                        # add the node to the graph
                        self.base_node._tree._model.add_interaction_node(self.element)  # type: ignore

            # node._parent = self  # type: ignore

    def collect_elements(self, my_node):
        all_elements = []

        def collect_elements(node):
            for child in node.children:
                if isinstance(child, ElementNode):
                    all_elements.append(child.element)
                else:
                    collect_elements(child)

        collect_elements(my_node)
        return all_elements

    def remove_node(self, node):
        if not isinstance(node, Node):
            raise TypeError("The node is not a Node object.")

        # collect all the elements from the node
        all_elements = self.collect_elements(node)

        # remove the elements from the dictionary and the graph
        for element in all_elements:
            del self.base_node.tree._model._elements[str(element.guid)]
            self.base_node.tree._model._interactions.delete_node(str(element.guid))

        # remove the node from the tree
        self.base_node.remove(node)

    def find_node(self, node_name):
        def _find_node(node):
            for child in node.children:
                if child.name == node_name:
                    return child
                else:
                    return _find_node(child)
            return None

        return _find_node(self.base_node)

    def find_element_node(self, element):
        def _find_element_node(node):
            for child in node.children:
                if isinstance(child, ElementNode):
                    if child.element == element:
                        return child
                else:
                    return _find_element_node(child)
            return None

        return _find_element_node(self.base_node)

    def remove_element(self, element):
        if not isinstance(element, Element):
            raise TypeError("The element is not an Element object.")

        # remove the elements from the dictionary and the graph
        del self.base_node.tree._model._elements[str(element.guid)]
        self.base_node.tree._model._interactions.delete_node(str(element.guid))

        # find and remove the node from the tree
        found_node = self.find_element_node(element)
        if found_node:
            self.base_node.remove(found_node)

    def insert_node(self, node, node_names=[]):
        pass

    #     # add element to the dictionary
    #     paths = node_names  # [1:]

    #     for idx, path_name in enumerate(paths):

    #         # check if there are branches with the same name
    #         found = False

    #         if self.base_node._children:
    #             for b in self.base_node._children:  # type: ignore
    #                 if b.name == str(path_name):
    #                     self.base_node = b
    #                     found = True
    #                     break

    #         if found and idx == len(paths) - 1:
    #             self.base_node.add_node(node)  # type: ignore
    #             break

    #         if found is False:
    #             return

    def merge(self, other_model):
        """merge current model with the other model"""

        def add_nodes(curr_node, other_node):
            # try to find GroupNode with the same name
            print("curr_node", curr_node.name, "other_node", other_node.name)
            # given two lists of nodes find the common nodes and merge them together otherwise add the node
            non_intersecting_nodes = []

            for other_child in other_node.children:
                is_found = False
                for curr_child in curr_node.children:
                    if curr_child.name == other_child.name:
                        is_found = True
                        if isinstance(curr_child, ElementNode) and isinstance(other_child, ElementNode):
                            curr_child.parent.composition.add_node(other_child)
                        elif isinstance(curr_child, GroupNode) and isinstance(other_child, GroupNode):
                            # merge the nodes
                            print(curr_child.name, other_child.name)
                            add_nodes(curr_child, other_child)
                        break
                if is_found is False:
                    non_intersecting_nodes.append(other_child)

            # add non intersecting nodes
            for other_child in non_intersecting_nodes:
                curr_node.composition.add_node(other_child)
                print("adding", other_child.name)

        add_nodes(self.base_node, other_model._hierarchy.root)  # type: ignore

        # add elements to the dictionary
        print("other_model.elements", other_model.elements)
        for key, item in other_model.elements.items():
            self.base_node._tree._model._elements[key] = item

        # add graph nodes
        for node in other_model._interactions.nodes():
            self.base_node._tree._model._interactions.add_node(node)

        # add graph edges
        for edge in other_model._interactions.edges():
            self.base_node._tree._model._interactions.add_edge(edge[0], edge[1])

    def flatten(self, flatenned_node_name="flat_node"):
        """flatten the hierarchy structure"""

        # step1 - get elements from the hierarchy
        all_node_elements = []

        def collect_elements(node):
            for child in node.children:
                if isinstance(child, ElementNode):
                    all_node_elements.append(child.element)
                else:
                    collect_elements(child)

        collect_elements(self.base_node)
        # step2 - remove all nodes from the hierarchy¨
        self.base_node.clear_children()  # type: ignore

        # step3 - create a new node with the collected elements
        for element in all_node_elements:
            self.base_node.add_element(name=flatenned_node_name, element=element)  # type: ignore

    def graft(self):
        """in hierarchy structure place elements into separate nodes"""

        def _graft_node(self, node):
            if node.children is not None:
                for idx, child in enumerate(node.children):
                    is_element_node = isinstance(child, ElementNode)
                    print("child", child)
                    if is_element_node:
                        print("node", child)
                        name = child.name
                        element = child.element
                        parent = child.parent
                        group = GroupNode(name=name, geometry=None, attributes=child.attributes)
                        node.children[idx] = group
                        group._parent = parent
                        group._tree = parent._tree
                        group.add_element(name=name, element=element)
                    else:
                        _graft_node(self, child)

        _graft_node(self, self.base_node)

    def prune(self, level=0):
        # Prune the tree by moving elements from child nodes to parent nodes and deleting child nodes.
        if level == 0:
            self.flatten()
            return

        all_elements = []

        def flatten_the_deeper_level_while_taking_all_the_elements(node):
            if isinstance(node, ElementNode):
                all_elements.append(node.element)
                return
            elif len(node.children) == 0:
                return
            else:
                for child in node.children:
                    flatten_the_deeper_level_while_taking_all_the_elements(child)
                node.clear_children()

        def traverse_the_tree_and_prune(node, current_level):
            if current_level == 0:
                flatten_the_deeper_level_while_taking_all_the_elements(node)
                for element in all_elements:
                    node.add_element(element=element)
                all_elements.clear()
            else:
                for child in node.children:
                    traverse_the_tree_and_prune(child, current_level - 1)

        # Ensure the specified level is within the valid range of the tree.
        if level < 0:
            raise ValueError("Level must be a non-negative integer.")

        # Start pruning from the root node.
        traverse_the_tree_and_prune(self.base_node, level)

    # ==========================================================================
    # operators
    # ==========================================================================

    def is_node(self, node=None):
        my_node = node if node else self.base_node
        return my_node

    def get_child_by_index(self, index):
        return self.base_node._children[index]

    def set_child_by_index(self, index, new_node):

        # get the node
        node = self.base_node._children[index]

        # collect all the element in the current node and all the childs
        all_elements = []

        def get_elements(all_elements, node):
            if isinstance(node, ElementNode):
                all_elements.append(node.element)
                return

            for node in node._children:
                if isinstance(node, ElementNode):
                    all_elements.append(node.element)
                else:
                    for node in node.children:
                        get_elements(all_elements, node)

        get_elements(all_elements, node)

        # remove elements from the element dictionary and the graph
        for element in all_elements:
            del self.base_node._tree.model._elements[str(element.guid)]
            self.base_node._tree.model._interactions.delete_node(str(element.guid))

        # replace the node
        new_node._parent = node.parent
        del self.base_node._children[index]
        self.base_node._children.insert(index, new_node)

        # iterate of the new_node and add elements to the dictionary and the graph
        def add_elements_to_the_dictionary_and_graph(node):
            if isinstance(node, ElementNode):
                self.base_node._tree.model._elements[str(node.element.guid)] = node.element
                self.base_node._tree.model._interactions.add_node(str(node.element.guid))
                return

            for child in node.children:
                add_elements_to_the_dictionary_and_graph(child)

        add_elements_to_the_dictionary_and_graph(new_node)

    def get_child_by_name(self, name):

        for idx, child in enumerate(self.base_node._children):
            if str.lower(child.name) == str.lower(name):
                return self.get_child_by_index(idx)

    def set_child_by_name(self, name, new_node):

        node_index = -1
        for idx, child in enumerate(self.base_node._children):
            if str.lower(child.name) == str.lower(name):
                node_index = idx
                break
        if node_index != -1:
            self.set_child_by_index(node_index, new_node)

    def get_node_by_element_guid(self, guid):
        def get_node(node):

            for child in node.children:
                if isinstance(child, ElementNode):
                    if child.element.guid == guid:
                        return child.parent
                else:
                    local_result = get_node(child)
                    if local_result is not None:
                        return local_result

        result = get_node(self.base_node)
        return result

    def get_node_by_element(self, element):
        return self.get_node_by_element_guid(element.guid)

    def set_element_by_guid(self, guid, element):

        # replaces the elements in the nodes
        def replace_element(node):
            for child in node.children:
                if isinstance(child, ElementNode):
                    if child.element.guid == guid:
                        child._my_object = element
                else:
                    replace_element(child)

        replace_element(self.base_node)

        # delete the element from the dictionary
        del self.base_node._tree.model._elements[str(guid)]
        self.base_node._tree.model._elements[str(element.guid)] = element

        # find edges in the graph with this node
        edges = self.base_node._tree.model._interactions.edges()
        new_edges = []
        for edge in edges:
            if edge[0] == str(guid):
                new_edges.append((str(element.guid), edge[1]))
            elif edge[1] == str(guid):
                new_edges.append((edge[0], str(element.guid)))
        self.base_node._tree.model._interactions.add_node(str(element.guid))
        for edge in new_edges:
            self.base_node._tree.model._interactions.add_edge(edge[0], edge[1])

        # delete the node from the graph
        self.base_node._tree.model._interactions.delete_node(str(guid))

    def set_element_by_element(self, existing_element, element):
        self.set_element_by_guid(existing_element.guid, element)

    def __getitem__(self, index_string_guid_element):
        """
        Get a child node from the ElementTree by index.

        This method allows you to retrieve a child node from the ElementTree based on its
        index in the list of children.

        Parameters
        ----------
        index : int
            The index of the child node to be retrieved.

        Returns
        -------
        Node
            The child node at the specified index.

        Raises
        ------
        TypeError
            If the index is not an integer.

        """

        # --------------------------------------------------------------------------
        # sanity checks
        # --------------------------------------------------------------------------
        if not isinstance(index_string_guid_element, (int, str, uuid.UUID, Element)):
            raise TypeError("The index must be integer, string, element.guid, or Element.")

        # --------------------------------------------------------------------------
        # change the node of the tree and update the node's tree and parent
        # --------------------------------------------------------------------------
        if isinstance(index_string_guid_element, int):
            # print("get_child_by_index")
            return self.get_child_by_index(index_string_guid_element)
        elif isinstance(index_string_guid_element, str):
            # print("get_child_by_name")
            return self.get_child_by_name(index_string_guid_element)
        elif isinstance(index_string_guid_element, uuid.UUID):
            # print("get_parent_node_by_element_guid")
            return self.get_node_by_element_guid(index_string_guid_element)
        elif isinstance(index_string_guid_element, Element):
            # print("get_parent_node_by_element")
            return self.get_node_by_element(index_string_guid_element)

    def __setitem__(self, index_string_guid_element, node_or_element):
        """
        Set a child node in the ElementTree by name.

        This method allows you to set a child node in the ElementTree at the specified name.

        Parameters
        ----------
        name : str
            The name at which to set the child node.

        node : Node
            The Node to be set as a child at the specified name.

        Raises
        ------
        TypeError
            If the provided node is not a Node object.

        """

        # --------------------------------------------------------------------------
        # sanity checks
        # --------------------------------------------------------------------------
        if not isinstance(node_or_element, (Node, Element)):
            raise TypeError("The object to replace is neither a Node nor an Element.")

        if not isinstance(index_string_guid_element, (int, str, uuid.UUID, Element)):
            raise TypeError("The index must be integer, string, element.guid, or Element.")

        # --------------------------------------------------------------------------
        # change the node of the tree and update the node's tree and parent
        # --------------------------------------------------------------------------
        if isinstance(index_string_guid_element, int) and isinstance(node_or_element, Node):
            # print("set_child_by_index")
            self.set_child_by_index(index_string_guid_element, node_or_element)
        elif isinstance(index_string_guid_element, str) and isinstance(node_or_element, Node):
            # print("set_child_by_name")
            self.set_child_by_name(index_string_guid_element, node_or_element)
        elif isinstance(index_string_guid_element, uuid.UUID) and isinstance(node_or_element, Element):
            # print("set_element_by_guid")
            self.set_element_by_guid(index_string_guid_element, node_or_element)
        elif isinstance(index_string_guid_element, Element) and isinstance(node_or_element, Element):
            # print("set_element_by_element")
            self.set_element_by_element(index_string_guid_element, node_or_element)


class Model(Data):
    """
    A class representing a model with elements, hierarchy, and interactions.

    The model is used to store a dictionary of elements where the key is the element's GUID (Global Unique Identifier),
    a hierarchical representation of the relationships between elements in a tree data structure,
    and an abstract representation of linkages or connections between elements and nodes in a graph data structure.

    Parameters:
        name (str, optional): The name of the model. Default is "my_model".
        elements (list, optional): A list of Element objects to initialize the model with. Default is an empty list.
        copy_elements (bool, optional): If True, elements are copied during initialization; if False, elements are
            added by reference. Default is False.

    Attributes:
        _elements (OrderedDict): A dictionary with GUID as keys and Element objects as values.
        _hierarchy (ElementTree): A hierarchical representation of the relationships between elements in a tree.
        _interactions (Graph): An abstract representation of linkages or connections between elements and nodes.

    Methods:
        - __init__(self, name="my_model", elements=[], copy_elements=False): Initializes a new Model instance.
        - add_elements(self, elements, copy_elements=False): Adds a list of Element objects to the model.

    Example Usage:
        # Create a model instance with a custom name and elements
        my_model = Model(name="custom_model", elements=[element1, element2])
    """

    def __init__(self, name="model", elements=[], copy_elements=False):
        """
        Initialize a new Model instance.

        Parameters:
            name (str, optional): The name of the model. Default is "my_model".
            elements (list, optional): A list of Element objects to initialize the model with. Default is an empty list.
            copy_elements (bool, optional): If True, elements are copied during initialization; if False, elements are
                added by reference. Default is False.
        """
        super(Model, self).__init__()

        # --------------------------------------------------------------------------
        # initialize the main properties of the model
        # --------------------------------------------------------------------------
        self._name = name  # the name of the model
        self._elements = OrderedDict()  # a flat collection of elements - dict{GUID, Element}
        self._hierarchy = ElementTree(model=self, name=name)  # hierarchical relationships between elements
        self._interactions = Graph(name=name)  # abstract linkage or connection between elements and nodes

        # --------------------------------------------------------------------------
        # process the user input
        # --------------------------------------------------------------------------
        self.add_elements(
            name="element", user_elements=elements, copy_elements=copy_elements
        )  # elements is a list of Element objects

        self.composition = Composition(self._hierarchy.root, self)

    # ==========================================================================
    # Serialization
    # ==========================================================================
    @property
    def data(self):

        return {
            "name": self._name,
            "elements": self._elements,
            "hierarchy": self._hierarchy.data,
            "interactions": self._interactions.data,
        }

    @classmethod
    def from_data(cls, data):
        model = cls(data["name"])
        model._elements = data["elements"]
        model._hierarchy = ElementTree.from_data(data["hierarchy"])
        model._hierarchy._model = model  # variable that points to the model class
        model._interactions = Graph.from_data(data["interactions"])
        return model

    # ==========================================================================
    # Key property getters
    # ==========================================================================
    @property
    def name(self):
        """
        Retrieve the name of the model.

        Returns
        -------
        str
            The name of the model.
        """
        return self._name

    @property
    def elements(self):
        """
        Retrieve all elements from the model.

        Returns
        -------
        dict
            A dictionary containing all elements in the model, where keys are element identifiers,
            and values are the corresponding elements.
        """
        return self._elements

    @property
    def hierarchy(self):
        """
        Retrieve the ElementTree from the model.

        Returns
        -------
        ElementTree
            The hierarchical structure of the model, represented as a ElementTree.
        """
        return self._hierarchy

    @property
    def interactions(self):
        """
        Retrieve the Graph from the model.
        Graph edges are GUID of elements

        Returns
        -------
        Graph
            The graph representing interactions between elements in the model.
        """
        return self._interactions

    # ==========================================================================
    # hierarchy methods
    # ==========================================================================

    def contains_node(self, node_name):
        return self.composition.contains_node(node_name)

    def add_elements(self, name=None, user_elements=[], copy_elements=False):
        guids = []
        for element in user_elements:
            guids.append(self.composition.add_element(name=name, element=element, copy_element=copy_elements))
        return guids

    def add_element(self, name=None, element=None, attributes=None, copy_element=False):
        return self.composition.add_element(
            name=name, element=element, attributes=attributes, copy_element=copy_element, parent=self._hierarchy.root
        )

    def add_group(self, name=None, geometry=None, attributes=None):
        return self.composition.add_group(
            name=name, geometry=geometry, attributes=attributes, parent=self._hierarchy.root
        )

    def collect_elements(self, my_node):
        self.composition.collect_elements(my_node)

    def remove_node(self, node):
        self.composition.remove_node(node)

    def find_node(self, node_name):
        return self.composition.find_node(node_name)

    def find_element_node(self, element):
        return self.composition.find_element_node(element)

    def remove_element(self, element):
        self.composition.remove_element(element)

    def insert_node(self, node, node_names=[]):
        self.composition.insert_node(node, node_names=node_names)

    def merge(self, other_model, copy_elements=False):
        self.composition.merge(other_model)

    def flatten(self, flatenned_node_name="flat_node"):
        self.composition.flatten(flatenned_node_name)

    def graft(self):
        self.composition.graft()

    def prune(self, level=0):
        self.composition.prune(level=level)

    def element_at(self, id):
        return list(self.elements.values())[id]

    def element_key_at(self, id):
        return list(self.elements.keys())[id]

    def children(self):
        return self.composition.base_node.children

    def clear_children(self):
        return self.composition.base_node._children.clear()

    # ==========================================================================
    # interactions properties and methods - self._interactions = Graph()
    # ==========================================================================
    def add_interaction_node(self, element):
        self._interactions.add_node(str(element.guid))

    def add_interaction(self, element0, element1, geometry=None):
        """
        Adds an interaction between two elements in the model.

        This method allows you to establish an interaction between two elements within the model.

        Parameters
        ----------
        element0 : Element
            The first element involved in the interaction.

        element1 : Element
            The second element involved in the interaction.

        Example
        -------
        model = Model()
        element0 = Element(...)  # Replace with actual Element instantiation.
        element1 = Element(...)  # Replace with actual Element instantiation.
        model.add_element(element0)
        model.add_element(element1)
        model.add_interaction(element0, element1)

        Returns
        -------
        tuple[hashable, hashable]
            The identifier of the edge.
        """
        # check if node exists
        # check if user inputs ElementNode or Element
        user_element0 = element0.element if isinstance(element0, ElementNode) else element0
        user_element1 = element1.element if isinstance(element1, ElementNode) else element1

        if self._interactions.has_node(str(user_element0.guid)) and self._interactions.has_node(
            str(user_element1.guid)
        ):
            if user_element0 is not None and user_element1 is not None:
                attribute_dict = {}
                attribute_dict["geometry"] = geometry
                attribute_dict["weight"] = distance_point_point(
                    user_element0.aabb_center(), user_element1.aabb_center()
                )
                return self._interactions.add_edge(str(user_element0.guid), str(user_element1.guid), attribute_dict)
        else:
            raise ValueError("The node does not exist.")

    def get_interactions(self):
        """
        Get all interactions between elements.

        Returns a list of all interactions between elements in the model.

        Returns
        -------
        list[tuple[hashable, hashable]]
            A list of tuples representing interactions, where each tuple contains two hashable
            identifiers for the elements involved in the interaction.
        """
        return list(self._interactions.edges())

    def get_interactions_geometry(self):
        """get geometric features within the interactions, if they exist"""
        return self._interactions.edges_attribute("geometry")

    def get_interactions_as_readable_info(self):
        """
        Get all interactions between elements with readable object information.

        Retrieve interactions between elements and represent them with minimal information
        about the objects involved. This method returns a list of tuples, where each tuple
        contains two strings describing the objects.

        Returns
        -------
        list[tuple(str, str)]
            A list of tuples, each containing two strings representing objects involved in
            interactions with their minimal information.
        """

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
        """
        Get all interactions between elements as lines.

        Retrieve interactions between elements and represent them as lines connecting the
        centers of the interacting elements. This method returns a list of Line objects
        representing the interactions.

        Returns
        -------
        list[Line]
            A list of Line objects representing interactions as lines between element centers.
        """

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

    def print_elements(self):
        """
        Print all elements in the model.

        This method prints all elements in the model to the console.
        """
        print(
            "================================== {} ===================================".format(self.interactions.name)
        )
        graph_nodes = list(self._interactions.nodes())
        for idx, e in enumerate(self._elements):
            print("element_guid: " + str(self._elements[e].guid) + " graph_node: " + str(graph_nodes[idx]))

    def print_interactions(self):
        """
        Print all interactions between elements.

        This method prints all interactions between elements in the model to the console.
        """
        print(
            "================================== {} ===================================".format(self.interactions.name)
        )
        edges = list(self._interactions.edges())
        for i in range(len(edges)):
            a = edges[i][0]
            b = edges[i][1]
            print("print_interactions ", str(self._elements[a].guid), " ", str(self._elements[b].guid))

    def get_interactions_as_nodes_and_neighbors_lists(self):
        nodes = []
        neighberhoods = []
        for node in self._interactions.nodes():
            nodes.append(node)
            neighberhoods.append(self._interactions.neighborhood(node))
        return (nodes, neighberhoods)

    # ==========================================================================
    # operators
    # ==========================================================================

    def get_child_by_index(self, index):
        return self.composition.get_child_by_index(index)

    def set_child_by_index(self, index, new_node):
        self.composition.set_child_by_index(index, new_node)

    def get_child_by_name(self, name):
        return self.composition.get_child_by_name(name)

    def set_child_by_name(self, name, new_node):
        self.composition.set_child_by_name(name, new_node)

    def get_node_by_element_guid(self, guid):
        return self.composition.get_node_by_element_guid(guid)

    def get_node_by_element(self, element):
        return self.composition.get_node_by_element(element)

    def set_element_by_guid(self, guid, element):
        self.composition.set_element_by_guid(guid, element)

    def set_element_by_element(self, existing_element, element):
        self.composition.set_element_by_element(existing_element, element)

    def __getitem__(self, index_string_guid_element):
        return self.composition.__getitem__(index_string_guid_element)

    def __setitem__(self, index_string_guid_element, node_or_element):
        self.composition.__setitem__(index_string_guid_element, node_or_element)

    # ==========================================================================
    # statistics
    # ==========================================================================
    @property
    def number_of_elements(self):
        """
        Get the number of elements in the model.

        Returns
        -------
        int
            The total number of elements in the model.
        """
        return len(list(self.elements))

    @property
    def number_of_nodes(self):
        """
        Count the total number of children in the tree hierarchy.

        Returns
        -------
        int
            The total number of child nodes in the tree hierarchy.
        """

        def _count(node):
            count = 0
            if node.children is None:
                return 0
            for child in node.children:
                count += 1 + _count(child)
            return count

        total_children = _count(self._hierarchy.root)
        return total_children

    @property
    def number_of_edges(self):
        """
        Get the number of edges in the model's interactions.

        Returns
        -------
        int
            The total number of edges in the interactions graph of the model.
        """
        return self._interactions.number_of_edges()

    # ==========================================================================
    # print
    # ==========================================================================

    def __repr__(self):
        """
        Return a string representation of the model for debugging and development.

        Returns
        -------
        str
            A string containing information about the model,
            including its name, number of elements, child nodes, and interactions.
        """

        return (
            "<"
            + self.__class__.__name__
            + ">"
            + " with {} elements, {} children, {} interactions, {} nodes".format(
                self.number_of_elements,
                self.number_of_nodes,
                self.number_of_edges,
                self._interactions.number_of_nodes(),
            )
        )

    def __str__(self):
        return self.__repr__()

    def print(self):
        """
        Print the spatial hierarchy of the tree for debugging and visualization.

        This method prints information about the tree's spatial hierarchy, including nodes, elements,
        parent-child relationships, and other relevant details.

        """

        print("\u2500" * 100)
        print("HIERARCHY")

        def _print(node, depth=0):
            parent_name = "None" if node.parent is None else node.parent.name

            # print current data
            message = "    " * depth + str(node) + " " + "| Parent: " + parent_name + " | Root: " + node.tree.name

            if depth == 0:
                message = str(self)

            print(message)

            # print elements
            # if isinstance(node.my_object, Element):
            #     print("    " * (depth + 1) + str(node.my_object))

            # recursively print
            if node.children is not None:
                for child in node.children:
                    _print(child, depth + 1)

        _print(self._hierarchy.root)

        print("INTERACTIONS")
        print("<Nodes>")
        for node in self._interactions.nodes():
            print(" " * 4 + str(node))
        print("<Edges>")
        for edge in self._interactions.edges():
            print(" " * 4 + str(edge[0]) + " " + str(edge[1]))
        print("\u2500" * 100)

    # ==========================================================================
    # copy model
    # ==========================================================================
    def copy(self):
        """copy the model"""

        # --------------------------------------------------------------------------
        # create the empty model
        # --------------------------------------------------------------------------
        copy = Model(name=self.name)

        # --------------------------------------------------------------------------
        # copy the hierarchy
        # --------------------------------------------------------------------------
        dict_old_guid_and_new_element = {}

        def copy_hierarchy(current_node, copy_node):
            for child in current_node.children:
                last_group_node = None
                # --------------------------------------------------------------------------
                # copy the elements
                # --------------------------------------------------------------------------
                if isinstance(child, ElementNode):
                    # copy the element
                    name = child.name
                    element = child._my_object.copy()
                    # add the element to the dictionary
                    copy._elements[str(element.guid)] = element
                    # add the element to the graph
                    copy.add_interaction_node(element)
                    # add the element to the parent
                    copy_node.add_element(name=name, element=element)
                    # add the element to the dictionary
                    dict_old_guid_and_new_element[str(child._my_object.guid)] = element
                # --------------------------------------------------------------------------
                # copy the groups
                # --------------------------------------------------------------------------
                elif isinstance(child, GroupNode):
                    # copy the group
                    name = child.name
                    geometry = None if child._my_object is None else child._my_object.copy()
                    # add the group to the parent
                    last_group_node = copy_node.add_group(name=name, geometry=geometry)
                # --------------------------------------------------------------------------
                # recursively copy the tree
                # --------------------------------------------------------------------------
                if isinstance(child, GroupNode):
                    copy_hierarchy(child, last_group_node)

        copy_hierarchy(self._hierarchy.root, copy._hierarchy.root)

        # --------------------------------------------------------------------------
        # copy the interactions, nodes should be added previously
        # --------------------------------------------------------------------------
        for edge in self._interactions.edges():
            node0 = dict_old_guid_and_new_element[edge[0]]
            node1 = dict_old_guid_and_new_element[edge[1]]
            copy.add_interaction(node0, node1)

        return copy

    def transform(self, transformation):
        """transform the model"""
        for e in self._elements.values():
            e.transform(transformation)

    def transformed(self, transformation):
        """transform the copy of the model"""
        copy = self.copy()
        copy.transform(transformation)
        return copy

    # ==========================================================================
    # Algorithms
    # ==========================================================================
    def find_interactions(
        self,
        simple_or_tree_search=True,
        detection_type=0,
        tmax=1e-2,
        amin=1e1,
        aaab_inflation=0.01,
        max_neighbors=8,
        attributes=[],
        skip_the_same=True,
    ):
        # ==========================================================================
        # ELEMENTS FROM JSON
        # ==========================================================================
        elements_list = list(self._elements.values())

        # ==========================================================================
        # FIND NEAREST OBJECTS BY
        # 1) SIMPLE 2X FOR LOOP
        # 2) KD-TREE
        # ==========================================================================
        collision_pairs = []
        if simple_or_tree_search:
            collision_pairs = Algorithms.get_collision_pairs_with_attributes(
                elements_list, attributes, aaab_inflation, skip_the_same
            )
        else:
            collision_pairs = Algorithms.get_collision_pairs_kdtree(
                elements_list, max_neighbors, True, attributes, skip_the_same
            )

        # ==========================================================================
        # INTERFACE DETECTION
        # 0 - face_to_face
        # 1 - polyline_to_polyline
        # 2 - face_to_plane
        # 3 - face_to_polyline
        # ==========================================================================
        output = []
        geometry_feature_detected = False
        if detection_type == 0:
            for idx, collision_pair in enumerate(collision_pairs):
                result = Algorithms.face_to_face(
                    elements_list[collision_pair[0]], elements_list[collision_pair[1]], tmax, amin
                )
                # print("face_to_face", collision_pair)
                # output: type, collission pair, face pair, intersection polygon
                for r in result:
                    if result:
                        output.append([collision_pair, r[0], r[1]])
            geometry_feature_detected = True

        # ==========================================================================
        # ADD GRAPH EDGES
        # ==========================================================================
        if geometry_feature_detected:
            for o in output:
                id0 = o[0][0]
                id1 = o[0][1]
                geometric_features = o[2]
                self.add_interaction(elements_list[id0], elements_list[id1], geometric_features)
        else:
            for idx, collision_pair in enumerate(collision_pairs):
                self.add_interaction(elements_list[collision_pair[0]], elements_list[collision_pair[1]])
                # self.add_interaction(elements_list[collision_pair[1]], elements_list[collision_pair[0]])

        # ==========================================================================
        # OUTPUT
        # ==========================================================================
        return output

    def find_shortest_path(self, element0, element1, output_display_geometry=False):
        elements = Algorithms.shortest_path(self, element0, element1)

        if output_display_geometry:
            # vizualize the shortest path, in this case colorize mesh faces as polygons
            geometry = []
            for element in elements:  # type: ignore
                if isinstance(element.geometry[0], Mesh):
                    polygons = element.geometry[0].to_polygons()
                    for polygon in polygons:
                        geometry.append(Polygon(polygon))
            return elements, geometry
        else:
            return elements

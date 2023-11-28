from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from collections import OrderedDict
from compas.datastructures import Graph
from compas.geometry import Line, Polygon, distance_point_point  # noqa: F401
from compas_assembly2 import Algorithms  # noqa: F401
from compas.datastructures import Datastructure
from compas.data import Data
from compas.datastructures import Mesh

# main functionality:
# the tree data-structure cannot have have nodes with the sam name to keep the order tidy
# elements
# hierarchy
# interactions
# add_element - adds an element
# add_node - adds a Node in the hierarhcy
# add_interaction - adds an interaction between two elements

# To-Do:
# create a DATASCHEMA for the model


class TreeNode(Data):
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
    parent : :class:`~compas.datastructures.TreeNode`
        The parent node of the tree node.
    children : list[:class:`~compas.datastructures.TreeNode`]
        The children of the tree node.
    tree : :class:`~compas.datastructures.Tree`
        The tree to which the node belongs.
    is_root : bool
        True if the node is the root node of the tree.
    is_leaf : bool
        True if the node is a leaf node of the tree.
    is_branch : bool
        True if the node is a branch node of the tree.
    acestors : generator[:class:`~compas.datastructures.TreeNode`]
        A generator of the acestors of the tree node.
    descendants : generator[:class:`~compas.datastructures.TreeNode`]
        A generator of the descendants of the tree node, using a depth-first preorder traversal.

    """

    DATASCHEMA = {
        "type": "object",
        "$recursiveAnchor": True,
        "properties": {
            "name": {"type": "string"},
            "attributes": {"type": "object"},
            "children": {"type": "array", "items": {"$recursiveRef": "#"}},
        },
        "required": ["name", "attributes", "children"],
    }

    def __init__(self, name=None, attributes=None):
        super(TreeNode, self).__init__(name=name)
        self.attributes = attributes or {}
        self._parent = None
        self._children = []
        self._tree = None

    def __repr__(self):
        return "<TreeNode {}>".format(self.name)

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

    @property
    def data(self):
        return {
            "name": self.name,
            "attributes": self.attributes,
            "children": [child.data for child in self.children],
        }

    @classmethod
    def from_data(cls, data):
        node = cls(data["name"], data["attributes"])
        for child in data["children"]:
            node.add(cls.from_data(child))
        return node

    def add(self, node):
        """
        Add a child node to this node.

        Parameters
        ----------
        node : :class:`~compas.datastructures.TreeNode`
            The node to add.

        Returns
        -------
        None

        Raises
        ------
        TypeError
            If the node is not a :class:`~compas.datastructures.TreeNode` object.

        """
        if not isinstance(node, TreeNode):
            raise TypeError("The node is not a TreeNode object.")
        if node not in self._children:
            self._children.append(node)
        node._parent = self

    def remove(self, node):
        """
        Remove a child node from this node.

        Parameters
        ----------
        node : :class:`~compas.datastructures.TreeNode`
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
        :class:`~compas.datastructures.TreeNode`
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


class Tree(Datastructure):
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
    root : :class:`~compas.datastructures.TreeNode`
        The root node of the tree.
    nodes : generator[:class:`~compas.datastructures.TreeNode`]
        The nodes of the tree.
    leaves : generator[:class:`~compas.datastructures.TreeNode`]
        A generator of the leaves of the tree.

    Examples
    --------
    >>> tree = Tree(name='tree')
    >>> root = TreeNode('root')
    >>> branch = TreeNode('branch')
    >>> leaf1 = TreeNode('leaf1')
    >>> leaf2 = TreeNode('leaf2')
    >>> tree.add(root)
    >>> root.add(branch)
    >>> branch.add(leaf1)
    >>> branch.add(leaf2)
    >>> print(tree)
    <Tree with 4 nodes>
    >>> tree.print()
    <TreeNode root>
        <TreeNode branch>
            <TreeNode leaf1>
            <TreeNode leaf2>

    """

    DATASCHEMA = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "root": TreeNode.DATASCHEMA,
            "attributes": {"type": "object"},
        },
        "required": ["name", "root", "attributes"],
    }

    def __init__(self, name=None, attributes=None):
        super(Tree, self).__init__(name=name)
        self.attributes.update(attributes or {})
        self._root = None

    @property
    def data(self):
        return {
            "name": self.name,
            "root": self.root.data,
            "attributes": self.attributes,
        }

    @classmethod
    def from_data(cls, data):
        tree = cls(data["name"], data["attributes"])
        root = TreeNode.from_data(data["root"])
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
        node : :class:`~compas.datastructures.TreeNode`
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
        :class:`~compas.datastructures.TreeNode`
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
        :class:`~compas.datastructures.TreeNode`
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
        list[:class:`~compas.datastructures.TreeNode`]
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


class Node(TreeNode):
    def __init__(self, name=None, elements=None, attributes=None):
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
        super(Node, self).__init__(name=name, attributes=attributes)
        self._children = []  # a sorted list of TreeNode objects instead of set()
        self._elements = []  # attributes of the node

        # --------------------------------------------------------------------------
        # user input - add elements to the current node and base tree model, if it exists
        # --------------------------------------------------------------------------
        self.add_elements(elements)

    # ==========================================================================
    # Serialization
    # ==========================================================================
    @property
    def data(self):
        return {
            "name": self.name,
            "attributes": self.attributes,
            "children": [child.data for child in self.children],
            "elements": self.elements,
        }

    @classmethod
    def from_data(cls, data):
        elements = data["elements"]
        node = cls(name=data["name"], elements=elements, attributes=data["attributes"])
        for child in data["children"]:
            node.add(cls.from_data(child))
        return node

    # ==========================================================================
    # properties
    # ==========================================================================

    @property
    def elements(self):
        """
        Get the list of elements or attributes associated with the Node.

        Returns
        -------
        list
            A list of elements or attributes linked to the Node.
        """
        return self._elements

    def clear_elements(self):
        """
        Clear the list of elements or attributes associated with the Node.

        Returns
        -------
        None
        """
        self._elements = []

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
        """
        Clear the list of elements or attributes associated with the Node.

        Returns
        -------
        None
        """
        self._children = []

    # ==========================================================================
    # less than to add elements to the SortedList
    # ==========================================================================

    def __contains__(self, item):
        for child in self._children:
            if child.name == item.name:
                return True
        return False

    def __lt__(self, other):
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
        if isinstance(self.name, str) and isinstance(other.name, str):
            return self.name < other.name
        elif isinstance(self.name, int) and isinstance(other.name, int):
            # returns false to add the element to the end of the list
            return self.name < other.name
        else:
            return False

    # ==========================================================================
    # operators
    # ==========================================================================

    def __getitem__(self, name):
        """
        Get the child element at the specified index.

        Parameters:
            index (int): The index of the child element to retrieve.

        Returns:
            The child element at the specified index.

        Raises:
            TypeError: If the index is not an integer.

        Example Usage:
            # Get the child element at index 0
            child_element = parent_element[0]
        """
        # --------------------------------------------------------------------------
        # sanity checks
        # --------------------------------------------------------------------------
        if isinstance(name, str):
            for child in self._children:
                if child.name == name:
                    return child
        else:
            raise TypeError("The name must be a string.")

        # if isinstance(index, int):
        #     return self._children[index]
        # else:
        #     raise TypeError("The index must be an integer.")

    def remove_all_elements_from_the_current_node(self):
        """
        Remove all elements from the current node.

        Example Usage:
            # Remove all elements from the current node
            node.remove_all_elements_from_the_current_node()
        """

        # remove elements from the element dictionary
        for e in self._elements:
            del self.tree._model._elements[str(e.guid)]  # type: ignore

        # remove the node from the graph
        for e in self._elements:
            self.tree._model._interactions.delete_node(str(e.guid))  # type: ignore

        # clear the current node list of elements
        self._elements.clear()

    def remove_all_children_from_the_current_node(self):

        # remove all the elements from all the childs
        for child in self._children:
            child.remove_all_elements_from_the_current_node()
            for future_child in child._children:
                future_child.remove_all_children_from_the_current_node()

        # remove all the childs, the childs are stored as SortedList()
        self._children.clear()
        del self._children

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

    def add_elements_to_the_model_dictionary(self, Node):
        """
        Add elements from the current node to the base dictionary of Model class.

        Example Usage:
            # Add elements from the current node to the base dictionary of Model class
            node.add_elements_to_the_model_dictionary()
        """
        for e in Node._elements:
            self.tree._model._elements[str(e.guid)] = e  # type: ignore
            self.tree._model.add_interaction_node(e)  # type: ignore

        for childnode in Node._children:
            childnode.add_elements_to_the_model_dictionary(childnode)

    def __setitem__(self, name, node):
        """
        Set the child element at the specified index to the given Node.
        WARNING: if the interactions property has edges, they are not updated

        This method allows you to replace a child element at the specified index with the provided Node.

        Parameters:
            index (int): The index of the child element to set.
            Node (Node): The Node object to set at the specified index.

        Raises:
            TypeError: If Node is not a Node object.
            TypeError: If the index is not an integer.

        Example Usage:
            # Set the child element at index 0 to a new Node
            parent_element[0] = new_model_node
        """

        # --------------------------------------------------------------------------
        # sanity checks
        # --------------------------------------------------------------------------
        if not isinstance(node, Node):
            raise TypeError("The node is not a Node object.")

        if not isinstance(name, str):
            raise TypeError("The index must be an str")

        index = None
        for child in self._children:
            if child.name == name:
                index = self._children.index(child)
                break

        if index is None:
            raise TypeError("The name does not exist")

        # --------------------------------------------------------------------------
        # Step 1 - remove elements from the old node and the Model _elements dictionary
        # --------------------------------------------------------------------------
        self._children[index].remove_all_elements_from_the_current_node()

        # --------------------------------------------------------------------------
        # Step 2 - all the children
        # --------------------------------------------------------------------------
        self._children[index].remove_all_children_from_the_current_node()

        # --------------------------------------------------------------------------
        # change the node of the tree and update the node's tree and parent
        # --------------------------------------------------------------------------
        temp_tree = self._children[index].tree
        temp_parent = self._children[index].parent
        self._children[index] = node
        self._children[index]._parent = temp_parent
        self._children[index]._tree = temp_tree

        # --------------------------------------------------------------------------
        # assign all the future childs of childs tree to the current branch tree
        # --------------------------------------------------------------------------
        self.change_base_tree(self.tree)

        # --------------------------------------------------------------------------
        # add elements to the model dictionary
        # --------------------------------------------------------------------------
        self.add_elements_to_the_model_dictionary(node)

    def __call__(self, index, value=None):
        """
        Get or set an element within the ElementTree by index.

        This method allows you to retrieve an element from the ElementTree by its index. You can also set an element at
        the specified index by providing a 'value'.

        Parameters:
            index (int): The index of the element to retrieve or set.
            value: The value to set at the specified index, if provided.

        Returns:
            Element: If 'value' is not provided, the element at the specified index.
            None: If 'value' is provided, and the element is set.

        """
        if value is None:
            return self.get_element(index)  # type: ignore
        else:
            self.set_element(index, value)  # type: ignore

    def get_element(self, index):
        """
        Get an element at the specified index.

        This method allows you to retrieve an element from the ElementTree by its index.

        Parameters:
            index (int): The index of the element to retrieve.

        Returns:
            Element: The element at the specified index.
        """
        return self._elements[index]

    def set_element(self, index, other_element):
        """
        Set the element of the current node to the given element.
        WARNING: if the interactions property has edges, they are not updated

        Parameters:
            other_element: The element to set for the current node.

        Example Usage:
            # Set the element of the current node to the given element
            node.set_element(other_element)
        """

        # --------------------------------------------------------------------------
        # first delete the old element from the Model _elements dictionary
        # --------------------------------------------------------------------------
        del self.tree._model.elements[str(self._elements[index].guid)]  # type: ignore

        # --------------------------------------------------------------------------
        # then add the new element to the Model _elements dictionary
        # --------------------------------------------------------------------------
        self.tree._model.elements[str(other_element.guid)] = other_element  # type: ignore

        # --------------------------------------------------------------------------
        # then apdate the graph
        # step 1 - get connected edges to the current node
        # step 2 - replace the node in the edges with the new one - do not need to delete edges
        # step 3 - delete the node from the graph
        # step 4 - add the new node to the graph
        # --------------------------------------------------------------------------

        edges = self.tree._model._interactions.connected_edges(str(self._elements[index].guid))  # type: ignore
        new_edges = []

        for edge in edges:
            if edge[0] == str(self._elements[index].guid):
                new_edges.append((str(other_element.guid), edge[1]))
            elif edge[1] == str(self._elements[index].guid):
                new_edges.append((edge[0], str(other_element.guid)))
            else:
                new_edges.append((edge[0], edge[1]))  # type: ignore

        self.tree._model._interactions.delete_node(str(self._elements[index].guid))  # type: ignore
        self.tree._model._interactions.add_node(str(other_element.guid))  # type: ignore

        for edge in new_edges:
            self.tree._model._interactions.add_edge(edge[0], edge[1])  # type: ignore

        # --------------------------------------------------------------------------
        # then update the element in the current node
        # --------------------------------------------------------------------------
        self._elements[index] = other_element

    # ==========================================================================
    # element properties and methods - self._elements = OrderedDict()
    # ==========================================================================

    def add_elements(self, user_elements):
        """
        Add a list of elements to the model (current node list and root dictionary).

        Parameters:
            elements (list): A list of elements to add to the model.

        Example Usage:
            # Add a list of elements to the model
            model.add_elements([element1, element2])
        """
        # --------------------------------------------------------------------------
        # the user input can be empty if the branch only store a name
        # --------------------------------------------------------------------------
        if user_elements is None:
            return

        # --------------------------------------------------------------------------
        # check if the user tries to add elements with the same GUID
        # --------------------------------------------------------------------------
        temp_guid_dict = {}
        all_elements_are_unique = True
        for e in user_elements:
            if str(e.guid) in temp_guid_dict:
                all_elements_are_unique = False
                break
            else:
                temp_guid_dict[str(e.guid)] = e

        if all_elements_are_unique is False:
            print(
                "WARNING: you are adding multiple elements with the same GUID,"
                + " the elements will be copied to avoid multi-referencing"
            )

        # --------------------------------------------------------------------------
        # depending if the condition is met add elements to the tree or make individual copies
        # --------------------------------------------------------------------------
        for element in user_elements:
            if all_elements_are_unique is False:
                element_copy = element.copy()
                self.add_element(element_copy)
            else:
                self.add_element(element)

    def add_element(self, element):
        """
        Add an element to the model (current node list and root dictionary).

        Parameters:
            element: An element to add to the model.

        Example Usage:
            # Add an element to the model
            model.add_element(element)
        """
        if element is not None:
            # add elements to the current node
            self._elements.append(element)

            # if the node is part of a tree, then add elements to the base dictionary of Model class
            if self.tree:
                # update the root class
                self.tree._model._elements[str(element.guid)] = element

                # add the node to the graph
                self.tree._model.add_interaction_node(element)

    # ==========================================================================
    # interactions properties and methods - self._interactions = Graph()
    # ==========================================================================

    def add_node(self, node):
        """
        Add a child node to this node. This function is overridden to use SortedList instead of set().

        Parameters:
            node (Node): The child node to add to this node.

        Raises:
            TypeError: If the node is not a Node object.

        Example Usage:
            # Add a child node to this node
            parent_node.add(child_node)
        """
        if not isinstance(node, Node):
            raise TypeError("The node is not a TreeNode object.")
        if node not in self._children:
            self._children.append(node)

            if self.tree is not None:
                if self.tree._model is not None:
                    # add elements from the current node to the base dictionary of Model class
                    root = self.tree
                    for e in node._elements:
                        root._model.elements[str(e.guid)] = e  # type: ignore

                    # add the node to the graph
                    for e in node._elements:
                        root._model.add_interaction_node(e)  # type: ignore

            node._parent = self

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
        return "<Node> {}, elements [{}]".format(self.name, len(self._elements))

    def __str__(self):
        return self.__repr__()


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
        self._root = None  # the root Node of the tree
        self._model = model  # variable that points to the model class

        # --------------------------------------------------------------------------
        # process the user input
        # --------------------------------------------------------------------------
        self.add(Node(name=name))  # the name can be empty
        # if self._model is not None:
        #     self._model.add_elements(elements)  # elements is a list of Element objects

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
            nodes.append(Node.from_data(node))
        for node in nodes:
            model_tree.add_node(node)
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
        """
        Get the number of elements in the tree.

        Returns:
            int: The number of elements in the tree.
        """
        count = 0

        def count_elements(node, count):
            for child in node.children:
                count += len(child.elements)
                count_elements(child, count)  # type: ignore
            return count

        count = count_elements(self.root, count)  # type: ignore
        return count

    # ==========================================================================
    # hierarchy methods: add Node, add_by_path
    # ==========================================================================

    def add_node(
        self,
        node,
        parent=None,
    ):
        """
        Add a node to the tree.

        Parameters:
            node (TreeNode): The node to add to the tree.
            parent (TreeNode): The parent node under which to add the new node. Default is None.

        Raises:
            TypeError: If the node is not a TreeNode object or if the parent is not a TreeNode object.
            ValueError: If the node already has a parent or if the tree already has a root node.

        Example Usage:
            # Add a node to the tree as a root node
            tree.add(node)
            # Add a node to the tree as a child of a parent node
            tree.add(node, parent=parent_node)
        """
        if not isinstance(node, TreeNode):
            raise TypeError("The node is not a TreeNode object.")

        if node.parent:
            raise ValueError("The node already has a parent, remove it from that parent first.")

        if parent is None:

            # WARNING: custom implementation, add the node as a root node
            if self.root is not None:
                self._root.add(node)  # type: ignore
                node._tree = self._root  # type: ignore

                if self._model is not None:
                    for e in node.elements:  # type: ignore
                        self._model.elements[str(e.guid)] = e  # type: ignore

                return node
                raise ValueError("The tree already has a root node, remove it first.")

            self._root = node
            node._tree = self  # type: ignore

        else:
            # add the node as a child of the parent node
            if not isinstance(parent, Node):
                raise TypeError("The parent node is not a Node object.")

            if parent.tree is not self:
                raise ValueError("The parent node is not part of this tree.")

            parent.add(node)
            return node

    def insert_element(self, element, path=[], duplicate=False):
        """
        Add an element to the tree using a specified path.

        Parameters:
            element (Element): The element to add to the tree.
            path (list): A list of path names specifying the location where the element should be added.
            duplicate (bool): Whether to allow duplicate elements in the tree. Default is False.

        Example Usage:
            # Add an element to the tree using a path
            tree.insert_element(element, path=["path_name"])
        """

        # add element to the dictionary
        self._model.elements[str(element.guid)] = element  # type: ignore
        branch = self.root

        node = None
        for path_name in path:

            # check if there are branches with the same name

            found = False
            for b in branch._children:  # type: ignore
                if b.name == str(path_name):
                    node = b
                    found = True
                    break

            if found is False:
                node = Node(name=str(path_name), elements=[])
                branch.add(node)  # type: ignore

            branch = node
        node.add_element(element)  # type: ignore

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
        """
        Return a string representation of the ElementTree.

        Returns:
            str: A string representation of the ElementTree.

        Example Usage:
            # Get a string representation of the ElementTree
            tree_str = str(model_tree)
        """
        return self.__repr__()

    def print(self):
        """
        Print the spatial hierarchy of the tree for debugging and visualization.

        This method prints information about the tree's spatial hierarchy, including nodes, elements,
        parent-child relationships, and other relevant details.

        """

        def _print(node, depth=0):

            parent_name = "None" if node.parent is None else node.parent.name

            # print current data
            print("-" * 100)
            message = "    " * depth + str(node) + " " + " | Parent: " + parent_name + " | Root: " + node.tree.name

            if depth == 0:
                message += " | Elements: " + "{" + str(node.tree.number_of_elements) + "}"

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
        """
        Add an interaction between two elements.

        Parameters:
            element0 (Element): The first element involved in the interaction.
            element1 (Element): The second element involved in the interaction.

        Example Usage:
            # Add an interaction between two elements
            model.add_interaction(element1, element2)
        """

        if element0 is not None and element1 is not None:
            self._interactions.add_edge(str(element0.guid), str(element1.guid))  # type: ignore

    def get_interactions(self):
        """
        Get all interactions between elements.

        Returns:
            list: A list of tuples representing interactions between elements.

        Example Usage:
            # Get a list of all interactions between elements
            interactions = model.get_interactions()
        """
        return list(self._interactions.edges())  # type: ignore

    def get_interactions_as_readable_info(self):
        """
        Get all interactions between elements as readable information.

        Returns:
            list: A list of tuples representing interactions between elements in a readable format.

        Example Usage:
            # Get a list of interactions between elements in a readable format
            readable_interactions = model.get_interactions_as_readable_info()
        """

        # create dictionary of elements ids
        dict_guid_and_index = {}
        counter = 0
        for key in self._elements:  # type: ignore
            dict_guid_and_index[key] = counter
            counter = counter + 1

        edges = self.get_interactions()
        readable_edges = []
        for i in range(len(edges)):
            a = edges[i][0]
            b = edges[i][1]
            obj0 = self._elements[a].name + " " + str(dict_guid_and_index[a])  # type: ignore
            obj1 = self._elements[b].name + " " + str(dict_guid_and_index[b])  # type: ignore
            readable_edges.append((obj0, obj1))
        return readable_edges

    def get_interactions_as_lines(self):
        """
        Get all interactions between elements as lines.

        Returns:
            list: A list of Line objects representing interactions between elements as lines.

        Example Usage:
            # Get a list of interactions between elements as lines
            interaction_lines = model.get_interactions_as_lines()
        """
        lines = []
        edges = self.get_interactions()
        for i in range(len(edges)):
            a = edges[i][0]
            b = edges[i][1]
            point0 = self._elements[a].aabb_center()  # type: ignore
            point1 = self._elements[b].aabb_center()  # type: ignore
            line = Line(point0, point1)
            lines.append(line)
        return lines

    # ==========================================================================
    # operators
    # ==========================================================================

    def __getitem__(self, name):
        """
        Get the child Node at the specified index.

        Parameters:
            index (int): The index of the child Node to retrieve.

        Returns:
            The child Node at the specified index.

        Raises:
            TypeError: If the index is not an integer.

        Example Usage:
            # Get the child Node at index 0
            child_node = model_tree[0]
        """
        # --------------------------------------------------------------------------
        # sanity checks
        # --------------------------------------------------------------------------
        if not isinstance(name, str):
            raise TypeError("The name is not a string.")

        # --------------------------------------------------------------------------
        # return the node
        # --------------------------------------------------------------------------
        return self._root[name]  # type: ignore

    def __setitem__(self, name, model_node):
        """
        Set the child Node at the specified index to the given Node.

        Parameters:
            index (int): The index of the child Node to set.
            model_node (Node): The Node object to set at the specified index.

        Raises:
            TypeError: If model_node is not a Node object.

        Example Usage:
            # Set the child Node at index 0 to a new Node
            model_tree[0] = new_model_node
        """
        # --------------------------------------------------------------------------
        # sanity checks
        # --------------------------------------------------------------------------
        if not isinstance(model_node, Node):
            raise TypeError("The node is not a Node object.")

        if not isinstance(name, str):
            raise TypeError("The name must be an integer")

        # --------------------------------------------------------------------------
        # Step 1 - remove elements from the old node and the Model _elements dictionary
        # --------------------------------------------------------------------------
        self._root[name] = model_node  # type: ignore

    def __call__(self, index, value=None):
        """
        Get or set an element within the ElementTree by index.

        This method allows you to retrieve an element from the ElementTree by its index. You can also set an element at
        the specified index by providing a 'value'.

        Parameters:
            index (int): The index of the element to retrieve or set.
            value: The value to set at the specified index, if provided.

        Returns:
            Element: If 'value' is not provided, the element at the specified index.
            None: If 'value' is provided, and the element is set.

        """
        if value is None:
            return self._root.get_element(index)  # type: ignore
        else:
            self._root.set_element(index, value)  # type: ignore


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

    def __init__(self, name="root", elements=[], copy_elements=False):
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
        self._hierarchy = ElementTree(self, name)  # hierarchical relationships between elements
        self._interactions = Graph(name=name)  # abstract linkage or connection between elements and nodes

        # --------------------------------------------------------------------------
        # process the user input
        # --------------------------------------------------------------------------
        self.add_elements(elements, copy_elements)  # elements is a list of Element objects

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
    # element properties and methods - self._elements = OrderedDict()
    # ==========================================================================

    def contains_node(self, node_name):
        for child in self.hierarchy.root._children:  # type: ignore
            if child.name == node_name:
                return True
        return False

    def add_elements(self, user_elements, copy_elements=False):
        """
        Add a list of elements to the model, ensuring GUID uniqueness.

        This method allows you to add a list of elements to the model. If the list contains
        elements with the same GUID, it checks for uniqueness and, if needed, makes copies
        of the elements to avoid multi-referencing.

        Parameters:
            user_elements (list): A list of elements to add to the model.
            copy_elements (bool, optional): If True, elements are copied during addition to
                avoid multi-referencing. Default is False.

        Example Usage:
            # Add a list of elements to the model
            model.add_elements([element1, element2])
        """
        # --------------------------------------------------------------------------
        # The user input can be empty if the branch only stores a name.
        # --------------------------------------------------------------------------
        if user_elements is None:
            return

        # --------------------------------------------------------------------------
        # Check if the user tries to add elements with the same GUID.
        # --------------------------------------------------------------------------
        temp_guid_dict = {}
        all_elements_are_unique = True
        if not copy_elements:
            for e in user_elements:
                if str(e.guid) in temp_guid_dict:
                    all_elements_are_unique = False
                    break
                else:
                    temp_guid_dict[str(e.guid)] = e

            if not all_elements_are_unique:
                print(
                    "WARNING: You are adding multiple elements with the same GUID. "
                    "The elements will be copied to avoid multi-referencing."
                )
        else:
            all_elements_are_unique = False

        # --------------------------------------------------------------------------
        # Depending on whether the condition is met, add elements to the tree or make individual copies.
        # --------------------------------------------------------------------------
        added_elements = []
        for element in user_elements:
            if not all_elements_are_unique:
                element_copy = element.copy()
                self.add_element(element_copy)
                added_elements.append(element_copy)
            else:
                self.add_element(element)
                added_elements.append(element)

        return added_elements

    def add_element(self, element, copy_element=False):
        """
        Adds an element to the model.

        This method allows you to add a single element to the model, and the element is stored
        in the model's elements dictionary.

        Also, this method is mainly used by the ElementTree and Node classes to add elements to the Model class.

        Parameters
        ----------
        element : Element
            The element to be added to the model.

        Returns
        -------
        Element
            The added element.

        Example
        -------
        model = Model()
        new_element = Element(...)  # Replace with actual Element instantiation.
        model.add_element(new_element)
        model_elements = model.elements  # Access the elements property to get the added element.

        """

        if element is not None:
            element_copy = element.copy() if copy_element else element
            element_guid = str(element_copy.guid)
            self.elements[element_guid] = element_copy
            self.add_interaction_node(element_copy)
            return element_copy

    def get_element(self, key):
        return self.elements[key]

    def element_at(self, id):
        return list(self.elements.values())[id]

    def element_key_at(self, id):
        return list(self.elements.keys())[id]

    # ==========================================================================
    # hierarchy methods: add Node, add_by_poath
    # ==========================================================================

    def add_node(self, node, parent=None):
        """
        Add a node to the model.

        This method allows you to add a node to the model. If the node is added as a root node,
        it is added to the model's elements dictionary.

        Parameters
        ----------
        node : Node
            The node to be added to the model.

        parent : Node, optional
            The parent node under which to add the new node. Default is None.

        Returns
        -------
        Node
            The added node.

        Raises
        ------
        TypeError
            If the node is not a Node object or if the parent is not a Node object.

        ValueError
            If the node already has a parent or if the tree already has a root node.

        Example
        -------
        model = Model()
        new_node = Node(...)
        """

        self._hierarchy.add_node(node=node, parent=parent)

    def insert_node(self, node, path=[], duplicate=False):
        """
        Add a node to the model using a specified path.

        This method allows you to add a node to the model using a specified path. If the node is added as a root node,
        it is added to the model's elements dictionary.

        Parameters
        ----------
        node : Node
            The node to be added to the model.

        path : list, optional
            A list of path names specifying the location where the node should be added. Default is [].

        duplicate : bool, optional
            Whether to allow duplicate nodes in the model. Default is False.

        Returns
        -------
        Node
            The added node.

        Example
        -------
        model = Model()
        new_node = Node(...)
        """

        # add element to the dictionary
        branch = self._hierarchy.root
        paths = path  # [1:]

        for idx, path_name in enumerate(paths):

            # check if there are branches with the same name
            found = False
            for b in branch._children:  # type: ignore
                if b.name == str(path_name):
                    branch = b
                    found = True
                    break

            if found and idx == len(paths) - 1:
                branch.add_node(node)  # type: ignore
                break

            if found is False:
                return

    def insert_element(self, node, path=[], duplicate=False):
        self._hierarchy.insert_element(node, path, duplicate)

    def merge(self, other_model, copy_elements=False):
        """merge current model with the other model"""

        # --------------------------------------------------------------------------
        # merge elements
        # collect the added elements and their guids, incase they are copied
        # --------------------------------------------------------------------------
        dict_old_guid_and_new_guid = {}
        dict_old_guid_and_new_element = {}
        for element in other_model.elements.values():
            old_guid = str(element.guid)
            added_element = self.add_element(element, True)
            dict_old_guid_and_new_guid[old_guid] = str(added_element.guid)  # type: ignore
            dict_old_guid_and_new_element[old_guid] = added_element

        # --------------------------------------------------------------------------
        # merge interactions
        # add the graph edges based on the new mapping
        # --------------------------------------------------------------------------
        other_model_edges = other_model._interactions.edges()
        for edge in other_model_edges:
            node0 = dict_old_guid_and_new_element[edge[0]]
            node1 = dict_old_guid_and_new_element[edge[1]]
            self.add_interaction(node0, node1)

        # self.print_elements()
        # self.print_interactions()

        # --------------------------------------------------------------------------
        # merge hierarchy
        # replace the elements with the new ones
        # there can be two cases:
        # 1. the other model has the same
        # 2. the other model has similar hierarchy
        # 3. the other model has a different hierarchy
        # --------------------------------------------------------------------------

        # step 1 replace the elements with the new ones, incase they are copied
        def replace_elements(node):
            for element in node.elements:
                element = dict_old_guid_and_new_element[str(element.guid)]

            # recursively replace elements
            for child in node.children:
                replace_elements(child)

        replace_elements(other_model.hierarchy.root)

        # step 2 add nodes to the tree
        def add_nodes(main_node_childs, other_node_childs):
            # step one check if there nodes with the same name, if it is just merge the elements

            for other_node_child in other_node_childs:
                found = False
                for idx, main_node_child in enumerate(main_node_childs):
                    if main_node_child.name == other_node_child.name:
                        found = True
                        # add elements from the current node to the base dictionary of Model class
                        main_node_child._elements = main_node_child.elements + other_node_child.elements
                        # and recusively repeat the process
                        add_nodes(main_node_child.children, other_node_child.children)
                        break
                # if no matching name was found, add the whole node to the tree
                if found is False:
                    main_node_childs.append(other_node_child)

        add_nodes(self._hierarchy.root.children, other_model._hierarchy.root.children)  # type: ignore

    def flatten(self, flatenned_node_name="flat_node"):
        """flatten the hierarchy structure"""

        # step1 - get elements from the hierarchy
        all_node_elements = []
        all_node_elements.extend(self.hierarchy.root.elements)

        def collect_elements(node):
            for child in node.children:
                all_node_elements.extend(child.elements)
                collect_elements(child)

        collect_elements(self.hierarchy.root)
        # step2 - remove all nodes from the hierarchy
        self.hierarchy.root.clear_children()  # type: ignore

        # step3 - create a new node with the collected elements
        self.hierarchy.add_node(node=Node(name=flatenned_node_name, elements=all_node_elements))

    def _graft_node(self, node):
        if len(node.elements) > 1:
            for idx, element in enumerate(node.elements):
                grafted_node = Node(name=str(idx), elements=[element])
                self.hierarchy.add_node(node=grafted_node, parent=node)
            node.elements.clear()

        for child in node.children:
            self._graft_node(child)

    def graft(self):
        """in hierarchy structure place elements into separate nodes"""
        for child in self.hierarchy.root.children:  # type: ignore
            self._graft_node(child)

    def prune(self, level=0):
        # Prune the tree by moving elements from child nodes to parent nodes and deleting child nodes.
        if level == 0:
            self.flatten()
            return

        def flatten_the_deeper_level_while_taking_all_the_elements(node):
            if len(node.children) == 0:
                return
            else:
                for child in node.children:
                    flatten_the_deeper_level_while_taking_all_the_elements(child)
                for child in node.children:
                    node.elements.extend(child.elements)
                node.clear_children()

        def traverse_the_tree_and_prune(node, current_level):
            if current_level == 0:
                flatten_the_deeper_level_while_taking_all_the_elements(node)
            else:
                for child in node.children:
                    traverse_the_tree_and_prune(child, current_level - 1)

        # Ensure the specified level is within the valid range of the tree.
        if level < 0:
            raise ValueError("Level must be a non-negative integer.")

        # Start pruning from the root node.
        traverse_the_tree_and_prune(self.hierarchy.root, level)

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

        if element0 is not None and element1 is not None:
            attribute_dict = {}
            attribute_dict["geometry"] = geometry
            attribute_dict["weight"] = distance_point_point(element0.aabb_center(), element1.aabb_center())
            return self._interactions.add_edge(str(element0.guid), str(element1.guid), attribute_dict)

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

    def __getitem__(self, name):
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
        # return the root node
        # --------------------------------------------------------------------------
        return self._hierarchy._root[name]  # type: ignore

    def __setitem__(self, name, node):
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
        if not isinstance(node, Node):
            raise TypeError("The node is not a Node object.")

        # --------------------------------------------------------------------------
        # change the node of the tree and update the node's tree and parent
        # --------------------------------------------------------------------------
        the_node = self._hierarchy._root._children[name]  # type: ignore
        the_node = node  # type: ignore
        the_node._tree = self  # type: ignore
        the_node._parent = self  # type: ignore
        # self._hierarchy._root._children.add(model_node)  # type: ignore
        # self._hierarchy._nodes[index]._tree = self  # type: ignore
        # self._hierarchy._nodes[index]._parent = self  # type: ignore

        # --------------------------------------------------------------------------
        # temporary disavk^^
        # if index is 0, then set all properties related to the root node
        # --------------------------------------------------------------------------
        # if index == 0:
        #     self._hierarchy._root._children = self._nodes[index]  # type: ignore

    def __call__(self, index):
        """
        Get an element by index.

        This method allows you to retrieve an element from the dictionary-like structure
        by providing the index.

        Parameters
        ----------
        index : int
            The index of the element to be retrieved.

        Returns
        -------
        Element
            The element at the specified index.2

        """
        key = list(self._elements.keys())[index]
        return self._elements[key]

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
    def number_of_childs_in_hierarchy(self):
        """
        Count the total number of children in the tree hierarchy.

        Returns
        -------
        int
            The total number of child nodes in the tree hierarchy.
        """

        def _count(node):
            count = 0
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
        name = self._hierarchy.name
        return (
            "Model "
            + "<"
            + name
            + ">"
            + " with {} elements, {} children, {} interactions, {} nodes".format(
                self.number_of_elements,
                self.number_of_childs_in_hierarchy,
                self.number_of_edges,
                self._interactions.number_of_nodes(),
            )
        )

    def __str__(self):
        """
        Return a user-friendly string representation of the model.

        Returns
        -------
        str
            A user-friendly string containing information about the model,
            including its name, number of elements, child nodes, and interactions.
        """

        return self.__repr__()

    def print(self):
        """
        Print the spatial hierarchy of the tree for debugging and visualization.

        This method prints information about the tree's spatial hierarchy, including nodes, elements,
        parent-child relationships, and other relevant details.

        """

        def _print(node, depth=0):

            parent_name = "None" if node.parent is None else node.parent.name

            # print current data
            print("-" * 100)
            message = "    " * depth + str(node) + " " + " | Parent: " + parent_name + " | Root: " + node.tree.name

            if depth == 0:
                # message += " | Elements: " + "{" + str(len(node.tree._model._elements)) + "}"
                message = str(self)

            print(message)

            # print elements
            for e in node._elements:
                print("    " * (depth + 1) + str(e))

            # recursively print
            for child in node.children:
                _print(child, depth + 1)

        _print(self._hierarchy.root)

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
        # copy the elements
        # --------------------------------------------------------------------------
        dict_old_guid_and_new_element = {}
        for e in self._elements.values():
            dict_old_guid_and_new_element[str(e.guid)] = copy.add_element(e, True)

        # --------------------------------------------------------------------------
        # copy the hierarchy
        # --------------------------------------------------------------------------
        def copy_nodes(main_node_childs, other_node_childs):

            # recursively copy nodes
            for idx, other_node_child in enumerate(other_node_childs):

                # copy the child elements
                elements_copied = []
                for element in main_node_childs[idx].elements:
                    elements_copied.append(dict_old_guid_and_new_element[str(element.guid)])

                copy._hierarchy.add_node(Node(name=main_node_childs[idx].name, elements=elements_copied))

                # recursively copy nodes
                copy_nodes(main_node_childs[idx].children, other_node_child.children)

        copy_nodes(self._hierarchy.root.children, self._hierarchy.root.children)  # type: ignore

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

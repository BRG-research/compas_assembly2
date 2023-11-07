from collections import OrderedDict
from compas.datastructures import Graph
from compas.geometry import Line  # noqa: F401
from compas_assembly2 import Tree, TreeNode


class ModelNode(TreeNode):
    def __init__(self, name=None, elements=None, attributes=None):
        """
        Initialize a ModelNode.

        Parameters
        ----------
        name : str, optional
            A name or identifier for the node.

        elements : list, optional
            A list of attributes or elements to be associated with the node.

        attributes : dict, optional
            A dictionary of additional attributes to be associated with the node.

        """
        super(ModelNode, self).__init__(name=name, attributes=attributes)
        self._children = []  # a sorted list of TreeNode objects instead of set()
        self._elements = []  # attributes of the node

        # --------------------------------------------------------------------------
        # user input - add elements to the current node and base tree model, if it exists
        # --------------------------------------------------------------------------
        self.add_elements(elements)

    # ==========================================================================
    # properties
    # ==========================================================================

    @property
    def elements(self):
        """
        Get the list of elements or attributes associated with the ModelNode.

        Returns
        -------
        list
            A list of elements or attributes linked to the ModelNode.
        """
        return self._elements

    @property
    def children(self):
        """
        Get the child nodes of the ModelNode.

        Returns
        -------
        SortedList
            A sorted list of child nodes (ModelNode objects) linked to the current ModelNode.
        """
        return self._children

    # ==========================================================================
    # less than to add elements to the SortedList
    # ==========================================================================

    def __lt__(self, other):
        """
        Less than operator for sorting assemblies by name.

        This method is implemented for SortedList to work properly when sorting
        ModelNodes by name. It compares the names of two ModelNodes and returns
        True if the name of 'self' is less than the name of 'other'.

        Parameters
        ----------
        other : ModelNode
            Another ModelNode object to compare against.

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

    def __getitem__(self, index):
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
        if isinstance(index, int):
            return self._children[index]
        else:
            raise TypeError("The index must be an integer.")

    def remove_all_elements_from_the_current_node(self):
        """
        Remove all elements from the current node.

        Example Usage:
            # Remove all elements from the current node
            node.remove_all_elements_from_the_current_node()
        """
        for e in self._elements:
            del self.tree._model._elements[e.guid]  # type: ignore
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
            new_tree (ModelTree): The new ModelTree object to set as the base tree.

        Example Usage:
            # Change the base tree of the current node
            node.change_base_tree(new_tree)
        """
        self._tree = new_tree
        for child in self._children:
            child.change_base_tree(new_tree)

    def add_elements_to_the_model_dictionary(self, modelnode):
        """
        Add elements from the current node to the base dictionary of Model class.

        Example Usage:
            # Add elements from the current node to the base dictionary of Model class
            node.add_elements_to_the_model_dictionary()
        """
        for e in modelnode._elements:
            self.tree._model._elements[e.guid] = e  # type: ignore

        for childnode in modelnode._children:
            childnode.add_elements_to_the_model_dictionary(childnode)

    def __setitem__(self, index, modelnode):
        """
        Set the child element at the specified index to the given ModelNode.

        This method allows you to replace a child element at the specified index with the provided ModelNode.

        Parameters:
            index (int): The index of the child element to set.
            modelnode (ModelNode): The ModelNode object to set at the specified index.

        Raises:
            TypeError: If modelnode is not a ModelNode object.
            TypeError: If the index is not an integer.

        Example Usage:
            # Set the child element at index 0 to a new ModelNode
            parent_element[0] = new_model_node
        """

        # --------------------------------------------------------------------------
        # sanity checks
        # --------------------------------------------------------------------------
        if not isinstance(modelnode, ModelNode):
            raise TypeError("The node is not a ModelNode object.")

        if not isinstance(index, int):
            raise TypeError("The index must be an integer")

        print("ModelNode setter is called")
        # --------------------------------------------------------------------------
        # Step 1 - remove elements from the old node and the Model _elements dictionary
        # --------------------------------------------------------------------------
        print(self.name)
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
        self._children[index] = modelnode
        self._children[index]._parent = temp_parent
        self._children[index]._tree = temp_tree

        # --------------------------------------------------------------------------
        # assign all the future childs of childs tree to the current branch tree
        # --------------------------------------------------------------------------
        self.change_base_tree(self.tree)

        # --------------------------------------------------------------------------
        # add elements to the model dictionary
        # --------------------------------------------------------------------------
        self.add_elements_to_the_model_dictionary(modelnode)

    def __call__(self, index, value=None):
        """
        Get or set an element within the ModelTree by index.

        This method allows you to retrieve an element from the ModelTree by its index. You can also set an element at
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

        This method allows you to retrieve an element from the ModelTree by its index.

        Parameters:
            index (int): The index of the element to retrieve.

        Returns:
            Element: The element at the specified index.
        """
        return self._elements[index]

    def set_element(self, index, other_element):
        """
        Set the element of the current node to the given element.

        Parameters:
            other_element: The element to set for the current node.

        Example Usage:
            # Set the element of the current node to the given element
            node.set_element(other_element)
        """

        print("set_element_method")

        # --------------------------------------------------------------------------
        # first delete the old element from the Model _elements dictionary
        # --------------------------------------------------------------------------
        del self.tree._model.elements[self._elements[index].guid]  # type: ignore

        # --------------------------------------------------------------------------
        # then add the new element to the Model _elements dictionary
        # --------------------------------------------------------------------------
        self.tree._model.elements[other_element.guid] = other_element  # type: ignore

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
            if e.guid in temp_guid_dict:
                all_elements_are_unique = False
                break
            else:
                temp_guid_dict[e.guid] = e

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
                self.tree._model._elements[element.guid] = element

                # add the node to the graph
                self.tree._model._interactions.add_node(element.guid)

    # ==========================================================================
    # interactions properties and methods - self._interactions = Graph()
    # ==========================================================================

    def add(self, node):
        """
        Add a child node to this node. This function is overridden to use SortedList instead of set().

        Parameters:
            node (ModelNode): The child node to add to this node.

        Raises:
            TypeError: If the node is not a ModelNode object.

        Example Usage:
            # Add a child node to this node
            parent_node.add(child_node)
        """
        if not isinstance(node, ModelNode):
            raise TypeError("The node is not a TreeNode object.")
        if node not in self._children:
            self._children.append(node)

            # add elements from the current node to the base dictionary of Model class
            root = self.tree
            for e in node._elements:
                root._model.elements[e.guid] = e  # type: ignore

            node._parent = self

    # ==========================================================================
    # print
    # ==========================================================================

    def __repr__(self):
        """
        Return a string representation of the ModelNode.

        Returns:
            str: A string representation of the ModelNode, including its name and the number of elements.

        Example Usage:
            # Get a string representation of the ModelNode
            node_repr = repr(model_node)
        """
        return "ModelNode {}, elements {}".format(self.name, len(self._elements))

    def __str__(self):
        return self.__repr__()


class ModelTree(Tree):
    """
    A class representing a tree structure for a model.

    The ModelTree class extends the Tree class and is used to create a hierarchical tree structure for a model,
    which can contain ModelNode elements.

    Parameters:
        model (Model): The model to associate with the tree.
        name (str): The name of the tree. Default is "root".
        elements (list): A list of Element objects to initialize the model with. Default is None.
        attributes (dict): Additional attributes for the tree. Default is None.

    Attributes:
        _root (ModelNode): The root ModelNode of the tree.
        _model (Model): A variable that points to the model class.

    Methods:
        - __init__(self, model, name="root", elements=None, attributes=None): Initializes a new ModelTree instance.

    Example Usage:
        # Create a model tree associated with a model
        model_tree = ModelTree(model_instance, name="custom_tree")
    """

    def __init__(self, model, name="root", elements=None, attributes=None):
        """
        Initialize a new ModelTree instance.

        Parameters:
            model (Model): The model to associate with the tree.
            name (str): The name of the tree. Default is "root".
            elements (list): A list of Element objects to initialize the model with. Default is None.
            attributes (dict): Additional attributes for the tree. Default is None.
        """
        super(ModelTree, self).__init__(name=name, attributes=attributes)

        # --------------------------------------------------------------------------
        # initialize the main properties of the model
        # --------------------------------------------------------------------------
        self._root = None  # the root ModelNode of the tree
        self._model = model  # variable that points to the model class

        # --------------------------------------------------------------------------
        # process the user input
        # --------------------------------------------------------------------------
        self.add(ModelNode(name=name))  # the name can be empty
        self._model.add_elements(elements)  # elements is a list of Element objects

    # ==========================================================================
    # hierarchy methods: add ModelNode, add_by_poath
    # ==========================================================================

    def add(
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

                for e in node.elements:  # type: ignore
                    self.root.elements[e.guid] = e  # type: ignore

                return node
                raise ValueError("The tree already has a root node, remove it first.")

            self._root = node
            node._tree = self  # type: ignore

        else:
            # add the node as a child of the parent node
            if not isinstance(parent, TreeNode):
                raise TypeError("The parent node is not a TreeNode object.")

            if parent.tree is not self:
                raise ValueError("The parent node is not part of this tree.")

            parent.add(node)
            return node

    def add_by_path(self, element, path_names=[], duplicate=False):
        """
        Add an element to the tree using a specified path.

        Parameters:
            element (Element): The element to add to the tree.
            path_names (list): A list of path names specifying the location where the element should be added.
            duplicate (bool): Whether to allow duplicate elements in the tree. Default is False.

        Example Usage:
            # Add an element to the tree using a path
            tree.add_by_paths(element, path_names=["path_name"])
        """

        # add element to the dictionary
        self._model.elements[element.guid] = element
        branch = self.root

        node = None
        for path_name in path_names:

            # check if there are branches with the same name

            found = False
            for b in branch._children:  # type: ignore
                if b.name == str(path_name):
                    node = b
                    found = True
                    break

            if found is False:
                node = ModelNode(name=str(path_name), elements=[])
                branch.add(node)  # type: ignore

            branch = node
        print("added element to node: ", node.name, " ", len(node.elements))  # type: ignore
        node._elements.append(element)  # type: ignore
        node.tree.elements[element.guid] = element  # type: ignore

    # ==========================================================================
    # print statements
    # ==========================================================================

    def __repr__(self):
        """
        Return a string representation of the ModelTree.

        Returns:
            str: A string representation of the ModelTree, including the number of nodes.

        Example Usage:
            # Get a string representation of the ModelTree
            tree_repr = repr(model_tree)
        """
        return "ModelTree with {} nodes".format(len(list(self.nodes)))

    def __str__(self):
        """
        Return a string representation of the ModelTree.

        Returns:
            str: A string representation of the ModelTree.

        Example Usage:
            # Get a string representation of the ModelTree
            tree_str = str(model_tree)
        """
        return self.__repr__()

    def print(self):
        """
        Print the spatial hierarchy of the tree.

        Example Usage:
            # Print the spatial hierarchy of the ModelTree
            model_tree.print()
        """

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
            self._interactions.add_edge(element0.guid, element1.guid)  # type: ignore

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

    def __getitem__(self, index):
        """
        Get the child ModelNode at the specified index.

        Parameters:
            index (int): The index of the child ModelNode to retrieve.

        Returns:
            The child ModelNode at the specified index.

        Raises:
            TypeError: If the index is not an integer.

        Example Usage:
            # Get the child ModelNode at index 0
            child_node = model_tree[0]
        """
        # --------------------------------------------------------------------------
        # sanity checks
        # --------------------------------------------------------------------------
        if not isinstance(index, int):
            raise TypeError("The index is not an integer.")

        # --------------------------------------------------------------------------
        # return the node
        # --------------------------------------------------------------------------
        print("ModelTree getter is called")
        return self._root._children[index]  # type: ignore

    def __setitem__(self, index, model_node):
        """
        Set the child ModelNode at the specified index to the given ModelNode.

        Parameters:
            index (int): The index of the child ModelNode to set.
            model_node (ModelNode): The ModelNode object to set at the specified index.

        Raises:
            TypeError: If model_node is not a ModelNode object.

        Example Usage:
            # Set the child ModelNode at index 0 to a new ModelNode
            model_tree[0] = new_model_node
        """
        # --------------------------------------------------------------------------
        # sanity checks
        # --------------------------------------------------------------------------
        if not isinstance(model_node, ModelNode):
            raise TypeError("The node is not a ModelNode object.")

        if not isinstance(index, int):
            raise TypeError("The index must be an integer")
        print("ModelTree setter is called")
        # --------------------------------------------------------------------------
        # Step 1 - remove elements from the old node and the Model _elements dictionary
        # --------------------------------------------------------------------------
        self._root[index] = model_node  # type: ignore

    def __call__(self, index, value=None):
        """
        Get or set an element within the ModelTree by index.

        This method allows you to retrieve an element from the ModelTree by its index. You can also set an element at
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


class Model:
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
        _hierarchy (ModelTree): A hierarchical representation of the relationships between elements in a tree.
        _interactions (Graph): An abstract representation of linkages or connections between elements and nodes.

    Methods:
        - __init__(self, name="my_model", elements=[], copy_elements=False): Initializes a new Model instance.
        - add_elements(self, elements, copy_elements=False): Adds a list of Element objects to the model.

    Example Usage:
        # Create a model instance with a custom name and elements
        my_model = Model(name="custom_model", elements=[element1, element2])
    """

    def __init__(self, name="my_model", elements=[], copy_elements=False):
        """
        Initialize a new Model instance.

        Parameters:
            name (str, optional): The name of the model. Default is "my_model".
            elements (list, optional): A list of Element objects to initialize the model with. Default is an empty list.
            copy_elements (bool, optional): If True, elements are copied during initialization; if False, elements are
                added by reference. Default is False.
        """
        # --------------------------------------------------------------------------
        # initialize the main properties of the model
        # --------------------------------------------------------------------------
        self._elements = OrderedDict()  # a flat collection of elements - dict{GUID, Element}
        self._hierarchy = ModelTree(self, name)  # hierarchical relationships between elements
        self._interactions = Graph(name=name)  # abstract linkage or connection between elements and nodes

        # --------------------------------------------------------------------------
        # process the user input
        # --------------------------------------------------------------------------
        self.add_elements(elements, copy_elements)  # elements is a list of Element objects

    # ==========================================================================
    # Key property getters
    # ==========================================================================

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
        Retrieve the ModelTree from the model.

        Returns
        -------
        ModelTree
            The hierarchical structure of the model, represented as a ModelTree.
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
                if e.guid in temp_guid_dict:
                    all_elements_are_unique = False
                    break
                else:
                    temp_guid_dict[e.guid] = e

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
        for element in user_elements:
            if not all_elements_are_unique:
                element_copy = element.copy()
                self.add_element(element_copy)
            else:
                self.add_element(element)

    def add_element(self, element):
        """
        Adds an element to the model.

        This method allows you to add a single element to the model, and the element is stored
        in the model's elements dictionary.

        Also, this method is mainly used by the ModelTree and ModelNode classes to add elements to the Model class.

        Parameters
        ----------
        element : Element
            The element to be added to the model.

        Example
        -------
        model = Model()
        new_element = Element(...)  # Replace with actual Element instantiation.
        model.add_element(new_element)
        model_elements = model.elements  # Access the elements property to get the added element.

        """

        if element is not None:
            self.elements[element.guid] = element
            self._interactions.add_node(element.guid)

    # ==========================================================================
    # interactions properties and methods - self._interactions = Graph()
    # ==========================================================================

    def add_interaction(self, element0, element1):
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
            return self._interactions.add_edge(element0.guid, element1.guid)

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

    # ==========================================================================
    # operators
    # ==========================================================================

    def __getitem__(self, index):
        """
        Get a child node from the ModelTree by index.

        This method allows you to retrieve a child node from the ModelTree based on its
        index in the list of children.

        Parameters
        ----------
        index : int
            The index of the child node to be retrieved.

        Returns
        -------
        ModelNode
            The child node at the specified index.

        Raises
        ------
        TypeError
            If the index is not an integer.

        """

        # --------------------------------------------------------------------------
        # sanity checks
        # --------------------------------------------------------------------------
        if not isinstance(index, int):
            raise TypeError("The index is not integer.")

        # --------------------------------------------------------------------------
        # return the root node
        # --------------------------------------------------------------------------
        return self._hierarchy._root._children[index]  # type: ignore

    def __setitem__(self, index, model_node):
        """
        Set a child node in the ModelTree by index.

        This method allows you to set a child node in the ModelTree at the specified index.

        Parameters
        ----------
        index : int
            The index at which to set the child node.

        model_node : ModelNode
            The ModelNode to be set as a child at the specified index.

        Raises
        ------
        TypeError
            If the provided node is not a ModelNode object.

        """

        # --------------------------------------------------------------------------
        # sanity checks
        # --------------------------------------------------------------------------
        if not isinstance(model_node, ModelNode):
            raise TypeError("The node is not a ModelNode object.")

        # --------------------------------------------------------------------------
        # change the node of the tree and update the node's tree and parent
        # --------------------------------------------------------------------------
        self._hierarchy._root._children[index] = model_node  # type: ignore
        self._hierarchy._root._children[index]._tree = self  # type: ignore
        self._hierarchy._root._children[index]._parent = self  # type: ignore
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
            + " with {} elements, {} children, {} interactions".format(
                self.number_of_elements, self.number_of_childs_in_hierarchy, self.number_of_edges
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
        name = self._hierarchy.name
        return (
            "Model "
            + "<"
            + name
            + ">"
            + " with {} elements, {} children, {} interactions".format(
                self.number_of_elements, self.number_of_childs_in_hierarchy, self.number_of_edges
            )
        )

    def print(self):
        """
        Print the spatial hierarchy of the tree for debugging and visualization.

        This method prints information about the tree's spatial hierarchy, including nodes, elements,
        parent-child relationships, and other relevant details.

        """

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

        _print(self._hierarchy.root)

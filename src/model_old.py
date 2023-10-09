from tree import TreeNode, Tree
from compas_assembly2.sortedlist import SortedList
from collections import OrderedDict
from compas.datastructures import Graph
from compas.geometry import bounding_box, Point, Line, Frame, Transformation, Rotation, Translation  # noqa: F401
from compas_assembly2 import Element
import copy


class Model(Tree):
    def __init__(self, name="my_model", attributes=None):
        super(Model, self).__init__(name=name, attributes=attributes)
        self._elements = OrderedDict()  # a flat collection of elements - dict{GUID, Element}
        self._nodes = SortedList()  # hierarchical relationships between elements
        self._interactions = Graph()  # abstract linkage or connection between elements
        self.add_root(ModelNode(name=name))

    def add_root(self, node):
        """Add a root node to the tree."""
        if not isinstance(node, ModelNode):
            raise TypeError("The node is not a ModelNode object.")
        if not node.is_root:
            raise ValueError("The node is already part of another tree.")
        self._root = node
        node._tree = self
        node._parent = self
        self._nodes.add(node)

    # ==========================================================================
    # DICTIONARY METHODS
    # ==========================================================================
    def add_element(self, element):
        self._elements[element.guid] = element

    def get_element(self, index):
        return self.__call__(index)

    def __call__(self, index):
        try:
            if isinstance(index, int):
                return list(self._elements.values())[index]
            else:
                return self._elements[index]
        except KeyError:
            raise IndexError("Index out of range or key not found")

    # ==========================================================================
    # HIERARCHY METHODS
    # ==========================================================================
    def add(self, name="sub_model_such_as_structure", list_of_elements=[]):
        """Add a node to the tree."""
        node = ModelNode(name=name, elements=list_of_elements)
        if not isinstance(node, TreeNode):
            raise TypeError("The node is not a TreeNode object.")
        if self.root is None:
            raise ValueError("The tree has no root node, use add_root() first.")
        else:
            self._nodes[0].add(name, list_of_elements)

        # add elements to the model
        for e in list_of_elements:
            self.add_element(e)

    def __add__(self, other):
        self.add(other.name, other._elements)

    def __iadd__(self, other):
        self.add(other.name, other._elements)

    def add_mode_node(self, model_node):
        self._nodes.add(model_node)
        # add elements to the model
        elements = model_node.get_elements_in_all_branches()
        for e in elements:
            self.add_element(e)

    def __getitem__(self, arg):
        """get element by index"""
        if isinstance(arg, str):
            id = -1
            for local_id, my_TreeNode in enumerate(self._nodes):
                if my_TreeNode.name == arg:
                    id = local_id
                    break
            if id == -1:
                print("WARNING GETTER the element is not found")
                return
            else:
                return self._nodes[id]
        elif isinstance(arg, int):
            return self._nodes[arg]

    def __setitem__(self, arg, user_object):
        """replace current TreeNode or its name with the user given one

        Returns:
            None

        Examples:
            >>> my_TreeNode = TreeNode("model") # for sure you need to place elements inside
            >>> my_TreeNode.add_tree_node(TreeNode("child"))
            >>> my_TreeNode.add_tree_node(Element(name="beam", simplex=Point(0, 0, 0)))
            >>> other_TreeNode = TreeNode("model") # for sure you need to place elements inside
            >>> other_element = Element(name="plate", simplex=Point(0, 0, 0))
            >>> my_TreeNode[0] = other_TreeNode
            >>> # or
            >>> my_TreeNode[0] = other_element
        """
        input_name = arg

        # --------------------------------------------------------------------------
        # user gives integer as an input
        # --------------------------------------------------------------------------
        if isinstance(arg, int):
            if isinstance(user_object, ModelNode):
                user_object.parent = self._hierarchy._children[arg].parent  # type: ignore
                self._hierarchy._children.add(user_object)
        # --------------------------------------------------------------------------
        # user gives string as an input
        # --------------------------------------------------------------------------
        else:
            # find index of the element
            id = -1
            for local_id, my_TreeNode in enumerate(self._hierarchy._children):
                if my_TreeNode.name == input_name:
                    id = local_id
                    break
            # if the element is not found
            if id == -1:
                print("WARNING SETTER the element is not found")
                return
            else:
                if isinstance(user_object, TreeNode):
                    self._hierarchy._children[input_name] = user_object

    # ==========================================================================
    # INTERACTIONS METHODS
    # ==========================================================================
    def add_interactions(self, element0, element1):
        pass

    def create_graph(self):
        self.interactions = Graph()
        for idx, i in enumerate(self._elements.values()):
            self.interactions.add_node(key=idx, attr_dict=None, path=i)

    # ==========================================================================
    # MODEL COLLECTION METHODS
    # ==========================================================================

    def merge_models(self, model):
        pass

    def copy(self):
        """copy model

        # Returns:
        #     TreeNode

        # Examples:
        #     >>> my_TreeNode = TreeNode("model") # for sure you need to place elements inside
        #     >>> my_copy = my_TreeNode.copy()

        """
        # Create a new instance with the same name
        new_instance = Model(name=self._nodes.name)
        new_instance._elements = copy.deepcopy(self._elements)
        new_instance._nodes = self._nodes.copy()
        new_instance._interactions = copy.deepcopy(self._interactions)

        return new_instance

    def transform(self):
        pass

    # def __repr__(self):
    #     self.__repr__
    #     root_nodes = ""
    #     # for my_node in self._nodes:
    #     #     root_nodes += my_node.stringify_tree_node()

    #     return (
    #         "\n==================================================================================================="
    #         + "\nelements: "
    #         + str(len(self._elements))
    #         + "\n==================================================================================================="
    #         + "\n"
    #         + "Current: "
    #         + self.__class__.__name__
    #         + " "
    #         + self.name
    #         + "["
    #         + str(len(self._nodes))
    #         + "]"
    #         + " | Root: "
    #         + str(self._root)
    #         + root_nodes
    #         + "\n==================================================================================================="
    #         + "\ninteractions:\n"
    #         + str(self._interactions)
    #         + "\n==================================================================================================="
    #     )

    def __str__(self):
        return self.__repr__()


class ModelNode(TreeNode):
    def __init__(self, name="mode_node_name", elements=[]):
        super(ModelNode, self).__init__(name=name)
        self._children = SortedList()  # a sorted list of TreeNode objects instead of set()
        self._elements = elements  # attributes of the node

    @property
    def level(self):
        """Returns the level of the current branch

        Returns:
            int

        Examples:
            >>> my_TreeNode = TreeNode("my_TreeNode")
            >>> level = my_TreeNode.level

        """
        level = 0
        p = self._parent
        while p:
            level = level + 1
            if hasattr(p, "_parent") is False:
                break
            p = p.parent
        return level

    # ==========================================================================
    # SORTED LIST METHODS
    # ==========================================================================

    def __lt__(self, other):
        """Less than operator for sorting assemblies by name.
        It is implemented for SortedList to work properly.

        Returns:
            bool

        Examples:
            >>> my_TreeNode = TreeNode("my_TreeNode")
            >>> other_TreeNode = TreeNode("other_TreeNode")
            >>> is_group_smaller = my_TreeNode < other_TreeNode

        """
        if isinstance(self.name, str) and isinstance(other.name, str):
            # try:
            #     integer0 = int(self.name)
            #     integer1 = int(other.name)
            #     return integer0 < integer1
            # except nameError:
            return self.name < other.name
        elif isinstance(self.name, int) and isinstance(other.name, int):
            # returns false to add element to the end of the list
            return self.name < other.name
        else:
            return False

    # ==========================================================================
    # ADD
    # ==========================================================================
    def add(self, name=None, elements=[], parent=None, tree=None):
        """Add a child node to this node."""
        node = ModelNode(name=name, elements=elements)

        # original implementaion:
        if not isinstance(node, TreeNode):
            raise TypeError("The node is not a TreeNode object.")
        self._children.add(node)

        node._parent = self
        node._tree = self.tree
        # if self._tree:
        #     self.tree.nodes.add(node)

    def get_elements_in_all_branches(self):
        """returns all elements in all branches

        Returns:
            list

        Examples:
            >>> my_TreeNode = TreeNode("my_TreeNode")
            >>> all_elements = my_TreeNode.get_elements_in_all_branches()

        """
        elements = []
        for child in self._children:
            elements += child.get_elements_in_all_branches()
        elements += self._elements
        return elements

    # ==========================================================================
    # OPERATORS [], +, +=
    # ==========================================================================

    def __getitem__(self, arg):
        """get element by index"""
        if isinstance(arg, str):
            id = -1
            for local_id, my_TreeNode in enumerate(self._children):
                if my_TreeNode.name == arg:
                    id = local_id
                    break
            if id == -1:
                print("WARNING GETTER the element is not found")
                return
            else:
                return self._children[id]
        elif isinstance(arg, int):
            return self._children[arg]

    def __setitem__(self, arg, user_object):
        """replace current TreeNode or its name with the user given one

        Returns:
            None

        Examples:
            >>> my_TreeNode = TreeNode("model") # for sure you need to place elements inside
            >>> my_TreeNode.add_tree_node(TreeNode("child"))
            >>> my_TreeNode.add_tree_node(Element(name="beam", simplex=Point(0, 0, 0)))
            >>> other_TreeNode = TreeNode("model") # for sure you need to place elements inside
            >>> other_element = Element(name="plate", simplex=Point(0, 0, 0))
            >>> my_TreeNode[0] = other_TreeNode
            >>> # or
            >>> my_TreeNode[0] = other_element
        """
        input_name = arg

        # --------------------------------------------------------------------------
        # user gives integer as an input
        # --------------------------------------------------------------------------
        if isinstance(arg, int):
            if isinstance(user_object, ModelNode):
                user_object.parent = self._hierarchy._children[arg].parent  # type: ignore
                self._children.add(user_object)
        # --------------------------------------------------------------------------
        # user gives string as an input
        # --------------------------------------------------------------------------
        else:
            # find index of the element
            id = -1
            for local_id, my_TreeNode in enumerate(self._children):
                if my_TreeNode.name == input_name:
                    id = local_id
                    break
            # if the element is not found
            if id == -1:
                print("WARNING SETTER the element is not found")
                return
            else:
                if isinstance(user_object, TreeNode):
                    self._children[input_name] = user_object

    def get_element(self, index):
        return self._elements[index]

    def set_element(self, index, value):
        self._elements[index] = value
        self._tree._elements[value.guid] = value

    def __call__(self, index, value=None):
        try:
            return self._elements[index]
        except KeyError:
            raise IndexError("Index out of range or key not found")

    # ==========================================================================
    # COPY
    # ==========================================================================
    def _recursive_copy(self):
        # Create a new instance with the same name
        new_instance = copy.deepcopy(TreeNode(self.name))

        # Recursively copy child and its descendants
        for child in self._children:
            child_copy = child._recursive_copy()
            new_instance.add(child_copy)

        return new_instance

    def copy(self):
        """copy TreeNode and its childs

        Returns:
            TreeNode

        Examples:
            >>> my_TreeNode = TreeNode("model") # for sure you need to place elements inside
            >>> my_copy = my_TreeNode.copy()

        """
        # Create a new instance with the same name
        new_instance = self._recursive_copy()

        # # Once the structure is copied run the initialization again
        # if self.parent is None:
        #     new_instance.init_root()  # collects all the elements
        #     new_instance.graph = copy.deepcopy(self.graph)  # transfer the connectivity

        return new_instance

    # ==========================================================================
    #  PRINT
    # ==========================================================================
    def _stringify_tree_node(self, tree_node_str):
        """private method used by stringify_tree_node"""
        prefix = "   " * (self.level + 0)
        prefix = prefix + "|__ Current: " + self.__class__.__name__ + " "  # if self._parent  else ""
        element_count = "" if len(self._elements) == 0 else "(" + str(len(self._elements)) + ")"
        tree_node_str = (
            "---------------------------------------------------------------------------------------------------\n"
            + prefix
            + str(self.name)
            + "["
            + str(len(self._children))
            + "]"
            + element_count
            + " | Parent: "
            + self._parent.__class__.__name__
            + " "
            + self._parent.name
            + " | Tree: "
            + self._tree.__class__.__name__
            + " "
            + self._tree.name
        )
        tree_node_str += "\n"

        if self._children:
            for child in self._children:
                child_stringified = child._stringify_tree_node(tree_node_str)
                if child_stringified:
                    tree_node_str += child_stringified
                # print also elements, each element is printed in a new line
        for element in self._elements:
            tree_node_str += "   " * (self.level + 1) + "    Element: " + str(element) + "\n"
        return tree_node_str

    def stringify_tree_node(self):
        """returns the printed TreeNode structure

        Returns:
            str: A string representation of the TreeNode.

        Examples:
            >>> my_TreeNode = TreeNode("my_TreeNode")
            >>> my_string = my_TreeNode.stringify_tree_node()

        """
        tree_node_str = "\n"
        tree_node_str += self._stringify_tree_node(tree_node_str)
        return tree_node_str

    def __repr__(self):
        return self.stringify_tree_node()

    def __str__(self):
        return self.__repr__()


if __name__ == "__main__":

    # ==========================================================================
    # Model constructor
    # ==========================================================================
    model = Model("model")

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
    # Add elements to the model | Get elements from the model
    # ==========================================================================
    model.add_element(e0)
    model.add_element(e1)
    model.add_element(e2)
    model.add_element(e3)
    model.add_element(e4)
    model.add_element(e5)
    model.add_element(e6)
    # print(model.get_element(1))
    # print(model(1))

    # ==========================================================================
    # Add hierarchy to the model
    # ==========================================================================

    model.add("structures")
    # print(model[0].name, model[0][0]._parent)  # root
    # print(model[0][0].name)  # structures
    # model[0][0].add("timber", [e0, e1, e2, e3])
    # print(model[0][0][0].name, model[0][0][0]._parent)  # structures

    # model[0].add("concrete", [e4, e5, e6])
    # element_from_assembly = model[0][0].get_element(0)
    # model[0][0].set_element(0, e1)

    # ==========================================================================
    # Print model
    # ==========================================================================
    print(model)
    # print(model[0][0].get(0))
    # print(model[0][0](0))

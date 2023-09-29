"""
Element
Petras Vestartas
2021-10-01

# ==========================================================================
# Description
# ==========================================================================
The Assembly is a nested structure of assemblies and elements.

# ==========================================================================
# The minimal example
# ==========================================================================

NEVER DO THIS:
class Assembly:
    def __init__(self, assembly):
        self.assemblies = []  # list<Assembly>

DO THIS INSTEAD BECAUSE ASSEMBLY MUST BE FINITE NOT RECURSIVE + IT CAN STORE PATH:
class Assembly:
    def __init__(self, value):
        self.value = value  # can be a string or class<Element>
        self.parent_assembly = None
        self.sub_assemblies = SortedList() # meaning the class<Assembly> must have __lt__ method


# ==========================================================================
# What types are stored?
# ==========================================================================
The main property is called "value", it can be either:
a) group -> a string (indexing for the hierarch using text)
b) assembly -> class<assembly> (beams, plates, nodes, etc.)

# ==========================================================================
# How can the group hierarchy reperesented in one single class?
# ==========================================================================
It is represented by three propertes:
a) value -> group or class<element>
b) parent_assembly -> None or group
c) sub_assemblies -> list<Assembly or Element or mix of both>

# ==========================================================================
# How new assemblies or groups are add_assemblyed?
# ==========================================================================
When a sub_assembly assembly is add_assemblyed the parent_assembly is set to the value assembly.
def add_assembly_assembly(self, sub_assembly):
    sub_assembly.parent_assembly = self
    self.sub_assemblies.add(sub_assembly)

# ==========================================================================
# What the assembly is copied?
# ==========================================================================
One tree can have multiple references of the same object can exist in one assembly,
only one object exists in a memory, this is handled by UUID

# ==========================================================================
# What about links between elements?
# ==========================================================================

a) root assembly has links between elements (a graph), which can be empty
b) the root assembly stores all elements

+---+---+---+---+---+---+--MORE-DETAILS-BELOW--+---+---+---+---+---+---+---+

# ==========================================================================
# How assemblies are transformed?
# ==========================================================================
Transformation is performed on a value branch and its sub_assemblies using methods:
a) transform, transformed
b) orient, oriented (for the most common operation)

# ==========================================================================
# How to vizualize a tree?
# ==========================================================================
def print_tree(self):
    prefix = "   " * self.level
    prefix = prefix + "|__ " if self.parent_assembly else ""
    print(prefix + self.path_str)
    if self.sub_assemblies:
        for sub_assembly in self.sub_assemblies:
            sub_assembly.print_tree()

# ==========================================================================
# How to know the level an object is nested at?
# ==========================================================================
@property
def level(self):
    level = 0
    p = self.parent_assembly
    while p:
        level = level + 1
        p = p.parent_assembly
    return level

# ==========================================================================
# How to know the depth an object is nested at?
# ==========================================================================
@property
def depth(self):
    # Initialize depth to 0 and start from the value node
    depth = 0
    current_node = self

    # Backtrack to the root parent_assembly while incrementing depth
    while current_node.parent_assembly:
        depth = depth + 1
        current_node = current_node.parent_assembly

    # Calculate the maximum depth by traversing sub_assemblies's subtrees
    return self._calculate_depth(self, depth)


"""

# todo:
# [x] - 1. serialization methods
# [x] - 2. flatten the tree, to nested lists, collapse leaves by certain amount
# [x] - 3. update example filesy
# [x] - 4. show method
# [x] - 5. write tests for transformation, copy, properties retrieval
# [x] - 6. create assembly from json file
# [ ] - 7. add a frame to the root assembly for transformation
# [ ] - 8.1. add adjacency graph in the root and write examples files, vizualize it using networkx
# [ ] - 8.2. visualize the adjacency in the viewer simply, by drawing lines between element bbox centers
# [ ] - 9.1. add collision detection between elements, for this you need to flatten the elements and
# [ ] - 9.2. define collision pairs as lists of indices e.g. v0 "0,5,7", v1 "1,5,8"

import copy
from compas.data import Data
from compas.geometry import bounding_box, Point
from compas_assembly2 import Element
from compas.colors import Color
from compas_assembly2.sortedlist import SortedList
from compas_assembly2.viewer import Viewer
from compas.data import json_load, json_dump


class Assembly(Data):
    """Assembly is a tree data-structure.
    There are several ways how the data-structure can be used:
    a) the recursive structure allows to store group names as tree branches and elements as tree leaves.
    b) elememts can be nested within elements, which allows to store the assembly hierarchy.
    c) the root of assembly is responsible for storing links between elements

    Parameters
    ----------
        value : str - for grouping | Element or other type - for storing data
            each assembly must have a value
        parent_assembly : None or Assembly
            this values is assigned automatically
        sub_assemblies : SortedList
            this values is assigned automatically

    Attributes
    ----------
        make_copy : bool
            if True, the value will be copied, otherwise it will be referenced
        name : str
            the name of the value either
        is_group_or_assembly : bool
            True if the current branch value is a string
        level : int
            the level of the current branch
        root : Assembly or None
            the root of the current branch
        depth : int
            the surface are of an element based on complex geometry
        type : str
            name GROUP if the value is string else ELEMENT
        number_of_elements : int
            the total number of elements in the assembly

    Example 1
    ---------
        >>> # EXAMPLE 1
        >>> my_assembly = Assembly("my_assembly")
        >>> print(my_assembly)
        ======================================= ROOT ASSEMBLY =============================================
        GROUP --> my_assembly
        ===================================================================================================

    Example 2
    ---------
        >>> # EXAMPLE 2
        >>> my_assembly = Assembly("model")
        >>> my_assembly.add_assembly(Element(name="beam", simplex=Point(0, 0, 0)))
        >>> my_assembly.add_assembly(Element(name="beam", simplex=Point(0, 5, 0)))
        >>> my_assembly.add_assembly(Element(name="plate", simplex=Point(0, 0, 0)))
        >>> my_assembly.add_assembly(Element(name="plate", simplex=Point(0, 7, 0)))
        >>> print(my_assembly)
        ======================================= ROOT ASSEMBLY =============================================
        GROUP --> model
            |__ ELEMENT --> TYPE_BEAM ID_-1 GUID_e47fe051-74e1-4ab6-8d0e-a57421c9c5f1
            |__ ELEMENT --> TYPE_BEAM ID_-1 GUID_f2de9226-1b87-4dec-9a7c-c64b9f4805fb
            |__ ELEMENT --> TYPE_PLATE ID_-1 GUID_7c0700f9-ae92-4dfc-88d1-2edee0989da5
            |__ ELEMENT --> TYPE_PLATE ID_-1 GUID_1384368c-2992-4b83-857a-2f9343179e49
        ===================================================================================================

    Example 3
    ---------
        >>> # EXAMPLE 3
        >>> my_assembly = Assembly("model")
        >>> structure = Assembly("structure")
        >>> #
        >>> timber = Assembly("timber")
        >>> structure.add_assembly(timber)
        >>> timber.add_assembly(Assembly(Element(name="beam", simplex=Point(0, 0, 0))))
        >>> timber.add_assembly(Assembly(Element(name="beam", simplex=Point(0, 5, 0))))
        >>> timber.add_assembly(Assembly(Element(name="plate", simplex=Point(0, 0, 0))))
        >>> timber.add_assembly(Assembly(Element(name="plate", simplex=Point(0, 7, 0))))
        >>> #
        >>> concrete = Assembly("concrete")
        >>> structure.add_assembly(concrete)
        >>> concrete.add_assembly(Assembly(Element(name="node", simplex=Point(0, 0, 0))))
        >>> concrete.add_assembly(Assembly(Element(name="block", simplex=Point(0, 5, 0))))
        >>> concrete.add_assembly(Assembly(Element(name="block", simplex=Point(0, 0, 0))))
        >>> #
        >>> my_assembly.add_assembly(structure)
        >>> print(my_assembly)
        ======================================= ROOT ASSEMBLY =============================================
        GROUP --> model
        |__ GROUP --> structure
            |__ GROUP --> concrete
                |__ ELEMENT --> TYPE_NODE ID_-1 GUID_2f1b5777-7ba6-41b1-a6ac-13460ce5637e
                |__ ELEMENT --> TYPE_BLOCK ID_-1 GUID_45b6a07c-566d-4ea0-b705-52d8d2dfb751
                |__ ELEMENT --> TYPE_BLOCK ID_-1 GUID_407920bf-ba2e-4fb0-8155-173bc447fc41
            |__ GROUP --> timber
                |__ ELEMENT --> TYPE_BEAM ID_-1 GUID_d8231f79-b018-4693-9bb9-811219de383f
                |__ ELEMENT --> TYPE_BEAM ID_-1 GUID_a134c723-9dae-4672-97cf-8733ce808a00
                |__ ELEMENT --> TYPE_PLATE ID_-1 GUID_6657b58e-0c41-402e-8841-c756e42f697e
                |__ ELEMENT --> TYPE_PLATE ID_-1 GUID_1f4a7641-394c-449a-b49c-714e98c87e62
        ===================================================================================================
    """

    # ==========================================================================
    # CONSTRUCTOR THAt HAS A RECURSIVE DATA-STRUCTURE, DO NOT CHANGE IT!
    # ==========================================================================
    def __init__(self, value, make_copy=True):
        super(Assembly, self).__init__()

        # --------------------------------------------------------------------------
        # the main data-structure representation, do not change it!
        # --------------------------------------------------------------------------
        self.make_copy = make_copy
        self.value = value if self.make_copy is False or isinstance(value, str) else value.copy()
        self.parent_assembly = None
        self.sub_assemblies = SortedList()

        # --------------------------------------------------------------------------
        # attributes
        # --------------------------------------------------------------------------
        self.init_root()

    @staticmethod
    def example():
        """example of the assembly tree structure

        Returns:
            Assembly

        Examples:
            >>> my_assembly = Assembly.example()

        """

        root = Assembly("model")
        structure = Assembly("structure")

        timber = Assembly("timber")
        timber.add_assembly(Assembly(Element(name="beam", simplex=Point(0, 0, 0))))
        timber.add_assembly(Assembly(Element(name="beam", simplex=Point(0, 5, 0))))
        timber.add_assembly(Assembly(Element(name="plate", simplex=Point(0, 0, 0))))
        timber.add_assembly(Assembly(Element(name="plate", simplex=Point(0, 7, 0))))

        concrete = Assembly("concrete")
        structure.add_assembly(concrete)
        concrete.add_assembly(Assembly(Element(name="node", simplex=Point(0, 0, 0))))
        concrete.add_assembly(Assembly(Element(name="block", simplex=Point(0, 5, 0))))
        concrete.add_assembly(Assembly(Element(name="block", simplex=Point(0, 0, 0))))

        structure.add_assembly(timber)
        root.add_assembly(structure)
        return root

    # ==========================================================================
    # ATTRIBUTES
    # ==========================================================================

    @property
    def name(self):
        """Returns the name of the value either
        a) the name of the group
        b) the name of the element

        Returns:
            string

        Examples:
            >>> my_assembly = Assembly("my_assembly")
            >>> as_as_defined_in__repr__ = my_assembly.name
        """
        if isinstance(self.value, str):
            return self.value
        else:
            return str(self.value)

    @property
    def is_group_or_assembly(self):
        """Returns True if the current branch value is a string

        Returns:
            bool

        Examples:
            >>> my_assembly = Assembly("my_assembly")
            >>> is_group = my_assembly.is_group_or_assembly

        """
        return isinstance(self.value, str)

    @property
    def level(self):
        """Returns the level of the current branch

        Returns:
            int

        Examples:
            >>> my_assembly = Assembly("my_assembly")
            >>> level = my_assembly.level

        """
        level = 0
        p = self.parent_assembly
        while p:
            level = level + 1
            p = p.parent_assembly
        return level

    @property
    def root(self):
        """Returns the root of the current branch

        Returns:
            Assembly

        Examples:
            >>> my_assembly = Assembly("my_assembly")
            >>> root_assembly = my_assembly.root

        """

        current_node = self
        while current_node.parent_assembly:
            current_node = current_node.parent_assembly
        return current_node

    @property
    def depth(self):
        """Returns the depth of the current branch

        Returns:
            int

        Examples:
            >>> my_assembly = Assembly("my_assembly")
            >>> depth = my_assembly.depth

        """
        # Initialize depth to 0 and start from the value node
        depth = 0
        current_node = self

        # Backtrack to the root parent_assembly while incrementing depth
        while current_node.parent_assembly:
            depth = depth + 1
            current_node = current_node.parent_assembly

        # Calculate the maximum depth by traversing sub_assemblies's subtrees
        return self._calculate_depth(self, depth)

    def _calculate_depth(self, node, depth):
        if not node.sub_assemblies:
            # If the node has no sub_assemblies, return the value depth
            return depth

        max_child_depth = depth
        for sub_assembly in node.sub_assemblies:
            # Recursively calculate the depth for each sub_assembly's subtree
            child_depth = self._calculate_depth(sub_assembly, depth + 1)
            if child_depth > max_child_depth:
                max_child_depth = child_depth

        # Return the maximum depth among sub_assemblies's subtrees
        return max_child_depth

    @property
    def type(self):
        """Returns name GROUP if the value is string else ELEMENT

        Returns:
            str

        Examples:
            >>> my_assembly = Assembly("my_assembly")
            >>> type_name = my_assembly.type

        """
        if isinstance(self.value, str):
            return "GROUP"
        else:
            return "ELEMENT"

    @property
    def number_of_elements(self):
        """Counts the total number of elements in the assembly

        Returns: The total number of elements in the assembly.
            int

        Examples:
            Create an assembly and count its elements:
            >>> my_assembly = Assembly("my_assembly")
            >>> sub_1 = Assembly("sub_1")
            >>> sub_2 = Assembly("sub_2")
            >>> element = Element(name="beam", simplex=Point(0, 0, 0))
            >>> my_assembly.add_assembly(sub_1)
            >>> my_assembly.add_assembly(sub_2)
            >>> my_assembly.add_element(element)
            >>> count = my_assembly.number_of_elements
            1

        """
        number_of_elements = 0
        for sub_assembly in self.sub_assemblies:
            if isinstance(sub_assembly.value, str):
                number_of_elements += sub_assembly.number_of_elements
            else:
                number_of_elements += 1
                number_of_elements += sub_assembly.number_of_elements
        return number_of_elements

    # ==========================================================================
    # SORTED LIST METHODS
    # ==========================================================================

    def __lt__(self, other):
        """Less than operator for sorting assemblies by name.
        It is implemented for SortedList to work properly.

        Returns:
            bool

        Examples:
            >>> my_assembly = Assembly("my_assembly")
            >>> other_assembly = Assembly("other_assembly")
            >>> is_group_smaller = my_assembly < other_assembly

        """
        if isinstance(self.value, str) and isinstance(other.value, str):
            try:
                integer0 = int(self.value)
                integer1 = int(other.value)
                return integer0 < integer1
            except ValueError:
                return self.value < other.value
        else:
            # returns false to add element to the end of the list
            return False

    # ==========================================================================
    # SERIALIZATION
    # ==========================================================================

    @property
    def data(self):
        # create the data object from the class properties§+
        # call the inherited Data constructor for json serialization
        data = {
            "value": self.value,
            "make_copy": self.make_copy,
        }

        # custom properties - handles circular references
        data["parent_assembly"] = None if self.parent_assembly is None else self.parent_assembly.value
        data["sub_assemblies"] = [sub.data for sub in self.sub_assemblies]

        # return the data object
        return data

    @data.setter
    def data(self, data):
        # vice versa - create the class properties from the data object
        # call the inherited Data constructor for json serialization

        # main properties
        self.value = data["value"]
        self.make_copy = data["make_copy"]

        # custom properties
        self.parent_assembly = data["parent_assembly"]
        self.sub_assemblies = data["sub_assemblies"]

    @classmethod
    def from_data(cls, data):
        """Alternative to None default __init__ parameters."""

        obj = Assembly(value=data["value"], make_copy=data["make_copy"])

        # custom properties
        parent_assembly_data = data.get("parent_assembly")
        if isinstance(parent_assembly_data, dict):
            obj.parent_assembly = Assembly.from_data(parent_assembly_data)
        else:
            obj.parent_assembly = None

        # Handle the sub_assemblies list
        obj.sub_assemblies = []
        for sub_data in data["sub_assemblies"]:
            if isinstance(sub_data, dict):
                sub_obj = Assembly.from_data(sub_data)  # Recursively create sub-assembly
                sub_obj.parent_assembly = obj  # Set the parent assembly
                obj.sub_assemblies.append(sub_obj)
            else:
                # Handle non-Assembly data types (e.g., strings or integers)
                obj.sub_assemblies.append(sub_data)

        # Return the object
        return obj

    def serialize(self, fp, pretty=False):
        """Serialize the assembly to a JSON file.

        Returns:
            None

        Examples:
            >>> my_assembly = Assembly("my_assembly")
            >>> my_assembly.serialize("my_assembly.json", pretty=True)

        """
        json_dump(data=self.data, fp=fp, pretty=pretty)

    @staticmethod
    def deserialize(fp):
        """Deserialize the assembly to a JSON file.

        Returns:
            Assembly

        Examples:
            >>> my_assembly = Assembly("my_assembly")
            >>> my_assembly = Assembly.deserialize("my_assembly.json")

        """
        data = json_load(fp=fp)
        return Assembly.from_data(data)

    # ==========================================================================
    # PRINT METHODS
    # ==========================================================================

    def __repr__(self):
        """print the tree structure of the Assembly

        Returns:
            str: A string representation of the Assembly.

        Examples:
            >>> my_assembly = Assembly("my_assembly")
            >>> print(my_assembly)

        """
        return self.stringify_tree()

    def _stringify_tree(self, tree_str):
        """private method used by stringify_tree"""
        prefix = "   " * self.level
        prefix = prefix + "|__ " if self.parent_assembly else ""
        tree_str = prefix + self.type + " --> " + self.name + "\n"
        if self.sub_assemblies:
            for sub_assembly in self.sub_assemblies:
                subtree = sub_assembly._stringify_tree(tree_str)
                if subtree:
                    tree_str += subtree
        return tree_str

    def stringify_tree(self):
        """returns the printed tree structure

        Returns:
            str: A string representation of the Assembly.

        Examples:
            >>> my_assembly = Assembly("my_assembly")
            >>> my_string = stringify_tree(my_assembly)

        """
        tree_str = (
            "\n======================================= ROOT ASSEMBLY =============================================\n"
        )
        tree_str += self._stringify_tree(tree_str)
        tree_str += (
            "===================================================================================================\n"
        )
        return tree_str

    def _print_tree(self):
        """private method used by print_tree"""
        prefix = "   " * self.level
        prefix = prefix + "|__ " if self.parent_assembly else ""
        print(prefix + self.type + " --> " + self.name)
        if self.sub_assemblies:
            for sub_assembly in self.sub_assemblies:
                sub_assembly._print_tree()

    def print_tree(self):
        """returns the printed tree structure

        Returns:
            None

        Examples:
            >>> my_assembly = Assembly("my_assembly")
            >>> my_assembly.print_tree()

        """
        print("======================================= ROOT ASSEMBLY =============================================")
        self._print_tree()
        print("===================================================================================================")

    # ==========================================================================
    # ROOT BRANCH BEHAVIOR
    # ==========================================================================

    def init_root(self):
        """initialize the root assembly properties"""
        if self.parent_assembly is None:
            self.graph = []

    def remove_root(self):
        """remove the root assembly properties"""
        if self.parent_assembly is not None:
            del self.graph

    def transfer_root(self, new_root):
        """transfer the root assembly properties"""
        # --------------------------------------------------------------------------
        # if it was already the sub_assembly it probably did not have any connectivity
        # --------------------------------------------------------------------------
        if self.parent_assembly is not None:
            return

        # --------------------------------------------------------------------------
        # update links
        # --------------------------------------------------------------------------
        n = len(self.graph)
        for pair in self.graph:
            new_root.graph.append(pair[0] + n, pair[1] + n)

    # ==========================================================================
    # APPEND METHODS
    # add_assembly() | add_assembly_sub_assemblies
    # add_by_index() | add_by_indexs
    # merge_assembly() | merge_assemblies
    # ==========================================================================

    def add_assembly(self, sub_assembly_or_element):
        """adds assembly to the current assembly sub-assemblies list,
        if the user inout element or any other type, it will wrap into the assembly

        Returns:
            None

        Examples:
            >>> my_assembly = Assembly("my_assembly")
            >>> other_assembly = Assembly("other_assembly")
            >>> element = Element(name="beam", simplex=Point(0, 0, 0))
            >>> my_assembly.add_assembly(other_assembly)
            >>> # or
            >>> my_assembly.add_assembly(element)
            >>> # or
            >>> my_assembly.add_assembly(any_geometry_type)

        """
        # check if the input is an element or assembly
        sub_assembly = (
            sub_assembly_or_element
            if isinstance(sub_assembly_or_element, Assembly)
            else Assembly(sub_assembly_or_element)
        )

        # update the parent_assembly and transfer the root properties
        sub_assembly.parent_assembly = self
        sub_assembly.transfer_root(self)

        # add_assembly the sub_assembly to the list
        self.sub_assemblies.add(sub_assembly)

    def merge_assembly(self, a1, allow_duplicate_assembly_branches=False, allow_duplicate_assembly_leaves=True):
        """merge elements within two assemblies
        if the names of the groups are the same then the elements are merged in the same branch
        else they are added based on the a1 group names
        the merging have two boolean flag to allow duplicate branch names and leaves, if elements are references

        Returns:
            None

        Examples:
            >>> my_assembly = Assembly("my_assembly")
            >>> a1 = Assembly("a1")
            >>> my_assembly.merge_assembly(a1)
            >>> # or if you want to have duplicated branches with the same names
            >>> my_assembly.merge_assembly(a1, True, True)

        """

        # Helper function to find a node with the same name in a list of nodes
        def find_node_by_path(nodes, node_a1):
            if allow_duplicate_assembly_branches:  # or a1.is_group_or_assembly or node_a1.is_group_or_assembly
                return None
            else:
                if allow_duplicate_assembly_leaves:
                    if node_a1.is_group_or_assembly is False:
                        return None

                for node in nodes:
                    if node.name == node_a1.name:
                        return node
                return None

        # Iterate through the nodes in a1
        for node_a1 in a1.sub_assemblies:
            # Check if there is an equivalent node in a0
            existing_node_a0 = find_node_by_path(self.sub_assemblies, node_a1)
            if existing_node_a0 is not None:
                # Recursively merge the sub_assemblies of the two nodes
                existing_node_a0.merge_assembly(
                    node_a1, allow_duplicate_assembly_branches, allow_duplicate_assembly_leaves
                )
            else:
                # If no corresponding node is found, add_assembly the node from a1 to a0
                self.add_assembly(node_a1)

    def add_by_index(
        self, value, name_list=None, allow_duplicate_assembly_branches=False, allow_duplicate_assembly_leaves=True
    ):
        """add element to the assembly by creating group that follows element indices
        otherwise user can give a list of names to add an element to the specific branch

        Returns:
            None

        Examples:
            >>> my_assembly = Assembly("my_assembly")
            >>> element = Element(name="beam", simplex=Point(0, 0, 0))
            >>> my_assembly.add_by_index(element)
            >>> # or
            >>> my_assembly.add_by_index(element, [0,5,9])

        """
        # create value
        name_list = name_list if name_list is not None else value.id

        branch_tree = Assembly("temp_-->_it_will_be_deleted_in_merge_assembly_method")
        last_branch = branch_tree
        for name in name_list:
            assemblyvalue = str(name) if isinstance(name, int) else name
            sub_assembly = Assembly(assemblyvalue)
            last_branch.add_assembly(sub_assembly)
            last_branch = sub_assembly

        # add_assembly "real" value to the last value
        last_branch.add_assembly(Assembly(value))

        # merge this value with the rest
        self.merge_assembly(branch_tree, allow_duplicate_assembly_branches, allow_duplicate_assembly_leaves)

    # ==========================================================================
    # MODIFY THE TREE STRUCTURE e.g. collapse, prune, graft
    # ==========================================================================
    def collapse(self, level):
        """Iterate through sub-assemblies and adjust their levels based on user input.
        0 - outputs one list with all elements
        1 - keep only the first branch level

        n - , where n is the deepest level, will place each element into individual branch

        Returns:
            Assembly

        Examples:
            >>> my_assembly = Assembly("my_assembly")
            >>> collapsed_assembly = my_assembly.collapse(0)

        """

        if level < 0:
            raise ValueError("Level must be a non-negative integer.")

        # Start by copying the current assembly.
        collapsed_assembly = self.copy()

        if level == 0:
            elements = collapsed_assembly.flatten()
            collapsed_assembly.sub_assemblies = SortedList()
            for element in elements:
                collapsed_assembly.add_assembly(Assembly(element, True))

        # Iterate through sub-assemblies.
        queue = []
        queue.extend(collapsed_assembly.sub_assemblies)
        for sub_assembly in queue:
            # If the sub-assembly has sub-assemblies, add_assembly them to the queue.
            if sub_assembly.level >= level:
                # find leave and add_assembly it to the sub_assembly
                elements = sub_assembly.flatten()
                sub_assembly.sub_assemblies = SortedList()
                for element in elements:
                    sub_assembly.add_assembly(Assembly(element, True))
            else:
                queue.extend(sub_assembly.sub_assemblies)

        return collapsed_assembly

    def graft(self, name="0"):
        """iterate through the assemblies if the leaves have multiple elements in a current assembly,
        then split it into individual branches under the given name

        Returns:
            Assembly

        Examples:
            >>> my_assembly = Assembly("my_assembly")
            >>> grafted_assembly = my_assembly.graft()

        """

        # Start by copying the current assembly.
        grafted_assembly = self.copy()

        # Iterate through sub-assemblies.
        queue = []
        queue.extend(grafted_assembly.sub_assemblies)
        for sub_assembly in queue:
            # If the sub-assembly has sub-assemblies, add_assembly them to the queue.
            if isinstance(sub_assembly.value, str) is False:
                temp = Assembly(value=sub_assembly.value)
                sub_assembly.value = name
                sub_assembly.add_assembly(temp)
            else:
                queue.extend(sub_assembly.sub_assemblies)

        return grafted_assembly

    def prune(self, level):
        """Iterate through sub-assemblies and remove all sub-assemblies deeper than the given level.

        Returns:
            Assembly

        Examples:
            >>> my_assembly = Assembly("my_assembly")
            >>> pruned_assembly = my_assembly.prune(2)

        """

        if level < 0:
            raise ValueError("Level must be a non-negative integer.")

        # Start by copying the current assembly.
        collapsed_assembly = self.copy()

        if level == 0:
            collapsed_assembly.sub_assemblies = SortedList()

        # Iterate through sub-assemblies.
        queue = []
        queue.extend(collapsed_assembly.sub_assemblies)
        for sub_assembly in queue:
            # If the sub-assembly has sub-assemblies, add_assembly them to the queue.
            if sub_assembly.level >= level:
                # delete the branches that are deeper than a certain level
                sub_assembly.sub_assemblies = SortedList()
            else:
                queue.extend(sub_assembly.sub_assemblies)

        return collapsed_assembly

    # ==========================================================================
    # CONVERTION TO LISTS
    # ==========================================================================
    def to_nested_list(self):
        """convert the tree to nested lists
        ATTENTION: in majority of practical cases use to_lists() method instead
        it reduces the hierarchy to a list of lists

        Returns:
            list(list(list(...)), list(...))

        Examples:
            >>> my_assembly = Assembly("my_assembly")
            >>> my_lists = my_assembly.to_nested_list()

        """

        def _to_nested_list(assembly):
            # divide into 1) empty assemblies 2) nested ones
            result = []

            for sub_assembly in assembly.sub_assemblies:
                if isinstance(sub_assembly.value, Element):
                    result.append(sub_assembly.value)
                else:
                    result.append(_to_nested_list(sub_assembly))
            if len(result) > 0:
                return result

        return _to_nested_list(self)

    def to_lists(self, collapse_level=None):
        """unwrap the nested nested n times lists in one list of lists

        Returns:
            list(list(element0, element1, ...), list(element0, element1, ...))

        Examples:
            >>> my_assembly = Assembly("my_assembly")
            >>> my_list = my_assembly.to_lists()

        """

        # references
        assembly = self

        # collapse
        if collapse_level is not None:
            if collapse_level >= 0:
                assembly = self.collapse(collapse_level)
            else:
                assembly = self.graft("0")

        # convert the tree to nested list
        tree = assembly.to_nested_list()

        # convert the nested lists to list of lists
        lists = []
        queue = list(tree)  # type: ignore
        while queue:
            item = queue.pop(0)
            individual_elements = []
            if isinstance(item, list):
                for i in item:
                    if isinstance(i, list):
                        queue = [i] + queue
                    else:
                        individual_elements.append(i)
            if len(individual_elements) > 0:
                lists.append(individual_elements)

        if len(lists) == 0:
            return tree
        else:
            return lists

    def _flatten(self, list):
        """private method used by flatten method"""
        if self.sub_assemblies:
            for sub_assembly in self.sub_assemblies:
                if isinstance(sub_assembly.value, str) is False:  # isinstance(sub_assembly.value, Element)
                    list.append(sub_assembly.value)
                if len(sub_assembly.sub_assemblies) > 0:
                    sub_assembly._flatten(list)
        return list

    def flatten(self):
        """get all elemenets of the assembly in one single list

        Returns:
            list( element0, element1, ... )

        Examples:
            >>> my_assembly = Assembly("my_assembly")
            >>> my_list = my_assembly.flatten()

        """
        list = []
        return self._flatten(list)

    # ==========================================================================
    # OPERATORS [], +, +=
    # ==========================================================================
    def __getitem__(self, arg):
        """get the assembly by name or index
        a) my_assembly["name"] or my_assembly[0]
        b) or nested asses my_assembly["name1"]["name2"] or my_assembly[0][0]

        ATTENTION:
        if you want to retrieve an element write my_assembly["name"].value

        Returns:
            Assembly

        Examples:
            >>> my_assembly = Assembly("model") # for sure you need to place elements inside
            >>> my_assembly.add_assembly(Assembly("another_assembly"))
            >>> my_sub_assembly = my_assembly[0]
            >>> # or
            >>> my_sub_assembly = my_assembly[0][1]

        """

        # string input
        if isinstance(arg, str):
            id = -1
            for local_id, my_assembly in enumerate(self.sub_assemblies):
                if my_assembly.name == arg:
                    id = local_id
                    break
            if id == -1:
                print("WARNING GETTER the element is not found")
                return
            else:
                return self.sub_assemblies[id]
        elif isinstance(arg, int):
            return self.sub_assemblies[arg]

            # INCASE YOU WANT TO OUTPUT ELEMENT NOT THE ASSEMBLY
            # # check if value is string
            # if isinstance(self.sub_assemblies[arg].value, str):  # type: ignore
            #     return self.sub_assemblies[arg]
            # else:
            #     return self.sub_assemblies[arg].value  # type: ignore

    def __setitem__(self, arg, user_object):
        """replace current assembly or its value with the user given one

        Returns:
            None

        Examples:
            >>> my_assembly = Assembly("model") # for sure you need to place elements inside
            >>> other_assembly = Assembly("model") # for sure you need to place elements inside
            >>> other_element = Element(name="beam", simplex=Point(0, 0, 0))
            >>> my_assembly[0] = other_assembly
            >>> # or
            >>> my_sub_assembly[0] = other_element
        """
        input_name = arg

        if isinstance(arg, int):
            if isinstance(user_object, Element):
                self.sub_assemblies[arg].value = user_object  # type: ignore
            elif isinstance(user_object, Assembly):
                user_object.parent_assembly = self.sub_assemblies[arg].parent_assembly
                del self.sub_assemblies[arg]
                self.sub_assemblies.add(user_object)

        else:
            # find index of the element
            id = -1
            for local_id, my_assembly in enumerate(self.sub_assemblies):
                if my_assembly.name == input_name:
                    id = local_id
                    break

            # if the element is not found
            if id == -1:
                print("WARNING SETTER the element is not found")
                return
            else:
                if isinstance(user_object, Element):
                    self.sub_assemblies[input_name].value = user_object  # type: ignore
                elif isinstance(user_object, Assembly):
                    self.sub_assemblies[input_name] = user_object

    def __add__(self, other):
        """plus sign to merge two assemblies as a copy

        Returns:
            Assembly

        Examples:
            >>> assembly_0 = Assembly("model") # for sure you need to place elements inside
            >>> assembly_1 = Assembly("model") # for sure you need to place elements inside
            >>> my_sub_assembly = assembly_0 + assembly_1
        """
        copy = self.copy()
        copy.merge_assembly(other)
        return copy

    def __iadd__(self, other):
        """plus equal sign to merge two assemblies as a copy

        Returns:
            Assembly

        Examples:
            >>> my_assembly = Assembly("model") # for sure you need to place elements inside
            >>> other_assembly = Assembly("model") # for sure you need to place elements inside
            >>> my_assembly += other_assembly

        """
        copy = self.copy()
        copy.merge_assembly(other)
        return copy

    # ==========================================================================
    # COPY
    # ==========================================================================
    def _recursive_copy(self):
        # Create a new instance with the same value
        new_instance = Assembly(self.value)

        # Recursively copy sub_assembly and its descendants
        for sub_assembly in self.sub_assemblies:
            child_copy = sub_assembly._recursive_copy()
            new_instance.add_assembly(child_copy)

        return new_instance

    def copy(self):
        """copy assembly and its sub_assemblies

        Returns:
            Assembly

        Examples:
            >>> my_assembly = Assembly("model") # for sure you need to place elements inside
            >>> my_copy = my_assembly.copy()

        """
        # Create a new instance with the same value
        new_instance = self._recursive_copy()

        # Once the structure is copied run the initialization again
        if self.parent_assembly is None:
            new_instance.init_root()  # collects all the elements
            new_instance.graph = copy.deepcopy(self.graph)  # transfer the connectivity

        return new_instance

    # ==========================================================================
    # TRANSFORM TREE ELEMENTS
    # transform_to_frame, transform_from_frame_to_frame, transform and copies
    # ==========================================================================
    def transform_to_frame(self, target_frame):
        pass

    def transformed_to_frame(self, target_frame):
        pass

    def transform_all_to_frame(self, target_frame):
        """Transforms all the elements to the target frame.
        Use it when you want to orient all elements e.g. to XY plane

        Returns:
            None

        Examples:
            >>> my_assembly = Assembly("model") # for sure you need to place elements inside
            >>> t = Frame([0, 0, 10], [1, 0, 0], [0, 1, 0])
            >>> my_assembly.transform_all_to_frame(t)

        """
        # apply the transformation the value
        if isinstance(self.value, Element):
            self.value.transformed_to_frame(target_frame)

        # recursively iterate through sub_assemblies value and transform them
        for sub_assembly in self.sub_assemblies:
            sub_assembly.transform_to_frame(target_frame)

    def transformed_all_to_frame(self, target_frame):
        """Copies and transforms all the elements to the target frame.
        Use it when you want to orient all elements e.g. to XY plane

        Returns:
            Assembly

        Examples:
            >>> my_assembly = Assembly("model") # for sure you need to place elements inside
            >>> t = Frame([0, 0, 10], [1, 0, 0], [0, 1, 0])
            >>> transformed_assembly = my_assembly.transformed_all_to_frame(t)

        """
        new_instance = self.copy()
        new_instance.transform_to_frame(target_frame)
        return new_instance

    def transform_from_frame_to_frame(self, source_frame, target_frame):
        """Transforms the value and all sub_assemblies from the source frame to the target frame.

        Returns:
            None

        Examples:
            >>> s = Frame([0, 0, 0], [1, 0, 0], [0, 1, 0])
            >>> t = Frame([0, 0, 10], [1, 0, 0], [0, 1, 0])
            >>> my_assembly = Assembly("model") # for sure you need to place elements inside
            >>> my_assembly.transform_from_frame_to_frame(s, t)

        """
        # apply the transformation the value
        if isinstance(self.value, Element):
            self.value.transform_from_frame_to_frame(source_frame, target_frame)

        # recursively iterate through sub_assemblies value and transform them
        for sub_assembly in self.sub_assemblies:
            sub_assembly.transform_to_frame(source_frame, target_frame)

    def transformed_from_frame_to_frame(self, source_frame, target_frame):
        """Transforms the value and all sub_assemblies
        from the source frame to the target frame and returns a copy.

        Returns:
            Assembly

        Examples:
            >>> s = Frame([0, 0, 0], [1, 0, 0], [0, 1, 0])
            >>> t = Frame([0, 0, 10], [1, 0, 0], [0, 1, 0])
            >>> my_assembly = Assembly("model") # for sure you need to place elements inside
            >>> transformed_assembly = my_assembly.transformed_from_frame_to_frame(s, t)

        """
        new_instance = self.copy()
        new_instance.transformed_from_frame_to_frame(source_frame, target_frame)
        return new_instance

    def transform(self, transformation):
        """Transforms the value and all sub_assemblies by the given transformation.

        Returns:
            None

        Examples:
            >>> transformation = Translation.from_vector([1, 2, 3])
            >>> my_assembly = Assembly("model") # for sure you need to place elements inside
            >>> my_assembly.transform(transformation)

        """
        # apply the transformation the value
        if isinstance(self.value, Element):
            self.value.transform(transformation)

        # recursively iterate through sub_assemblies value and transform them
        for sub_assembly in self.sub_assemblies:
            sub_assembly.transform(transformation)

    def transformed(self, transformation):
        """Transforms the value and all sub_assemblies by the given transformation and returns a copy.

        Returns:
            Assembly

        Examples:
            >>> transformation = Translation.from_vector([1, 2, 3])
            >>> my_assembly = Assembly("model") # for sure you need to place elements inside
            >>> transformed_assembly = my_assembly.transformed(transformation)

        """
        new_instance = self.copy()
        new_instance.transform(transformation)
        return new_instance

    # ==========================================================================
    # GET ALL ELEMENT PROPERTIES OR RUN THEIR METHODS
    # ==========================================================================
    def child_properties(self, collection, attribute_name="_aabb"):
        """get properties from the assembly values and sub_assemblies
        to know which functions exist in the assembly look at the Element class or documentation

        Returns:
            None

        Examples:
            >>> my_assembly = Assembly("model") # for sure you need to place elements inside
            >>> output_list = []
            >>> my_assembly.child_properties(output_list, "frame")

        """
        # collect attibutes
        if isinstance(self.value, Element):
            result = getattr(self.value, attribute_name, None)

            # check possible results
            collection.append(result)
            if result is None:
                print("WARNING Attribute --> " + attribute_name + " <-- not found in " + str(self.value))
            else:
                collection.append(result)

        # recursively iterate through sub_assemblies and collect the attribute
        for sub_assembly in self.sub_assemblies:
            sub_assembly.child_properties(collection, attribute_name)

    def child_behave(self, collection, method_name="aabb", *args, **kwargs):
        """Run methods from all the elements in the assembly and sub_assemblies
        to know which functions exist in the assembly look at the Element class or documentation
        self.child_behave(collection, "method_name", arg1, arg2, kwarg1=value1, kwarg2=value2)

        Returns:
            None

        Examples:
            >>> my_assembly = Assembly("model") # for sure you need to place elements inside
            >>> output_list = []
            >>> my_assembly.child_properties(output_list, "aabb", inflate=0.00)

        """

        # run the method

        # Use getattr() to check if the method exists and call it
        method_to_call = getattr(self.value, method_name, None)

        # check possible results
        if method_to_call is None or callable(method_to_call) is False:
            print("WARNING Method --> " + method_name + " <-- not found in " + str(self.value))
        else:
            # Call the method with add_assemblyitional arguments
            result = method_to_call(*args, **kwargs)
            # check possible results
            collection.append(result)

        # recursively iterate through sub_assemblies and collect the attribute
        for sub_assembly in self.sub_assemblies:
            sub_assembly.child_behave(collection, method_name, *args, **kwargs)

    def aabb(self, inflate=0.00):
        """compute the axis aligned bounding box of the assembly
        by collecting all the elements bounding boxes

        Returns:
            list(Point)

        Examples:
            >>> bounding_box_eight_corner_points = my_assembly.aabb(inflate = 0.01)
        """
        # first compute the aabb and then get it
        collection = []
        self.child_behave(collection, "aabb", inflate)

        # the output can be empty
        if collection is None:
            print("WARNING the bounding box is empty")
            return collection

        # flatten all bounding-boxes points
        collection_flat = []
        for points in collection:
            collection_flat.extend(points)

        # compute the bounding-box from all the boxes
        points_bbox = bounding_box(collection_flat)

        return points_bbox

    # ==========================================================================
    # VIZUALIZE
    # ==========================================================================
    def show(
        self,
        collapse_level=0,
        viewer_type="view2",
        width=1280,
        height=1600,
        show_grid=False,
        show_indices=False,
        show_names=False,
        show_simplices=False,
        show_complexes=True,
        show_aabbs=False,
        show_oobbs=False,
        show_convex_hulls=False,
        show_frames=False,
        show_fabrication=False,
        show_structure=False,
        text_height=30,  # type: ignore
        display_axis_scale=0.5,
        point_size=8,
        line_width=2,
        colors=[
            Color(0.929, 0.082, 0.498),
            Color(0.129, 0.572, 0.815),
            Color(0.5, 0.5, 0.5),
            Color(0.95, 0.95, 0.95),
            Color(0, 0, 0),
        ],
        color_red=[],
        measurements=[],
        geometry=[],
    ):
        """visualize the assembly in the viewer,
        check the Viewer.py file for more details

        Returns:
            None

        Examples:
            >>> my_assembly = Assembly("model") # for sure you need to place elements inside
            >>> my_assembly.show()
            >>> # or
            >>> my_assembly.show(collapse_level=2)

        """
        lists_of_elements = self.to_lists(collapse_level) if collapse_level >= 0 else self.graft("0").to_lists()
        Viewer.show_elements(
            lists_of_elements=lists_of_elements,
            viewer_type=viewer_type,
            width=width,
            height=height,
            show_grid=show_grid,
            show_indices=show_indices,
            show_names=show_names,
            show_simplices=show_simplices,
            show_complexes=show_complexes,
            show_aabbs=show_aabbs,
            show_oobbs=show_oobbs,
            show_convex_hulls=show_convex_hulls,
            show_frames=show_frames,
            show_fabrication=show_fabrication,
            show_structure=show_structure,
            text_height=text_height,
            display_axis_scale=display_axis_scale,
            point_size=point_size,
            line_width=line_width,
            colors=colors,
            color_red=color_red,
            measurements=measurements,
            geometry=geometry,
        )


if __name__ == "__main__":
    my_assembly = Assembly("model")
    my_assembly.add_assembly(Element(name="beam", simplex=Point(0, 0, 0)))
    my_assembly.add_assembly(Element(name="beam", simplex=Point(0, 5, 0)))
    my_assembly.add_assembly(Element(name="plate", simplex=Point(0, 0, 0)))
    my_assembly.add_assembly(Element(name="plate", simplex=Point(0, 7, 0)))
    print(my_assembly)

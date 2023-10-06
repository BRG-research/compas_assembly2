"""
Element
Petras Vestartas
2021-10-01

# ==========================================================================
# Description
# ==========================================================================
The TreeNode is a nested structure of assemblies and elements.

# ==========================================================================
# The minimal example
# ==========================================================================

NEVER DO THIS:
class TreeNode:
    def __init__(self, TreeNode):
        self.assemblies = []  # list<TreeNode>

DO THIS INSTEAD BECAUSE TreeNode MUST BE FINITE NOT RECURSIVE + IT CAN STORE PATH:
class TreeNode:
    def __init__(self, name):
        self.name = name  # can be a string or class<Element>
        self.parent = None
        self.childs = SortedList() # meaning the class<TreeNode> must have __lt__ method


# ==========================================================================
# What types are stored?
# ==========================================================================
The main property is called "name", it can be either:
a) group -> a string (indexing for the hierarch using text)
b) TreeNode -> class<TreeNode> (beams, plates, nodes, etc.)

# ==========================================================================
# How can the group hierarchy reperesented in one single class?
# ==========================================================================
It is represented by three propertes:
a) name -> group or class<element>
b) parent -> None or group
c) childs -> list<TreeNode or Element or mix of both>

# ==========================================================================
# How new assemblies or groups are add_tree_nodeed?
# ==========================================================================
When a child TreeNode is add_tree_nodeed the parent is set to the name TreeNode.
def add_tree_node_TreeNode(self, child):
    child.parent = self
    self.childs.add(child)

# ==========================================================================
# What the TreeNode is copied?
# ==========================================================================
One TreeNode can have multiple references of the same object can exist in one TreeNode,
only one object exists in a memory, this is handled by UUID

# ==========================================================================
# What about links between elements?
# ==========================================================================

a) root TreeNode has links between elements (a graph), which can be empty
b) the root TreeNode stores all elements

+---+---+---+---+---+---+--MORE-DETAILS-BELOW--+---+---+---+---+---+---+---+

# ==========================================================================
# How assemblies are transformed?
# ==========================================================================
Transformation is performed on a name branch and its childs using methods:
a) transform, transformed
b) orient, oriented (for the most common operation)

# ==========================================================================
# How to vizualize a TreeNode?
# ==========================================================================
def print_TreeNode(self):
    prefix = "   " * self.level
    prefix = prefix + "|__ " if self.parent else ""
    print(prefix + self.path_str)
    if self.childs:
        for child in self.childs:
            child.print_TreeNode()

# ==========================================================================
# How to know the level an object is nested at?
# ==========================================================================
@property
def level(self):
    level = 0
    p = self.parent
    while p:
        level = level + 1
        p = p.parent
    return level

# ==========================================================================
# How to know the depth an object is nested at?
# ==========================================================================
@property
def depth(self):
    # Initialize depth to 0 and start from the name node
    depth = 0
    current_node = self

    # Backtrack to the root parent while incrementing depth
    while current_node.parent:
        depth = depth + 1
        current_node = current_node.parent

    # Calculate the maximum depth by traversing childs's subTreeNodes
    return self._calculate_depth(self, depth)


"""

# user iteracts with the Model class only, meaning all the functions must be within the Model class

# todo:
# [x] - 1. serialization methods
# [x] - 2. flatten the TreeNode, to nested lists, collapse leaves by certain amount
# [x] - 3. update example filesy
# [x] - 4. show method
# [x] - 5. write tests for transformation, copy, properties retrieval
# [x] - 6. create TreeNode from json file
# [ ] - 7. is it necessary? -> add a frame to the root TreeNode for transformation
# [ ] - 8.1. add adjacency graph in the root and write examples files, vizualize it using networkx
# [ ] - 8.2. visualize the adjacency in the viewer simply, by drawing lines between element bbox centers
# [ ] - 9.1. add collision detection between elements, for this you need to flatten the elements and
# [ ] - 9.2. define collision pairs as lists of indices e.g. v0 "0,5,7", v1 "1,5,8"
# [ ] - 10 - write contact detection between elements and fill the root graph

import copy
from compas.data import Data
from compas.geometry import bounding_box, Point, Line, Frame, Transformation, Rotation, Translation  # noqa: F401
from compas_assembly2 import Element
from compas.colors import Color
from compas_assembly2.sortedlist import SortedList
from compas_assembly2.viewer import Viewer
from compas.data import json_load, json_dump
from compas.datastructures import Graph
from collections import OrderedDict


class Model(Data):
    """a data-structure to represent for storing elements and their relationships and hierarchies.
    You can also think about this data-structure a the root of the TreeNode.

    Args:
        elements (dict, optional): a flat collection of elements - dict{GUID, Element}. Defaults to {}.
        hierarchy (TreeNode, optional): hierarchical relationships between elements. Defaults to TreeNode("model").
        interactions (Graph, optional): abstract linkage or connection between elements. Defaults to Graph().

    """

    def __init__(self, name="model"):

        # --------------------------------------------------------------------------
        # for the Data Inheritance and serzialization
        # --------------------------------------------------------------------------
        super(Model, self).__init__()

        # --------------------------------------------------------------------------
        # main properties
        # --------------------------------------------------------------------------
        self.elements = OrderedDict()  # a flat collection of elements - dict{GUID, Element}
        self.hierarchy = TreeNode(name=name, elements=[], parent=self)  # hierarchical relationships between elements
        self.interactions = Graph()  # abstract linkage or connection between elements

        # --------------------------------------------------------------------------
        # attributes
        # --------------------------------------------------------------------------
        self.name = name

    # ==========================================================================
    # SERIALIZE
    # ==========================================================================
    @property
    def data(self):
        pass
        # # create the data object from the class properties§+
        # # call the inherited Data constructor for json serialization
        # data = {
        #     "name": self.name,
        #     "make_copy": self.make_copy,
        # }

        # # custom properties - handles circular references
        # data["parent"] = None if self.parent is None else self.parent.name
        # data["childs"] = [sub.data for sub in self.childs]

        # # return the data object
        # return data

    @data.setter
    def data(self, data):
        pass
        # # vice versa - create the class properties from the data object
        # # call the inherited Data constructor for json serialization

        # # main properties
        # self.name = data["name"]
        # self.make_copy = data["make_copy"]

        # # custom properties
        # self.parent = data["parent"]
        # self.childs = data["childs"]

    @classmethod
    def from_data(cls, data):
        # """Alternative to None default __init__ parameters."""
        pass

        # obj = TreeNode(name=data["name"], make_copy=data["make_copy"])

        # # custom properties
        # parent_data = data.get("parent")
        # if isinstance(parent_data, dict):
        #     obj.parent = TreeNode.from_data(parent_data)
        # else:
        #     obj.parent = None

        # Handle the childs list
        # obj.childs = []
        # for sub_data in data["childs"]:
        #     if isinstance(sub_data, dict):
        #         sub_obj = TreeNode.from_data(sub_data)  # Recursively create sub-TreeNode
        #         sub_obj.parent = obj  # Set the parent TreeNode
        #         obj.childs.append(sub_obj)
        #     else:
        #         # Handle non-TreeNode data types (e.g., strings or integers)
        #         obj.childs.append(sub_data)

        # # Return the object
        # return obj

    def serialize(self, fp, pretty=False):
        """Serialize the TreeNode to a JSON file."""
        json_dump(data=self.data, fp=fp, pretty=pretty)

    @staticmethod
    def deserialize(fp):
        """Deserialize the TreeNode to a JSON file."""
        data = json_load(fp=fp)
        return TreeNode.from_data(data)

    # ==========================================================================
    # DICTIONARY METHODS
    # ==========================================================================
    def add(self, element):
        self.elements[element.guid] = element

    # ==========================================================================
    # HIERARCHY METHODS
    # ==========================================================================
    def add_hierarchy(self, name="sub_model_such_as_structure", list_of_elements=[]):
        self.hierarchy.add_hierarchy(name=name, elements=list_of_elements, parent=self)
        # print(type(self))

    # ==========================================================================
    # INTERACTIONS METHODS
    # ==========================================================================
    def add_interactions(self, element0, element1):
        pass

    def create_graph(self):
        self.interactions = Graph()
        paths = self.collect_paths_to_elements()
        for idx, i in enumerate(paths):
            self.interactions.add_node(key=idx, attr_dict=None, path=i)

    # ==========================================================================
    # OPERATORS [], +, +=
    # ==========================================================================

    def __getitem__(self, arg):
        """get element by index"""
        if isinstance(arg, str):
            id = -1
            for local_id, my_TreeNode in enumerate(self.hierarchy.childs):
                if my_TreeNode.name == arg:
                    id = local_id
                    break
            if id == -1:
                print("WARNING GETTER the element is not found")
                return
            else:
                return self.hierarchy.childs[id]
        elif isinstance(arg, int):
            return self.hierarchy.childs[arg]

    def __setitem__(self, arg, user_object):
        """get element by index"""
        pass

    def __call__(self, index):
        try:
            if isinstance(index, int):
                return list(self.elements.values())[index]
            else:
                return self.elements[index]
        except KeyError:
            raise IndexError("Index out of range or key not found")

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
        new_instance = Model(name=self.hierarchy.name)
        new_instance.elements = copy.deepcopy(self.elements)
        new_instance.hierarchy = self.hierarchy.copy()
        new_instance.interactions = copy.deepcopy(self.interactions)

        return new_instance

    def transform(self):
        pass

    def __repr__(self):
        return (
            "Model: "
            + self.name
            + "\n elements: "
            + str(len(self.elements))
            + "\n hierarchy: "
            + self.hierarchy.stringify_tree_node()
            + "\n interactions: "
            + str(self.interactions)
        )

    def __str__(self):
        return self.__repr__()

    # ==========================================================================
    # COLLISION DETECTION
    # ==========================================================================
    def collect_paths_to_elements(self, current_path=None):
        """
        Recursively collect paths to elements of class type 'Element' within the TreeNode.

        Args:
            current_path (list, optional): The current path in the TreeNode. Defaults to None.

        Returns:
            list of tuple: A list of paths (tuples of indices) to 'Element' instances in the TreeNode.

        Examples:
            >>> my_TreeNode = TreeNode("model")
            >>> structure = TreeNode("structure")
            >>> #
            >>> timber = TreeNode("timber")
            >>> structure.add_tree_node(timber)
            >>> timber.add_tree_node(TreeNode(Element(name="beam", simplex=Point(0, 0, 0))))
            >>> timber.add_tree_node(TreeNode(Element(name="beam", simplex=Point(0, 5, 0))))
            >>> timber.add_tree_node(TreeNode(Element(name="plate", simplex=Point(0, 0, 0))))
            >>> timber.add_tree_node(TreeNode(Element(name="plate", simplex=Point(0, 7, 0))))
            >>> #
            >>> concrete = TreeNode("concrete")
            >>> structure.add_tree_node(concrete)
            >>> concrete.add_tree_node(TreeNode(Element(name="node", simplex=Point(0, 0, 0))))
            >>> concrete.add_tree_node(TreeNode(Element(name="block", simplex=Point(0, 5, 0))))
            >>> concrete.add_tree_node(TreeNode(Element(name="block", simplex=Point(0, 0, 0))))
            >>> #
            >>> my_TreeNode.add_tree_node(structure)
            >>> #
            >>> collected_paths = my_TreeNode.collect_paths_to_elements()
            >>> print(collected_paths)
            [(0, 0, 0), (0, 0, 1), (0, 0, 2), (0, 1, 0), (0, 1, 1), (0, 1, 2), (0, 1, 3)]
        """
        if current_path is None:
            current_path = []

        collected_paths = []

        # Check if the current node is of the target class
        if isinstance(self.hierarchy, Element):
            collected_paths.append(tuple(current_path))

        # Iterate through childs
        for index, child in enumerate(self.hierarchy.childs):
            current_path.append(index)  # Append the current index to the path
            collected_paths.extend(child.collect_paths_to_elements(current_path))
            current_path.pop()  # Remove the current index from the path

        return collected_paths

    def collision(self):
        """check collision detection between all the elements in the TreeNode

        Notes:
            nodes in the graph have a path attribute that is a tuple of indices:
            self.root.graph.add_node(key=idx, attr_dict=None, path=i)
            you can use it to retrieve individual elements from the assemnbly
            if you do not want to flatten it

        Following are the steps:
            1) unwrap the TreeNode to a list of elements and string as levels
            2) iterate in a simple for loop or any other structure to detect collisions
            3) fill the graph with the collision pairs

        Examples:
            >>> import random
            >>> from math import radians
            >>> from compas.geometry import Box
            >>> from compas_TreeNode2 import ELEMENT_NAME
            >>> #
            >>> b1 = Element(
            ...     name=ELEMENT_NAME.BLOCK,
            ...     id=0,
            ...     frame=Frame.worldXY,
            ...     simplex=Point(0, 0, 0),
            ...     complex=Box.from_width_height_depth(0.5, 0.5, 0.5))
            >>> #
            >>> num_copies = 200
            >>> max_translation = 8  # Maximum translation distance from the center
            >>> my_TreeNode = TreeNode("model")
            >>> my_TreeNode.add_tree_node("boxes")
            >>> for _ in range(num_copies):
            ...     # Generate random rotation and translation
            ...     random_axis = [random.random(), random.random(), random.random()]
            ...     random_rotation = Rotation.from_axis_and_angle(random_axis, radians(random.uniform(0, 360)))
            ...     vector = [random.uniform(-max_translation, max_translation) for _ in range(3)]
            ...     vector[2] = 0
            ...     random_translation = Translation.from_vector(vector)
            ...     # Apply random rotation and translation
            ...     transformed_element = b1.transformed(random_translation * random_rotation)
            ...     my_TreeNode[0].add_tree_node(transformed_element)
            >>> #
            >>> # collision
            >>> my_TreeNode.collision()
            >>> #
            >>> # iterate nodes and add lines for graph display
            >>> geometry = []
            >>> for pair in my_TreeNode.graph.edges():
            ...     # print(pair)
            ...     aabb0 = my_TreeNode[0][pair[0]].aabb()
            ...     c0 = Point(
            ...         (aabb0[0][0] + aabb0[6][0]) * 0.5,
            ...         (aabb0[0][1] + aabb0[6][1]) * 0.5,
            ...         (aabb0[0][2] + aabb0[6][2]) * 0.5
            ...     )
            ...     aabb1 = my_TreeNode[0][pair[1]].aabb()
            ...     c1 = Point(
            ...         (aabb1[0][0] + aabb1[6][0]) * 0.5,
            ...         (aabb1[0][1] + aabb1[6][1]) * 0.5,
            ...         (aabb1[0][2] + aabb1[6][2]) * 0.5
            ...     )
            ...     line = Line(c0, c1)
            ...     geometry.append(line)
        """

        elements = self.hierarchy.flatten()
        n = len(elements)

        # initialize the graph incase it does not exist
        self.create_graph()

        # check collision between elements, if one exists add_tree_node edge to the graph
        for i in range(n):
            for j in range(n):
                if i != j:
                    if elements[i].has_collision(elements[j]):
                        # print("collision between " + str(i) + " and " + str(j))
                        self.interactions.add_edge(i, j)

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
        """visualize the TreeNode in the viewer,
        check the Viewer.py file for more details

        # Returns:
        #     None

        # Examples:
        #     >>> try:
        #     ...     import compas_view2
        #     ...     my_TreeNode = TreeNode("model")  # for sure you need to place elements inside
        #     ...     p0 = Point(0, 0, 0)
        #     ...     p1 = Point(1, 0, 0)
        #     ...     my_TreeNode.add_tree_node(Element(name="beam", simplex=Point(0, 0, 0), complex=Line(p0, p1)))
        #     ...     my_TreeNode.show(collapse_level=0)

        """
        lists_of_elements = (
            self.hierarchy.to_lists(collapse_level) if collapse_level >= 0 else self.hierarchy.graft("0").to_lists()
        )
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


class TreeNode(Data):
    """TreeNode is a TreeNode data-structure.
    There are several ways how the data-structure can be used:
    a) the recursive structure allows to store group names as TreeNode branches and elements as TreeNode leaves.
    b) elememts can be nested within elements, which allows to store the TreeNode hierarchy.
    c) the root of TreeNode is responsible for storing links between elements

    Parameters
    ----------
        name : str - for grouping | Element or other type - for storing data
            each TreeNode must have a name
        parent : None or TreeNode
            this names is assigned automatically
        childs : SortedList
            this names is assigned automatically

    Attributes
    ----------
        make_copy : bool
            if True, the name will be copied, otherwise it will be referenced
        name : str
            the name of the name either
        is_group_or_TreeNode : bool
            True if the current branch name is a string
        level : int
            the level of the current branch
        root : TreeNode or None
            the root of the current branch
        depth : int
            the surface are of an element based on complex geometry
        type : str
            name GROUP if the name is string else ELEMENT
        number_of_elements : int
            the total number of elements in the TreeNode

    Example 1
    ---------
        >>> # EXAMPLE 1
        >>> my_TreeNode = TreeNode("my_TreeNode")
        >>> print(my_TreeNode)
        ======================================= ROOT TreeNode =============================================
        GROUP --> my_TreeNode
        ===================================================================================================

    Example 2
    ---------
        >>> # EXAMPLE 2
        >>> my_TreeNode = TreeNode("model")
        >>> my_TreeNode.add_tree_node(Element(name="beam", simplex=Point(0, 0, 0)))
        >>> my_TreeNode.add_tree_node(Element(name="beam", simplex=Point(0, 5, 0)))
        >>> my_TreeNode.add_tree_node(Element(name="plate", simplex=Point(0, 0, 0)))
        >>> my_TreeNode.add_tree_node(Element(name="plate", simplex=Point(0, 7, 0)))
        >>> print(my_TreeNode)  # doctest: +SKIP
        ======================================= ROOT TreeNode =============================================
        GROUP --> model
           |__ ELEMENT --> TYPE_BEAM ID_-1 GUID_fbe2a019-d3d0-4bb0-99a8-9a3a8276a4b3
           |__ ELEMENT --> TYPE_BEAM ID_-1 GUID_70d454cb-aa8b-4241-8cfb-cce98da476bb
           |__ ELEMENT --> TYPE_PLATE ID_-1 GUID_274f0a58-d301-4fc2-b9d1-06afa8f02d60
           |__ ELEMENT --> TYPE_PLATE ID_-1 GUID_cdcc2a05-d142-4a8f-a315-ef3aa2dc60ca
        ===================================================================================================

    Example 3
    ---------
        >>> # EXAMPLE 3
        >>> my_TreeNode = TreeNode("model")
        >>> structure = TreeNode("structure")
        >>> #
        >>> timber = TreeNode("timber")
        >>> structure.add_tree_node(timber)
        >>> timber.add_tree_node(TreeNode(Element(name="beam", simplex=Point(0, 0, 0))))
        >>> timber.add_tree_node(TreeNode(Element(name="beam", simplex=Point(0, 5, 0))))
        >>> timber.add_tree_node(TreeNode(Element(name="plate", simplex=Point(0, 0, 0))))
        >>> timber.add_tree_node(TreeNode(Element(name="plate", simplex=Point(0, 7, 0))))
        >>> #
        >>> concrete = TreeNode("concrete")
        >>> structure.add_tree_node(concrete)
        >>> concrete.add_tree_node(TreeNode(Element(name="node", simplex=Point(0, 0, 0))))
        >>> concrete.add_tree_node(TreeNode(Element(name="block", simplex=Point(0, 5, 0))))
        >>> concrete.add_tree_node(TreeNode(Element(name="block", simplex=Point(0, 0, 0))))
        >>> #
        >>> my_TreeNode.add_tree_node(structure)
        >>> print(my_TreeNode)  # doctest: +SKIP
        ======================================= ROOT TreeNode =============================================
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
    # CONSTRUCTOR THAT HAS A RECURSIVE DATA-STRUCTURE, DO NOT CHANGE IT!
    # ==========================================================================
    def __init__(
        self,
        name="my_tree",
        elements=[],
        parent=None,
    ):
        super(TreeNode, self).__init__()

        # --------------------------------------------------------------------------
        # the main data-structure representation, do not change it!
        # --------------------------------------------------------------------------
        self.name = name
        self.parent = parent
        self.childs = SortedList()

        # --------------------------------------------------------------------------
        # attributes
        # -----------------------------------------------------------------------
        self.elements = [] if elements is None else elements

    @staticmethod
    def example():
        """example of the TreeNode TreeNode structure

        Returns:
            TreeNode

        Examples:
            >>> my_TreeNode = TreeNode.example()

        """

        root = TreeNode("model")
        structure = TreeNode("structure")

        timber = TreeNode("timber")
        timber.add_tree_node(TreeNode(Element(name="beam", simplex=Point(0, 0, 0))))
        timber.add_tree_node(TreeNode(Element(name="beam", simplex=Point(0, 5, 0))))
        timber.add_tree_node(TreeNode(Element(name="plate", simplex=Point(0, 0, 0))))
        timber.add_tree_node(TreeNode(Element(name="plate", simplex=Point(0, 7, 0))))

        concrete = TreeNode("concrete")
        structure.add_tree_node(concrete)
        concrete.add_tree_node(TreeNode(Element(name="node", simplex=Point(0, 0, 0))))
        concrete.add_tree_node(TreeNode(Element(name="block", simplex=Point(0, 5, 0))))
        concrete.add_tree_node(TreeNode(Element(name="block", simplex=Point(0, 0, 0))))

        structure.add_tree_node(timber)
        root.add_tree_node(structure)
        return root

    # ==========================================================================
    # ATTRIBUTES
    # ==========================================================================

    @property
    def is_group_or_TreeNode(self):
        """Returns True if the current branch name is a string

        Returns:
            bool

        Examples:
            >>> my_TreeNode = TreeNode("my_TreeNode")
            >>> is_group = my_TreeNode.is_group_or_TreeNode

        """
        return isinstance(self.name, str)

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
        p = self.parent
        while p:
            level = level + 1
            if hasattr(p, "parent") is False:
                break
            p = p.parent
        return level

    @property
    def root(self):
        """Returns the root of the current branch

        Returns:
            TreeNode

        Examples:
            >>> my_TreeNode = TreeNode("my_TreeNode")
            >>> root_TreeNode = my_TreeNode.root

        """

        current_node = self
        while current_node.parent:
            if hasattr(current_node, "parent") is False:
                break
            current_node = current_node.parent
        return current_node

    @property
    def depth(self):
        """Returns the depth of the current branch

        Returns:
            int

        Examples:
            >>> my_TreeNode = TreeNode("my_TreeNode")
            >>> depth = my_TreeNode.depth

        """
        # Initialize depth to 0 and start from the name node
        depth = 0
        current_node = self

        # Backtrack to the root parent while incrementing depth
        while current_node.parent:
            if hasattr(current_node, "parent") is False:
                break
            depth = depth + 1
            current_node = current_node.parent

        # Calculate the maximum depth by traversing childs's subTreeNodes
        return self._calculate_depth(self, depth)

    def _calculate_depth(self, node, depth):
        if not node.childs:
            # If the node has no childs, return the name depth
            return depth

        max_child_depth = depth
        for child in node.childs:
            # Recursively calculate the depth for each child's subTreeNode
            child_depth = self._calculate_depth(child, depth + 1)
            if child_depth > max_child_depth:
                max_child_depth = child_depth

        # Return the maximum depth among childs's subTreeNodes
        return max_child_depth

    @property
    def number_of_elements(self):
        """Counts the total number of elements in the TreeNode

        Returns: The total number of elements in the TreeNode.
            int

        Examples:
            Create an TreeNode and count its elements:
            >>> my_TreeNode = TreeNode("my_TreeNode")
            >>> sub_1 = TreeNode("sub_1")
            >>> sub_2 = TreeNode("sub_2")
            >>> element = Element(name="beam", simplex=Point(0, 0, 0))
            >>> my_TreeNode.add_tree_node(sub_1)
            >>> my_TreeNode.add_tree_node(sub_2)
            >>> my_TreeNode.add_tree_node(element)
            >>> count = my_TreeNode.number_of_elements
        """
        number_of_elements = 0
        for child in self.childs:
            if isinstance(child.name, str):
                number_of_elements += child.number_of_elements
            else:
                number_of_elements += 1
                number_of_elements += child.number_of_elements
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
    # SERIALIZATION
    # ==========================================================================

    @property
    def data(self):
        # create the data object from the class properties§+
        # call the inherited Data constructor for json serialization
        data = {
            "name": self.name,
        }

        # custom properties - handles circular references
        data["parent"] = None if self.parent is None else self.parent.name
        data["childs"] = [sub.data for sub in self.childs]

        # return the data object
        return data

    @data.setter
    def data(self, data):
        # vice versa - create the class properties from the data object
        # call the inherited Data constructor for json serialization

        # main properties
        self.name = data["name"]

        # custom properties
        self.parent = data["parent"]
        self.childs = data["childs"]

    @classmethod
    def from_data(cls, data):
        """Alternative to None default __init__ parameters."""

        obj = TreeNode(name=data["name"])

        # custom properties
        parent_data = data.get("parent")
        if isinstance(parent_data, dict):
            obj.parent = TreeNode.from_data(parent_data)
        else:
            obj.parent = None

        # Handle the childs list
        obj.childs = []
        for sub_data in data["childs"]:
            if isinstance(sub_data, dict):
                sub_obj = TreeNode.from_data(sub_data)  # Recursively create sub-TreeNode
                sub_obj.parent = obj  # Set the parent TreeNode
                obj.childs.append(sub_obj)
            else:
                # Handle non-TreeNode data types (e.g., strings or integers)
                obj.childs.append(sub_data)

        # Return the object
        return obj

    def serialize(self, fp, pretty=False):
        """Serialize the TreeNode to a JSON file.

        Returns:
            None

        Examples:
            >>> my_TreeNode = TreeNode("model")
            >>> my_TreeNode.add_tree_node(Element(name="beam", simplex=Point(0, 0, 0)))
            >>> my_TreeNode.add_tree_node(Element(name="beam", simplex=Point(0, 5, 0)))
            >>> my_TreeNode.add_tree_node(Element(name="plate", simplex=Point(0, 0, 0)))
            >>> my_TreeNode.add_tree_node(Element(name="plate", simplex=Point(0, 7, 0)))
            >>> fp = "src/compas_TreeNode2/data_sets/doc_string_example.json"
            >>> my_TreeNode.serialize(fp)

        """
        json_dump(data=self.data, fp=fp, pretty=pretty)

    @staticmethod
    def deserialize(fp):
        """Deserialize the TreeNode to a JSON file.

        Returns:
            TreeNode

        Examples:
            >>> my_TreeNode = TreeNode("model")
            >>> my_TreeNode.add_tree_node(Element(name="beam", simplex=Point(0, 0, 0)))
            >>> my_TreeNode.add_tree_node(Element(name="beam", simplex=Point(0, 5, 0)))
            >>> my_TreeNode.add_tree_node(Element(name="plate", simplex=Point(0, 0, 0)))
            >>> my_TreeNode.add_tree_node(Element(name="plate", simplex=Point(0, 7, 0)))
            >>> fp = "src/compas_TreeNode2/data_sets/doc_string_example.json"
            >>> my_TreeNode.serialize(fp)
            >>> my_TreeNode = TreeNode.deserialize(fp)

        """
        data = json_load(fp=fp)
        return TreeNode.from_data(data)

    # ==========================================================================
    # PRINT METHODS
    # ==========================================================================

    def __repr__(self):
        """print the TreeNode structure of the TreeNode

        Returns:
            str: A string representation of the TreeNode.

        Examples:
            >>> my_TreeNode = TreeNode("my_TreeNode")
            >>> print(my_TreeNode)  # doctest: +SKIP
            ======================================= ROOT TreeNode =============================================
            GROUP --> my_TreeNode
            ===================================================================================================
        """
        return self.stringify_tree_node()

    def _stringify_tree_node(self, tree_node_str):
        """private method used by stringify_tree_node"""
        prefix = "   " * self.level
        prefix = prefix + "|__ " if self.parent else ""
        tree_node_str = prefix + self.name + " parent: " + str(type(self.parent))
        element_count = "" if len(self.elements) == 0 else " --> " + str(len(self.elements))
        tree_node_str += element_count
        tree_node_str += "\n"
        if self.childs:
            for child in self.childs:
                child_stringified = child._stringify_tree_node(tree_node_str)
                if child_stringified:
                    tree_node_str += child_stringified
                # print also elements, each element is printed in a new line
                for element in child.elements:
                    tree_node_str += "   " * (self.level + 1) + "   " + str(element) + "\n"
        return tree_node_str

    def stringify_tree_node(self):
        """returns the printed TreeNode structure

        Returns:
            str: A string representation of the TreeNode.

        Examples:
            >>> my_TreeNode = TreeNode("my_TreeNode")
            >>> my_string = my_TreeNode.stringify_tree_node()

        """
        tree_node_str = (
            "\n======================================= ROOT TreeNode =============================================\n"
        )
        tree_node_str += self._stringify_tree_node(tree_node_str)
        tree_node_str += (
            "===================================================================================================\n"
        )
        return tree_node_str

    def _print_TreeNode(self):
        """private method used by print_TreeNode"""
        prefix = "   " * self.level
        prefix = prefix + "|__ " if self.parent else ""
        print(prefix + self.type + " --> " + self.name)
        if self.childs:
            for child in self.childs:
                child._print_TreeNode()

    def print_TreeNode(self):
        """returns the printed TreeNode structure

        Returns:
            str: A string representation of the TreeNode.

        Examples:
            >>> my_TreeNode = TreeNode("my_TreeNode")
            >>> my_TreeNode.print_TreeNode()  # doctest: +SKIP

        """
        print("======================================= ROOT TreeNode =============================================")
        self._print_TreeNode()
        print("===================================================================================================")

    # ==========================================================================
    # ROOT BRANCH BEHAVIOR
    # ==========================================================================

    # def init_root(self):
    #     """initialize the root TreeNode properties"""
    #     if self.parent is None:
    #         self.graph = Graph()

    # def remove_root(self):
    #     """remove the root TreeNode properties"""
    #     if self.parent is not None:
    #         del self.graph

    # def transfer_root(self, new_root):
    #     """transfer the root TreeNode properties"""
    #     # --------------------------------------------------------------------------
    #     # if it was already the child it probably did not have any connectivity
    #     # --------------------------------------------------------------------------
    #     if self.parent is not None:
    #         return

    #     # --------------------------------------------------------------------------
    #     # update links
    #     # --------------------------------------------------------------------------
    #     n = self.graph.number_of_nodes()
    #     for pair in new_root.graph.edges():
    #         new_root.graph.append(pair[0] + n, pair[1] + n)

    # ==========================================================================
    # APPEND METHODS
    # add_tree_node() | add_tree_node_childs
    # add_by_index() | add_by_indexs
    # merge_tree_node() | merge_assemblies
    # ==========================================================================
    def add_hierarchy(self, elements, name="my_tree_node", parent=None):
        """adds TreeNode to the current TreeNode sub-assemblies list,
        if the user inout element or any other type, it will wrap into the TreeNode

        Returns:
            None

        Examples:
            >>> my_tree_node = TreeNode("my_tree_node")
            >>> e0 = Element(name="beam", simplex=Point(0, 0, 0))
            >>> e1 = Element(name="plate", simplex=Point(0, 0, 0))
            >>> my_tree_node.add_tree_node([e0, e1], "other_tree_node")

        """

        # update the parent and transfer the root properties
        tree_node = TreeNode(name=name, elements=elements, parent=self)

        # add_tree_node the child to the list
        self.childs.add(tree_node)

        # update the root dictionary of elements
        # print(type(self.root))
        # for element in elements:
        #     self.root.elements[element.guid] = element

    def merge_tree_node(self, a1, allow_duplicate_TreeNode_branches=False, allow_duplicate_TreeNode_leaves=True):
        """merge elements within two assemblies
        if the names of the groups are the same then the elements are merged in the same branch
        else they are added based on the a1 group names
        the merging have two boolean flag to allow duplicate branch names and leaves, if elements are references

        Returns:
            None

        Examples:
            >>> my_TreeNode = TreeNode("my_TreeNode")
            >>> a1 = TreeNode("a1")
            >>> my_TreeNode.merge_tree_node(a1)
            >>> # or if you want to have duplicated branches with the same names
            >>> my_TreeNode.merge_tree_node(a1, True, True)

        """

        # Helper function to find a node with the same name in a list of nodes
        def find_node_by_path(nodes, node_a1):
            if allow_duplicate_TreeNode_branches:  # or a1.is_group_or_TreeNode or node_a1.is_group_or_TreeNode
                return None
            else:
                if allow_duplicate_TreeNode_leaves:
                    if node_a1.is_group_or_TreeNode is False:
                        return None

                for node in nodes:
                    if node.name == node_a1.name:
                        return node
                return None

        # Iterate through the nodes in a1
        for node_a1 in a1.childs:
            # Check if there is an equivalent node in a0
            existing_node_a0 = find_node_by_path(self.childs, node_a1)
            if existing_node_a0 is not None:
                # Recursively merge the childs of the two nodes
                existing_node_a0.merge_tree_node(
                    node_a1, allow_duplicate_TreeNode_branches, allow_duplicate_TreeNode_leaves
                )
            else:
                # If no corresponding node is found, add_tree_node the node from a1 to a0
                self.add_tree_node(node_a1)

    def add_by_index(
        self, name, name_list=None, allow_duplicate_TreeNode_branches=False, allow_duplicate_TreeNode_leaves=True
    ):
        """add element to the TreeNode by creating group that follows element indices
        otherwise user can give a list of names to add an element to the specific branch

        Returns:
            None

        Examples:
            >>> my_TreeNode = TreeNode("my_TreeNode")
            >>> element = Element(name="beam", simplex=Point(0, 0, 0))
            >>> my_TreeNode.add_by_index(element)
            >>> # or
            >>> my_TreeNode.add_by_index(element, [0,5,9])

        """
        # create name
        name_list = name_list if name_list is not None else name.id

        branch_TreeNode = TreeNode("temp_-->_it_will_be_deleted_in_merge_tree_node_method")
        last_branch = branch_TreeNode
        for name in name_list:
            TreeNodename = str(name) if isinstance(name, int) else name
            child = TreeNode(TreeNodename)
            last_branch.add_tree_node(child)
            last_branch = child

        # add_tree_node "real" name to the last name
        last_branch.add_tree_node(TreeNode(name))

        # merge this name with the rest
        self.merge_tree_node(branch_TreeNode, allow_duplicate_TreeNode_branches, allow_duplicate_TreeNode_leaves)

    # ==========================================================================
    # MODIFY THE TreeNode STRUCTURE e.g. collapse, prune, graft
    # ==========================================================================
    def collapse(self, level):
        """Iterate through sub-assemblies and adjust their levels based on user input.
        0 - outputs one list with all elements
        1 - keep only the first branch level

        n - , where n is the deepest level, will place each element into individual branch

        Returns:
            TreeNode

        Examples:
            >>> my_TreeNode = TreeNode("my_TreeNode")
            >>> collapsed_TreeNode = my_TreeNode.collapse(0)

        """

        if level < 0:
            raise nameError("Level must be a non-negative integer.")

        # Start by copying the current TreeNode.
        collapsed_TreeNode = self.copy()

        if level == 0:
            elements = collapsed_TreeNode.flatten()
            collapsed_TreeNode.childs = SortedList()
            for element in elements:
                collapsed_TreeNode.add_tree_node(TreeNode(element))

        # Iterate through sub-assemblies.
        queue = []
        queue.extend(collapsed_TreeNode.childs)
        for child in queue:
            # If the sub-TreeNode has sub-assemblies, add_tree_node them to the queue.
            if child.level >= level:
                # find leave and add_tree_node it to the child
                elements = child.flatten()
                child.childs = SortedList()
                for element in elements:
                    child.add_tree_node(TreeNode(element))
            else:
                queue.extend(child.childs)

        return collapsed_TreeNode

    def graft(self, name="0"):
        """iterate through the assemblies if the leaves have multiple elements in a current TreeNode,
        then split it into individual branches under the given name

        Returns:
            TreeNode

        Examples:
            >>> my_TreeNode = TreeNode("my_TreeNode")
            >>> grafted_TreeNode = my_TreeNode.graft()

        """

        # Start by copying the current TreeNode.
        grafted_TreeNode = self.copy()

        # Iterate through sub-assemblies.
        queue = []
        queue.extend(grafted_TreeNode.childs)
        for child in queue:
            # If the sub-TreeNode has sub-assemblies, add_tree_node them to the queue.
            if isinstance(child.name, str) is False:
                temp = TreeNode(name=child.name)
                child.name = name
                child.add_tree_node(temp)
            else:
                queue.extend(child.childs)

        return grafted_TreeNode

    def prune(self, level):
        """Iterate through sub-assemblies and remove all sub-assemblies deeper than the given level.

        Returns:
            TreeNode

        Examples:
            >>> my_TreeNode = TreeNode("my_TreeNode")
            >>> pruned_TreeNode = my_TreeNode.prune(2)

        """

        if level < 0:
            raise nameError("Level must be a non-negative integer.")

        # Start by copying the current TreeNode.
        collapsed_TreeNode = self.copy()

        if level == 0:
            collapsed_TreeNode.childs = SortedList()

        # Iterate through sub-assemblies.
        queue = []
        queue.extend(collapsed_TreeNode.childs)
        for child in queue:
            # If the sub-TreeNode has sub-assemblies, add_tree_node them to the queue.
            if child.level >= level:
                # delete the branches that are deeper than a certain level
                child.childs = SortedList()
            else:
                queue.extend(child.childs)

        return collapsed_TreeNode

    # ==========================================================================
    # CONVERTION TO LISTS
    # ==========================================================================
    def to_nested_list(self):
        """convert the TreeNode to nested lists
        ATTENTION: in majority of practical cases use to_lists() method instead
        it reduces the hierarchy to a list of lists

        Returns:
            list(list(list(...)), list(...))

        Examples:
            >>> my_TreeNode = TreeNode("my_TreeNode")
            >>> my_lists = my_TreeNode.to_nested_list()

        """

        def _to_nested_list(TreeNode):
            # divide into 1) empty assemblies 2) nested ones
            result = []

            for child in TreeNode.childs:
                if isinstance(child.name, Element):
                    result.append(child.name)
                else:
                    result.append(_to_nested_list(child))
            if len(result) > 0:
                return result

        return _to_nested_list(self)

    def to_lists(self, collapse_level=None):
        """unwrap the nested nested n times lists in one list of lists

        Returns:
            list(list(element0, element1, ...), list(element0, element1, ...))

        Examples:
            >>> my_TreeNode = TreeNode("my_TreeNode")
            >>> my_list = my_TreeNode.to_lists()

        """

        if len(self.childs) == 0:
            return []

        # references
        TreeNode = self

        # collapse
        if collapse_level is not None:
            if collapse_level >= 0:
                TreeNode = self.collapse(collapse_level)
            else:
                TreeNode = self.graft("0")

        # convert the TreeNode to nested list
        TreeNode = TreeNode.to_nested_list()

        # convert the nested lists to list of lists
        lists = []
        queue = list(TreeNode)  # type: ignore
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
            return TreeNode
        else:
            return lists

    def _flatten(self, list):
        """private method used by flatten method"""
        if self.childs:
            for child in self.childs:
                if isinstance(child.name, str) is False:  # isinstance(child.name, Element)
                    list.append(child.name)
                if len(child.childs) > 0:
                    child._flatten(list)
        return list

    def flatten(self):
        """get all elemenets of the TreeNode in one single list

        Returns:
            list( element0, element1, ... )

        Examples:
            >>> my_TreeNode = TreeNode("my_TreeNode")
            >>> my_list = my_TreeNode.flatten()

        """
        list = []
        return self._flatten(list)

    # ==========================================================================
    # OPERATORS [], +, +=
    # ==========================================================================
    def __getitem__(self, arg):
        """get the TreeNode by name or index
        a) my_TreeNode["name"] or my_TreeNode[0]
        b) or nested asses my_TreeNode["name1"]["name2"] or my_TreeNode[0][0]

        ATTENTION:
        if you want to retrieve an element write my_TreeNode["name"].name

        Returns:
            TreeNode

        Examples:
            >>> my_TreeNode = TreeNode("model") # for sure you need to place elements inside
            >>> my_TreeNode.add_tree_node(TreeNode("another_TreeNode"))
            >>> my_TreeNode[0].add_tree_node(Element(name="beam", simplex=Point(0, 0, 0)))
            >>> my_TreeNode[0].add_tree_node(Element(name="plate", simplex=Point(0, 0, 0)))
            >>> my_child = my_TreeNode[0]
            >>> # or
            >>> my_child = my_TreeNode[0][1]

        """

        # string input
        if isinstance(arg, str):
            id = -1
            for local_id, my_TreeNode in enumerate(self.childs):
                if my_TreeNode.name == arg:
                    id = local_id
                    break
            if id == -1:
                print("WARNING GETTER the element is not found")
                return
            else:
                return self.childs[id]
        elif isinstance(arg, int):
            return self.childs[arg]

            # INCASE YOU WANT TO OUTPUT ELEMENT NOT THE TreeNode
            # # check if name is string
            # if isinstance(self.childs[arg].name, str):  # type: ignore
            #     return self.childs[arg]
            # else:
            #     return self.childs[arg].name  # type: ignore

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
            if isinstance(user_object, TreeNode):
                user_object.parent = self.childs[arg].parent  # type: ignore
                del self.childs[arg]
                self.childs.add(user_object)
        # --------------------------------------------------------------------------
        # user gives string as an input
        # --------------------------------------------------------------------------
        else:
            # find index of the element
            id = -1
            for local_id, my_TreeNode in enumerate(self.childs):
                if my_TreeNode.name == input_name:
                    id = local_id
                    break
            # if the element is not found
            if id == -1:
                print("WARNING SETTER the element is not found")
                return
            else:
                if isinstance(user_object, TreeNode):
                    self.childs[input_name] = user_object

    def __call__(self, index):
        """this works as a setter and getter since classes are references in memory"""
        return self.elements[index]

    def __add__(self, other):
        """plus sign to merge two assemblies as a copy

        Returns:
            TreeNode

        Examples:
            >>> TreeNode_0 = TreeNode("model") # for sure you need to place elements inside
            >>> TreeNode_1 = TreeNode("model") # for sure you need to place elements inside
            >>> my_child = TreeNode_0 + TreeNode_1
        """
        copy = self.copy()
        copy.merge_tree_node(other)
        return copy

    def __iadd__(self, other):
        """plus equal sign to merge two assemblies as a copy

        Returns:
            TreeNode

        Examples:
            >>> my_TreeNode = TreeNode("model") # for sure you need to place elements inside
            >>> other_TreeNode = TreeNode("model") # for sure you need to place elements inside
            >>> my_TreeNode += other_TreeNode

        """
        copy = self.copy()
        copy.merge_tree_node(other)
        return copy

    # ==========================================================================
    # COPY
    # ==========================================================================
    def _recursive_copy(self):
        # Create a new instance with the same name
        new_instance = copy.deepcopy(TreeNode(self.name))

        # Recursively copy child and its descendants
        for child in self.childs:
            child_copy = child._recursive_copy()
            new_instance.add_tree_node(child_copy)

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
    # TRANSFORM TreeNode ELEMENTS
    # transform_to_frame, transform_from_frame_to_frame, transform and copies
    # ==========================================================================
    def transform_to_frame(self, target_frame):
        """transfrom the TreeNode name to the target frame
        this works if the current TreeNode is element,
        meaning the elements are nested within elements
        WARNING: do not use this function for the TreeNode or subTreeNode
        whose name is not element, it will directly ignore it"""

        if isinstance(self.name, Element):
            self.transform_from_frame_to_frame(self.name.frame, target_frame)
            self.name.transform_to_frame(target_frame)

    def transformed_to_frame(self, target_frame):
        """transfrom the TreeNode copy name to the target frame
        this works if the current TreeNode is element,
        meaning the elements are nested within elements
        WARNING: do not use this function for the TreeNode or subTreeNode
        whose name is not element, it will directly ignore it"""

        copy = self.copy()
        self.transform_to_frame(target_frame)
        return copy

    def transform_all_to_frame(self, target_frame):
        """Transforms all the elements to the target frame.
        Use it when you want to orient all elements e.g. to XY plane

        Returns:
            None

        Examples:
            >>> my_TreeNode = TreeNode("model")  # for sure you need to place elements inside
            >>> t = Frame([0, 0, 10], [1, 0, 0], [0, 1, 0])
            >>> my_TreeNode.transform_all_to_frame(t)

        """
        # apply the transformation the name
        if isinstance(self.name, Element):
            self.name.transform_to_frame(target_frame)

        # recursively iterate through childs name and transform them
        for child in self.childs:
            child.transform_all_to_frame(target_frame)

    def transformed_all_to_frame(self, target_frame):
        """Copies and transforms all the elements to the target frame.
        Use it when you want to orient all elements e.g. to XY plane

        Returns:
            TreeNode

        Examples:
            >>> my_TreeNode = TreeNode("model")  # for sure you need to place elements inside
            >>> t = Frame([0, 0, 10], [1, 0, 0], [0, 1, 0])
            >>> transformed_TreeNode = my_TreeNode.transformed_all_to_frame(t)

        """
        new_instance = self.copy()
        new_instance.transform_all_to_frame(target_frame)
        return new_instance

    def transform_from_frame_to_frame(self, source_frame, target_frame):
        """Transforms the name and all childs from the source frame to the target frame.

        Returns:
            None

        Examples:
            >>> s = Frame([0, 0, 0], [1, 0, 0], [0, 1, 0])
            >>> t = Frame([0, 0, 10], [1, 0, 0], [0, 1, 0])
            >>> my_TreeNode = TreeNode("model") # for sure you need to place elements inside
            >>> my_TreeNode.transform_from_frame_to_frame(s, t)

        """
        # apply the transformation the name
        if isinstance(self.name, Element):
            self.name.transform_from_frame_to_frame(source_frame, target_frame)

        # recursively iterate through childs name and transform them
        for child in self.childs:
            child.transform_from_frame_to_frame(source_frame, target_frame)

    def transformed_from_frame_to_frame(self, source_frame, target_frame):
        """Transforms the name and all childs
        from the source frame to the target frame and returns a copy.

        Returns:
            TreeNode

        Examples:
            >>> s = Frame([0, 0, 0], [1, 0, 0], [0, 1, 0])
            >>> t = Frame([0, 0, 10], [1, 0, 0], [0, 1, 0])
            >>> my_TreeNode = TreeNode("model") # for sure you need to place elements inside
            >>> transformed_TreeNode = my_TreeNode.transformed_from_frame_to_frame(s, t)

        """

        new_instance = self.copy()
        new_instance.transform_from_frame_to_frame(source_frame, target_frame)
        return new_instance

    def transform(self, transformation):
        """Transforms the name and all childs by the given transformation.

        Returns:
            None

        Examples:
            >>> transformation = Translation.from_vector([1, 2, 3])
            >>> my_TreeNode = TreeNode("model")  # for sure you need to place elements inside
            >>> my_TreeNode.transform(transformation)

        """
        # apply the transformation the name
        if isinstance(self.name, Element):
            self.name.transform(transformation)

        # recursively iterate through childs name and transform them
        for child in self.childs:
            child.transform(transformation)

    def transformed(self, transformation):
        """Transforms the name and all childs by the given transformation and returns a copy.

        Returns:
            TreeNode

        Examples:
            >>> transformation = Translation.from_vector([1, 2, 3])
            >>> my_TreeNode = TreeNode("model")  # for sure you need to place elements inside
            >>> transformed_TreeNode = my_TreeNode.transformed(transformation)

        """
        new_instance = self.copy()
        new_instance.transform(transformation)
        return new_instance

    # ==========================================================================
    # GET ALL ELEMENT PROPERTIES OR RUN THEIR METHODS
    # ==========================================================================
    def child_properties(self, collection, attribute_name="_aabb"):
        """get properties from the TreeNode names and childs
        to know which functions exist in the TreeNode look at the Element class or documentation

        Returns:
            None

        Examples:
            >>> my_TreeNode = TreeNode("model") # for sure you need to place elements inside
            >>> my_TreeNode.add_tree_node(Element(name="beam", simplex=Point(0, 0, 0)))
            >>> output_list = []
            >>> my_TreeNode.child_properties(output_list, "frame")

        """
        # collect attibutes
        if isinstance(self.name, Element):
            result = getattr(self.name, attribute_name, None)

            # check possible results
            collection.append(result)
            if result is None:
                pass
                print("WARNING Attribute --> " + attribute_name + " <-- not found in " + str(self.name))
            else:
                collection.append(result)

        # recursively iterate through childs and collect the attribute
        for child in self.childs:
            child.child_properties(collection, attribute_name)

    def child_behave(self, collection, method_name="aabb", *args, **kwargs):
        """Run methods from all the elements in the TreeNode and childs
        to know which functions exist in the TreeNode look at the Element class or documentation
        self.child_behave(collection, "method_name", arg1, arg2, kwarg1=name1, kwarg2=name2)

        Returns:
            None

        Examples:
            >>> my_TreeNode = TreeNode("model")  # for sure you need to place elements inside
            >>> my_TreeNode.add_tree_node(Element(name="beam", simplex=Point(0, 0, 0), complex=Point(0, 0, 0)))
            >>> output_list = []
            >>> my_TreeNode.child_behave(output_list, "aabb", 0.00)

        """

        # Use getattr() to check if the method exists and call it
        method_to_call = getattr(self.name, method_name, None)

        # check possible results
        if method_to_call is None or callable(method_to_call) is False:
            pass
            # print("WARNING Method --> " + method_name + " <-- not found in " + str(self.name))
        else:
            # Call the method with additional arguments
            result = method_to_call(*args, **kwargs)
            # check possible results
            collection.append(result)

        # recursively iterate through childs and collect the attribute
        for child in self.childs:
            child.child_behave(collection, method_name, *args, **kwargs)

    def aabb(self, inflate=0.00):
        """compute the axis aligned bounding box of the TreeNode
        by collecting all the elements bounding boxes

        Returns:
            list(Point)

        Examples:
            >>> my_TreeNode = TreeNode("model") # for sure you need to place elements inside
            >>> my_TreeNode.add_tree_node(Element(name="beam", simplex=Point(0, 0, 0)))
            >>> bounding_box_eight_corner_points = my_TreeNode.aabb(inflate = 0.01)
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
    # Add elements to the model
    # ==========================================================================
    model.add(e0)
    model.add(e1)
    model.add(e2)
    model.add(e3)
    model.add(e4)
    model.add(e5)
    model.add(e6)

    # ==========================================================================
    # Add hierarchy to the model
    # ==========================================================================
    # this function must check if the root has the same name, if not add it
    model.add_hierarchy("structures")
    model[0].add_hierarchy([e0, e1, e2, e3], "timber")
    model[0].add_hierarchy([e4, e5, e6], "concrete")
    print(model)
    # print(model(0))
    # print(model(e1.guid))

    # # access using the most common way
    # model.hierarchy.childs[0].elements

    # # access using getter of the tree
    # model.hierarchy[0].elements

    # # access using the getter and caller of the tree e.g.
    # print(model.hierarchy["assembly_1"](0))

    # ==========================================================================
    # display
    # ==========================================================================
    # print(model)
    # my_TreeNode = TreeNode("model")
    # structure = TreeNode("structure")
    # #
    # timber = TreeNode("timber")
    # structure.add_tree_node(timber)
    # timber.add_tree_node(TreeNode(Element(name="beam", simplex=Point(0, 0, 0))))
    # timber.add_tree_node(TreeNode(Element(name="beam", simplex=Point(0, 5, 0))))
    # timber.add_tree_node(TreeNode(Element(name="plate", simplex=Point(0, 0, 0))))
    # timber.add_tree_node(TreeNode(Element(name="plate", simplex=Point(0, 7, 0))))
    # #
    # concrete = TreeNode("concrete")
    # structure.add_tree_node(concrete)
    # concrete.add_tree_node(TreeNode(Element(name="node", simplex=Point(0, 0, 0))))
    # concrete.add_tree_node(TreeNode(Element(name="block", simplex=Point(0, 5, 0))))
    # concrete.add_tree_node(TreeNode(Element(name="block", simplex=Point(0, 0, 0))))
    # #
    # my_TreeNode.add_tree_node(structure)
    # #
    # print(my_TreeNode)

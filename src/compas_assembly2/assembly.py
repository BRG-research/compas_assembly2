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
    def __init__(self, assemblyname_or_element):
        self.name_or_element = assemblyname_or_element  # can be a string or class<Element>
        self.parent_assembly = None
        self.sub_assemblies = [] # list<Assembly>


# ==========================================================================
# What types are stored?
# ==========================================================================
The main property is called "name_or_element", it can be either:
a) group -> a string (indexing for the hierarch using text)
b) assembly -> class<assembly> (beams, plates, nodes, etc.)

# ==========================================================================
# How can the group hierarchy reperesented in one single class?
# ==========================================================================
It is represented by three propertes:
a) name_or_element -> group or class<element>
b) parent_assembly -> None or group
c) sub_assemblies -> list<Assembly or Element or mix of both>

# ==========================================================================
# How new assemblies or groups are added?
# ==========================================================================
When a sub_assembly assembly is added the parent_assembly is set to the name_or_element assembly.
def add_assembly(self, sub_assembly):
    sub_assembly.parent_assembly = self
    self.sub_assemblies.append(sub_assembly)

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
Transformation is performed on a name_or_element branch and its sub_assemblies using methods:
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
    # Initialize depth to 0 and start from the name_or_element node
    depth = 0
    current_node = self

    # Backtrack to the root parent_assembly while incrementing depth
    while current_node.parent_assembly:
        depth = depth + 1
        current_node = current_node.parent_assembly

    # Calculate the maximum depth by traversing sub_assemblies's subtrees
    return self._calculate_depth(self, depth)


"""

import copy
from compas.data import Data
from compas.geometry import bounding_box, Point
from compas_assembly2 import Element
from compas.colors import Color
from compas.data import json_dump, json_load
# todo:
# 1. serialization method
# 3. show method
# 3. write tests for transformation, copy, properties retrieval
# ...
# 4. create a version with a dictionary, it is not dictionary, if really needed, then it is a sorted list (for sorting you also need keys)
class Assembly(Data):
    """Assembly is a tree data-structure.
    The recursive structure allows to store group names as tree branches and elements as tree leaves.
    The root of assembly is responsible for storing links between elements"""

    # ==========================================================================
    # Constructor and main body of the tree structureAssembly_Tree
    # ==========================================================================
    def __init__(self, name_or_obj, make_copy=True):
        super(Assembly, self).__init__()

        # --------------------------------------------------------------------------
        # the main data-structure representation, do not change it!
        # --------------------------------------------------------------------------
        self.make_copy = make_copy
        self.name_or_element = name_or_obj if self.make_copy is False or isinstance(name_or_obj, str) else name_or_obj.copy()
        self.parent_assembly = None
        self.sub_assemblies = []  # can be a list or dictionary or sorted dictionary

        # --------------------------------------------------------------------------
        # attributes
        # --------------------------------------------------------------------------
        self.init_root()

    # ==========================================================================
    # SERIALIZATION
    # ==========================================================================

    @property
    def data(self):
        # create the data object from the class properties§+
        # call the inherited Data constructor for json serialization
        data = {
            "name_or_obj": self.name_or_element,
            "make_copy": self.make_copy,
        }

        # custom properties - handles circular references
        data["parent_assembly"] = None if self.parent_assembly is None else self.parent_assembly.name_or_element
        data["sub_assemblies"] = [sub.data for sub in self.sub_assemblies]

        # return the data object
        return data

    @data.setter
    def data(self, data):
        # vice versa - create the class properties from the data object
        # call the inherited Data constructor for json serialization

        # main properties
        self.name_or_element = data["name_or_obj"]
        self.make_copy = data["make_copy"]

        # custom properties
        self.parent_assembly = data["parent_assembly"]
        self.sub_assemblies = data["sub_assemblies"]

    @classmethod
    def from_data(cls, data):
        """Alternative to None default __init__ parameters."""

        obj = Assembly(name_or_obj=data["name_or_obj"], make_copy=data["make_copy"])

        # custom properties
        parent_assembly_data = data.get("parent_assembly")
        if isinstance(parent_assembly_data, dict):
            obj.parent_assembly = Assembly.from_data(parent_assembly_data)
        else:
            obj.parent_assembly = None
        
        # Handle the sub_assemblies list
        
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




    def __repr__(self):
        return self.name

    @property
    def name(self):
        if isinstance(self.name_or_element, str):
            return self.name_or_element
        else:
            return str(self.name_or_element)

    @property
    def is_group_or_assembly(self):
        return isinstance(self.name_or_element, str)

    @property
    def level(self):
        level = 0
        p = self.parent_assembly
        while p:
            level = level + 1
            p = p.parent_assembly
        return level

    @property
    def root(self):
        current_node = self
        while current_node.parent_assembly:
            current_node = current_node.parent_assembly
        return current_node

    @property
    def depth(self):
        # Initialize depth to 0 and start from the name_or_element node
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
            # If the node has no sub_assemblies, return the name_or_element depth
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
        if isinstance(self.name_or_element, str):
            return "ASSEMBLY"
        else:
            return "ELEMENT"

    def _print_tree(self):
        prefix = "   " * self.level
        prefix = prefix + "|__ " if self.parent_assembly else ""
        print(prefix + self.type + " --> " + self.name)
        if self.sub_assemblies:
            for sub_assembly in self.sub_assemblies:
                sub_assembly._print_tree()

    def print_tree(self):
        print("======================================= ROOT ASSEMBLY =============================================")
        self._print_tree()
        print("===================================================================================================")

    # ==========================================================================
    # Functionality for the root assembly
    # ==========================================================================

    def init_root(self):
        if self.parent_assembly is None:
            self.graph = []
            self.all_assemblies = {}

    def remove_root(self):
        if self.parent_assembly is not None:
            del self.graph
            del self.all_assemblies

    def transfer_root(self, new_root):
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

        # --------------------------------------------------------------------------
        # update elements
        # --------------------------------------------------------------------------
        if not self.is_group_or_assembly:
            self.all_assemblies[self.name_or_element.guid] = self.name_or_element

        queue = [self]
        while queue:
            name_or_element = queue.pop(0)

            if not self.is_group_or_assembly:
                self.all_assemblies[self.name_or_element.guid] = self.name_or_element
            for sub_assembly in name_or_element.sub_assemblies:
                if not sub_assembly.is_group_or_assembly:
                    self.all_assemblies[sub_assembly.name_or_element.guid] = sub_assembly.name_or_element
                else:
                    queue.append(sub_assembly)

        # remove the attributes because they are not needed anymore
        self.remove_root_attributes()

    # ==========================================================================
    # APPEND METHODS
    # add() | add_sub_assemblies
    # add_by_index() | add_by_indexs
    # merge_assembly() | merge_assemblies
    # ==========================================================================

    def add(self, sub_assembly_or_object, sorted=True):
        sub_assembly = (
            sub_assembly_or_object if isinstance(sub_assembly_or_object, Assembly) else Assembly(sub_assembly_or_object)
        )

        sub_assembly.parent_assembly = self
        sub_assembly.transfer_root(self)

        # insert the sub_assembly
        if sorted and sub_assembly.is_group_or_assembly:
            # Find the index where the item should be inserted based on alphabetical order
            insert_index = 0
            while (
                insert_index < len(self.sub_assemblies) and self.sub_assemblies[insert_index].name < sub_assembly.name
            ):
                insert_index += 1

            # Insert the item at the determined index
            self.sub_assemblies.insert(insert_index, sub_assembly)
        else:
            self.sub_assemblies.append(sub_assembly)

    def merge_assembly(self, a1, allow_duplicate_assembly_branches=False, allow_duplicate_assembly_leaves=True):
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
                existing_node_a0.merge_assembly(node_a1, allow_duplicate_assembly_branches, allow_duplicate_assembly_leaves)
            else:
                # If no corresponding node is found, add the node from a1 to a0
                self.add(node_a1)

    def add_by_index(
        self, name_or_element, name_list=None, allow_duplicate_assembly_branches=False, allow_duplicate_assembly_leaves=True
    ):
        # create name_or_element
        name_list = name_list if name_list is not None else name_or_element.id

        branch_tree = Assembly("temp_-->_it_will_be_deleted_in_merge_assembly_method")
        last_branch = branch_tree
        for name in name_list:
            assemblyname_or_element = str(name) if isinstance(name, int) else name
            sub_assembly = Assembly(assemblyname_or_element)
            last_branch.add(sub_assembly)
            last_branch = sub_assembly

        # add "real" name_or_element to the last name_or_element
        last_branch.add(Assembly(name_or_element))

        # merge this name_or_element with the rest
        self.merge_assembly(branch_tree, allow_duplicate_assembly_branches, allow_duplicate_assembly_leaves)

    def __getitem__(self, arg):

        # names - user doesn't need to give the first assembly name
        input_name = arg if isinstance(arg, str) else str(arg)

        id = -1
        for local_id, my_assembly in enumerate(self.sub_assemblies):
            if my_assembly.name == input_name:
                id = local_id
                break
        if id == -1:
            print("WARNING GETTER the element is not found")
            return
        else:
            return self.sub_assemblies[id]

    def __setitem__(self, arg, user_object):
        input_name = arg

        if isinstance(arg, int):
            if isinstance(user_object, Element):
                self.sub_assemblies[arg].name_or_element = user_object
            elif isinstance(user_object, Assembly):
                self.sub_assemblies[arg] = user_object
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
                    self.sub_assemblies[input_name].name_or_element = user_object
                elif isinstance(user_object, Assembly):
                    self.sub_assemblies[input_name] = user_object

    def __add__(self, other):
        copy = self.copy()
        copy.merge_assembly(other)
        return copy

    def __iadd__(self, other):
        copy = self.copy()
        copy.merge_assembly(other)
        return copy

    # ==========================================================================
    # copy
    # ==========================================================================
    def _recursive_copy(self):
        # Create a new instance with the same name_or_element
        new_instance = Assembly(self.name_or_element)

        # Recursively copy sub_assembly and its descendants
        for sub_assembly in self.sub_assemblies:
            child_copy = sub_assembly._recursive_copy()
            new_instance.add(child_copy)

        return new_instance

    def copy(self):
        # Create a new instance with the same name_or_element
        new_instance = self._recursive_copy()

        # Once the structure is copied run the initialization again
        if self.parent_assembly is None:
            new_instance.init_root()  # collects all the elements
            new_instance.graph = copy.deepcopy(self.graph)  # transfer the connectivity

        return new_instance

    # ==========================================================================
    # geometry transformations
    # transform_to_frame, transform_from_frame_to_frame, transform and copies
    # ==========================================================================
    def transform_to_frame(self, target_frame):
        # apply the transformation the name_or_element
        if isinstance(self.name_or_element, Element):
            self.name_or_element.transformed_to_frame(target_frame)

        # recursively iterate through sub_assemblies name_or_element and transform them
        for sub_assembly in self.sub_assemblies:
            sub_assembly.transform_to_frame(target_frame)

    def transformed_to_frame(self, target_frame):
        new_instance = self.copy()
        new_instance.transform_to_frame(target_frame)
        return new_instance

    def transform_from_frame_to_frame(self, source_frame, target_frame):
        # apply the transformation the name_or_element
        if isinstance(self.name_or_element, Element):
            self.name_or_element.transform_from_frame_to_frame(source_frame, target_frame)

        # recursively iterate through sub_assemblies name_or_element and transform them
        for sub_assembly in self.sub_assemblies:
            sub_assembly.transform_to_frame(source_frame, target_frame)

    def transformed_from_frame_to_frame(self, source_frame, target_frame):
        new_instance = self.copy()
        new_instance.transformed_from_frame_to_frame(source_frame, target_frame)
        return new_instance

    def transform(self, transformation):
        # apply the transformation the name_or_element
        if isinstance(self.name_or_element, Element):
            self.name_or_element.transform(transformation)

        # recursively iterate through sub_assemblies name_or_element and transform them
        for sub_assembly in self.sub_assemblies:
            sub_assembly.transform(transformation)

    def transformed(self, transformation):
        new_instance = self.copy()
        new_instance.transform(transformation)
        return new_instance

    # ==========================================================================
    # bounding volumes
    # aabb
    # ==========================================================================
    def child_properties(self, collection, attribute_name="_aabb"):
        # collect attibutes
        if isinstance(self.name_or_element, Element):
            result = getattr(self.name_or_element, attribute_name, None)

            # check possible results
            collection.append(result)
            if result is None:
                print("WARNING Attribute --> " + attribute_name + " <-- not found in " + str(self.name_or_element))
            else:
                collection.append(result)

        # recursively iterate through sub_assemblies and collect the attribute
        for sub_assembly in self.sub_assemblies:
            sub_assembly.child_properties(collection, attribute_name)

    def child_behave(self, collection, method_name="aabb", *args, **kwargs):
        """# Assuming self is an instance of your class
        self.child_behave("method_name", collection, arg1, arg2, kwarg1=value1, kwarg2=value2)"""

        # run the method

        # Use getattr() to check if the method exists and call it
        method_to_call = getattr(self.name_or_element, method_name, None)

        # check possible results
        if method_to_call is None or callable(method_to_call) is False:
            print("WARNING Method --> " + method_name + " <-- not found in " + str(self.name_or_element))
        else:
            # Call the method with additional arguments
            result = method_to_call(*args, **kwargs)
            # check possible results
            collection.append(result)

        # recursively iterate through sub_assemblies and collect the attribute
        for sub_assembly in self.sub_assemblies:
            sub_assembly.child_behave(collection, method_name, *args, **kwargs)

    def aabb(self, inflate=0.00):
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
    # Vizualization
    # ==========================================================================
    def show(
        lists_of_elements=[],
        viewer_type="view2-0_rhino-1_blender-2",
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
        pass

def build_assembly_tree_0():

    root = Assembly("Oktoberfest")
    Schnitzel_Haus = Assembly("Restaurant The Taste of Berlin")
    Bier = Assembly("Bier")
    Bier.add(Assembly(Element(name="Water", simplex=Point(0, 0, 0), complex=Point(0, 0, 0))))
    Bier.add(Assembly(Element(name="Wheat malt", simplex=Point(0, 0, 0), complex=Point(0, 0, 0))))
    Bier.add(Assembly(Element(name="Noble hops", simplex=Point(0, 0, 0), complex=Point(0, 0, 0))))
    Bier.add(Assembly(Element(name="Wheat beer yeast", simplex=Point(0, 0, 0), complex=Point(0, 0, 0))))

    Schnitzel = Assembly("Schnitzel")
    Chicken = Assembly(Element(name="Chicken", simplex=Point(0, 0, 0), complex=Point(0, 0, 0)))
    Salt = Assembly(Element(name="Salt", simplex=Point(0, 0, 0), complex=Point(0, 0, 0)))
    Egg = Assembly(Element(name="Egg", simplex=Point(0, 0, 0), complex=Point(0, 0, 0)))
    Oil = Assembly(Element(name="Oil", simplex=Point(0, 0, 0), complex=Point(0, 0, 0)))
    Oil = Assembly(Point(0, 0, 0))
    Schnitzel.add(Chicken)
    Schnitzel.add(Salt)
    Schnitzel.add(Egg)
    Schnitzel.add(Oil)
    Schnitzel_Haus.add(Bier)
    Schnitzel_Haus.add(Schnitzel)
    root.add(Schnitzel_Haus)

    return root


def build_assembly_tree_1():
    # a1 name_or_element
    root = Assembly("Oktoberfest")
    Schnitzel_Haus = Assembly("Restaurant The Taste of Berlin")
    Bier = Assembly("Bier")
    Bier.add(Assembly(Element(name="Water", simplex=Point(0, 0, 0))))
    Bier.add(Assembly(Element(name="Pilsner malt", simplex=Point(0, 0, 0))))
    Bier.add(Assembly(Element(name="Saaz hops", simplex=Point(0, 0, 0))))
    Bier.add(Assembly(Element(name="Lager yeast", simplex=Point(0, 0, 0))))

    Bier2 = Assembly("Bier2")
    Schnitzel_Haus.add(Bier2)
    Schnitzel = Assembly("Schnitzel")
    Veal = Assembly(Element(name="Veal", simplex=Point(0, 0, 0)))
    Salt = Assembly(Element(name="Salt", simplex=Point(0, 0, 0)))
    Egg = Assembly(Element(name="Egg", simplex=Point(0, 0, 0)))
    Butter = Assembly(Element(name="Butter", simplex=Point(0, 0, 0)))
    Lemon = Assembly(Element(name="Lemon", simplex=Point(0, 0, 0)))

    Schnitzel.add(Veal)
    Schnitzel.add(Salt)
    Schnitzel.add(Egg)
    Schnitzel.add(Egg)
    Schnitzel.add(Butter)
    Schnitzel.add(Lemon)
    Schnitzel_Haus.add(Bier)
    Schnitzel_Haus.add(Schnitzel)
    root.add(Schnitzel_Haus)
    # print(root.depth)
    # print(root.sub_assemblies[0].depth)
    return root


if __name__ == "__main__":

    # --------------------------------------------------------------------------
    # Constructor
    # --------------------------------------------------------------------------
    a0 = build_assembly_tree_0()
    

    # # --------------------------------------------------------------------------
    # # Collection operators
    # # --------------------------------------------------------------------------
    # new_element0 = Element(name="___NEW_INSERTED_ELEMENT_0___", id=[0, 1])
    # a0["Restaurant The Taste of Berlin"]["Bier"][0] = new_element0

    # # # getter - append assemnbly to the current branch
    # new_element1 = Element(name="___NEW_INSERTED_ELEMENT_1___", id=[0, 1])
    # a0["Restaurant The Taste of Berlin"]["Bier"].add(new_element1)

    # # these operators call merge_assembly method, the structure is copie internally
    # # if you do not want to copy data just call merge_assembly method
    # # a1 = build_assembly_tree_1()
    # # a0.merge_assembly(a1)
    # # a0 = a0 + a1
    # # a0 += a0

    # new_element2 = Element(name="___NEW_INSERTED_ELEMENT_2___", id=[0, 1])
    # a0.add_by_index(new_element2, None, allow_duplicate_assembly_branches=False, allow_duplicate_assembly_leaves=True)
    # a0.add_by_index(new_element2, None, allow_duplicate_assembly_branches=False, allow_duplicate_assembly_leaves=True)
    # a0.add_by_index(new_element2, [0, 2])

    # # -----allow_duplicate_assembly_branc---------------------------------------------------------------------
    # a0_copy = a0.copy()

    # --------------------------------------------------------------------------
    # print the tree
    # --------------------------------------------------------------------------
    a0.print_tree()

    # --------------------------------------------------------------------------
    # geometry methods
    # --------------------------------------------------------------------------
    # print(a0.aabb(0.1))

    # --------------------------------------------------------------------------
    # SERIALIZATION
    # --------------------------------------------------------------------------
    json_dump(data=a0, fp="src/compas_assembly2/data_sets/assembly.json", pretty=True)
    a0_serialized = json_load(fp="src/compas_assembly2/data_sets/assembly.json")
    a0_serialized.print_tree()
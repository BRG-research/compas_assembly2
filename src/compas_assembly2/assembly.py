from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas.data import Data
from compas.geometry import Frame, Point

from compas_assembly2 import Element
from compas.datastructures import Graph

# https://grantjenks.com/docs/sortedcontainers/sorteddict.html
from compas_assembly2.sorteddict import SortedDict
import time


class Assembly(Data):
    """
    The compas_assembly2 represents:
    - a collection of structural elements such as blocks, beams, nodes, and plates.
    - it is a recursive structure reminiscent of the Composite pattern.
    - an element is primarily a description of simple and complex geometry.
    - initially elements do not have neither connectivity nor grouping information.
    - the grouping and connectivity are added manually by the user or automatically by collision detection.
    - an assembly can contain assemblies within assemblies.

    The visual representation of the assembly structure is below:
    - it means that the top-level assembly contains:
        - a list _all_elements (to query by id)
        - a list of child assemblies (to group elements)
        - a graph (for connectivity between all elements)
    """

    def __init__(self, name=None, elements=None, frame=None, **kwargs):
        """
        Initialize a new Assembly instance.

        Args:
            name (str): The name of the assembly. Default is "Root Assembly" if not provided.
            elements (list): A list of elements to add to the assembly.
            frame (Frame): The orientation frame for the assembly. Default is a default frame.
            **kwargs: Additional keyword arguments.

        Attributes:
            _id (int): The unique identifier for this assembly.
            _name (str): The name of the assembly.
            attributes (dict): Additional attributes associated with the assembly.
            _root: The root assembly in the assembly hierarchy.
            _parent: The parent assembly to which this assembly belongs.
            _assembly_childs (list): A list of child assemblies within this assembly.
            _assembly_dict (dict): A dictionary for looking up assemblies by name.
            _number_of_assemblies (int): The number of assemblies in the hierarchy.
            _level (int): The level of this assembly within the assembly hierarchy.
            _depth (int): The maximum depth of the assembly hierarchy.
            _elements (SortedDict): A sorted dictionary containing elements associated with this assembly.
            _graph (Graph): A graph for representing connectivity between elements.
            _frame (Frame): The orientation frame of the assembly.
        """

        # --------------------------------------------------------------------------
        # call the inherited Data constructor for json serialization
        # --------------------------------------------------------------------------
        super(Assembly, self).__init__()

        # --------------------------------------------------------------------------
        # declare index, naming and attributes
        # --------------------------------------------------------------------------
        # self._id = 0
        if name:
            self._name = name
        else:
            self._name = "-"

        self.attributes = {"name": name or "Assembly"}
        self.attributes.update(kwargs)

        # --------------------------------------------------------------------------
        # nested assemblies
        # the lookup is possible by
        #   1. using the recusive looping
        #   2. using the assembly id
        # --------------------------------------------------------------------------
        self._root = self
        self._parent = self
        self._assembly_childs = []  # there is no indexing for for assembly nesting
        self._assembly_dict = {}  # flat dictionary for the lookup using assembly ids
        self._number_of_assemblies = 0
        self._level = 0
        self._depth = 0

        # --------------------------------------------------------------------------
        # element dictionary
        # --------------------------------------------------------------------------
        self._elements = SortedDict()  # all elements in a model including nested assemblies ones

        if elements:
            print("elements given")
            for element in elements:
                # self.add_element_by_index(element)
                key = self.to_tuple(element.id)
                if key in self._elements:
                    self._elements[key].append(element)
                else:
                    self._elements[key] = [element]

        self._graph = Graph()  # for grouping elements

        # --------------------------------------------------------------------------
        # orientation frames
        # if user does not give a frame, try to define it based on simplex
        # --------------------------------------------------------------------------
        if isinstance(frame, Frame):
            self._frame = Frame.copy(frame)
        else:
            self._frame = Frame([0, 0, 0], [1, 0, 0], [0, 1, 0])

        # --------------------------------------------------------------------------
        # declare graph
        # --------------------------------------------------------------------------
        self._graph.update_default_node_attributes(
            {
                "element_name": None,
            }
        )

    # ==========================================================================
    # SETTER AND GETTER METHODS
    # ==========================================================================
    def to_tuple(self, input_data):
        """
        Convert input data to a tuple.

        Args:
            input_data: The input data to be converted.

        Returns:
            tuple: The converted input data as a tuple.

        Raises:
            ValueError: If the input data is not an integer, tuple, or list of integers.
        """
        if isinstance(input_data, int):
            return (input_data,)
        elif isinstance(input_data, (tuple, list)):
            return tuple(input_data)
        else:
            raise ValueError("Input must be an integer, tuple, or list of integers")

    def __getitem__(self, index):
        """
        Get elements by their ID.

        Args:
            index: The ID of the elements to retrieve.

        Returns:
            list: A list of elements with the specified ID.
        """
        key = self.to_tuple(index)
        return self._elements[key]

    def __setitem__(self, index, element):
        """
        Set elements by their ID.

        Args:
            index: The ID of the elements to set.
            element: The element to add or set.
        """
        key = self.to_tuple(index)
        if key in self._elements:
            self._elements[key].append(element)
        else:
            self._elements[key] = [element]

    def to_list(self):
        """
        Convert the dictionary of elements to a flat list of elements.

        Returns:
            list: A flat list of elements.
        """

        elements_list = []
        for _elements_list in self._elements.values():
            for element in _elements_list:
                elements_list.append(element)
        return elements_list

    def _get_elements_by_level(self, assembly, level, elements_lists, current_level=1):
        """Get elements by level in recursively."""

        if (current_level - 1) == level:
            child_elements_list = []
            for _elements_list in assembly._elements.values():
                for element in _elements_list:
                    child_elements_list.append(element)
            elements_lists.append(child_elements_list)
        else:
            child_elements_list = []
            for _elements_list in assembly._elements.values():
                for element in _elements_list:
                    child_elements_list.append(element)

        if current_level <= level:
            for child_assembly in assembly._assembly_childs:
                self._get_elements_by_level(child_assembly, level, elements_lists, current_level + 1)

    def to_lists(self, level=0, sort_childs_by_index=True):
        """
        Convert the dictionary of elements to a list of lists of elements, grouped by level.

        Args:
            level (int): The level to group elements by.
            sort_childs_by_index (bool): Whether to sort child assemblies by their index.

        Returns:
            list: A list of lists of elements.
        """

        elements_lists = []

        # one big mass of assembly
        if level is None or level <= 0:  # or level > self._depth
            for _elements_list in self._elements.values():
                elements_lists.extend(_elements_list)
            elements_lists = [elements_lists]
        # individual elements
        elif level > self._depth:
            for _elements_list in self._elements.values():
                elements_lists.extend(_elements_list)
        else:
            # get N-th level childs
            self._get_elements_by_level(self, level, elements_lists)

        # # sort the childs by the id of element
        # if sort_childs_by_index:
        #     tuple_list = []
        #     for element_list in elements_lists:
        #         tuple_list.append(element_list[0].id)

        #     combined_list = list(zip(tuple_list, elements_lists))
        #     combined_list.sort(key=lambda x: x[0])
        #     elements_lists = [item[1] for item in combined_list]

        return elements_lists

    def replace_in_empty(self, input_string, word, start_index, end_index):
        """
        Replace characters within a string with a specified word.

        Args:
            input_string (str): The input string.
            word (str): The word to replace characters with.
            start_index (int): The starting index of the characters to replace.
            end_index (int): The ending index of the characters to replace.

        Returns:
            str: The modified string.

        Raises:
            ValueError: If the indices are out of bounds.
        """
        if start_index < 0 or end_index >= len(input_string):
            raise ValueError("Indices are out of bounds")

        original_length = len(input_string)
        empty_part = input_string[:start_index] + " " * (end_index - start_index + 1) + input_string[end_index + 1 :]
        word = word[: end_index - start_index + 1].ljust(end_index - start_index + 1)

        new_string = empty_part[:start_index] + word + empty_part[end_index + 1 :]

        if len(new_string) != original_length:
            raise ValueError("New string length does not match the original length")

        return new_string

    def print_elements(self, assembly=None, prefix=""):
        """
        Print the elements and assembly structure.

        Args:
            assembly: The assembly to print. Defaults to the root assembly.
            prefix (str): A prefix for indentation.

        Example:
            assembly.print_elements()  # Print the assembly structure.
        """

        if assembly is None:
            assembly = self

        indentation = "    " * assembly._level

        elements_str = ", ".join([str(e) for e in assembly._elements.values()])
        elements_str = ""

        for e in assembly._elements.values():
            elements_str = elements_str + str(e) + ", " + str(id(e[0]))
        arrow = ">" if prefix else "-"

        print(
            "----- Assembly name: {} ----- lists {} {} {} [{}]".format(
                assembly.name, indentation, prefix, arrow, elements_str
            )
        )

        for idx, child in enumerate(assembly._assembly_childs):
            arrow = "--" if idx == len(assembly._assembly_childs) - 1 else "|--"
            self.print_elements(child, "{}".format(arrow))

    # ==========================================================================
    # TREE QUERING METHODS
    # ==========================================================================
    def add_element(self, element):
        """
        Add an element to the assembly.

        Args:
            element: The element to add.
        """
        # there are no assemblies, add the element to the root assembly
        key = self.to_tuple(element.id)
        # print("root", element, self)
        if key in self._elements:
            self._elements[key].append(element)
        else:
            self._elements[key] = [element]

    def add_element_by_index(self, element):
        """
        Add an element to the assembly with an index.

        Args:
            element: The element to add.

        Note:
            The element index can be a list, creating nested assemblies if needed.
        """

        # assemblies are created based on the assembly indices
        # option 1 - index is an integer
        if isinstance(element.id, int):
            self.add_element(element)  # add elements to the parent assembly
            if element.id >= len(self._assembly_childs):
                empty_assembly = Assembly(elements=[element])
                empty_assembly._root = self._root
                self.add_assembly(empty_assembly)
            else:
                assembly = self._assembly_childs[element.id]
                assembly.add_element(element)

        # option 2 - index is a list
        elif isinstance(element.id, (tuple, list)):

            # when the list is empty the element is added to the root assembly
            parent_assembly = self

            # self.add_element(element)  # add elements to the parent assembly

            # if the list is not empty we start adding elements iteratevely
            # parent assembly always contains child elements since they are references
            for index, local_index in enumerate(element.id):
                if isinstance(local_index, int) is False:
                    raise ValueError("Input must be an integer, tuple, or list of integers")

                # check if there is any current child with the same name
                # WARNING this can be optional, when assemblies with the same names must exist
                found_child = False
                print(parent_assembly)
                for child in parent_assembly._assembly_childs:
                    # print("_________________________", child.name, local_index)
                    if child.name == str(local_index):
                        parent_assembly = child
                        found_child = True
                        break
                # print("_________________________", found_child)

                # add elements to the parent assembly
                # print("local_index", local_index, "child_count", len(parent_assembly._assembly_childs))
                # print("parent_assembly", parent_assembly._id, self._root._number_of_assemblies)
                if found_child is False:
                    assembly = (
                        Assembly(elements=[element], name=str(local_index))
                        if index == len(element.id) - 1
                        else Assembly(name=str(local_index))
                    )
                    assembly._root = self._root
                    parent_assembly = parent_assembly.add_assembly(assembly)
                else:
                    parent_assembly.add_element(element)

    def add_assembly(self, assembly):
        """
        Add a child assembly to this assembly.

        Args:
            assembly (Assembly): The child assembly to be added.
            name (str): The name of the child assembly.

        Returns:
            Assembly: The added child assembly.
        """
        # change the root of the given assembly to current assembly
        # assembly.root = self._root

        # construct the child assembly from the given assembly
        # for elements in assembly._elements.values():
        #     for element in elements:
        #         self.add_element_by_index(element)
        # assembly._elements.clear()
        temp_assembly = Assembly()
        # temp_assembly._id = 0
        if assembly._name:
            temp_assembly._name = assembly.name
        else:
            temp_assembly._name = "-"

        temp_assembly.attributes = {"name": temp_assembly._name or "Assembly"}
        temp_assembly.attributes.update(assembly.attributes)

        # --------------------------------------------------------------------------
        # nested assemblies
        # the lookup is possible by
        #   1. using the recusive looping
        #   2. using the assembly id
        # --------------------------------------------------------------------------
        temp_assembly._root = self
        temp_assembly._parent = self
        temp_assembly._assembly_childs = []  # there is no indexing for for assembly nesting
        temp_assembly._assembly_dict = {}  # flat dictionary for the lookup using assembly ids
        temp_assembly._number_of_assemblies = 0
        temp_assembly._level = self._level + 1
        temp_assembly._depth = max(self._root._depth, self._level + 1)

        # --------------------------------------------------------------------------
        # element dictionary
        # --------------------------------------------------------------------------
        temp_assembly._elements = SortedDict()  # all elements in a model including nested assemblies ones

        if assembly._elements:
            print("elements given")
            for element_list in assembly._elements.values():
                for element in element_list:
                    print("element", element)
                    # self.add_element_by_index(element)
                    key = temp_assembly.to_tuple(element.id)
                    if key in temp_assembly._elements:
                        temp_assembly._elements[key].append(element)
                    else:
                        temp_assembly._elements[key] = [element]

        temp_assembly._graph = Graph()  # for grouping elements

        # --------------------------------------------------------------------------
        # orientation frames
        # if user does not give a frame, try to define it based on simplex
        # --------------------------------------------------------------------------
        if isinstance(temp_assembly._frame, Frame):
            temp_assembly._frame = Frame.copy(temp_assembly._frame)
        else:
            temp_assembly._frame = Frame([0, 0, 0], [1, 0, 0], [0, 1, 0])

        # --------------------------------------------------------------------------
        # declare graph
        # --------------------------------------------------------------------------
        temp_assembly._graph.update_default_node_attributes(
            {
                "element_name": None,
            }
        )

        # self._elements.update(assembly._elements)
        # self.add_element_by_index(child_assembly)
        self._assembly_childs.append(temp_assembly)
        return temp_assembly

        # add the assembly to the root dictionary
        # if child_assembly.name in self._assembly_dict:
        #     self._root._assembly_dict[child_assembly.name].append(child_assembly)
        # else:
        #     self._root._assembly_dict[child_assembly.name] = [child_assembly]

        # return self._root._assembly_dict[child_assembly.name][-1]

    def retrieve_assembly_by_name(self, val):
        """
        Retrieve an assembly by its name.

        Args:
            val (str): The name of the assembly to retrieve.

        Returns:
            Assembly: The retrieved assembly.

        Note:
            If the target name is "0," it returns the root assembly.
        """

        # if the target index is 0, return the root assembly
        if val == 0:
            return self

        queue = [self]

        while queue:

            # remove the first element from the queue
            assembly_child = queue.pop(0)

            # check if the target index is found
            if val == assembly_child.name:
                return assembly_child

            # keep adding childs to the queue until the target index is found
            queue.extend(assembly_child._assembly_childs)

        return None  # Node not found

    # ==========================================================================
    # OPTIONAL PROPERTIES - ELEMENTS
    # ==========================================================================
    @property
    def number_of_elements(self):
        """
        Get the number of elements in the assembly.

        Returns:
            int: The number of elements.
        """
        return len(self._elements)

    # ==========================================================================
    # ASSEMBLY METHODS
    # ==========================================================================

    # ==========================================================================
    # CONSTRUCTOR OVERLOADING
    # ==========================================================================

    # ==========================================================================
    # SERIALIZATION
    # ==========================================================================

    # ==========================================================================
    # OPTIONAL PROPERTIES - ELEMENTS
    # ==========================================================================

    def get_by_key(self, key):
        """
        Get elements by a specified key.

        Args:
            key (str): The key to search for in element attributes.

        Returns:
            list: A list of elements with the specified key.

        Example:
            assembly.get_by_key('t')  # Get elements with the 't' key in their attributes.
        """
        return [element.value for element in self._elements if key in element.attr]

    def get_elements_properties(self, property_name, flatten=True):
        """
        Get properties of elements flattened (True) or in nested lists (False).

        Args:
            property_name (str): The name of the property to retrieve.
            flatten (bool): Whether to flatten the properties into a single list.

        Returns:
            list: A list of element properties.

        Example:
            assembly.get_elements_properties('length')  # Get lengths of all elements.
        """
        elements_properties = []
        # for element_list in self._elements._objects.values():
        #     for element in element_list:
        for elements_list in self._elements.values():
            for element in elements_list:
                if hasattr(element, property_name):
                    property_value = getattr(element, property_name)
                    if flatten:
                        elements_properties.extend(property_value)
                    else:
                        elements_properties.append(property_value)
        return elements_properties

    # ==========================================================================
    # OPTIONAL PROPERTIES - ELEMENTS
    # ==========================================================================

    # ==========================================================================
    # COLLISION DETECTION
    # ==========================================================================
    def find_collisions_brute_force(self):
        """
        Find collisions between elements using a brute-force approach.

        Returns:
            list: A list of collision pairs, each pair containing the IDs of colliding elements.

        Note:
            This method is for display purposes to check which elements are colliding.
        """
        # start measuring time
        start_time = time.time()

        # input
        all_elements = [item for sublist in self._elements.values() for item in sublist]  # .to_flat_list()

        # output
        collision_pairs = []

        # only for display to check which elements are colliding
        element_collisions = [2] * self.number_of_elements
        for i in range(self.number_of_elements):
            for j in range(i + 1, self.number_of_elements):
                if all_elements[i].has_collision(all_elements[j]):
                    # collision_pairs.append([i, j])
                    collision_pairs.append([all_elements[i].id, all_elements[j].id])
                    # print(f"Collision between {all_elements[i].id} and {all_elements[j].id}")
                    element_collisions[i] = 0
                    element_collisions[j] = 0

        # end measuring time
        end_time = time.time()
        execution_time = end_time - start_time
        print(
            "Execution time: {:.6f} seconds\nnumber of elements: {}\nnumber of collisions: {}".format(
                execution_time, self.number_of_elements, len(collision_pairs)
            )
        )

        return collision_pairs

    # ==========================================================================
    # JOINT DETECTION
    # ==========================================================================
    def find_joints(self, collision_pairs_as_element_ids):
        """
        Find joints between elements based on collision pairs.

        Args:
            collision_pairs_as_element_ids (list): A list of collision pairs, each pair containing element IDs.

        Returns:
        """
        # it is assumed that keys are single element lists
        joints = []
        for pair in collision_pairs_as_element_ids:
            e0 = self.__getitem__(pair[0])[0]
            e1 = self.__getitem__(pair[1])[0]
            joints.extend(e0.face_to_face(e1))
        return joints

    # ==========================================================================
    # geometry - orient, copy, transform
    # ==========================================================================
    def copy(self):
        pass

    def transform(self, transformation):
        pass

    def transformed(self, transformation):
        pass

    def orient(self, frame):
        pass

    def oriented(self, frame):
        pass


# ==============================================================================
# Example Usage:
# ==============================================================================
if __name__ == "__main__":

    # this assembly has already nested assemblies by index
    assembly_1 = Assembly()
    # assembly_1.add_element(
    #     Element(id=[1, 2, 3], frame=Frame.worldXY(), simplex=Point(0, 0, 0), attr={"t": "Block", "m": 30})
    # )

    assembly_1.add_element_by_index(
        Element(id=[1, 2, 3], frame=Frame.worldXY(), simplex=Point(0, 0, 0), attr={"t": "Block", "m": 30})
    )
    print("__________________________________________________________________________________________")
    assembly_1.print_elements()
    # print(assembly_1._assembly_childs[0]._assembly_childs[0]._assembly_childs[0]._level)
    print("__________________________________________________________________________________________")

    # if you add this assembly to another assembly
    assembly_0 = Assembly()
    assembly_0.add_assembly(assembly_1)
    # assembly_0.add_assembly(assembly_1)
    # assembly_0._assembly_childs[0].add_assembly(assembly_1)
    # assembly_0._assembly_childs[0]._assembly_childs[0].add_assembly(assembly_1)

    # # assembly.add_element_by_index(
    # #     Element(id=[1, 2, 3], frame=Frame.worldXY(), simplex=Point(1, 0, 0), attr={"t": "Block", "m": 30})
    # # )

    assembly_0.print_elements()
    print("__________________________________________________________________________________________")
    # assembly_0.add_element_by_index(
    #     Element(id=[1, 2, 4], frame=Frame.worldXY(), simplex=Point(1, 0, 0), attr={"t": "Block", "m": 30})
    # )

    # assembly_1 = Assembly()

    # assembly_1.add_element_by_index(
    #     Element(id=[3, 0, 3], frame=Frame.worldXY(), simplex=Point(0, 5, 0), attr={"t": "Beam", "m": 25})
    # )

    # assembly_0.add_assembly(assembly_1)

    # print(assembly_0.print_elements())

    # assembly.add_element_by_index(
    #     Element(id=[3, 1, 3], frame=Frame.worldXY(), simplex=Point(0, 5, 0), attr={"t": "Beam", "m": 25})
    # )
    # assembly.add_element_by_index(
    #     Element(id=[0, 2, 4], frame=Frame.worldXY(), simplex=Point(7, 0, 0), attr={"t": "Block", "m": 25})
    # )
    # assembly.add_element_by_index(
    #     Element(id=[1, 0, 3], frame=Frame.worldXY(), simplex=Point(6, 0, 0), attr={"t": "Plate", "m": 40})
    # )
    # assembly.add_element_by_index(
    #     Element(id=[2, 2], frame=Frame.worldXY(), simplex=Point(0, 0, 8), attr={"t": "Block", "m": 30})
    # )

    #     # get the list of elements, instead of the dictionary (lists of lists with keys)
    #     print(assembly._elements.to_flat_list())
    #     print(assembly._elements.to_nested_list())
    #     print(assembly)
    #     print(assembly._elements.to_trimmed_dict("X"))
    #     print(assembly._elements.to_trimmed_list(0))

    #     # get properties of the elements
    #     print(assembly.get_elements_properties("simplex", True))
    #     print(assembly.get_elements_properties("simplex", False))

    # assembly.print_elements()

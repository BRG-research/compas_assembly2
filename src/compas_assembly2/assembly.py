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
import pytest



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
            depth (int): The maximum depth of the assembly hierarchy.
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
        self._allow_duplicate_assembly_names = False
        self._root = self
        self._parent = self
        self._assembly_childs = []  # there is no indexing for for assembly nesting
        self._assembly_dict = {}  # flat dictionary for the lookup using assembly names
        self._number_of_assemblies = 0
        self._level = 0
        self._depth = 0

        # --------------------------------------------------------------------------
        # element dictionary
        # --------------------------------------------------------------------------
        self._elements = SortedDict()  # all elements in a model including nested assemblies ones

        if elements:
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

        # --------------------------------------------------------------------------
        # when user runs this method, the asssembly is root
        # in other cases, the recursion assigns the assembly to the childs
        # --------------------------------------------------------------------------
        if assembly is None:
            assembly = self

        # --------------------------------------------------------------------------
        # identation based on the assembly level (if it is correctly set)
        # --------------------------------------------------------------------------
        indentation = "    " * assembly._level
        arrow = ">" if prefix else "-->"

        # --------------------------------------------------------------------------
        # element names
        # --------------------------------------------------------------------------
        elements_str = ""
        for e_list in assembly._elements.values():
            for e in e_list:
                elements_str = elements_str + "\n----- E " + str(e)
        
        # --------------------------------------------------------------------------
        # print the current level
        # --------------------------------------------------------------------------
        if (assembly._level == 0):
            print("___________________________________________________________________________________________________")

        print(
            "----- A NAME_{} DEPTH_{} LEVEL_{} ROOT_MEMO_{} ----- lists {} {}{} {}".format(
                assembly._name,
                assembly.depth,
                assembly._level,
                hex(id(assembly._root)),
                indentation,
                prefix,
                arrow,
                elements_str
            )
        )
        if (assembly._level == assembly.depth):
            print("___________________________________________________________________________________________________")
        # --------------------------------------------------------------------------
        # enumerate childs and print them recursively
        # -------------------------------------------------------------------------- -------------------------------------------------------------------------
        for idx, child in enumerate(assembly._assembly_childs):
            arrow = "--" if idx == len(assembly._assembly_childs) - 1 else "--"
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
                # empty_assembly._root = self._root
                self.add_assembly(empty_assembly)
            else:
                assembly = self._assembly_childs[element.id]
                assembly.add_element(element)

        # option 2 - index is a list
        elif isinstance(element.id, (tuple, list)):

            # when the list is empty the element is added to the root assembly
            parent_assembly = self

            # if the list is not empty we start adding elements iteratevely
            for index, local_index in enumerate(element.id):
                if isinstance(local_index, int) is False:
                    raise ValueError("Input must be an integer, tuple, or list of integers")

                # check if there is any current child with the same name
                # WARNING this can be optional, when assemblies with the same names must exist
                found_child = False
                
                for child in parent_assembly._assembly_childs:
                    if child.name == str(local_index):
                        parent_assembly = child
                        found_child = True
                        break

                # add elements to the parent assembly
                if found_child is False:
                    temp_elements = [] if index < len(element.id) - 1 else [element]
                    assembly = (
                        Assembly(elements=temp_elements, name=str(local_index))
                        if index == len(element.id) - 1
                        else Assembly(name=str(local_index))
                    )
                    print("temp_elements", assembly._elements)
                    parent_assembly = parent_assembly.add_assembly(assembly)

                    # update the depth of the current and root, the depth is always number of integers + 1
                    self._depth = max(self._depth, len(element.id)+1)
                    parent_assembly._depth = max(self._depth, len(element.id)+1)
                    parent_assembly._root = self
                elif found_child is True and index == len(element.id) - 1:
                    #print("found_child", found_child)
                    parent_assembly.add_element(element)
        print("________DEPTH_________", self._depth)


    def add_assembly(self, assembly, debug = False):
        """
        Add a child assembly to this assembly.

        Args:
            assembly (Assembly): The child assembly to be added.
            name (str): The name of the child assembly.

        Returns:
            Assembly: The added child assembly.
        """

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
        temp_assembly._name = assembly._name
        temp_assembly._parent = self
        temp_assembly._assembly_childs = assembly._assembly_childs  # there is no indexing for assembly nesting
        temp_assembly._assembly_dict = {}  # flat dictionary for the lookup using assembly ids
        temp_assembly._number_of_assemblies = 0
        temp_assembly._level = self._level + 1
        temp_assembly._depth = max(self._depth, temp_assembly._level)
        

        # --------------------------------------------------------------------------
        # element dictionary
        # --------------------------------------------------------------------------
        temp_assembly._elements = SortedDict()

        if assembly._elements:
            for element_list in assembly._elements.values():
                for element in element_list:
                    key = temp_assembly.to_tuple(element.id)
                    if key in temp_assembly._elements:
                        temp_assembly._elements[key].append(element)
                    else:
                        temp_assembly._elements[key] = [element]

        temp_assembly._graph = Graph()  # for grouping elements

        # --------------------------------------------------------------------------
        # assembly childs dictionary
        # update inner assemblies
        # --------------------------------------------------------------------------
        queue = list(temp_assembly._assembly_childs)

        while queue:
            temp_assembly_child = queue.pop(0)
            # -->
            temp_assembly_child._root = self
            temp_assembly_child._level = temp_assembly_child._level + 1
            self._root._depth = max(self._root._depth, temp_assembly_child._level)
            # <--
            queue.extend(temp_assembly_child._assembly_childs)

        # --------------------------------------------------------------------------
        # reassign depths
        # --------------------------------------------------------------------------
        queue = list(temp_assembly._assembly_childs)
        temp_assembly._depth = self._root._depth

        while queue:
            temp_assembly_child = queue.pop(0)
            # -->
            temp_assembly_child._depth = self._root._depth
            # <--
            queue.extend(temp_assembly_child._assembly_childs)


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

        # --------------------------------------------------------------------------
        # the assemblies can have either duplicated names or uniques names
        # the implementation explores both
        # --------------------------------------------------------------------------
        self._assembly_childs.append(temp_assembly)


        if (self._allow_duplicate_assembly_names == False):
            # print("self._allow_duplicate_assembly_names == False")
            pass
        else:
            pass

            # print("self._allow_duplicate_assembly_names == True")
            # --------------------------------------------------------------------------
            # check if there is any current child with the same name
            # --------------------------------------------------------------------------
            # def find_child_by_name(current_assemblies, my_assembly):
            #     id = -1
            #     for i in range(len(current_assemblies)):
            #         if (self.current_assemblies[i].name == my_assembly.name):
            #             id = i
            #             break
            #     return id

            # # id = find_child_by_name(self._assembly_childs, temp_assembly)
            # id = -1
            # if (id == -1):
            #     self._assembly_childs.append(temp_assembly)
            # else:
            #     for temp_assembly_child in temp_assembly:
            #         id = find_child_by_name(self._assembly_childs[id], temp_assembly_child)
            #         if (id == -1):
            #             self._assembly_childs[id].append(temp_assembly_child)
            #         else:
            #             for temp_temp_assembly_child in temp_assembly_child:
            #                 id = find_child_by_name(self._assembly_childs[id]._assembly_childs, temp_temp_assembly_child)
            #                 if (id == -1):
            #                     self._assembly_childs[id]._assembly_childs.append(temp_temp_assembly_child)
            #                 else:
            #                     pass
        return temp_assembly

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
        # --------------------------------------------------------------------------
        # input
        # --------------------------------------------------------------------------
        _number_of_elements = 0

        # --------------------------------------------------------------------------
        # number of elements in the root assembly
        # --------------------------------------------------------------------------

        for _elements_list in self._elements.values():
            _number_of_elements = _number_of_elements + len(_elements_list)

        # --------------------------------------------------------------------------
        # number of elements in the child assemblies
        # --------------------------------------------------------------------------
        queue = list(self._assembly_childs)

        while queue:
            temp_assembly_child = queue.pop(0)
            # -->
            for _elements_list in temp_assembly_child._elements.values():
                _number_of_elements = _number_of_elements + len(_elements_list)
            # <--
            queue.extend(temp_assembly_child._assembly_childs)

        # --------------------------------------------------------------------------
        # output
        # --------------------------------------------------------------------------
        return _number_of_elements
    
    @property
    def has_childs(self):
        """
        Check if the assembly has child assemblies.

        Returns:
            bool: True if the assembly has child assemblies.
        """
        return len(self._assembly_childs) > 0

    @property
    def depth(self):
        """
        Get the depth of the assembly.

        Returns:
            int: The depth of the assembly.
        """
        return self._root._depth
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
                    collision_pairs.append([all_elements[i].id, all_elements[j].id])
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

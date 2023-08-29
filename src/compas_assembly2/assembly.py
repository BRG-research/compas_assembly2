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


class Assembly_Child(Data):
    def __init__(self, assembly, parent, **kwargs):
        super(Assembly_Child, self).__init__()

        # indexing and naming
        self._root = assembly._root
        self._parent = parent
        self._root._number_of_assemblies = self._root._number_of_assemblies + 1
        self._id = self._root._number_of_assemblies
        self._name = assembly._name

        # current elements of the child assembly
        # add current assembly elements to the root Assembly
        # WARNING: there is no check for duplicate objects
        self._elements = SortedDict()
        for elements in assembly._elements.values():
            # since dictionary can have multiple elements with the same key, iterate over the list
            for element in elements:
                self.add_element(element)
                # self._parent.add_element(element)

        # child recursive tree
        self._assembly_childs = []  # there is no indexing for assembly nesting
        self._root._assembly_dict[self._id] = [self]

    # --------------------------------------------------------------------------
    # ASSEMBLY METHODS
    # --------------------------------------------------------------------------
    def add_assembly(self, assembly):
        # change the root of the given assembly
        assembly._root = self._root

        # construct the child assembly from the given assembly
        child_assembly = Assembly_Child(assembly, self)
        self._assembly_childs.append(child_assembly)

        # add the assembly to the root dictionary
        if child_assembly._name in self._root._assembly_dict:
            self._root._assembly_dict[child_assembly._name].append(child_assembly)
        else:
            self._root._assembly_dict[child_assembly._name] = [child_assembly]

        return self._root._assembly_dict[child_assembly._name][-1]

    # --------------------------------------------------------------------------
    # ELEMENT METHODS
    # --------------------------------------------------------------------------
    def to_tuple(self, input_data):
        if isinstance(input_data, int):
            return (input_data,)
        elif isinstance(input_data, (tuple, list)):
            return tuple(input_data)
        else:
            raise ValueError("Input must be an integer, tuple, or list of integers")

    def add_element(self, element):
        # there are no assemblies, add the element to the root assembly
        # print("child", element)
        key = self.to_tuple(element.id)
        if key in self._elements:
            self._elements[key].append(element)
        else:
            self._elements[key] = [element]


class Assembly(Data):
    def __init__(self, name=None, elements=None, frame=None, **kwargs):
        """
        The compas_assembly2 represents:
            a collection of structural elements such as blocks, beams, nodes, and plates.
            it is a recursive structure is reminiscent of the Composite pattern.
            an element is primary a description of a simple and complex geometry.
            initially elements do not have neither connectivity nor grouping information.
            the grouping and connectivity is added manually by the user or automatically by collision detection.
            assembly can contain assemblies within assemblies
            the visual representation of the assembly structure is below:
            it means that the top level assembly contains:
                a list _all_elements (to query by id)
                a list of child assemblies (to grouping elements)
                a graph (for connectivity between all elements)
        """

        # --------------------------------------------------------------------------
        # call the inherited Data constructor for json serialization
        # --------------------------------------------------------------------------
        super(Assembly, self).__init__()

        # --------------------------------------------------------------------------
        # declare index, naming and attributes
        # --------------------------------------------------------------------------
        self._id = 0
        if name:
            self._name = name
        else:
            self._name = "Root Assembly"

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
        if isinstance(input_data, int):
            return (input_data,)
        elif isinstance(input_data, (tuple, list)):
            return tuple(input_data)
        else:
            raise ValueError("Input must be an integer, tuple, or list of integers")

    def __getitem__(self, index):  # id is a list
        key = self.to_tuple(index)
        return self._elements[key]

    def __setitem__(self, index, element):  # id is a list
        key = self.to_tuple(index)
        if key in self._elements:
            self._elements[key].append(element)
        else:
            self._elements[key] = [element]

    def to_list(self):
        """Convert dictionary of _elements to a flat list of elements."""

        elements_list = []
        for _elements_list in self._elements.values():
            for element in _elements_list:
                elements_list.append(element)
        return elements_list

    def _get_elements_by_level(self, assembly, level, elements_lists, current_level=1):
        if current_level == level and assembly._assembly_childs:
            child_elements_list = []
            for _elements_list in assembly._elements.values():
                for element in _elements_list:
                    child_elements_list.append(element)
            elements_lists.append(child_elements_list)

        if current_level < level:
            for child_assembly in assembly._assembly_childs:
                self._get_elements_by_level(child_assembly, level, elements_lists, current_level + 1)

    def to_lists(self, level=1, sort_childs_by_index=True):
        """Convert dictionary of _elements to a list of list of elements."""

        elements_lists = []

        if level is None:
            for _elements_list in self._elements.values():
                elements_lists.append(_elements_list)
        else:
            # get first level childs
            self._get_elements_by_level(self, level, elements_lists)
            # if self._assembly_childs:
            #     for child_assembly in self._assembly_childs:
            #         child_elements_list = []
            #         for _elements_list in child_assembly._elements.values():
            #             for element in _elements_list:
            #                 child_elements_list.append(element)
            #         elements_lists.append(child_elements_list)

            # sort the childs by the id of element
            if sort_childs_by_index:
                tuple_list = []
                for element_list in elements_lists:
                    tuple_list.append(element_list[0].id)

                combined_list = list(zip(tuple_list, elements_lists))
                combined_list.sort(key=lambda x: x[0])
                elements_lists = [item[1] for item in combined_list]

        return elements_lists

        # # if the target index is 0, return the root assembly
        # result = []

        # queue = [self]

        # while queue:

        #     # remove the first element from the queue
        #     assembly_child = queue.pop(0)

        #     if assembly_nesting_level is None:
        #         # collect the elements of the assembly
        #         result.append(assembly_child._elements.values())

        #         # keep adding childs to the queue until the target index is found
        #         queue.extend(assembly_child._assembly_childs)

        # return result  # Node not found

    def replace_in_empty(self, input_string, word, start_index, end_index):
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
        if assembly is None:
            assembly = self

        _parent = assembly._parent
        counter = 0

        while _parent._id != 0:
            _parent = _parent._parent
            counter = counter + 1

        indentation = "|   " * counter

        elements_str = ", ".join([str(e) for e in assembly._elements.values()])
        arrow = "|-" if prefix else "-"
        print("--------- Assembly name: {} {} {} [{}]".format(assembly.name, indentation, prefix, arrow, elements_str))

        for idx, child in enumerate(assembly._assembly_childs):
            child_prefix = "|   " if idx < len(assembly._assembly_childs) - 1 else "    "
            arrow = "`--" if idx == len(assembly._assembly_childs) - 1 else "|--"
            self.print_elements(child, "{}{}".format(child_prefix, arrow))

    # ==========================================================================
    # TREE QUERING METHODS
    # ==========================================================================
    def add_element(self, element):
        # there are no assemblies, add the element to the root assembly
        key = self.to_tuple(element.id)
        # print("root", element, self)
        if key in self._elements:
            self._elements[key].append(element)
        else:
            self._elements[key] = [element]

    def add_element_by_index(self, element):
        """the element index can be a list, if it is the case, the case create assembly childs"""
        # print("add_element_by_index", element.id, "\n")

        # assemblies are created based on the assembly indices
        # option 1 - index is an integer
        if isinstance(element.id, int):
            self.add_element(element)  # add elements to the parent assembly
            if element.id >= len(self._assembly_childs):
                empty_assembly = Assembly(elements=[element])
                self.add_assembly(empty_assembly)
            else:
                assembly = self._assembly_childs[element.id]
                assembly.add_element(element)

        # option 2 - index is a list
        elif isinstance(element.id, (tuple, list)):

            # when the list is empty the element is added to the root assembly
            parent_assembly = self

            self.add_element(element)  # add elements to the parent assembly

            # if the list is not empty we start adding elements iteratevely
            # parent assembly always contains child elements since they are references
            for local_index in element.id:
                if isinstance(local_index, int) is False:
                    raise ValueError("Input must be an integer, tuple, or list of integers")

                # check if there is any current child with the same name
                # WARNING this can be optional, when assemblies with the same names must exist
                found_child = False
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
                    assembly = Assembly(elements=[element], name=str(local_index))
                    # print("create new assembly, parent_assembly", parent_assembly)
                    parent_assembly = parent_assembly.add_assembly(assembly)
                else:
                    # print("add to existing assembly")
                    parent_assembly.add_element(element)
                    # print("exists assembly, parent_assembly", parent_assembly)
                    # print("add to existing assembly, parent_assembly", parent_assembly)
                # print("parent_assembly", parent_assembly._id, self._root._number_of_assemblies)

    def add_assembly(self, assembly, name=None):
        # change the root of the given assembly
        assembly.root = self._root

        # construct the child assembly from the given assembly
        child_assembly = Assembly_Child(assembly, self._parent)
        self._assembly_childs.append(child_assembly)

        # add the assembly to the root dictionary
        if child_assembly.name in self._assembly_dict:
            self._root._assembly_dict[child_assembly.name].append(child_assembly)
        else:
            self._root._assembly_dict[child_assembly.name] = [child_assembly]

        return self._root._assembly_dict[child_assembly.name][-1]

    def retrieve_assembly_by_index(self, val):

        # if the target index is 0, return the root assembly
        if val == 0:
            return self

        queue = [self]

        while queue:

            # remove the first element from the queue
            assembly_child = queue.pop(0)

            # check if the target index is found
            if val == assembly_child._id:
                return assembly_child

            # keep adding childs to the queue until the target index is found
            queue.extend(assembly_child._assembly_childs)

        return None  # Node not found

    def retrieve_assembly_by_name(self, val):

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
        """Get the number of elements in the assembly."""
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
        Get the element(s) with the specified key.

        Parameters:
            key (str): The t of the key to search for.

        Returns:
            List[Element]: A list of Element objects that match the specified key and value.

        Example:
            assembly.add(Element(id=(1, 2, 3), l_frame=None, g_frame=None, attr={'t': 'Block', 'm': 30}))
            assembly.add(Element(id=(1, 3, 5), l_frame=None, g_frame=None, attr={'t': 'Beam', 'm': 25}))

            result = assembly.get_by_key('t')
            print(result)  # Output: [Element1, Element2]
        """
        return [element.value for element in self._elements if key in element.attr]

    def get_elements_properties(self, property_name, flatten=True):
        """Get properties of elements flattened (True) or in nested lists (False)."""
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
    assembly = Assembly()
    assembly.add_element_by_index(
        Element(id=[1, 2, 3], frame=Frame.worldXY(), simplex=Point(0, 0, 0), attr={"t": "Block", "m": 30})
    )
    # print(assembly._elements)
    # assembly.add_element_by_index(
    #     Element(id=[1, 2, 3], frame=Frame.worldXY(), simplex=Point(1, 0, 0), attr={"t": "Block", "m": 30})
    # )

    assembly.add_element_by_index(
        Element(id=[1, 2, 4], frame=Frame.worldXY(), simplex=Point(1, 0, 0), attr={"t": "Block", "m": 30})
    )
    # assembly.add_element_by_index(
    #     Element(id=[3, 0, 3], frame=Frame.worldXY(), simplex=Point(0, 5, 0), attr={"t": "Beam", "m": 25})
    # )
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

    print(assembly.print_elements())

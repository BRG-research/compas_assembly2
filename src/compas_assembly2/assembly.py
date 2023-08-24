from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas.data import Data
from compas.geometry import Frame

# from compas_assembly2 import Element
from compas.datastructures import Graph

# https://grantjenks.com/docs/sortedcontainers/sorteddict.html
from compas_assembly2.sortedgroup import SortedGroup
import time


class Assembly_Child(Data):
    def __init__(self, assembly, **kwargs):
        super(Assembly_Child, self).__init__()

        # indexing and naming
        self.root.number_of_assemblies = self.root.number_of_assemblies + 1
        self.id = self.root.number_of_assemblies
        self.name = assembly.name

        # current elements of the child assembly
        self.elements = assembly.elements

        # child recursive tree
        self.root = assembly.root
        self.assembly_childs = []
        self.root.assembly_dict[self.id] = self

    def add_assembly(self, assembly):
        # change the root of the given assembly
        assembly.root = self.root

        # construct the child assembly from the given assembly
        child_assembly = Assembly_Child(assembly)

        # add the assembly to the root dictionary
        self.assembly_childs.append(child_assembly)

        if child_assembly.name in self.root.assembly_dict:
            self.root.assembly_dict[child_assembly.name].append(child_assembly)
        else:
            self.root.assembly_dict[child_assembly.name] = [child_assembly]


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
        # declare main properties: elements, joints
        # --------------------------------------------------------------------------
        self.id = 0
        self.name = name
        self.elements = []  # all elements in a model
        self.graph = Graph()  # for grouping elements

        # --------------------------------------------------------------------------
        # nested assemblies
        # the lookup is possible by
        #   1. using the recusive looping
        #   2. using the assembly id
        # --------------------------------------------------------------------------
        self.root = self
        self.assembly_childs = []  # for grouping elements
        self.assembly_dict = {}  # for the lookup using assembly ids
        self.number_of_assemblies = 0

        # --------------------------------------------------------------------------
        # orientation frames
        # if user does not give a frame, try to define it based on simplex
        # --------------------------------------------------------------------------
        if isinstance(frame, Frame):
            self.frame = Frame.copy(frame)
        else:
            self.frame = Frame([0, 0, 0], [1, 0, 0], [0, 1, 0])

        # --------------------------------------------------------------------------
        # declare attributes
        # --------------------------------------------------------------------------
        self.attributes = {"name": name or "Assembly"}
        self.attributes.update(kwargs)

        # --------------------------------------------------------------------------
        # declare graph
        # --------------------------------------------------------------------------
        self.graph.update_default_node_attributes(
            {
                "element_name": None,
            }
        )

    # ==========================================================================
    # TREE QUERING METHODS
    # ==========================================================================
    def add_assembly(self, assembly):
        # change the root of the given assembly
        assembly.root = self.root

        # construct the child assembly from the given assembly
        child_assembly = Assembly_Child(assembly)

        # add the assembly to the list of child assemblies
        self.assembly_childs.append(child_assembly)

        # add the assembly to the root dictionary
        if child_assembly.name in self.assembly_dict:
            self.assembly_dict[child_assembly.name].append(child_assembly)
        else:
            self.assembly_dict[child_assembly.name] = [child_assembly]

    def retrieve_assembly_by_index(self, val):

        # if the target index is 0, return the root assembly
        if val == 0:
            return self

        queue = [self]

        while queue:

            # remove the first element from the queue
            assembly_child = queue.pop(0)

            # check if the target index is found
            if val == assembly_child.id:
                return assembly_child

            # keep adding childs to the queue until the target index is found
            queue.extend(assembly_child.assembly_childs)

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
            queue.extend(assembly_child.assembly_childs)

        return None  # Node not found

    # ==========================================================================
    # CONSTRUCTOR OVERLOADING
    # ==========================================================================

    # ==========================================================================
    # SERIALIZATION
    # ==========================================================================

    # ==========================================================================
    # OPTIONAL PROPERTIES - ELEMENTS
    # ==========================================================================

    # def get_by_key(self, key):
    #     """
    #     Get the element(s) with the specified key.

    #     Parameters:
    #         key (str): The t of the key to search for.

    #     Returns:
    #         List[Element]: A list of Element objects that match the specified key and value.

    #     Example:
    #         assembly.add(Element(id=(1, 2, 3), l_frame=None, g_frame=None, attr={'t': 'Block', 'm': 30}))
    #         assembly.add(Element(id=(1, 3, 5), l_frame=None, g_frame=None, attr={'t': 'Beam', 'm': 25}))

    #         result = assembly.get_by_key('t')
    #         print(result)  # Output: [Element1, Element2]
    #     """
    #     return [element.value for element in self._elements if key in element.attr]

    # def get_elements_properties(self, property_name, flatten=True):
    #     """Get properties of elements flattened (True) or in nested lists (False)."""
    #     elements_properties = []
    #     for element_list in self._elements._objects.values():
    #         for element in element_list:
    #             if hasattr(element, property_name):
    #                 property_value = getattr(element, property_name)
    #                 if flatten:
    #                     elements_properties.extend(property_value)
    #                 else:
    #                     elements_properties.append(property_value)
    #     return elements_properties

    # ==========================================================================
    # OPTIONAL PROPERTIES - ELEMENTS
    # ==========================================================================

    # ==========================================================================
    # COLLISION DETECTION
    # ==========================================================================
    # def find_collisions_brute_force(self):
    #     # start measuring time
    #     start_time = time.time()

    #     # input
    #     all_elements = self._elements.to_flat_list()

    #     # output
    #     collision_pairs = []

    #     # only for display to check which elements are colliding
    #     element_collisions = [2] * self._elements.size()
    #     for i in range(self._elements.size()):
    #         for j in range(i + 1, self._elements.size()):
    #             if all_elements[i].has_collision(all_elements[j]):
    #                 # collision_pairs.append([i, j])
    #                 collision_pairs.append([all_elements[i].id, all_elements[j].id])
    #                 # print(f"Collision between {all_elements[i].id} and {all_elements[j].id}")
    #                 element_collisions[i] = 0
    #                 element_collisions[j] = 0

    #     # end measuring time
    #     end_time = time.time()
    #     execution_time = end_time - start_time
    #     print(
    #         "Execution time: {:.6f} seconds\nnumber of elements: {}\nnumber of collisions: {}".format(
    #             execution_time, self._elements.size(), len(collision_pairs)
    #         )
    #     )

    #     return collision_pairs

    # ==========================================================================
    # JOINT DETECTION
    # ==========================================================================
    # def find_joints(self, collision_pairs_as_element_ids):
    #     # it is assumed that keys are single element lists
    #     joints = []
    #     for pair in collision_pairs_as_element_ids:
    #         joints.extend(self._elements[pair[0]][0].face_to_face(self._elements[pair[1]][0]))
    #     return joints

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
# if __name__ == "__main__":
#     assembly = Assembly()
#     assembly._elements.add(
#         Element(id=[1, 2, 3], frame=Frame.worldXY(), simplex=Point(0, 0, 0), attr={"t": "Block", "m": 30})
#     )
#     assembly._elements.add(
#         Element(id=[1, 2, 3], frame=Frame.worldXY(), simplex=Point(1, 0, 0), attr={"t": "Block", "m": 30})
#     )
#     assembly._elements.add(
#         Element(id=[1, 2, 4], frame=Frame.worldXY(), simplex=Point(1, 0, 0), attr={"t": "Block", "m": 30})
#     )
#     assembly._elements.add(
#         Element(id=[3, 0, 3], frame=Frame.worldXY(), simplex=Point(0, 5, 0), attr={"t": "Beam", "m": 25})
#     )
#     assembly._elements.add(
#         Element(id=[3, 1, 3], frame=Frame.worldXY(), simplex=Point(0, 5, 0), attr={"t": "Beam", "m": 25})
#     )
#     assembly._elements.add(
#         Element(id=[0, 2, 4], frame=Frame.worldXY(), simplex=Point(7, 0, 0), attr={"t": "Block", "m": 25})
#     )
#     assembly._elements.add(
#         Element(id=[1, 0, 3], frame=Frame.worldXY(), simplex=Point(6, 0, 0), attr={"t": "Plate", "m": 40})
#     )
#     assembly._elements.add(
#         Element(id=[2, 2], frame=Frame.worldXY(), simplex=Point(0, 0, 8), attr={"t": "Block", "m": 30})
#     )

#     # get the list of elements, instead of the dictionary (lists of lists with keys)
#     print(assembly._elements.to_flat_list())
#     print(assembly._elements.to_nested_list())
#     print(assembly)
#     print(assembly._elements.to_trimmed_dict("X"))
#     print(assembly._elements.to_trimmed_list(0))

#     # get properties of the elements
#     print(assembly.get_elements_properties("simplex", True))
#     print(assembly.get_elements_properties("simplex", False))

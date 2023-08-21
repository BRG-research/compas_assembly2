from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas.data import Data
from compas.geometry import Frame, Point
from compas_assembly2 import Element
from compas.datastructures import Graph

# https://grantjenks.com/docs/sortedcontainers/sorteddict.html
from compas_assembly2.sortedcontainers.sortedgroup import SortedGroup


class Assembly(Data):
    # ==========================================================================
    # constructor
    # ==========================================================================
    def __init__(self, name=None, elements=None, joints=None, frame=None, **kwargs):
        """
        Initialize an empty ordered dictionary of lists[Element].
        The collection has methods for grouping assembly and selection by attributes.

        A key of the dictionary are the indices of the _elements.
        They can be represented as tuples e.g. (0) or (0, 1) or (1, 5, 9).

        Two _elements can have the same key, even if it is not advised to do so.
        This is why it is an ordered dictionary of lists, not a items.

        Example:
            assembly = Group()
        """

        # --------------------------------------------------------------------------
        # call the inherited Data constructor for json serialization
        # --------------------------------------------------------------------------
        super(Assembly, self).__init__()

        # --------------------------------------------------------------------------
        # declare main properties
        # --------------------------------------------------------------------------
        self._elements = SortedGroup()
        self._joints = SortedGroup()

        # --------------------------------------------------------------------------
        # orientation frames
        # if user does not give a frame, try to define it based on simplex
        # --------------------------------------------------------------------------
        if isinstance(frame, Frame):
            self.frame = Frame.copy(frame)
        else:
            self.frame = Frame([0, 0, 0], [1, 0, 0], [0, 1, 0])

        # assign global frames to elements
        for key, elements in self._elements._objects.items():
            for element in elements:
                element.g_frame = self.frame

        # --------------------------------------------------------------------------
        # declare attributes
        # --------------------------------------------------------------------------
        self.attributes = {"name": name or "Assembly"}
        self.attributes.update(kwargs)

        # --------------------------------------------------------------------------
        # declare graph
        # --------------------------------------------------------------------------
        self.graph = Graph()
        self.graph.update_default_node_attributes(
            {
                "element_name": None,
            }
        )
        self.graph.update_default_edge_attributes(
            {
                "joint_name": None,
            }
        )

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

        for element_list in self._elements._objects.values():
            for element in element_list:
                if hasattr(element, property_name):
                    property_value = getattr(element, property_name)
                    if flatten:
                        elements_properties.extend(property_value)
                    else:
                        elements_properties.append(property_value)

        return elements_properties

    def get_fabrication_data(self, key):
        pass

    def get_structure_data(self, key):
        pass

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
    assembly._elements.add(
        Element(id=[1, 2, 3], frame=Frame.worldXY(), simplex=Point(0, 0, 0), attr={"t": "Block", "m": 30})
    )
    assembly._elements.add(
        Element(id=[1, 2, 3], frame=Frame.worldXY(), simplex=Point(1, 0, 0), attr={"t": "Block", "m": 30})
    )
    assembly._elements.add(
        Element(id=[1, 2, 4], frame=Frame.worldXY(), simplex=Point(1, 0, 0), attr={"t": "Block", "m": 30})
    )
    assembly._elements.add(
        Element(id=[3, 0, 3], frame=Frame.worldXY(), simplex=Point(0, 5, 0), attr={"t": "Beam", "m": 25})
    )
    assembly._elements.add(
        Element(id=[3, 1, 3], frame=Frame.worldXY(), simplex=Point(0, 5, 0), attr={"t": "Beam", "m": 25})
    )
    assembly._elements.add(
        Element(id=[0, 2, 4], frame=Frame.worldXY(), simplex=Point(7, 0, 0), attr={"t": "Block", "m": 25})
    )
    assembly._elements.add(
        Element(id=[1, 0, 3], frame=Frame.worldXY(), simplex=Point(6, 0, 0), attr={"t": "Plate", "m": 40})
    )
    assembly._elements.add(
        Element(id=[2, 2], frame=Frame.worldXY(), simplex=Point(0, 0, 8), attr={"t": "Block", "m": 30})
    )

    # get the list of elements, instead of the dictionary (lists of lists with keys)
    print(assembly._elements.to_flat_list())
    print(assembly._elements.to_nested_list())
    print(assembly)
    print(assembly._elements.to_trimmed_dict("X"))
    print(assembly._elements.to_trimmed_list(0))

    # get properties of the elements
    print(assembly.get_elements_properties("simplex", True))
    print(assembly.get_elements_properties("simplex", False))

from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas.data import Data
from compas.geometry import Frame, Point
from compas_assembly2 import Element
from compas.datastructures import Graph

# https://grantjenks.com/docs/sortedcontainers/sorteddict.html
from compas_assembly2.sortedcontainers.sorteddict import SortedDict


class Assembly(Data):
    # ==========================================================================
    # constructor
    # ==========================================================================
    def __init__(self, name=None, elements=None, joints=None, frame=None, **kwargs):
        """
        Initialize an empty ordered dictionary of lists[Element].
        The collection has methods for grouping group_elements and selection by attributes.

        A key of the dictionary are the indices of the _elements.
        They can be represented as tuples e.g. (0) or (0, 1) or (1, 5, 9).

        Two _elements can have the same key, even if it is not advised to do so.
        This is why it is an ordered dictionary of lists, not a items.

        Example:
            group_elements = Group()
        """

        # --------------------------------------------------------------------------
        # call the inherited Data constructor for json serialization
        # --------------------------------------------------------------------------
        super(Assembly, self).__init__()

        # --------------------------------------------------------------------------
        # declare main properties
        # --------------------------------------------------------------------------
        self._elements = SortedDict()
        self._joints = SortedDict()

        # --------------------------------------------------------------------------
        # orientation frames
        # if user does not give a frame, try to define it based on simplex
        # --------------------------------------------------------------------------
        if isinstance(frame, Frame):
            self.frame = Frame.copy(frame)
        else:
            self.frame = Frame([0, 0, 0], [1, 0, 0], [0, 1, 0])

        # assign global frames to elements
        for key, elements in self._elements.items():
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

    # ==========================================================================
    # properties - operator overload [] and []=
    # ==========================================================================
    def __getitem__(self, *args):
        """
        Get the list of Element objects associated with the given key (id).

        Parameters:
            *args: The integers that make up the key to access the _elements.

        Returns:
            list: The list of Element objects associated with the given key.

        Raises:
            KeyError: If the key is not found in the _elements dictionary.

        Example:
            group_elements.add(Element(id=(1, 2, 3), l_frame=None, g_frame=None, attr={'t': 'Block', 'm': 30}))
            group_elements.add(Element(id=(1, 3, 5), l_frame=None, g_frame=None, attr={'t': 'Beam', 'm': 25}))

            result = group_elements[1, 2, 3]
            print(result)  # Output: [Element1]
        """
        # --------------------------------------------------------------------------
        # elements by index
        # --------------------------------------------------------------------------
        key_tuple = args[0]
        group_elements = []
        for key in self._elements.keys():
            if key == key_tuple:  # [: len(key_tuple)]
                group_elements.extend(self._elements[key])
        return group_elements

    def __setitem__(self, *args, element):
        """
        Set the value associated with the given key (id).

        Parameters:
            *args: The integers that make up the key to set the _elements.
            element (Element): The Element object to be associated with the given key.

        Raises:
            TypeError: If the element is not an instance of the Element class.

        Example:
            element1 = Element(id=(1, 2, 3), l_frame=None, g_frame=None, attr={'t': 'Block', 'm': 30})
            element2 = Element(id=(1, 3, 5), l_frame=None, g_frame=None, attr={'t': 'Beam', 'm': 25})

            group_elements[1, 2, 3] = element1
            group_elements[1, 3, 5] = element2
        """
        key_tuple = tuple(args)
        if not isinstance(element, list):
            raise TypeError("Value must be a list of Element objects.")
        self._elements[key_tuple] = element

    # ==========================================================================
    # properties - collection properties
    # ==========================================================================

    def __repr__(self):
        """
        Return a string representation of the ordered multi-key list.

        Returns:
            str: The string representation of the ordered multi-key list.

        Example:
            group_elements.add(Element(id=(1, 2, 3), l_frame=None, g_frame=None, attr={'t': 'Block', 'm': 30}))
            group_elements.add(Element(id=(1, 3, 5), l_frame=None, g_frame=None, attr={'t': 'Beam', 'm': 25}))

            print(group_elements)  # Output: [(1, 2, 3), (1, 3, 5)]
        """
        # print elements per key
        message = "________________________Group_________________________\n"
        for key, items in self._elements.items():
            message += str(key) + ": " + str(items) + "\n"
        message += "______________________________________________________\n"
        return message

    def is_empty(self):
        """
        Add multiple group_elements to the Group object.

        Parameters:
            *group_elements (Element): One or more Element objects to add.

        Example:
            element1 = Element(id=(1, 2, 3), l_frame=None, g_frame=None, attr={'t': 'Block', 'm': 30})
            element2 = Element(id=(1, 3, 5), l_frame=None, g_frame=None, attr={'t': 'Beam', 'm': 25})

            group_elements.add_range(element1, element2)
        """
        return len(self._elements) == 0

    def size(self):
        """
        Get the number of _elements in the ordered multi-key list.

        Returns:
            int: The number of _elements in the ordered multi-key list.

        Example:
            group_elements.size()  # Output: 0

            group_elements.add(Element(id=(1, 2, 3), l_frame=None, g_frame=None, attr={'t': 'Block', 'm': 30}))
            group_elements.add(Element(id=(1, 3, 5), l_frame=None, g_frame=None, attr={'t': 'Beam', 'm': 25}))

            group_elements.size()  # Output: 2
        """
        return len(self._elements)

    def get_by_key(self, key):
        """
        Get the element(s) with the specified key.

        Parameters:
            key (str): The t of the key to search for.

        Returns:
            List[Element]: A list of Element objects that match the specified key and value.

        Example:
            group_elements.add(Element(id=(1, 2, 3), l_frame=None, g_frame=None, attr={'t': 'Block', 'm': 30}))
            group_elements.add(Element(id=(1, 3, 5), l_frame=None, g_frame=None, attr={'t': 'Beam', 'm': 25}))

            result = group_elements.get_by_key('t')
            print(result)  # Output: [Element1, Element2]
        """
        return [element.value for element in self._elements if key in element.attr]

    def get_elements_properties(self, property_name, flatten=True):
        """Get properties of elements flattened (True) or in nested lists (False)."""
        elements_properties = []

        for element_list in self._elements.values():
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
    # collections - add methods
    # ==========================================================================

    def add(self, element):
        """
        Add an element with multiple keys to the ordered multi-key list.
        If an element already exists with the same id, it will be appended to the list of _elements.

        Parameters:
            element (Element): An Element Data-Structure.

        Example:
            element1 = Element(id=(1, 2, 3), l_frame=None, g_frame=None, attr={'t': 'Block', 'm': 30})
            element2 = Element(id=(1, 3, 5), l_frame=None, g_frame=None, attr={'t': 'Beam', 'm': 25})

            group_elements.add(element1)
            group_elements.add(element2)
        """

        if tuple(element.id) in self._elements:
            self._elements[tuple(element.id)].append(element)
        else:
            self._elements[tuple(element.id)] = [element]

    def merge(self, other_elements):
        """
        Merge the current Group object with another Group object.

        Parameters:
            other_elements (Group): The Group object to merge with.

        Returns:
            Group: A new Group object containing the merged group_elements.

        Note:
            The original Group objects remain unchanged. The merged group_elements are
            added to a new Group object that is returned as the result.

        Example:
            elements1 = Group()
            elements1.add(Element(id=(1, 2, 3), l_frame=None, g_frame=None, attr={'t': 'Block', 'm': 30}))
            elements1.add(Element(id=(1, 3, 5), l_frame=None, g_frame=None, attr={'t': 'Beam', 'm': 25}))

            elements2 = Group()
            elements2.add(Element(id=(1, 3, 8), l_frame=None, g_frame=None, attr={'t': 'Plate', 'm': 40}))
            elements2.add(Element(id=(1, 2, 8), l_frame=None, g_frame=None, attr={'t': 'Block', 'm': 30}))

            merged_elements = elements1.merge(elements2)
            print(merged_elements.size())  # Output: 4
        """
        merged_elements = Group()

        for elements_dict in [self._elements, other_elements._elements]:
            for key, values in elements_dict.items():
                for element in values:
                    merged_elements.add(element)

        return merged_elements

    def add_range(self, *group_elements):
        """
        Add multiple group_elements to the Group object.

        Parameters:
            *group_elements (Element): One or more Element objects to add.

        Example:
            element1 = Element(id=(1, 2, 3), l_frame=None, g_frame=None, attr={'t': 'Block', 'm': 30})
            element2 = Element(id=(1, 3, 5), l_frame=None, g_frame=None, attr={'t': 'Beam', 'm': 25})

            group_elements.add_range(element1, element2)
        """
        for element in group_elements:
            self.add(element)

    def to_flat_list(self):
        """A list of elements in a sorted way following the SortedDictionary"""
        elements_as_list = []

        for element_list in self._elements.values():
            elements_as_list.extend(element_list)

        return elements_as_list

    def to_nested_list(self):
        """Lists for each key of the dictionary"""
        elements_as_list = []

        for element_list in self._elements.values():
            elements_as_list.append(element_list)

        return elements_as_list

    def to_trimmed_dict(self, *args):
        """Trim dictionary by given how many positions have to be kept"""
        new_dict = SortedDict()
        for key, items in self._elements.items():
            length = min(len(key), len(args))
            indices = key[:length]
            new_key = tuple(indices)
            if new_key not in new_dict:
                new_dict[new_key] = []
            new_dict[new_key].extend(items)
        self._elements = new_dict

        return self

    def to_trimmed_list(self, *args):
        """Trim list by given how many positions have to be kept"""

        # create a new dictionary
        new_dict = SortedDict()
        for key, items in self._elements.items():
            length = min(len(key), len(args))
            indices = key[:length]
            new_key = tuple(indices)
            if new_key not in new_dict:
                new_dict[new_key] = []
            new_dict[new_key].extend(items)
        self._elements = new_dict

        # get lists from dictionary
        elements_as_list = []
        for element_list in new_dict.values():
            elements_as_list.append(element_list)

        return elements_as_list

    # ==========================================================================
    # collections - remove methods
    # ==========================================================================

    def remove_by_element(self, element):
        """
        Remove an element from the ordered multi-key list if it exists.

        Parameters:
            element (Element): The element to remove from the ordered multi-key list.

        Example:
            element1 = Element(id=(1, 2, 3), l_frame=None, g_frame=None, attr={'t': 'Block', 'm': 30})
            group_elements.add(element1)

            group_elements.remove_by_element(element1)
        """
        if element in self._elements:
            id = element.id
            self._elements[id].remove(element)
            if not self._elements[id]:
                del self._elements[id]

    def remove_by_id(self, id=None):
        """
        Remove and return the element at the specified id or the last element if id is not provided.

        Parameters:
            id (int, optional): The id of the element to remove.
                                   If not provided, the last element will be removed.

        Returns:
            Element: The removed element.

        Example:
            group_elements.add(Element(id=(1, 2, 3), l_frame=None, g_frame=None, attr={'t': 'Block', 'm': 30}))
            group_elements.add(Element(id=(1, 3, 5), l_frame=None, g_frame=None, attr={'t': 'Beam', 'm': 25}))

            removed_element = group_elements.remove_by_id(0)
            print(removed_element)  # Output: (1, 2, 3)
        """
        if id is None:
            return self._elements.popitem()[0]  # Remove and return the last element
        if 0 <= id < len(self._elements):
            return list(self._elements.keys())[id]
        raise IndexError("Index out of range")

    def remove_by_key(self, key):
        """
        Remove and return the element at the specified id or the last element if id is not provided.

        Parameters:
            id (int, optional): The id of the element to remove.
                                   If not provided, the last element will be removed.

        Returns:
            Element: The removed element.

        Example:
            group_elements.add(Element(id=(1, 2, 3), l_frame=None, g_frame=None, attr={'t': 'Block', 'm': 30}))
            group_elements.add(Element(id=(1, 3, 5), l_frame=None, g_frame=None, attr={'t': 'Beam', 'm': 25}))

            removed_element = group_elements.remove_by_id(0)
            print(removed_element)  # Output: (1, 2, 3)
        """
        _elements_to_remove = [element for element in self._elements if key in element.attr]
        for element in _elements_to_remove:
            del self._elements[element]

    # ==========================================================================
    # collections - iterators
    # ==========================================================================
    def __iter__(self):
        """
        Return an iterator over the keys of the _elements.

        Returns:
            iterator: An iterator over the keys.

        Example:
            group_elements.add(Element(id=(1, 2, 3), l_frame=None, g_frame=None, attr={'t': 'Block', 'm': 30}))
            group_elements.add(Element(id=(1, 3, 5), l_frame=None, g_frame=None, attr={'t': 'Beam', 'm': 25}))

            for key in group_elements:
                print(key)  # Output: (1, 2, 3), (1, 3, 5)
        """
        return iter(self._elements)

    # ==========================================================================
    # collections - partitioning methods
    # ==========================================================================

    def regroup_by_keeping_first_indices(self, num_indices_to_keep):
        """
        Regroup the ordered dictionary _elements by keeping the first N indices of each key.

        Parameters:
            num_indices_to_keep (int): The number of indices to keep in the regrouped keys.

        Example:
            group_elements.add(Element(id=(1, 2, 3), l_frame=None, g_frame=None, attr={'t': 'Block', 'm': 30}))
            group_elements.add(Element(id=(1, 2, 4), l_frame=None, g_frame=None, attr={'t': 'Beam', 'm': 25}))
            group_elements.add(Element(id=(1, 3, 5), l_frame=None, g_frame=None, attr={'t': 'Plate', 'm': 40}))

            group_elements.regroup_after_keeping_first_indices(2)

        Result:
            # Before regrouping: {(1, 2, 3): [Element1], (1, 2, 4): [Element2], (1, 3, 5): [Element3]}
            # After regrouping: {(1, 2): [Element1, Element2], (1, 3): [Element3]}
        """
        new__elements = SortedDict()  # ignore
        for key, value in self._elements.items():
            if len(key) >= num_indices_to_keep:
                new_key = key[:num_indices_to_keep]
                new__elements.setdefault(new_key, []).append(value)
        return new__elements

    def regroup_by_key(self, key_t):
        """
        Regroup the ordered dictionary _elements into a dictionary by a specific key.

        Parameters:
            key_t (str): The t of the key by which _elements should be regrouped.

        Returns:
            dict: A dictionary with the specified key as the key and a list of _elements with that key as the value.

        Example:
            group_elements.add(Element(id=(1, 2, 3), l_frame=None, g_frame=None, attr={'t': 'Block', 'm': 30}))
            group_elements.add(Element(id=(1, 3, 5), l_frame=None, g_frame=None, attr={'t': 'Beam', 'm': 25}))

            group_elements.regroup_by_key('t')

        Result:
            {'Block': [Element1], 'Beam': [Element2]}
        """
        grouped_dict = SortedDict()

        # Check if the key is present in all _elements
        for element_list in self._elements.values():
            for element in element_list:
                if key_t not in element.keys:
                    raise ValueError(f"The key '{key_t}' is not present in all _elements.")

        # Group _elements based on the specified key
        for element_list in self._elements.values():
            for element in element_list:
                key_value = element.keys[key_t]
                if key_value not in grouped_dict:
                    grouped_dict[key_value] = []
                grouped_dict[key_value].append(element)

        return grouped_dict

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
    group_elements = Assembly()
    group_elements.add(
        Element(id=[1, 2, 3], frame=Frame.worldXY(), simplex=Point(0, 0, 0), attr={"t": "Block", "m": 30})
    )
    group_elements.add(
        Element(id=[1, 2, 3], frame=Frame.worldXY(), simplex=Point(1, 0, 0), attr={"t": "Block", "m": 30})
    )
    group_elements.add(
        Element(id=[1, 2, 4], frame=Frame.worldXY(), simplex=Point(1, 0, 0), attr={"t": "Block", "m": 30})
    )
    group_elements.add(
        Element(id=[3, 0, 3], frame=Frame.worldXY(), simplex=Point(0, 5, 0), attr={"t": "Beam", "m": 25})
    )
    group_elements.add(
        Element(id=[3, 1, 3], frame=Frame.worldXY(), simplex=Point(0, 5, 0), attr={"t": "Beam", "m": 25})
    )
    group_elements.add(
        Element(id=[0, 2, 4], frame=Frame.worldXY(), simplex=Point(7, 0, 0), attr={"t": "Block", "m": 25})
    )
    group_elements.add(
        Element(id=[1, 0, 3], frame=Frame.worldXY(), simplex=Point(6, 0, 0), attr={"t": "Plate", "m": 40})
    )
    group_elements.add(Element(id=[2, 2], frame=Frame.worldXY(), simplex=Point(0, 0, 8), attr={"t": "Block", "m": 30}))

    # get the list of elements, instead of the dictionary (lists of lists with keys)
    print(group_elements.to_flat_list())
    print(group_elements.to_nested_list())
    print(group_elements)
    print(group_elements.to_trimmed_dict("X"))
    print(group_elements.to_trimmed_list(0))

    # get properties of the elements
    print(group_elements.get_elements_properties("simplex", True))
    print(group_elements.get_elements_properties("simplex", False))

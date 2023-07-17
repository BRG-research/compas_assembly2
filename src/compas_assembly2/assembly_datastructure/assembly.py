from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas.datastructures import Datastructure
from group import Group


class Assembly(Datastructure):

    def __init__(self, name=None, **kwargs):
        super(Assembly, self).__init__()
        self.attributes = {"name": name or "Assembly"}
        self.attributes.update(kwargs)

        # two collections of elements and joints that has
        # indices for groupînt
        # and keys for selectin
        self.elements_group = Group()
        self.joints_group = Group()


# class Assembly(Datastructure):
#     """A data structure for managing the connections between different elements of an assembly.
#     The assembly contains a) elements, b) connections, c) groups.
#     The elements follows structural names such as a beam, a block or a plate.
#     The connections are used to track connectivity between elements with attributes.
#     The groups stores information about sub-sets of assembly elements.


#     Parameters
#     ----------
#     elements : OrderedDict
#         A dictionary of elements, with the key being the element's index and the value being the element itself.
#     joints : list
#         A list of joints
#     groups : list
#     name : str, optional
#         The name of the assembly.

#     Attributes
#     ----------
#     attributes : dict[str, Any]
#         General attributes of the data structure that will be included in the data dict and serialization.
#     graph : :class:`~compas.datastructures.Graph`
#         The graph that is used under the hood to store the parts and their connections.


#     """

#     def __init__(self, elements=None, joints=None, groups=None, name=None, **kwargs):

#         # default constructor of the inherited Datastructure class
#         super(Assembly, self).__init__()
#         self.attributes = {"name": name or "Assembly"}
#         self.attributes.update(kwargs)

#         # main paramenters
#         self.elements = OrderedDict() if elements is None else elements
#         self.joints = [] if joints is None else joints
#         self.groups = [] if groups is None else groups

#         # parameters that can be ignored


#     # ==========================================================================
#     # properties
#     # ==========================================================================

#     @property
#     def name(self):
#         return self.attributes.get("name") or self.__class__.__name__

#     @name.setter
#     def name(self, value):
#         self.attributes["name"] = value

#     # ==========================================================================
#     # customization
#     # ==========================================================================

#     def __str__(self):
#         tpl = "<Assembly with {} elements and {} joints>"
#         return tpl.format(len(self.elements), len(self.joints))

#     # ==========================================================================
#     # collection properties
#     # ==========================================================================
#     def _is_valid_tuple_of_integers(self, key):
#         """
#         Check if the input is a valid tuple of integers.

#         Parameters:
#             key (tuple): The input tuple to be checked.

#         Returns:
#             bool: True if the input is a tuple of integers, False otherwise.
#         """
#         if isinstance(key, tuple):
#             return all(isinstance(item, int) for item in key)
#         return False

#     def add_element(self, key, obj):
#         """
#         Add an element to the collection with a given key.
#         If the key already exists, it will replace the existing element.

#         Parameters:
#             key (tuple): The key to be used for indexing the element.
#             obj (any): The element to be added to the collection.
#         """
#         if self._is_valid_tuple_of_integers(key):
#             self.collection[key] = obj
#         else:
#             raise ValueError("Invalid input: Please enter a valid tuple of integers.")

#     def remove_element(self, key):
#         """
#         Remove an element from the collection based on the provided key.

#         Parameters:
#             key (tuple): The key used to identify the element to be removed.

#         Raises:
#             KeyError: If the key does not exist in the collection.
#         """
#         del self.collection[key]

#     def get_element(self, key):
#         """
#         Retrieve an element from the collection based on the provided key.

#         Parameters:
#             key (tuple): The key used to retrieve the element.

#         Returns:
#             any: The element corresponding to the given key.

#         Raises:
#             KeyError: If the key does not exist in the collection.
#         """
#         return self.collection[key]

#     def get_elements_sorted(self):
#         """
#         Retrieve a list of elements from the collection, sorted by their keys.

#         Returns:
#             list: A list of elements, sorted by the keys.
#         """
#         return list(self.collection.values())

#     def get_element_keys(self):
#         """
#         Retrieve a list of keys from the collection, sorted in ascending order.

#         Returns:
#             list: A list of keys, sorted in ascending order.
#         """
#         return list(self.collection.keys())

#     def get_element_values(self):
#         """
#         Retrieve all values from the collection.

#         Returns:
#             list: A list of all the values stored in the collection.
#         """
#         return list(self.collection.values())

#     def __len__(self):
#         """
#         Get the number of elements in the collection.

#         Returns:
#             int: The number of elements in the collection.
#         """
#         return len(self.collection)

#     def __repr__(self):
#         """
#         Get the string representation of the collection.

#         Returns:
#             str: The string representation of the collection.
#         """
#         return f"SortedIndexedKeyedCollection({self.collection})"

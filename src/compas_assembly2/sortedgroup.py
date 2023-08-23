from compas_assembly2.sorteddict import SortedDict


class SortedGroup:
    def __init__(self, objects=None):
        self._objects = SortedDict()
        if objects:
            self.add_range(objects)

    # ==========================================================================
    # properties - operator overload [] and []=
    # ==========================================================================
    def __getitem__(self, *args):
        """
        Get the list of Element objects associated with the given key (id).

        Parameters:
            *args: The integers that make up the key to access the _objects.

        Returns:
            list: The list of Element objects associated with the given key.

        Raises:
            KeyError: If the key is not found in the _objects dictionary.

        Example:
            group_objects.add(Element(id=(1, 2, 3), l_frame=None, g_frame=None, attr={'t': 'Block', 'm': 30}))
            group_objects.add(Element(id=(1, 3, 5), l_frame=None, g_frame=None, attr={'t': 'Beam', 'm': 25}))

            result = group_objects[1, 2, 3]
            print(result)  # Output: [Element1]
        """
        # --------------------------------------------------------------------------
        # elements by index
        # --------------------------------------------------------------------------
        key_tuple = args[0]
        if isinstance(key_tuple, list):
            key_tuple = tuple(key_tuple)

        # group_objects = []

        # for key in self._objects.keys():
        #     print(key)
        #     if key == key_tuple:  # [: len(key_tuple)]
        #         group_objects.extend(self._objects[key])
        return self._objects[key_tuple]

    def __setitem__(self, args, obj):
        """
        Set the value associated with the given key (id).

        Parameters:
            *args: The integers that make up the key to set the _objects.
            obj (Element): The Element object to be associated with the given key.

        Raises:
            TypeError: If the obj is not an instance of the Element class.

        Example:
            element1 = Element(id=(1, 2, 3), l_frame=None, g_frame=None, attr={'t': 'Block', 'm': 30})
            element2 = Element(id=(1, 3, 5), l_frame=None, g_frame=None, attr={'t': 'Beam', 'm': 25})

            group_objects[1, 2, 3] = element1
            group_objects[1, 3, 5] = element2
        """
        key_tuple = args  # tuple(args)
        if not isinstance(obj, list):
            raise TypeError("Value must be a list of Element objects.")
        self._objects[key_tuple] = obj

    # ==========================================================================
    # properties - collection properties
    # ==========================================================================

    def __repr__(self):
        """
        Return a string representation of the ordered multi-key list.

        Returns:
            str: The string representation of the ordered multi-key list.

        Example:
            group_objects.add(Element(id=(1, 2, 3), l_frame=None, g_frame=None, attr={'t': 'Block', 'm': 30}))
            group_objects.add(Element(id=(1, 3, 5), l_frame=None, g_frame=None, attr={'t': 'Beam', 'm': 25}))

            print(group_objects)  # Output: [(1, 2, 3), (1, 3, 5)]
        """
        # print elements per key
        message = "________________________Group_________________________\n"
        for key, items in self._objects.items():
            message += str(key) + ": " + str(items) + "\n"
        message += "______________________________________________________\n"
        return message

    def is_empty(self):
        """
        Add multiple group_objects to the Group object.

        Parameters:
            *group_objects (Element): One or more Element objects to add.

        Example:
            element1 = Element(id=(1, 2, 3), l_frame=None, g_frame=None, attr={'t': 'Block', 'm': 30})
            element2 = Element(id=(1, 3, 5), l_frame=None, g_frame=None, attr={'t': 'Beam', 'm': 25})

            group_objects.add_range(element1, element2)
        """
        return len(self._objects) == 0

    def size(self):
        """
        Get the number of _objects in the ordered multi-key list.

        Returns:
            int: The number of _objects in the ordered multi-key list.

        Example:
            group_objects.size()  # Output: 0

            group_objects.add(Element(id=(1, 2, 3), l_frame=None, g_frame=None, attr={'t': 'Block', 'm': 30}))
            group_objects.add(Element(id=(1, 3, 5), l_frame=None, g_frame=None, attr={'t': 'Beam', 'm': 25}))

            group_objects.size()  # Output: 2
        """
        return len(self._objects)

    def add(self, obj):
        """
        Add an obj with multiple keys to the ordered multi-key list.
        If an obj already exists with the same id, it will be appended to the list of _elements.

        Parameters:
            obj (Element): An Element Data-Structure.

        Example:
            element1 = Element(id=(1, 2, 3), l_frame=None, g_frame=None, attr={'t': 'Block', 'm': 30})
            element2 = Element(id=(1, 3, 5), l_frame=None, g_frame=None, attr={'t': 'Beam', 'm': 25})

            group_elements.add(element1)
            group_elements.add(element2)
        """

        if tuple(obj.id) in self._objects:
            self._objects[tuple(obj.id)].append(obj)
        else:
            self._objects[tuple(obj.id)] = [obj]

    def merge(self, other_objects):
        """
        Merge the current Group object with another Group object.

        Parameters:
            other_objects (Group): The Group object to merge with.

        Returns:
            Group: A new Group object containing the merged group_objects.

        Note:
            The original Group objects remain unchanged. The merged group_objects are
            added to a new Group object that is returned as the result.

        Example:
            elements1 = Group()
            elements1.add(Element(id=(1, 2, 3), l_frame=None, g_frame=None, attr={'t': 'Block', 'm': 30}))
            elements1.add(Element(id=(1, 3, 5), l_frame=None, g_frame=None, attr={'t': 'Beam', 'm': 25}))

            elements2 = Group()
            elements2.add(Element(id=(1, 3, 8), l_frame=None, g_frame=None, attr={'t': 'Plate', 'm': 40}))
            elements2.add(Element(id=(1, 2, 8), l_frame=None, g_frame=None, attr={'t': 'Block', 'm': 30}))

            merged_objects = elements1.merge(elements2)
            print(merged_objects.size())  # Output: 4
        """
        merged_objects = SortedGroup()

        for elements_dict in [self._objects, other_objects._objects]:
            for key, values in elements_dict.items():
                for obj in values:
                    merged_objects.add(obj)

        return merged_objects

    def add_range(self, group_objects):
        """
        Add multiple group_objects to the Group object.

        Parameters:
            *group_objects (Element): One or more Element objects to add.

        Example:
            element1 = Element(id=(1, 2, 3), l_frame=None, g_frame=None, attr={'t': 'Block', 'm': 30})
            element2 = Element(id=(1, 3, 5), l_frame=None, g_frame=None, attr={'t': 'Beam', 'm': 25})

            group_objects.add_range(element1, element2)
        """
        for obj in group_objects:
            self.add(obj)

    def to_flat_list(self):
        """A list of elements in a sorted way following the SortedDictionary"""
        elements_as_list = []

        for element_list in self._objects.values():
            elements_as_list.extend(element_list)

        return elements_as_list

    def to_nested_list(self):
        """Lists for each key of the dictionary"""
        elements_as_list = []

        for element_list in self._objects.values():
            elements_as_list.append(element_list)

        return elements_as_list

    def to_trimmed_dict(self, *args):
        """Trim dictionary by given how many positions have to be kept"""
        new_dict = SortedDict()
        for key, items in self._objects.items():
            length = min(len(key), len(args))
            indices = key[:length]
            new_key = tuple(indices)
            if new_key not in new_dict:
                new_dict[new_key] = []
            new_dict[new_key].extend(items)
        self._objects = new_dict

        return self

    def to_trimmed_list(self, *args):
        """Trim list by given how many positions have to be kept"""

        # create a new dictionary
        new_dict = SortedDict()
        for key, items in self._objects.items():
            length = min(len(key), len(args))
            indices = key[:length]
            new_key = tuple(indices)
            if new_key not in new_dict:
                new_dict[new_key] = []
            new_dict[new_key].extend(items)
        self._objects = new_dict

        # get lists from dictionary
        elements_as_list = []
        for element_list in new_dict.values():
            elements_as_list.append(element_list)

        return elements_as_list

    # ==========================================================================
    # collections - remove methods
    # ==========================================================================

    def remove_by_element(self, obj):
        """
        Remove an obj from the ordered multi-key list if it exists.

        Parameters:
            obj (Element): The obj to remove from the ordered multi-key list.

        Example:
            element1 = Element(id=(1, 2, 3), l_frame=None, g_frame=None, attr={'t': 'Block', 'm': 30})
            group_objects.add(element1)

            group_objects.remove_by_element(element1)
        """
        if obj in self._objects:
            id = obj.id
            self._objects[id].remove(obj)
            if not self._objects[id]:
                del self._objects[id]

    def remove_by_id(self, id=None):
        """
        Remove and return the obj at the specified id or the last obj if id is not provided.

        Parameters:
            id (int, optional): The id of the obj to remove.
                                   If not provided, the last obj will be removed.

        Returns:
            Element: The removed obj.

        Example:
            group_objects.add(Element(id=(1, 2, 3), l_frame=None, g_frame=None, attr={'t': 'Block', 'm': 30}))
            group_objects.add(Element(id=(1, 3, 5), l_frame=None, g_frame=None, attr={'t': 'Beam', 'm': 25}))

            removed_element = group_objects.remove_by_id(0)
            print(removed_element)  # Output: (1, 2, 3)
        """
        if id is None:
            return self._objects.popitem()[0]  # Remove and return the last obj
        if 0 <= id < len(self._objects):
            return list(self._objects.keys())[id]
        raise IndexError("Index out of range")

    def remove_by_key(self, key):
        """
        Remove and return the obj at the specified id or the last obj if id is not provided.

        Parameters:
            id (int, optional): The id of the obj to remove.
                                   If not provided, the last obj will be removed.

        Returns:
            Element: The removed obj.

        Example:
            group_objects.add(Element(id=(1, 2, 3), l_frame=None, g_frame=None, attr={'t': 'Block', 'm': 30}))
            group_objects.add(Element(id=(1, 3, 5), l_frame=None, g_frame=None, attr={'t': 'Beam', 'm': 25}))

            removed_element = group_objects.remove_by_id(0)
            print(removed_element)  # Output: (1, 2, 3)
        """
        _objects_to_remove = [obj for obj in self._objects if key in obj.attr]
        for obj in _objects_to_remove:
            del self._objects[obj]

    # ==========================================================================
    # collections - iterators
    # ==========================================================================
    def __iter__(self):
        """
        Return an iterator over the keys of the _objects.

        Returns:
            iterator: An iterator over the keys.

        Example:
            group_objects.add(Element(id=(1, 2, 3), l_frame=None, g_frame=None, attr={'t': 'Block', 'm': 30}))
            group_objects.add(Element(id=(1, 3, 5), l_frame=None, g_frame=None, attr={'t': 'Beam', 'm': 25}))

            for key in group_objects:
                print(key)  # Output: (1, 2, 3), (1, 3, 5)
        """
        return iter(self._objects)

    # ==========================================================================
    # collections - partitioning methods
    # ==========================================================================

    def regroup_by_keeping_first_indices(self, num_indices_to_keep):
        """
        Regroup the ordered dictionary _objects by keeping the first N indices of each key.

        Parameters:
            num_indices_to_keep (int): The number of indices to keep in the regrouped keys.

        Example:
            group_objects.add(Element(id=(1, 2, 3), l_frame=None, g_frame=None, attr={'t': 'Block', 'm': 30}))
            group_objects.add(Element(id=(1, 2, 4), l_frame=None, g_frame=None, attr={'t': 'Beam', 'm': 25}))
            group_objects.add(Element(id=(1, 3, 5), l_frame=None, g_frame=None, attr={'t': 'Plate', 'm': 40}))

            group_objects.regroup_after_keeping_first_indices(2)

        Result:
            # Before regrouping: {(1, 2, 3): [Element1], (1, 2, 4): [Element2], (1, 3, 5): [Element3]}
            # After regrouping: {(1, 2): [Element1, Element2], (1, 3): [Element3]}
        """
        new__objects = SortedDict()  # ignore
        for key, value in self._objects.items():
            if len(key) >= num_indices_to_keep:
                new_key = key[:num_indices_to_keep]
                new__objects.setdefault(new_key, []).append(value)
        return new__objects

    def regroup_by_key(self, key_t):
        """
        Regroup the ordered dictionary _objects into a dictionary by a specific key.

        Parameters:
            key_t (str): The t of the key by which _objects should be regrouped.

        Returns:
            dict: A dictionary with the specified key as the key and a list of _objects with that key as the value.

        Example:
            group_objects.add(Element(id=(1, 2, 3), l_frame=None, g_frame=None, attr={'t': 'Block', 'm': 30}))
            group_objects.add(Element(id=(1, 3, 5), l_frame=None, g_frame=None, attr={'t': 'Beam', 'm': 25}))

            group_objects.regroup_by_key('t')

        Result:
            {'Block': [Element1], 'Beam': [Element2]}
        """
        grouped_dict = SortedDict()

        # Check if the key is present in all _objects
        for element_list in self._objects.values():
            for obj in element_list:
                if key_t not in obj.keys:
                    raise ValueError("The key '{}' is not present in all _objects.".format(key_t))

        # Group _objects based on the specified key
        for element_list in self._objects.values():
            for obj in element_list:
                key_value = obj.keys[key_t]
                if key_value not in grouped_dict:
                    grouped_dict[key_value] = []
                grouped_dict[key_value].append(obj)

        return grouped_dict

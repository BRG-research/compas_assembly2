from compas_assembly2 import Assembly, Element
from compas.geometry import Frame, Point
import pytest


@pytest.fixture
def setup_assemblies():
    # Create an empty assembly and add an element by index
    assembly_1 = Assembly(name="b")
    assembly_1._allow_duplicate_assembly_names = False
    assembly_1.add_element_by_index(
        Element(id=[1, 2, 3], frame=Frame.worldXY(), simplex=Point(0, 0, 0), attr={"t": "Block", "m": 30})
    )

    assembly_2 = Assembly(name="b")
    assembly_2._allow_duplicate_assembly_names = False
    assembly_2.add_element_by_index(
        Element(id=[1, 3, 3], frame=Frame.worldXY(), simplex=Point(0, 0, 0), attr={"t": "Block", "m": 30})
    )

    # Create another empty assembly and add the previous assembly to this assembly
    assembly_0 = Assembly(name="a")
    assembly_0._allow_duplicate_assembly_names = False
    assembly_0.add_assembly(assembly_1)
    assembly_0.merge_assemblies(assembly_2)

    return assembly_0


def test_add_element_by_index_two_times(setup_assemblies):
    assembly_0 = setup_assemblies
    

    # Print the result (for debugging purposes)
    assembly_0.print_elements()

    # Assertions
    # assert assembly_0.number_of_elements == 2


if __name__ == "__main__":
    pytest.main([__file__, "-s"])



# ==============================================================================
# Example Usage:
# ==============================================================================



# this assembly has already nested assemblies by index

# assembly_1.add_element(
#     Element(id=[1, 2, 3], frame=Frame.worldXY(), simplex=Point(0, 0, 0), attr={"t": "Block", "m": 30})
# )


# assembly_1.print_elements()
# print(assembly_1._assembly_childs[0]._assembly_childs[0]._assembly_childs[0]._level)
# if you add this assembly to another assembly


# # assembly.add_element_by_index(
# #     Element(id=[1, 2, 3], frame=Frame.worldXY(), simplex=Point(1, 0, 0), attr={"t": "Block", "m": 30})
# # )assembly_0.print_elements()setup_assemblies
# assembly.add_element_by_index(
#     Element(id=[3, 1, 3], frame=Frame.worldXY(), simplex=Point(0, 5, 0), attr={"t": "Beam", "m": 25})
# )
# assembly.add_element_by_index(
#     Element(id=[0, 2, 4], frame=Frame.worldXY(), simplex=Point(7, 0, 0), attr={"t": "Block", "m": 25})
# )
# assembly.add_element_by_index(
#     Element(id=[1, 0, 3], frame=Frame.worldXY(), simplex=Point(6, 0, 0), attr={"t": "Plate", "m": 40})
# )queue = list(self._assembly_childs)
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

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

    assembly_1.add_element_by_index(
        Element(id=[1, 2, 3], frame=Frame.worldXY(), simplex=Point(0, 0, 0), attr={"t": "Block", "m": 30})
    )
    assembly_1.add_element_by_index(
        Element(id=[1, 2, 4], frame=Frame.worldXY(), simplex=Point(0, 0, 0), attr={"t": "Block", "m": 30})
    )

    assembly_1.add_element_by_index(
        Element(id=[1, 2, 3, 4], frame=Frame.worldXY(), simplex=Point(0, 0, 0), attr={"t": "Block", "m": 30})
    )

    return assembly_1


def test_add_element_by_index_two_times(setup_assemblies):
    assembly_0 = setup_assemblies
    

    # Print the result (for debugging purposes)
    assembly_0.print_elements()

    # Assertions
    # assert assembly_0.number_of_elements == 2


if __name__ == "__main__":
    pytest.main([__file__, "-s"])

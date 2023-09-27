from compas_assembly2 import Assembly, Element
from compas.geometry import Frame, Point
import pytest


@pytest.fixture
def setup_assemblies():
    # Create an empty assembly and add an element by index
    assembly_1 = Assembly(value="b")
    assembly_1.add_by_index(
        Element(id=[1, 2, 3], frame=Frame.worldXY(), simplex=Point(0, 0, 0), attr={"t": "Block", "m": 30})
    )

    # Create another empty assembly and add the previous assembly to this assembly
    assembly_0 = Assembly(value="a")
    assembly_0.add_assembly(assembly_1)

    return assembly_0


def test_add_element_by_index_to_empty_assembly_and_merge_it_with_empty_assembly(setup_assemblies):
    assembly_0 = setup_assemblies

    # Print the result (for debugging purposes)
    print(assembly_0)

    # Assertions
    assert assembly_0.number_of_elements == 1
    assert assembly_0.depth == 5
    assert assembly_0.name == "a"
    assert assembly_0.level == 0

    # Check child assemblies
    queue = list(assembly_0.sub_assemblies)
    expected_names = ["b", "1", "2", "3", "TYPE_CUSTOM"]
    expected_levels = [1, 2, 3, 4, 5]
    counter = 0

    while queue:
        temp_assembly_child = queue.pop(0)
        assert temp_assembly_child.name.split(" ")[0] == expected_names[counter]
        assert temp_assembly_child.level == expected_levels[counter]
        counter += 1
        queue.extend(temp_assembly_child.sub_assemblies)


if __name__ == "__main__":
    pytest.main([__file__, "-s"])

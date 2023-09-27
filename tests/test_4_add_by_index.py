from compas_assembly2 import Assembly, Element
from compas.geometry import Frame, Point
import compas_assembly2
import pytest


@pytest.fixture
def setup_assemblies():
    # Create an empty assembly and add an element by index
    assembly_1 = Assembly(value="tree")

    assembly_1.add_by_index(
        Element(
            name=compas_assembly2.ELEMENT_NAME.BLOCK,
            id=[1, 2, 3],
            frame=Frame.worldXY(),
            simplex=Point(0, 0, 0),
            attr={"t": "Block", "m": 30},
        ),
        None,
        allow_duplicate_assembly_branches=False,
        allow_duplicate_assembly_leaves=True,
    )

    assembly_1.add_by_index(
        Element(
            name=compas_assembly2.ELEMENT_NAME.BLOCK,
            id=[1, 2, 3],
            frame=Frame.worldXY(),
            simplex=Point(0, 0, 0),
            attr={"t": "Block", "m": 30},
        ),
        None,
        allow_duplicate_assembly_branches=False,
        allow_duplicate_assembly_leaves=True,
    )
    assembly_1.add_by_index(
        Element(
            name=compas_assembly2.ELEMENT_NAME.BLOCK,
            id=[1, 2, 4],
            frame=Frame.worldXY(),
            simplex=Point(0, 0, 0),
            attr={"t": "Block", "m": 30},
        ),
        None,
        allow_duplicate_assembly_branches=False,
        allow_duplicate_assembly_leaves=True,
    )

    assembly_1.add_by_index(
        Element(
            name=compas_assembly2.ELEMENT_NAME.BLOCK,
            id=[1, 2, 3, 4],
            frame=Frame.worldXY(),
            simplex=Point(0, 0, 0),
            attr={"t": "Block", "m": 30},
        ),
        [0, 2],  # user gives the branch instead of taking from the id
        allow_duplicate_assembly_branches=False,
        allow_duplicate_assembly_leaves=True,
    )

    return assembly_1


def test_add_by_index_two_times(setup_assemblies):
    assembly_0 = setup_assemblies

    # Print the result (for debugging purposes)
    print(assembly_0)

    # Assertions
    assert assembly_0.number_of_elements == 4


if __name__ == "__main__":
    pytest.main([__file__, "-s"])

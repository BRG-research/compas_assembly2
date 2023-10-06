from compas_assembly2 import Assembly, Element
from compas.geometry import Point
import pytest


@pytest.fixture
def build_assembly_of_elements():

    root = Assembly("model")
    structure = Assembly("structure")

    timber = Assembly("timber")
    timber.add_assembly(Assembly(Element(name="beam", simplex=Point(0, 0, 0))))
    timber.add_assembly(Assembly(Element(name="beam", simplex=Point(0, 5, 0))))
    timber.add_assembly(Assembly(Element(name="plate", simplex=Point(0, 0, 0))))
    timber.add_assembly(Assembly(Element(name="plate", simplex=Point(0, 7, 0))))

    # if the value type is "Element", Assembly constructor is not needed, since it is check inside the method
    concrete = Assembly("concrete")
    structure.add_assembly(concrete)
    concrete.add_assembly(Element(name="node", simplex=Point(0, 0, 0)))
    concrete.add_assembly(Element(name="block", simplex=Point(0, 5, 0)))
    concrete.add_assembly(Element(name="block", simplex=Point(0, 0, 0)))

    structure.add_assembly(timber)
    root.add_assembly(structure)
    return root


def test_add_element_by_index_two_times(build_assembly_of_elements):
    assembly = build_assembly_of_elements
    assembly = assembly.collapse(0)
    print(assembly)

    # Assertions
    assert assembly.number_of_elements == 7


if __name__ == "__main__":
    pytest.main([__file__, "-s"])

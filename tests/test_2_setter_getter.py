from compas_assembly2 import Assembly, Element
from compas.geometry import Point
from compas.datastructures import Mesh
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

    # create default tree
    assembly = build_assembly_of_elements

    # change element
    mesh = Mesh.from_polyhedron(6)
    center = Point(0, 0.2578, 0.58)
    new_element = Element(name="___NEW_INSERTED_ELEMENT_0___", id=[0, 1], simplex=center, complex=mesh)

    # replace existing assembly - setter accepts either assembly or element
    assembly["structure"]["concrete"][0] = new_element
    assembly["structure"]["concrete"][1] = Assembly(value=new_element)

    # add to existing assembly - getter returns always assemblies
    assembly["structure"]["concrete"][1].add_assembly(new_element)

    # get assembly value
    element_in_the_assembly = assembly["structure"]["concrete"][1].value

    # print for debugging
    print(assembly)
    print(element_in_the_assembly)

    # Assertions
    assert assembly.number_of_elements == 8


if __name__ == "__main__":
    pytest.main([__file__, "-s"])

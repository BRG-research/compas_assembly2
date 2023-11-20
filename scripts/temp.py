from compas_assembly2 import Element
from compas.geometry import Point

element = Element(name="beam", geometry_simplified=Point(0, 0, 0))
element_guid = element.guid
print(element_guid)
element = Element(name="beam", geometry_simplified=Point(0, 0, 0))
element_guid2 = element.guid
print(element_guid2)

print(element_guid, element_guid2)
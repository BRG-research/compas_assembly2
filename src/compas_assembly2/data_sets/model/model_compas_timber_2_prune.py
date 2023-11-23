from compas_assembly2 import Model, Node, Element
from compas.geometry import Point

if __name__ == "__main__":
    # ==========================================================================
    # create elements
    # ==========================================================================
    e0 = Element(name="beam", geometry_simplified=Point(0, 0, 0))
    e1 = Element(name="beam", geometry_simplified=Point(0, 5, 0))
    e2 = Element(name="plate", geometry_simplified=Point(0, 0, 0))
    e3 = Element(name="plate", geometry_simplified=Point(0, 0, 0))

    e4 = Element(name="block", geometry_simplified=Point(0, 5, 0))
    e5 = Element(name="block", geometry_simplified=Point(0, 0, 0))
    e6 = Element(name="block", geometry_simplified=Point(0, 0, 0))

    # ==========================================================================
    # create Model1
    # ==========================================================================
    model = Model()  # the root of hierarchy automatically initializes the root node as <my_model>
    model.add_node(Node("structure1"))  # type: ignore
    model.add_node(Node("structure2"))  # type: ignore
    model.hierarchy["structure2"].add_node(Node("sub_structure", elements=[e3, e4]))  # type: ignore
    model.hierarchy["structure2"]["sub_structure"].add_node(Node("sub_structure", elements=[e5, e6]))
    model.hierarchy["structure1"].add_node(Node("timber1", elements=[e0, e1]))  # type: ignore
    model.hierarchy["structure1"].add_node(Node("concrete1", elements=[e2]))  # type: ignore
    model.add_interaction(e0, e1)
    model.add_interaction(e0, e2)

    # ==========================================================================
    # Methods: prune, graft
    # ==========================================================================
    model.prune(2)
    model.print()

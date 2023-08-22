from compas.datastructures import Mesh
from compas.geometry import Point, Polyline, Box, Translation, Frame, Line, Pointcloud
import random
from compas_assembly2 import Element, Viewer, FabricationNest, ELEMENT_NAME

# https://compas.dev/compas/latest/reference/generated/compas.data.Data.html
from compas.data import json_dump


if __name__ == "__main__":

    # ==========================================================================
    # GEOMETRY OBJECTS
    # ==========================================================================
    mesh = Mesh.from_polyhedron(4)
    mesh.transform(Translation.from_vector((-3, 0, 0)))
    polyline_0 = Polyline(
        [
            (0.25, 2, -0.25),
            (0.25, 2, 0.25),
            (-0.25, 2, 0.25),
            (-0.25, 2, -0.25),
            (0.25, 2, -0.25),
        ]
    )
    polyline_1 = Polyline(
        [
            (0.25, -2, -0.25),
            (0.25, -2, 0.25),
            (-0.25, -2, 0.25),
            (-0.25, -2, -0.25),
            (0.25, -2, -0.25),
        ]
    )
    cloud = Pointcloud(
        [Point(random.uniform(-0.25, 0.25), random.uniform(-2, 2), random.uniform(-0.25, 0.25)) for _ in range(200)]
    )
    box = Box(Frame([3, 0, 0], [0.866, 0.1, 0.0], [0.5, 0.866, 0.0]), 2, 4, 0.25)
    geo_0 = [mesh]
    geo_1 = [polyline_0, polyline_1, cloud]
    geo_2 = [box]

    # ==========================================================================
    # INITIALIZE ELEMENTS
    # ==========================================================================
    elem_0 = Element(
        name=ELEMENT_NAME.BLOCK,
        id=[0, 1],
        frame=Frame([-3, 0, 0], [0.866, 0.1, 0.0], [0.5, 0.866, 0.0]),
        simplex=[Point(-3, 0, 0)],
        complex=geo_0,
    )

    elem_1 = Element(
        name=ELEMENT_NAME.FRAME,
        id=[0, 2],
        frame=Frame([0, 0, 0], [0, 1, 0.0], [1, 0, 0.0]),
        simplex=[Line((0, -2, 0), (0, 2, 0))],
        complex=geo_1,
    )

    elem_2 = Element(
        name=ELEMENT_NAME.PLATE,
        id=[3, 0],
        frame=Frame([3, 0, 0], [0.866, 0.1, 0.0], [0.5, 0.866, 0.0]),
        simplex=[
            Polyline(
                [
                    Point(2.236, -2.102, -0.125),
                    Point(1.777, 1.872, -0.125),
                    Point(3.764, 2.102, -0.125),
                    Point(4.223, -1.872, -0.125),
                    Point(2.236, -2.102, -0.125),
                ]
            )
        ],
        complex=geo_2,
    )

    # ==========================================================================
    # SET ELEMENT PROPERTIES
    # ==========================================================================
    elem_0.frame_global = Frame([-3, 3, 0], [1.866, 1.1, 0.0], [0.5, 0.866, 1.0])
    elem_1.frame_global = Frame([0, 3, 0], [0.866, 1.1, 0.0], [0.5, 0.866, 0.0])
    elem_2.frame_global = Frame([3, 3, 0], [0.866, 0.1, 0.0], [0.1, 0.866, 0.0])

    elements = [elem_0, elem_1, elem_2]
    for e in elements:
        # get collision information
        e.aabb(0.1)
        e.oobb(0.1)
        e.convex_hull

        # Update fabrication and structure information
        # e.fabrication["cut"] = True
        # e.fabrication["drill"] = False
        # e.structure["nodes"] = [(0, 0, 1), (0, 0, 0)]

    # ==========================================================================
    # ELEMENT COPY
    # ==========================================================================
    print(elem_0)
    elem_copy = elem_0.copy()
    elem_copy.fabrication["cut"] = False
    print(elem_copy)

    # ==========================================================================
    # FABRICATION NEST
    # ==========================================================================
    FabricationNest.pack_elements(elements=elements, nest_type=2, inflate=0.5)
    print(elem_0)
    # ==========================================================================
    # compas_view2
    # ==========================================================================
    Viewer.show_elements(elements, viewer_type="view2")

    # ==========================================================================
    # SERIALIZATION
    # ==========================================================================
    json_dump(data=elements, fp="src/compas_assembly2/data_sets/1_element_initialization.json", pretty=True)

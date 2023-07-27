from compas.datastructures import Mesh
from compas.geometry import Point, Polyline, Box, Translation, Frame, Line, Pointcloud
import random
from compas_assembly2.element import Element, ELEMENT_TYPE
from compas_assembly2.viewer import Viewer
from compas.data import json_dump, json_load  # https://compas.dev/compas/latest/reference/generated/compas.data.Data.html
import compas_rhino


if __name__ == "__main__":
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

    elem_0 = Element(
        element_type=ELEMENT_TYPE.BLOCK,
        id=(0, 1),
        simplex=[Point(-3, 0, 0)],
        display_shapes=geo_0,
        local_frame=Frame([-3, 0, 0], [0.866, 0.1, 0.0], [0.5, 0.866, 0.0]),
        global_frame=Frame([-3, 3, 0], [1.866, 1.1, 0.0], [0.5, 0.866, 1.0]),
    )

    elem_1 = Element(
        element_type=ELEMENT_TYPE.FRAME,
        id=(0, 2),
        simplex=[Line((0, -2, 0), (0, 2, 0))],
        display_shapes=geo_1,
        local_frame=Frame([0, 0, 0], [0.866, 0.1, 0.0], [0.5, 0.866, 0.0]),
        global_frame=Frame([0, 3, 0], [0.866, 1.1, 0.0], [0.5, 0.866, 0.0]),
    )

    elem_2 = Element(
        element_type=ELEMENT_TYPE.PLATE,
        id=(3, 0),
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
        display_shapes=geo_2,
        local_frame=Frame([3, 0, 0], [0.866, 0.1, 0.0], [0.5, 0.866, 0.0]),
        global_frame=Frame([3, 3, 0], [0.866, 0.1, 0.0], [0.1, 0.866, 0.0]),
    )

    elements = [elem_0, elem_1, elem_2]
    for elem in elements:
        elem.get_aabb(0, True, True)
    # Viewer.run(elements=elements, viewer_type="view2")

    json_dump(data=elements, fp="src/compas_assembly2/data_sets/1_block_beam_plate.json", pretty=True)
    #elements_loaded_from_json = json_load(fp="src/compas_assembly2/data_sets/1_block_beam_plate.json")
    elements_loaded_from_json = json_load(fp="src/compas_assembly2/rhino_commands/rhino_command_convert_to_assembly.json")
    for elem in elements_loaded_from_json:
        elem.get_aabb(0, True, True)
        print(elem.element_type)
    Viewer.run(elements=elements_loaded_from_json, viewer_type="view2")




    #"../src/compas_assembly2/rhino_commands/rhino_command_convert_to_assembly.json",
    # print before updating the fabrication, assembly, and structural information
    # print(type(elem))
    # print(elem.get_aabb(0, Frame.worldXY, True))
    # print(elem._oobb)

    # # Update fabrication information
    # elem.fabrication["cut"] = True
    # elem.fabrication["drill"] = False

    # # Update assembly information
    # elem.assembly["inerstion_direction"] = (0, 0, 1)

    # # Update structural information
    # elem.structure["nodes"] = [(0, 0, 1), (0, 0, 0)]

    # # print after updating the fabrication, assembly, and structural information
    # # print(elem)

    # print(elem)
    # elem_copy = elem.copy()
    # elem_copy.fabrication["cut"] = False
    # print(elem_copy)

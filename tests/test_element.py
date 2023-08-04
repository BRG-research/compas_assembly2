from compas.datastructures import Mesh
from compas.geometry import Point, Polyline, Box, Translation, Frame, Line, Pointcloud, distance_point_point
import random
from compas_assembly2.element import Element, ELEMENT_TYPE
from compas_assembly2.viewer import Viewer
from compas_assembly2.fabrication import Fabrication, FABRICATION_TYPES
# https://compas.dev/compas/latest/reference/generated/compas.data.Data.html
from compas.data import json_dump, json_load


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
        id=[0, 1],
        simplex=[Point(-3, 0, 0)],
        display_shapes=geo_0,
        local_frame=Frame([-3, 0, 0], [0.866, 0.1, 0.0], [0.5, 0.866, 0.0]),
        global_frame=Frame([-3, 3, 0], [1.866, 1.1, 0.0], [0.5, 0.866, 1.0]),
    )

    elem_1 = Element(
        element_type=ELEMENT_TYPE.FRAME,
        id=[0, 2],
        simplex=[Line((0, -2, 0), (0, 2, 0))],
        display_shapes=geo_1,
        local_frame=Frame([0, 0, 0], [0.866, 0.1, 0.0], [0.5, 0.866, 0.0]),
        global_frame=Frame([0, 3, 0], [0.866, 1.1, 0.0], [0.5, 0.866, 0.0]),
    )

    elem_2 = Element(
        element_type=ELEMENT_TYPE.PLATE,
        id=[3, 0],
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
    for e in elements:
        e.get_aabb(0.01)
        e.get_oobb(0.01)
        e.get_convex_hull()
    # Viewer.run(elements=elements, viewer_type="view2")

    json_dump(data=elements, fp="src/compas_assembly2/data_sets/1_block_beam_plate.json", pretty=True)
    # elements_json = json_load(fp="src/compas_assembly2/data_sets/1_block_beam_plate.json")
    elements_json = json_load(fp="src/compas_assembly2/rhino_commands/rhino_command_convert_to_assembly.json")
    elements_json.sort(key=lambda element: element.element_type, reverse=True)

    # nest elements linearly and add the the nest frame to the fabrication
    # first compute the bounding box of the elements, get the horizontal length, and create frames
    nest_type = 1
    width = {}
    height = {}
    height_step = 4
    inflate = 0.1

    for e in elements_json:
        e.get_aabb(inflate)
        e.get_oobb(inflate)
        e.get_convex_hull()

    center = Point(0, 0, 0)
    for e in elements_json:
        center = center + e.local_frame.point
    center = center/len(elements_json)

    for e in elements_json:
        width[e.element_type] = 0

    for index, (key, value) in enumerate(width.items()):
        height[key] = index*height_step*0

    for i, e in enumerate(elements_json):

        temp_width = 0
        source_frame = e.local_frame.copy()
        target_frame = Frame([0, 0, 0], source_frame.xaxis, source_frame.yaxis)

        if nest_type == 0:
            # --------------------------------------------------------------------------
            # aabb linear nesting
            # --------------------------------------------------------------------------
            temp_width = e.get_aabb()[6][0]-e.get_aabb()[0][0]
            # get the maximum height of the elements
            height[e.element_type] = max(height[e.element_type], e.get_aabb()[6][1]-e.get_aabb()[0][1])
            source_frame = Frame(
                e.get_aabb()[0],
                [e.get_aabb()[1][0]-e.get_aabb()[0][0],
                 e.get_aabb()[1][1]-e.get_aabb()[0][1],
                 e.get_aabb()[1][2]-e.get_aabb()[0][2]],
                [e.get_aabb()[3][0]-e.get_aabb()[0][0],
                 e.get_aabb()[3][1]-e.get_aabb()[0][1],
                 e.get_aabb()[3][2]-e.get_aabb()[0][2]])
            target_frame = Frame(
                [width[e.element_type], height[e.element_type], 0],
                [1, 0, 0],
                [0, 1, 0])
        elif nest_type == 1:
            # --------------------------------------------------------------------------
            # oobb linear nesting
            # --------------------------------------------------------------------------
            temp_width = distance_point_point(e.get_oobb()[0], e.get_oobb()[1])
            # get the maximum height of the elements
            height[e.element_type] = max(height[e.element_type], distance_point_point(e.get_oobb()[0], e.get_oobb()[3]))
            source_frame = Frame(
                e.get_oobb()[0],
                [e.get_oobb()[1][0]-e.get_oobb()[0][0],
                 e.get_oobb()[1][1]-e.get_oobb()[0][1],
                 e.get_oobb()[1][2]-e.get_oobb()[0][2]],
                [e.get_oobb()[3][0]-e.get_oobb()[0][0],
                 e.get_oobb()[3][1]-e.get_oobb()[0][1],
                 e.get_oobb()[3][2]-e.get_oobb()[0][2]])
            target_frame = Frame(
                [width[e.element_type], height[e.element_type], 0],
                [1, 0, 0],
                [0, 1, 0])
        elif nest_type == 3:
            # --------------------------------------------------------------------------
            # move of center
            # --------------------------------------------------------------------------
            t = 1.25
            x = (1 - t) * center.x + t * source_frame.point.x
            y = (1 - t) * center.y + t * source_frame.point.y
            z = (1 - t) * center.z + t * source_frame.point.z
            target_frame = Frame([x, y, z], source_frame.xaxis, source_frame.yaxis)

        # --------------------------------------------------------------------------
        # assignment of fabrication data
        # --------------------------------------------------------------------------

        fabrication = Fabrication(
            fabrication_type=FABRICATION_TYPES.NESTING,
            id=-1,
            frames=[source_frame, target_frame])
        e.fabrication[FABRICATION_TYPES.NESTING] = (fabrication)
        width[e.element_type] = width[e.element_type] + temp_width

    # --------------------------------------------------------------------------
    # center the frames
    # --------------------------------------------------------------------------
    print(height)
    last_height = 0
    for index, (key, value) in enumerate(width.items()):
        temp_height = height[key]
        height[key] = last_height
        last_height = last_height + temp_height

    print(height)
    for e in elements_json:
        e.fabrication[FABRICATION_TYPES.NESTING].frames[1].point.x = \
            e.fabrication[FABRICATION_TYPES.NESTING].frames[1].point.x - \
            width[e.element_type] * 0.5
        e.fabrication[FABRICATION_TYPES.NESTING].frames[1].point.y = height[e.element_type] - last_height*0.5

    Viewer.run(elements=elements_json, viewer_type="view2", show_grid=False)

    # "../src/compas_assembly2/rhino_commands/rhino_command_convert_to_assembly.json",
    # print before updating the fabrication, assembly, and structural information
    # print(type(e))
    # print(e.get_aabb(0, Frame.worldXY, True))
    # print(e._oobb)

    # # Update fabrication information
    # e.fabrication["cut"] = True
    # e.fabrication["drill"] = False

    # # Update assembly information
    # e.assembly["inerstion_direction"] = (0, 0, 1)

    # # Update structural information
    # e.structure["nodes"] = [(0, 0, 1), (0, 0, 0)]

    # # print after updating the fabrication, and structural information
    # # print(e)

    # print(e)
    # elem_copy = e.copy()
    # elem_copy.fabrication["cut"] = False
    # print(elem_copy)

from compas.datastructures import Mesh
from compas.geometry import Point, Polyline, Box, Translation, Frame, Line, Pointcloud, distance_point_point
import random
from compas_assembly2.element import Element, ELEMENT_TYPE
from compas_assembly2.viewer import Viewer
from compas_assembly2.fabrication import Fabrication, FABRICATION_TYPES
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
    for elem in elements:
        elem.get_aabb(0.01)
        elem.get_oobb(0.01)
        elem.get_convex_hull()
    # Viewer.run(elements=elements, viewer_type="view2")

    json_dump(data=elements, fp="src/compas_assembly2/data_sets/1_block_beam_plate.json", pretty=True)
    #elements_loaded_from_json = json_load(fp="src/compas_assembly2/data_sets/1_block_beam_plate.json")
    elements_loaded_from_json = json_load(fp="src/compas_assembly2/rhino_commands/rhino_command_convert_to_assembly.json")




    # center = Point(0, 0, 0)
    # for elem in elements_loaded_from_json:
    #     center = center + elem.local_frame.point
        
    # center = center/len(elements_loaded_from_json)
    # for elem in elements_loaded_from_json:
    #     polyline = Polyline([center,elem.local_frame.point])
    #     fabrication = Fabrication.create_insertion_sequence_from_polyline(0,polyline,False)
    #     elem.fabrication[fabrication.type] = fabrication

    # nest elements linearly and add the the nest frame to the fabrication
    # first compute the bounding box of the elements, get the horizontal length, and create frame based on previous mesaurements
    nest_type = 1
    width = {}
    height = {}
    height_step = 4
    inflate = 0.1

    for elem in elements_loaded_from_json:
        elem.get_aabb(inflate)
        elem.get_oobb(inflate)
        elem.get_convex_hull()

    center = Point(0, 0, 0)
    for elem in elements_loaded_from_json:
        center = center + elem.local_frame.point
    center = center/len(elements_loaded_from_json)

    for elem in elements_loaded_from_json:
        width[elem.element_type] = 0
    width["BLOCK"] = 0
    width["FRAME"] = 0
    width["PLATE"] = 0
    
    for index, (key, value) in enumerate(width.items()):
        height[key] = index*height_step
    print(width)
    print(height)



    for i, elem in enumerate(elements_loaded_from_json):

        temp_width = 0
        source_frame = elem.local_frame.copy()
        target_frame = Frame([0,0,0],source_frame.xaxis,source_frame.yaxis)

        if nest_type == 0:
            # --------------------------------------------------------------------------
            # aabb linear nesting
            # --------------------------------------------------------------------------
            temp_width = elem.get_aabb()[6][0]-elem.get_aabb()[0][0]
            source_frame = Frame(
                elem.get_aabb()[0],
                [elem.get_aabb()[1][0]-elem.get_aabb()[0][0],elem.get_aabb()[1][1]-elem.get_aabb()[0][1],elem.get_aabb()[1][2]-elem.get_aabb()[0][2]],
                [elem.get_aabb()[3][0]-elem.get_aabb()[0][0],elem.get_aabb()[3][1]-elem.get_aabb()[0][1],elem.get_aabb()[3][2]-elem.get_aabb()[0][2]])
            target_frame = Frame(
                [width[elem.element_type],height[elem.element_type],0],
                [1,0,0],
                [0,1,0])
        elif nest_type == 1:
            # --------------------------------------------------------------------------
            # oobb linear nesting
            # --------------------------------------------------------------------------
            temp_width = distance_point_point( elem.get_oobb()[0], elem.get_oobb()[1])
            source_frame = Frame(
                elem.get_oobb()[0],
                [elem.get_oobb()[1][0]-elem.get_oobb()[0][0],elem.get_oobb()[1][1]-elem.get_oobb()[0][1],elem.get_oobb()[1][2]-elem.get_oobb()[0][2]],
                [elem.get_oobb()[3][0]-elem.get_oobb()[0][0],elem.get_oobb()[3][1]-elem.get_oobb()[0][1],elem.get_oobb()[3][2]-elem.get_oobb()[0][2]])
            target_frame = Frame(
                [width[elem.element_type],height[elem.element_type],0],
                [1,0,0],
                [0,1,0])
        elif nest_type == 3:
            # --------------------------------------------------------------------------
            # move of center
            # --------------------------------------------------------------------------
            t = 1.25
            x = (1 - t) * center.x + t * source_frame.point.x
            y = (1 - t) * center.y + t * source_frame.point.y
            z = (1 - t) * center.z + t * source_frame.point.z
            target_frame = Frame([x,y,z],source_frame.xaxis,source_frame.yaxis)
            
        # --------------------------------------------------------------------------
        # assignment of fabrication data
        # --------------------------------------------------------------------------
        fabrication = Fabrication(fabrication_type = FABRICATION_TYPES.NESTING, id=-1, frames=[source_frame,target_frame])
        elem.fabrication[FABRICATION_TYPES.NESTING] = (fabrication)
        width[elem.element_type] = width[elem.element_type] + temp_width

    # --------------------------------------------------------------------------
    # center the frames
    # --------------------------------------------------------------------------
    for elem in elements_loaded_from_json:
        elem.fabrication[FABRICATION_TYPES.NESTING].frames[1].point.x = elem.fabrication[FABRICATION_TYPES.NESTING].frames[1].point.x - width[elem.element_type]*0.5
        elem.fabrication[FABRICATION_TYPES.NESTING].frames[1].point.y = elem.fabrication[FABRICATION_TYPES.NESTING].frames[1].point.y - (len(height)-1)*height_step*0.5


    Viewer.run(elements=elements_loaded_from_json, viewer_type="view2", show_grid=False)


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

    # # print after updating the fabrication, and structural information
    # # print(elem)

    # print(elem)
    # elem_copy = elem.copy()
    # elem_copy.fabrication["cut"] = False
    # print(elem_copy)

from compas.geometry import Point, Frame, distance_point_point
from compas_assembly2 import Viewer, Fabrication, FABRICATION_TYPES

# https://compas.dev/compas/latest/reference/generated/compas.data.Data.html
from compas.data import json_load


if __name__ == "__main__":

    # ==========================================================================
    # ELEMENTS FROM JSON
    # ==========================================================================
    elements_json = json_load(fp="src/compas_assembly2/rhino_commands/rhino_command_convert_to_assembly.json")

    # ==========================================================================
    # ELEMENTS NEST - TEST FABRICATION TYPE
    # This can be a function in a class that inherits from FABRICATION class
    # ==========================================================================
    elements_json.sort(key=lambda element: element.name, reverse=True)
    # nest elements linearly and add the the nest frame to the fabrication
    # first compute the bounding box of the elements, get the horizontal length, and create frames
    nest_type = 1
    width = {}
    height = {}
    height_step = 4
    inflate = 0.1

    for e in elements_json:
        e.aabb(inflate)
        e.oobb(inflate)
        e.get_convex_hull()

    center = Point(0, 0, 0)
    for e in elements_json:
        center = center + e.local_frame.point
    center = center / len(elements_json)

    for e in elements_json:
        width[e.name] = 0

    for index, (key, value) in enumerate(width.items()):
        height[key] = index * height_step * 0

    for i, e in enumerate(elements_json):

        temp_width = 0
        source_frame = e.local_frame.copy()
        target_frame = Frame([0, 0, 0], source_frame.xaxis, source_frame.yaxis)

        if nest_type == 0 and e.aabb() is not None:
            # --------------------------------------------------------------------------
            # aabb linear nesting
            # --------------------------------------------------------------------------
            temp_width = e.aabb()[6][0] - e.aabb()[0][0]
            # get the maximum height of the elements
            height[e.name] = max(height[e.name], e.aabb()[6][1] - e.aabb()[0][1])
            source_frame = Frame(
                e.aabb()[0],
                [
                    e.aabb()[1][0] - e.aabb()[0][0],
                    e.aabb()[1][1] - e.aabb()[0][1],
                    e.aabb()[1][2] - e.aabb()[0][2],
                ],
                [
                    e.aabb()[3][0] - e.aabb()[0][0],
                    e.aabb()[3][1] - e.aabb()[0][1],
                    e.aabb()[3][2] - e.aabb()[0][2],
                ],
            )
            target_frame = Frame([width[e.name], height[e.name], 0], [1, 0, 0], [0, 1, 0])
        elif nest_type == 1 and e.oobb() is not None:
            # --------------------------------------------------------------------------
            # oobb linear nesting
            # --------------------------------------------------------------------------
            temp_width = distance_point_point(e.oobb()[0], e.oobb()[1])
            # get the maximum height of the elements
            height[e.name] = max(height[e.name], distance_point_point(e.oobb()[0], e.oobb()[3]))
            source_frame = Frame(
                e.oobb()[0],
                [
                    e.oobb()[1][0] - e.oobb()[0][0],
                    e.oobb()[1][1] - e.oobb()[0][1],
                    e.oobb()[1][2] - e.oobb()[0][2],
                ],
                [
                    e.oobb()[3][0] - e.oobb()[0][0],
                    e.oobb()[3][1] - e.oobb()[0][1],
                    e.oobb()[3][2] - e.oobb()[0][2],
                ],
            )
            target_frame = Frame([width[e.name], height[e.name], 0], [1, 0, 0], [0, 1, 0])
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
            fabrication_type=FABRICATION_TYPES.NESTING, id=-1, frames=[source_frame, target_frame]
        )
        e.fabrication[FABRICATION_TYPES.NESTING] = fabrication
        width[e.name] = width[e.name] + temp_width

    # --------------------------------------------------------------------------
    # center the frames
    # --------------------------------------------------------------------------
    last_height = 0
    for index, (key, value) in enumerate(width.items()):
        temp_height = height[key]
        height[key] = last_height
        last_height = last_height + temp_height

    # ==========================================================================
    # SET ELEMENTS FABRICATION PROPERTY
    # ==========================================================================
    for e in elements_json:
        e.fabrication[FABRICATION_TYPES.NESTING].frames[1].point.x = (
            e.fabrication[FABRICATION_TYPES.NESTING].frames[1].point.x - width[e.name] * 0.5
        )
        e.fabrication[FABRICATION_TYPES.NESTING].frames[1].point.y = height[e.name] - last_height * 0.5

    # ==========================================================================
    # VIEW2
    # ==========================================================================
    Viewer.run(elements=elements_json, viewer_type="view2", show_grid=False)

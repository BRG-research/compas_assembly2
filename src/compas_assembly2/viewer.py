from compas.geometry import (
    Polyline,
    Point,
    Box,
    Line,
    Vector,
    Pointcloud,
    # Transformation,
    Translation,
    Frame,
    Quaternion,
    Scale,
)
from compas.datastructures import Mesh
from compas.colors import Color

# from compas_assembly2.fabrication import FABRICATION_TYPES
import math
import time

# ==========================================================================
# DISPLAY IN DIFFERENT VIEWERS
# TODO:
# data-structures of fabrication, and structure -> noqa: F841
# add rhino and blender
# ==========================================================================

opacity = 0.9
start = time.time()
stop = False


class Viewer:
    @staticmethod
    def string_to_color(input_string):
        # Generate a hash value from the input string
        hash_value = hash(input_string)

        # Ensure the hash value is positive (hash() can return negative values)
        hash_value = abs(hash_value)

        # Extract RGB components from the hash value
        red = hash_value % 256
        green = (hash_value // 256) % 256
        blue = (hash_value // (256**2)) % 256

        # Create a compas color
        compas_color = Color(red / 255.0, green / 255.0, blue / 255.0)

        return compas_color

    @staticmethod
    def show_elements(
        lists_of_elements=[],
        viewer_type="view2-0_rhino-1_blender-2",
        width=1280,
        height=1600,
        show_grid=False,
        show_indices=False,
        show_names=False,
        show_simplices=False,
        show_geometryes=True,
        show_aabbs=False,
        show_oobbs=False,
        show_convex_hulls=False,
        show_frames=False,
        show_fabrication=False,
        show_structure=False,
        text_height=30,  # type: ignore
        display_axis_scale=0.5,
        point_size=8,
        line_width=2,
        colors=[
            Color(0.929, 0.082, 0.498),
            Color(0.129, 0.572, 0.815),
            Color(0.5, 0.5, 0.5),
            Color(0.95, 0.95, 0.95),
            Color(0, 0, 0),
        ],
        color_red=[],
        measurements=[],
        geometry=[],
        scale=1.0,
    ):
        if viewer_type == "view" or "view2" or "compas_view2" or "0":
            try:
                from compas_view2.app import App
                from compas_view2.shapes import Text

            except ImportError:
                print("compas_view2 is not installed. Skipping the code. ---> Use pip install compas_view <---")
            else:
                # The code here will only be executed if the import was successful
                if lists_of_elements is None:
                    print("WARNING VIEW2 - lists_of_elements is None")
                    return

                if len(lists_of_elements) == 0:
                    print("WARNING VIEW2 - lists_of_elements is Empty")
                    return

                # if there is one list then wrap it to another list for a single assembly
                if isinstance(lists_of_elements, list):
                    if isinstance(lists_of_elements[0], list) is False:
                        lists_of_elements = [lists_of_elements]

                # initialize the viewer
                # modifications to the default viewer:
                # def _init_sidebar ->  self.window.addToolBar(QtCore.Qt.RightToolBarArea, self.sidebar)
                viewer = App(
                    viewmode="lighted",
                    version="120",
                    enable_sidebar=True,
                    width=width,
                    height=height,
                    show_grid=show_grid,
                )

                # change the position of the window, accomodate the sidebar of OS
                viewer.window.setGeometry(width + 35, 0, width - 35, height)

                viewer_objects = {
                    "viewer_indices": [],
                    "viewer_names": [],
                    "viewer_simplices": [],
                    "viewer_geometryes": [],
                    "viewer_frames": [],
                    "viewer_frame_globals": [],
                    "viewer_aabbs": [],
                    "viewer_oobbs": [],
                    "viewer_convex_hulls": [],
                    "viewer_fabrication": [],
                    "viewer_structure": [],
                    "viewer_measurements": [],
                    "viewer_geometry": [],
                    "viewer_all": [],
                }

                # --------------------------------------------------------------------------
                # elements can be a lists of lists to define lists_of_elements of elements
                # the viewer will display only one level of grouping
                # if you want to explore different nestingm the user must give such input
                # iterate throu
                # --------------------------------------------------------------------------

                dict_elements_lists_of_elements = {}
                elements = []

                for counter, group in enumerate(lists_of_elements):
                    if isinstance(group, list):
                        for e in group:
                            key = e.guid
                            dict_elements_lists_of_elements[key] = (e, counter)
                            elements.append(e)
                    else:
                        # group is an element in this case
                        key = group.guid
                        dict_elements_lists_of_elements[key] = (group, counter)
                        elements.append(group)

                faces_colors = color_red if len(color_red) == len(elements) else [3] * len(elements)

                # --------------------------------------------------------------------------
                # add text - indices
                # --------------------------------------------------------------------------

                for counter, element in enumerate(elements):
                    # --------------------------------------------------------------------------
                    # Scale elements
                    # --------------------------------------------------------------------------
                    element.transform(Scale.from_factors([scale, scale, scale]))

                    # --------------------------------------------------------------------------
                    # add text - indices
                    # --------------------------------------------------------------------------
                    element_id = element.guid

                    text = Text(
                        ",".join(map(str, element.id)),
                        element.frame.point + Vector(0, 0, 0.01),
                        height=text_height,
                    )

                    o = viewer.add(
                        data=text,
                        name=element_id,
                        color=colors[0],
                        is_selected=False,
                        is_visible=show_indices,
                        show_points=True,
                        show_lines=True,
                        show_faces=False,
                        pointcolor=Color(0, 0, 0),
                        linecolor=Color(0, 0, 0),
                        facecolor=Color(0.85, 0.85, 0.85),
                        linewidth=line_width,
                        pointsize=point_size,
                    )

                    viewer_objects["viewer_indices"].append(o)

                    # --------------------------------------------------------------------------
                    # add text - names
                    # --------------------------------------------------------------------------

                    text = Text(
                        element.name,
                        element.frame.point + Vector(0, 0, 0.01),
                        height=text_height,
                    )
                    o = viewer.add(
                        data=text,
                        name=element_id,
                        color=colors[1],
                        is_selected=False,
                        is_visible=show_names,
                        show_points=True,
                        show_lines=True,
                        show_faces=False,
                        pointcolor=Color(0, 0, 0),
                        linecolor=Color(0, 0, 0),
                        facecolor=Color(0.75, 0.75, 0.75),
                        linewidth=line_width,
                        pointsize=point_size,
                    )

                    viewer_objects["viewer_names"].append(o)

                    # --------------------------------------------------------------------------
                    # add geometry_simplified
                    # --------------------------------------------------------------------------
                    for i in range(len(element.geometry_simplified)):
                        if isinstance(element.geometry_simplified[i], Polyline) or isinstance(
                            element.geometry_simplified[i], Line
                        ):
                            o = viewer.add(
                                data=element.geometry_simplified[i],
                                name=element_id,
                                is_selected=False,
                                is_visible=show_simplices,
                                show_points=True,
                                show_lines=False,
                                show_faces=False,
                                pointcolor=colors[4],
                                linecolor=colors[4],
                                facecolor=Color(0.75, 0.75, 0.75),
                                linewidth=line_width,
                                pointsize=point_size,
                            )

                            viewer_objects["viewer_simplices"].append(o)
                            """
                            lines = []
                            for j in range(len(element.geometry_simplified[i].points) - 1):
                                # Given points
                                point_j = element.geometry_simplified[i].points[j]
                                point_j_plus_1 = element.geometry_simplified[i].points[j + 1]
                                vector = Vector.from_start_end(point_j, point_j_plus_1)
                                vector = vector.unitized()
                                vector = vector.scaled(0.1)
                                #interpolated_point = (point_j[0] + 0.9 * (point_j_plus_1[0] - point_j[0]),
                                #point_j[1] + 0.9 * (point_j_plus_1[1] - point_j[1]))

                                #lines.append(Line(point_j, point_j_plus_1-vector))
                                viewer_simplices.append(
                                    viewer.add(
                                        data=Line(point_j, point_j_plus_1-vector),
                                        name="viewer_geometry_simplified",
                                        is_selected=False,
                                        is_visible=show_simplices,
                                        show_points=True,
                                        show_lines=False,
                                        show_faces=False,
                                        pointcolor=Color(0, 0, 0),
                                        linecolor=Color(0, 0, 0),
                                        facecolor=Color(0.75, 0.75, 0.75),
                                        linewidth=line_width,
                                        pointsize=point_size,
                                    )
                                )
                            """
                        elif isinstance(element.geometry_simplified[i], Point):
                            o = viewer.add(
                                data=element.geometry_simplified[i],
                                name=element_id,
                                is_selected=False,
                                is_visible=show_simplices,
                                show_points=True,
                                show_lines=False,
                                show_faces=False,
                                pointcolor=colors[4],
                                linecolor=colors[4],
                                facecolor=Color(0.75, 0.75, 0.75),
                                linewidth=line_width,
                                pointsize=point_size,
                            )
                            viewer_objects["viewer_simplices"].append(o)
                        elif isinstance(element.geometry_simplified[i], Mesh):
                            o = viewer.add(
                                data=element.geometry_simplified[i],
                                name=element_id,
                                is_selected=False,
                                is_visible=show_simplices,
                                show_points=True,
                                show_lines=True,
                                show_faces=True,
                                pointcolor=colors[4],
                                linecolor=colors[4],
                                facecolor=Color(0.75, 0.75, 0.75),
                                linewidth=line_width,
                                pointsize=point_size,
                            )
                            viewer_objects["viewer_simplices"].append(o)

                    # --------------------------------------------------------------------------
                    # add geometryes
                    # --------------------------------------------------------------------------

                    for i in range(len(element.geometry)):
                        if isinstance(element.geometry[i], Mesh):
                            if element.geometry[i].number_of_vertices() > 0:
                                o = viewer.add(
                                    data=element.geometry[i],
                                    name=element_id,
                                    is_selected=False,
                                    is_visible=show_geometryes,
                                    show_points=False,
                                    show_lines=True,
                                    show_faces=True,
                                    pointcolor=Color(0, 0, 0),
                                    linecolor=colors[4],
                                    facecolor=colors[faces_colors[counter]],  # default 3
                                    linewidth=1,
                                    opacity=0.9,  # type: ignore
                                    hide_coplanaredges=True,
                                )
                                viewer_objects["viewer_geometryes"].append(o)

                        elif (
                            isinstance(element.geometry[i], Polyline)
                            or isinstance(element.geometry[i], Line)
                            or isinstance(element.geometry[i], Box)
                        ):
                            o = viewer.add(
                                data=element.geometry[i],
                                name=element_id,
                                is_selected=False,
                                is_visible=show_geometryes,
                                show_points=False,
                                show_lines=True,
                                show_faces=True,
                                pointcolor=Color(0, 0, 0),
                                linecolor=colors[4],
                                facecolor=colors[faces_colors[counter]],  # colors[3],
                                linewidth=1,
                            )
                            viewer_objects["viewer_geometryes"].append(o)
                        elif isinstance(element.geometry[i], Pointcloud):
                            o = viewer.add(
                                data=element.geometry[i],
                                name=element_id,
                                is_selected=False,
                                is_visible=show_geometryes,
                                show_points=True,
                                show_lines=False,
                                show_faces=False,
                                pointcolor=colors[4],
                                linecolor=Color(0, 0, 0),
                                facecolor=Color(0, 0, 0),
                                linewidth=0,
                                pointsize=2,
                            )

                            viewer_objects["viewer_geometryes"].append(o)

                    # --------------------------------------------------------------------------
                    # add frames
                    # --------------------------------------------------------------------------

                    frame_globals_lines = [
                        Line(
                            element.frame_global.point,
                            element.frame_global.point + element.frame_global.xaxis * display_axis_scale * 0.5,
                        ),
                        Line(
                            element.frame_global.point,
                            element.frame_global.point + element.frame_global.yaxis * display_axis_scale * 0.5,
                        ),
                        Line(
                            element.frame_global.point,
                            element.frame_global.point + element.frame_global.zaxis * display_axis_scale * 0.5,
                        ),
                    ]

                    for i in range(len(frame_globals_lines)):
                        o = viewer.add(
                            frame_globals_lines[i],
                            name=element_id,
                            is_selected=False,
                            is_visible=show_frames,
                            show_points=False,
                            show_lines=False,
                            show_faces=True,
                            pointcolor=Color(1, 0, 0),
                            linecolor=colors[i % 3],
                            facecolor=colors[i % 3],
                            linewidth=line_width,
                            # u=16,
                        )
                        viewer_objects["viewer_frame_globals"].append(o)

                    frames_lines = [
                        Line(
                            element.frame.point,
                            element.frame.point + element.frame.xaxis * display_axis_scale,
                        ),
                        Line(
                            element.frame.point,
                            element.frame.point + element.frame.yaxis * display_axis_scale,
                        ),
                        Line(
                            element.frame.point,
                            element.frame.point + element.frame.zaxis * display_axis_scale,
                        ),
                    ]

                    for i in range(len(frames_lines)):
                        o = viewer.add(
                            frames_lines[i],
                            name=element_id,
                            is_selected=False,
                            is_visible=show_frames,
                            show_points=False,
                            show_lines=False,
                            show_faces=True,
                            pointcolor=Color(1, 0, 0),
                            linecolor=colors[i % 3],
                            facecolor=colors[i % 3],
                            linewidth=line_width,
                            # u=16,
                        )
                        viewer_objects["viewer_frames"].append(o)

                    # --------------------------------------------------------------------------
                    # add aabb | oobb | convex hull
                    # --------------------------------------------------------------------------
                    if element._aabb:
                        aabb_mesh = Mesh.from_vertices_and_faces(
                            element._aabb,
                            [[0, 1, 2, 3], [4, 5, 6, 7], [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7]],
                        )

                        o = viewer.add(
                            data=aabb_mesh,  # Pointcloud(element._aabb),
                            name=element_id,
                            is_selected=False,
                            is_visible=show_aabbs,
                            show_points=True,
                            show_lines=True,
                            show_faces=True,
                            pointcolor=colors[0],
                            linecolor=Color(1, 1, 1),
                            facecolor=Color(0, 0, 0),
                            linewidth=1,
                            pointsize=point_size,
                        )
                        viewer_objects["viewer_aabbs"].append(o)

                        if element._oobb:
                            oobb_mesh = Mesh.from_vertices_and_faces(
                                element._oobb,
                                [[0, 1, 2, 3], [4, 5, 6, 7], [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7]],
                            )
                            o = viewer.add(
                                data=oobb_mesh,  # Pointcloud(element._oobb),
                                name=element_id,
                                is_selected=False,
                                is_visible=show_oobbs,
                                show_points=True,
                                show_lines=True,
                                show_faces=True,
                                pointcolor=colors[1],
                                linecolor=Color(1, 1, 1),
                                facecolor=Color(0, 0, 0),
                                linewidth=1,
                                pointsize=point_size,
                            )
                            viewer_objects["viewer_oobbs"].append(o)

                    if element.convex_hull:
                        if element.convex_hull.number_of_vertices() > 0:
                            o = viewer.add(
                                data=element.convex_hull,
                                name=element_id,
                                is_selected=False,
                                is_visible=show_convex_hulls,
                                show_points=False,
                                show_lines=True,
                                show_faces=True,
                                pointcolor=Color(0, 0, 0),
                                linecolor=Color(1, 1, 1),
                                facecolor=colors[4],
                                linewidth=1,
                                pointsize=point_size,
                            )
                            viewer_objects["viewer_convex_hulls"].append(o)

                # --------------------------------------------------------------------------
                # measurements - lines with text
                # --------------------------------------------------------------------------
                for i in range(len(measurements)):
                    text = Text(
                        str(measurements[i].length),
                        measurements[i].midpoint + Vector(0, 0, 0.1),
                        height=text_height,
                    )

                    o = viewer.add(
                        data=text,
                        name="measurement",
                        color=colors[0],
                        is_selected=False,
                        is_visible=True,
                        show_points=True,
                        show_lines=True,
                        show_faces=False,
                        pointcolor=Color(0, 0, 0),
                        linecolor=Color(0, 0, 0),
                        facecolor=Color(0.85, 0.85, 0.85),
                        linewidth=line_width,
                        pointsize=point_size,
                    )

                    line = viewer.add(
                        data=measurements[i],
                        name="measurement",
                        is_selected=False,
                        is_visible=True,
                        show_points=True,
                        show_lines=True,
                        show_faces=False,
                        pointcolor=Color(0, 0, 0),
                        linecolor=Color(0, 0, 0),
                        facecolor=Color(0.85, 0.85, 0.85),
                        linewidth=line_width,
                        pointsize=point_size,
                    )

                    viewer_objects["viewer_measurements"].append(o)
                    viewer_objects["viewer_measurements"].append(line)

                # --------------------------------------------------------------------------
                # geometry to temporary visualize during the develipment
                # --------------------------------------------------------------------------
                for i in range(len(geometry)):
                    # copy, because if you add two objects with the same guid
                    # they will be scale two times
                    geometry_copy = geometry[i].copy()
                    geometry_copy.transform(Scale.from_factors([scale, scale, scale]))
                    o = viewer.add(
                        data=geometry_copy,
                        name="geometry",
                        is_selected=False,
                        is_visible=True,
                        show_points=True,
                        show_lines=True,
                        show_faces=True,
                        pointcolor=Color(0, 0, 0),
                        linecolor=Color(0, 0, 0),
                        facecolor=colors[1],  # Color(0.85, 0.85, 0.85),
                        linewidth=line_width,
                        pointsize=point_size,
                    )

                    viewer_objects["viewer_geometry"].append(o)

                # --------------------------------------------------------------------------
                # add fabrication geometry
                # --------------------------------------------------------------------------
                frames_original = []  # noqa: F841
                frames_target = []  # noqa: F841

                # --------------------------------------------------------------------------
                # ui
                # --------------------------------------------------------------------------

                @viewer.checkbox(text="show_indices", checked=show_indices)
                def check_display_ids(checked):
                    for obj in viewer_objects["viewer_indices"]:
                        obj.is_visible = checked
                    viewer.view.update()

                @viewer.checkbox(text="show_names", checked=show_names)
                def check_display_names(checked):
                    for obj in viewer_objects["viewer_names"]:
                        obj.is_visible = checked
                    viewer.view.update()

                @viewer.checkbox(text="show_simplices", checked=show_simplices)
                def check_display_implices(checked):
                    for obj in viewer_objects["viewer_simplices"]:
                        obj.is_visible = checked
                    viewer.view.update()

                @viewer.checkbox(text="show_geometryes", checked=show_geometryes)
                def check_geometryes(checked):
                    for obj in viewer_objects["viewer_geometryes"]:
                        obj.is_visible = checked
                    viewer.view.update()

                @viewer.checkbox(text="show_aabbs", checked=show_aabbs)
                def check_aabb(checked):
                    for obj in viewer_objects["viewer_aabbs"]:
                        obj.is_visible = checked
                    viewer.view.update()

                @viewer.checkbox(text="show_oobbs", checked=show_oobbs)
                def check_oobb(checked):
                    for obj in viewer_objects["viewer_oobbs"]:
                        obj.is_visible = checked
                    viewer.view.update()

                @viewer.checkbox(text="show_convex_hulls", checked=show_convex_hulls)
                def check_convex_hulls(checked):
                    for obj in viewer_objects["viewer_convex_hulls"]:
                        obj.is_visible = checked
                    viewer.view.update()

                @viewer.checkbox(text="show_frames", checked=show_frames)
                def check_frames(checked):
                    for obj in viewer_objects["viewer_frames"]:
                        obj.is_visible = checked
                    viewer.view.update()

                @viewer.checkbox(text="show_frame_globals", checked=show_frames)
                def check_frame_globals(checked):
                    for obj in viewer_objects["viewer_frame_globals"]:
                        obj.is_visible = checked
                    viewer.view.update()

                @viewer.checkbox(text="show_measurements", checked=True)
                def check_measurements(checked):
                    for obj in viewer_objects["viewer_measurements"]:
                        obj.is_visible = checked
                    viewer.view.update()

                @viewer.slider(title="fabrication_example", maxval=100, step=1)  # type: ignore
                def slider_nesting(t):
                    def interpolate_frames(frame0, frame1, t):
                        """
                        Interpolate smoothly between two frames using Slerp and Lerp.

                        Parameters:
                            frame0 (Frame): The starting frame.
                            frame1 (Frame): The ending frame.
                            t (float): Interpolation parameter between 0 and 1.

                        Returns:
                            Frame: The interpolated frame.
                        """
                        # Perform linear interpolation for the position (point) component
                        point = Point(*frame0.point) * (1 - t) + Point(*frame1.point) * t

                        # Perform spherical linear interpolation (Slerp) for the orientation (quaternion) component
                        q0 = Quaternion.from_frame(frame0)
                        q1 = Quaternion.from_frame(frame1)

                        def interpolate_quaternion(q0, q1, t):
                            # Perform subtraction: q1 - q0
                            q_diff = Quaternion(q1.w - q0.w, q1.x - q0.x, q1.y - q0.y, q1.z - q0.z)

                            # Perform scaling: t * (q1 - q0)
                            q_scaled = Quaternion(q_diff.w * t, q_diff.x * t, q_diff.y * t, q_diff.z * t)

                            # Perform addition: q0 + t * (q1 - q0)
                            interpolated_quaternion = Quaternion(
                                q0.w + q_scaled.w, q0.x + q_scaled.x, q0.y + q_scaled.y, q0.z + q_scaled.z
                            )

                            return interpolated_quaternion

                        interpolated_quaternion = interpolate_quaternion(q0, q1, t)  # q0 * (1 - t) + q1 * t

                        # Convert the interpolated quaternion back to a frame
                        point = Point(*frame0.point) * (1 - t) + Point(*frame1.point) * t
                        interpolated_frame = Frame.from_quaternion(interpolated_quaternion, point)

                        return interpolated_frame

                    # try to find fabrication data in the name of nesting
                    # this matrix will be then applied to multiple objects
                    dict_matrices = {}
                    # for id, element in enumerate(elements):
                    #     for key, value in element.fabrication.items():
                    #         if key == FABRICATION_TYPES.NESTING:
                    #             target_frame = interpolate_frames(value.frames[0], value.frames[1], t / 100)
                    #             compas_matrix = Transformation.from_frame_to_frame(value.frames[0], target_frame)
                    #             dict_matrices[element.guid] = compas_matrix.matrix

                    # change positions of elements
                    if dict_matrices:
                        for key, value in viewer_objects.items():
                            if key == "viewer_measurements" or key == "viewer_geometry":
                                continue
                            for item in value:
                                item.matrix = dict_matrices[item.name]

                    # update the viewer after all the matrices are changed
                    viewer.view.update()

                # change opacity of elements
                @viewer.slider(title="opacity", maxval=100, step=1, value=95)  # type: ignore
                def slider_opacity(t):
                    global opacity
                    opacity = t / 100.0

                    for o in viewer_objects["viewer_geometryes"]:
                        o.opacity = opacity

                # insertion vector visualization following the order of elements

                @viewer.button(text="run_insertion")
                def reset_click():
                    global stop
                    stop = False

                    @viewer.on(interval=1)
                    def move(t):
                        global stop
                        if stop:
                            return

                        for id, o in enumerate(viewer_objects["viewer_geometryes"]):
                            scale = 1 - ((t / 12) % 1)
                            xform = Translation.from_vector(
                                dict_elements_lists_of_elements[o.name][0].insertion * scale
                            )

                            if dict_elements_lists_of_elements[o.name][1] > t / 12:
                                o.is_visible = False

                                o.matrix = xform = Translation.from_vector(
                                    dict_elements_lists_of_elements[o.name][0].insertion
                                ).matrix
                            else:
                                o.is_visible = True
                                o.opacity = opacity
                                if dict_elements_lists_of_elements[o.name][1] == math.floor(t / 12):
                                    o.matrix = xform.matrix
                                else:
                                    o.matrix = xform = Translation.from_vector(Vector(0, 0, 0)).matrix

                @viewer.button(text="stop_insertion")
                def stop_click():
                    global stop
                    stop = True

                @viewer.slider(title="insertion", maxval=len(lists_of_elements) * 100, step=1, value=0)  # type: ignore
                def slider_insertion(t):
                    for id, o in enumerate(viewer_objects["viewer_geometryes"]):
                        scale = 1 - ((t / 100.0) % 1)
                        xform = Translation.from_vector(dict_elements_lists_of_elements[o.name][0].insertion * scale)

                        if dict_elements_lists_of_elements[o.name][1] > t / 100:
                            o.is_visible = False

                            o.matrix = xform = Translation.from_vector(
                                dict_elements_lists_of_elements[o.name][0].insertion
                            ).matrix
                        else:
                            o.is_visible = True
                            o.opacity = opacity
                            if dict_elements_lists_of_elements[o.name][1] == math.floor(t / 100):
                                o.matrix = xform.matrix
                            else:
                                o.matrix = xform = Translation.from_vector(Vector(0, 0, 0)).matrix

                # color element by index
                @viewer.slider(
                    title="color_index", maxval=len(viewer_objects["viewer_geometryes"]), step=1, value=0
                )  # type: ignore
                def slider_color(t):
                    # instead of slider do somethign else for a list selection

                    for id, o in enumerate(viewer_objects["viewer_geometryes"]):
                        if id == t:
                            o.facecolor = Color(1, 0, 0)
                        else:
                            o.facecolor = Color(0.85, 0.85, 0.85)

                # get the element index from selection
                @viewer.button(text="see_index")
                def click():
                    selected_indices = []
                    selected_indices_flattened = []
                    for id, o in enumerate(viewer_objects["viewer_geometryes"]):
                        if o.is_selected:
                            selected_indices.append(str(dict_elements_lists_of_elements[o.name][0].id))
                            selected_indices_flattened.append(str(id))
                    selected_indices_str = ", ".join(selected_indices)
                    selected_indices_flattened_str = ", ".join(selected_indices_flattened)

                    if selected_indices_str == "":
                        info_message = """Nothing is selected."""
                        viewer.info(info_message)
                    else:
                        info_message = ("Element indices:\n" "{0}\n" "Element indices flattened:\n" "{1}").format(
                            selected_indices_str, selected_indices_flattened_str
                        )
                        print(selected_indices_str)
                        print(selected_indices_flattened_str)
                        viewer.info(info_message)

                # --------------------------------------------------------------------------
                # color objects by type
                # --------------------------------------------------------------------------
                type_colors = [
                    Color(0.929, 0.082, 0.498),  # 0
                    Color(0.129, 0.572, 0.815),  # 1
                    Color(0.929, 0.082, 0.498),  # 2
                    Color(0.129, 0.572, 0.815),  # 3
                    Color(0.929, 0.082, 0.498),  # 4 BEAM
                    Color(0.129, 0.572, 0.815),  # 5
                    Color(0.929, 0.082, 0.498),  # 6
                    Color(0.129, 0.572, 0.815),  # 7
                    Color(0.929, 0.082, 0.498),  # 8 PLATE
                    Color(0.129, 0.572, 0.815),  # 9
                ]

                @viewer.button(text="color_by_type")
                def color_by_type(checked):

                    for obj in viewer_objects["viewer_geometryes"]:
                        # Calculate a unique hash for the input string
                        def custom_hash(input_string):
                            # Seed value for consistency
                            seed = 0
                            for char in input_string:
                                seed = ord(char) + (seed << 6) + (seed << 16) - seed

                            return seed

                        hash_value = custom_hash(dict_elements_lists_of_elements[obj.name][0].name)
                        mapped_integer = (abs(hash_value) + 1) % 11

                        obj.facecolor = type_colors[mapped_integer % len(colors)]
                        viewer.view.update()

                @viewer.button(text="color_grey")
                def color_grey(checked):

                    for obj in viewer_objects["viewer_geometryes"]:
                        obj.facecolor = colors[3]
                        viewer.view.update()

                # --------------------------------------------------------------------------
                # run
                # --------------------------------------------------------------------------
                viewer.show()

        elif viewer_type == "rhino" or "1":
            pass
        elif viewer_type == "blender" or "2":
            pass

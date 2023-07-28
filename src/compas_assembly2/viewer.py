from compas.geometry import Polyline, Point, Box, Line, Vector, Pointcloud
from compas.datastructures import Mesh
from compas.colors import Color
from compas_assembly2.element import Element, ELEMENT_TYPE
# ==========================================================================
# DISPLAY IN DIFFERENT VIEWERS
# TODO:
# data-structures of fabrication, assembly, and structure -> noqa: F841
# add rhino and blender
# ==========================================================================


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
        blue = (hash_value // (256 ** 2)) % 256

        # Create a compas color
        compas_color = Color(red / 255.0, green / 255.0, blue / 255.0)

        return compas_color

    @staticmethod
    def run(
        elements=[],
        viewer_type="view2-0_rhino-1_blender-2",
        width=1920,
        height=1200,
        show_indices=False,
        show_types=False,
        show_simplices=True,
        show_display_shapes=False,
        show_aabbs=False,
        show_oobbs=False,
        show_convex_hulls=False,
        show_frames=False,
        show_fabrication=False,
        show_assembly=False,
        show_structure=False,
        text_height=30,  # type: ignore
        display_axis_scale=0.5,
        point_size=8,
        line_width=2,
        colors=[
            Color(0.929, 0.082, 0.498),
            Color(0.129, 0.572, 0.815),
            Color(0.5, 0.5, 0.5),
            Color(0.75, 0.75, 0.75),
            Color(0, 0, 0),
        ],
    ):
        if viewer_type == "view" or "view2" or "compas_view2" or "0":
            try:
                from compas_view2.app import App
                from compas_view2.shapes import Text
                from compas_view2.collections import Collection

            except ImportError:
                print("compas_view2 is not installed. Skipping the code. ---> Use pip install compas_view <---")
            else:
                # The code here will only be executed if the import was successful

                # initialize the viewer
                viewer = App(
                    viewmode="shaded",
                    enable_sidebar=True,
                    width=width,
                    height=height,
                    show_grid=True,
                )
                viewer_indices = []
                viewer_types = []
                viewer_simplices = []
                viewer_display_shapes = []
                viewer_aabbs = []
                viewer_oobbs = []
                viewer_convex_hulls = []
                viewer_frames = []
                viewer_fabrication = []  # noqa: F841
                viewer_assembly = []  # noqa: F841
                viewer_structure = []  # noqa: F841

                for element in elements:
                    # --------------------------------------------------------------------------
                    # add text - indices
                    # --------------------------------------------------------------------------

                    text = Text(
                        ",".join(map(str, element.id)),
                        element.local_frame.point + Vector(0, 0, 0.01),
                        height=text_height,
                    )
                    viewer_indices.append(
                        viewer.add(
                            data=text,
                            name="viewer_text",
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
                    )

                    # --------------------------------------------------------------------------
                    # add text - types
                    # --------------------------------------------------------------------------

                    text = Text(
                        
                        element.element_type,
                        element.local_frame.point + Vector(0, 0, 0.01),
                        height=text_height,
                    )

                    viewer_types.append(
                        viewer.add(
                            data=text,
                            name="viewer_types",
                            color=colors[1],
                            is_selected=False,
                            is_visible=show_types,
                            show_points=True,
                            show_lines=True,
                            show_faces=False,
                            pointcolor=Color(0, 0, 0),
                            linecolor=Color(0, 0, 0),
                            facecolor=Color(0.75, 0.75, 0.75),
                            linewidth=line_width,
                            pointsize=point_size,
                        )
                    )

                    # --------------------------------------------------------------------------
                    # add simplex
                    # --------------------------------------------------------------------------
                    for i in range(len(element.simplex)):
                        
                        if (
                            isinstance(element.simplex[i], Polyline)
                            or isinstance(element.simplex[i], Line)
                        ):  
                            viewer_simplices.append(
                                viewer.add(
                                    data=element.simplex[i],
                                    name="viewer_simplex",
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
                            )
                            """
                            lines = []
                            for j in range(len(element.simplex[i].points) - 1):
                                # Given points
                                point_j = element.simplex[i].points[j]
                                point_j_plus_1 = element.simplex[i].points[j + 1]
                                vector = Vector.from_start_end(point_j, point_j_plus_1)
                                vector = vector.unitized()
                                vector = vector.scaled(0.1)
                                
                                #interpolated_point = (point_j[0] + 0.9 * (point_j_plus_1[0] - point_j[0]),
                                #point_j[1] + 0.9 * (point_j_plus_1[1] - point_j[1]))

                                #lines.append(Line(point_j, point_j_plus_1-vector))

                            
                                viewer_simplices.append(
                                    viewer.add(
                                        data=Line(point_j, point_j_plus_1-vector),
                                        name="viewer_simplex",
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
                        elif(isinstance(element.simplex[i], Point)):
                            viewer_simplices.append(
                                viewer.add(
                                    data=element.simplex[i],
                                    name="viewer_simplex",
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
                            )
                        elif(isinstance(element.simplex[i], Mesh)):
                            viewer_simplices.append(
                                viewer.add(
                                    data=element.simplex[i],
                                    name="viewer_simplex",
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
                            )

                    # --------------------------------------------------------------------------
                    # add display shapes
                    # --------------------------------------------------------------------------

                    for i in range(len(element.display_shapes)):
                        if (
                            isinstance(element.display_shapes[i], Mesh)
                            or isinstance(element.display_shapes[i], Polyline)
                            or isinstance(element.display_shapes[i], Line)
                            or isinstance(element.display_shapes[i], Box)
                        ):
                            
                            viewer_display_shapes.append(
                                viewer.add(
                                    data=element.display_shapes[i],
                                    name="viewer_display_shape_mesh",
                                    is_selected=False,
                                    is_visible=show_display_shapes,
                                    show_points=False,
                                    show_lines=True,
                                    show_faces=True,
                                    pointcolor=Color(0, 0, 0),
                                    linecolor=colors[4],
                                    facecolor=colors[3],#Viewer.string_to_color(element.element_type),#colors[3],
                                    linewidth=1,
                                    opacity=0.333,  # type: ignore
                                )
                            )
                        elif isinstance(element.display_shapes[i], Pointcloud):
                            viewer_display_shapes.append(
                                viewer.add(
                                    data=element.display_shapes[i],
                                    name="viewer_display_shape_mesh",
                                    is_selected=False,
                                    is_visible=show_display_shapes,
                                    show_points=True,
                                    show_lines=False,
                                    show_faces=False,
                                    pointcolor=colors[4],
                                    linecolor=Color(0, 0, 0),
                                    facecolor=Color(0, 0, 0),
                                    linewidth=0,
                                    pointsize=2,
                                )
                            )

                    # --------------------------------------------------------------------------
                    # add frames
                    # --------------------------------------------------------------------------

                    frames_lines = [
                        Line(
                            element.local_frame.point,
                            element.local_frame.point + element.local_frame.xaxis * display_axis_scale,
                        ),
                        Line(
                            element.local_frame.point,
                            element.local_frame.point + element.local_frame.yaxis * display_axis_scale,
                        ),
                        Line(
                            element.local_frame.point,
                            element.local_frame.point + element.local_frame.zaxis * display_axis_scale,
                        ),
                        Line(
                            element.global_frame.point,
                            element.global_frame.point + element.global_frame.xaxis * display_axis_scale * 0.5,
                        ),
                        Line(
                            element.global_frame.point,
                            element.global_frame.point + element.global_frame.yaxis * display_axis_scale * 0.5,
                        ),
                        Line(
                            element.global_frame.point,
                            element.global_frame.point + element.global_frame.zaxis * display_axis_scale * 0.5,
                        ),
                    ]

                    for i in range(len(frames_lines)):
                        viewer_frames.append(
                            viewer.add(
                                frames_lines[i],
                                name="viewer_frames",
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
                        )

                    # --------------------------------------------------------------------------
                    # add aabb | oobb | convex hull
                    # --------------------------------------------------------------------------
                    if (element._aabb):
                        aabb_mesh = Mesh.from_vertices_and_faces(
                            element._aabb,
                            [[0, 1, 2, 3], [4, 5, 6, 7], [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7]],
                        )

                        viewer_aabbs.append(
                            viewer.add(
                                data=aabb_mesh,  # Pointcloud(element._aabb),
                                name="viewer_aabb",
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
                        )

                        if (element._oobb):
                            oobb_mesh = Mesh.from_vertices_and_faces(
                                element._oobb,
                                [[0, 1, 2, 3], [4, 5, 6, 7], [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7]],
                            )
                            viewer_oobbs.append(
                                viewer.add(
                                    data=oobb_mesh,  # Pointcloud(element._oobb),
                                    name="viewer_oobb",
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
                            )

                    if (element._convex_hull):
                        viewer_convex_hulls.append(
                            viewer.add(
                                data=element._convex_hull,
                                name="viewer_convex_hull",
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
                        )

                # --------------------------------------------------------------------------
                # add fabrication geometry
                # --------------------------------------------------------------------------

                # --------------------------------------------------------------------------
                # ui
                # --------------------------------------------------------------------------

                @viewer.checkbox(text="show_indices", checked=show_indices)
                def check_display_ids(checked):
                    for obj in viewer_indices:
                        obj.is_visible = checked
                    viewer.view.update()

                @viewer.checkbox(text="show_types", checked=show_types)
                def check_display_types(checked):
                    for obj in viewer_types:
                        obj.is_visible = checked
                    viewer.view.update()

                @viewer.checkbox(text="show_simplices", checked=show_simplices)
                def check_display_implices(checked):
                    for obj in viewer_simplices:
                        obj.is_visible = checked
                    viewer.view.update()

                @viewer.checkbox(text="show_display_shapes", checked=show_display_shapes)
                def check_display_shapes(checked):
                    for obj in viewer_display_shapes:
                        obj.is_visible = checked
                    viewer.view.update()

                @viewer.checkbox(text="show_aabbs", checked=show_aabbs)
                def check_aabb(checked):
                    for obj in viewer_aabbs:
                        obj.is_visible = checked
                    viewer.view.update()

                @viewer.checkbox(text="show_oobbs", checked=show_oobbs)
                def check_oobb(checked):
                    for obj in viewer_oobbs:
                        obj.is_visible = checked
                    viewer.view.update()

                @viewer.checkbox(text="show_convex_hulls", checked=show_convex_hulls)
                def check_convex_hulls(checked):
                    for obj in viewer_convex_hulls:
                        obj.is_visible = checked
                    viewer.view.update()

                @viewer.checkbox(text="show_frames", checked=show_frames)
                def check_frames(checked):
                    for obj in viewer_frames:
                        obj.is_visible = checked
                    viewer.view.update()

                # --------------------------------------------------------------------------
                # run
                # --------------------------------------------------------------------------
                viewer.show()

        elif viewer_type == "rhino" or "1":
            pass
        elif viewer_type == "blender" or "2":
            pass

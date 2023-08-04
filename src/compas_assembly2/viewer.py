from compas.geometry import Polyline, Point, Box, Line, Vector, Pointcloud, Transformation, Translation, Frame, Quaternion
from compas.datastructures import Mesh
from compas.colors import Color
from compas_assembly2.element import Element, ELEMENT_TYPE
from compas_assembly2.fabrication import Fabrication, FABRICATION_TYPES
import math
# ==========================================================================
# DISPLAY IN DIFFERENT VIEWERS
# TODO:
# data-structures of fabrication, and structure -> noqa: F841
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
        show_grid=False,
        show_indices=False,
        show_types=False,
        show_simplices=True,
        show_display_shapes=True,
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
                    viewmode="lighted",
                    version="120",
                    enable_sidebar=True,
                    width=width,
                    height=height,
                    show_grid=show_grid,
  

                )
                
                viewer_objects = {
                    "viewer_indices":[], 
                    "viewer_types":[], 
                    "viewer_simplices":[], 
                    "viewer_display_shapes":[], 
                    "viewer_local_frames":[], 
                    "viewer_global_frames":[], 
                    "viewer_aabbs":[], 
                    "viewer_oobbs":[], 
                    "viewer_convex_hulls":[], 
                    "viewer_fabrication":[], 
                    "viewer_structure":[],
                    "viewer_all":[]}


                for element in elements:
                    # --------------------------------------------------------------------------
                    # add text - indices
                    # --------------------------------------------------------------------------
                    element_id = str(element.id)

                    text = Text(
                        ",".join(map(str, element.id)),
                        element.local_frame.point + Vector(0, 0, 0.01),
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
                    # add text - types
                    # --------------------------------------------------------------------------

                    text = Text(
                        
                        element.element_type,
                        element.local_frame.point + Vector(0, 0, 0.01),
                        height=text_height,
                    )
                    o = viewer.add(
                            data=text,
                            name=element_id,
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

                    viewer_objects["viewer_types"].append(o)

                    # --------------------------------------------------------------------------
                    # add simplex
                    # --------------------------------------------------------------------------
                    for i in range(len(element.simplex)):
                        
                        if (
                            isinstance(element.simplex[i], Polyline)
                            or isinstance(element.simplex[i], Line)
                        ):  
                            o = viewer.add(
                                    data=element.simplex[i],
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

                            viewer_objects["viewer_simplices"].append( o)
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
                            o = viewer.add(
                                    data=element.simplex[i],
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
                            viewer_objects["viewer_simplices"].append( o)
                        elif(isinstance(element.simplex[i], Mesh)):
                            o = viewer.add(
                                    data=element.simplex[i],
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
                            viewer_objects["viewer_simplices"].append( o)

                    # --------------------------------------------------------------------------
                    # add display shapes
                    # --------------------------------------------------------------------------

                    for i in range(len(element.display_shapes)):
                        if (
                            isinstance(element.display_shapes[i], Mesh)
                        ):
                            

                            o = viewer.add(
                                    data=element.display_shapes[i],
                                    name=element_id,
                                    is_selected=False,
                                    is_visible=show_display_shapes,
                                    show_points=False,
                                    show_lines=True,
                                    show_faces=True,
                                    pointcolor=Color(0, 0, 0),
                                    linecolor=colors[4],
                                    facecolor=colors[3],#Viewer.string_to_color(element.element_type),#colors[3],
                                    linewidth=1,
                                    opacity=0.9,  # type: ignore
                                    hide_coplanaredges=True,
                                )
                            
                            viewer_objects["viewer_display_shapes"].append( o)

                        elif (isinstance(element.display_shapes[i], Polyline)
                             or isinstance(element.display_shapes[i], Line)
                             or isinstance(element.display_shapes[i], Box)
                        ):
                            o = viewer.add(
                                    data=element.display_shapes[i],
                                    name=element_id,
                                    is_selected=False,
                                    is_visible=show_display_shapes,
                                    show_points=False,
                                    show_lines=True,
                                    show_faces=True,
                                    pointcolor=Color(0, 0, 0),
                                    linecolor=colors[4],
                                    facecolor=colors[3],#Viewer.string_to_color(element.element_type),#colors[3],
                                    linewidth=1,
                                )
                            viewer_objects["viewer_display_shapes"].append( o)
                        elif isinstance(element.display_shapes[i], Pointcloud):
                            o = viewer.add(
                                    data=element.display_shapes[i],
                                    name=element_id,
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
                            
                            viewer_objects["viewer_display_shapes"].append( o)

                    # --------------------------------------------------------------------------
                    # add frames
                    # --------------------------------------------------------------------------

                    global_frames_lines = [
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

                    for i in range(len(global_frames_lines)):
                        o = viewer.add(
                                global_frames_lines[i],
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
                        viewer_objects["viewer_global_frames"].append( o)

                    local_frames_lines = [
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
                        )
                    ]

                    for i in range(len(local_frames_lines)):
                        o = viewer.add(
                                local_frames_lines[i],
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
                        viewer_objects["viewer_local_frames"].append( o)

                    # --------------------------------------------------------------------------
                    # add aabb | oobb | convex hull
                    # --------------------------------------------------------------------------
                    if (element._aabb):
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
                                pointsize=point_size
                            )
                        viewer_objects["viewer_aabbs"].append( o)

                        if (element._oobb):
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
                            viewer_objects["viewer_oobbs"].append( o)

                    if (element._convex_hull):
                        o = viewer.add(
                                data=element._convex_hull,
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
                        viewer_objects["viewer_convex_hulls"].append( o)

                # --------------------------------------------------------------------------
                # add fabrication geometry
                # --------------------------------------------------------------------------
                frames_original = []
                frames_target = []



                # --------------------------------------------------------------------------
                # ui
                # --------------------------------------------------------------------------

                @viewer.checkbox(text="show_indices", checked=show_indices)
                def check_display_ids(checked):
                    for obj in viewer_objects["viewer_indices"]:
                        obj.is_visible = checked
                    viewer.view.update()

                @viewer.checkbox(text="show_types", checked=show_types)
                def check_display_types(checked):
                    for obj in viewer_objects["viewer_types"]:
                        obj.is_visible = checked
                    viewer.view.update()

                @viewer.checkbox(text="show_simplices", checked=show_simplices)
                def check_display_implices(checked):
                    for obj in viewer_objects["viewer_simplices"]:
                        obj.is_visible = checked
                    viewer.view.update()

                @viewer.checkbox(text="show_display_shapes", checked=show_display_shapes)
                def check_display_shapes(checked):
                    for obj in viewer_objects["viewer_display_shapes"]:
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

                @viewer.checkbox(text="show_local_frames", checked=show_frames)
                def check_local_frames(checked):
                    for obj in viewer_objects["viewer_local_frames"]:
                        obj.is_visible = checked
                    viewer.view.update()

                @viewer.checkbox(text="show_global_frames", checked=show_frames)
                def check_global_frames(checked):
                    for obj in viewer_objects["viewer_global_frames"]:
                        obj.is_visible = checked
                    viewer.view.update()



                @viewer.slider(title="fabrication_example", maxval=100, step=1, bgcolor=Color.white())
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
                            interpolated_quaternion = Quaternion(q0.w + q_scaled.w, q0.x + q_scaled.x, q0.y + q_scaled.y, q0.z + q_scaled.z)

                            return interpolated_quaternion
                        
                        interpolated_quaternion =  interpolate_quaternion(q0, q1, t) #q0 * (1 - t) + q1 * t

                        # Convert the interpolated quaternion back to a frame
                        point = Point(*frame0.point) * (1 - t) + Point(*frame1.point) * t
                        interpolated_frame = Frame.from_quaternion(interpolated_quaternion, point) 

                        return interpolated_frame

                    # try to find fabrication data in the name of nesting
                    # this matrix will be then applied to multiple objects
                    dict_matrices = {} 
                    for id, element in enumerate(elements):
                        for key, value in element.fabrication.items():
                            if (key == FABRICATION_TYPES.NESTING):
                                target_frame = interpolate_frames(value.frames[0],value.frames[1], t/100 )
                                compas_matrix = Transformation.from_frame_to_frame(value.frames[0], target_frame)
                                dict_matrices[str(element.id)]=(compas_matrix.matrix)

                    # change positions of elements
                    for key, value in viewer_objects.items():
                            for item in value:
                                item.matrix = dict_matrices[item.name]


                    # update the viewer after all the matrices are changed
                    viewer.view.update()

                @viewer.slider(title="opacity", maxval=100, step=1, bgcolor=Color.white(), value=95)
                def slider_opacity(t):
                    for o in viewer_objects["viewer_display_shapes"]:
                            o.opacity = t/100.0
                # --------------------------------------------------------------------------
                # run
                # --------------------------------------------------------------------------

                viewer.show()

        elif viewer_type == "rhino" or "1":
            pass
        elif viewer_type == "blender" or "2":
            pass

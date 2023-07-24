from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import copy
from compas.geometry import (
    Frame,
    Geometry,
    Transformation,
    Translation,
    Polyline,
    Point,
    Box,
    Line,
    Pointcloud,
    bounding_box,
    convex_hull,
)
from compas.datastructures import Mesh
from compas.datastructures import mesh_bounding_box
from enum import Enum
from compas.colors import Color
import random


class ElementType(Enum):
    BLOCK = 10
    BLOCK_CONCAVE = 11
    BLOCK_X = 12
    FRAME = 20
    FRAME_BENT = 21
    FRAME_X = 22
    PLATE = 30
    SHELL = 31
    SHELL_X = 32


class Element:
    """Class representing a structural object of an assembly."""

    # ==========================================================================
    # CONSTRUCTORS (INPUT)
    # ==========================================================================
    """Class representing a structural object of an assembly.

    This class defines structural elements used in an assembly.
    Each element is defined by inputs: an ID, attributes, geometrical shape, orientation frames.
    Additionally, it stores output dictionaries for fabrication, assembly, and structural information.

    Parameters
    ----------
        element_type (ElementType): The type of the element, e.g., ElementType.BLOCK, ElementType.BEAM and etc.
        id (tuple or int): A unique identifier for the element, represented as a tuple, e.g.,(0) or (0, 1) or (1, 5, 9).
        attr (dict, optional): A dictionary containing attributes of the element. Defaults to an empty dictionary.
        simplex (list, optional): Supported types: Point, Polyline (for lines use two points), List(Polyline)
        display_shapes  (list, optional): Supported types: Mesh, Polyline, Box, Line, Pointcloud.
        local_frame (Frame, optional): The local frame of the element.
        global_frame (Frame, optional): The global frame of the element.
        kwargs (dict, optional): Additional keyword arguments can be passed to the element.

    Attributes
    ----------
        get_bbox (list): A list of XYZ coordinates defining the bounding box for collision detection.

    Example
    -------
        if __name__ == "__main__":
            elem = Element(
                element_type=ElementType.BLOCK,
                id=(0, 1),
                display_shapes =[],
                local_frame=Frame(point=(0, 0, 0), xaxis=(1, 0, 0), yaxis=(0, 1, 0)),
                global_frame=Frame.worldXY(),
                width=10,
                height=50,
                length=95,
            )

            # print before updating the fabrication, assembly, and structural information
            print(elem)

            # Update fabrication information
            elem.fabrication["cut"] = True
            elem.fabrication["drill"] = False

            # Update assembly information
            elem.assembly["inerstion_direction"] = (0, 0, 1)

            # Update structural information
            elem.structure["nodes"] = [(0, 0, 1), (0, 0, 0)]

            # print after updating the fabrication, assembly, and structural information
            print(elem)
    """

    def __init__(
        self,
        element_type=ElementType.BLOCK,
        id=(0, 1),
        simplex=[],
        display_shapes=[],
        local_frame=Frame.worldXY,
        global_frame=Frame.worldXY,
        **kwargs,
    ):
        # indexing + attributes
        self.id = (id,) if isinstance(id, int) else id  # tuple e.g. (0, 1) or (1, 5, 9)
        self.element_type = element_type  # type of the element, e.g., block, beam, plate, node, etc.
        self.attributes = {}  # set the attributes of an object
        self.attributes.update(kwargs)  # update the attributes of with the kwargs

        # minimal representatio and geometrical shapes
        # iterate through the input geometry
        # check if they are valid geometry objects
        # duplicate them and add them geometry list to avoid transformation issues
        self.simplex = []  # geometry, can be meshes, breps, curves, points, etc.
        for g in simplex:
            if isinstance(g, Geometry) or isinstance(g, Mesh):
                self.simplex.append(g.copy())

        self.display_shapes = []  # geometry, can be meshes, breps, curves, points, etc.
        for g in display_shapes:
            if isinstance(g, Geometry) or isinstance(g, Mesh):
                self.display_shapes.append(g.copy())

        # collision detection, these members are private access them using getters
        self._aabb = []  # XYZ coordinates of 8 points defining a box
        self._oobb = []  # XYZ coordinates of 8 points defining a box
        self._convex_hull = Mesh()  # convex hull of the geometry
        self._outlines = []  # closed polylines - in majority of cases objects will have planar faces
        self._outlines_frames = []  # closed polylines planes - in majority of cases objects will have planar faces

        # orientation frames
        self.local_frame = Frame.copy(local_frame) or Frame.worldXY()  # set the local frame of an object
        self.global_frame = Frame.copy(global_frame) or Frame.worldXY()  # set the global frame of an object

        # output for further processing
        self.fabrication = dict()
        self.assembly = dict()
        self.structure = dict()

    # ==========================================================================
    # PROPERTIES
    # ==========================================================================

    def get_aabb(self, inflate=0.01, frame=Frame.worldXY, compute_convex_hull=False):
        # iterate display_shapes  and get the bounding box by geometry type
        # Mesh, Polyline, Box, Line
        frame_to_computed_oobb = frame or Frame.worldXY
        points = []
        points_bbox = []

        for i in range(len(self.display_shapes)):
            corners = []
            if isinstance(self.display_shapes[i], Mesh):
                corners = mesh_bounding_box(self.display_shapes[i])
                if compute_convex_hull:
                    points.extend(list(self.display_shapes[i].vertices_attributes("xyz")))
            elif isinstance(self.display_shapes[i], Polyline):
                # polylines are a list of points
                corners = bounding_box(self.display_shapes[i])
                if compute_convex_hull:
                    points.extend(self.display_shapes[i])
            elif isinstance(self.display_shapes[i], Line):
                corners = [self.display_shapes[i].start, self.display_shapes[i].end]
                if compute_convex_hull:
                    points.extend(corners)
            elif isinstance(self.display_shapes[i], Box):
                corners = bounding_box(self.display_shapes[i].points)
                frame_to_computed_oobb = self.display_shapes[i].frame
                if compute_convex_hull:
                    points.extend(corners)
            elif isinstance(self.display_shapes[i], Pointcloud):
                points.extend(self.display_shapes[i].points)

            if len(corners) == 8:
                points_bbox.extend([corners[0], corners[6]])
            elif len(corners) == 2:
                points_bbox.extend(corners)

        # if no points found, return
        if len(points_bbox) < 2:
            return

        # compute axis-aligned bounding box
        points_bbox = bounding_box(points_bbox)
        self._aabb = bounding_box(
            [
                [points_bbox[0][0] - inflate, points_bbox[0][1] - inflate, points_bbox[0][2] - inflate],
                [points_bbox[6][0] + inflate, points_bbox[6][1] + inflate, points_bbox[6][2] + inflate],
            ]
        )

        # compute the object oriented bounding box
        if frame_to_computed_oobb != Frame.worldXY:
            xform = Transformation.from_frame_to_frame(Frame.worldXY(), frame_to_computed_oobb)
            xform_inv = xform.inverse()

            self._oobb = []
            for i in range(len(points_bbox)):
                point = Point(*points_bbox[i])
                point.transform(xform)
                self._oobb.append(point)
            self._oobb = bounding_box(self._oobb)

            for i in range(len(self._oobb)):
                point = Point(*self._oobb[i])
                point.transform(xform_inv)
                self._oobb[i] = list(point)
        else:
            self._oobb = self._aabb

        # compute the convex hull
        if compute_convex_hull and len(points) > 2:
            self._convex_hull = convex_hull(points)
        else:
            self._convex_hull = None

        return self._aabb

    def __repr__(self):
        """
        Return a string representation of the Element.

        Returns:
            str: The string representation of the Element.
        """
        return f"""
(Type: {self.element_type},
 ID: {self.id},
 Minimal Representation Geometries: {self.display_shapes },
 Vizualization Geometries: {self.display_shapes },
 Local Frame: {self.local_frame},
 Global Frame: {self.global_frame},
 Fabrication: {self.fabrication},
 Assembly: {self.assembly},
 Structure: {self.structure},
 Attributes: {self.attributes})"""

    # ==========================================================================
    # PROPERTIES FOR DIGITAL FABRICATION (OUTPUT)
    # ==========================================================================

    def get_fabrication(self, key):
        pass

    def get_assembly(self, key):
        pass

    def get_structure(self, key):
        pass

    # ==========================================================================
    # COPY ALL GEOMETRY OBJECTS
    # ==========================================================================

    def copy(self):
        # copy main properties
        new_instance = self.__class__(
            self.element_type,
            self.id,
            self.display_shapes,
            self.local_frame,
            self.global_frame,
            **self.attributes,
        )

        # deepcopy of the fabrication, assembly and structural information¨
        new_instance.fabrication = copy.deepcopy(self.fabrication)
        new_instance.assembly = copy.deepcopy(self.assembly)
        new_instance.structure = copy.deepcopy(self.structure)

        return new_instance

    # ==========================================================================
    # TRANSFORMATIONS
    # ==========================================================================

    def transform(self, transformation):
        """
        Transforms the display_shapes , local frame, and global frame of the Element.

        Parameters:
            transformation (Transformation): The transformation to be applied to the Element's geometry and frames.

        Returns:
            None
        """
        for i in range(len(self.simplex)):
            self.simplex[i].transform(transformation)

        for i in range(len(self.display_shapes)):
            self.display_shapes[i].transform(transformation)

        self.local_frame.transform(transformation)
        self.global_frame.transform(transformation)

    def transformed(self, transformation):
        """
        Creates a transformed copy of the Element.

        Parameters:
            transformation (Transformation): The transformation to be applied to the copy.

        Returns:
            Element: A new instance of the Element with the specified transformation applied.
        """
        new_instance = self.copy()
        new_instance.transform(transformation)
        return new_instance

    def orient(self, frame):
        """
        Applies frame_to_frame transformation to the display_shapes , local frame, and global frame of the Element.

        Parameters:
            frame (Frame): The target frame to which  the Element will be transformed.

        Returns:
            None
        """
        xform = Transformation.from_frame_to_frame(self.local_frame, frame)
        self.transform(xform)

    def oriented(self, frame):
        """
        Creates an oriented copy of the Element.

        Parameters:
            frame (Frame): The target frame to which the Element will be transformed.

        Returns:
            Element: A new instance of the Element with the specified orientation applied.
        """
        new_instance = self.copy()
        new_instance.orient(frame)
        return new_instance

    # ==========================================================================
    # COLLISION DETECTION
    # ==========================================================================

    def collide(self, other):
        pass

    # ==========================================================================
    # DISPLAY IN DIFFERENT VIEWERS
    # ==========================================================================

    @staticmethod
    def display(
        elements=[],
        viewer_type="view2-0_rhino-1_blender-2",
        show_simplex=True,
        show_shapes=False,
        show_frames=False,
        show_aabb=False,
        show_oobb=False,
        show_convex_hull=False,
        show_fabrication=False,
        show_assembly=False,
        show_structure=False,
    ):
        if viewer_type == "view" or "view2" or "compas_view2" or "0":
            try:
                from compas_view2.app import App

            except ImportError:
                print("compas_view2 is not installed. Skipping the code. ---> Use pip install compas_view <---")
            else:
                # The code here will only be executed if the import was successful

                # initialize the viewer
                viewer = App(viewmode="shaded", enable_sidebar=True, width=1280, height=800)
                viewer_display_shapes = []
                viewer_aabbs = []

                for element in elements:
                    # --------------------------------------------------------------------------
                    # add simplex
                    # --------------------------------------------------------------------------

                    # --------------------------------------------------------------------------
                    # add display shapes
                    # --------------------------------------------------------------------------

                    # loop through the display_shapes and add them to the viewer

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
                                    is_visible=True,
                                    show_points=False,
                                    show_lines=True,
                                    show_faces=True,
                                    pointcolor=Color(0, 0, 0),
                                    linecolor=Color(0, 0, 0),
                                    facecolor=Color(0.75, 0.75, 0.75),
                                )
                            )
                        elif isinstance(element.display_shapes[i], Pointcloud):
                            viewer_display_shapes.append(
                                viewer.add(
                                    data=element.display_shapes[i],
                                    name="viewer_display_shape_mesh",
                                    is_selected=False,
                                    is_visible=True,
                                    show_points=True,
                                    show_lines=False,
                                    show_faces=False,
                                    pointcolor=Color(0, 0, 0),
                                    linecolor=Color(0, 0, 0),
                                    facecolor=Color(0, 0, 0),
                                    linewidth=0,
                                    pointsize=3,
                                )
                            )

                    # --------------------------------------------------------------------------
                    # add frames
                    # --------------------------------------------------------------------------

                    # --------------------------------------------------------------------------
                    # add aabb | oobb | convex hull
                    # --------------------------------------------------------------------------
                    viewer_aabbs.append(
                        viewer.add(
                            data=Pointcloud(element._aabb),
                            name="viewer_aabb",
                            is_selected=False,
                            is_visible=True,
                            show_points=True,
                            show_lines=False,
                            show_faces=False,
                            pointcolor=Color(1, 0, 0),
                            linecolor=Color(0, 0, 0),
                            facecolor=Color(1, 0, 0),
                            linewidth=1,
                            pointsize=7,
                        )
                    )
                    # --------------------------------------------------------------------------
                    # add fabrication geometry
                    # --------------------------------------------------------------------------

                @viewer.checkbox(text="display_shapes", checked=True)
                def check(checked):
                    for obj in viewer_display_shapes:
                        obj.is_visible = checked
                    viewer.view.update()

                @viewer.checkbox(text="display_aabbs", checked=True)
                def check_aabb(checked):
                    for obj in viewer_aabbs:
                        obj.is_visible = checked
                        viewer.view.update()

                viewer.show()

        elif viewer_type == "rhino" or "1":
            pass
        elif viewer_type == "blender" or "2":
            pass


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
    line = Line((0, -2, 0), (0, 2, 0))
    cloud = Pointcloud(
        [Point(random.uniform(-0.25, 0.25), random.uniform(-2, 2), random.uniform(-0.25, 0.25)) for _ in range(200)]
    )

    box = Box(Frame([3, 0, 0], [0.866, 0.1, 0.0], [0.5, 0.866, 0.0]), 2, 4, 0.25)

    geo_0 = [mesh]

    geo_1 = [line, polyline_0, polyline_1, cloud]

    geo_2 = [box]

    elem_0 = Element(
        element_type=ElementType.BLOCK,
        id=(0, 1),
        simplex=[line],
        display_shapes=geo_0,
        local_frame=Frame(point=(-3, 0, 0), xaxis=(1, 0, 0), yaxis=(0, 1, 0)),
        global_frame=Frame.worldXY(),
    )

    elem_1 = Element(
        element_type=ElementType.BLOCK,
        id=(0, 2),
        simplex=[line],
        display_shapes=geo_1,
        local_frame=Frame(point=(0, 0, 0), xaxis=(1, 0, 0), yaxis=(0, 1, 0)),
        global_frame=Frame.worldXY(),
    )

    elem_2 = Element(
        element_type=ElementType.BLOCK,
        id=(3, 0),
        simplex=[line],
        display_shapes=geo_2,
        local_frame=Frame(point=(3, 0, 0), xaxis=(1, 0, 0), yaxis=(0, 1, 0)),
        global_frame=Frame.worldXY(),
    )

    elements = [elem_0, elem_1, elem_2]
    for elem in elements:
        elem.get_aabb()
    Element.display(elements=elements, viewer_type="view2")

    # # print before updating the fabrication, assembly, and structural information
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

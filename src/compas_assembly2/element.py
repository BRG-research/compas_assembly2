from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import copy
from compas.geometry import (
    Frame,
    Geometry,
    Transformation,
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
from compas.datastructures import Datastructure
from compas.data import Data
from enum import Enum


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


class Element(Data):
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
        self.guid = None  # guid of the element
        self.id = (id,) if isinstance(id, int) else id  # tuple e.g. (0, 1) or (1, 5, 9)
        self.element_type = element_type  # type of the element, e.g., block, beam, plate, node, etc.
        self.attributes = {}  # set the attributes of an object
        self.attributes.update(kwargs)  # update the attributes of with the kwargs

        # minimal representation and geometrical shapes
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
    # DATA
    # ==========================================================================

    # jsonschema
    JSONSCHEMA = {
        "type": "object",
        "properties": {
            "element_type": {"type": "integer", "minimum": -0},
            # "id": {"type": "object"},
            # "local_frame": Frame.JSONSCHEMA,
            # "global_frame": Frame.JSONSCHEMA,
        },
        "required": [
            "element_type",
            # "id",
            # "local_frame",
            # "global_frame"
        ],
    }

    __slots__ = [
        "_element_type",
        # "_id",
        # "_local_frame",
        # "_global_frame",
    ]

    # data
    @property
    def data(self):
        data = {
            "element_type": self.element_type,
            # "id": self.id,
            # "local_frame": self.local_frame,
            # "global_frame": self.global_frame,
        }
        return data

    @data.setter
    def data(self, data):
        self.element_type = data.get("element_type") or ElementType.BLOCK
        # self.id = data.get("id") or (0, 1)
        # self.local_frame = data.get("local_frame") or Frame.worldXY()
        # self.global_frame = data.get("global_frame") or Frame.worldXY()

    # json
    def to_json(self):
        """Returns a dictionary of structured data representing the graph that can be serialised to JSON format.

        This is effectively a post-processing step for the :meth:`to_data` method.

        Returns
        -------
        dict
            The serialisable structured data dictionary.

        See Also
        --------
        :meth:`from_jsondata`

        """
        data = self.data

        return data

    @classmethod
    def from_jsondata(cls, data):
        """Construct a graph from structured data representing the graph in JSON format.

        This is effectively a pre-processing step for the :meth:`from_data` method.

        Parameters
        ----------
        data : dict
            The structured data dictionary.

        Returns
        -------
        :class:`~compas.datastructures.Graph`
            The constructed graph.

        See Also
        --------
        :meth:`to_jsondata`

        """
        # _node = data["node"] or {}
        # _edge = data["edge"] or {}
        # # process the nodes
        # node = {literal_eval(key): attr for key, attr in iter(_node.items())}
        # data["node"] = node
        # # process the edges
        # edge = {}
        # for u, nbrs in iter(_edge.items()):
        #     nbrs = nbrs or {}
        #     u = literal_eval(u)
        #     edge[u] = {}
        #     for v, attr in iter(nbrs.items()):
        #         attr = attr or {}
        #         v = literal_eval(v)
        #         edge[u][v] = attr
        # data["edge"] = edge
        return cls.from_data(data)

    @property
    def guid(self):
        return self._guid

    @guid.setter
    def guid(self, value):
        self._guid = value


    # ==========================================================================
    # PROPERTIES
    # ==========================================================================
    def get_aabb(self, inflate=0.00, compute_oobb=True, compute_convex_hull=False):

        # iterate display_shapes  and get the bounding box by geometry type
        # Mesh, Polyline, Box, Line
        points = []
        points_bbox = []

        for i in range(len(self.display_shapes)):
            corners = []
            if isinstance(self.display_shapes[i], Mesh):
                corners = mesh_bounding_box(self.display_shapes[i])
                if compute_convex_hull or compute_oobb:
                    points.extend(list(self.display_shapes[i].vertices_attributes("xyz")))
            elif isinstance(self.display_shapes[i], Polyline):
                corners = bounding_box(self.display_shapes[i])
                if compute_convex_hull or compute_oobb:
                    points.extend(self.display_shapes[i])
            elif isinstance(self.display_shapes[i], Line):
                corners = [self.display_shapes[i].start, self.display_shapes[i].end]
                if compute_convex_hull or compute_oobb:
                    points.extend(corners)
            elif isinstance(self.display_shapes[i], Box):
                points = self.display_shapes[i].points
                corners = bounding_box(points)
                if compute_convex_hull or compute_oobb:
                    points.extend(points)
            elif isinstance(self.display_shapes[i], Pointcloud):
                corners = bounding_box(self.display_shapes[i].points)
                points.extend(self.display_shapes[i].points)

            if len(corners) == 8:
                points_bbox.extend([corners[0], corners[6]])
            elif len(corners) == 2:
                points_bbox.extend(corners)
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
        if self.local_frame != Frame.worldXY:
            xform = Transformation.from_frame_to_frame(self.local_frame, Frame.worldXY())
            xform_inv = xform.inverse()

            self._oobb = []
            for i in range(len(points)):
                point = Point(*points[i])
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
            faces = convex_hull(points)
            self._convex_hull = Mesh.from_vertices_and_faces(points, faces)
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

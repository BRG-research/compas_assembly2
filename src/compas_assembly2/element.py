import compas
from compas.geometry import (
    Frame,
    Vector,
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
from compas.datastructures import Mesh, mesh_bounding_box
from compas.data import Data
import copy
import compas_assembly2


class Element(Data):

    # ==========================================================================
    # CONSTRUCTORS (INPUT)
    # ==========================================================================
    """Class representing a structural object of an assembly.

    This class defines structural elements used in an assembly.
    Each element is defined by inputs: an ID, attributes, geometrical shape, orientation frames.
    Additionally, it stores output dictionaries for fabrication, and structural information.

    Parameters
    ----------
        name (str): The name of the element, e.g., "BLOCK", "BEAM" and etc.
        id (list[int] or int): A unique identifier as a list, e.g.,[0] or [0, 1] or [1, 5, 9].
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
                name=compas_assembly2.ELEMENT_NAME.BLOCK,
                id=[0, 1],
                display_shapes =[],
                local_frame=Frame(point=(0, 0, 0), xaxis=(1, 0, 0), yaxis=(0, 1, 0)),
                global_frame=Frame.worldXY(),
                width=10,
                height=50,
                length=95,
            )

            # print before updating the fabrication, and structural information
            print(elem)

            # Update fabrication information
            elem.fabrication["cut"] = True
            elem.fabrication["drill"] = False
            elem.fabrication["insertion_sequence"] = [1, 2, 3, 4]
            elem.fabrication["printing_toolpath"] = [(0, 0, 1), (0, 0, 0)]

            # Update structural information
            elem.structure["nodes"] = [(0, 0, 1), (0, 0, 0)]

            # print after updating the fabrication, and structural information
            print(elem)
    """

    def __init__(
        self,
        name=compas_assembly2.ELEMENT_NAME.CUSTOM,
        id=[-1],
        simplex=[],
        display_shapes=[],
        local_frame=Frame.worldXY,
        global_frame=Frame.worldXY,
        **kwargs
    ):
        # --------------------------------------------------------------------------
        # call the inherited Data constructor for json serialization
        # --------------------------------------------------------------------------
        super(Element, self).__init__()

        # --------------------------------------------------------------------------
        # indexing + attributes
        # --------------------------------------------------------------------------
        self.id = (
            [
                id,
            ]
            if isinstance(id, int)
            else id
        )  # tuple e.g. (0, 1) or (1, 5, 9)
        self.name = name  # name of the element, e.g., block, beam, plate, node, etc.
        self.attributes = {}  # set the attributes of an object
        self.attributes.update(kwargs)  # update the attributes of with the kwargs

        # --------------------------------------------------------------------------
        # minimal representation and geometrical shapes
        # iterate through the input geometry
        # check if they are valid geometry objects
        # duplicate them and add them geometry list to avoid transformation issues
        # --------------------------------------------------------------------------
        self.simplex = []  # geometry, can be meshes, breps, curves, points, etc.

        if isinstance(simplex, list):
            # list of numbers, means user gives a point
            if isinstance(simplex[0], (int, float, complex)) and len(simplex) == 3:
                self.simplex.append(Point(simplex[0], simplex[1], simplex[2]))
            # else user gives geometries
            else:
                for g in simplex:
                    if isinstance(g, Geometry) or isinstance(g, Mesh):
                        self.simplex.append(g.copy())
                    elif isinstance(g, list):
                        if len(g) == 3:
                            self.simplex.append(Point(g[0], g[1], g[2]))
        else:
            # one geometry object
            if isinstance(simplex, Geometry):
                self.simplex.append(simplex.copy())

        if (len(simplex) == 0):
            raise AssertionError("User must define a simple geometry")

        # --------------------------------------------------------------------------
        # display geometry - geometry, can be meshes, breps, curves, points, etc.
        # --------------------------------------------------------------------------
        self.display_shapes = []
        if (display_shapes):
            for g in display_shapes:
                if isinstance(g, Geometry) or isinstance(g, Mesh):
                    self.display_shapes.append(g.copy())

        # --------------------------------------------------------------------------
        # orientation frames
        # if user does not give a frame, try to define it based on simplex
        # --------------------------------------------------------------------------
        if isinstance(local_frame, Frame):
            self.local_frame = Frame.copy(local_frame)
        else:
            origin = [0, 0, 0]
            if (isinstance(self.simplex[0], Point)):
                origin = self.simplex[0]
            elif (isinstance(self.simplex[0], Line)):
                origin = self.simplex[0].start
            elif (isinstance(self.simplex[0], Polyline)):
                origin = self.simplex[0][0]
            self.local_frame = Frame(origin, [1, 0, 0], [0, 1, 0])

        self.global_frame = (
            Frame.copy(global_frame) if isinstance(global_frame, Frame) else Frame([0, 0, 0], [1, 0, 0], [0, 1, 0])
        )  # set the global frame of an object

        # --------------------------------------------------------------------------
        # collision detection, these members are private access them using getters
        # --------------------------------------------------------------------------
        self._aabb = []  # XYZ coordinates of 8 points defining a box
        self._oobb = []  # XYZ coordinates of 8 points defining a box
        self._convex_hull = Mesh()  # convex hull of the geometry
        self._outlines = []  # closed polylines - in majority of cases objects will have planar faces
        self._outlines_frames = []  # closed polylines planes - in majority of cases objects will have planar faces

        # --------------------------------------------------------------------------
        # output for further processing
        # --------------------------------------------------------------------------
        self.fabrication = {}
        self.structure = {}

    # ==========================================================================
    # DATA
    # element_type=ElementType.BLOCK,
    # id=(0, 1),
    # simplex=[],
    # display_shapes=[],
    # local_frame=Frame.worldXY,
    # global_frame=Frame.worldXY,
    # ==========================================================================
    # create the data object from the class properties
    @property
    def data(self):
        # call the inherited Data constructor for json serialization
        data = {
            "name": self.name,
            "id": self.id,
            "simplex": self.simplex,
            "display_shapes": self.display_shapes,
            "local_frame": self.local_frame,
            "global_frame": self.global_frame,
            "attributes": self.attributes,
        }

        # custom properties
        data["aabb"] = self._aabb
        data["oobb"] = self._oobb
        data["convex_hull"] = self._convex_hull
        data["outlines"] = self._outlines
        data["outlines_frames"] = self._outlines_frames

        # fabrication | structure
        data["fabrication"] = self.fabrication
        data["structure"] = self.structure

        # return the data object
        return data

    # vice versa - create the class properties from the data object
    @data.setter
    def data(self, data):
        # call the inherited Data constructor for json serialization

        # main properties
        self.name = data["name"]
        self.id = data["id"]

        self.simplex = data["simplex"]
        self.display_shapes = data["display_shapes"]
        self.local_frame = data["local_frame"]
        self.global_frame = data["global_frame"]
        self.attributes = data["attributes"]

        # custom properties
        self._aabb = data["aabb"]
        self._oobb = data["oobb"]
        self._convex_hull = data["convex_hull"]
        self._outlines = data["outlines"]
        self._outlines_frames = data["outlines_frames"]

        # fabrication | structure
        self.fabrication = data["fabrication"]
        self.structure = data["structure"]

    @classmethod
    def from_data(cls, data):
        """Alternative to None default __init__ parameters."""
        obj = Element(
            name=data["name"],
            id=data["id"],
            simplex=data["simplex"],
            display_shapes=data["display_shapes"],
            local_frame=data["local_frame"],
            global_frame=data["global_frame"],
            **data["attributes"],
        )

        # custom properties
        obj._aabb = data["aabb"]
        obj._oobb = data["oobb"]
        obj._convex_hull = data["convex_hull"]
        obj._outlines = data["outlines"]
        obj._outlines_frames = data["outlines_frames"]

        # fabrication | structure

        obj.fabrication = data["fabrication"]
        obj.structure = data["structure"]

        # return the object
        return obj

    # ==========================================================================
    # PROPERTIES
    # ==========================================================================
    def get_aabb(self, inflate=0.00):

        # if the aabb is already computed return it
        if self._aabb:
            return self._aabb

        # iterate display_shapes  and get the bounding box by geometry name
        # Mesh, Polyline, Box, Line
        points_bbox = []

        for i in range(len(self.display_shapes)):
            if isinstance(self.display_shapes[i], Mesh):
                corners = mesh_bounding_box(self.display_shapes[i])
                points_bbox.extend([corners[0], corners[6]])
            elif isinstance(self.display_shapes[i], Polyline):
                corners = bounding_box(self.display_shapes[i])
                points_bbox.extend([corners[0], corners[6]])
            elif isinstance(self.display_shapes[i], Line):
                points_bbox.extend([self.display_shapes[i].start, self.display_shapes[i].end])
            elif isinstance(self.display_shapes[i], Box):
                corners = bounding_box(self.display_shapes[i].points)
                points_bbox.extend([corners[0], corners[6]])
            elif isinstance(self.display_shapes[i], Pointcloud):
                corners = bounding_box(self.display_shapes[i].points)
                points_bbox.extend([corners[0], corners[6]])

        # if no points found, return
        if len(points_bbox) < 2:
            if (inflate > 0.00):
                self._aabb = bounding_box([
                    self.local_frame.point+Vector(inflate, inflate, inflate),
                    self.local_frame.point-Vector(inflate, inflate, inflate)])
                return self._oobb
            else:
                return None

        # compute axis-aligned-bounding-box of all objects
        points_bbox = bounding_box(points_bbox)
        self._aabb = bounding_box(
            [
                [points_bbox[0][0] - inflate, points_bbox[0][1] - inflate, points_bbox[0][2] - inflate],
                [points_bbox[6][0] + inflate, points_bbox[6][1] + inflate, points_bbox[6][2] + inflate],
            ]
        )

        # return the aabb (8 points)
        return self._aabb

    def get_oobb(self, inflate=0.00):

        # if the oobb is already computed return it
        if self._oobb:
            return self._oobb

        # iterate display_shapes and get the bounding box by geometry name
        # Mesh, Polyline, Box, Line
        points = []

        for i in range(len(self.display_shapes)):

            if isinstance(self.display_shapes[i], Mesh):
                points.extend(list(self.display_shapes[i].vertices_attributes("xyz")))
            elif isinstance(self.display_shapes[i], Polyline):
                points.extend(self.display_shapes[i])
            elif isinstance(self.display_shapes[i], Line):
                points.extend([self.display_shapes[i].start, self.display_shapes[i].end])
            elif isinstance(self.display_shapes[i], Box):
                points.extend(self.display_shapes[i].points)
            elif isinstance(self.display_shapes[i], Pointcloud):
                points.extend(self.display_shapes[i].points)

        # if no points found, return
        if len(points) < 2:
            if (inflate > 0.00):
                self._oobb = bounding_box([
                    self.local_frame.point+Vector(inflate, inflate, inflate),
                    self.local_frame.point-Vector(inflate, inflate, inflate)])
                return self._oobb
            else:
                return None

        # compute the object-oriented-bounding-box
        # transforming points from local frame to worldXY
        # compute the bbox
        # orient the points back to the local frame
        xform = Transformation.from_frame_to_frame(self.local_frame, Frame.worldXY())
        xform_inv = xform.inverse()

        self._oobb = []
        for i in range(len(points)):
            point = Point(*points[i])
            point.transform(xform)
            self._oobb.append(point)
        self._oobb = bounding_box(self._oobb)

        # inflate the oobb
        self._oobb = bounding_box(
            [
                [self._oobb[0][0] - inflate, self._oobb[0][1] - inflate, self._oobb[0][2] - inflate],
                [self._oobb[6][0] + inflate, self._oobb[6][1] + inflate, self._oobb[6][2] + inflate],
            ]
        )

        # orient the points back to the local frame
        for i in range(len(self._oobb)):
            point = Point(*self._oobb[i])
            point.transform(xform_inv)
            self._oobb[i] = list(point)

        # return the oobb  (8 points)
        return self._oobb

    def get_convex_hull(self):

        # if the convex hull is already computed return it
        if self._convex_hull.is_empty() is False:
            return self._convex_hull

        # iterate display_shapes and get the bounding box by geometry name
        # Mesh, Polyline, Box, Line
        points = []

        for i in range(len(self.display_shapes)):
            if isinstance(self.display_shapes[i], Mesh):
                points.extend(list(self.display_shapes[i].vertices_attributes("xyz")))
            elif isinstance(self.display_shapes[i], Polyline):
                points.extend(self.display_shapes[i])
            elif isinstance(self.display_shapes[i], Line):
                points.extend([self.display_shapes[i].start, self.display_shapes[i].end])
            elif isinstance(self.display_shapes[i], Box):
                points.extend(self.display_shapes[i].points)
            elif isinstance(self.display_shapes[i], Pointcloud):
                points.extend(self.display_shapes[i].points)

        # if no points found, return
        if len(points) < 2:
            return Mesh()

        # compute the convex hull
        # use it with caution, it does not work, specially with coplanar points

        if len(points) > 2:
            faces = convex_hull(points)
            self._convex_hull = Mesh.from_vertices_and_faces(points, faces)
            return self._convex_hull
        else:
            self._convex_hull = Mesh()
            return self._convex_hull

    # ==========================================================================
    # GEOMETRIC FEATURES E.G. JOINERY. INTERFACES
    # ==========================================================================
    def clear_features(self, features_to_clear=None):
        """Clear all features from this Part."""
        # raise NotImplementedError
        pass

    def add_feature(self, feature, apply=False):
        """Add a Feature to this Part.

        Parameters
        ----------
        feature : :class:`~compas.assembly.Feature`
            The feature to add
        apply : :bool:
            If True, feature is also applied. Otherwise, feature is only added and user must call `apply_features`.

        Returns
        -------
        None
        """
        # raise NotImplementedError
        pass

    # ==========================================================================
    # PROPERTIES FOR DIGITAL FABRICATION (OUTPUT)
    # ==========================================================================

    def get_fabrication(self, key):
        pass

    def get_structure(self, key):
        pass

    # ==========================================================================
    # CONVERSIONS
    # ==========================================================================
    @staticmethod
    def to_elements(simplices=[], display_shapes=None, compute_nesting=1):
        """ convert a list of geometries to elements, with assumtion that other property will be filled later """
        elements = []
        contains_display_shapes = display_shapes is list

        for id, s in enumerate(simplices):
            if (contains_display_shapes):
                elements.append(Element.to_element(s, display_shapes[id % len(display_shapes)]))
            else:
                elements.append(Element.to_element(s))

        if (compute_nesting > 0):
            # nest elements linearly and add the the nest frame to the fabrication
            # first compute the bounding box of the elements, get the horizontal length, and create frames
            nest_type = compute_nesting
            width = {}
            height = {}
            height_step = 4
            inflate = 0.1

            for e in elements:
                e.get_aabb(inflate)
                e.get_oobb(inflate)
                e.get_convex_hull()

            center = Point(0, 0, 0)
            for e in elements:
                center = center + e.local_frame.point
            center = center / len(elements)

            for e in elements:
                width[e.name] = 0

            for index, (key, value) in enumerate(width.items()):
                height[key] = index * height_step * 0

            for i, e in enumerate(elements):

                temp_width = 0
                source_frame = e.local_frame.copy()
                target_frame = Frame([0, 0, 0], source_frame.xaxis, source_frame.yaxis)

                if nest_type == 1 and e.get_aabb() is not None:
                    # --------------------------------------------------------------------------
                    # aabb linear nesting
                    # --------------------------------------------------------------------------
                    temp_width = e.get_aabb()[6][0] - e.get_aabb()[0][0]
                    # get the maximum height of the elements
                    height[e.name] = max(height[e.name], e.get_aabb()[6][1] - e.get_aabb()[0][1])
                    source_frame = Frame(
                        e.get_aabb()[0],
                        [
                            e.get_aabb()[1][0] - e.get_aabb()[0][0],
                            e.get_aabb()[1][1] - e.get_aabb()[0][1],
                            e.get_aabb()[1][2] - e.get_aabb()[0][2],
                        ],
                        [
                            e.get_aabb()[3][0] - e.get_aabb()[0][0],
                            e.get_aabb()[3][1] - e.get_aabb()[0][1],
                            e.get_aabb()[3][2] - e.get_aabb()[0][2],
                        ],
                    )
                    target_frame = Frame([width[e.name], height[e.name], 0], [1, 0, 0], [0, 1, 0])
                elif nest_type == 2 and e.get_oobb() is not None:
                    # --------------------------------------------------------------------------
                    # oobb linear nesting
                    # --------------------------------------------------------------------------
                    temp_width = compas.geometry.distance_point_point(e.get_oobb()[0], e.get_oobb()[1])
                    # get the maximum height of the elements
                    height[e.name] = max(height[e.name],
                                         compas.geometry.distance_point_point(e.get_oobb()[0], e.get_oobb()[3]))
                    source_frame = Frame(
                        e.get_oobb()[0],
                        [
                            e.get_oobb()[1][0] - e.get_oobb()[0][0],
                            e.get_oobb()[1][1] - e.get_oobb()[0][1],
                            e.get_oobb()[1][2] - e.get_oobb()[0][2],
                        ],
                        [
                            e.get_oobb()[3][0] - e.get_oobb()[0][0],
                            e.get_oobb()[3][1] - e.get_oobb()[0][1],
                            e.get_oobb()[3][2] - e.get_oobb()[0][2],
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

                fabrication = compas_assembly2.Fabrication(
                    fabrication_type=compas_assembly2.FABRICATION_TYPES.NESTING, id=-1,
                    frames=[source_frame, target_frame]
                )
                e.fabrication[compas_assembly2.FABRICATION_TYPES.NESTING] = fabrication
                width[e.name] = width[e.name] + temp_width

            # --------------------------------------------------------------------------
            # center the frames
            # --------------------------------------------------------------------------
            h = 0
            for index, (key, value) in enumerate(width.items()):
                temp_height = height[key]
                height[key] = h
                h = h + temp_height

            for e in elements:
                e.fabrication[compas_assembly2.FABRICATION_TYPES.NESTING].frames[1].point.x = (
                    e.fabrication[compas_assembly2.FABRICATION_TYPES.NESTING].frames[1].point.x - width[e.name] * 0.5
                )
                e.fabrication[compas_assembly2.FABRICATION_TYPES.NESTING].frames[1].point.y = height[e.name] - h * 0.5

        # output
        return elements

    @staticmethod
    def to_element(simplex=None, display_shape=None):
        """ convert a geometry to an lement, with assumtion that other property will be filled later """
        return Element(simplex=simplex, display_shapes=display_shape)

    # ==========================================================================
    # COPY ALL GEOMETRY OBJECTS
    # ==========================================================================

    def copy(self):
        # copy main properties
        new_instance = self.__class__(
            self.name, self.id, self.display_shapes, self.local_frame, self.global_frame, **self.attributes
        )

        # deepcopy of the fabrication, and structural information
        new_instance.fabrication = copy.deepcopy(self.fabrication)
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

    def transform_to_frame(self, frame):
        """
        Applies frame_to_frame transformation to the display_shapes , local frame, and global frame of the Element.

        Parameters:
            frame (Frame): The target frame to which  the Element will be transformed.

        Returns:
            None
        """
        xform = Transformation.from_frame_to_frame(self.local_frame, frame)
        self.transform(xform)

    def transform_from_frame_to_frame(self, source_frame, target_frame):
        """
        Applies frame_to_frame transformation to the display_shapes , local frame, and global frame of the Element.

        Parameters:
            frame (Frame): The target frame to which  the Element will be transformed.

        Returns:
            None
        """
        xform = Transformation.from_frame_to_frame(source_frame, target_frame)
        self.transform(xform)

    def transformed_to_frame(self, frame):
        """
        Creates an oriented copy of the Element.

        Parameters:
            frame (Frame): The target frame to which the Element will be transformed.

        Returns:
            Element: A new instance of the Element with the specified orientation applied.
        """
        new_instance = self.copy()
        new_instance.transform_to_frame(frame)
        return new_instance

    def transformed_from_frame_to_frame(self, source_frame, target_frame):
        """
        Creates an oriented copy of the Element.

        Parameters:
            frame (Frame): The target frame to which the Element will be transformed.

        Returns:
            Element: A new instance of the Element with the specified orientation applied.
        """
        new_instance = self.copy()
        new_instance.transform_from_frame_to_frame(source_frame, target_frame)
        return new_instance

    # ==========================================================================
    # COLLISION DETECTION
    # ==========================================================================

    def collide(self, other):
        pass

    # ==========================================================================
    # DESCRIPTION
    # ==========================================================================

    def __repr__(self):
        """
        Return a string representation of the Element.

        Returns:
            str: The string representation of the Element.
        """
        return """
# (Type: {0},
#  ID: {1},
#  Minimal Representation Geometries: {2},
#  Vizualization Geometries: {3},
#  Local Frame: {4},
#  Global Frame: {5},
#  Fabrication: {6},
#  Structure: {7},
#  Attributes: {8})""".format(
            self.name,
            self.id,
            self.simplex,
            self.display_shapes,
            self.local_frame,
            self.global_frame,
            self.fabrication,
            self.structure,
            self.attributes,
        )

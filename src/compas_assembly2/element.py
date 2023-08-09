from compas.data import Data
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
    distance_point_point,
)
from compas.datastructures import Mesh, mesh_bounding_box
import copy
import compas_assembly2


class Element(Data):

    """Class representing a structural object of an assembly.

    Parameters
    ----------
        name : str
            e.g., "BLOCK", "BEAM", "FRAME"
            to be consistent majority of names are stored in compas_assembly2.ELEMENT_NAME class
        id : list[int] or int
            unique identifier/s , e.g.,0 or [0] or [0, 1] or [1, 5, 9].
            one object can have an index and belong to a group/s
        frame : :class:`~compas.geometry.Frame`
            local frame of the element
            there is also a global frame stored as an attribute
        simplex : list[:class:`~compas.geometry.Polyline`]
            minimal geometrical represetation of an object
            type is a polyline since it can represent: a point, a line or a polyline
        complex : list[any]
            a list of geometries used for the element visualization
            currently supported types: :class:`~compas.geometry` or :class:`~compas.datastrcutures.Mesh`
        insertion : list[:class:`~compas.geometry.Vector`, int]
            direction of the element, often defined by a single vector (can be also a sequence)
            and an index in an insertion sequence
        kwargs (dict, optional):
            additional keyword arguments can be passed to the element.

    Attributes
    ----------
        frame_global : :class:`~compas.geometry.Frame`
            global plane that can be used for the element orientation in a larger assembly
        aabb : list[:class:`~compas.geometry.Point`]:
            a list of XYZ coordinates defining the bounding box for collision detection.
        oobb : list[:class:`~compas.geometry.Point`]:
            a list of XYZ coordinates defining the an oriented bounding box to the frame.
        convex_hull : list[:class:`~compas.datastrcutures.Mesh`]:
            a mesh computed from the complex geometries points
        area : float
            the surface are of an element based on complex geometry
        volume : float
            the volume of an element based on complex 3d geometry

    Examples
    --------
        >>> element = Element("BLOCK", 0, Frame.worldXY(), Point(0,0,0), \
                            Box(Frame.worldXY(), 1.0, 2.0, 3.0), \
                            [Vector(0, 0, 1), 0])
    """

    def __init__(self, name="block", id=[0], frame=None, simplex=None, complex=None, insertion=None, **kwargs):
        # --------------------------------------------------------------------------
        # call the inherited Data constructor for json serialization
        # --------------------------------------------------------------------------
        super(Element, self).__init__()

        # --------------------------------------------------------------------------
        # name
        # the string can be any string
        # but better use the existing container: compas_assembly2.ELEMENT_NAME.BLOCK
        # --------------------------------------------------------------------------
        if name is None:
            self.name = compas_assembly2.ELEMENT_NAME.CUSTOM
        self.name = name.upper()

        # --------------------------------------------------------------------------
        # indexing
        # indices are store as a list to keep grouping information e.g. [0,1]
        # --------------------------------------------------------------------------
        if id is None:
            self.id = [-1]
        self.id = [id] if isinstance(id, int) else id

        # --------------------------------------------------------------------------
        # orientation frames
        # if user does not give a frame, try to define it based on simplex
        # --------------------------------------------------------------------------
        if isinstance(frame, Frame):
            self.frame = Frame.copy(frame)
        else:
            origin = [0, 0, 0]
            if isinstance(simplex[0], Point):  # type: ignore
                origin = simplex[0]  # type: ignore
            elif isinstance(simplex[0], Line):  # type: ignore
                origin = simplex[0].start  # type: ignore
            elif isinstance(simplex[0], Polyline):  # type: ignore
                origin = simplex[0][0]  # type: ignore
            elif isinstance(simplex[0], (int, float)) and len(simplex) == 3:  # type: ignore
                origin = simplex
            self.frame = Frame(origin, [1, 0, 0], [0, 1, 0])

        # --------------------------------------------------------------------------
        # minimal representation and geometrical shapes
        # iterate through the input geometry
        # check if they are valid geometry objects
        # duplicate them and add them geometry list to avoid transformation issues
        # geometry, can be meshes, breps, curves, points, etc.
        # --------------------------------------------------------------------------
        self.simplex = []
        if simplex:
            if isinstance(simplex, list):
                # input - list of numbers, means user gives a point (most probably)
                if isinstance(simplex[0], (int, float)) and len(simplex) == 3:
                    self.simplex.append(Point(simplex[0], simplex[1], simplex[2]))
                # input - list of gometries
                else:
                    for g in simplex:
                        if isinstance(g, Geometry) or isinstance(g, Mesh):
                            self.simplex.append(g.copy())
                        elif isinstance(g, list):
                            if len(g) == 3:
                                self.simplex.append(Point(g[0], g[1], g[2]))
            else:
                # input - one geometry
                if isinstance(simplex, Geometry):
                    self.simplex.append(simplex.copy())

            if len(simplex) == 0:  # type: ignore
                raise AssertionError("User must define a simple geometry")

        # --------------------------------------------------------------------------
        # display geometry - geometry, can be meshes, breps, curves, pointcloud, etc.
        # --------------------------------------------------------------------------
        self.complex = []
        if complex:
            # input - list of gometries
            if isinstance(complex, list):
                for g in complex:
                    if isinstance(g, Geometry) or isinstance(g, Mesh):
                        self.complex.append(g.copy())
            # input - one geometry
            else:
                if isinstance(complex, Geometry) or isinstance(complex, Mesh):
                    self.complex.append(complex.copy())

        # --------------------------------------------------------------------------
        # insertion direction and index in a sequnece
        # the insertion direction can be a vector, but also a polyline, plane...
        # the index is always integer
        # --------------------------------------------------------------------------
        is_insertion_valid = False
        if insertion:
            if isinstance(insertion, list):
                # input - list of vector
                if len(insertion) == 1:
                    if isinstance(insertion[0], Vector):
                        self.insertion = [insertion[0], self.id[-1]]
                        is_insertion_valid = True
                # input - list of vector and index
                elif len(insertion) == 2:
                    if isinstance(insertion[0], Vector) and isinstance(insertion[1], (int, float)):
                        self.insertion = [insertion[0], insertion[1]]
                        is_insertion_valid = True
                # input - list of vector coordinates in one list
                elif len(insertion) == 3:
                    self.insertion = [Vector(insertion[0], insertion[1], insertion[2]), self.id[-1]]
                    is_insertion_valid = True
                # input - list of vector coordinates and id in one list
                elif len(insertion) == 4:
                    self.insertion = [Vector(insertion[0], insertion[1], insertion[2]), insertion[3]]
                    is_insertion_valid = True
            elif isinstance(insertion, Vector):
                # input - vector
                self.insertion = [insertion, self.id[-1]]
                is_insertion_valid = True

        if not is_insertion_valid:
            self.insertion = [Vector(0, 0, 1), self.id[-1]]

        # --------------------------------------------------------------------------
        # custom attributes given by the user
        # --------------------------------------------------------------------------
        self.attributes = {}  # set the attributes of an object
        self.attributes.update(kwargs)  # update the attributes of with the kwargs

        # --------------------------------------------------------------------------
        # compute aabb and oobb, since most of the time they are used
        # --------------------------------------------------------------------------
        self.aabb(0.00)
        self.oobb(0.00)

    # ==========================================================================
    # ATTRIBUTES
    # ==========================================================================

    @property
    def frame_global(self):
        """Frame that gives orientation of the element in the larger group of Elements"""

        # define this property dynamically in the class
        if not hasattr(self, "_frame_global"):
            self._frame_global = Frame([0, 0, 0], [1, 0, 0], [0, 1, 0])
        return self._frame_global

    @frame_global.setter
    def frame_global(self, value):
        """Frame that gives orientation of the element in the larger group of Elements"""
        self._frame_global = value

    def aabb(self, inflate=0.00):
        """Compute bounding box based on complex geometries points"""

        # define this property dynamically in the class
        if not hasattr(self, "_aabb"):
            self._aabb = []  # XYZ coordinates of 8 points defining a box

        # if the aabb is already computed return it
        # and the user does not give another inflation value
        if self._aabb and abs(inflate) < 0.001:
            return self._aabb

        # iterate complex  and get the bounding box by geometry name
        # Mesh, Polyline, Box, Line
        points_bbox = []

        for i in range(len(self.complex)):
            if isinstance(self.complex[i], Mesh):
                corners = mesh_bounding_box(self.complex[i])
                points_bbox.extend([corners[0], corners[6]])
            elif isinstance(self.complex[i], Polyline):
                corners = bounding_box(self.complex[i])
                points_bbox.extend([corners[0], corners[6]])
            elif isinstance(self.complex[i], Line):
                points_bbox.extend([self.complex[i].start, self.complex[i].end])
            elif isinstance(self.complex[i], Box):
                corners = bounding_box(self.complex[i].points)
                points_bbox.extend([corners[0], corners[6]])
            elif isinstance(self.complex[i], Pointcloud):
                corners = bounding_box(self.complex[i].points)
                points_bbox.extend([corners[0], corners[6]])

        # if no points found, return
        if len(points_bbox) < 2:
            if inflate > 0.00:
                self._aabb = bounding_box(
                    [
                        self.frame.point + Vector(inflate, inflate, inflate),  # type: ignore
                        self.frame.point - Vector(inflate, inflate, inflate),  # type: ignore
                    ]
                )
                return self._aabb
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

    def oobb(self, inflate=0.00):
        """Compute the oriented bounding box based on complex geometries points"""

        # define this property dynamically in the class
        if not hasattr(self, "_oobb"):
            self._oobb = []  # XYZ coordinates of 8 points defining a box

        # if the oobb is already computed return it
        # and the user does not give another inflation value
        if self._oobb and abs(inflate) < 0.001:
            return self._oobb

        # iterate complex and get the bounding box by geometry name
        # Mesh, Polyline, Box, Line
        points = []

        for i in range(len(self.complex)):
            if isinstance(self.complex[i], Mesh):
                points.extend(list(self.complex[i].vertices_attributes("xyz")))
            elif isinstance(self.complex[i], Polyline):
                points.extend(self.complex[i])
            elif isinstance(self.complex[i], Line):
                points.extend([self.complex[i].start, self.complex[i].end])
            elif isinstance(self.complex[i], Box):
                points.extend(self.complex[i].points)
            elif isinstance(self.complex[i], Pointcloud):
                points.extend(self.complex[i].points)

        # if no points found, return
        if len(points) < 2:
            if inflate > 0.00:
                self._oobb = bounding_box(
                    [
                        self.frame.point + Vector(inflate, inflate, inflate),  # type: ignore
                        self.frame.point - Vector(inflate, inflate, inflate),  # type: ignore
                    ]
                )
                return self._oobb
            else:
                return None

        # compute the object-oriented-bounding-box
        # transforming points from local frame to worldXY
        # compute the bbox
        # orient the points back to the local frame
        xform = Transformation.from_frame_to_frame(self.frame, Frame.worldXY())
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

    @property
    def convex_hull(self):
        """Compute convex hull from complex points"""

        # define this property dynamically in the class
        if not hasattr(self, "_convex_hull"):
            self._convex_hull = Mesh()

        # if the convex hull is already computed return it
        if self._convex_hull.is_empty() is False:
            return self._convex_hull

        # iterate complex and get the bounding box by geometry name
        # Mesh, Polyline, Box, Line
        points = []

        for i in range(len(self.complex)):
            if isinstance(self.complex[i], Mesh):
                points.extend(list(self.complex[i].vertices_attributes("xyz")))
            elif isinstance(self.complex[i], Polyline):
                points.extend(self.complex[i])
            elif isinstance(self.complex[i], Line):
                points.extend([self.complex[i].start, self.complex[i].end])
            elif isinstance(self.complex[i], Box):
                points.extend(self.complex[i].points)
            elif isinstance(self.complex[i], Pointcloud):
                points.extend(self.complex[i].points)

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

    @property
    def outlines(self):
        """Outlines of polygonal complex shapes e.g. mesh face outlines
        they are often made from polylines and polyline planes"""

        # define this property dynamically in the class
        if not hasattr(self, "_outlines"):
            self._outlines = []
        return self._outlines

    @property
    def fabrication(self):
        """Fabrication information e.g. subtractive, additive, nesting and etc"""

        # define this property dynamically in the class
        if not hasattr(self, "_fabrication"):
            self._fabrication = {}
        return self._fabrication

    @property
    def structure(self):
        """Structure information e.g. force vectors, minimal representation and etc"""

        # define this property dynamically in the class
        if not hasattr(self, "_structure"):
            self._structure = {}
        return self._structure

    # ==========================================================================
    # SERIALIZATION
    # ==========================================================================
    # create the data object from the class properties
    @property
    def data(self):
        # call the inherited Data constructor for json serialization
        data = {
            "name": self.name,
            "id": self.id,
            "frame": self.frame,
            "simplex": self.simplex,
            "complex": self.complex,
            "attributes": self.attributes,
        }

        # custom properties
        data["frame_global"] = self.frame_global
        data["aabb"] = self.aabb()
        data["oobb"] = self.oobb()
        data["convex_hull"] = self.convex_hull
        data["outlines"] = self.outlines
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
        self.frame = data["frame"]
        self.simplex = data["simplex"]
        self.complex = data["complex"]
        self.attributes = data["attributes"]

        # custom properties
        self._frame_global = data["frame_global"]
        self._aabb = data["aabb"]
        self._oobb = data["oobb"]
        self._convex_hull = data["convex_hull"]
        self._outlines = data["outlines"]
        self._fabrication = data["fabrication"]
        self._structure = data["structure"]

    @classmethod
    def from_data(cls, data):
        """Alternative to None default __init__ parameters."""
        obj = Element(
            name=data["name"],
            id=data["id"],
            frame=data["frame"],
            simplex=data["simplex"],
            complex=data["complex"],
            **data["attributes"],
        )

        # custom properties
        obj._frame_global = data["frame_global"]
        obj._aabb = data["aabb"]
        obj._oobb = data["oobb"]
        obj._convex_hull = data["convex_hull"]
        obj._outlines = data["outlines"]
        obj._fabrication = data["fabrication"]
        obj._structure = data["structure"]

        # return the object
        return obj

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
    # CONVERSIONS
    # ==========================================================================
    @staticmethod
    def to_elements(simplices=[], complexes=None):
        """convert a list of geometries to elements, with assumtion that other property will be filled later"""
        elements = []
        contains_complex = complexes is list

        for id, s in enumerate(simplices):
            if contains_complex:
                elements.append(Element.to_element(s, complexes[id % len(complexes)]))
            else:
                elements.append(Element.to_element(s))

        # output
        return elements

    @staticmethod
    def to_element(simplex=None, complex=None):
        """convert a geometry to an element, with assumtion that other property will be filled later"""
        return Element(simplex=simplex, complex=complex)

    # ==========================================================================
    # COPY ALL GEOMETRY OBJECTS
    # ==========================================================================

    def copy(self):
        # copy main properties
        new_instance = self.__class__(
            name=self.name, id=self.id, frame=self.frame, simplex=self.simplex, complex=self.complex, **self.attributes
        )

        # deepcopy of the fabrication, and structural information
        new_instance.frame_global = self.frame_global.copy()
        new_instance._aabb = copy.deepcopy(self.aabb())
        new_instance._oobb = copy.deepcopy(self.oobb())
        new_instance._convex_hull = copy.deepcopy(self.convex_hull)
        new_instance._outlines = copy.deepcopy(self.outlines)
        new_instance._fabrication = copy.deepcopy(self.fabrication)
        new_instance._structure = copy.deepcopy(self.structure)

        return new_instance

    # ==========================================================================
    # TRANSFORMATIONS
    # ==========================================================================

    def transform(self, transformation):
        """
        Transforms the complex , local frame, and global frame of the Element.

        Parameters:
            transformation (Transformation): The transformation to be applied to the Element's geometry and frames.

        Returns:
            None
        """

        # transorm the geometry
        self.frame.transform(transformation)
        self.frame_global.transform(transformation)

        for i in range(len(self.simplex)):
            self.simplex[i].transform(transformation)

        for i in range(len(self.complex)):
            self.complex[i].transform(transformation)

        # recompute the bounding-box
        self._aabb.clear()
        self.aabb()

        # transform the oobb and convex-hull
        self.oobb()
        for i in range(len(self._oobb)):
            p = Point(self._oobb[i][0], self._oobb[i][1], self._oobb[i][2]).transformed(transformation)
            self._oobb[i] = [p.x, p.y, p.z]

        if self.convex_hull:
            if self.convex_hull.number_of_vertices() > 0:
                self.convex_hull.transform(transformation)

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
        Applies frame_to_frame transformation to the complex , local frame, and global frame of the Element.

        Parameters:
            frame (Frame): The target frame to which  the Element will be transformed.

        Returns:
            None
        """
        xform = Transformation.from_frame_to_frame(self.frame, frame)
        self.transform(xform)

    def transform_from_frame_to_frame(self, source_frame, target_frame):
        """
        Applies frame_to_frame transformation to the complex , local frame, and global frame of the Element.

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
    # COLLISION DETECTIONblock
    # ==========================================================================

    def collide(self, other, **kwargs):
        """check collision using aabb and oobb
        this function is often intermediate between high-performance tree searches
        then this collision is computed
        and then the interface can be found"""

        # --------------------------------------------------------------------------
        # sanity check
        # --------------------------------------------------------------------------
        if (not self.aabb()) or (not other.aabb()):
            return False

        # --------------------------------------------------------------------------
        # aabb collision
        # --------------------------------------------------------------------------
        collision_x_axis = self._aabb[6][0] < other._aabb[0][0] or other._aabb[6][0] < self._aabb[0][0]  # type: ignore
        collision_y_axis = self._aabb[6][1] < other._aabb[0][1] or other._aabb[6][1] < self._aabb[0][1]  # type: ignore
        collision_z_axis = self._aabb[6][2] < other._aabb[0][2] or other._aabb[6][2] < self._aabb[0][2]  # type: ignore
        aabb_collision = not (collision_x_axis or collision_y_axis or collision_z_axis)
        # print("aabb_collison", aabb_collision)
        if not aabb_collision:
            return False

        # --------------------------------------------------------------------------
        # oobb collision
        # https://discourse.mcneel.com/t/box-contains-box-check-for-coincident-boxes/59642/19
        # --------------------------------------------------------------------------

        # point, axis, size description
        class OBB:
            def to_p(self, p):
                return Point(p[0], p[1], p[2])

            def __init__(self, box=[]):
                origin = (self.to_p(box[0]) + self.to_p(box[6])) * 0.5
                x_axis = self.to_p(box[1]) - self.to_p(box[0])
                y_axis = self.to_p(box[3]) - self.to_p(box[0])
                self.frame = Frame(origin, x_axis, y_axis)
                self.half_size = [0.0, 0.0, 0.0]
                self.half_size[0] = distance_point_point(box[0], box[1]) * 0.5
                self.half_size[1] = distance_point_point(box[0], box[3]) * 0.5
                self.half_size[2] = distance_point_point(box[0], box[4]) * 0.5

        # convert the eight points to a frame and half-size description
        box1 = OBB(self._oobb)
        box2 = OBB(other._oobb)

        # get sepratation plane
        def GetSeparatingPlane(RPos, axis, box1, box2):
            # print(RPos, axis)
            return abs(RPos.dot(axis)) > (
                abs((box1.frame.xaxis * box1.half_size[0]).dot(axis))
                + abs((box1.frame.yaxis * box1.half_size[1]).dot(axis))
                + abs((box1.frame.zaxis * box1.half_size[2]).dot(axis))
                + abs((box2.frame.xaxis * box2.half_size[0]).dot(axis))
                + abs((box2.frame.yaxis * box2.half_size[1]).dot(axis))
                + abs((box2.frame.zaxis * box2.half_size[2]).dot(axis))
            )

        # compute the oobb collision
        RPos = box2.frame.point - box1.frame.point  # type: ignore

        result = not (
            GetSeparatingPlane(RPos, box1.frame.xaxis, box1, box2)
            or GetSeparatingPlane(RPos, box1.frame.yaxis, box1, box2)
            or GetSeparatingPlane(RPos, box1.frame.zaxis, box1, box2)
            or GetSeparatingPlane(RPos, box2.frame.xaxis, box1, box2)
            or GetSeparatingPlane(RPos, box2.frame.yaxis, box1, box2)
            or GetSeparatingPlane(RPos, box2.frame.zaxis, box1, box2)
            or GetSeparatingPlane(RPos, box1.frame.xaxis.cross(box2.frame.xaxis), box1, box2)  # type: ignore
            or GetSeparatingPlane(RPos, box1.frame.xaxis.cross(box2.frame.yaxis), box1, box2)  # type: ignore
            or GetSeparatingPlane(RPos, box1.frame.xaxis.cross(box2.frame.zaxis), box1, box2)  # type: ignore
            or GetSeparatingPlane(RPos, box1.frame.yaxis.cross(box2.frame.xaxis), box1, box2)  # type: ignore
            or GetSeparatingPlane(RPos, box1.frame.yaxis.cross(box2.frame.yaxis), box1, box2)  # type: ignore
            or GetSeparatingPlane(RPos, box1.frame.yaxis.cross(box2.frame.zaxis), box1, box2)  # type: ignore
            or GetSeparatingPlane(RPos, box1.frame.zaxis.cross(box2.frame.xaxis), box1, box2)  # type: ignore
            or GetSeparatingPlane(RPos, box1.frame.zaxis.cross(box2.frame.yaxis), box1, box2)  # type: ignore
            or GetSeparatingPlane(RPos, box1.frame.zaxis.cross(box2.frame.zaxis), box1, box2)  # type: ignore
        )

        # print("oobb_collison", result)
        return result

    def find_interface(self, other, **kwargs):
        """there are few possible cases
        a) an element touch other element by a flat face
        b) an element simplex is close to another simplex e.g. line to line proxity"""
        pass

    # ==========================================================================
    # MOST COMMON CONVERSIONS
    # ==========================================================================
    @staticmethod
    def from_simplex_and_complex(simplex, complex, id=-1):
        """method create a block element at the origin point with the frame at worldXY"""
        return Element(
            name=compas_assembly2.ELEMENT_NAME.BLOCK, id=id, frame=Frame.worldXY, simplex=simplex, complex=complex
        )

    @staticmethod
    def from_block(block):
        """method create a block element at the origin point with the frame at worldXY"""
        return Element(
            name=compas_assembly2.ELEMENT_NAME.BLOCK, id=0, frame=Frame.worldXY, simplex=Point(0, 0, 0), complex=block
        )

    @staticmethod
    def from_frame(width, height, depth):
        """method create a frame element at the origin point with the frame at worldXY"""
        return Element(
            name=compas_assembly2.ELEMENT_NAME.BLOCK,
            id=0,
            frame=Frame.worldXY,
            simplex=Line(Point(-width, 0, 0), Point(width, 0, 0)),
            complex=Box.from_width_height_depth(width, height, depth),
        )

    @staticmethod
    def from_plate(polylines):
        """method create a plate element at the origin point with the frame at worldXY"""
        return Element(
            name=compas_assembly2.ELEMENT_NAME.BLOCK, id=0, frame=Frame.worldXY, simplex=polylines, complex=polylines
        )

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
#  Outlines: {6},
#  Fabrication: {7},
#  Structure: {8},
#  Attributes: {9})""".format(
            self.name,
            self.id,
            self.simplex,
            self.complex,
            self.frame,
            self.frame_global,
            self.outlines,
            self.fabrication,
            self.structure,
            self.attributes,
        )

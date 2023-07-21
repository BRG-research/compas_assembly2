from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import copy
from compas.geometry import Frame, Geometry, Transformation, Polyline, Point, Box
from compas.datastructures import Mesh
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
        geometries (list, optional): A list of geometries. It can include meshes, breps, curves, points and etc.
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
                geometries=[],
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
        geometries=[],
        local_frame=Frame.worldXY,
        global_frame=Frame.worldXY,
        **kwargs,
    ):
        # indexing + attributes
        self.id = (id,) if isinstance(id, int) else id  # tuple e.g. (0, 1) or (1, 5, 9)
        self.element_type = element_type  # type of the element, e.g., block, beam, plate, node, etc.
        self.attributes = {}  # set the attributes of an object
        self.attributes.update(kwargs)  # update the attributes of with the kwargs

        # geometrical shape
        # iterate through the input geometry
        # check if they are valid geometry objects
        # duplicate them and add them geometry list to avoid transformation issues
        self.geometries = []  # geometry, can be meshes, breps, curves, points, etc.
        for g in geometries:
            if isinstance(g, Geometry) or isinstance(g, Mesh):
                self.geometries.append(g.copy())

        # collision detection
        self.aabb = []  # XYZ coordinates of 8 points defining a box
        self.oobb = []  # XYZ coordinates of 8 points defining a box
        self.convex_hull = Mesh()  # convex hull of the geometry

        # orientation

        self.local_frame = Frame.copy(local_frame) or Frame.worldXY()  # set the local frame of an object
        self.global_frame = Frame.copy(global_frame) or Frame.worldXY()  # set the global frame of an object

        # output for further processing
        self.fabrication = dict()
        self.assembly = dict()
        self.structure = dict()

    # ==========================================================================
    # PROPERTIES
    # ==========================================================================

    @property
    def get_aabb(self, compute_object_oriented_bounding_box=False, compute_convex_hull=False):
        # iterate geometries and get the bounding box
        for i in range(len(self.geometries)):
            pass

            # compute the object oriented bounding box
            if compute_object_oriented_bounding_box:
                pass

            # compute the convex hull
            if compute_object_oriented_bounding_box:
                pass

        return self.aabb

    def __repr__(self):
        """
        Return a string representation of the Element.

        Returns:
            str: The string representation of the Element.
        """
        return f"""
(Type: {self.element_type},
 ID: {self.id},
 Local Frame: {self.local_frame},
 Global Frame: {self.global_frame},
 Geometries: {self.geometries},
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
            self.element_type, self.id, self.geometries, self.local_frame, self.global_frame, **self.attributes
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
        Transforms the geometries, local frame, and global frame of the Element.

        Parameters:
            transformation (Transformation): The transformation to be applied to the Element's geometries and frames.

        Returns:
            None
        """
        for i in range(len(self.geometries)):
            self.geometries[i].transform(transformation)

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
        Applies frame_to_frame transformation to the geometries, local frame, and global frame of the Element.

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

    def display(self, viewer_type, key):
        pass


if __name__ == "__main__":
    mesh = Mesh.from_polyhedron(6)
    polyline = Polyline([(0, 0, 0), (1, 0, 0), (1, 1, 0)])
    # curve = cg.NurbsCurve(
    #     points=[(0, 0, 0), (1, 3, 0), (2, 3, 0), (3, 0, 0)],
    #     knots=[0, 0, 0, 1, 1, 1],
    #     degree=2,
    #     weights=[1.0, 1.0, 1.0, 1.0],
    # )
    point = Point(0, 0, 0)
    box = Box(Frame.worldXY(), 1, 1, 1)
    # brep = cg.Brep.from_box(box)
    geos = [
        mesh,
        polyline,
        point,
        box,
    ]

    elem = Element(
        element_type=ElementType.BLOCK,
        id=(0, 1),
        geometries=geos,
        local_frame=Frame(point=(0, 0, 0), xaxis=(1, 0, 0), yaxis=(0, 1, 0)),
        global_frame=Frame.worldXY(),
        width=10,
        height=50,
        length=95,
    )

    # print before updating the fabrication, assembly, and structural information
    # print(elem)

    # Update fabrication information
    elem.fabrication["cut"] = True
    elem.fabrication["drill"] = False

    # Update assembly information
    elem.assembly["inerstion_direction"] = (0, 0, 1)

    # Update structural information
    elem.structure["nodes"] = [(0, 0, 1), (0, 0, 0)]

    # print after updating the fabrication, assembly, and structural information
    # print(elem)

    print(elem)
    elem_copy = elem.copy()
    elem_copy.fabrication["cut"] = False
    print(elem_copy)

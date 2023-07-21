from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

# from compas.plugins import pluggable
# from compas.geometry import Geometry
# from compas.utilities import linspace

from compas.geometry import Frame
from enum import Enum


class ElementType(Enum):
    BLOCK = 1
    BEAM = 2
    BEAM_BENT = 3
    PLATE = 4
    PLATE_BENT = 5
    NODE = 6
    CUSTOM = 7


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
        geo (list, optional): A list of geometries. It can include meshes, breps, curves, points and etc.
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
                geo=[],
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
        geo=[],
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
        self.geo = geo  # geometry, can be meshes, breps, curves, points, etc.

        # collision detection
        self.bbox = []  # XYZ coordinates of 8 points defining a box

        # orientation
        self.local_frame = local_frame or Frame.worldXY()  # set the local frame of an object
        self.global_frame = global_frame or Frame.worldXY()  # set the global frame of an object

        # output for further processing
        self.fabrication = dict()
        self.assembly = dict()
        self.structure = dict()

    # ==========================================================================
    # PROPERTIES
    # ==========================================================================

    @property
    def get_bbox(self):
        pass

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

    def duplicate(self):
        pass

    # ==========================================================================
    # TRANSFORMATIONS
    # ==========================================================================

    def transform(self, transformation):
        pass

    def transformed(self, transformation):
        pass

    def orient(self, frame):
        pass

    def oriented(self, frame):
        pass

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


0

from compas.data import Data
from compas.geometry import Frame, Vector, Polyline, Point
from compas_assembly2 import FABRICATION_TYPES


class Fabrication(Data):
    """Fabrication data-structure for subtractive and additive processes

    it mainly should stores:
    a) the fabrication type
    b) index for the sequence
    c) frames for movement
    d) and commands for hardware control e.g. laser on/off, change of speed, tool-change etc.

    in reality these properties have to post-processed by the hardware control software, toolpath planner and etc.

    !!! do not inherit Fabrication class, use the Composition method instead !!!
    !!! multi-inheritance will lead to confusion, stay simple !!!
    !!! this is a just simple container that is stored inside each element
    !!! all the functionality should be implemented in the FabricationSomeName classes to would
    !!! would take multiple elements and distribute the fabrication objects between them

    if you would inherit it from Fabrication class, it would correspond to one object only,
    most often there is a case when multiple objects have to be used for one fabrication process
    a) drilling or cutting multiple objects by user given specification
    b) nesting
    c) 3d printing multiple elements in one batch
    d) generating joinery between two or more elements

    if you really have a special process you can fill **kwargs with your own attributes
    more simply this class stands as a container without functionality"""

    def __init__(self, fabrication_type=None, id=None, frames=None, **kwargs):

        # inherit from data
        super(Fabrication, self).__init__()

        self.type = fabrication_type or FABRICATION_TYPES.CUSTOM
        self.id = -1 if id is None else id
        self.frames = [] if frames is None else frames  # for movement
        self.commands = []  # for hardware control
        self.attributes = {}
        self.attributes.update(kwargs)

    # ==========================================================================
    # SERIALIZATION
    # ==========================================================================
    # create the data object from the class properties
    @property
    def data(self):
        # call the inherited Data constructor for json serialization
        data = {
            "type": self.type,
            "id": self.id,
            "frames": self.frames,
            "commands": self.commands,
            "attributes": self.attributes,
        }

        # return the data object
        return data

    # vice versa - create the class properties from the data object
    @data.setter
    def data(self, data):
        # call the inherited Data constructor for json serialization

        # main properties
        self.type = data["type"]
        self.id = data["id"]
        self.frames = data["frames"]
        self.commands = data["commands"]
        self.attributes = data["attributes"]

    @classmethod
    def from_data(cls, data):
        """Alternative to None default __init__ parameters."""
        obj = Fabrication(
            type=data["type"],
            id=data["id"],
            frames=data["frames"],
            commands=data["commands"],
            **data["attributes"],
        )

        # return the object
        return obj

    @staticmethod
    def perpendicular_to(_o, _v):
        v = Vector.from_start_end(_o, _v)
        i, j, k = 0, 0, 0
        a, b = 0.0, 0.0
        k = 2

        if abs(v.y) > abs(v.x):
            if abs(v.z) > abs(v.y):
                # |v.z| > |v.y| > |v.x|
                i = 2
                j = 1
                k = 0
                a = v.z
                b = -v.y
            elif abs(v.z) >= abs(v.x):
                # |v.y| >= |v.z| >= |v.x|
                i = 1
                j = 2
                k = 0
                a = v.y
                b = -v.z
            else:
                # |v.y| > |v.x| > |v.z|
                i = 1
                j = 0
                k = 2
                a = v.y
                b = -v.x
        elif abs(v.z) > abs(v.x):
            # |v.z| > |v.x| >= |v.y|
            i = 2
            j = 0
            k = 1
            a = v.z
            b = -v.x
        elif abs(v.z) > abs(v.y):
            # |v.x| >= |v.z| > |v.y|
            i = 0
            j = 2
            k = 1
            a = v.x
            b = -v.z
        else:
            # |v.x| >= |v.y| >= |v.z|
            i = 0
            j = 1
            k = 2
            a = v.x
            b = -v.y

        perp = Vector(0, 0, 0)
        perp[i] = b
        perp[j] = a
        perp[k] = 0.0
        return perp, v.cross(perp)
        # return True if a != 0.0 else False

    @staticmethod
    def from_line(polyline):

        if polyline:
            points = []
            counter = 0
            for p in polyline:
                if counter == 2:
                    break
                counter = counter + 1
                points.append(Point(p[0], p[1], p[2]))

            if counter == 2:
                x_axis_vector, y_axis_vector = Fabrication.perpendicular_to(points[0], points[1])
                return Frame(points[0], x_axis_vector, y_axis_vector)
            else:
                return Frame([0, 0, 0], [1, 0, 0], [0, 1, 0])
        else:
            return Frame([0, 0, 0], [1, 0, 0], [0, 1, 0])

    @classmethod
    def create_insertion_sequence_from_polyline(cls, id=-1, polyline=None, xy_or_direction_orientation=True):
        """Create a fabrication sequence from a polyline"""

        if polyline is None:
            raise Exception("No polyline provided")

        frames = []
        if xy_or_direction_orientation or len(polyline.points) == 1:
            for i in range(len(polyline.points)):
                frames.append(Frame(polyline.points[i], [1, 0, 0], [0, 1, 0]))
        else:
            for i in range(len(polyline.points) - 1):
                polyline_segment = Polyline([polyline.points[i], polyline.points[i + 1]])
                frame = Fabrication.from_line(polyline_segment)
                frames.append(frame)

        return cls(type="fabrication_movement", id=id, frames=frames)

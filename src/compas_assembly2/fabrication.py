from compas.geometry import Frame, Vector, Polyline, Point


class FABRICATION_TYPES:
    MOVEMENT = "MOVEMENT_LINEAR"
    SUBTRACTION_DRILL = "SUBTRACTION_DRILL"
    SUBTRACTION_CUT = "SUBTRACTION_CUT"
    SUBTRACTION_MILL = "SUBTRACTION_MILL"
    SUBTRACTION_SLICE = "SUBTRACTION_SLICE"
    ADDITION_PRINT = "ADDITION_PRINT"
    ADDITION_SPRAY = "ADDITION_SPRAY"
    ADDITION_EXTRUDE = "ADDITION_EXTRUDE"
    NESTING = "NESTING"
    CUSTOM = "CUSTOM"


class Fabrication:
    """Fabrication data-structure for subtractive and additive processes"""

    def __init__(self, fabrication_type=None, id=None, frames=None, **kwargs):
        self.type = fabrication_type or FABRICATION_TYPES.CUSTOM
        self.id = id or (0)
        self.frames = frames or []
        self.attributes = {}
        self.attributes.update(kwargs)

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

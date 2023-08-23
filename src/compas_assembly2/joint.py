from compas.data import Data
from compas.geometry import Point, Line, centroid_points_weighted


class Joint(Data):
    """
    A data structure for representing joinery or interfaces between elements
    and managing their fabrication and structural properties.

    Parameters
    ----------
    polygon
    type
    frame
    surface_area
    forces
    toolpaths
    """

    def __init__(self, polygon=None, type=None, frame=None, surface_area=None, forces=None, toolpaths=None):
        super(Joint, self).__init__()

        # main properties
        self.type = type
        self.polygon = polygon
        self.frame = frame
        self.surface_area = surface_area

        # structure properties
        self.forces = forces

        # fabrication properties
        self.toolpaths = toolpaths

    # ==========================================================================
    # CONSTRUCTOR OVERLAODING
    # ==========================================================================

    # ==========================================================================
    # SERIALIZATION
    # ==========================================================================
    @property
    def data(self):
        return {
            "polygon": self.polygon,
            "type": self.type,
            "frame": self.frame,
            "surface_area": self.surface_area,
            "forces": self.forces,
            "toolpaths": self.toolpaths,
        }

    @data.setter
    def data(self, data):
        self.polygon = data["polygon"]
        self.type = data["type"]
        self.frame = data["frame"]
        self.surface_area = data["surface_area"]
        self.forces = data["forces"]
        self.toolpaths = data["toolpaths"]

    @classmethod
    def from_data(cls, data):
        """Construct an interface from a data dict.

        Parameters
        ----------
        data : dict
            The data dictionary.

        Returns
        -------
        :class:`compas_assembly.datastructures.Interface`

        """
        return cls(**data)

    # ==========================================================================
    # OPTIONAL PROPERTIES - FABRICATION
    # ==========================================================================
    def assign_joint(self, name, **kwargs):
        pass

    # ==========================================================================
    # OPTIONAL PROPERTIES - STRUCTURE
    # ==========================================================================
    @property
    def contact_forces(self):
        lines = []
        if not self.forces:
            return lines
        frame = self.frame
        w = frame.zaxis
        for point, force in zip(self.polygon.points, self.forces):
            point = Point(*point)
            force = force["c_np"] - force["c_nn"]
            p1 = point + w * force * 0.5
            p2 = point - w * force * 0.5
            lines.append(Line(p1, p2))
        return lines

    @property
    def compression_forces(self):
        lines = []
        if not self.forces:
            return lines
        frame = self.frame
        w = frame.zaxis
        for point, force in zip(self.polygon.points, self.forces):
            point = Point(*point)
            force = force["c_np"] - force["c_nn"]
            if force > 0:
                p1 = point + w * force * 0.5
                p2 = point - w * force * 0.5
                lines.append(Line(p1, p2))
        return lines

    @property
    def tension_forces(self):
        lines = []
        if not self.forces:
            return lines
        frame = self.frame
        w = frame.zaxis
        for point, force in zip(self.polygon.points, self.forces):
            point = Point(*point)
            force = force["c_np"] - force["c_nn"]
            if force < 0:
                p1 = point + w * force * 0.5
                p2 = point - w * force * 0.5
                lines.append(Line(p1, p2))
        return lines

    @property
    def friction_forces(self):
        lines = []
        if not self.forces:
            return lines
        frame = self.frame
        u, v = frame.xaxis, frame.yaxis
        for point, force in zip(self.polygon.points, self.forces):
            point = Point(*point)
            ft_uv = (u * force["c_u"] + v * force["c_v"]) * 0.5
            p1 = point + ft_uv
            p2 = point - ft_uv
            lines.append(Line(p1, p2))
        return lines

    @property
    def resultant_force(self):
        if not self.forces:
            return []
        frame = self.frame
        w, u, v = frame.zaxis, frame.xaxis, frame.yaxis
        normalcomponents = [f["c_np"] - f["c_nn"] for f in self.forces]
        sum_n = sum(normalcomponents)
        sum_u = sum(f["c_u"] for f in self.forces)
        sum_v = sum(f["c_v"] for f in self.forces)
        position = Point(*centroid_points_weighted(self.polygon.points, normalcomponents))
        forcevector = (w * sum_n + u * sum_u + v * sum_v) * 0.5
        p1 = position + forcevector
        p2 = position - forcevector
        return [Line(p1, p2)]

from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from math import radians
from compas.geometry import Rotation
from compas.geometry import add_vectors
from compas.geometry import subtract_vectors
from compas.geometry import transform_points
from compas.geometry import angle_vectors
from compas.geometry import Frame
from compas.geometry import Vector
from compas.datastructures import Mesh
from compas_assembly2 import Element, Model, ModelNode, ViewerModel


class Arch:
    """Create voussoir geometry for a semi-circular arch with given rise and span.

    Parameters
    ----------
    rise : float
        The distance between the base of the arch and the highest point of the intrados.
    span : float
        The distance between opposite intrados points at the base.
    thickness : float
        The distance between intrados and extrados.
    depth : float
        The depth of the arch.
    n : int

    """

    def __init__(self, rise, span, thickness, depth, n=None):
        super(Arch, self).__init__()
        self.rise = rise
        self.span = span
        self.thickness = thickness
        self.depth = depth
        self.n = n

    def blocks(self):
        """Compute the blocks.

        Returns
        -------
        list
            A list of blocks defined as simple meshes.

        Notes
        -----
        This method is used by the ``from_geometry`` constructor of the assembly data structure
        to create an assembly "from geometry".

        """
        if self.rise > self.span / 2:
            raise Exception("Not a semicircular arch.")

        radius = self.rise / 2 + self.span**2 / (8 * self.rise)
        # base = [0.0, 0.0, 0.0]
        top = [0.0, 0.0, self.rise]
        left = [-self.span / 2, 0.0, 0.0]
        center = [0.0, 0.0, self.rise - radius]
        my_vector = subtract_vectors(left, center)
        springing = angle_vectors(my_vector, [-1.0, 0.0, 0.0])
        sector = radians(180) - 2 * springing
        angle = sector / self.n

        a = top
        b = add_vectors(top, [0, self.depth, 0])
        c = add_vectors(top, [0, self.depth, self.thickness])
        d = add_vectors(top, [0, 0, self.thickness])

        R = Rotation.from_axis_and_angle([0, 1.0, 0], 0.5 * sector, center)
        bottom = transform_points([a, b, c, d], R)

        # --------------------------------------------------------------------------
        # blocks
        # --------------------------------------------------------------------------
        blocks = []
        elements = []
        for i in range(self.n):
            R = Rotation.from_axis_and_angle([0, 1.0, 0], -angle, center)
            top = transform_points(bottom, R)
            vertices = bottom + top
            faces = [
                [0, 1, 2, 3],
                [7, 6, 5, 4],
                [3, 7, 4, 0],
                [6, 2, 1, 5],
                [7, 3, 2, 6],
                [5, 1, 0, 4],
            ]
            mesh = Mesh.from_vertices_and_faces(vertices, faces)
            blocks.append(mesh)
            bottom = top
            mid_point = [
                (vertices[0][0] + vertices[6][0]) * 0.5,
                (vertices[0][1] + vertices[6][1]) * 0.5,
                (vertices[0][2] + vertices[6][2]) * 0.5,
            ]
            x_axis = Vector.from_start_end(vertices[1], vertices[0])
            y_axis = Vector.from_start_end(vertices[4], vertices[0])
            frame = Frame(mid_point, x_axis, y_axis)
            element = Element(simplex=mid_point, complex=[mesh], frame=frame)
            elements.append(element)

        # --------------------------------------------------------------------------
        # create model
        # --------------------------------------------------------------------------
        model = Model(name="arch")
        model.hierarchy.add(ModelNode("blocks", elements=elements))

        # --------------------------------------------------------------------------
        # add interactions
        # --------------------------------------------------------------------------
        for i in range(self.n - 1):
            model.add_interaction(model(i), model(i + 1))

        # --------------------------------------------------------------------------
        # output
        # --------------------------------------------------------------------------
        return model


if __name__ == "__main__":
    arch = Arch(rise=1, span=20, thickness=0.5, depth=10, n=5)
    model = arch.blocks()
    print(model)
    model.print()
    ViewerModel.run(model, scale_factor=1)

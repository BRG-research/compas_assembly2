from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from math import cos, sin, pi
from compas.geometry import Vector, Frame
from compas.datastructures import Mesh
from compas_assembly2 import Element, Model, Node, ViewerModel


def geom_dome(ro, theta, phi):
    x = ro * sin(theta) * cos(phi)
    y = ro * sin(theta) * sin(phi)
    z = ro * cos(theta)
    point = [x, y, z]
    return point


def radius(r_i, r_f, theta_upper, theta_lower, theta):
    r = r_i + (r_f - r_i) / (theta_upper - theta_lower) * theta
    return r


class Dome:
    """Create voussoirs for a spherical dome geometry with given rise and span.

    Parameters
    ----------

    """

    def __init__(
        self,
        meridians=40,
        hoops=20,
        oculus=pi / 30,
        spring=pi / 2,
        r_i=3.9,
        r_f=3.2,
        R_i=4,
        R_f=3.5,
    ):
        super(Dome, self).__init__()
        self.meridians = meridians
        self.hoops = hoops
        self.oculus = oculus
        self.spring = spring

        self.r_i = r_i
        self.r_f = r_f
        self.R_i = R_i
        self.R_f = R_f

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
        step_phi = (2 * pi - 0) / (2 * self.meridians)
        phi_delta = (2 * pi - 0) / self.meridians
        theta_delta = (self.spring - self.oculus) / self.hoops

        phi = []
        for i in range(self.meridians + 1):
            phi.append(0 + i * phi_delta)

        theta = []
        for i in range(self.hoops + 1):
            theta.append(self.oculus + i * theta_delta)

        # --------------------------------------------------------------------------
        # blocks
        # --------------------------------------------------------------------------

        blocks = []
        elements = []
        for j in range(self.meridians):
            for i in range(self.hoops):
                if i % 2 == 0:
                    step = 0
                else:
                    step = step_phi

                vertices = []

                r = radius(self.r_i, self.r_f, self.spring, self.oculus, theta[i])
                R = radius(self.R_i, self.R_f, self.spring, self.oculus, theta[i])

                vertices.append(geom_dome(r, theta[i], phi[j] + step))
                vertices.append(geom_dome(R, theta[i], phi[j] + step))
                vertices.append(geom_dome(R, theta[i], phi[j + 1] + step))
                vertices.append(geom_dome(r, theta[i], phi[j + 1] + step))

                r = radius(self.r_i, self.r_f, self.spring, self.oculus, theta[i + 1])
                R = radius(self.R_i, self.R_f, self.spring, self.oculus, theta[i + 1])

                vertices.append(geom_dome(r, theta[i + 1], phi[j] + step))
                vertices.append(geom_dome(R, theta[i + 1], phi[j] + step))
                vertices.append(geom_dome(R, theta[i + 1], phi[j + 1] + step))
                vertices.append(geom_dome(r, theta[i + 1], phi[j + 1] + step))

                faces = [
                    [0, 4, 5, 1],
                    [1, 5, 6, 2],
                    [0, 1, 2, 3],
                    [0, 3, 7, 4],
                    [5, 4, 7, 6],
                    [6, 7, 3, 2],
                ]

                block = Mesh.from_vertices_and_faces(vertices, faces)
                blocks.append(block)

                mid_point = [
                    (vertices[0][0] + vertices[6][0]) * 0.5,
                    (vertices[0][1] + vertices[6][1]) * 0.5,
                    (vertices[0][2] + vertices[6][2]) * 0.5,
                ]
                x_axis = Vector.from_start_end(vertices[3], vertices[0])
                y_axis = Vector.from_start_end(vertices[4], vertices[0])
                frame = Frame(mid_point, x_axis, y_axis)
                element = Element(geometry_simplified=[mid_point], geometry=[block], frame=frame)
                elements.append(element)

        # --------------------------------------------------------------------------
        # create model
        # --------------------------------------------------------------------------
        model = Model(name="arch")
        model.add_node(Node("blocks", elements=elements))

        # --------------------------------------------------------------------------
        # add interactions
        # -----------------------------------------
        # ---------------------------------
        # for i in range(self.n-1):
        #     model.add_interaction(model(i), model(i+1))

        # --------------------------------------------------------------------------
        # output
        # --------------------------------------------------------------------------
        return model


if __name__ == "__main__":
    # oculus=pi / 30,
    # spring=pi / 2,
    # r_i=3.9,
    # r_f=3.2,
    # R_i=4,
    # R_f=3.5,
    dome = Dome(meridians=20, hoops=5, oculus=pi / 30, spring=pi / 2)
    model = dome.blocks()
    print(model)
    model.print()
    ViewerModel.run(model, scale_factor=1)

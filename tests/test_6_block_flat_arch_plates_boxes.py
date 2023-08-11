from compas_assembly2 import Viewer, Element, FabricationNest
from compas.datastructures import Mesh
import compas
from compas.geometry import (
    Point,
    Line,
    Plane,
    Vector,
    intersection_plane_plane_plane,
)


class _:
    class Ear:
        """
        Represents an ear of a polygon. An ear is a triangle formed by three consecutive vertices of the polygon.
        """

        def __init__(self, points, indexes, ind):
            """
            Initialize an Ear instance.

            Args:
                points (list): List of vertex coordinates.
                indexes (list): List of vertex indexes.
                ind (int): Index of the current vertex.
            """
            self.index = ind
            self.coords = points[ind]
            length = len(indexes)
            index_in_indexes_arr = indexes.index(ind)
            self.next = indexes[(index_in_indexes_arr + 1) % length]
            if index_in_indexes_arr == 0:
                self.prew = indexes[length - 1]
            else:
                self.prew = indexes[index_in_indexes_arr - 1]
            self.neighbour_coords = [points[self.prew], points[self.next]]

        def is_inside(self, point):
            """
            Check if a given point is inside the triangle formed by the ear.

            Args:
                point (list): Coordinates of the point to check.

            Returns:
                bool: True if the point is inside the triangle, False otherwise.
            """
            p1 = self.coords
            p2 = self.neighbour_coords[0]
            p3 = self.neighbour_coords[1]
            p0 = point

            d = [
                (p1[0] - p0[0]) * (p2[1] - p1[1]) - (p2[0] - p1[0]) * (p1[1] - p0[1]),
                (p2[0] - p0[0]) * (p3[1] - p2[1]) - (p3[0] - p2[0]) * (p2[1] - p0[1]),
                (p3[0] - p0[0]) * (p1[1] - p3[1]) - (p1[0] - p3[0]) * (p3[1] - p0[1]),
            ]

            if d[0] * d[1] >= 0 and d[2] * d[1] >= 0 and d[0] * d[2] >= 0:
                return True
            return False

        def is_ear_point(self, p):
            """
            Check if a given point is one of the vertices of the ear triangle.

            Args:
                p (list): Coordinates of the point to check.

            Returns:
                bool: True if the point is a vertex of the ear triangle, False otherwise.
            """
            if p == self.coords or p in self.neighbour_coords:
                return True
            return False

        def validate(self, points, indexes, ears):
            """
            Validate if the ear triangle is a valid ear by checking its convexity and that no points lie inside.

            Args:
                points (list): List of vertex coordinates.
                indexes (list): List of vertex indexes.
                ears (list): List of other ear triangles.

            Returns:
                bool: True if the ear triangle is valid, False otherwise.
            """
            not_ear_points = [
                points[i] for i in indexes if points[i] != self.coords and points[i] not in self.neighbour_coords
            ]
            insides = [self.is_inside(p) for p in not_ear_points]
            if self.is_convex() and True not in insides:
                for e in ears:
                    if e.is_ear_point(self.coords):
                        return False
                return True
            return False

        def is_convex(self):
            """
            Check if the ear triangle is convex.

            Returns:
                bool: True if the ear triangle is convex, False otherwise.
            """
            a = self.neighbour_coords[0]
            b = self.coords
            c = self.neighbour_coords[1]
            ab = [b[0] - a[0], b[1] - a[1]]
            bc = [c[0] - b[0], c[1] - b[1]]
            if ab[0] * bc[1] - ab[1] * bc[0] <= 0:
                return False
            return True

        def get_triangle(self):
            """
            Get the indices of the vertices forming the ear triangle.

            Returns:
                list: List of vertex indices forming the ear triangle.
            """
            return [self.prew, self.index, self.next]

    class Earcut:
        """
        A class for triangulating a simple polygon using the ear-cutting algorithm.
        """

        def __init__(self, points):
            """
            Initialize an Earcut instance with the input points.

            Args:
                points (list): List of vertex coordinates forming the polygon.
            """
            self.vertices = points
            self.ears = []
            self.neighbours = []
            self.triangles = []
            self.length = len(points)

        def update_neighbours(self):
            """
            Update the list of neighboring vertices.
            """
            neighbours = []
            self.neighbours = neighbours

        def add_ear(self, new_ear):
            """
            Add a new ear to the list of ears and update neighboring vertices.

            Args:
                new_ear (Ear): The new ear triangle to be added.
            """
            self.ears.append(new_ear)
            self.neighbours.append(new_ear.prew)
            self.neighbours.append(new_ear.next)

        def find_ears(self):
            """
            Find valid ear triangles among the vertices and add them to the ears list.
            """
            i = 0
            indexes = list(range(self.length))
            while True:
                if i >= self.length:
                    break
                new_ear = _.Ear(self.vertices, indexes, i)
                if new_ear.validate(self.vertices, indexes, self.ears):
                    self.add_ear(new_ear)
                    indexes.remove(new_ear.index)
                i += 1

        def triangulate(self):
            """
            Triangulate the polygon using the ear-cutting algorithm.
            """
            indexes = list(range(self.length))
            self.find_ears()

            num_of_ears = len(self.ears)

            if num_of_ears == 0:
                raise ValueError("No ears found for triangulation.")
            if num_of_ears == 1:
                self.triangles.append(self.ears[0].get_triangle())
                return

            while True:
                if len(self.ears) == 2 and len(indexes) == 4:
                    self.triangles.append(self.ears[0].get_triangle())
                    self.triangles.append(self.ears[1].get_triangle())
                    break

                if len(self.ears) == 0:
                    raise IndexError("Unable to find more ears for triangulation.")
                current = self.ears.pop(0)

                indexes.remove(current.index)
                self.neighbours.remove(current.prew)
                self.neighbours.remove(current.next)

                self.triangles.append(current.get_triangle())

                # Check if prew and next vertices form new ears
                prew_ear_new = _.Ear(self.vertices, indexes, current.prew)
                next_ear_new = _.Ear(self.vertices, indexes, current.next)
                if (
                    prew_ear_new.validate(self.vertices, indexes, self.ears)
                    and prew_ear_new.index not in self.neighbours
                ):
                    self.add_ear(prew_ear_new)
                    continue
                if (
                    next_ear_new.validate(self.vertices, indexes, self.ears)
                    and next_ear_new.index not in self.neighbours
                ):
                    self.add_ear(next_ear_new)
                    continue

    class Triagulator:
        @staticmethod
        def _get_frame(_points, _orientation_point=None):
            """create a frame from a polyline"""

            # create a normal by averaging the cross-products of a polyline
            normal = compas.geometry.Vector(0, 0, 0)
            count = len(_points)
            center = compas.geometry.Point(0, 0, 0)
            is_closed = (
                compas.geometry.distance_point_point(
                    compas.geometry.Point(*_points[0]), compas.geometry.Point(*_points[-1])
                )
                < 0.01
            )
            sign = 1 if is_closed else 0

            for i in range(count - sign):
                num = ((i - 1) + count - sign) % (count - sign)
                item1 = ((i + 1) + count - sign) % (count - sign)
                point3d = _points[num]
                point3d1 = _points[item1]
                item2 = _points[i]
                normal += compas.geometry.cross_vectors(item2 - point3d, point3d1 - item2)
                center = center + point3d
            normal.unitize()
            center = center / count

            # get the longest edge
            longest_segment_length = 0.0
            longest_segment_start = None
            longest_segment_end = None

            for i in range(len(_points) - sign):
                point1 = _points[i]
                point2 = _points[
                    (i + 1) % len(_points)
                ]  # To create a closed polyline, connect the last point to the first one.

                segment_length = compas.geometry.distance_point_point(point1, point2)

                if segment_length > longest_segment_length:
                    longest_segment_length = segment_length
                    longest_segment_start = point1
                    longest_segment_end = point2

            # create x and y-axes for the frame
            x_axis = compas.geometry.Vector.from_start_end(longest_segment_start, longest_segment_end)
            x_axis.unitize()
            y_axis = compas.geometry.cross_vectors(normal, x_axis)
            y_axis = compas.geometry.Vector(y_axis[0], y_axis[1], y_axis[2])
            # create the frame
            center = compas.geometry.centroid_points(_points)
            frame = compas.geometry.Frame(center, x_axis, y_axis)

            # orient the from the orientation point to the opposite direction
            if _orientation_point is not None:
                signed_distance = compas.geometry.distance_point_plane_signed(
                    _orientation_point, compas.geometry.Plane.from_frame(frame)
                )
                if signed_distance > 0.001:
                    frame = compas.geometry.Frame(frame.point, -x_axis, y_axis)
            # output
            return frame

        @staticmethod
        def from_box_corners():
            pass

        @staticmethod
        def from_points(points):
            polygon = compas.geometry.Polygon(points=points)
            xform = compas.geometry.Transformation.from_frame_to_frame(
                _.Triagulator._get_frame(points), compas.geometry.Frame.worldXY()
            )
            polygon.transform(xform)
            ear_cut = _.Earcut(polygon.points)
            ear_cut.triangulate()
            polygon.transform(xform.inverse())
            return compas.datastructures.Mesh.from_vertices_and_faces(polygon.points, ear_cut.triangles)

        @staticmethod
        def from_loft_two_polygons(points0, points1):
            n = len(points0)

            is_closed = (
                compas.geometry.distance_point_point(
                    compas.geometry.Point(*points0[0]), compas.geometry.Point(*points0[-1])
                )
                < 0.01
            )
            sign = 1 if is_closed else 0
            n = n - sign

            # create a polygon from the first set of points
            # orient to worldXY
            # triangulate
            polygon = compas.geometry.Polygon(points=points0)
            xform = compas.geometry.Transformation.from_frame_to_frame(
                _.Triagulator._get_frame(points0, points1[0]), compas.geometry.Frame.worldXY()
            )
            polygon.transform(xform)
            ear_cut = _.Earcut(polygon.points)
            ear_cut.triangulate()
            triangles = ear_cut.triangles

            # create mesh loft
            vertices = points0[:n] + points1[0:n]
            faces = triangles.copy()

            # top and bottom faces
            for triangle in triangles:
                faces.append([triangle[2] + n, triangle[1] + n, triangle[0] + n])

            # side faces
            for i in range(n):
                next = (i + 1) % n
                faces.append([i, next, next + n, i + n])

            # check cycles
            mesh = Mesh.from_vertices_and_faces(vertices, faces)
            # print(mesh.face_neighbors(1))
            return mesh


def get_arc_points(p1, p2, num_points, height):
    x1, y1, z1 = p1
    x2, y2, z2 = p2

    # Calculate control point
    cx = (x1 + x2) / 2
    cy = height

    # Calculate arc points
    arc_points = []
    for i in range(num_points):
        t = i / (num_points - 1)
        px = (1 - t) ** 2 * x1 + 2 * (1 - t) * t * cx + t**2 * x2
        py = (1 - t) ** 2 * y1 + 2 * (1 - t) * t * cy + t**2 * y2
        arc_points.append([px, 0, py])

    return arc_points


def calculate_normals_with_length(points, normal_scalar):
    normals = []

    for i in range(len(points)):
        if i == 0:
            # Handle left boundary
            delta_x = points[i + 1][0] - points[i][0]
            delta_z = points[i + 1][2] - points[i][2]
        elif i == len(points) - 1:
            # Handle right boundary
            delta_x = points[i][0] - points[i - 1][0]
            delta_z = points[i][2] - points[i - 1][2]
        else:
            delta_x = points[i + 1][0] - points[i - 1][0]
            delta_z = points[i + 1][2] - points[i - 1][2]

        normal_length = (delta_x**2 + delta_z**2) ** 0.5
        if normal_length == 0:
            normal_x, normal_z = 0, 0
        else:
            normal_x = -delta_z / normal_length
            normal_z = delta_x / normal_length

        normals.append([normal_x * normal_scalar, 0, normal_z * normal_scalar])

    normals[0] = [0, 0, 1]
    normals[-1] = [0, 0, 1]

    return normals


def move_points_by_normals(arc_points, normals, scale):
    moved_points = []

    for point, normal in zip(arc_points, normals):
        moved_point = [point[0] + normal[0] * scale, point[1] + normal[1] * scale, point[2] + normal[2] * scale]
        moved_points.append(moved_point)

    return moved_points


def move_points_to_target_z(arc_points, normals, target_z):
    moved_points = []

    for point, normal in zip(arc_points, normals):
        if normal[2] == 0:
            # Avoid division by zero if normal is parallel to the xy-plane
            continue

        # Calculate the parameter t where the normal line intersects the target z-coordinate line
        t = (target_z - point[2]) / normal[2]

        moved_point = [point[0] + normal[0] * t, point[1] + normal[1] * t, target_z]
        moved_points.append(moved_point)

    return moved_points


def move_points_in_two_opposite_directions(points, direction, distance):
    new_points_0 = []
    new_points_1 = []
    direction_magnitude = sum(d**2 for d in direction) ** 0.5
    normalized_direction = [d / direction_magnitude for d in direction]
    movement_positive = [d * distance for d in normalized_direction]
    movement_negative = [-d * distance for d in normalized_direction]
    for point in points:
        new_points_0.append(
            [
                point[0] + movement_positive[0],
                point[1] + movement_positive[1],
                point[2] + movement_positive[2],
            ]
        )
        new_points_1.append(
            [
                point[0] + movement_negative[0],
                point[1] + movement_negative[1],
                point[2] + movement_negative[2],
            ]
        )
    return new_points_0, new_points_1


# ==========================================================================
# CREATE POINTES FOR THE ARC
# ==========================================================================

# Create the arc curve points
# arc_points = create_arc_curve(center, radius, start_angle, end_angle, num_points)
n = 10
length = 3.0
height = 0.5
offset = 0.5
p_b_0 = get_arc_points([-length, 0, 0], [length, 0, 0], n, height)
normals = calculate_normals_with_length(p_b_0, 0.5)
# p_t_0  = move_points_by_normals(p_b_0, normals, 1)
p_t_0 = move_points_to_target_z(p_b_0, normals, height)
p_b_0, p_b_1 = move_points_in_two_opposite_directions(p_b_0, [0, 1, 0], offset)
p_t_0, p_t_1 = move_points_in_two_opposite_directions(p_t_0, [0, 1, 0], offset)
pts = p_b_0 + p_b_1 + p_t_0 + p_t_1
elements = Element.to_elements(pts)

# ==========================================================================
# MEASUREMENT
# ==========================================================================
measurements = []
geometry = []
arc_start = Point(p_b_1[0][0], p_b_1[0][1], p_b_1[0][2])
arc_end = Point(p_b_1[-1][0], p_b_1[-1][1], p_b_1[-1][2])
line = Line(arc_start, arc_end)
measurements.append(line)

# ==========================================================================
# CREATE PLATES
# ==========================================================================


def mesh_box_from_eight_points(vertices):
    # define the faces with the ccw winding
    faces = [
        [0, 3, 2, 1],
        [4, 5, 6, 7],
        [0, 1, 5, 4],
        [1, 2, 6, 5],
        [2, 3, 7, 6],
        [3, 0, 4, 7],
    ]

    mesh = Mesh.from_vertices_and_faces(vertices, faces)
    p0 = Point(vertices[0][0], vertices[0][1], vertices[0][2])
    p1 = Point(vertices[6][0], vertices[6][1], vertices[6][2])
    center = (p0 + p1) * 0.5

    return mesh, center


plate_thickness = 0.04
elements = []
side_planes_for_beams = [
    Plane(Point(0, 0, height - plate_thickness), Vector(0, 0, 1)),
    Plane(Point(-length, 0, 0), Vector(-1, 0, 0)),
    Plane(Point(length, 0, 0), Vector(1, 0, 0)),
]
side_planes_for_ribs_sequentialy = []

for i in range(n - 1):
    # --------------------------------------------------------------------------
    # Create the mesh
    # --------------------------------------------------------------------------
    vertices = [
        p_b_0[0 + i],
        p_b_0[1 + i],
        p_b_1[1 + i],
        p_b_1[0 + i],
        p_t_0[0 + i],
        p_t_0[1 + i],
        p_t_1[1 + i],
        p_t_1[0 + i],
    ]

    box, center = mesh_box_from_eight_points(vertices)

    # --------------------------------------------------------------------------
    # Collect planes for ribs
    # --------------------------------------------------------------------------
    plane = Plane(Point(*box.face_centroid(0)) + Vector(*box.face_normal(0)) * plate_thickness, box.face_normal(0))
    side_planes_for_beams.insert(-1, plane)

    # --------------------------------------------------------------------------
    # Create plates
    # --------------------------------------------------------------------------

    def create_plate(mesh, f=0):
        # plate
        f_n = mesh.face_neighbors(f)
        plane0 = Plane(mesh.face_centroid(f), mesh.face_normal(f))
        plane1 = Plane(
            Point(*mesh.face_centroid(f)) + Vector(*mesh.face_normal(f)) * plate_thickness, mesh.face_normal(f)
        )

        outline = []
        outline_temp = []
        for j in range(len(f_n)):
            p0 = intersection_plane_plane_plane(
                plane0,
                mesh.face_plane(f_n[j]),
                mesh.face_plane(f_n[(j + 1) % len(f_n)]),
            )
            outline.append(p0)
            p1 = intersection_plane_plane_plane(
                plane1,
                mesh.face_plane(f_n[j]),
                mesh.face_plane(f_n[(j + 1) % len(f_n)]),
            )
            outline_temp.append(p1)
        outline = outline + outline_temp
        mesh, center = mesh_box_from_eight_points(outline)
        return center, mesh

    meshes = [
        create_plate(box, f=0)[1],
        create_plate(box, f=2)[1],
        create_plate(box, f=3)[1],
        create_plate(box, f=4)[1],
        create_plate(box, f=5)[1],
    ]
    elements.append(Element.from_simplex_and_complex(center, meshes))


def points_from_side_plane(plane, side_planes):
    points = []
    for i in range(len(side_planes)):
        p0 = intersection_plane_plane_plane(plane, side_planes[i], side_planes[(i + 1) % len(side_planes)])
        points.append(Point(p0[0], p0[1], p0[2]))
    return points


# ==========================================================================
# NEST ELEMENTS
# ==========================================================================
FabricationNest.pack_elements(elements=elements, nest_type=3, inflate=0.1, height_step=4)

# ==========================================================================
# VIEWER
# ==========================================================================
color_red = [3] * len(elements)
color_red[0] = 0
Viewer.show_elements(elements, show_grid=True, measurements=measurements, geometry=geometry, color_red=color_red)

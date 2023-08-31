from compas_assembly2 import Viewer, Element, FabricationNest, Assembly
from compas.datastructures import Mesh
from compas.geometry import (
    Point,
    Line,
    Plane,
    Frame,
    Vector,
    Polygon,
    Transformation,
    Scale,
    intersection_plane_plane_plane,
    distance_point_point,
    cross_vectors,
    centroid_points,
    distance_point_plane_signed,
)
import math
from compas.data import json_dump

try:
    from compas_wood.joinery import get_connection_zones

    compas_wood_available = True
except ImportError:
    print("compas_wood package not available. Please install it.")
    compas_wood_available = False


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
            normal = Vector(0, 0, 0)
            count = len(_points)
            center = Point(0, 0, 0)
            is_closed = distance_point_point(Point(*_points[0]), Point(*_points[-1])) < 0.01
            sign = 1 if is_closed else 0

            for i in range(count - sign):
                num = ((i - 1) + count - sign) % (count - sign)
                item1 = ((i + 1) + count - sign) % (count - sign)
                point3d = _points[num]
                point3d1 = _points[item1]
                item2 = _points[i]
                normal += cross_vectors(item2 - point3d, point3d1 - item2)
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

                segment_length = distance_point_point(point1, point2)

                if segment_length > longest_segment_length:
                    longest_segment_length = segment_length
                    longest_segment_start = point1
                    longest_segment_end = point2

            # create x and y-axes for the frame
            x_axis = Vector.from_start_end(longest_segment_start, longest_segment_end)
            x_axis.unitize()
            y_axis = cross_vectors(normal, x_axis)
            y_axis = Vector(y_axis[0], y_axis[1], y_axis[2])
            # create the frame
            center = centroid_points(_points)
            frame = Frame(center, x_axis, y_axis)

            # orient the from the orientation point to the opposite direction
            reversed = False
            if _orientation_point is not None:
                signed_distance = distance_point_plane_signed(_orientation_point, Plane.from_frame(frame))
                if signed_distance > 0.001:
                    frame = Frame(frame.point, -x_axis, y_axis)
                    reversed = True
            # output0
            return frame, reversed

        @staticmethod
        def from_box_corners():
            pass

        @staticmethod
        def from_points(points):
            polygon = Polygon(points=points)
            frame = _.Triagulator._get_frame(points)
            xform, reversed = Transformation.from_frame_to_frame(frame, Frame.worldXY())
            polygon.transform(xform)
            ear_cut = _.Earcut(polygon.points)
            ear_cut.triangulate()

            return Mesh.from_vertices_and_faces(polygon.points, ear_cut.triangles)

        @staticmethod
        def from_loft_two_polygons(_points0, _points1):
            n = len(_points0)

            is_closed = distance_point_point(Point(*_points0[0]), Point(*_points0[-1])) < 0.01
            sign = 1 if is_closed else 0
            n = n - sign

            # create a polygon from the first set of points
            # orient to worldXY
            # triangulate

            # points0.reverse()
            frame, reversed = _.Triagulator._get_frame(_points0, _points1[0])
            points0 = list(_points0)
            points1 = list(_points1)
            xform = Transformation.from_frame_to_frame(frame, Frame.worldXY())
            if reversed:
                points0.reverse()
                points1.reverse()
            polygon = Polygon(points=points0)
            polygon.transform(xform)
            ear_cut = _.Earcut(polygon.points)
            ear_cut.triangulate()
            polygon.transform(xform.inverse())
            triangles = ear_cut.triangles

            # create mesh loft
            vertices = points0[:n] + points1[0:n]
            faces = []

            # top and bottom faces
            triangles = ear_cut.triangles
            if reversed:
                for triangle in triangles:
                    faces.append([triangle[0] + n, triangle[1] + n, triangle[2] + n])

                for triangle in triangles:
                    faces.append([triangle[2], triangle[1], triangle[0]])
            else:
                for triangle in triangles:
                    faces.append([triangle[0], triangle[1], triangle[2]])

                for triangle in triangles:
                    faces.append([triangle[2] + n, triangle[1] + n, triangle[0] + n])

            # side faces
            for i in range(n):
                next = (i + 1) % n
                faces.append([i, next, next + n, i + n])

            # check cycles
            mesh = Mesh.from_vertices_and_faces(vertices, faces)
            return mesh

        @staticmethod
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

    class MyScribble:
        @staticmethod
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

        @staticmethod
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

        @staticmethod
        def move_points_by_normals(arc_points, normals, scale):
            moved_points = []

            for point, normal in zip(arc_points, normals):
                moved_point = [point[0] + normal[0] * scale, point[1] + normal[1] * scale, point[2] + normal[2] * scale]
                moved_points.append(moved_point)

            return moved_points

        @staticmethod
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

        @staticmethod
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

        @staticmethod
        def points_from_side_plane(plane, side_planes, offset=0.0):
            points = []
            plane_offset = Plane(plane.point + plane.normal * offset, plane.normal) if abs(offset) > 0.01 else plane
            for i in range(len(side_planes)):
                p0 = intersection_plane_plane_plane(
                    plane_offset, side_planes[i], side_planes[(i + 1) % len(side_planes)]
                )
                if p0 is None:
                    raise Exception("Could not find intersection point")
                points.append(Point(p0[0], p0[1], p0[2]))
            return points

        @staticmethod
        def get_dual_planes(planes):
            dual_planes = []

            planes_with_ends = list(planes)
            planes_with_ends.insert(0, planes[0])
            # planes_with_ends.append(planes[-1])

            dual_planes.append(planes[0])

            for i in range(0, len(planes_with_ends) - 1):
                origin = (planes_with_ends[i].point + planes_with_ends[i + 1].point) * 0.5
                normal = (planes_with_ends[i].normal + planes_with_ends[i + 1].normal) * 0.5
                dual_planes.append(Plane(origin, normal))

            dual_planes.append(planes[-1])

            return dual_planes


# ==========================================================================
# CREATE POINTES FOR THE ARC
# ==========================================================================

# Create the arc curve points
# arc_poi,nts = create_arc_curve(center, radius, start_angle, end_angle, num_points)
n = 11
n = max(5, n - (n % 2) + 1)

length = 3.0
height = 0.5
offset = 0.5
p_b_0 = _.MyScribble.get_arc_points([-length, 0, 0], [length, 0, 0], n, height * 1.66)
normals = _.MyScribble.calculate_normals_with_length(p_b_0, 0.5)
# p_t_0  = move_points_by_normals(p_b_0, normals, 1)
p_t_0 = _.MyScribble.move_points_to_target_z(p_b_0, normals, height)
p_b_0, p_b_1 = _.MyScribble.move_points_in_two_opposite_directions(p_b_0, [0, 1, 0], offset)
p_t_0, p_t_1 = _.MyScribble.move_points_in_two_opposite_directions(p_t_0, [0, 1, 0], offset)
pts = p_b_0 + p_b_1 + p_t_0 + p_t_1
elements = Element.from_simplices_and_complexes(pts, None)

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
def remap_sequence(i, n):
    # original_sequence = list(range(n))
    # remapped_sequence = [0] * n

    # for i in original_sequence:
    if i < math.ceil(n / 2.0):
        return i * 2
    else:
        return n - i * 2 + n - 1


# return remapped_sequence

plate_thickness = 0.04
assembly = Assembly()
side_planes_for_beams = [
    Plane(Point(0, 0, height - plate_thickness), Vector(0, 0, 1)),
    Plane(Point(-length, 0, 0), Vector(-1, 0, 0)),
    Plane(Point(length, 0, 0), Vector(1, 0, 0)),
]
side_planes_for_ribs_sequentialy = []
planes_bot = []
planes_side = []


boxes = []

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

    box, center = _.Triagulator.mesh_box_from_eight_points(vertices)
    boxes.append(box)

    # --------------------------------------------------------------------------
    # Collect planes for ribs
    # --------------------------------------------------------------------------
    plane_bot = Plane(Point(*box.face_centroid(0)), box.face_normal(0))
    planes_bot.append(plane_bot)
    plane_side = Plane(Point(*box.face_centroid(5)), box.face_normal(5))
    planes_side.append(plane_side)
    if i == (n - 2):
        plane_side_last = Plane(Point(*box.face_centroid(3)), -Vector(*box.face_normal(3)))
        planes_side.append(plane_side_last)

planes_dual = _.MyScribble.get_dual_planes(planes_side)
plane_top = Plane(Point(0, 0, height), Vector(0, 0, 1))

# ==========================================================================
# GET BOTTOM PLATES --.--.--.--.--
# ==========================================================================
planes_assemblys = []
for i in range(0, n - 1, 2):
    planes_assemblys.append([i, i + 1])

for i in range(len(planes_assemblys)):
    bottom_plate_planes = [
        Plane(
            Point(*boxes[planes_assemblys[i][0]].face_centroid(5)),
            -Vector(*boxes[planes_assemblys[i][0]].face_normal(5)),
        ),
        Plane(Point(0, -offset, 0), Vector(0, -1, 0)),
        Plane(
            Point(*boxes[planes_assemblys[i][-1]].face_centroid(3)),
            -Vector(*boxes[planes_assemblys[i][-1]].face_normal(3)),
        ),
        Plane(Point(0, offset, 0), Vector(0, 1, 0)),
    ]

    bottom_plate_base_plane = Plane(
        (
            Point(*boxes[planes_assemblys[i][0]].face_centroid(0))
            + Point(*boxes[planes_assemblys[i][-1]].face_centroid(0))
        )
        * 0.5,
        (Point(*boxes[planes_assemblys[i][0]].face_normal(0)) + Point(*boxes[planes_assemblys[i][-1]].face_normal(0)))
        * 0.5,
    )

    assembly.add_element_by_index(
        Element.from_plate_planes(
            bottom_plate_base_plane,
            bottom_plate_planes,
            -plate_thickness,
            [0, remap_sequence(i, len(planes_assemblys))],
        )
    )


# ==========================================================================
# GET TOP PLATES -.--.--.--.--.-
# ==========================================================================
planes_assemblys = [[0], [1, 2], [3, 4], [5, 6], [7, 8], [9]]

planes_assemblys = [[0]]
for i in range(1, n - 3, 2):
    planes_assemblys.append([i, i + 1])
planes_assemblys.append([n - 2])

for i in range(len(planes_assemblys)):
    top_plate_planes = [
        Plane(
            Point(*boxes[planes_assemblys[i][0]].face_centroid(5)),
            -Vector(*boxes[planes_assemblys[i][0]].face_normal(5)),
        ),
        Plane(Point(0, -offset, 0), Vector(0, -1, 0)),
        Plane(
            Point(*boxes[planes_assemblys[i][-1]].face_centroid(3)),
            -Vector(*boxes[planes_assemblys[i][-1]].face_normal(3)),
        ),
        Plane(Point(0, offset, 0), Vector(0, 1, 0)),
    ]

    top_plate_base_plane = Plane(Point(0, 0, height), Vector(0, 0, 1))

    assembly.add_element_by_index(
        Element.from_plate_planes(
            top_plate_base_plane, top_plate_planes, plate_thickness, [1, remap_sequence(i, len(planes_assemblys))]
        )
    )

# ==========================================================================
# CREATE WEB PLATES ALTERNATING IN U and V directions
# ==========================================================================


# ==========================================================================
# WEB PLATES0
# ==========================================================================
planes_assemblys = [[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]
planes_assemblys = []
for i in range(0, n - 1, 2):
    planes_assemblys.append([i, i + 1])


for i in range(len(planes_assemblys)):
    bottom_plate_planes = [
        Plane(
            (
                Point(*boxes[planes_assemblys[i][0]].face_centroid(0))
                + Point(*boxes[planes_assemblys[i][-1]].face_centroid(0))
            )
            * 0.5,
            (
                Point(*boxes[planes_assemblys[i][0]].face_normal(0))
                + Point(*boxes[planes_assemblys[i][-1]].face_normal(0))
            )
            * 0.5,
        ),
        Plane(
            Point(*boxes[planes_assemblys[i][0]].face_centroid(5)),
            -Vector(*boxes[planes_assemblys[i][0]].face_normal(5)),
        ),
        plane_top,
        Plane(
            Point(*boxes[planes_assemblys[i][-1]].face_centroid(3)),
            -Vector(*boxes[planes_assemblys[i][-1]].face_normal(3)),
        ),
    ]

    web_base_plane = Plane(Point(0, 0.35, 0), Vector(0, 1, 0))

    assembly.add_element_by_index(
        Element.from_plate_planes(
            web_base_plane, bottom_plate_planes, plate_thickness, [0, remap_sequence(i, len(planes_assemblys))]
        )
    )
    assembly.add_element_by_index(
        Element.from_plate_planes(
            web_base_plane.offset(-0.75),
            bottom_plate_planes,
            plate_thickness,
            [0, remap_sequence(i, len(planes_assemblys))],
        )
    )

# ==========================================================================
# WEB PLATES1
# ==========================================================================
centroid_assemblys = [[0], [1, 2], [3, 4], [5, 6], [7, 8], [9]]
planes_assemblys0 = [[0, 1], [0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]
planes_assemblys1 = [[0, 1], [2, 3], [4, 5], [6, 7], [8, 9], [8, 9]]

centroid_assemblys = [[0]]
for i in range(1, n - 3, 2):
    centroid_assemblys.append([i, i + 1])
centroid_assemblys.append([n - 2])

planes_assemblys0 = [[0, 1]]
for i in range(0, n - 1, 2):
    planes_assemblys0.append([i, i + 1])

planes_assemblys1 = []
for i in range(0, n - 1, 2):
    planes_assemblys1.append([i, i + 1])
planes_assemblys1.append([(n - 3), (n - 2)])
inclined_webs = True


for i in range(len(planes_assemblys0)):
    p0 = Point(*boxes[centroid_assemblys[i][0]].face_centroid(5))
    p1 = Point(*boxes[centroid_assemblys[i][-1]].face_centroid(3))

    def linear_interpolation(p0, p1, t):
        interpolated_x = p0[0] + t * (p1[0] - p0[0])
        interpolated_y = p0[1] + t * (p1[1] - p0[1])
        interpolated_z = p0[2] + t * (p1[2] - p0[2])
        interpolated_point = Point(interpolated_x, interpolated_y, interpolated_z)
        return interpolated_point

    p_web0 = Plane(linear_interpolation(p0, p1, 0.15), Vector(1, 0, 0))
    p_web1 = Plane(linear_interpolation(p0, p1, 0.85), Vector(1, 0, 0))

    top_plate_planes = [
        Plane(
            (
                Point(*boxes[planes_assemblys0[i][0]].face_centroid(0))
                + Point(*boxes[planes_assemblys0[i][-1]].face_centroid(0))
            )
            * 0.5,
            (
                Vector(*boxes[planes_assemblys0[i][0]].face_normal(0))
                + Vector(*boxes[planes_assemblys0[i][-1]].face_normal(0))
            )
            * 0.5,
        ),
        Plane(Point(0, -offset, 0), Vector(0, -1, 0)),
        Plane(Point(0, 0, height), Vector(0, 0, 1)),
        Plane(Point(0, offset, 0), Vector(0, 1, 0)),
    ]

    p_web0 = (
        Plane(linear_interpolation(p0, p1, 0.15), Vector(1, 0, 0))
        if not inclined_webs
        else Plane(
            linear_interpolation(p0, p1, 0.15),
            cross_vectors(
                Vector(0, 1, 0),
                (Vector(*boxes[planes_assemblys0[i][-1]].face_normal(0))) * 0.5,
            ),
        )
    )

    p_web1 = Plane(linear_interpolation(p0, p1, 0.85), p_web0.normal)

    id = [1, remap_sequence(i, len(planes_assemblys0))]
    assembly.add_element_by_index(Element.from_plate_planes(p_web0, top_plate_planes, plate_thickness, id))

    top_plate_planes = [
        Plane(
            (
                Point(*boxes[planes_assemblys1[i][0]].face_centroid(0))
                + Point(*boxes[planes_assemblys1[i][-1]].face_centroid(0))
            )
            * 0.5,
            (
                Vector(*boxes[planes_assemblys1[i][0]].face_normal(0))
                + Vector(*boxes[planes_assemblys1[i][-1]].face_normal(0))
            )
            * 0.5,
        ),
        Plane(Point(0, -offset, 0), Vector(0, -1, 0)),
        Plane(Point(0, 0, height), Vector(0, 0, 1)),
        Plane(Point(0, offset, 0), Vector(0, 1, 0)),
    ]

    assembly.add_element_by_index(
        Element.from_plate_planes(
            p_web1,
            top_plate_planes,
            -plate_thickness,
            id,
            top_plate_planes[0].normal,
        )
    )

    for temp_element in assembly._elements[id[0], id[1]]:
        temp_element.insertion = top_plate_planes[0].normal

# ==========================================================================
# NEST ELEMENTS
# ==========================================================================
# assembly.to_nested_list
# elements = assembly.reassembly_by_keeping_first_indices(0)
FabricationNest.pack_elements(elements=assembly.to_list(), nest_type=2, inflate=0.1, height_step=4)

# ==========================================================================
# WRITE PLATE GEOMETRY TO JSON
# ==========================================================================
simplices = assembly.get_elements_properties("simplex", True)
json_dump(simplices, "tests/json_dumps/simplices.json")

# ==========================================================================
# COMPAS_WOOD
# ==========================================================================
if compas_wood_available:
    # ==========================================================================
    # COMPAS_WOOD SCALE POLYLINES DUE TO TOLERANCE
    # ==========================================================================
    scale = Scale.from_factors([100, 100, 100])
    for s in simplices:
        s.transform(scale)

    # ==========================================================================
    # COMPAS_WOOD CREATE ADJACENCY
    # ==========================================================================
    adjancency = []
    nested_lists = assembly.to_lists()
    for i in range(len(nested_lists)):
        adjancency.append(0 + 3 * i)
        adjancency.append(2 + 3 * i)
        adjancency.append(-1)
        adjancency.append(-1)
        adjancency.append(0 + 3 * i)
        adjancency.append(1 + 3 * i)
        adjancency.append(-1)
        adjancency.append(-1)

    adjancency.extend([16, 1, -1, -1])
    adjancency.extend([17, 1, -1, -1])
    adjancency.extend([22, 1, -1, -1])
    adjancency.extend([16, 2, -1, -1])
    adjancency.extend([17, 2, -1, -1])
    adjancency.extend([22, 2, -1, -1])

    adjancency.extend([19, 4, -1, -1])
    adjancency.extend([20, 4, -1, -1])
    adjancency.extend([26, 4, -1, -1])
    adjancency.extend([19, 5, -1, -1])
    adjancency.extend([20, 5, -1, -1])
    adjancency.extend([26, 5, -1, -1])

    adjancency.extend([23, 7, -1, -1])
    adjancency.extend([28, 7, -1, -1])
    adjancency.extend([23, 8, -1, -1])
    adjancency.extend([28, 8, -1, -1])

    adjancency.extend([25, 10, -1, -1])
    adjancency.extend([32, 10, -1, -1])
    adjancency.extend([25, 11, -1, -1])
    adjancency.extend([32, 11, -1, -1])

    adjancency.extend([29, 13, -1, -1])
    adjancency.extend([31, 13, -1, -1])
    adjancency.extend([29, 14, -1, -1])
    adjancency.extend([31, 14, -1, -1])

    # ==========================================================================
    # COMPAS_WOOD RUN
    # ==========================================================================
    division_length = 300
    joint_parameters = [
        division_length,
        0.5,
        9,
        division_length * 1.5,
        0.65,
        10,
        division_length * 1.5,
        0.5,
        21,
        division_length,
        0.95,
        30,
        division_length,
        0.95,
        40,
        division_length,
        0.95,
        50,
    ]
    print(simplices)
    simplices = get_connection_zones(simplices, None, None, None, adjancency, joint_parameters, 2, [1, 1, 1.1], 4)

    # ==========================================================================
    # COMPAS_WOOD SCALE BACK TO ORIGINAL SCALE THE OUTLINES
    # ==========================================================================
    scale = Scale.from_factors([1 / 100, 1 / 100, 1 / 100])
    for outlines in simplices:
        for outline in outlines:
            outline.transform(scale)

    # ==========================================================================
    # CHANGE SIMPLEX AND COMPLEX OF ELEMENTS
    # ==========================================================================
    counter = 0
    print(nested_lists)
    for element_list in nested_lists:
        for element in element_list:
            element.simplex = simplices[counter]
            element.complex = [_.Triagulator.from_loft_two_polygons(simplices[counter][-2], simplices[counter][-1])]
            counter = counter + 1
else:
    print("WARNING: the code is skipped because compas_wood not found")

# ==========================================================================
# assembly IN A DIFFERENT ASSEMBLY ORDER
# ==========================================================================
assembly_as_nested_list = assembly.to_lists(2)
assembly_as_nested_list_reordered = []
half = math.floor(len(assembly_as_nested_list) / 2)
for i in range(half):
    assembly_as_nested_list_reordered.append(assembly_as_nested_list[i])
    assembly_as_nested_list_reordered.append(assembly_as_nested_list[i + half])

if len(assembly_as_nested_list) % 2 == 1:
    assembly_as_nested_list_reordered.append(assembly_as_nested_list[-1])


# ==========================================================================
# VIEWER
# ==========================================================================
color_red = [3] * assembly.number_of_elements
color_red[0] = 0
color_red[1] = 0
color_red[2] = 0
Viewer.show_elements(
    assembly_as_nested_list_reordered,
    show_simplices=False,
    show_grid=False,
    measurements=measurements,
    geometry=geometry,
    color_red=color_red,
)

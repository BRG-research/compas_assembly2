import compas


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
            new_ear = Ear(self.vertices, indexes, i)
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
            prew_ear_new = Ear(self.vertices, indexes, current.prew)
            next_ear_new = Ear(self.vertices, indexes, current.next)
            if prew_ear_new.validate(self.vertices, indexes, self.ears) and prew_ear_new.index not in self.neighbours:
                self.add_ear(prew_ear_new)
                continue
            if next_ear_new.validate(self.vertices, indexes, self.ears) and next_ear_new.index not in self.neighbours:
                self.add_ear(next_ear_new)
                continue


class EarcutCompas:
    @staticmethod
    def get_frame(_points):
        """create a frame from a polyline"""

        # create a normal by averaging the cross-products of a polyline
        normal = compas.geometry.Vector(0, 0, 0)
        count = len(_points)
        center = compas.geometry.Point(0, 0, 0)
        is_closed = compas.geometry.distance_point_point(
            compas.geometry.Point(*_points[0]),
            compas.geometry.Point(*_points[-1])) < 0.01
        sign = 1 if is_closed else 0
        print(sign)

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
        x_axis = compas.geometry.Vector.from_start_end(
            longest_segment_start, longest_segment_end
        )
        x_axis.unitize()
        y_axis = compas.geometry.cross_vectors(normal, x_axis)
        y_axis = compas.geometry.Vector(y_axis[0], y_axis[1], y_axis[2])
        # create the frame
        center = compas.geometry.centroid_points(_points)
        frame = compas.geometry.Frame(center, x_axis, y_axis)

        # output
        return frame

    @staticmethod
    def triangulate_points(points):
        polygon = compas.geometry.Polygon(points=points)
        xform = compas.geometry.Transformation.from_frame_to_frame(
            EarcutCompas.get_frame(points),
            compas.geometry.Frame.worldXY())
        polygon.transform(xform)
        ear_cut = Earcut(polygon.points)
        ear_cut.triangulate()
        polygon.transform(xform.inverse())
        mesh = compas.datastructures.Mesh.from_vertices_and_faces(polygon.points, ear_cut.triangles)
        return mesh

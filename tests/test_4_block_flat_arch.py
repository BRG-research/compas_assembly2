from compas_assembly2 import Viewer, Element, FabricationNest
from compas.datastructures import Mesh
from compas.geometry import Point, Line


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
arc_start = Point(p_b_1[0][0], p_b_1[0][1], p_b_1[0][2])
arc_end = Point(p_b_1[-1][0], p_b_1[-1][1], p_b_1[-1][2])
line = Line(arc_start, arc_end)
measurements.append(line)

# ==========================================================================
# CREATE ELEMENTS
# ==========================================================================
elements = []
for i in range(n - 1):
    # --------------------------------------------------------------------------
    # Create the mesh
    # --------------------------------------------------------------------------

    # define the vertices
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

    # --------------------------------------------------------------------------
    # Create the element
    # --------------------------------------------------------------------------
    element = Element.from_simplex_and_complex(center, mesh, i)
    elements.append(element)

# ==========================================================================
# NEST ELEMENTS
# ==========================================================================
FabricationNest.pack_elements(elements=elements, nest_type=2, inflate=0.1, height_step=4)

# ==========================================================================
# VIEWER
# ==========================================================================
color_red = [3] * len(elements)
color_red[0] = 0
Viewer.show_elements(elements, show_grid=True, measurements=measurements, color_red=color_red)

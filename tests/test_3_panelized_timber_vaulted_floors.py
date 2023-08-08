from compas_assembly2 import Viewer, Element, FabricationNest


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
    new_points = []
    direction_magnitude = sum(d**2 for d in direction) ** 0.5
    normalized_direction = [d / direction_magnitude for d in direction]
    movement_positive = [d * distance for d in normalized_direction]
    movement_negative = [-d * distance for d in normalized_direction]
    for point in points:
        new_points.append(
            [
                point[0] + movement_positive[0],
                point[1] + movement_positive[1],
                point[2] + movement_positive[2],
            ]
        )
        new_points.append(
            [
                point[0] + movement_negative[0],
                point[1] + movement_negative[1],
                point[2] + movement_negative[2],
            ]
        )
    return new_points


# Create the arc curve points
# arc_points = create_arc_curve(center, radius, start_angle, end_angle, num_points)
arc_points0 = get_arc_points([-5.0, 0, 0], [5.0, 0, 0], 6, 3)
normals = calculate_normals_with_length(arc_points0, 0.5)
arc_points1 = arc_points1 = move_points_by_normals(arc_points0, normals, 1)
arc_points2 = move_points_to_target_z(arc_points0, normals, 2)
arc_points = arc_points0 + arc_points2
arc_points_moved = move_points_in_two_opposite_directions(arc_points, [0, 1, 0], 1)
elements = Element.to_elements(arc_points_moved)

# ==========================================================================
# NEST ELEMENTS
# ==========================================================================
FabricationNest.pack_elements(elements=elements, nest_type=2, inflate=0.1, height_step=4)

# ==========================================================================
# VIEWER
# ==========================================================================
Viewer.show_elements(elements, show_grid=True)

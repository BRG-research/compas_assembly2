from compas_assembly2 import Viewer, Element


def create_arc(p1, p2, num_points, height):
    x1, y1, z1 = p1
    x2, y2, z2 = p2

    # Calculate control point
    cx = (x1 + x2) / 2
    cy = height

    # Calculate arc points
    arc_points = []
    for i in range(num_points):
        t = i / (num_points - 1)
        px = (1 - t) ** 2 * x1 + 2 * (1 - t) * t * cx + t ** 2 * x2
        py = (1 - t) ** 2 * y1 + 2 * (1 - t) * t * cy + t ** 2 * y2
        arc_points.append([px, 0, py])

    return arc_points


# Create the arc curve points
# arc_points = create_arc_curve(center, radius, start_angle, end_angle, num_points)
arc_points = create_arc([-5.0, 0, 0], [5.0, 0, 0], 10, 3)
print(arc_points)
elements = Element.to_elements(arc_points, compute_nesting=1)
Viewer.show_elements(elements, show_grid=True)

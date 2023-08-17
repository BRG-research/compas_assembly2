# from compas.geometry import Polygon
# from compas.datastructures import Mesh

# polygon = Polygon.from_sides_and_radius_xy(6, 1)
# hole = Polygon.from_sides_and_radius_xy(6, 0.5)
# mesh = Mesh.from_polygons([polygon])

# mesh.update_default_face_attributes(holes=None)

# mesh.face_attribute(0, "holes", [hole])
# mesh.face_attributes()
import math


def remap_sequence(n):
    original_sequence = list(range(n))
    remapped_sequence = [0] * n

    for i in original_sequence:
        if i < n // 2:
            remapped_sequence[i] = i * 2
        else:
            remapped_sequence[i] = n - i * 2 + n - 1

    return remapped_sequence


n = 11  # Change this value to the desired sequence length
result = remap_sequence(n)
print(result)

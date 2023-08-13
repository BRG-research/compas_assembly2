from math import radians
from compas.geometry import Point, Box, Translation, Rotation, Frame
from compas_assembly2 import Element, ELEMENT_NAME, Viewer, FabricationNest
from compas_assembly2.collisions.kdtree import KDTree
import random

# ==========================================================================
# INIT ELEMENT
# ==========================================================================
b1 = Element(
    name=ELEMENT_NAME.BLOCK,
    id=0,
    frame=Frame.worldXY,
    simplex=Point(0, 0, 0),
    complex=Box.from_width_height_depth(0.5, 0.5, 0.5),
)

# ==========================================================================
# TRANSFORM AND COPY ELEMENT
# ==========================================================================
num_copies = 200
max_translation = 8  # Maximum translation distance from the center
elements = []


for _ in range(num_copies):
    # Generate random rotation and translation
    random_axis = [random.random(), random.random(), random.random()]
    random_rotation = Rotation.from_axis_and_angle(random_axis, radians(random.uniform(0, 360)))
    vector = [random.uniform(-max_translation, max_translation) for _ in range(3)]
    vector[2] = 0
    random_translation = Translation.from_vector(vector)

    # Apply random rotation and translation
    transformed_element = b1.transformed(random_translation * random_rotation)

    elements.append(transformed_element)


# ==========================================================================
# NEST ELEMENTS
# ==========================================================================
FabricationNest.pack_elements(elements=elements, nest_type=2, inflate=0.0, height_step=4)

# ==========================================================================
# CHECK COLLISION
# BVH https://github.com/lyd405121/ti-bvh
# KDTREE https://github.com/tjkemper/knn
# KDTREE NUMPY https://github.com/paradoxysm/kdtrees/issues/12
# KDTREE SCIPY https://github.com/hamaskhan/3D-Nearest-Neighbor-Search-KD-Tree/blob/main/main.py
# KDTREE PLANNER NUMPY https://github.com/Pradeep-Gopal/RRT_3D_python_KDtree
# ==========================================================================
collision_pairs = []
element_collisions = [2] * len(elements)
for i in range(len(elements)):
    for j in range(i + 1, len(elements)):
        if elements[i].collide(elements[j]):
            collision_pairs.append([i, j])
            element_collisions[i] = 0
            element_collisions[j] = 0

# print("Collision pairs:", collision_pairs)
# print("Element collisions:", element_collisions)
# ==========================================================================
# KDTREE https://github.com/tjkemper/knn
# knn - number of closest point
# kdn - closest points by distance
# kdn_bounding_box - closest bounding boxes given a distance
# check the closest distance between min and max
# ==========================================================================
list3d_2 = [
    [0, 0, 0],
    [5, 1, 0],
    [-5, 2, 0],
    [5, 5, 1],
    [5, -5, 2],
    [-5, -5, 3],
    [-5, 5, 4],
    [5, 5, 5],
    [5, 5, -5],
    [5, -5, 5],
    [5, -5, -5],
    [-5, 5, 5],
    [-5, 5, -5],
    [-5, -5, 5],
    [-5, -5, -5],
]

num_dims = 3
tree = KDTree(list3d_2, num_dims)
k = 2
result = tree.kdn([7, -7, 7], 0.1)
print(result)
# print(result[0][0])
# tree.visualize(visual_type=VisualType.graphical)
# tree.visualize_knn(point, result)

# ==========================================================================
# VIEWER
# ==========================================================================
Viewer.show_elements(elements=elements, color_red=element_collisions, show_grid=True)

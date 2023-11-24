from math import radians
from compas.geometry import Point, Box, Translation, Rotation, Frame
from compas_assembly2 import Element, ELEMENT_NAME  # Viewer

# from compas_assembly2.r_tree.bounding_box import BoundingBox
# from compas_assembly2.r_tree.r_tree import Rtree
# from compas_assembly2.r_tree.utilities import get_euclidean_distance
# from compas_assembly2.r_tree.configuration import VECTOR_DIMENSION, MAXIMUM_NUMBER_OF_CHILDREN

import random
import time

# ==========================================================================
# INIT ELEMENT
# ==========================================================================
b1 = Element(
    name=ELEMENT_NAME.BLOCK,
    id=0,
    frame=Frame.worldXY,
    geometry_simplified=Point(0, 0, 0),
    geometry=Box.from_width_height_depth(0.5, 0.5, 0.5),
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
# CHECK COLLISION
# Compile my own RTree from C++ and run it via CTypes to be compatible with ironpython
# BVH https://github.com/lyd405121/ti-bvh
# KDTREE https://github.com/tjkemper/knn
# KDTREE NUMPY https://github.com/paradoxysm/kdtrees/issues/12
# KDTREE SCIPY https://github.com/hamaskhan/3D-Nearest-Neighbor-Search-KD-Tree/blob/main/main.py
# KDTREE PLANNER NUMPY https://github.com/Pradeep-Gopal/RRT_3D_python_KDtree
# ==========================================================================

# ==========================================================================
# SIMPLE FOR LOOP
# ==========================================================================
start_time = time.time()
collision_pairs = []
element_collisions = [2] * len(elements)
for i in range(len(elements)):
    for j in range(i + 1, len(elements)):
        if elements[i].has_collision(elements[j]):
            collision_pairs.append([i, j])
            element_collisions[i] = 0
            element_collisions[j] = 0
end_time = time.time()
execution_time = end_time - start_time
print(f"Execution time: {execution_time:.6f} seconds")

# ==========================================================================
# VIEWER
# ==========================================================================
# Viewer.show_elements(elements, color_red=element_collisions, show_grid=False)
# Viewer.show_elements(elements, color_red=element_collisions, show_grid=False)

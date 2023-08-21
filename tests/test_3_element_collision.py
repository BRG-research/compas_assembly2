from math import radians
from compas.geometry import Point, Box, Translation, Rotation, Frame
from compas_assembly2 import Element, ELEMENT_NAME, Viewer, FabricationNest

from compas_assembly2.r_tree.bounding_box import BoundingBox
from compas_assembly2.r_tree.r_tree import Rtree
from compas_assembly2.r_tree.utilities import get_euclidean_distance
from compas_assembly2.r_tree.configuration import VECTOR_DIMENSION, MAXIMUM_NUMBER_OF_CHILDREN

import random
import time

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
        if elements[i].collide(elements[j]):
            collision_pairs.append([i, j])
            element_collisions[i] = 0
            element_collisions[j] = 0
end_time = time.time()
execution_time = end_time - start_time
print(f"Execution time: {execution_time:.6f} seconds")

# ==========================================================================
# R-TREE
# ==========================================================================
# start_time = time.time()

# r_tree = Rtree()
# r_tree.set_logging(False)
# INTERFACE_BORDER = 100
# already_generated_vectors = set()


# for i in range(len(elements)):
#     box_corners = elements[i].aabb()
#     p_min = (box_corners[0][0], box_corners[0][1], box_corners[0][2])
#     p_max = (box_corners[6][0], box_corners[6][1], box_corners[6][2])

#     if p_min not in already_generated_vectors:
#         r_tree.insert(p_min)
#         # data_list.append(vector)
#         already_generated_vectors.add(p_min)
#     else:
#         print("Vector already added.")

#     if p_max not in already_generated_vectors:
#         r_tree.insert(p_max)
#         # data_list.append(vector)
#         already_generated_vectors.add(p_max)
#     else:
#         print("Vector already added.")


# for i in range(len(elements)):
#     id = i
#     min_vec = (elements[id].aabb()[0][0], elements[id].aabb()[0][1], elements[id].aabb()[0][2])
#     max_vec = (elements[id].aabb()[6][0], elements[id].aabb()[6][1], elements[id].aabb()[6][2])
#     print(min_vec, max_vec)
#     elapsed_time1 = r_tree.search_by_query_box(min_vec, max_vec)

# execution_time = end_time - start_time
# print(f"Execution time: {execution_time:.6f} seconds")

# ==========================================================================
# VIEWER
# ==========================================================================
Viewer.show_elements(elements, color_red=element_collisions, show_grid=True)

# from compas.geometry import Polygon
# from compas.datastructures import Mesh

# polygon = Polygon.from_sides_and_radius_xy(6, 1)
# hole = Polygon.from_sides_and_radius_xy(6, 0.5)
# mesh = Mesh.from_polygons([polygon])

# mesh.update_default_face_attributes(holes=None)

# mesh.face_attribute(0, "holes", [hole])
# mesh.face_attributes()


# def remap_sequence(n):
#     original_sequence = list(range(n))
#     remapped_sequence = [0] * n

#     for i in original_sequence:
#         if i < n // 2:
#             remapped_sequence[i] = i * 2
#         else:
#             remapped_sequence[i] = n - i * 2 + n - 1

#     return remapped_sequence


# n = 11  # Change this value to the desired sequence length
# result = remap_sequence(n)
# print(result)

import time
import random
from compas_assembly2.r_tree.bounding_box import BoundingBox
from compas_assembly2.r_tree.r_tree import Rtree
from compas_assembly2.r_tree.utilities import get_euclidean_distance
from compas_assembly2.r_tree.configuration import VECTOR_DIMENSION, MAXIMUM_NUMBER_OF_CHILDREN

data_list = []
already_generated_vectors = set()


# For testing purposes


def search_by_query_box_brute_force(from_coord, to_coord):
    current_time = time.time()
    query_box = BoundingBox()
    query_box.min_coord = from_coord
    query_box.max_coord = to_coord
    result = []

    for vec in data_list:
        if query_box.includes_vector(vec):
            result.append(vec)
    elapsed_time = time.time() - current_time
    print("Result using brute force: (Len:", len(result), ")", sorted(result))
    print("Brute force took", elapsed_time, "seconds!")
    return elapsed_time


def search_k_nearest_brute_force(vector, k):
    if k <= 0:
        print("Invalid k")
        return
    current_time = time.time()
    sorted_data_by_distances = sorted(data_list, key=lambda x: get_euclidean_distance(x, vector))
    result = []
    if len(sorted_data_by_distances) >= k:
        result = sorted_data_by_distances[:k]
    else:
        result = sorted_data_by_distances
    elapsed_time = time.time() - current_time
    print("Result using brute force: (Len:", len(result), ")", sorted(result))
    print("Brute force took", elapsed_time, "seconds!")
    return elapsed_time


def generate_random_vectors(r_tree, from_value, to_value, vectors_inserted_count):
    random.seed(time.time())
    start_time = time.time()
    count = 0
    for i in range(vectors_inserted_count):
        vector = tuple(random.randint(from_value, to_value) for _ in range(VECTOR_DIMENSION))
        if vector in already_generated_vectors:
            continue
        already_generated_vectors.add(vector)
        r_tree.insert(vector)
        data_list.append(vector)
        count += 1
        if count % 250 == 0:
            print("Inserted", int(count / vectors_inserted_count * 100), "%")
    elapsed_time = time.time() - start_time
    print("Insert done.")
    print("Data inserted in", elapsed_time, "seconds!")


def main():
    global data_list, already_generated_vectors
    r_tree = Rtree()
    r_tree.set_logging(False)
    INTERFACE_BORDER = 100

    while True:
        print("*" * INTERFACE_BORDER)
        print("R tree interface:")
        print(
            "R tree settings:",
            "Dimension:",
            VECTOR_DIMENSION,
            "Child nodes limit:",
            MAXIMUM_NUMBER_OF_CHILDREN,
            "(Can be changed in configuration file.)",
        )
        print("1) Insert many vectors at once")
        print("2) Insert specific vector")
        print("3) Print R tree")
        print("4) Search by query box")
        print("5) Search k nearest neighbours")
        print("6) Clear R tree")
        print("*" * INTERFACE_BORDER)
        choice = int(input("> "))
        if choice == 1:
            count = int(input("How many? > "))
            min_val = int(input("Vector min_value > "))
            max_val = int(input("Vector max_value > "))
            generate_random_vectors(r_tree, min_val, max_val, count)
        elif choice == 2:
            vector = tuple(int(i) for i in input("Specify vector (Example: 1,-2,3,4) > ").split(","))
            if vector not in already_generated_vectors:
                r_tree.insert(vector)
                data_list.append(vector)
                already_generated_vectors.add(vector)
                print("Done.")
            else:
                print("Vector already added.")
        elif choice == 3:
            r_tree.print()
        elif choice == 4:
            min_vec = tuple(int(i) for i in input("Query box min_vector (Example: 1,-2,3,4) > ").split(","))
            max_vec = tuple(int(i) for i in input("Vector max_vector (Example: 1,-2,3,4) > ").split(","))
            elapsed_time1 = r_tree.search_by_query_box(min_vec, max_vec)
            elapsed_time2 = search_by_query_box_brute_force(min_vec, max_vec)
            if elapsed_time1 and elapsed_time2:
                print("R_tree was", elapsed_time2 / elapsed_time1, "x faster.")
        elif choice == 5:
            count = int(input("How many? > "))
            vec = tuple(int(i) for i in input("Query vector (Example: 1,-2,3,4) > ").split(","))
            elapsed_time1 = r_tree.search_k_nearest_from(vec, count)
            elapsed_time2 = search_k_nearest_brute_force(vec, count)
            if elapsed_time1 and elapsed_time2:
                print("R_tree was", elapsed_time2 / elapsed_time1, "x faster.")
        elif choice == 6:
            r_tree = Rtree()
            data_list = []
            already_generated_vectors = set()


if __name__ == "__main__":
    main()

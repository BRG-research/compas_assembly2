import math
from compas_assembly2.r_tree.configuration import VECTOR_DIMENSION


def vector_lt_comparator(vector1, vector2):
    return all(vector1[i] < vector2[i] for i in range(VECTOR_DIMENSION))


def vector_le_comparator(vector1, vector2):
    return all(vector1[i] <= vector2[i] for i in range(VECTOR_DIMENSION))


def get_euclidean_distance(vector1, vector2):
    return math.sqrt(sum((vector2[i] - vector1[i]) ** 2 for i in range(VECTOR_DIMENSION)))

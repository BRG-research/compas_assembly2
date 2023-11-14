from compas_assembly2.r_tree.utilities import get_euclidean_distance, vector_le_comparator
from compas_assembly2.r_tree.configuration import VECTOR_DIMENSION


class BoundingBox:
    def __init__(self):
        self.min_coord = [None] * VECTOR_DIMENSION
        self.max_coord = [None] * VECTOR_DIMENSION

    def includes_vector(self, vector):
        if self.min_coord[0] is None:
            return False
        return all(self.min_coord[i] <= vector[i] <= self.max_coord[i] for i in range(VECTOR_DIMENSION))

    def overlaps(self, bb):
        if self.min_coord[0] is None:
            return False
        return vector_le_comparator(self.min_coord, bb.max_coord) and vector_le_comparator(bb.min_coord, self.max_coord)

    def recalculate_bb_by_vector(self, vector):
        if self.min_coord[0] is None:
            self.min_coord = vector
            self.max_coord = vector
            return

        self.min_coord = tuple(min(self.min_coord[i], vector[i]) for i in range(VECTOR_DIMENSION))
        self.max_coord = tuple(max(self.max_coord[i], vector[i]) for i in range(VECTOR_DIMENSION))

    def recalculate_bb_by_child_node(self, child_node):
        if self.min_coord[0] is None:
            self.min_coord = child_node.bounding_box.min_coord
            self.max_coord = child_node.bounding_box.max_coord
            return

        self.min_coord = tuple(
            min(self.min_coord[i], child_node.bounding_box.min_coord[i]) for i in range(VECTOR_DIMENSION)
        )
        self.max_coord = tuple(
            max(self.max_coord[i], child_node.bounding_box.max_coord[i]) for i in range(VECTOR_DIMENSION)
        )

    # Heuristic for BB enlargement when looking for candidate
    def get_bb_enlargement_if_inserted(self, vector):
        if self.includes_vector(vector):
            return 0
        new_min_coord = [min(self.min_coord[i], vector[i]) for i in range(VECTOR_DIMENSION)]
        new_max_coord = [max(self.max_coord[i], vector[i]) for i in range(VECTOR_DIMENSION)]
        return get_euclidean_distance(self.min_coord, new_min_coord) + get_euclidean_distance(
            self.max_coord, new_max_coord
        )

    def get_center(self):
        return [(self.min_coord[i] + self.max_coord[i]) / 2 for i in range(VECTOR_DIMENSION)]

    def get_closest_point(self, vector):
        result_vector = [None] * VECTOR_DIMENSION
        for i in range(VECTOR_DIMENSION):
            result_vector[i] = max(self.min_coord[i], vector[i])
            result_vector[i] = min(self.max_coord[i], result_vector[i])
        return result_vector

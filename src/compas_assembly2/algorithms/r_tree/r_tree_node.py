from compas_assembly2.r_tree.bounding_box import BoundingBox
from compas_assembly2.r_tree.utilities import get_euclidean_distance
from compas_assembly2.r_tree.configuration import MAXIMUM_NUMBER_OF_CHILDREN


class RTreePoint:
    def __init__(self, coord, id) -> None:
        self.coord = coord
        self.id = id


class RtreeNode:
    def __init__(self, point: RTreePoint):
        if point is None:
            raise ValueError("Point cannot be None")
        self.parent = point
        self.bounding_box = None
        self.leaf_node = False
        self.child_nodes = []

    def can_insert(self):
        return len(self.child_nodes) < MAXIMUM_NUMBER_OF_CHILDREN

    def set_bounding_box(self, bounding_box):
        self.bounding_box = bounding_box

    def set_as_leaf_node(self):
        self.leaf_node = True

    def is_internal_node(self):
        return not self.leaf_node

    def is_leaf_node(self):
        return self.leaf_node

    def insert(self, obj):
        self.child_nodes.append(obj)
        if self.is_leaf_node():
            self.bounding_box.recalculate_bb_by_vector(obj)
        else:
            obj.parent = self
            self.bounding_box.recalculate_bb_by_child_node(obj)

    def get_count(self):
        return len(self.child_nodes)

    # Heuristic for splitting the node
    def split_node_quadratic(self):
        # Calculate distances between all pairs, chose 2 most distinct points, then insert closest objects
        new_node1, new_node2 = RtreeNode(self.parent), RtreeNode(self.parent)
        new_node1.set_bounding_box(BoundingBox())
        new_node2.set_bounding_box(BoundingBox())
        if self.is_leaf_node():
            new_node1.set_as_leaf_node()
            new_node2.set_as_leaf_node()
        pairs_distance = {}

        for i in self.child_nodes:
            for j in self.child_nodes:
                if i == j:
                    continue
                if (i, j) in pairs_distance:
                    pairs_distance[j, i] = pairs_distance[i, j]
                else:
                    if self.is_internal_node():
                        pairs_distance[i, j] = get_euclidean_distance(
                            i.bounding_box.get_center(), j.bounding_box.get_center()
                        )
                    elif self.is_leaf_node():
                        pairs_distance[i, j] = get_euclidean_distance(i, j)
        pair_distance_sorted_list = sorted(pairs_distance.items(), key=lambda item: item[1], reverse=True)
        seed_node_1 = pair_distance_sorted_list[0][0][0]
        seed_node_2 = pair_distance_sorted_list[0][0][1]
        new_node1.insert(seed_node_1)
        new_node2.insert(seed_node_2)
        for child in self.child_nodes:
            if child == seed_node_1 or child == seed_node_2:
                continue
            if pairs_distance[child, seed_node_1] < pairs_distance[child, seed_node_2]:
                new_node1.insert(child)
            else:
                new_node2.insert(child)
        return new_node1, new_node2

    def __eq__(self, o: object) -> bool:
        return super().__eq__(o)

    def __hash__(self) -> int:
        return super().__hash__()

    def set_parent(self, parent):
        self.parent = parent

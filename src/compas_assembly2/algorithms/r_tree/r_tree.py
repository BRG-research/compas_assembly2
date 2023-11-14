import time
from compas_assembly2.r_tree.bounding_box import BoundingBox
from compas_assembly2.r_tree.r_tree_node import RtreeNode, RTreePoint
from compas_assembly2.r_tree.utilities import get_euclidean_distance
from compas_assembly2.r_tree.priority_queue import PriorityQueue
from compas_assembly2.r_tree.priority_queue_element import PriorityQueueElement


class Rtree:
    def __init__(self):
        tmp_node = RtreeNode(RTreePoint([0] * 3, -1))
        tmp_node.set_as_leaf_node()
        tmp_node.set_bounding_box(BoundingBox())
        self.root = tmp_node
        self.LOGGING = False

    def print(self):
        if self.LOGGING:
            print("Current tree structure: ")
        print("Root:", end=" ")
        stack = [(self.root, 0)]
        while stack:
            curr_node, depth = stack.pop()
            print("    " * depth, end="")
            if curr_node.is_internal_node():
                print(
                    "Internal node -> bounding box:",
                    curr_node.bounding_box.min_coord,
                    curr_node.bounding_box.max_coord,
                    "Child_nodes:",
                    len(curr_node.child_nodes),
                )
                for child_node in curr_node.child_nodes:
                    stack.append((child_node, depth + 1))
            else:
                print(
                    "Leaf node ->",
                    "bounding box:",
                    curr_node.bounding_box.min_coord,
                    curr_node.bounding_box.max_coord,
                    ", Data (count:",
                    len(curr_node.child_nodes),
                    "):",
                    curr_node.child_nodes,
                )

    # Inserts vector, finds suitable subtree, splits node  if necessary
    def insert(self, vector):
        suitable_node = self.root
        while suitable_node.is_internal_node():
            min_enlargement = 2**32
            next_node = suitable_node.child_nodes[0]
            for child in suitable_node.child_nodes:
                tmp_enlargement = child.bounding_box.get_bb_enlargement_if_inserted(vector)
                if tmp_enlargement < min_enlargement:
                    min_enlargement = tmp_enlargement
                    next_node = child
            suitable_node = next_node

        if self.LOGGING:
            print("<Info> Inserting data", vector)

        if suitable_node.can_insert():
            suitable_node.insert(vector)
            parent = suitable_node.parent
            while parent:
                parent.bounding_box.recalculate_bb_by_child_node(suitable_node)
                suitable_node = parent
                parent = parent.parent
        else:
            # Splits
            if self.LOGGING:
                print("<Info> Splitting node", suitable_node)
            suitable_node.insert(vector)
            while True:
                new_node1, new_node2 = suitable_node.split_node_quadratic()
                if suitable_node.parent is None:
                    new_root_node = RtreeNode(None)
                    new_root_node.set_bounding_box(BoundingBox())
                    new_root_node.insert(new_node1)
                    new_root_node.insert(new_node2)
                    self.root = new_root_node
                    break
                else:
                    parent_node = suitable_node.parent
                    parent_node.child_nodes.remove(suitable_node)  # BUG
                    parent_node.insert(new_node1)
                    parent_node.insert(new_node2)
                    if parent_node.can_insert():
                        parent = parent_node.parent
                        while parent:
                            parent.bounding_box.recalculate_bb_by_child_node(parent_node)
                            parent_node = parent
                            parent = parent.parent
                        break
                    else:
                        suitable_node = parent_node

    def search_by_query_box(self, min_coord, max_coord):
        current_time = time.time()
        query_box = BoundingBox()
        query_box.min_coord = min_coord
        query_box.max_coord = max_coord
        result = []
        result_tmp = []
        stack = [self.root]
        while stack:
            curr_node = stack.pop()
            if query_box.overlaps(curr_node.bounding_box):
                if curr_node.is_internal_node():
                    for child_node in curr_node.child_nodes:
                        stack.append(child_node)
                elif curr_node.is_leaf_node():
                    result_tmp.extend(curr_node.child_nodes)
        for vec in result_tmp:
            if query_box.includes_vector(vec):
                result.append(vec)
        elapsed_time = time.time() - current_time
        print("Search by query box result:(Len:", len(result), ")", sorted(result))
        print("R tree query took", elapsed_time, "seconds!")
        return elapsed_time

    def search_by_query_box_id(self, min_coord, max_coord):
        query_box = BoundingBox()
        query_box.min_coord = min_coord
        query_box.max_coord = max_coord
        result = []
        result_tmp = []
        stack = [self.root]
        while stack:
            curr_node = stack.pop()
            if query_box.overlaps(curr_node.bounding_box):
                if curr_node.is_internal_node():
                    for child_node in curr_node.child_nodes:
                        stack.append(child_node)
                elif curr_node.is_leaf_node():
                    result_tmp.extend(curr_node.child_nodes)
                    for child_node in curr_node.child_nodes:
                        print(child_node)
                    # print(curr_node.child_nodes)
        for vec in result_tmp:
            if query_box.includes_vector(vec):
                result.append(vec)
        return result

    def search_k_nearest_from(self, vector, k):
        if k <= 0:
            print("Invalid k")
            return
        curr_time = time.time()
        priority_queue = PriorityQueue()
        priority_queue.push(
            PriorityQueueElement(
                (get_euclidean_distance(vector, self.root.bounding_box.get_closest_point(vector)), self.root)
            )
        )
        result_vectors = []
        while not priority_queue.is_empty() and len(result_vectors) < k:
            element = priority_queue.pop()
            curr_node = element.data[1]
            if isinstance(curr_node, RtreeNode):
                for child in curr_node.child_nodes:
                    if curr_node.is_internal_node():
                        priority_queue.push(
                            PriorityQueueElement(
                                (
                                    get_euclidean_distance(vector, child.bounding_box.get_closest_point(vector))
                                    if not child.bounding_box.includes_vector(vector)
                                    else -get_euclidean_distance(vector, child.bounding_box.get_center()),
                                    child,
                                )
                            )
                        )
                    else:
                        priority_queue.push(PriorityQueueElement((get_euclidean_distance(vector, child), child)))
            else:
                result_vectors.append(curr_node)

        elapsed_time = time.time() - curr_time
        print(k, "nearest vectors from", vector, "(Len:", len(result_vectors), ")", sorted(result_vectors))
        print("R tree query took", elapsed_time, "seconds.")
        return elapsed_time

    def set_logging(self, bool_val):
        self.LOGGING = bool_val

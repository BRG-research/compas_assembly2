import math


class Node:
    def __init__(self, data=None, left=None, right=None, parent=None, axis=None, depth=None, id=None):
        self.id = id
        self.data = data
        self.left = left
        self.right = right
        self.parent = parent
        self.axis = axis
        self.depth = depth

    def __str__(self, level=0):
        string = "\t" * level + str(self.data) + "\n"
        if self.left:
            string += self.left.__str__(level + 1)
        else:
            string += "\t" * (level + 1) + "None" + "\n"
        if self.right:
            string += self.right.__str__(level + 1)
        else:
            string += "\t" * (level + 1) + "None" + "\n"
        return string


# https://en.wikipedia.org/wiki/K-d_tree


class KDTreePoint:
    def __init__(self, id, point):
        self.id = id
        self.xyz = point


class KDTree:
    def __init__(self, point_list, num_dims):
        self.point_list = []
        for id, point in enumerate(point_list):
            self.point_list.append(KDTreePoint(id, point))

        # self.point_list = point_list
        self.num_dims = num_dims
        self.root = self._build(self.point_list, 0, None)

    def _build(self, point_list, depth, parent):
        if not point_list:
            return None

        axis = depth % self.num_dims

        point_sorted_list = sorted(point_list, key=lambda point: point.xyz[axis])
        median = len(point_sorted_list) // 2
        median_value = point_sorted_list[median].xyz[axis]

        # Ensure points with same axis value are moved to the right side of the tree.
        # This violates the halveness property, but allows simple (efficient?) knn search.
        split_index = median
        while split_index >= 1 and point_sorted_list[split_index - 1].xyz[axis] == median_value:
            split_index -= 1
        split_point = point_sorted_list[split_index]

        node = Node()
        node.data = split_point.xyz
        node.id = split_point.id
        node.left = self._build(point_sorted_list[:split_index], depth + 1, node)
        node.right = self._build(point_sorted_list[split_index + 1 :], depth + 1, node) # noqa
        node.parent = parent
        node.axis = axis
        node.depth = depth
        return node

    def knn(self, point, k):
        # k_best = [[point, dist], [point, dist], ...]
        k_best = []
        self._knn_helper(self.root, point, k, k_best)
        return k_best

    def _knn_helper(self, curr_node, point, k, k_best):
        if not curr_node:
            return

        # Recurse
        recurse_right = True
        if point[curr_node.axis] >= curr_node.data[curr_node.axis]:
            self._knn_helper(curr_node.right, point, k, k_best)
        elif point[curr_node.axis] < curr_node.data[curr_node.axis]:
            recurse_right = False
            self._knn_helper(curr_node.left, point, k, k_best)
        else:
            print("knn: Should never reach this point.")

        curr_dist = kd_dist(curr_node.data, point)
        # curr_node.datasdaddv fds
        if len(k_best) < k or curr_dist < k_best[-1][1]:
            self._knn_insort(k_best, [curr_node.data, curr_dist, curr_node.id])

        if len(k_best) > k:
            k_best.pop()

        # Check if distance to splitting plane is less than the worst k_best distance.
        # If so, there could be closer neighbors in that subtree.
        worst_k_best_dist = k_best[-1][1]
        dist_to_splitting_plane = abs(curr_node.data[curr_node.axis] - point[curr_node.axis])

        if len(k_best) < k or dist_to_splitting_plane < worst_k_best_dist:
            node_to_check = curr_node.left if recurse_right else curr_node.right
            self._knn_helper(node_to_check, point, k, k_best)

        # print(k_best)

    def _knn_insort(self, point_dist_list, point_dist):
        lo, hi = 0, len(point_dist_list)

        while lo < hi:
            mid = (lo + hi) // 2
            if point_dist[1] >= point_dist_list[mid][1]:
                lo = mid + 1
            else:
                hi = mid
        point_dist_list.insert(lo, point_dist)

    # Todo: implement w/ balance invariant
    # https://en.wikipedia.org/wiki/K-d_tree#Balancing
    def add(self, point):
        pass

    def remove(self, point):
        pass

    def kdn(self, point, distance):
        closest_points = []
        self._kdn_helper(self.root, point, distance, closest_points)
        return closest_points

    def _kdn_helper(self, curr_node, point, distance, closest_points):
        if not curr_node:
            return

        # Determine whether to explore the left or right subtree based on the current node's axis value
        recurse_right = True
        if point[curr_node.axis] >= curr_node.data[curr_node.axis]:
            self._kdn_helper(curr_node.right, point, distance, closest_points)
        elif point[curr_node.axis] < curr_node.data[curr_node.axis]:
            recurse_right = False
            self._kdn_helper(curr_node.left, point, distance, closest_points)

        # Calculate the distance between the current node's data and the query point
        curr_dist = kd_dist(curr_node.data, point)

        # Check if the current node is within the specified distance and add it to the closest points list
        if curr_dist <= distance:
            closest_points.append([curr_node.data, curr_dist, curr_node.id])

        # Calculate the distance to the splitting plane of the current node along its axis
        dist_to_splitting_plane = abs(curr_node.data[curr_node.axis] - point[curr_node.axis])

        # Check if the distance to the splitting plane is within the specified distance,
        # which indicates the need to explore the other subtree as well
        if dist_to_splitting_plane <= distance:
            node_to_check = curr_node.left if recurse_right else curr_node.right
            self._kdn_helper(node_to_check, point, distance, closest_points)

    def kdn_bounding_box(self, lower_corner, upper_corner):
        closest_points = []
        self._kdn_bounding_box_helper(self.root, lower_corner, upper_corner, closest_points)
        return closest_points

    def _kdn_bounding_box_helper(self, curr_node, lower_corner, upper_corner, closest_points):
        if not curr_node:
            return

        axis = curr_node.axis
        node_value = curr_node.data[axis]

        # Determine whether to explore the left or right subtree based on the current node's axis value
        if lower_corner[axis] <= node_value <= upper_corner[axis]:
            # Recurse into both subtrees if the splitting plane is within the bounding box
            self._kdn_bounding_box_helper(curr_node.left, lower_corner, upper_corner, closest_points)
            self._kdn_bounding_box_helper(curr_node.right, lower_corner, upper_corner, closest_points)
        elif node_value < lower_corner[axis]:
            # Recurse into the right subtree if the splitting plane is to the left of the bounding box
            self._kdn_bounding_box_helper(curr_node.right, lower_corner, upper_corner, closest_points)
        else:
            # Recurse into the left subtree if the splitting plane is to the right of the bounding box
            self._kdn_bounding_box_helper(curr_node.left, lower_corner, upper_corner, closest_points)

        # Check if the current node's data is within the bounding box
        in_bounding_box = all(lower_corner[i] <= curr_node.data[i] <= upper_corner[i] for i in range(self.num_dims))
        if in_bounding_box:
            closest_points.append(curr_node.data)

    def kdn_bounding_box_with_additional_check(self, lower_corner, upper_corner, additional_check=None):
        # # Example additional check function based on node.id
        # def custom_check(id):
        #     # Perform your custom check logic using the provided id
        #     return id % 2 == 0  # For example, add nodes with even IDs

        closest_points = []
        self._kdn_bounding_box_helper(self.root, lower_corner, upper_corner, closest_points, additional_check)
        return closest_points

    def _kdn_bounding_box_helper_with_additional_check(
        self, curr_node, lower_corner, upper_corner, closest_points, additional_check=None
    ):
        if not curr_node:
            return

        axis = curr_node.axis
        node_value = curr_node.data[axis]

        # Determine whether to explore the left or right subtree based on the current node's axis value
        if lower_corner[axis] <= node_value <= upper_corner[axis]:
            # Recurse into both subtrees if the splitting plane is within the bounding box
            self._kdn_bounding_box_helper(curr_node.left, lower_corner, upper_corner, closest_points, additional_check)
            self._kdn_bounding_box_helper(curr_node.right, lower_corner, upper_corner, closest_points, additional_check)
        elif node_value < lower_corner[axis]:
            # Recurse into the right subtree if the splitting plane is to the left of the bounding box
            self._kdn_bounding_box_helper(curr_node.right, lower_corner, upper_corner, closest_points, additional_check)
        else:
            # Recurse into the left subtree if the splitting plane is to the right of the bounding box
            self._kdn_bounding_box_helper(curr_node.left, lower_corner, upper_corner, closest_points, additional_check)

        # Check if the current node's data is within the bounding box and satisfies the additional check
        in_bounding_box = all(lower_corner[i] <= curr_node.data[i] <= upper_corner[i] for i in range(self.num_dims))
        if in_bounding_box and (additional_check is None or additional_check(curr_node.id)):
            closest_points.append(curr_node.data)


def kd_dist(point1, point2):
    if len(point1) != len(point2):
        raise ValueError("Points must have same number of dimensions.")

    result = 0
    for i in range(len(point1)):
        result += (point1[i] - point2[i]) ** 2

    result = math.sqrt(result)
    return result

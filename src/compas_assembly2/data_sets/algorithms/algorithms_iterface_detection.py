from compas.data import json_load
from compas.geometry import (
    Point,
    Box,
    Frame,
    Polygon,
    Plane,
    Transformation,
    transform_points,
    distance_point_point,
)
from compas_assembly2 import Element, ELEMENT_NAME, JOINT_NAME

# from compas_assembly2 import View  # type: ignore
from compas.datastructures import Mesh
from math import fabs

# from compas_assembly2.r_tree.bounding_box import BoundingBox
# from compas_assembly2.r_tree.r_tree import Rtree
# from compas_assembly2.r_tree.utilities import get_euclidean_distance
# from compas_assembly2.r_tree.configuration import VECTOR_DIMENSION, MAXIMUM_NUMBER_OF_CHILDREN

try:
    from shapely.geometry import Polygon as ShapelyPolygon

    shapely_available = True
except ImportError:
    print("shapely package not available. Please install it.")
    shapely_available = False

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
# num_copies = 2
# max_translation = 8  # Maximum translation distance from the center
# elements = []


# for _ in range(num_copies):
#     # Generate random rotation and translation
#     random_axis = [random.random(), random.random(), random.random()]
#     random_rotation = Rotation.from_axis_and_angle(random_axis, radians(random.uniform(0, 360)))
#     vector = [random.uniform(-max_translation, max_translation) for _ in range(3)]
#     vector[2] = 0
#     random_translation = Translation.from_vector(vector)

#     # Apply random rotation and translation
#     transformed_element = b1.transformed(random_translation * random_rotation)

#     elements.append(transformed_element)


# ==========================================================================
# CHECK COLLISION
# Compile my own RTree from C++ and run it via CTypes to be compatible with ironpython
# BVH https://github.com/lyd405121/ti-bvh
# KDTREE https://github.com/tjkemper/knn
# KDTREE NUMPY https://github.com/paradoxysm/kdtrees/issues/12
# KDTREE SCIPY https://github.com/hamaskhan/3D-Nearest-Neighbor-Search-KD-Tree/blob/main/main.py
# KDTREE PLANNER NUMPY https://github.com/Pradeep-Gopal/RRT_3D_python_KDtree
# ==========================================================================

geometry = []
polygons = []


# https://en.wikipedia.org/wiki/K-d_tree


class Algorithms:
    # ==========================================================================
    # METHODS - FACE-TO-FACE DETECTION
    # ==========================================================================
    @staticmethod
    def get_collision_pairs(elements):
        # ==========================================================================
        # SIMPLE FOR LOOP
        # ==========================================================================
        collision_pairs = []
        for i in range(len(elements)):
            for j in range(i + 1, len(elements)):
                if elements[i].has_collision(elements[j]):
                    collision_pairs.append([i, j])
        return collision_pairs

    @staticmethod
    def get_collision_pairs_with_attributes(elements, attributes=[], skip_the_same=True):
        if len(elements) != len(attributes):
            print("WARNING: the number of attributes must be equal to the number of elements")
            return []

        collision_pairs = []
        for i in range(len(elements)):
            for j in range(i + 1, len(elements)):
                attr_i, attr_j = attributes[i], attributes[j]
                elem_i, elem_j = elements[i], elements[j]

                if (skip_the_same and attr_i != attr_j) or (not skip_the_same and attr_i == attr_j):
                    if elem_i.has_collision(elem_j):
                        collision_pairs.append([i, j])
        return collision_pairs

    @staticmethod
    def has_collision(elements):
        # ==========================================================================
        # SIMPLE FOR LOOP
        # ==========================================================================
        element_collisions = [2] * len(elements)
        for i in range(len(elements)):
            for j in range(i + 1, len(elements)):
                if elements[i].has_collision(elements[j]):
                    element_collisions[i] = 0
                    element_collisions[j] = 0
        return element_collisions

    @staticmethod
    def get_collision_pairs_kdtree(elements):
        # get points
        points = []
        diagonal_distances = []
        for e in elements:
            points.append(e.aabb_center(0.01))
            diagonal_distances.append(distance_point_point(e.aabb()[0], e.aabb()[6]))

        from numpy import asarray
        from scipy.spatial import cKDTree

        def find_nearest_neighbours(cloud, nmax, distance_list, dims=3):
            cloud = asarray(cloud)[:, :dims]
            tree = cKDTree(cloud)
            nnbrs = [tree.query(root, nmax) for root in cloud]
            nnbrs = [(d.flatten().tolist(), n.flatten().tolist()) for d, n in nnbrs]

            # remove the root from the list of nearest neighbours that are too far aways
            my_set = set()
            nnbrs_culled = []
            for idx, nnbr in enumerate(nnbrs):
                local_culled = []
                nnbr_distances_without_self = nnbr[0][1:]
                nnbr_indices_without_self = nnbr[1][1:]
                for jdx, nnbr_distance_without_self in enumerate(nnbr_distances_without_self):
                    if nnbr_distance_without_self < distance_list[idx]:
                        local_culled.append(nnbr_indices_without_self[jdx])

                        # sort the indices to avoid duplicates and output the set of tuples
                        sorted_idx = idx
                        sorted_jdx = nnbr_indices_without_self[jdx]
                        if sorted_idx > sorted_jdx:
                            sorted_idx, sorted_jdx = sorted_jdx, sorted_idx
                            my_set.add((sorted_idx, sorted_jdx))
                nnbrs_culled.append(local_culled)

            return my_set

        result = find_nearest_neighbours(points, 10, diagonal_distances)
        print(result)
        return result

        # # construct the kd-tree
        # kd_tree = KDTree(points, num_dims=3)

        # # find neighbors
        # for idx, p in enumerate(points):
        #     result = kd_tree.k(p, diagonal_distances[idx])
        #     print(result)

    @staticmethod
    def face_to_face(element0, element1, tmax=1e-2, amin=1e1):
        """construct interfaces by intersecting coplanar mesh faces
        Parameters
        ----------
        assembly : compas_assembly.datastructures.Assembly
            An assembly of discrete blocks.
        nmax : int, optional
            Maximum number of neighbours per block.
        tmax : float, optional
            Maximum deviation from the perfectly flat interface plane.
        amin : float, optional
            Minimum area of a "face-face" interface.

        Returns
        -------
        Polygon of the Interface - :class:`compas.geometry.Polygon`
        Current Element ID - list[int]
        Other Element ID - list[int]
        Current Element Face Index - int
        Other Element Face Index - int
        """

        # --------------------------------------------------------------------------
        # sanity check
        # --------------------------------------------------------------------------
        if shapely_available is False:
            return []

        if len(element0.geometry) == 0 or len(element1.geometry) == 0:
            raise AssertionError("You must assign geometry geometry to the element")

        if not isinstance(element0.geometry[0], Mesh) or not isinstance(element1.geometry[0], Mesh):
            raise AssertionError("The geometry must be a mesh")

        # --------------------------------------------------------------------------
        # iterate face polygons and get intersection area
        # DEPENDENCY: shapely library
        # --------------------------------------------------------------------------

        def to_shapely_polygon(matrix, polygon, tmax=1e-3, amin=1e-1):
            """convert a compas polygon to shapely polygon on xy plane"""

            # orient points to the xy plane
            projected = transform_points(polygon.points, matrix)
            # geometry.append(Polygon(projected))

            # check if the oriented point is on the xy plane within the tolerance
            # then return the shapely polygon
            if not all(fabs(point[2]) < tmax for point in projected):
                for point in projected:
                    print("tolerance is off " + str(fabs(point[2])))
                return None
            elif polygon.area < amin:
                print("area is off")
                return None
            else:
                return ShapelyPolygon(projected)

        def to_compas_polygon(matrix, shapely_polygon):
            """convert a shapely polygon to compas polygon back to the frame"""

            # convert coordiantes to 3D by adding the z coordinate
            coords = [[x, y, 0.0] for x, y, _ in shapely_polygon.exterior.coords]

            # orient points to the original first mesh frame
            coords = transform_points(coords, matrix.inverted())[:-1]

            # convert to compas polygon
            return Polygon(coords)

        def is_coplanar(frame0, frame1, t_normal_colinearity=1e-1, t_dist_frames=1e-1):
            """check if two frames are coplanar and at the same position"""

            # get the normal vector of the first frame
            normal0 = frame0.normal

            # get the normal vector of the second frame
            normal1 = frame1.normal

            cross_product = normal0.cross(normal1)

            # check if the two normal vectors are parallel
            are_parellel = abs(cross_product.length) < t_normal_colinearity

            # are planes at the same positions?
            plane = Plane(frame0.point, frame0.normal)
            projected_point = plane.projected_point(frame1.point)
            are_close = distance_point_point(projected_point, frame1.point) < t_dist_frames
            return are_parellel and are_close

        joints = []

        for id_0, face_polygon_0 in enumerate(element0.face_polygons):

            # get the transformation matrix
            matrix = Transformation.from_frame_to_frame(element0.face_frames[id_0].copy(), Frame.worldXY())

            # get the shapely polygon
            shapely_polygon_0 = to_shapely_polygon(matrix, face_polygon_0, tmax, amin)
            if shapely_polygon_0 is None:
                print("WARNING: shapely_polygon_0 is None, frame or polygon is bad")
                continue

            for id_1, face_polygon_1 in enumerate(element1.face_polygons):

                if is_coplanar(element0.face_frames[id_0], element1.face_frames[id_1]) is False:
                    continue

                # get the shapely polygon
                shapely_polygon_1 = to_shapely_polygon(matrix, face_polygon_1, tmax, amin)
                if shapely_polygon_1 is None:
                    continue

                # check if polygons intersect
                if not shapely_polygon_0.intersects(shapely_polygon_1):
                    # print("shapely_polygon_0.intersects(shapely_polygon_1)")
                    continue

                # get intersection area and check if it is big enough within the given tolerance
                intersection = shapely_polygon_0.intersection(shapely_polygon_1)
                area = intersection.area
                if area < amin:
                    continue

                # convert shapely polygon to compas polygon
                polygon = to_compas_polygon(matrix, intersection)

                joints.append(
                    [JOINT_NAME.FACE_TO_FACE, polygon, element0.face_frames[id_0], element1.face_frames[id_1], area]
                )

        # output
        return joints

    @staticmethod
    def polyline_to_polyline(element0, element1, tmax=1e-6, amin=1e-1):
        pass

    @staticmethod
    def face_to_plane(element0, element1, tmax=1e-6, amin=1e-1):
        pass

    @staticmethod
    def face_to_polyline(element0, element1, tmax=1e-6, amin=1e-1):
        pass

    @staticmethod
    def find_support(model):
        pass


if __name__ == "__main__":
    # ==========================================================================
    # ELEMENTS FROM JSON
    # ==========================================================================
    path = "src/compas_assembly2/data_sets/element/element_alessandro_0.json"
    elements_json = json_load(path)

    # ==========================================================================
    # KDTREE
    # ==========================================================================
    collision_pairs = Algorithms.get_collision_pairs_kdtree(elements_json)

    # ==========================================================================
    # NEAREST NEIGHBOR
    # ==========================================================================
    attributes = []
    for e in elements_json:
        attributes.append(e.id[0])

    collision_pairs = Algorithms.get_collision_pairs_with_attributes(elements_json, attributes)

    # ===================================a=======================================
    # FACE
    # ==========================================================================
    displayed_elements = []
    for idx, collision_pair in enumerate(collision_pairs):
        result = Algorithms.face_to_face(elements_json[collision_pair[0]], elements_json[collision_pair[1]])
        for r in result:
            if result:
                geometry.append(r[1])

    # print(elements_json)

    # ==========================================================================
    # VIEWER
    # ==========================================================================

    # Viewer.show_elements(elements_json, show_grid=False, scale=0.001, geometry=geometry)

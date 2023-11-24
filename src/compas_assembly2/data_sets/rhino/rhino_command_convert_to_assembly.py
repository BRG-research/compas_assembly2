import rhinoscriptsyntax as rs  # type: ignore https://github.com/mcneel/rhinoscriptsyntax
import Rhino  # type: ignore
from compas.datastructures import Mesh
from compas.geometry import (
    Polyline,
    Frame,
    Polygon,
    Vector,
    Plane,
    Transformation,
)
from compas.geometry import (
    centroid_points,
    cross_vectors,
    bounding_box,
    distance_point_point,
    distance_point_plane_signed,
)

import compas_assembly2
from compas_assembly2.element import Element
from compas.data import (
    json_dump,
)  # https://compas.dev/compas/latest/reference/generated/compas.data.Data.html
import time

# select objects
ids = rs.GetObjects("Select objects", preselect=True, select=True)

# ==========================================================================
# TODO
# ==========================================================================
# build display pipeline in rhino, where button acts as radio buttons in compas_assembly2

# ==========================================================================
# Get object groups indices as list
# ==========================================================================


def object_groups(object_id):
    rhino_object = rs.coercerhinoobject(object_id, True, True)
    if rhino_object.GroupCount < 1:
        return []
    group_indices = rhino_object.GetGroupList()
    return list(group_indices)


# ==========================================================================
# create a container to store geometry with attributes
# ==========================================================================


class object_with_attributes:
    def __init__(self, guid, group_ids, geometry, layer_name):
        self.guid = guid
        self.group_ids = group_ids
        self.geometry = geometry
        self.layer_name = layer_name

    def __repr__(self):
        return "(guid: %s, group_ids: %s, geometry: %s, layer_name: %s)" % (
            self.guid,
            self.group_ids,
            self.geometry,
            self.layer_name,
        )


# ==========================================================================
# populate the object_with_attributes with geometry guid and group ids
# ==========================================================================


objects_with_attributes = []
for i in ids:
    objects_with_attributes.append(
        object_with_attributes(
            guid=i, group_ids=object_groups(i), geometry=rs.coercegeometry(i), layer_name=rs.ObjectLayer(i)
        )
    )

# ==========================================================================
# group objects based on group_ids by the most common group_id
# ==========================================================================


def partition_by_common_group_id(objects_list):
    # Manually count the occurrences of each integer ID in group_ids of all objects
    group_id_counts = {}
    for obj in objects_list:
        for group_id in obj.group_ids:
            group_id_counts[group_id] = group_id_counts.get(group_id, 0) + 1

    # Sort the objects based on the frequency of integer IDs in descending order
    objects_list.sort(key=lambda obj: sum(group_id_counts[group_id] for group_id in obj.group_ids), reverse=True)

    # Create a dictionary to group the objects based on the most common integer IDs
    group_count = Rhino.RhinoDoc.ActiveDoc.Groups.Count
    # print("TOTAL GROUP_COUNT: ", group_count)

    grouped_objects = {}
    for obj in objects_list:
        if len(obj.group_ids) == 0:
            grouped_objects.setdefault(-group_count, []).append(obj)
            group_count = group_count + 1
            print("WARNING: object is not in a group")
        else:
            most_common_group_id = max(obj.group_ids, key=lambda group_id: group_id_counts[group_id])
            grouped_objects.setdefault(most_common_group_id, []).append(obj)

    return grouped_objects


grouped_objects = partition_by_common_group_id(objects_with_attributes)

# ==========================================================================
# define a data-structure simplices
# ==========================================================================


class compas_assembly_user_input:
    def __init__(self, type, most_common_group_id):
        self.type = type
        self.most_common_group_id = most_common_group_id
        self.user_input_geometry = []

    def __repr__(self):
        return "(type %s, most_common_group_id: %s, geometry_count: %s)" % (
            self.type,
            self.most_common_group_id,
            self.user_input_geometry,
        )


# ==========================================================================
# rhino to compas conversions
# ==========================================================================
class conversions:
    @classmethod
    def get_frame(cls, _polyline, _orientation_point=None):
        """create a frame from a polyline"""

        # create a normal by averaging the cross-products of a polyline
        normal = Vector(0, 0, 0)
        count = len(_polyline)
        for i in range(count - 1):
            num = ((i - 1) + count - 1) % (count - 1)
            item1 = ((i + 1) + count - 1) % (count - 1)
            point3d = _polyline[num]
            point3d1 = _polyline[item1]
            item2 = _polyline[i]
            normal += cross_vectors(item2 - point3d, point3d1 - item2)
        normal.unitize()

        # get the longest edge
        longest_segment_length = 0.0
        longest_segment_start = None
        longest_segment_end = None

        for i in range(len(_polyline) - 1):
            point1 = _polyline[i]
            point2 = _polyline[
                (i + 1) % len(_polyline)
            ]  # To create a closed polyline, connect the last point to the first one.

            segment_length = distance_point_point(point1, point2)

            if segment_length > longest_segment_length:
                longest_segment_length = segment_length
                longest_segment_start = point1
                longest_segment_end = point2

        # create x and y-axes for the frame
        x_axis = Vector.from_start_end(
            longest_segment_start, longest_segment_end
        )  # Vector.from_start_end(_polyline[0], _polyline[1])
        x_axis.unitize()
        y_axis = cross_vectors(normal, x_axis)
        y_axis = Vector(y_axis[0], y_axis[1], y_axis[2])
        # create the frame
        center = centroid_points(_polyline.points)
        frame = Frame(center, x_axis, y_axis)
        if _orientation_point is not None:
            signed_distance = distance_point_plane_signed(_orientation_point, Plane.from_frame(frame))

            if signed_distance < -0.001:
                frame = Frame(frame.point, -x_axis, y_axis)

        # output
        return frame

    @staticmethod
    def is_clockwise_closed_polyline_on_xy_plane(polygon):
        """check if a polyline is oriented clockwise or anti-clockwise"""
        n = len(polygon) - 1
        signed_area = 0

        for i in range(n):
            x1, y1 = polygon[i][0], polygon[i][1]
            x2, y2 = polygon[(i + 1) % n][0], polygon[(i + 1) % n][1]  # Connect last vertex to the first vertex
            signed_area += x1 * y2 - x2 * y1

        sum_val = 0
        for i in range(len(polygon) - 1):
            sum_val = sum_val + (polygon[i + 1][0] - polygon[i][0]) * (polygon[i + 1][1] + polygon[i][1])

        return sum_val > 0

    @classmethod
    def sort_polyline_pairs(cls, plines):
        """given a list of polylines sort them into top and bottom lists"""
        # return plines, plines
        # considers types: LineCurve, NurbsCurve, PolylineCurve
        if len(plines) % 2 != 0:
            return plines

        # Sort polylines based on bounding box diagonal

        diagonals = []
        for i in range(len(plines)):
            pts = bounding_box(plines[i].points)
            diagonals.append(distance_point_point(pts[0], pts[6]))

        diagonals, plines = zip(*sorted(zip(diagonals, plines), reverse=True))
        plines = list(plines)

        # orient all polylines to the first outline's plane
        frame_2d = Frame([0, 0, 0], [1, 0, 0], [0, 1, 0])

        frame_3d = conversions.get_frame(plines[0], plines[1][0])
        T = Transformation.from_frame_to_frame(frame_3d, frame_2d)
        T_INV = Transformation.from_frame_to_frame(frame_2d, frame_3d)

        for i in range(len(plines)):
            plines[i] = plines[i].transformed(T)

        # on the first outline's plane:
        # a) make all polylines orientation anti-clockwise
        # b) split the plines list into two lists: top and bottom, based on the distance to the first outline's plane
        # c) in these lists, make order the plines based on the longest bounding box diagonal
        # d) orient the not the first ones anticlockwise to indicate holes of polygons

        # Orient bottom_polylines anticlockwise to indicate holes of polygons
        # Reverse the first two ones
        for i in range(1, len(plines)):
            is_clock_wise = conversions.is_clockwise_closed_polyline_on_xy_plane(plines[i])

            if is_clock_wise:
                plines[i] = Polyline(reversed(plines[i].points))

        points0 = list(plines[0].points)
        points1 = list(plines[0].points)
        points0.reverse()
        points1.reverse()
        plines[0] = Polyline(points0)
        plines[1] = Polyline(points1)

        # Split plines into top and bottom based on their distance to the origin point
        positions = []

        for i in range(len(plines)):
            positions.append(abs(plines[i][0][2]))

        positions, plines = zip(*sorted(zip(positions, plines)))

        first_half, second_half = plines[: len(plines) // 2], plines[len(plines) // 2 :]  # noqa E203
        # first_half = plines[::2]
        # second_half = plines[1::2]

        # Sort the second list polyline based on the first list order
        second_half_sorted = []

        for i in range(len(second_half)):
            distances = []

            for j in range(len(first_half)):
                distances.append((i, distance_point_point(second_half[i][0], first_half[i][0])))

            sorted_distances = sorted(distances, key=lambda x: x[1])
            second_half_sorted.append(second_half[sorted_distances[0][0]])

        # merge the two lists into one
        merged = []
        merged.extend(first_half)
        merged.extend(second_half_sorted)

        # Orient the plines back to their original position using the inverse matrix
        # the half is just a reference so no need to transform it twice

        for i in range(len(merged)):
            merged[i].transform(T_INV)
        """
        for i in range(len(first_half)):
            first_half[i].transform(I)
        """
        return first_half, merged, frame_3d  # [first_half[0]]

    @classmethod
    def perpendicular_to(cls, _o, _v):
        v = Vector.from_start_end(_o, _v)
        i, j, k = 0, 0, 0
        a, b = 0.0, 0.0
        k = 2

        if abs(v.y) > abs(v.x):
            if abs(v.z) > abs(v.y):
                # |v.z| > |v.y| > |v.x|
                i = 2
                j = 1
                k = 0
                a = v.z
                b = -v.y
            elif abs(v.z) >= abs(v.x):
                # |v.y| >= |v.z| >= |v.x|
                i = 1
                j = 2
                k = 0
                a = v.y
                b = -v.z
            else:
                # |v.y| > |v.x| > |v.z|
                i = 1
                j = 0
                k = 2
                a = v.y
                b = -v.x
        elif abs(v.z) > abs(v.x):
            # |v.z| > |v.x| >= |v.y|
            i = 2
            j = 0
            k = 1
            a = v.z
            b = -v.x
        elif abs(v.z) > abs(v.y):
            # |v.x| >= |v.z| > |v.y|
            i = 0
            j = 2
            k = 1
            a = v.x
            b = -v.z
        else:
            # |v.x| >= |v.y| >= |v.z|
            i = 0
            j = 1
            k = 2
            a = v.x
            b = -v.y

        perp = Vector(0, 0, 0)
        perp[i] = b
        perp[j] = a
        perp[k] = 0.0
        return perp, v.cross(perp)
        # return True if a != 0.0 else False

    @classmethod
    def from_rhino_frame(cls, line_nurbs_polyline_curve):
        # considers types: LineCurve, NurbsCurve, PolylineCurve
        curve = rs.coercecurve(line_nurbs_polyline_curve)
        result, polyline = curve.TryGetPolyline()

        if result:
            points = []
            counter = 0
            for p in polyline:
                if counter == 2:
                    break
                counter = counter + 1
                points.append([p.X, p.Y, p.Z])

            if counter == 2:
                return Frame(points[0], points[1] - points[0], points[2] - points[0])
            elif counter == 1:
                x_axis_vector, y_axis_vector = conversions.perpendicular_to(points[0], points[1])
                return Frame(points[0], x_axis_vector, y_axis_vector)
            else:
                return Frame([0, 0, 0], [1, 0, 0], [0, 1, 0])
        else:
            return Frame([0, 0, 0], [1, 0, 0], [0, 1, 0])

    @classmethod
    def from_rhino_polyline(cls, line_nurbs_polyline_curve):
        # considers types: LineCurve, NurbsCurve, PolylineCurve
        curve = rs.coercecurve(line_nurbs_polyline_curve)
        result, polyline = curve.TryGetPolyline()
        if result:
            points = []
            for p in polyline:
                points.append([p.X, p.Y, p.Z])
            return Polyline(points)
        else:
            return None

    @classmethod
    def from_rhino_mesh(cls, mesh):
        compas_mesh = Mesh()
        if mesh.Ngons.Count == 0:
            for vertex in mesh.Vertices:
                compas_mesh.add_vertex(attr_dict=dict(x=float(vertex.X), y=float(vertex.Y), z=float(vertex.Z)))

            for face in mesh.Faces:
                if face.A == face.D or face.C == face.D:
                    compas_mesh.add_face([face.A, face.B, face.C])
                else:
                    compas_mesh.add_face([face.A, face.B, face.C, face.D])

        else:
            polygons = []
            for i in range(mesh.Ngons.Count):
                vertices = mesh.Ngons.GetNgon(i).BoundaryVertexIndexList()

                points = []
                for v in vertices:
                    p = mesh.Vertices[v]
                    points.append([p.X, p.Y, p.Z])
                points.append(points[0])
                polygons.append(Polygon(points))

            compas_mesh = Mesh.from_polygons(polygons)
        return compas_mesh

    @classmethod
    def from_rhino_brep(cls, brep):
        mesh_params = Rhino.Geometry.MeshingParameters.Default
        mesh_params.JaggedSeams = False
        mesh_params.ClosedObjectPostProcess = False
        mesh_params.ComputeCurvature = False
        mesh_params.SimplePlanes = True
        mesh_params.GridAmplification = 0
        mesh_params.GridAngle = 0
        mesh_params.GridAspectRatio = 0
        mesh_params.GridMaxCount = 0
        mesh_params.GridMinCount = 0
        mesh_params.MaximumEdgeLength = 0
        mesh_params.MinimumEdgeLength = 1e10
        mesh_array = Rhino.Geometry.Mesh.CreateFromBrep(brep, mesh_params)
        mesh = Rhino.Geometry.Mesh()
        for m in mesh_array:
            mesh.Append(m)
        mesh.Vertices.CombineIdentical(True, True)
        mesh.UnifyNormals()
        mesh.Compact()
        compas_mesh = conversions.from_rhino_mesh(mesh)
        # Rhino.RhinoDoc.ActiveDoc.Objects.AddMesh(mesh)
        return compas_mesh


# ==========================================================================
# fill the Element properties based on geometry and layer name information
# ==========================================================================


def process_string(input_string):
    # Convert the string to lowercase
    input_string = input_string.lower()
    result = {"ELEMENT_NAME": "warning_not_defined", "PROPERTY_TYPE": "warning_not_defined"}
    # Check if the string contains "::"
    if "::" in input_string:
        # Split the string into substrings using "::"
        substrings = input_string.split("::")
        # print(substrings)
        # Process each substring independently
        for substring in substrings:
            if "type" in substring:
                # Remove the "type" substring and keep only letters in the substring
                substring = substring.replace("type", "")
                substring = "".join(filter(str.isalpha, substring))

                # Check if the string contains any of the specified substrings
                if "block" in input_string:
                    result["ELEMENT_NAME"] = "block"
                elif "beam" in input_string:
                    result["ELEMENT_NAME"] = "beam"
                elif "plate" in input_string:
                    result["ELEMENT_NAME"] = "plate"

            elif "geometry_simplified" in input_string:
                result["PROPERTY_TYPE"] = "geometry_simplified"
            elif "geometry" in input_string:
                result["PROPERTY_TYPE"] = "geometry"
            elif "frame" in input_string:
                result["PROPERTY_TYPE"] = "frame"
            elif "frame_global" in input_string:
                result["PROPERTY_TYPE"] = "frame_global"
            elif "id" in input_string:
                result["PROPERTY_TYPE"] = "id"
            elif "insertion" in input_string:
                result["PROPERTY_TYPE"] = "insertion"
    return result  # Return None if none of the specified substrings are found


elements = []
counter = 0
dict_id = {"BLOCK": 0, "BEAM": 1, "PLATE": 2}

for group_id, subsequent_groups in grouped_objects.items():
    # --------------------------------------------------------------------------
    # parse the layer information
    # --------------------------------------------------------------------------
    layer_name = subsequent_groups[0].layer_name
    processed_layer_name = process_string(layer_name)

    # --------------------------------------------------------------------------
    # create objects, the assignment of right properties is dependent on user
    # --------------------------------------------------------------------------
    # TODO skip certain objects
    # create elementcop
    o = Element(
        # ensure that this name exists
        name=compas_assembly2.ELEMENT_NAME.exists(processed_layer_name["ELEMENT_NAME"].upper()),  # type: ignore
        # id=[dict_id[processed_layer_name["ELEMENT_NAME"].upper()], counter],  # noqa: E231
        id=[counter],  # noqa: E231
    )
    counter = counter + 1

    for obj in subsequent_groups:
        # print(obj.layer_name, processed_layer_name["PROPERTY_TYPE"])
        layer_name = obj.layer_name
        processed_layer_name = process_string(layer_name)
        # print(processed_layer_name, layer_name)
        # print processed_layer_name["PROPERTY_TYPE"]
        # --------------------------------------------------------------------------
        # geometry_simplified
        # --------------------------------------------------------------------------
        if processed_layer_name["PROPERTY_TYPE"] == "geometry_simplified":
            # print("_____________geometry_simplified_________________", type(obj.geometry), layer_name)
            if str(type(obj.geometry)) == "<type 'Mesh'>":
                o.geometry_simplified.append(conversions.from_rhino_mesh(obj.geometry))
            elif (
                str(type(obj.geometry)) == "<type 'LineCurve'>"
                or str(type(obj.geometry)) == "<type 'NurbsCurve'>"
                or str(type(obj.geometry)) == "<type 'PolylineCurve'>"
            ):
                o.geometry_simplified.append(conversions.from_rhino_polyline(obj.geometry))
                # print(o.geometry_simplified)
        # --------------------------------------------------------------------------
        # frame
        # --------------------------------------------------------------------------
        elif processed_layer_name["PROPERTY_TYPE"] == "frame":
            if (
                str(type(obj.geometry)) == "<type 'LineCurve'>"
                or str(type(obj.geometry)) == "<type 'NurbsCurve'>"
                or str(type(obj.geometry)) == "<type 'PolylineCurve'>"
            ):
                o.frame = conversions.from_rhino_frame(obj.geometry)
        # --------------------------------------------------------------------------
        # frame_global
        # --------------------------------------------------------------------------
        elif processed_layer_name["PROPERTY_TYPE"] == "frame_global":
            if (
                str(type(obj.geometry)) == "<type 'LineCurve'>"
                or str(type(obj.geometry)) == "<type 'NurbsCurve'>"
                or str(type(obj.geometry)) == "<type 'PolylineCurve'>"
            ):
                o.frame_global = conversions.from_rhino_frame(obj.geometry)
        # --------------------------------------------------------------------------
        # geometry
        # --------------------------------------------------------------------------
        elif processed_layer_name["PROPERTY_TYPE"] == "geometry":
            # print("______________________________", type(obj.geometry))
            if str(type(obj.geometry)) == "<type 'Mesh'>":
                o.geometry.append(conversions.from_rhino_mesh(obj.geometry))
            elif str(type(obj.geometry)) == "<type 'Brep'>":
                o.geometry.append(conversions.from_rhino_brep(obj.geometry))
            elif str(type(obj.geometry)) == "<type 'Extrusion'>":
                o.geometry.append(conversions.from_rhino_brep(obj.geometry.ToBrep(True)))
            elif (
                str(type(obj.geometry)) == "<type 'LineCurve'>"
                or str(type(obj.geometry)) == "<type 'NurbsCurve'>"
                or str(type(obj.geometry)) == "<type 'PolylineCurve'>"
            ):
                o.geometry.append(conversions.from_rhino_polyline(obj.geometry))

        # --------------------------------------------------------------------------
        # id
        # --------------------------------------------------------------------------
        elif processed_layer_name["PROPERTY_TYPE"] == "id":
            if str(type(obj.geometry)) == "<type 'TextDot'>":

                def extract_integers_from_string(input_string):
                    integers = []
                    current_integer = ""

                    for char in input_string:
                        if char.isdigit():
                            current_integer += char
                        elif current_integer:
                            integers.append(int(current_integer))
                            current_integer = ""

                    if current_integer:
                        integers.append(int(current_integer))

                    return integers

                o.id = extract_integers_from_string(obj.geometry.Text) + o.id
        # --------------------------------------------------------------------------
        # insertion line
        # --------------------------------------------------------------------------
        elif processed_layer_name["PROPERTY_TYPE"] == "insertion":
            # print(str(type(obj.geometry)))
            if (
                str(type(obj.geometry)) == "<type 'LineCurve'>"
                or str(type(obj.geometry)) == "<type 'NurbsCurve'>"
                or str(type(obj.geometry)) == "<type 'PolylineCurve'>"
            ):
                p0 = obj.geometry.PointAtStart
                p1 = obj.geometry.PointAtEnd
                o.insertion = Vector(p0.X - p1.X, p0.Y - p1.Y, p0.Z - p1.Z)

    # --------------------------------------------------------------------------
    # reassign center incase local and global frames are not given
    # --------------------------------------------------------------------------
    frame_xy = Frame([0, 0, 0], [1, 0, 0], [0, 1, 0])
    if o.frame == frame_xy:
        if len(o.geometry_simplified) > 0:
            if isinstance(o.geometry_simplified[0], Mesh):
                o.frame = Frame(o.geometry_simplified[0].centroid(), [1, 0, 0], [0, 1, 0])
            elif isinstance(o.geometry_simplified[0], Polyline):
                if o.geometry_simplified[0].is_closed:
                    o.frame = Frame(o.geometry_simplified[0][0], [1, 0, 0], [0, 1, 0])
                else:
                    x_axis_vector, y_axis_vector = conversions.perpendicular_to(
                        o.geometry_simplified[0][0], o.geometry_simplified[0][1]
                    )

                    o.frame = Frame(o.geometry_simplified[0][0], x_axis_vector, y_axis_vector)
        elif len(o.geometry) > 0:
            if isinstance(o.geometry[0], Mesh):
                center = o.geometry[0].centroid()
                o.geometry_simplified.append(center)
                o.frame = Frame(center, [1, 0, 0], [0, 1, 0])
            elif isinstance(o.geometry[0], Polyline):
                if o.geometry[0].is_closed():
                    o.frame = Frame(o.geometry[0][0], [1, 0, 0], [0, 1, 0])
                else:
                    x_axis_vector, y_axis_vector = conversions.perpendicular_to(o.geometry[0][0], o.geometry[0][1])
                    o.frame = Frame(o.geometry[0][0], x_axis_vector, y_axis_vector)

    # --------------------------------------------------------------------------
    # special case for plates, where the simplices must be sorted and split
    # --------------------------------------------------------------------------
    if o.name == "PLATE":
        start = time.time()
        first_half, merged, frame = conversions.sort_polyline_pairs(o.geometry_simplified)
        end = time.time()
        # print("time", end - start)
        # print(merged)
        # o.geometry_simplified = first_half
        o.frame = frame

    # --------------------------------------------------------------------------
    # collect the element instance
    # --------------------------------------------------------------------------
    print(o)
    # print(len(o.geometry))
    elements.append(o)


# ==========================================================================
# fill the compas_assembly_user_input with geometry and types
# ==========================================================================
# write data to file
json_dump(data=elements, fp="element_alessandro_1.json", pretty=False)

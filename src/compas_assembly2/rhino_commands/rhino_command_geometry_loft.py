import rhinoscriptsyntax as rs  # noqa https://github.com/mcneel/rhinoscriptsyntax # type: ignore
from rhinoscriptsyntax import rhutil  # type: ignore
import scriptcontext  # type: ignore
import Rhino.RhinoDoc  # type: ignore
import Rhino.Geometry  # type: ignore
import System  # type: ignore
from System.Drawing import Color  # type: ignore
from compas.geometry import Polygon, Polyline
from compas.datastructures import Mesh

# select objects
ids = rs.GetObjects("Select objects", preselect=True, select=True)

# ==========================================================================
# TODO
# ==========================================================================
# get object groups, sort objects in a tree based on group names
# write objects information into json or xml
# read in compas_assembly and display it in python
# build display pipeline in rhino, where button acts as radio buttons in compas_assembly2

# ==========================================================================
# Get object groups indices as list
# ==========================================================================


def object_groups(object_id):
    rhino_object = rhutil.coercerhinoobject(object_id, True, True)
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
    print(group_count)

    grouped_objects = {}
    for obj in objects_list:
        if len(obj.group_ids) == 0:
            grouped_objects.setdefault(group_count, []).append(obj)
            group_count = group_count + 1
            print("WARNING: object is not in a group")
        else:
            most_common_group_id = max(obj.group_ids, key=lambda group_id: group_id_counts[group_id])
            grouped_objects.setdefault(most_common_group_id, []).append(obj)

    return grouped_objects


grouped_objects = partition_by_common_group_id(objects_with_attributes)

# ==========================================================================
# rhino to compas conversions
# ==========================================================================


class conversions:
    @classmethod
    def from_rhino_polyline(cls, line_nurbs_polyline_curve):
        # considers types: LineCurve, NurbsCurve, PolylineCurve
        curve = rs.coercecurve(line_nurbs_polyline_curve)
        result, polyline = curve.TryGetPolyline()

        points = []
        for p in polyline:
            points.append([p.X, p.Y, p.Z])
        return Polyline(points)

    @classmethod
    def from_rhino_mesh(cls, mesh):

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


# ==========================================================================
# create loft between polylines
# ==========================================================================
class polyline_lofter:
    @classmethod
    def to_polyline_from_cp(cls, curve):

        polyline = Rhino.Geometry.Polyline()
        result, polyline1 = curve.TryGetPolyline()

        if result is False:

            nurbsCurve = curve.ToNurbsCurve()
            point3dArray = []

            for i in range(nurbsCurve.Points.Count):
                result, pt = nurbsCurve.Points.GetPoint(i)
                point3dArray.append(pt)

            polyline1 = Rhino.Geometry.Polyline(point3dArray)
            nurbsCurve = polyline1.ToNurbsCurve()
            result, polyline1 = nurbsCurve.TryGetPolyline()

            polyline1.CollapseShortSegments(0.01)

            polyline1 = Rhino.Geometry.Polyline(polyline1)
            polyline = polyline1

        else:
            polyline1.CollapseShortSegments(0.01)
            polyline = polyline1

        return polyline

    @classmethod
    def loft_polylines_with_holes(cls, curves0, curves1):
        """Loft polylines with holes

        Parameters
        ----------
        curves0 : list[rg.Polyline]
        curves1 : list[rg.Polyline]

        Returns
        -------
        rg.Mesh
            mesh as lofted polylines and cap them
        """

        ###############################################################################
        # user input
        ###############################################################################

        flag = len(curves0) != 0 if True else len(curves1) != 0
        if flag:

            curves = []
            curves2 = []

            flag0 = len(curves1) == 0
            flag1 = len(curves0) == 0 and len(curves1) != 0
            flag2 = len(curves0) and len(curves1)

            if flag0:
                for i in range(len(curves0)):
                    if float(i) >= float(len(curves0)) * 0.5:
                        curves2.Add(curves0[i])  # type: ignore
                    else:
                        curves.Add(curves0[i])  # type: ignore
            elif flag1:
                for i in range(0, len(curves1), 2):  # type: ignore
                    curves.Add(curves1[i])  # type: ignore
                    curves2.Add(curves1[i + 1])  # type: ignore
            elif flag2:
                curves = curves0
                curves2 = curves1

            curves0 = curves
            curves1 = curves2

        ###############################################################################
        # sort curves which one is border and which ones are holes
        ###############################################################################
        length = -1.0
        border_id = -1
        count = 0

        for curve in curves0:
            diagonal = curve.GetBoundingBox(True).Diagonal
            temp_length = diagonal.Length
            if temp_length > length:
                length = temp_length
                border_id = count
            count = count + 1

        border0 = polyline_lofter.to_polyline_from_cp(curves0[border_id])
        border1 = polyline_lofter.to_polyline_from_cp(curves1[border_id])
        holes0 = []
        holes1 = []
        for i in range(curves0.Count):  # type: ignore
            if i != border_id:
                holes0.Add(curves0[i])  # type: ignore
                holes1.Add(curves1[i])  # type: ignore

        ###############################################################################
        # Create mesh of the bottom face
        ###############################################################################
        mesh_bottom = Rhino.Geometry.Mesh.CreatePatch(
            border0, Rhino.RhinoDoc.ActiveDoc.ModelAngleToleranceRadians, None, holes0, None, None, True, 1
        )

        ###############################################################################
        # Convert closed polylines to open ones
        ###############################################################################

        point_3d_array = []
        for i in range(len(mesh_bottom.Vertices)):
            point_3d_array.append(mesh_bottom.Vertices.Point3dAt(i))

        open_curve_points_0 = []
        open_curve_points_1 = []

        for i in range(border0.Count - 1):
            open_curve_points_0.append(border0[i])
            open_curve_points_1.append(border1[i])

        for i in range(holes0.Count):  # type: ignore
            holes0_polyline = polyline_lofter.to_polyline_from_cp(holes0[i])
            holes1_polyline = polyline_lofter.to_polyline_from_cp(holes1[i])
            for j in range(len(holes0_polyline) - 1):
                open_curve_points_0.append(holes0_polyline[j])
                open_curve_points_1.append(holes1_polyline[j])

        ###############################################################################
        # Using the bottom mesh vertices create the top mesh f
        ###############################################################################
        points_to_sort_new = polyline_lofter.sort_set_of_points(open_curve_points_0, point_3d_array)
        mesh_top = mesh_bottom.DuplicateMesh()

        for i in range(len(points_to_sort_new)):
            mesh_top.Vertices.SetVertex(i, open_curve_points_1[points_to_sort_new[i]])

        ###############################################################################
        # Merge the top and bottom mesh into one and add sides
        ###############################################################################
        mesh = Rhino.Geometry.Mesh()
        mesh.Append(mesh_bottom)
        mesh.Append(mesh_top)

        count = mesh_bottom.Vertices.Count
        for p in range(mesh_bottom.TopologyEdges.Count):

            if mesh_bottom.TopologyEdges.GetConnectedFaces(p).Length == 1:
                topologyVertices = mesh_bottom.TopologyEdges.GetTopologyVertices(p)
                mesh.Faces.AddFace(
                    topologyVertices.I, topologyVertices.J, topologyVertices.J + count, topologyVertices.I + count
                )

        mesh.UnifyNormals()
        mesh.Ngons.AddPlanarNgons(Rhino.RhinoDoc.ActiveDoc.ModelAbsoluteTolerance * 1, 3, 1, True)

        ###############################################################################
        # Unweld ngons meshes
        ###############################################################################
        unwelded_ngon_mesh = Rhino.Geometry.Mesh()
        count = 0
        for ngonAndFacesEnumerable in mesh.GetNgonAndFacesEnumerable():

            faces = []
            for j in ngonAndFacesEnumerable.FaceIndexList():
                faces.append(System.Int32(j))

            temp_ngon_mesh = mesh.DuplicateMesh().Faces.ExtractFaces(faces)

            # add colors
            if count < 2:
                temp_ngon_mesh.VertexColors.CreateMonotoneMesh(Color.LightGray)
            else:
                temp_ngon_mesh.VertexColors.CreateMonotoneMesh(Color.DeepPink)

            unwelded_ngon_mesh.Append(temp_ngon_mesh)
            count = count + 1

        ###############################################################################
        # Output
        ###############################################################################
        unwelded_ngon_mesh.RebuildNormals()
        return unwelded_ngon_mesh

    @classmethod
    def sort_set_of_points(cls, points_to_sort, guide_points):
        """Sort one array of point by an another point array

        use it like this:
        #points_to_sort_new = []
        #for i in points_to_sort_ids:
        #    points_to_sort_new.append(points_to_sort[i])

        Parameters
        ----------
        points_to_sort : list[rg.Point3d]
        guide_points : list[rg.Point3d]

        Returns
        -------
        list[int]
            the list of indices of the sorted array
        """

        # create a copy
        points_to_sort_copy = []
        for i in points_to_sort:
            points_to_sort_copy.append(Rhino.Geometry.Point3d(i))

        guide_points_copy = []
        for i in guide_points:
            guide_points_copy.append(Rhino.Geometry.Point3d(i))

        # make indices of points
        points_to_sort_ids = list(range(0, len(points_to_sort_copy)))
        guide_points_ids = list(range(0, len(guide_points_copy)))

        # sort both lists by xyz coordinates together with indices
        points_to_sort_copy, points_to_sort_ids = zip(*sorted(zip(points_to_sort_copy, points_to_sort_ids)))
        guide_points_copy, guide_points_ids = zip(*sorted(zip(guide_points_copy, guide_points_ids)))

        # sort guide points indices and order the points to sort indec
        guide_points_ids, points_to_sort_ids = zip(*sorted(zip(guide_points_ids, points_to_sort_ids)))

        # can be used like this:
        # points_to_sort_new = []
        # for i in points_to_sort_ids:
        #    points_to_sort_new.append(points_to_sort[i])

        return points_to_sort_ids


# ==========================================================================
# loft the meshes and add it the groups
# ==========================================================================
def add_mesh_to_group(mesh, group_id):
    # Check if the group exists
    group_name = scriptcontext.doc.Groups.GroupName(group_id)
    if not rs.IsGroup(group_name):
        print("Group with ID does not exist.")
        return False

    # Add the mesh to the group
    mesh_id = Rhino.RhinoDoc.ActiveDoc.Objects.AddMesh(mesh)

    if mesh_id:
        rs.AddObjectToGroup(mesh_id, group_name)
        print("Mesh added to Group.")
        return True
    else:
        print("Failed to create the mesh.")
        return True


for group_id, subsequent_groups in grouped_objects.items():
    curves = []
    for obj in subsequent_groups:
        if (
            str(type(obj.geometry)) == "<type 'LineCurve'>"
            or str(type(obj.geometry)) == "<type 'NurbsCurve'>"
            or str(type(obj.geometry)) == "<type 'PolylineCurve'>"
        ):
            curves.append(obj.geometry)
    if len(curves) == 2:
        mesh = polyline_lofter.loft_polylines_with_holes([curves[0].ToNurbsCurve()], [curves[1].ToNurbsCurve()])
        add_mesh_to_group(mesh, group_id)
        print("two_curves", group_id)

import rhinoscriptsyntax as rs  # noqa https://github.com/mcneel/rhinoscriptsyntax
from rhinoscriptsyntax import rhutil  # noqa
import Rhino
import compas_rhino
from compas.datastructures import Mesh
from compas.geometry import Point, Polyline, Box, Translation, Frame, Line, Pointcloud, Polygon, Vector
import random
from compas_assembly2.viewer import Viewer
from compas_assembly2.element import Element, ELEMENT_TYPE
from compas.data import json_dump, json_load  # https://compas.dev/compas/latest/reference/generated/compas.data.Data.html

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
    print("TOTAL GROUP_COUNT: ", group_count)
    
    grouped_objects = {}
    for obj in objects_list:
        if(len(obj.group_ids) == 0):
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
    def find_perpendicular_vectors(cls, normalPointA, normalPointB):
        # Calculate the direction vector of the plane
        direction_vector = Vector.from_start_end(normalPointA, normalPointB)
    
        # Calculate the x-axis vector by taking the cross product of the normal vector and the direction vector
        normal_vector = Vector(*normalPointA)  # Use one of the normal points
        x_axis_vector = normal_vector.cross(direction_vector)
    
        # Calculate the y-axis vector by taking the cross product of the normal vector and the x-axis vector
        y_axis_vector = normal_vector.cross(x_axis_vector)
    
        # Normalize the vectors (optional step, but makes them unit vectors)
        x_axis_vector.unitize()
        y_axis_vector.unitize()
    
        return x_axis_vector, y_axis_vector
        
    @classmethod
    def from_rhino_frame(cls,line_nurbs_polyline_curve):
        # considers types: LineCurve, NurbsCurve, PolylineCurve
        curve = rs.coercecurve(line_nurbs_polyline_curve)
        result, polyline = curve.TryGetPolyline()
        
        if(result):
            points = []
            counter = 0
            for p in polyline:
                if (counter == 2):
                    break
                counter = counter+1
                points.append([p.X, p.Y, p.Z])
                
            if(counter == 2):
                return Frame(points[0],points[1]-points[0],points[2]-points[0])
            elif(counter == 1):
                x_axis_vector, y_axis_vector, conversions.find_perpendicular_vectors(points[0],points[1])
                return Frame(points[0],x_axis_vector, y_axis_vector)
            else:
                return Frame([0, 0, 0], [1, 0, 0], [0, 1, 0])
        else:
            return Frame([0, 0, 0], [1, 0, 0], [0, 1, 0])
    
    @classmethod
    def from_rhino_polyline(cls,line_nurbs_polyline_curve):
        # considers types: LineCurve, NurbsCurve, PolylineCurve
        curve = rs.coercecurve(line_nurbs_polyline_curve)
        result, polyline = curve.TryGetPolyline()
        if(result):
            points = []
            for p in polyline:
                points.append([p.X, p.Y, p.Z])
            return Polyline(points)
        else:
            return None
    
    @classmethod
    def from_rhino_mesh(cls,mesh):
        
        polygons = []
        
        for i in range(mesh.Ngons.Count):
            vertices = mesh.Ngons.GetNgon(i).BoundaryVertexIndexList()
            
            points =  []
            for v in vertices:
                p = mesh.Vertices[v]
                points.append([p.X,p.Y,p.Z])
            points.append(points[0])
            
            
            polygons.append(Polygon(points))
        
        compas_mesh = Mesh.from_polygons(polygons)
        return compas_mesh

# ==========================================================================
# fill the Element properties based on geometry and layer name information
# ==========================================================================


def process_string(input_string):
    # Convert the string to lowercase
    input_string = input_string.lower()
    result = {"ELEMENT_TYPE":"warning_not_defined", "PROPERTY_TYPE":"warning_not_defined"}
    # Check if the string contains "::"
    if "::" in input_string:
        # Split the string into substrings using "::"
        substrings = input_string.split("::")
        #print(substrings)
        # Process each substring independently
        for substring in substrings:
            if "type" in substring:
                # Remove the "type" substring and keep only letters in the substring
                substring = substring.replace("type", "")
                substring = ''.join(filter(str.isalpha, substring))
                
                
                # Check if the string contains any of the specified substrings
                
                if "block" in input_string:
                    result["ELEMENT_TYPE"] = "block"
                elif "frame" in input_string:
                    result["ELEMENT_TYPE"] = "frame"
                elif "plate" in input_string:
                    result["ELEMENT_TYPE"] = "plate"
            
            elif "simplex" in input_string:
                result["PROPERTY_TYPE"] = "simplex"
            elif "display_shapes" in input_string:
                result["PROPERTY_TYPE"] = "display_shapes"
            elif "local_frame" in input_string:
                result["PROPERTY_TYPE"] = "local_frame"
            elif "global_frame" in input_string:
                result["PROPERTY_TYPE"] = "global_frame"
    return result  # Return None if none of the specified substrings are found




elements = []
counter = 0
for group_id, subsequent_groups in grouped_objects.items():
    
    # --------------------------------------------------------------------------
    # parse the layer infornate
    # --------------------------------------------------------------------------
    layer_name = subsequent_groups[0].layer_name
    processed_layer_name = process_string(layer_name)
    #print(processed_layer_name)
    
    # --------------------------------------------------------------------------
    # create objects, the assignment of right properties is dependent on user
    # --------------------------------------------------------------------------
    #TODO skip certain objects
    
    # create element
    o = Element(element_type=ELEMENT_TYPE.find_element_type(processed_layer_name["ELEMENT_TYPE"]),id=(counter,group_id))
    counter = counter+1
    
    for obj in subsequent_groups:
        layer_name = obj.layer_name
        processed_layer_name = process_string(layer_name)
        print(processed_layer_name, layer_name)
        # --------------------------------------------------------------------------
        # simplex
        # --------------------------------------------------------------------------
        if(processed_layer_name["PROPERTY_TYPE"]=="simplex"):
            #print("_____________simplex_________________", type(obj.geometry), layer_name)
            if str(type(obj.geometry)) == "<type 'Mesh'>":
                o.simplex.append(conversions.from_rhino_mesh(obj.geometry))
            elif (
                str(type(obj.geometry)) == "<type 'LineCurve'>"
                or str(type(obj.geometry)) == "<type 'NurbsCurve'>"
                or str(type(obj.geometry)) == "<type 'PolylineCurve'>"
            ):
                o.simplex.append(conversions.from_rhino_polyline(obj.geometry))
        # --------------------------------------------------------------------------
        # local_frame
        # --------------------------------------------------------------------------
        elif(processed_layer_name["PROPERTY_TYPE"]=="local_frame"):
            
            if (
                str(type(obj.geometry)) == "<type 'LineCurve'>"
                or str(type(obj.geometry)) == "<type 'NurbsCurve'>"
                or str(type(obj.geometry)) == "<type 'PolylineCurve'>"
            ):
                o.local_frame = conversions.from_rhino_frame(obj.geometry)
        # --------------------------------------------------------------------------
        # global_frame
        # --------------------------------------------------------------------------
        elif(processed_layer_name["PROPERTY_TYPE"]=="global_frame"):
            if (
                str(type(obj.geometry)) == "<type 'LineCurve'>"
                or str(type(obj.geometry)) == "<type 'NurbsCurve'>"
                or str(type(obj.geometry)) == "<type 'PolylineCurve'>"
            ):
                o.global_frame = conversions.from_rhino_frame(obj.geometry)
        # --------------------------------------------------------------------------
        # display_shapes
        # --------------------------------------------------------------------------
        elif(processed_layer_name["PROPERTY_TYPE"]=="display_shapes"):
            #print("______________________________")
            if str(type(obj.geometry)) == "<type 'Mesh'>":
                o.display_shapes.append(conversions.from_rhino_mesh(obj.geometry))
            elif (
                str(type(obj.geometry)) == "<type 'LineCurve'>"
                or str(type(obj.geometry)) == "<type 'NurbsCurve'>"
                or str(type(obj.geometry)) == "<type 'PolylineCurve'>"
            ):
                o.display_shapes.append(conversions.from_rhino_polyline(obj.geometry))
    
    # --------------------------------------------------------------------------
    # reassingn center incase local and global frames are not given
    # --------------------------------------------------------------------------
    frame_xy = Frame([0, 0, 0], [1, 0, 0], [0, 1, 0])
    if(o.local_frame == frame_xy ):
        if len(o.simplex)>0 :
            if isinstance(o.simplex[0], Mesh):
                o.local_frame = Frame(o.simplex[0].centroid(), [1,0,0], [0,1,0])
            elif isinstance(o.simplex[0], Polyline):
                    if(o.simplex[0].is_closed()):
                        o.local_frame = Frame(o.simplex[0][0], [1,0,0], [0,1,0])
                        #print("is_closed")
                    else:
                        x_axis_vector, y_axis_vector = conversions.find_perpendicular_vectors(o.simplex[0][0],o.simplex[0][1])
                        o.local_frame = Frame(o.simplex[0][0],x_axis_vector, y_axis_vector)
                        #print("is_open")
        elif len(o.display_shapes)>0:
            if isinstance(o.display_shapes[0], Mesh):
                #print(o.display_shapes[0])
                center = o.display_shapes[0].centroid()
                o.simplex.append(center)
                o.local_frame = Frame(center, [1,0,0], [0,1,0])
            elif isinstance(o.display_shapes[0], Polyline):
                    if(o.display_shapes[0].is_closed()):
                        
                        o.local_frame = Frame(o.display_shapes[0][0], [1,0,0], [0,1,0])
                        #print("is_closed")
                    else:
                        x_axis_vector, y_axis_vector = conversions.find_perpendicular_vectors(o.display_shapes[0][0],o.display_shapes[0][1])
                        o.local_frame = Frame(o.display_shapes[0][0],x_axis_vector, y_axis_vector)
                        vprint("is_open")
    
    # --------------------------------------------------------------------------
    # collect the element instance
    # --------------------------------------------------------------------------
    
    elements.append(o)


# ==========================================================================
# fill the compas_assembly_user_input with geometry and types
# ==========================================================================
# write data to file
json_dump(data=elements, fp="rhino_command_convert_to_assembly.json", pretty=True)
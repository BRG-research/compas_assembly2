import rhinoscriptsyntax as rs  # noqa https://github.com/mcneel/rhinoscriptsyntax
from rhinoscriptsyntax import rhutil  # noqa

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


def parition_by_common_group_id(objects_list):
    # Manually count the occurrences of each integer ID in group_ids of all objects
    group_id_counts = {}
    for obj in objects_list:
        for group_id in obj.group_ids:
            group_id_counts[group_id] = group_id_counts.get(group_id, 0) + 1

    # Sort the objects based on the frequency of integer IDs in descending order
    objects_list.sort(key=lambda obj: sum(group_id_counts[group_id] for group_id in obj.group_ids), reverse=True)

    # Create a dictionary to group the objects based on the most common integer IDs
    grouped_objects = {}
    for obj in objects_list:
        most_common_group_id = max(obj.group_ids, key=lambda group_id: group_id_counts[group_id])
        grouped_objects.setdefault(most_common_group_id, []).append(obj)

    return grouped_objects


grouped_objects = parition_by_common_group_id(objects_with_attributes)


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
# fill the compas_assembly_user_input with geometry and types
# ==========================================================================


dict_compas_assembly_user_input = {"blocks": [], "frames": [], "plates": []}

# Collect the partitioned input to user input:
# Block - mesh
# Frame - line
# Plate - top_and_bottom_outlines
for group_id, subsequent_groups in grouped_objects.items():
    print("Most Common Group ID:", group_id)

    valid = False
    print(subsequent_groups[0].layer_name)
    if str.lower(subsequent_groups[0].layer_name) == "block":
        o = compas_assembly_user_input("BLOCK", group_id)
        for obj in subsequent_groups:
            if str(type(obj.geometry)) == "<type 'Mesh'>":
                o.user_input_geometry.append(obj.geometry)
        dict_compas_assembly_user_input["blocks"].append(o)
    elif str.lower(subsequent_groups[0].layer_name) == "frame":
        o = compas_assembly_user_input("FRAME", group_id)
        for obj in subsequent_groups:
            if (
                str(type(obj.geometry)) == "<type 'LineCurve'>"
                or str(type(obj.geometry)) == "<type 'NurbsCurve'>"
                or str(type(obj.geometry)) == "<type 'PolylineCurve'>"
            ):
                o.user_input_geometry.append(obj.geometry)
        dict_compas_assembly_user_input["frames"].append(o)
    elif str.lower(subsequent_groups[0].layer_name) == "plate":
        o = compas_assembly_user_input("PLATE", group_id)
        for obj in subsequent_groups:
            if (
                str(type(obj.geometry)) == "<type 'LineCurve'>"
                or str(type(obj.geometry)) == "<type 'NurbsCurve'>"
                or str(type(obj.geometry)) == "<type 'PolylineCurve'>"
            ):
                o.user_input_geometry.append(obj.geometry)
        dict_compas_assembly_user_input["plates"].append(o)

    # print grouping information
    """
    for obj in subsequent_groups:
        print(obj)
        if isinstance(subsequent_groups, dict):
            for subsequent_group_id, objects in subsequent_groups.items():
                print("Subsequent Group ID:", subsequent_group_id)
                for obj in objects:
                    print(obj)
        else:
            for obj in subsequent_groups:
                print(obj)
    print()
    """


for key, value in dict_compas_assembly_user_input.items():
    print(key + ":")
    for item in value:
        print("  " + str(item))


# ==========================================================================
# fill the compas_assembly_user_input with geometry and types
# ==========================================================================
# write data to file

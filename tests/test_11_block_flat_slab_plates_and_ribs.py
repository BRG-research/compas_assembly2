from compas_assembly2 import Viewer, FabricationNest, Assembly

# https://compas.dev/compas/latest/reference/generated/compas.data.Data.html
from compas.data import json_load
from compas.geometry import Scale
from compas_assembly2.element import _

try:
    from compas_wood.joinery import get_connection_zones

    compas_wood_available = True
except ImportError:
    print("compas_wood package not available. Please install it.")
    compas_wood_available = False

if __name__ == "__main__":
    # ==========================================================================
    # ELEMENTS FROM JSON
    # ==========================================================================
    elements_json = json_load(fp="src/compas_assembly2/rhino_commands/rhino_command_convert_to_assembly_3.json")
    print(elements_json)

    # ==========================================================================
    # ELEMENTS NEST - TEST FABRICATION TYPE
    # This can be a function in a class that inherits from FABRICATION class
    # ==========================================================================
    elements_json.sort(key=lambda element: element.name, reverse=True)

    # ==========================================================================
    # COLLIDE ELEMENTS
    # ==========================================================================
    assembly = Assembly(name="elements_json")
    for element in elements_json:
        print(element.id)
        assembly.add_element_by_index(element)
    # collision_pairs = assembly.find_collisions_brute_force()
    # # pair0 = collision_pairs[0]

    # # print(assembly._elements._objects.keys()[0])
    # # print(assembly._elements._objects[tuple(pair0[0])])
    # # print(assembly._elements[pair0[0]])
    # joints = assembly.find_joints(collision_pairs)
    # print(joints)
    geometry = []
    # for joint in joints:
    #     geometry.append(joint.polygon)

    # print(collision_pairs)

    # ==========================================================================
    # DETECT JOINTS
    # ==========================================================================

# ==========================================================================
# COMPAS_WOOD
# ==========================================================================
if compas_wood_available and False:
    # ==========================================================================
    # COMPAS_WOOD SCALE POLYLINES DUE TO TOLERANCE
    # ==========================================================================
    simplices = assembly.get_elements_properties("simplex", True)
    scale = Scale.from_factors([100, 100, 100])
    for s in simplices:
        s.transform(scale)

    # ==========================================================================
    # COMPAS_WOOD CREATE ADJACENCY
    # ==========================================================================
    adjancency = []
    nested_lists = assembly.to_lists()
    # for i in range(len(nested_lists)):
    #     adjancency.append(0 + 3 * i)
    #     adjancency.append(2 + 3 * i)
    #     adjancency.append(-1)
    #     adjancency.append(-1)
    #     adjancency.append(0 + 3 * i)
    #     adjancency.append(1 + 3 * i)
    #     adjancency.append(-1)
    #     adjancency.append(-1)

    adjancency.extend([1, 0, -1, -1])
    adjancency.extend([1, 2, -1, -1])
    adjancency.extend([4, 0, -1, -1])
    adjancency.extend([4, 3, -1, -1])

    adjancency.extend([5, 7, -1, -1])
    adjancency.extend([5, 6, -1, -1])
    adjancency.extend([9, 8, -1, -1])
    adjancency.extend([8, 6, -1, -1])

    adjancency.extend([10, 11, -1, -1])
    adjancency.extend([10, 12, -1, -1])
    adjancency.extend([13, 11, -1, -1])
    adjancency.extend([13, 14, -1, -1])

    adjancency.extend([15, 16, -1, -1])
    adjancency.extend([15, 17, -1, -1])
    adjancency.extend([19, 16, -1, -1])
    adjancency.extend([19, 18, -1, -1])

    adjancency.extend([20, 21, -1, -1])
    adjancency.extend([20, 22, -1, -1])

    adjancency.extend([23, 24, -1, -1])
    adjancency.extend([23, 25, -1, -1])

    adjancency.extend([26, 27, -1, -1])
    adjancency.extend([26, 28, -1, -1])

    adjancency.extend([29, 30, -1, -1])
    adjancency.extend([29, 31, -1, -1])

    adjancency.extend([52, 53, -1, -1])
    adjancency.extend([52, 54, -1, -1])

    adjancency.extend([33, 34, -1, -1])
    adjancency.extend([33, 32, -1, -1])
    adjancency.extend([32, 0, -1, -1])
    adjancency.extend([34, 25, -1, -1])

    adjancency.extend([35, 36, -1, -1])
    adjancency.extend([35, 37, -1, -1])
    adjancency.extend([36, 16, -1, -1])
    adjancency.extend([37, 25, -1, -1])

    adjancency.extend([38, 39, -1, -1])
    adjancency.extend([39, 21, -1, -1])
    adjancency.extend([39, 2, -1, -1])

    adjancency.extend([41, 22, -1, -1])
    adjancency.extend([41, 40, -1, -1])
    adjancency.extend([41, 7, -1, -1])

    adjancency.extend([42, 43, -1, -1])
    adjancency.extend([42, 44, -1, -1])

    adjancency.extend([43, 6, -1, -1])
    adjancency.extend([44, 31, -1, -1])

    adjancency.extend([45, 46, -1, -1])
    adjancency.extend([45, 47, -1, -1])

    adjancency.extend([47, 11, -1, -1])
    adjancency.extend([46, 31, -1, -1])

    adjancency.extend([49, 12, -1, -1])
    adjancency.extend([49, 27, -1, -1])
    adjancency.extend([49, 48, -1, -1])

    adjancency.extend([51, 17, -1, -1])
    adjancency.extend([51, 28, -1, -1])
    adjancency.extend([51, 50, -1, -1])

    adjancency.extend([55, 56, -1, -1])
    adjancency.extend([55, 57, -1, -1])

    adjancency.extend([58, 59, -1, -1])
    adjancency.extend([58, 60, -1, -1])

    adjancency.extend([61, 62, -1, -1])
    adjancency.extend([61, 63, -1, -1])

    adjancency.extend([64, 65, -1, -1])
    adjancency.extend([64, 66, -1, -1])

    adjancency.extend([57, 27, -1, -1])
    adjancency.extend([57, 12, -1, -1])
    adjancency.extend([56, 53, -1, -1])
    adjancency.extend([56, 30, -1, -1])

    adjancency.extend([60, 24, -1, -1])
    adjancency.extend([59, 17, -1, -1])
    adjancency.extend([60, 54, -1, -1])
    adjancency.extend([59, 28, -1, -1])

    adjancency.extend([62, 2, -1, -1])
    adjancency.extend([63, 24, -1, -1])
    adjancency.extend([62, 21, -1, -1])
    adjancency.extend([63, 54, -1, -1])

    adjancency.extend([66, 22, -1, -1])
    adjancency.extend([66, 7, -1, -1])
    adjancency.extend([65, 53, -1, -1])
    adjancency.extend([65, 30, -1, -1])

    # ==========================================================================
    # COMPAS_WOOD RUN
    # ==========================================================================
    division_length = 40
    joint_parameters = [
        division_length,
        0.5,
        9,
        division_length * 1.5,
        0.65,
        10,
        division_length * 1.5,
        0.5,
        21,
        division_length,
        0.95,
        30,
        division_length,
        0.95,
        40,
        division_length,
        0.95,
        50,
    ]

    simplices = get_connection_zones(simplices, None, None, None, adjancency, joint_parameters, 2, [1, 1, 1.1], 4)
    # ==========================================================================
    # COMPAS_WOOD SCALE BACK TO ORIGINAL SCALE THE OUTLINES
    # ==========================================================================
    scale = Scale.from_factors([1 / 100, 1 / 100, 1 / 100])
    for outlines in simplices:
        for outline in outlines:
            outline.transform(scale)

    # ==========================================================================
    # CHANGE SIMPLEX AND COMPLEX OF ELEMENTS
    # ==========================================================================
    counter = 0
    for element_list in nested_lists:
        for element in element_list:
            element.simplex = simplices[counter]
            element.complex = [
                _.Triagulator.from_loft_two_point_lists(simplices[counter][-2].points, simplices[counter][-1].points)[0]
            ]
            counter = counter + 1

# ==========================================================================
# NEST ELEMENTS
# ==========================================================================
FabricationNest.pack_elements(elements=assembly.to_list(), nest_type=2, inflate=0.1, height_step=4)

# ==========================================================================
# VIEW2
# ==========================================================================
element_lists = assembly.to_lists(2)
print(element_lists)
Viewer.show_elements(
    element_lists, viewer_type="view2", show_grid=False, geometry=geometry
)  # assembly._elements.to_trimmed_list("x")

from compas_assembly2 import Viewer, FabricationNest, Assembly

# https://compas.dev/compas/latest/reference/generated/compas.data.Data.html
from compas.data import json_load


if __name__ == "__main__":
    # ==========================================================================
    # ELEMENTS FROM JSON
    # ==========================================================================
    elements_json = json_load(fp="src/compas_assembly2/rhino_commands/rhino_command_convert_to_assembly_0.json")

    # ==========================================================================
    # ELEMENTS NEST - TEST FABRICATION TYPE
    # This can be a function in a class that inherits from FABRICATION class
    # ==========================================================================
    elements_json.sort(key=lambda element: element.name, reverse=True)

    # ==========================================================================
    # COLLIDE ELEMENTS
    # ==========================================================================
    assembly = Assembly(value="elements_json")
    # , elements=elements_json
    for element in elements_json:
        assembly.add_by_index(element)
    
    print(assembly)

    # print(elements_json)
    # collision_pairs = assembly.find_collisions_brute_force()
    # # pair0 = collision_pairs[0]

    # # print(assembly._elements._objects.keys()[0])
    # # print(assembly._elements._objects[tuple(pair0[0])])
    # # print(assembly._elements[pair0[0]])
    # joints = assembly.find_joints(collision_pairs)
    geometry = []
    # for joint in joints:
    #     geometry.append(joint.polygon)

    # print(collision_pairs)

    # ==========================================================================
    # DETECT JOINTS
    # ==========================================================================

    # ==========================================================================
    # NEST ELEMENTS
    # ==========================================================================
    FabricationNest.pack_elements(elements=assembly.flatten(), nest_type=2, inflate=0.1, height_step=4)

    # ==========================================================================
    # VIEW2
    # ==========================================================================
    Viewer.show_elements(assembly.to_lists(), viewer_type="view2", show_grid=False, geometry=geometry)

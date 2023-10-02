from compas_assembly2 import FabricationNest, Assembly

# https://compas.dev/compas/latest/reference/generated/compas.data.Data.html
from compas.data import json_load
from compas.geometry import Scale, Frame, Translation, Transformation  # noqa: F401

try:
    from compas_wood.joinery import get_connection_zones  # noqa: F401

    compas_wood_available = True
except ImportError:
    print("compas_wood package not available. Please install it.")
    compas_wood_available = False

if __name__ == "__main__":
    # ==========================================================================
    # ELEMENTS FROM JSON
    # ==========================================================================
    elements_json = json_load(fp="src/compas_assembly2/rhino_commands/rhino_command_convert_to_assembly_3.json")

    # ==========================================================================
    # ELEMENTS NEST - TEST FABRICATION TYPE
    # This can be a function in a class that inherits from FABRICATION class
    # ==========================================================================
    elements_json.sort(key=lambda element: element.name, reverse=True)

    # ==========================================================================
    # COLLIDE ELEMENTS
    # ==========================================================================
    assembly = Assembly(value="elements_json")
    for element in elements_json:
        assembly.add_by_index(element)

    geometry = []

    # ==========================================================================
    # DETECT JOINTS
    # ==========================================================================

# ==========================================================================
# NEST ELEMENTS
# ==========================================================================
FabricationNest.pack_elements(elements=assembly.flatten(), nest_type=2, inflate=0.1, height_step=4)  # type: ignore

# ==========================================================================
# VIEW2
# ==========================================================================
# assembly.print_tree()
translation = Translation.from_vector([0, 0, 3])
frame0 = Frame.worldXY()
frame1 = Frame([3, 3, 0], [0, 1, 0], [0, 0, 1])

assembly = assembly.transformed_from_frame_to_frame(frame0, frame1)  # type: ignore
assembly.show(collapse_level=1)

# element_lists = assembly.collapse(2).to_lists()


# # # element_lists = [item for sublist in element_lists for item in sublist]
# # # print(flatten_to_individual_lists(element_lists))
# Viewer.show_elements(element_lists, viewer_type="view2", show_grid=False)  # assembly._elements.to_trimmed_list("x")

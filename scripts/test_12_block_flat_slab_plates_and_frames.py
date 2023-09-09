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
    elements_json = json_load(fp="src/compas_assembly2/rhino_commands/rhino_command_convert_to_assembly_4.json")

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
        assembly.add_element_by_index(element)

    geometry = []

    # ==========================================================================
    # DETECT JOINTS
    # ==========================================================================

# ==========================================================================
# NEST ELEMENTS
# ==========================================================================
FabricationNest.pack_elements(elements=assembly.to_list(), nest_type=2, inflate=0.1, height_step=4)

# ==========================================================================
# VIEW2
# ==========================================================================
element_lists = assembly.to_lists(1)
Viewer.show_elements(
    element_lists, viewer_type="view2", show_grid=False, geometry=geometry
)  # assembly._elements.to_trimmed_list("x")
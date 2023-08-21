from compas_assembly2 import Viewer, FabricationNest

# https://compas.dev/compas/latest/reference/generated/compas.data.Data.html
from compas.data import json_load


if __name__ == "__main__":

    # ==========================================================================
    # ELEMENTS FROM JSON
    # ==========================================================================
    elements_json = json_load(fp="src/compas_assembly2/rhino_commands/rhino_command_convert_to_assembly.json")

    # ==========================================================================
    # ELEMENTS NEST - TEST FABRICATION TYPE
    # This can be a function in a class that inherits from FABRICATION class
    # ==========================================================================
    elements_json.sort(key=lambda element: element.name, reverse=True)

    # ==========================================================================
    # NEST ELEMENTS
    # ==========================================================================
    FabricationNest.pack_elements(elements=elements_json, nest_type=2, inflate=0.1, height_step=4)

    # ==========================================================================
    # VIEW2
    # ==========================================================================
    Viewer.show_elements(elements_json, viewer_type="view2", show_grid=False)

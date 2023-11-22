from compas_assembly2 import Viewer
from compas.data import json_load

if __name__ == "__main__":
    # ==========================================================================
    # ELEMENTS FROM JSON
    # ==========================================================================
    path = "src/compas_assembly2/data_sets/element/element_vault_frame_box.json"
    elements_json = json_load(path)

    # ==========================================================================
    # VIEW2
    # ==========================================================================
    Viewer.show_elements(elements_json, show_grid=False, scale=0.001)
    #

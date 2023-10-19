from compas_assembly2 import Element, Viewer


if __name__ == "__main__":
    # ==========================================================================
    # ELEMENTS FROM JSON
    # ==========================================================================
    path = "src/compas_assembly2/rhino_commands/rhino_command_convert_to_assembly_floor_0_barrel_vault_hex.json"
    elements_json = Element.deserialize(path)

# ==========================================================================
# VIEW2
# ==========================================================================
Viewer.show_elements(elements_json, show_grid=True, scale=0.001)

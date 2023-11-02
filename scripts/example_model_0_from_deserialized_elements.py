from compas_assembly2 import Element, Model, ModelNode, ViewerModel


if __name__ == "__main__":
    # ==========================================================================
    # ELEMENTS FROM JSON
    # ==========================================================================
    path = "src/compas_assembly2/rhino_commands/rhino_command_convert_to_assembly_floor_0_barrel_vault_hex.json"
    elements_json = Element.deserialize(path)

    # ==========================================================================
    # MODEL
    # ==========================================================================
    # --------------------------------------------------------------------------
    # call the constructor
    # --------------------------------------------------------------------------
    model = Model("barrel_vault_hex")
    # --------------------------------------------------------------------------
    # add hirarchy
    # --------------------------------------------------------------------------

    structures = ModelNode("structures", elements=[])  # create node
    beams = ModelNode("beams", elements=[])  # create node
    plates = ModelNode("panels", elements=[])  # create node

    model.add(structures)  # create hierarchy by adding nodes to nodes
    structures.add(beams)  # create hierarchy by adding nodes to nodes
    structures.add(plates)  # create hierarchy by adding nodes to nodes

    # --------------------------------------------------------------------------
    # add elements to the hierarchy
    # --------------------------------------------------------------------------
    for element in elements_json:
        if element.name == "BEAM":
            beams.add_element(element)
        elif element.name == "PLATE":
            plates.add_element(element)

    # --------------------------------------------------------------------------
    # add linkages
    # --------------------------------------------------------------------------
    model.add_interaction(elements_json[8], elements_json[13])
    model.add_interaction(elements_json[13], elements_json[11])
    model.add_interaction(elements_json[7], elements_json[10])
    model.add_interaction(elements_json[6], elements_json[12])
    model.add_interaction(elements_json[12], elements_json[9])
    model.add_interaction(elements_json[18], elements_json[15])
    model.add_interaction(elements_json[17], elements_json[14])
    model.add_interaction(elements_json[14], elements_json[16])

    model.add_interaction(elements_json[7], elements_json[8])
    model.add_interaction(elements_json[7], elements_json[13])
    model.add_interaction(elements_json[7], elements_json[6])
    model.add_interaction(elements_json[7], elements_json[12])
    model.add_interaction(elements_json[10], elements_json[11])
    model.add_interaction(elements_json[10], elements_json[9])
    model.add_interaction(elements_json[10], elements_json[12])
    model.add_interaction(elements_json[10], elements_json[13])

    model.add_interaction(elements_json[18], elements_json[17])
    model.add_interaction(elements_json[18], elements_json[6])
    model.add_interaction(elements_json[18], elements_json[14])
    model.add_interaction(elements_json[18], elements_json[12])
    model.add_interaction(elements_json[15], elements_json[16])
    model.add_interaction(elements_json[15], elements_json[9])
    model.add_interaction(elements_json[15], elements_json[14])
    model.add_interaction(elements_json[15], elements_json[12])

    # beams connections
    # model.add_interaction(elements_json[5], elements_json[11])
    # model.add_interaction(elements_json[5], elements_json[13])
    # model.add_interaction(elements_json[5], elements_json[8])
    # model.add_interaction(elements_json[5], elements_json[4])
    # model.add_interaction(elements_json[5], elements_json[0])
    # model.add_interaction(elements_json[5], elements_json[1])
    # model.add_interaction(elements_json[5], elements_json[2])
    # model.add_interaction(elements_json[5], elements_json[3])

    # model.add_interaction(elements_json[22], elements_json[16])
    # model.add_interaction(elements_json[22], elements_json[14])
    # model.add_interaction(elements_json[22], elements_json[17])
    # model.add_interaction(elements_json[22], elements_json[21])
    # model.add_interaction(elements_json[22], elements_json[23])
    # model.add_interaction(elements_json[22], elements_json[24])
    # model.add_interaction(elements_json[22], elements_json[20])
    # model.add_interaction(elements_json[22], elements_json[19])

    # collumns connections
    geometry = model.get_interactions_as_lines()
    interactions = model.get_interactions_as_readable_info()
    print(interactions)
    # model.print()

# ==========================================================================
# VIEW2
# ==========================================================================
# model.print()
# print(model._interactions)
# Viewer.show_elements(elements_json, show_grid=True, scale=0.001, geometry=geometry)
ViewerModel.run(model)

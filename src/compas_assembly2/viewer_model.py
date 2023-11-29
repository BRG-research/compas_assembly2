from compas.geometry import Scale

from compas.colors import Color

import compas

compas_view2_imported = False

if not (compas.is_rhino() or compas.is_blender()):
    try:
        from compas_view2.app import App
        from compas_view2.collections import Collection
        from compas_view2.objects import MeshObject

        compas_view2_imported = True

    except ImportError:
        print("WARNING: compas_view2 is not installed!!!")


colors = [
    Color(0.929, 0.082, 0.498),
    Color(0.129, 0.572, 0.815),
    Color(0.5, 0.5, 0.5),
    Color(0.95, 0.95, 0.95),
    Color(0, 0, 0),
]


class ViewerModel:
    @classmethod
    def run(cls, model, scale_factor=0.001, geometry=[]):
        """display the model:
        a) right side shows the tree structure and element properties
        b) left side shows its adjacency
        elements class must have display_schema method that gives instructions how to display the properties"""

        # --------------------------------------------------------------------------
        # import viwer library
        # --------------------------------------------------------------------------
        if not compas_view2_imported:
            return

        # --------------------------------------------------------------------------
        # initialize the viewer
        # --------------------------------------------------------------------------
        viewer = App(show_grid=False, enable_sceneform=True, enable_propertyform=True, viewmode="lighted")

        # --------------------------------------------------------------------------
        # create a sceneform to display a tree structure
        # --------------------------------------------------------------------------
        elements_by_type = {}
        elements_by_guid = {}
        ViewerModel.create_spatial_structure(model, viewer, scale_factor, elements_by_type, elements_by_guid)

        # --------------------------------------------------------------------------
        # Create the form to toggle on and off the elements
        # --------------------------------------------------------------------------
        ViewerModel.visibility_of_class_properties(viewer, elements_by_type)

        # --------------------------------------------------------------------------
        #  Display adjacency
        # --------------------------------------------------------------------------
        ViewerModel.adjacency(viewer, model, elements_by_guid)

        # --------------------------------------------------------------------------
        #  Geometry that is not part of the model
        # --------------------------------------------------------------------------
        ViewerModel.add_geometry(viewer, scale_factor, geometry)

        # --------------------------------------------------------------------------
        # run the viewer
        # --------------------------------------------------------------------------
        viewer.show()

    @classmethod
    def add_to_dictionary(cls, dict, key, value):
        """helper function to add object in a list in the dictionary"""
        if key in dict:
            dict[key].append(value)
        else:
            dict[key] = [value]

    @classmethod
    def add_element_to_viewer(cls, viewer, element, scale_factor, elements_by_guid, elements_by_type, idx=0):
        """add element to the viewer"""

        # --------------------------------------------------------------------------
        # Create an empty object to store the Node name
        # --------------------------------------------------------------------------
        # node_geo = viewer.add(Collection([]), name="node_" + node.name)  # type: ignore

        # --------------------------------------------------------------------------
        # object that contains all the geometry properties of the element
        # --------------------------------------------------------------------------
        element_geo = viewer.add(
            Collection([]), name="element " + str.lower(element.name) + " " + str(idx)  # type: ignore
        )
        # node_geo.add(element_geo)

        # --------------------------------------------------------------------------
        # geometrical properties of an element
        # --------------------------------------------------------------------------

        display_schema = element.display_schema  # get the display schema from the element

        for idx, attr in enumerate(display_schema.items()):

            obj_name = attr[0]  # the geometrical attribute name
            display_options = attr[1]  # the display options of the attribute
            property_value = getattr(element, obj_name)

            # --------------------------------------------------------------------------
            # display the contents of the object
            # if the geometrical propery is stored in a list add a branch to it
            # --------------------------------------------------------------------------
            if isinstance(property_value, list):

                # an additiona branch
                sub_element_geo = viewer.add(Collection([]), name="property_" + obj_name)  # type: ignore
                element_geo.add(sub_element_geo)

                # individual geometry properties
                for obj in property_value:

                    ViewerModel.add_object(
                        viewer,
                        obj,
                        str.lower("property_" + type(obj).__name__),
                        display_options,
                        scale_factor,
                        sub_element_geo,
                        elements_by_guid,
                        obj_name + str(element.guid),
                        elements_by_type,
                    )

            else:

                ViewerModel.add_object(
                    viewer,
                    property_value,
                    "property_" + obj_name,
                    display_options,
                    scale_factor,
                    element_geo,
                    elements_by_guid,
                    obj_name + str(element.guid),
                    elements_by_type,
                )
        return element_geo

    @classmethod
    def create_spatial_structure(cls, model, viewer, scale_factor, elements_by_type, elements_by_guid):
        """display spatial structure of the model"""

        def _create_spatial_structure(node, viewer, prev_node_geo, elements_by_type, elements_by_guid):
            """recursive function to create the spatial structure of the model"""

            # --------------------------------------------------------------------------
            # Create an empty object to store the Node name
            # --------------------------------------------------------------------------
            node_geo = viewer.add(Collection([]), name="node_" + node.name)  # type: ignore

            # --------------------------------------------------------------------------
            # if object is not a root node, add it to the previous node
            # --------------------------------------------------------------------------
            if prev_node_geo:
                prev_node_geo.add(node_geo)

            # --------------------------------------------------------------------------
            # add children to the node
            # --------------------------------------------------------------------------
            if node.elements:
                # --------------------------------------------------------------------------
                # iterate elements and display properties following the display schema
                # --------------------------------------------------------------------------
                for idx, element in enumerate(node.elements):

                    # --------------------------------------------------------------------------
                    # object that contains all the geometry properties of the element
                    # --------------------------------------------------------------------------
                    element_geo = viewer.add(
                        Collection([]), name="element " + str.lower(element.name) + " " + str(idx)  # type: ignore
                    )
                    node_geo.add(element_geo)

                    # --------------------------------------------------------------------------
                    # geometrical properties of an element
                    # --------------------------------------------------------------------------

                    display_schema = element.display_schema  # get the display schema from the element

                    for idx, attr in enumerate(display_schema.items()):

                        obj_name = attr[0]  # the geometrical attribute name
                        display_options = attr[1]  # the display options of the attribute
                        property_value = getattr(element, obj_name)

                        # --------------------------------------------------------------------------
                        # display the contents of the object
                        # if the geometrical propery is stored in a list add a branch to it
                        # --------------------------------------------------------------------------
                        if isinstance(property_value, list):

                            # an additiona branch
                            sub_element_geo = viewer.add(Collection([]), name="property_" + obj_name)  # type: ignore
                            element_geo.add(sub_element_geo)

                            # individual geometry properties
                            for obj in property_value:

                                ViewerModel.add_object(
                                    viewer,
                                    obj,
                                    str.lower("property_" + type(obj).__name__),
                                    display_options,
                                    scale_factor,
                                    sub_element_geo,
                                    elements_by_guid,
                                    obj_name + str(element.guid),
                                    elements_by_type,
                                )

                        else:

                            ViewerModel.add_object(
                                viewer,
                                property_value,
                                "property_" + obj_name,
                                display_options,
                                scale_factor,
                                element_geo,
                                elements_by_guid,
                                obj_name + str(element.guid),
                                elements_by_type,
                            )

            # --------------------------------------------------------------------------
            # recursively add nodes
            # --------------------------------------------------------------------------
            for child_node in node.children:
                _create_spatial_structure(child_node, viewer, node_geo, elements_by_type, elements_by_guid)

        # --------------------------------------------------------------------------
        # the starting point of the recursive function
        # --------------------------------------------------------------------------
        _create_spatial_structure(model._hierarchy.root, viewer, None, elements_by_type, elements_by_guid)

        # --------------------------------------------------------------------------
        # add elements that are not in the hierarchy
        # --------------------------------------------------------------------------
        for idx, element in enumerate(model.elements.values()):
            if element not in elements_by_guid.values():
                ViewerModel.add_element_to_viewer(
                    viewer=viewer,
                    element=element,
                    scale_factor=scale_factor,
                    elements_by_guid=elements_by_guid,
                    elements_by_type=elements_by_type,
                    idx=idx,
                )

    @classmethod
    def add_object(
        cls,
        viewer,
        obj,
        name,
        display_options,
        scale_factor,
        sub_object,
        elements_by_guid,
        obj_name_and_guid,
        elements_by_type,
    ):
        """add object to the viewer and apply display options"""

        # --------------------------------------------------------------------------
        # hide the lines of the mesh
        # --------------------------------------------------------------------------

        # --------------------------------------------------------------------------
        # scale the object
        # --------------------------------------------------------------------------
        scale_xform = Scale.from_factors([scale_factor, scale_factor, scale_factor])
        obj.transform(scale_xform)

        # --------------------------------------------------------------------------
        # add object to the viewer
        # ---------------------------------------------------------------------------
        viewer_obj = viewer.add(
            obj,
            name=name,
            facecolor=display_options["facecolor"],
            linecolor=display_options["linecolor"],
            linewidth=display_options["linewidth"],
            opacity=display_options["opacity"],
            is_visible=display_options["is_visible"],
        )

        # --------------------------------------------------------------------------
        # hide the lines of the mesh
        # --------------------------------------------------------------------------
        if isinstance(viewer_obj, MeshObject):
            viewer_obj.show_lines = True

        # --------------------------------------------------------------------------
        # add object to the sub_object
        # --------------------------------------------------------------------------
        sub_object.add(viewer_obj)

        # --------------------------------------------------------------------------
        # add object to the dictionary of different types
        # --------------------------------------------------------------------------
        elements_by_guid[obj_name_and_guid] = viewer_obj

        # --------------------------------------------------------------------------
        # add object to the dictionary of different types to toggle the visibility
        # --------------------------------------------------------------------------
        ViewerModel.add_to_dictionary(elements_by_type, name, viewer_obj)

        # --------------------------------------------------------------------------
        # return the oject that will be added to the tree hierarchy for the scene form
        # --------------------------------------------------------------------------
        return viewer_obj

    @classmethod
    def visibility_of_class_properties(cls, viewer, elements_by_type):
        """create a form to toggle on and off the elements properties"""

        # --------------------------------------------------------------------------
        # create a form to toggle on and off the elements properties
        # the form is displayed on the right bottom side
        # --------------------------------------------------------------------------
        dock = viewer.sidedock("Show Hide Element Properties")

        # --------------------------------------------------------------------------
        # iterate the dictionary of elements sorted by type e.g. property_geometry_simplified
        # and create the checkboxes to toggle on and off the visibility
        # --------------------------------------------------------------------------
        for key, value in elements_by_type.items():

            # get state of object
            is_visible = elements_by_type[key][0].is_visible

            @viewer.checkbox(text=key, checked=is_visible, parent=dock.content_layout)
            def check(checked, key=key):
                for obj in elements_by_type[key]:
                    obj.is_visible = checked
                    viewer.view.update()

    @classmethod
    def adjacency(cls, viewer, model, elements_by_guid):
        """create a tab on the left side to display the adjacency of the elements
        when clicked geometries are highlighted"""

        object_colors = {}
        for obj in viewer.view.objects:
            object_colors[obj] = (obj.facecolor, obj.opacity, obj)

        def reset_colors(self, entry):
            for key, value in object_colors.items():
                value[2].facecolor = value[0]
                value[2].opacity = value[1]
            viewer.view.update()

        def show_attributes_form(self, entry):
            reset_colors(self, entry)
            entry["data"][0].facecolor = colors[0]
            entry["data"][0].opacity = 1
            for idx in range(1, len(entry["data"])):
                entry["data"][idx].facecolor = colors[1]
                entry["data"][idx].opacity = 1
            viewer.view.update()

        # --------------------------------------------------------------------------
        # vertex neighborhoods
        # --------------------------------------------------------------------------
        interactions_vertex_neighbors = model.get_interactions_as_nodes_and_neighbors_lists()

        dict_guid_and_index = {}
        counter = 0
        for key in model.elements:
            dict_guid_and_index[key] = counter
            counter = counter + 1

        my_contents_form_data = []
        for idx, node in enumerate(interactions_vertex_neighbors[0]):
            neighbors = interactions_vertex_neighbors[1][idx]

            vertex_neighbors_to_select = [elements_by_guid["geometry" + str(node)]]
            vertex_vertex_to_select = []
            for n in neighbors:
                vertex_neighbors_to_select.append(elements_by_guid["geometry" + str(n)])
                vertex_vertex_to_select.append(
                    [elements_by_guid["geometry" + str(node)], elements_by_guid["geometry" + str(n)]]
                )

            node_text = dict_guid_and_index[node]
            my_contents_form_data_current = {
                "key": node_text,
                "on_item_double_clicked": reset_colors,
                "on_item_pressed": show_attributes_form,
                "data": vertex_neighbors_to_select,
                # "attributes": {str.lower(str(interactions_readable[idx][1]))},
                "children": [],
                "attributes": {},
            }

            for jdx, n in enumerate(neighbors):
                neighbor_text = dict_guid_and_index[n]

                my_contents_form_data_current["children"].append(
                    {
                        "key": neighbor_text,
                        "on_item_double_clicked": reset_colors,
                        "on_item_pressed": show_attributes_form,
                        "data": vertex_vertex_to_select[jdx],
                        "children": [],
                        "attributes": {},
                        # "attributes": {"attribute7": 7, "attribute8": 8, "attribute9": 9},
                        # "color": (0, 0, 100),  # This assigns a color to the entrie row of this entry
                    }
                )
            my_contents_form_data.append(my_contents_form_data_current)

        # # --------------------------------------------------------------------------
        # # Define the function that will be called when an item is pressed
        # # --------------------------------------------------------------------------
        # def select(self, entry):
        #     viewer.selector.reset()
        #     entry["data"][0].is_selected = True  # here geometry is selected
        #     entry["data"][1].is_selected = True
        #     viewer.view.update()

        # # --------------------------------------------------------------------------
        # # Create the data
        # # by iterating the interactions list that contains the guids of the geometryes
        # # whereas the interactions_readable contains the names of the geometryes
        # # --------------------------------------------------------------------------
        # data = []

        # for idx, tuple_of_guids in enumerate(interactions):
        #     obj1 = elements_by_guid["geometry" + str(tuple_of_guids[0])]
        #     obj2 = elements_by_guid["geometry" + str(tuple_of_guids[1])]
        #     data.append(
        #         {
        #             "object1": str.lower(str(interactions_readable[idx][0])),
        #             "object2": str.lower(str(interactions_readable[idx][1])),
        #             "on_item_pressed": select,
        #             "data": [obj1, obj2],
        #         }
        #     )

        # --------------------------------------------------------------------------
        # Add the treeform
        # --------------------------------------------------------------------------
        viewer.treeform("Adjacency", data=my_contents_form_data, show_headers=False, columns=["key"])
        # viewer.treeform("Objects", location="left", data=data, show_headers=True, columns=["object1", "object2"])

    @classmethod
    def add_geometry(cls, viewer, scale_factor, geometry=[]):
        group = viewer.add(Collection([]), name="non_model_geometry")
        for obj in geometry:
            # --------------------------------------------------------------------------
            # scale the object
            # --------------------------------------------------------------------------
            scale_xform = Scale.from_factors([scale_factor, scale_factor, scale_factor])
            obj.transform(scale_xform)
            group.add(obj, name="geometry", facecolor=(0, 0.6, 1), linecolor=(0, 0, 0), linewidth=1, opacity=1)

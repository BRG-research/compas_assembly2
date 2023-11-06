from compas.geometry import (
    Scale,
)


try:
    from compas_view2.app import App
    from compas_view2.collections import Collection
    from compas_view2.objects import MeshObject

    compas_view2_imported = True
except ImportError:
    print("compas_view2 is not installed. Skipping the code. ---> Use pip install compas_view <---")
    compas_view2_imported = False


class ViewerModel:
    @classmethod
    def run(cls, model, scale_factor=0.001):
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
        viewer = App(enable_sceneform=True, enable_propertyform=True, viewmode="lighted")

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
    def create_spatial_structure(cls, model, viewer, scale_factor, elements_by_type, elements_by_guid):
        """display spatial structure of the model"""

        def _create_spatial_structure(node, viewer, prev_node_geo, elements_by_type, elements_by_guid):
            """recursive function to create the spatial structure of the model"""

            # --------------------------------------------------------------------------
            # Create an empty object to store the ModelNode name
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
            viewer_obj.show_lines = False

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
        # iterate the dictionary of elements sorted by type e.g. property_simplex
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
        when clicked complexes are highlighted"""

        # --------------------------------------------------------------------------
        # Get the adjacency from the model
        # --------------------------------------------------------------------------
        interactions_readable = model.get_interactions_as_readable_info()
        interactions = model.get_interactions()

        # --------------------------------------------------------------------------
        # Define the function that will be called when an item is pressed
        # --------------------------------------------------------------------------
        def select(self, entry):
            viewer.selector.reset()
            entry["data"][0].is_selected = True  # here complex is selected
            entry["data"][1].is_selected = True
            viewer.view.update()

        # --------------------------------------------------------------------------
        # Create the data
        # by iterating the interactions list that contains the guids of the complexes
        # whereas the interactions_readable contains the names of the complexes
        # --------------------------------------------------------------------------
        data = []

        for idx, tuple_of_guids in enumerate(interactions):
            obj1 = elements_by_guid["complex" + str(tuple_of_guids[0])]
            obj2 = elements_by_guid["complex" + str(tuple_of_guids[1])]
            data.append(
                {
                    "object1": str.lower(str(interactions_readable[idx][0])),
                    "object2": str.lower(str(interactions_readable[idx][1])),
                    "on_item_pressed": select,
                    "data": [obj1, obj2],
                }
            )

        # --------------------------------------------------------------------------
        # Add the treeform
        # --------------------------------------------------------------------------
        viewer.treeform("Objects", location="left", data=data, show_headers=True, columns=["object1", "object2"])

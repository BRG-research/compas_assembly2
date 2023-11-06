from compas.geometry import (
    Scale,
)

from compas_view2.objects import MeshObject
from compas_view2.collections import Collection


class ViewerModel:
    @classmethod
    def run(cls, model, scale_factor=0.001):
        # --------------------------------------------------------------------------
        # import viwer library
        # --------------------------------------------------------------------------

        try:
            from compas_view2.app import App

        except ImportError:
            print("compas_view2 is not installed. Skipping the code. ---> Use pip install compas_view <---")
            return

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
        if key in dict:
            dict[key].append(value)
        else:
            dict[key] = [value]

    @classmethod
    def create_spatial_structure(cls, model, viewer, scale_factor, elements_by_type, elements_by_guid):
        """display spatial structure of the model"""

        def _create_spatial_structure(node, viewer, prev_node_geometry_obj, elements_by_type, elements_by_guid):

            # --------------------------------------------------------------------------
            # Create an empty object to store the ModelNode name
            # --------------------------------------------------------------------------
            node_geometry_obj = viewer.add(Collection([]), name="node_" + node.name)  # type: ignore

            # --------------------------------------------------------------------------
            # if object is not a root node, add it to the previous node
            # --------------------------------------------------------------------------
            if prev_node_geometry_obj:
                prev_node_geometry_obj.add(node_geometry_obj)

            # --------------------------------------------------------------------------
            # add children to the node
            # --------------------------------------------------------------------------
            if node.elements:
                # --------------------------------------------------------------------------
                # iterate elements and display properties following the display schema
                # --------------------------------------------------------------------------
                for idx, element in enumerate(node.elements):

                    # --------------------------------------------------------------------------
                    # object that contains all the geometry of the element
                    # --------------------------------------------------------------------------
                    element_geometry_obj = viewer.add(
                        Collection([]), name="element " + str.lower(element.name) + " " + str(idx)
                    )
                    node_geometry_obj.add(element_geometry_obj)

                    # --------------------------------------------------------------------------
                    # geometrical properties of an element
                    # --------------------------------------------------------------------------
                    display_schema = element.display_schema
                    for idx, attr in enumerate(display_schema.items()):

                        object_name = attr[0]
                        display_options = attr[1]

                        property_value = getattr(element, object_name)

                        # --------------------------------------------------------------------------
                        # display the contents of the object
                        # if the geometrical propery is stored ina list add a branch to it
                        # --------------------------------------------------------------------------
                        if not isinstance(property_value, list):

                            geometry = ViewerModel.add_object(
                                viewer, property_value, "property_" + object_name, display_options, scale_factor
                            )
                            element_geometry_obj.add(geometry)
                            elements_by_guid[object_name + str(element.guid)] = geometry
                            ViewerModel.add_to_dictionary(elements_by_type, "property_" + object_name, geometry)

                        else:

                            sub_element_geometry_obj = viewer.add(Collection([]), name="property_" + object_name)

                            element_geometry_obj.add(sub_element_geometry_obj)

                            for obj in property_value:

                                geometry = ViewerModel.add_object(
                                    viewer,
                                    obj,
                                    str.lower("property_" + type(obj).__name__),
                                    display_options,
                                    scale_factor,
                                )

                                sub_element_geometry_obj.add(geometry)
                                elements_by_guid[object_name + str(element.guid)] = geometry
                                ViewerModel.add_to_dictionary(elements_by_type, "property_" + object_name, geometry)

            # recursively add nodes
            for child_node in node.children:
                _create_spatial_structure(child_node, viewer, node_geometry_obj, elements_by_type, elements_by_guid)

        _create_spatial_structure(model._hierarchy.root, viewer, None, elements_by_type, elements_by_guid)

    @classmethod
    def add_object(cls, viewer, obj, name, display_options, scale_factor):

        scale_xform = Scale.from_factors([scale_factor, scale_factor, scale_factor])
        obj.transform(scale_xform)

        obj = viewer.add(
            obj,
            name=name,
            facecolor=display_options["facecolor"],
            linecolor=display_options["linecolor"],
            linewidth=display_options["linewidth"],
            opacity=display_options["opacity"],
            is_visible=display_options["is_visible"],
        )
        if isinstance(obj, MeshObject):
            obj.show_lines = False

        return obj

    @classmethod
    def visibility_of_class_properties(cls, viewer, elements_by_type):
        dock = viewer.sidedock("Show Hide Element Properties")

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

        interactions_readable = model.get_interactions_as_readable_info()
        interactions = model.get_interactions()

        # Define the function that will be called when an item is pressed
        def select(self, entry):
            viewer.selector.reset()
            entry["data"][0].is_selected = True
            entry["data"][1].is_selected = True
            viewer.view.update()

        # Create the data
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

        # Add the treeform
        viewer.treeform("Objects", location="left", data=data, show_headers=True, columns=["object1", "object2"])

from compas.geometry import (
    # Polyline,
    # Point,
    # Box,
    # Line,
    # Vector,
    # Pointcloud,
    Transformation,
    # Translation,
    # Frame,
    # Quaternion,
    Scale,
)

# from compas.datastructures import Mesh
from compas.colors import Color
from compas_view2.collections import Collection

# from compas_assembly2.fabrication import FABRICATION_TYPES
# import math
# import time


class ViewerModel:
    @classmethod
    def run(cls, model, scale=0.001):
        # ==========================================================================
        # import viwer library
        # ==========================================================================

        try:
            from compas_view2.app import App
            from compas_view2.shapes import Arrow

        except ImportError:
            print("compas_view2 is not installed. Skipping the code. ---> Use pip install compas_view <---")
            return

        viewer = App(enable_sceneform=True, enable_propertyform=True, enable_sidedock1=True)
        viewer.sidedock1.setWindowTitle("Visibility of element properties")

        # ==========================================================================
        # create a sceneform to display a tree structure
        # ==========================================================================
        elements_by_type = {}
        ViewerModel.create_spatial_structure(model, viewer, scale, elements_by_type)

        # ==========================================================================
        # Create the form to toggle on and off the elements
        # ==========================================================================
        ViewerModel.visibility_of_class_properties(viewer, elements_by_type)

        # ==========================================================================
        #  Display adjacency
        # ==========================================================================
        interactions = model.get_interactions_as_readable_info()
        ViewerModel.adjacency(viewer, interactions)

        # ==========================================================================
        # run the viewer
        # ==========================================================================
        viewer.show()

    @classmethod
    def add_to_dictionary(cls, dict, key, value):
        if key in dict:
            dict[key].append(value)
        else:
            dict[key] = [value]

    @classmethod
    def create_spatial_structure(cls, model, viewer, scale, elements_by_type):
        """display spatial structure of the model"""

        def _create_spatial_structure(node, viewer, prev_node_geometry_obj, elements_by_type):

            # Create an empty object to store the ModelNode name
            node_geometry_obj = viewer.add(Collection([]), name="node_" + node.name)

            # if object is not a root node, add it to the previous node
            if prev_node_geometry_obj:
                prev_node_geometry_obj.add(node_geometry_obj)

            # add children to the node
            if node.elements:
                # --------------------------------------------------------------------------
                # iterate elements and display properties following the display schema
                # --------------------------------------------------------------------------
                for element in node.elements:

                    # --------------------------------------------------------------------------
                    # object that contains all the geometry of the element
                    # --------------------------------------------------------------------------
                    element_geometry_obj = viewer.add(Collection([]), name="element_" + str.lower(element.name))
                    node_geometry_obj.add(element_geometry_obj)
                    element_geometry_obj.matrix = Scale.from_factors([scale, scale, scale]).matrix
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
                            geometry = viewer.add(
                                property_value,
                                name="property_" + object_name,
                                is_visible=display_options["is_visible"],
                            )
                            element_geometry_obj.add(geometry)
                            ViewerModel.add_to_dictionary(elements_by_type, "property_" + object_name, geometry)
                        else:
                            sub_element_geometry_obj = viewer.add(Collection([]), name="property_" + object_name)
                            element_geometry_obj.add(sub_element_geometry_obj)
                            for obj in property_value:
                                geometry = viewer.add(
                                    obj,
                                    name=str.lower("property_" + type(obj).__name__),
                                    is_visible=display_options["is_visible"],
                                )
                                sub_element_geometry_obj.add(geometry)
                                ViewerModel.add_to_dictionary(elements_by_type, "property_" + object_name, geometry)

            # recursively add nodes
            for child_node in node.children:
                _create_spatial_structure(child_node, viewer, node_geometry_obj, elements_by_type)

        _create_spatial_structure(model.root, viewer, None, elements_by_type)

    @classmethod
    def visibility_of_class_properties(cls, viewer, elements_by_type):
        viewer.sidedock1.clear()

        for key, value in elements_by_type.items():

            # get state of object
            is_visible = elements_by_type[key][0].is_visible

            @viewer.checkbox(text=key, checked=is_visible, parent=viewer.sidedock1.content_layout)
            def check(checked, key=key):
                for obj in elements_by_type[key]:
                    obj.is_visible = checked
                    viewer.view.update()

    @classmethod
    def adjacency(cls, viewer, interactions):

        print("adjacency form")


        # Define the function that will be called when an item is pressed
        def select(self, entry):
            # print(self, entry)
            viewer.selector.reset()
            entry["data"][0].is_selected = True
            entry["data"][1].is_selected = True
            viewer.view.update()


        # # Create the data
        data = []

        # for i in range(10):
        #     obj1 = viewer.add(basic_box.transformed(Translation.from_vector((i, 0, 0))))
        #     obj2 = viewer.add(basic_box.transformed(Translation.from_vector((i, 1, 0))))
        #     data.append({"object1": i, "object2": 2 * i, "on_item_pressed": select, "data": [obj1, obj2]})

        # Add the treeform
        treeform2 = viewer.treeform("Objects", location="left", data=data, show_headers=True, columns=["object1", "object2"])

        # tabs = [
        #     {
        #         "name": "adjancency",
        #         "data": [
        #             {
        #                 "node_0": "a",
        #                 "node_1": 1,
        #             },
        #             {
        #                 "node_0": "b",
        #                 "node_1": 2,
        #             },
        #             {
        #                 "node_0": "c",
        #                 "node_1": 3,
        #             },
        #         ],
        #     },
        # ]

        # if(isinstance(adjacency, list)):
        

        # treeform2 = viewer.tabsform(
        #     "Adjacency Form",
        #     location="left",
        #     tabs=tabs,
        #     show_headers=True,
        #     columns=["node_0", "node_1"],
        #     striped_rows=True,
        # )

        
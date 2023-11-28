from compas.data import json_load
from compas.geometry import (
    Polygon,
)

from compas_assembly2 import Model, Algorithms, Viewer, ViewerModel, Element, Node
from compas.geometry import Frame


def example_get_collision_pairs():
    # ==========================================================================
    # ELEMENTS FROM JSON
    # ==========================================================================
    path = "src/compas_assembly2/data_sets/element/element_alessandro_0.json"
    elements_json = json_load(path)

    # ==========================================================================
    # NEAREST NEIGHBOR
    # ==========================================================================
    attributes = []
    # for e in elements_json:
    #     attributes.append(e.id[0])

    collision_pairs = Algorithms.get_collision_pairs_with_attributes(elements_json, attributes)
    print(collision_pairs)


def example_get_collision_pairs_with_attributes():
    # ==========================================================================
    # ELEMENTS FROM JSON
    # ==========================================================================
    path = "src/compas_assembly2/data_sets/element/element_alessandro_0.json"
    elements_json = json_load(path)

    # ==========================================================================
    # NEAREST NEIGHBOR
    # ==========================================================================
    attributes = []
    for e in elements_json:
        attributes.append(e.id[0])

    collision_pairs = Algorithms.get_collision_pairs_with_attributes(elements_json, attributes)
    print(collision_pairs)


def example_get_collision_pairs_kdtree():
    # ==========================================================================
    # ELEMENTS FROM JSON
    # ==========================================================================
    path = "src/compas_assembly2/data_sets/element/element_alessandro_0.json"
    elements_json = json_load(path)

    # ==========================================================================
    # KDTREE SEARCH
    # ==========================================================================
    collision_pairs_kd_tree = Algorithms.get_collision_pairs_kdtree(elements_json, max_neighbours=8)
    print(collision_pairs_kd_tree)


def example_face_to_face():
    # ==========================================================================
    # ELEMENTS FROM JSON
    # ==========================================================================
    path = "src/compas_assembly2/data_sets/element/element_alessandro_0.json"
    elements_json = json_load(path)

    # ==========================================================================
    # NEAREST NEIGHBOR
    # ==========================================================================
    attributes = []
    # for e in elements_json:
    #     attributes.append(e.id[0])

    collision_pairs = Algorithms.get_collision_pairs_with_attributes(elements_json, attributes)

    # ==========================================================================
    # FACE TO FACE DETECTION
    # ==========================================================================
    geometry = []
    for idx, collision_pair in enumerate(collision_pairs):
        result = Algorithms.face_to_face(elements_json[collision_pair[0]], elements_json[collision_pair[1]])
        for r in result:
            if result:
                geometry.append(r[1])
    Viewer.show_elements(elements_json, show_grid=False, scale=0.001, geometry=geometry)


def example_shortest_path():
    # ==========================================================================
    # ELEMENTS FROM JSON
    # ==========================================================================
    path = "src/compas_assembly2/data_sets/element/element_alessandro_0.json"
    elements_json = json_load(path)

    # ==========================================================================
    # NEAREST NEIGHBOR
    # ==========================================================================
    attributes = []
    # for e in elements_json:
    #     attributes.append(e.id[0])

    collision_pairs = Algorithms.get_collision_pairs_with_attributes(elements_json, attributes)

    # create model
    model = Model()
    model.add_elements(elements_json)
    for collision_pair in collision_pairs:
        model.add_interaction(elements_json[collision_pair[0]], elements_json[collision_pair[1]])

    # run the shortest path
    elements = Algorithms.shortest_path(model, model.element_at(0), model.element_at(7))

    # vizualize the shortest path, in this case colorize mesh faces as polygons
    geometry = []
    for element in elements:
        mesh = element.geometry[0]  # mesh in this case
        polygons = mesh.to_polygons()
        for polygon in polygons:
            geometry.append(Polygon(polygon))

    # ==========================================================================
    # VIEWER
    # ==========================================================================
    # ViewerModel.run(model, scale_factor=0.001)
    Viewer.show_elements(elements_json, show_grid=False, scale=0.001, geometry=geometry)


def example_model_interfaces():
    # ==========================================================================
    # ELEMENTS FROM JSON
    # ==========================================================================
    path = "src/compas_assembly2/data_sets/element/element_alessandro_0.json"
    elements_json = json_load(path)

    # ==========================================================================
    # CREATE MODEL
    # ==========================================================================
    model = Model()
    model.add_elements(elements_json)
    model.find_interactions()

    # ==========================================================================
    # Vizualize the interactions
    # ==========================================================================
    ViewerModel.run(model, scale_factor=0.001, geometry=model.get_interactions_geometry())


def example_model_interfaces_cross_vault():
    # ==========================================================================
    # ELEMENTS FROM JSON
    # ==========================================================================
    meshes = json_load("src/compas_assembly2/data_sets/mesh/cross_vault.json")

    # convert meshes to elements and the geometry_simplified is the mesh center
    elements = []
    for idx, mesh in enumerate(meshes):

        if mesh.number_of_faces() < 4:
            continue

        mid_point = mesh.centroid()
        faces = list(mesh.faces())

        x_axis = mesh.face_normal(faces[0])
        y_axis = mesh.face_normal(faces[1])
        frame = Frame(point=mid_point, xaxis=x_axis, yaxis=y_axis)
        element = Element(geometry_simplified=mid_point, geometry=mesh, frame=frame)
        elements.append(element)

    # ==========================================================================
    # CREATE MODEL
    # ==========================================================================
    model = Model(name="cross_vault")
    model.add_elements(elements)

    model.add_node(Node("blocks", elements=elements))
    model.find_interactions(tmax=1, amin=1e1 / 1000)
    model.print()

    # ==========================================================================
    # Vizualize the interactions
    # ==========================================================================
    # geometry=model.get_interactions_geometry()
    # ViewerModel.run(model, scale_factor=1, geometry=ca2.global_geometry)
    ViewerModel.run(model, scale_factor=1, geometry=model.get_interactions_geometry())


def example_model_shortest_path():
    # ==========================================================================
    # ELEMENTS FROM JSON
    # ==========================================================================
    path = "src/compas_assembly2/data_sets/element/element_alessandro_0.json"
    elements_json = json_load(path)

    # ==========================================================================
    # CREATE MODEL
    # ==========================================================================
    model = Model()
    model.add_elements(elements_json)
    model.find_interactions()

    # ==========================================================================
    # FIND SHORTEST PATH
    # ==========================================================================
    elements, geometry = model.find_shortest_path(elements_json[0], elements_json[7], True)

    # ==========================================================================
    # Vizualize the interactions
    # ==========================================================================
    ViewerModel.run(model, scale_factor=0.001, geometry=geometry)


def example_model_shortest_path_from_mesh():
    # ==========================================================================
    # ELEMENTS FROM JSON
    # ==========================================================================
    path = "src/compas_assembly2/data_sets/mesh/cross_vault.json"
    meshes_json = json_load(path)
    elements_json = []
    for idx, mesh in enumerate(meshes_json):
        frame = Frame(mesh.centroid(), mesh.face_normal(0), mesh.face_normal(1))
        element = Element(id=idx, geometry=mesh, geometry_simplified=mesh.centroid(), frame=frame)
        elements_json.append(element)

    # ==========================================================================
    # CREATE MODEL
    # ==========================================================================
    model = Model()
    model.add_elements(elements_json)
    model.find_interactions(detection_type=0, aaab_inflation=0.1, tmax=0.1, amin=1e1 / 1000)
    geometry_links = model.get_interactions_as_lines()

    # ==========================================================================
    # FIND SHORTEST PATH
    # ==========================================================================
    geometry = []
    elements, geometry = model.find_shortest_path(elements_json[4], elements_json[180], True)
    geometry_links.extend(geometry)
    elements, geometry = model.find_shortest_path(elements_json[91], elements_json[181], True)
    geometry_links.extend(geometry)
    elements, geometry = model.find_shortest_path(elements_json[92], elements_json[182], True)
    geometry_links.extend(geometry)
    elements, geometry = model.find_shortest_path(elements_json[3], elements_json[183], True)
    geometry_links.extend(geometry)
    # elements, geometry = model.find_shortest_path(elements_json[3], elements_json[135], True)
    # geometry_links.extend(geometry)
    # elements, geometry = model.find_shortest_path(elements_json[330], elements_json[135], True)
    # geometry_links.extend(geometry)
    # elements, geometry = model.find_shortest_path(elements_json[330], elements_json[0], True)
    # geometry_links.extend(geometry)
    # elements, geometry = model.find_shortest_path(elements_json[4], elements_json[37], True)
    # geometry_links.extend(geometry)

    # ==========================================================================
    # Vizualize the interactions
    # ==========================================================================
    # Viewer.show_elements(elements_json, show_grid=False, scale=1, geometry=geometry)
    ViewerModel.run(model, scale_factor=1, geometry=geometry_links)


if __name__ == "__main__":
    # example_get_collision_pairs()
    # example_get_collision_pairs_with_attributes()
    # example_get_collision_pairs_kdtree()
    # example_face_to_face()
    # example_shortest_path()
    # example_model_interfaces()
    # example_model_interfaces_cross_vault()
    example_model_shortest_path_from_mesh()
    # example_model_shortest_path()

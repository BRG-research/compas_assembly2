from compas.data import json_load
from compas.geometry import Frame
from compas_assembly2 import Element, Model, Node, ViewerModel

if __name__ == "__main__":

    meshes = json_load("src/compas_assembly2/data_sets/model/model_armadillo.json")

    # convert meshes to elements and the geometry_simplified is the mesh center
    elements = []
    for mesh in meshes:
        mid_point = mesh.centroid()
        x_axis = mesh.face_normal(0)
        y_axis = mesh.face_normal(1)
        frame = Frame(point=mid_point, xaxis=x_axis, yaxis=y_axis)
        element = Element(geometry_simplified=mid_point, geometry=[mesh], frame=frame)
        elements.append(element)

    # --------------------------------------------------------------------------
    # create model
    # --------------------------------------------------------------------------
    model = Model(name="cross_vault")
    model.add_node(Node("blocks", elements=elements))
    model.print()

    # --------------------------------------------------------------------------
    # Vizualize it
    # --------------------------------------------------------------------------
    ViewerModel.run(model, scale_factor=1)
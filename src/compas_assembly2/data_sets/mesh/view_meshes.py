from compas_view2.app import App

# load meshes from json file
from compas.data import json_load

meshes = json_load("src/compas_assembly2/data_sets/mesh/arch_pi_3_4.json")

viewer = App(show_grid=False, enable_sceneform=True, enable_propertyform=True, viewmode="lighted")

for mesh in meshes:
    viewer.add(mesh, hide_coplanaredges=True, linecolor=(0, 0, 0))  # type: ignore

viewer.show()

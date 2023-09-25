import os

from compas_ifc.viewer import IFC_viewer

HERE = os.path.dirname(__file__)
FILE = os.path.join(
    HERE,
    "..",
    "data",
    "A0090.ifc",
)


viewer = IFC_viewer()
viewer.open(FILE)

viewer.add_all()
viewer.show_forms()
viewer.view.camera.zoom_extents()

viewer.show()
# import os

# from compas_view2.app import App
# from compas_view2.collections import Collection

# from compas_ifc.model import Model

# HERE = os.path.dirname(__file__)
# FILE = os.path.join(
#     HERE,
#     "..",
#     "data",
#     "A0090.ifc",
# )

# # # model = Model(FILE)
# model = Model("C:/brg/2_code/compas_assembly2/data/A0090.ifc")
# for wall in model.get_entities_by_type("IFCSLAB"):
#     print("Converting brep:", wall)
#     # viewer.add(Collection(wall.body_with_opening), name="{}.Body".format(wall.name), opacity=0.5)

#     # print("creating section...")
#     # sections = []
#     # for shape in wall.body_with_opening:
#     #     sections.append(shape.slice(sectionPlane))

#     # print(sections)

#     # viewer.add(Collection(sections), name="{}.Sections".format(wall.name), linecolor=(1, 0, 0), linewidth=5)

# print("Finished")


# # viewer = IFC_viewer()
# # viewer.open(FILE)

# # viewer.add_all()
# # viewer.show_forms()
# # viewer.view.camera.zoom_extents()

# # viewer.run()

# # viewer = App(enable_sceneform=True)

# # all_entities = model.get_all_entities()
# # # print("Total number of entities: ", len(all_entities))
# # for entity in all_entities:
# #     print(entity)
# # for entity in model.get_all_entities():
# #     # print("Converting brep:", entity)
# #     print(entity.attributes)
# #     if entity.has_attribute("body"):
# #         viewer.add(Collection(entity.body), name="body", opacity=0.5, facecolor=(0, 1, 0))
# #         viewer.add(Collection(entity.opening), name="opening", facecolor=(1, 0, 0))
# #         obj = viewer.add(Collection(entity.body_with_opening), name="combined", show_faces=True)
# #     # obj.translation = [0, 2, 0]

# # # viewer.view.camera.zoom_extents()
# # # viewer.run()

from compas_view2.app import App
from compas.geometry import Box, Frame, Translation

viewer = App()


# Create some boxes and the data
basic_box = Box(1, 1, 1, Frame([0, 0, 0], [1, 0, 0], [0, 1, 0]))
data = []


# Define the function that will be called when an item is pressed
def select(self, entry):
    # print(self, entry)
    viewer.selector.reset()
    entry["data"][0].is_selected = True
    entry["data"][1].is_selected = True
    viewer.view.update()


# Create the data
for i in range(10):
    obj1 = viewer.add(basic_box.transformed(Translation.from_vector((i, 0, 0))))
    obj2 = viewer.add(basic_box.transformed(Translation.from_vector((i, 1, 0))))
    data.append({"object1": i, "object2": 2 * i, "on_item_pressed": select, "data": [obj1, obj2]})

# Add the treeform
treeform2 = viewer.treeform("Objects", location="right", data=data, show_headers=True, columns=["object1", "object2"])

viewer.show()

# from compas_view2.app import App
# import os
# from graphviz import Digraph
# import matplotlib.image as mpimg
# import matplotlib.pyplot as plt
# from PIL import Image


# # ==========================================================================
# # crate a Graphviz
# # ==========================================================================

# # Set the path to the Graphviz executable
# graphviz_executable = r"C:\Program Files\Graphviz\bin"
# os.environ["PATH"] += (
#     os.pathsep + graphviz_executable
# )  # Add the Graphviz bin directory to the PATH environment variable

# # Create a Digraph object
# dot = Digraph(comment="graph", format="png")
# # dot.attr(rankdir="LR")
# dot.node("structures", "structures", shape="rectangle")
# dot.node("plates", "plates", shape="rectangle")
# dot.node("beams", "beams", shape="rectangle")
# dot.node("beam0", "beam0", shape="rectangle")
# dot.node("beam1", "beam1", shape="rectangle")
# dot.node("beam2", "beam2", shape="rectangle")
# dot.node("plate0", "plate0", shape="rectangle")
# dot.node("plate1", "plate1", shape="rectangle")
# dot.node("plate2", "plate2", shape="rectangle")

# for i in range(3):
#     dot.node("block_" + str(i), "block_" + str(i), shape="rectangle")

# # dot.edges(["AB", "AL"], shape="none", constraint="false")
# dot.edge("structures", "plates", shape="none", constraint="True")
# dot.edge("structures", "beams", shape="none", constraint="True")

# for i in range(3):
#     dot.edge("beams", "block_" + str(i), shape="none", constraint="True")


# dot.edge("beams", "beam0", shape="none", constraint="True")
# dot.edge("beams", "beam1", shape="none", constraint="True")
# dot.edge("beams", "beam2", shape="none", constraint="True")
# dot.edge("plates", "plate0", shape="none", constraint="True")
# dot.edge("plates", "plate1", shape="none", constraint="True")
# dot.edge("plates", "plate2", shape="none", constraint="True")


# # Render the graph to a file
# graph_output_image_filename = "graph_output_image"
# dot.attr(dpi=str(300))
# dot.render(graph_output_image_filename, format="png", engine="dot", cleanup=True, view=False)

# # ==========================================================================
# # Open the generated image and resize it
# # ==========================================================================

# with Image.open(f"{graph_output_image_filename}.png") as img:
#     new_height = 440
#     new_width = int(new_height * img.size[0] / img.size[1])
#     img = img.resize((new_width, new_height))
#     img.save(f"{graph_output_image_filename}.png", format="PNG")

# # ==========================================================================
# # intialize the compas_view2
# # ==========================================================================
# from qtpy.QtWidgets import QApplication, QDesktopWidget

# app = QApplication([])  # Create a QApplication instance

# # Get the primary screen's geometry
# primary_screen = QDesktopWidget().screenGeometry(0)
# screen_width = primary_screen.width()
# screen_height = primary_screen.height()

# print(screen_width, screen_height)
# viewer = App(viewmode="shaded", enable_sidebar=True)  # Create a compas_view2 viewer
# viewer.window.setGeometry(0, 0, screen_width, screen_height)
# figure = viewer.plot(
#     "graph", location="bottom", min_height=500
# )  # Create an axis within the viewer to display the image

# # ==========================================================================
# # convert numpy.ndarray to matplotlib.figure.Figure
# # ==========================================================================

# image_data = mpimg.imread("graph_output_image.png")  # Load the image from "graph_output_image.png"
# fig, ax = plt.subplots()  # Create a Matplotlib figure and axis
# ax.imshow(image_data, cmap="gray", interpolation="nearest")  # Display the image on the axis
# figure.clf()  # Clear the figure
# figure.figimage(image_data, cmap="gray", interpolation="nearest")  # Display the image on the figure

# # ==========================================================================
# # run the compas_view2
# # ==========================================================================

# viewer.show()

from compas.geometry import Polyline
from compas_view2.app import App
import matplotlib.image as mpimg
from graphviz import Digraph
import os
import numpy as np
from PIL import Image

# Set the path to the Graphviz executable
graphviz_executable = r"C:\Program Files\Graphviz\bin"

# Add the Graphviz bin directory to the PATH environment variable
os.environ["PATH"] += os.pathsep + graphviz_executable

# Create a Digraph object
dot = Digraph(comment="The Round Table", format="png")


dot.node("A", "King Arthur")
dot.node("B", "Sir Bedevere the Wise")
dot.node("L", "Sir Lancelot the Brave")

dot.edges(["AB", "AL"])
dot.edge("B", "L", constraint="false")
dot.edge("B", "L", constraint="false")

# Set the output format and engine
format = "png"
engine = "dot"

# Set the DPI
dpi = 300

# Render the graph to a file
output_filename = "output"
dot.attr(dpi=str(dpi))
dot.render(output_filename, format=format, engine=engine, cleanup=True, view=False)

# Open the generated image and resize it
with Image.open(f"{output_filename}.png") as img:
    width, height = 1000, 1000  # Set your desired pixel dimensions
    img = img.resize((width, height))
    img.save(f"{output_filename}_resized.png", format="PNG")


# Load the image from "output.png"
image_data = mpimg.imread("output.png")
height, width, channels = image_data.shape
new_height = 500
new_width = int(new_height * width / height)
print(height, width, channels)


# Load the image
image_data = mpimg.imread("output_resized.png")

# Define the scaling factor
scale_factor = 2  # You can adjust this value as needed

# Rescale the image
import matplotlib.pyplot as plt


# Create a compas_view2 viewer
viewer = App(viewmode="shaded", enable_sidebar=True, width=1600, height=900)

# Create an axis within the viewer to display the image
figure = viewer.plot("My Plot", location="bottom", min_height=500)

# ==========================================================================
# convert numpy.ndarray to matplotlib.figure.Figure
# ==========================================================================


# Create a Matplotlib figure and axis
fig, ax = plt.subplots()

# Display the image on the axis
ax.imshow(image_data, cmap="gray", interpolation="nearest")

figure.clf()  # Clear the figure

figure.figimage(image_data, cmap="gray", interpolation="nearest")  # Display the image on the figure

# # axis.imshow(image, interpolation="bilinear", origin="lower")
viewer.show()

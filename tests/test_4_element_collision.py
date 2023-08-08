from math import radians
from compas.geometry import Point, Box, Translation, Rotation, Frame
from compas_assembly2 import Element, ELEMENT_NAME, Viewer, FabricationNest

# ==========================================================================
# INIT ELEMENT
# ==========================================================================
b1 = Element(
    name=ELEMENT_NAME.BLOCK,
    id=0,
    frame=Frame.worldXY,
    simplex=Point(0, 0, 0),
    complex=Box.from_width_height_depth(1, 1, 1),
)

# ==========================================================================
# TRANSFORM AND COPY ELEMENT
# ==========================================================================
T = Translation.from_vector([0, 0, 1])
R = Rotation.from_axis_and_angle([0, 0, 1], radians(45))
b2 = b1.transformed(T * R)

# ==========================================================================
# NEST ELEMENTS
# ==========================================================================
FabricationNest.pack_elements(elements=[b1, b2], nest_type=2, inflate=0.1, height_step=4)

# ==========================================================================
# CHECK COLLISION
# ==========================================================================

# ==========================================================================
# VIEWER
# ==========================================================================
Viewer.show_elements(elements=[b1, b2])

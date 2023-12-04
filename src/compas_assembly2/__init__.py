from __future__ import print_function  # noqa: F401 E402 F403
import compas  # noqa: F401 E402 F4037
import compas_assembly2  # noqa: F401 E402 F403
import os

"""

.. currentmodule:: compas_assembly2


.. toctree::
    :maxdepth: 1

Model class
===========

.. autosummary::
    :toctree: generated/
    :nosignatures:

    model.Tree
    model.Node
    model.GroupNode
    model.ElementNode
    model.Model


Element class
=============

.. autosummary::
    :toctree: generated/
    :nosignatures:

    element.Element

"""


__author__ = ["Petras Vestartas"]
__copyright__ = "Petras Vestartas"
__license__ = "MIT License"
__email__ = "petrasvestartas@gmail.com"
__version__ = "0.1.0"


HERE = os.path.dirname(__file__)

HOME = os.path.abspath(os.path.join(HERE, "../../"))
DATA = os.path.abspath(os.path.join(HOME, "data"))
DOCS = os.path.abspath(os.path.join(HOME, "docs"))
TEMP = os.path.abspath(os.path.join(HOME, "temp"))

__all_plugins__ = [
    "compas_assembly2",
]

__all__ = [
    "HOME",
    "DATA",
    "DOCS",
    "TEMP",
]

# Define the base URL for images based on the environment
if os.getenv("READTHEDOCS") == "True":
    base_url = "https://github.com/BRG-research/compas_assembly2/blob/main/docs/_images/"
else:
    base_url = ""

# Set the base URL for images in the html_context
html_context = {
    "base_url": base_url,
}


# Global variables relate to the assembly data-structure


class ELEMENT_NAME:
    BLOCK = "BLOCK"
    BLOCK_CONCAVE = "BLOCK_CONCAVE"
    BLOCK_X = "BLOCK_X"
    BEAM = "BEAM"
    BEAM_BENT = "BEAM_BENT"
    BEAM_X = "BEAM_X"
    PLATE = "PLATE"
    SHELL = "SHELL"
    SHELL_X = "SHELL_X"
    CUSTOM = "CUSTOM"

    @staticmethod
    def exists(input_string):
        input_string = input_string.upper()  # Convert input to uppercase for case-insensitive comparison
        if hasattr(ELEMENT_NAME, input_string):
            return getattr(ELEMENT_NAME, input_string)
        else:
            return "Invalid element type."


class JOINT_NAME:
    FACE_TO_FACE = "FACE_TO_FACE"
    AXIS_TO_AXIS = "AXIS_TO_AXIS"
    FRAME_TO_FACE = "FRAME_TO_FACE"
    OBJECT_MINUS_OBJECT = "OBJECT_MINUS_OBJECT"
    CUSTOM = "CUSTOM"


class FABRICATION_TYPES:
    MOVEMENT = "MOVEMENT_LINEAR"
    SUBTRACTION_DRILL = "SUBTRACTION_DRILL"
    SUBTRACTION_CUT = "SUBTRACTION_CUT"
    SUBTRACTION_MILL = "SUBTRACTION_MILL"
    SUBTRACTION_SLICE = "SUBTRACTION_SLICE"
    SUBTRACTION_SAW = "SUBTRACTION_SAW"
    ADDITION_SPRAY = "ADDITION_SPRAY"
    ADDITION_EXTRUDE = "ADDITION_EXTRUDE"
    NESTING = "NESTING"
    CUSTOM = "CUSTOM"


global_geometry = []

from element import Element  # noqa: F401 E402 F403
from algorithms import Algorithms  # noqa: F401 E402 F403
from model import Model, ElementTree, GroupNode, ElementNode  # noqa: F401 E402 F403

from viewer_model import ViewerModel  # noqa: F401 E402 F403
from viewer import Viewer  # noqa: F401 E402 F403

# from .joint import Joint  # noqa: F401 E402 F403
from block import Block  # noqa: F401 E402 F403
from beam import Beam  # noqa: F401 E402 F403

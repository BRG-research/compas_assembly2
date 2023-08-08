"""

.. currentmodule:: compas_assembly2


.. toctree::
    :maxdepth: 2

test module
===========

.. autosummary::
    :toctree: generated/
    :nosignatures:

    test.hello_compas_assembly2

Assembly class
==============

.. autosummary::
    :toctree: generated/
    :nosignatures:

    assembly.Assembly

Element class
=============

.. image:: ../_images/element.png
   :width: 75%
   :align: right
   :alt: compas_assembly2

.. image:: ../_images/element_collision.png
   :width: 75%
   :align: right
   :alt: compas_assembly2

.. image:: ../_images/element_type.png
   :width: 75%
   :align: right
   :alt: compas_assembly2

.. autosummary::
    :toctree: generated/
    :nosignatures:

    element.Element

Block class
===================

.. autosummary::
    :toctree: generated/
    :nosignatures:

    element_block.Block

Beam class
===================

.. autosummary::
    :toctree: generated/
    :nosignatures:

    element_beam.Beam

Group class
===========

.. image:: ../_images/group.png
   :width: 75%
   :align: right
   :alt: compas_assembly2

.. autosummary::
    :toctree: generated/
    :nosignatures:

    group.Group

Viewer class
============

.. image:: ../_images/log_0.gif
   :width: 75%
   :align: right
   :alt: compas_assembly2

.. autosummary::
    :toctree: generated/
    :nosignatures:

    viewer.Viewer

Fabrication class
=================

.. autosummary::
    :toctree: generated/
    :nosignatures:

    fabrication.Fabrication

FabricationNest class
=====================

.. autosummary::
    :toctree: generated/
    :nosignatures:

    fabrication_nest.FabricationNest

"""


from __future__ import print_function

import os


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
    FRAME = "FRAME"
    FRAME_BENT = "FRAME_BENT"
    FRAME_X = "FRAME_X"
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


class FABRICATION_TYPES:
    MOVEMENT = "MOVEMENT_LINEAR"
    SUBTRACTION_DRILL = "SUBTRACTION_DRILL"
    SUBTRACTION_CUT = "SUBTRACTION_CUT"
    SUBTRACTION_MILL = "SUBTRACTION_MILL"
    SUBTRACTION_SLICE = "SUBTRACTION_SLICE"
    ADDITION_PRINT = "ADDITION_PRINT"
    ADDITION_SPRAY = "ADDITION_SPRAY"
    ADDITION_EXTRUDE = "ADDITION_EXTRUDE"
    NESTING = "NESTING"
    CUSTOM = "CUSTOM"


from .element import Element  # noqa
from .viewer import Viewer  # noqa
from .fabrication import Fabrication  # noqa
from .fabrication_nest import FabricationNest  # noqa

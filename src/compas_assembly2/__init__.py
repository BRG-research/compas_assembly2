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

Element class
=============

.. image:: ../_images/element.png
   :width: 100%
   :align: right
   :alt: compas_assembly2

.. image:: ../_images/element_type.png
   :width: 100%
   :align: right
   :alt: compas_assembly2


.. autosummary::
    :toctree: generated/
    :nosignatures:

    element.Element

Group class
===========

.. autosummary::
    :toctree: generated/
    :nosignatures:

    group.Group

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

__all__ = ["HOME", "DATA", "DOCS", "TEMP"]

# Define the base URL for images based on the environment
if os.getenv("READTHEDOCS") == "True":
    base_url = "https://github.com/BRG-research/compas_assembly2/blob/main/docs/_images/"
else:
    base_url = ""

# Set the base URL for images in the html_context
html_context = {
    "base_url": base_url,
}

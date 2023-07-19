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

element module
==============

.. autosummary::
    :toctree: generated/
    :nosignatures:

    element.Element

group module
==============

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

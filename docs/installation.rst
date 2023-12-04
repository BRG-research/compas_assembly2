********************************************************************************
Installation
********************************************************************************

**Install**

.. code-block:: bash

    conda create -n assembly2 -c conda-forge compas compas_view2
    pip install -e .
    pip install -r requirements-dev.txt
    python -m compas_rhino.install
    python -m compas_rhino.install -p compas_assembly2

**Remove**

.. code-block:: bash

    conda env remove --name assembly2

.. Stable
.. ======

.. Stable releases of :mod:`compas_cgal` can be installed via ``conda-forge``.

.. .. code-block:: bash

..     conda create -n cgal -c conda-forge compas_cgal

.. Several examples use the COMPAS Viewer for visualisation.
.. To install :mod:`compas_view2` in the same environment

.. .. code-block:: bash

..     conda activate cgal
..     conda install compas_view2

.. Or everything in one go

.. .. code-block:: bash

..     conda create -n cgal -c conda-forge compas_cgal compas_view2

.. Dev Install
.. ===========

.. See :doc:`devguide`.

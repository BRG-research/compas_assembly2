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
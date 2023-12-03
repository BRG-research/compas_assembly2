********************************************************************************
compas_assembly2
********************************************************************************

The **compas_assembly2** represents:

.. .. image:: /_images/assembly.png
..    :width: 100%
..    :align: right
..    :alt: compas_assembly2

.. rst-class:: lead

   * elements:
      * structural elements such as blocks, beams, nodes, and plates.
      * an element is primary a description of a geometry (e.g. closed mesh) and simplified geometry (e.g. point, line).
      * initially elements do not have neither connectivity nor grouping information.
   * model:
      * a dictionary of elements, where the key is the element.guid
      * a tree to represent the assembly hierarchy
      * a graph to represent the connectivity of the elements


.. .. .. image:: /_images/logo.png
.. ..    :width: 20%
.. ..    :align: center
.. ..    :alt: compas_assembly2

.. .. .. raw::

.. .. image:: /_images/assembly2.png
..    :width: 100%
..    :align: right
..    :alt: compas_assembly2

.. .. rst-class:: lead

.. And the following the overview of the Assembly data-structure:

.. .. image:: /_images/assembly_code_visuals1.png
..    :width: 100%
..    :align: right
..    :alt: compas_assembly2

.. .. rst-class:: lead

.. .. image:: /_images/assembly_code_visuals2.png
..    :width: 100%
..    :align: right
..    :alt: compas_assembly2

.. .. rst-class:: lead

.. .. image:: /_images/assembly_code.png
..    :width: 100%
..    :align: right
..    :alt: compas_assembly2

.. .. rst-class:: lead

.. And the elements that are currently implemented:

.. .. image:: /_images/element_type.png
..    :width: 100%
..    :align: right
..    :alt: compas_assembly2

.. .. rst-class:: lead








.. .. figure:: /_images/
     :figclass: figure
     :class: figure-img img-fluid


Table of Contents
=================

.. toctree::
   :maxdepth: 3
   :titlesonly:

   Introduction <self>
   installation
   examples
   api


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`

.. Development Notes
.. =================
.. **20-07-2023 Juli, Donnerstag**

.. .. image:: _images/element.png
..    :width: 100%

.. .. image:: _images/element_type.png
..    :width: 100%

.. .. image:: _images/group.png
..    :width: 100%

.. **04-08-2023 August, Freitag**

.. .. image:: _images/log_0.gif
..    :width: 100%
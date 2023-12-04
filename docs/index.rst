********************************************************************************
Documentation of COMPAS ASSEMBLY2
********************************************************************************

.. rst-class:: lead

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


Table of Contents
=================

.. toctree::
   :maxdepth: 3
   :titlesonly:

   Introduction <self>
   installation
   tutorial
   examples
   api
   license
   acknowledgements


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`

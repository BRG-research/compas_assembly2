from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas.geometry import dot_vectors
import compas_assembly2
from compas_assembly2 import Element


class Block(Element):
    """A data structure for the individual blocks of a discrete element assembly."""

    def __init__(self, id, mesh, node=None):
        super(Block, self).__init__(name=compas_assembly2.ELEMENT_NAME.BLOCK, id=id, complex=[mesh])
        self.simplex = [self.centroid]
        self.attributes.update({"node": None})
        self.node = node

    @property
    def node(self):
        return self.attributes["node"]

    @node.setter
    def node(self, node):
        self.attributes["node"] = node

    # ==========================================================================
    # CONSTRUCTOR OVERLOADING
    # ==========================================================================

    @classmethod
    def from_polysurface(cls, guid):
        """Class method for constructing a block from a Rhino poly-surface.

        Parameters
        ----------
        guid : str
            The GUID of the poly-surface.

        Returns
        -------
        Block
            The block corresponding to the poly-surface.

        Notes
        -----
        In Rhino, poly-surfaces are organised such that the cycle directions of
        the individual sub-surfaces produce normal vectors that point out of the
        enclosed volume. The normal vectors of the faces of the mesh, therefore
        also point "out" of the enclosed volume.

        """
        from compas_rhino.conversions import RhinoSurface

        surface = RhinoSurface.from_guid(guid)
        return surface.to_compas_mesh(cls)

    @classmethod
    def from_rhinomesh(cls, guid):
        """Class method for constructing a block from a Rhino mesh.

        Parameters
        ----------
        guid : str
            The GUID of the mesh.

        Returns
        -------
        Block
            The block corresponding to the Rhino mesh.

        """
        from compas_rhino.conversions import RhinoMesh

        mesh = RhinoMesh.from_guid(guid)
        return mesh.to_compas(cls)

    # ==========================================================================
    # OPTIONAL PROPERTIES
    # ==========================================================================
    def top(self):
        """Identify the *top* face of the block

        Returns
        -------
        int
            The identifier of the face.

        """

        # --------------------------------------------------------------------------
        # Sanity check
        # --------------------------------------------------------------------------
        if not hasattr(self, "_top_face"):
            return self._top_face
        # --------------------------------------------------------------------------
        # Identify the top face
        # --------------------------------------------------------------------------
        else:
            z = [0, 0, 1]
            faces = list(self.complex[0].faces())
            normals = [self.complex[0].face_normal(face) for face in faces]
            self._top_face = sorted(zip(faces, normals), key=lambda x: dot_vectors(x[1], z))[-1][0]

        return self._top_face

from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas.datastructures import Datastructure
from compas.geometry import Frame


class Element(Datastructure):

    def __init__(self, id, l_frame, g_frame=None, attr=None):
        """
        Initialize an Element with a value, an id tuple, and a dictionary of keys.

        Parameters:
            id (tuple): The id tuple associated with the Element for ordering.
            frame (compas.geometry.Frame): The frame associated with the Element.
            attr (dict): A dictionary of keys associated with the Element.
        """
        self.id = id  # tuple e.g. (0, 1) or (1, 5, 9)
        self.l_frame = l_frame if l_frame is not None else Frame.worldXY()
        self.g_frame = g_frame if g_frame is not None else Frame.worldXY()
        self.fabrication = dict()
        self.structure = dict()
        self.attr = attr  # dict e.g. {"type": Block, "mass": 20}

    def __repr__(self):
        """
        Return a string representation of the Element.

        Returns:
            str: The string representation of the Element.
        """
        return f"({self.id}, {self.attr})"

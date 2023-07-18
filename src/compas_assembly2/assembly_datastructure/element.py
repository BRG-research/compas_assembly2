from compas.geometry import Frame


class Element:
    def __init__(self, id, l_frame, g_frame, attr=None):
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

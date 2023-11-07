# from compas.geometry import Point, Frame, distance_point_point
# from compas_assembly2 import Fabrication, FABRICATION_TYPES


# class FabricationNest:
#     """Fabrication Nesting class

#     currently implemented nesting methods:
#     a) pack_elements - orient objects next to each other in a linear fashion

#     all properties must be private
#     you just need to fill Fabrication dictionary in each element
#     consider this as a helper or utility class"""

#     _id = -1  # often used as a priority value for sorting which fabrication process comes first
#     _elements = None  # list of elements

#     def __init__(self, id=-1, elements=None):
#         self._elements = elements

#     @classmethod
#     def pack_elements(cls, elements=None, nest_type=1, inflate=0.1, height_step=4):
#         """pack_elements - orient objects next to each other in a linear fashion"""

#         cls._elements = elements

#         # nest cls._elements linearly and add the the nest frame to the fabrication
#         # first compute the bounding box of the cls._elements, get the horizontal length, and create frames

#         width = {}
#         height = {}

#         for e in cls._elements:  # type: ignore
#             e.aabb(inflate)
#             e.oobb(inflate)
#             e.convex_hull

#         center = Point(0, 0, 0)
#         for e in cls._elements:  # type: ignore
#             center = center + e.frame.point
#         center = center / len(cls._elements)  # type: ignore

#         for e in cls._elements:  # type: ignore
#             width[e.name] = 0

#         for index, (key, value) in enumerate(width.items()):
#             height[key] = index * height_step * 0

#         for i, e in enumerate(cls._elements):  # type: ignore
#             temp_width = 0
#             source_frame = e.frame.copy()
#             target_frame = Frame([0, 0, 0], source_frame.xaxis, source_frame.yaxis)

#             if nest_type == 1 and e.aabb() is not None:
#                 # --------------------------------------------------------------------------
#                 # aabb linear nesting
#                 # --------------------------------------------------------------------------
#                 temp_width = e.aabb()[6][0] - e.aabb()[0][0]
#                 # get the maximum height of the cls._elements
#                 height[e.name] = max(height[e.name], e.aabb()[6][1] - e.aabb()[0][1])
#                 source_frame = Frame(
#                     e.aabb()[0],
#                     [
#                         e.aabb()[1][0] - e.aabb()[0][0],
#                         e.aabb()[1][1] - e.aabb()[0][1],
#                         e.aabb()[1][2] - e.aabb()[0][2],
#                     ],
#                     [
#                         e.aabb()[3][0] - e.aabb()[0][0],
#                         e.aabb()[3][1] - e.aabb()[0][1],
#                         e.aabb()[3][2] - e.aabb()[0][2],
#                     ],
#                 )
#                 target_frame = Frame([width[e.name], height[e.name], 0], [1, 0, 0], [0, 1, 0])
#             elif nest_type == 2 and e.oobb() is not None:
#                 # --------------------------------------------------------------------------
#                 # oobb linear nesting
#                 # --------------------------------------------------------------------------
#                 temp_width = distance_point_point(e.oobb()[0], e.oobb()[1])
#                 # get the maximum height of the cls._elements
#                 height[e.name] = max(height[e.name], distance_point_point(e.oobb()[0], e.oobb()[3]))
#                 source_frame = Frame(
#                     e.oobb()[0],
#                     [
#                         e.oobb()[1][0] - e.oobb()[0][0],
#                         e.oobb()[1][1] - e.oobb()[0][1],
#                         e.oobb()[1][2] - e.oobb()[0][2],
#                     ],
#                     [
#                         e.oobb()[3][0] - e.oobb()[0][0],
#                         e.oobb()[3][1] - e.oobb()[0][1],
#                         e.oobb()[3][2] - e.oobb()[0][2],
#                     ],
#                 )
#                 target_frame = Frame([width[e.name], height[e.name], 0], [1, 0, 0], [0, 1, 0])
#             elif nest_type == 3:
#                 # --------------------------------------------------------------------------
#                 # move of center
#                 # --------------------------------------------------------------------------
#                 t = 1.25
#                 x = (1 - t) * center.x + t * source_frame.point.x
#                 y = (1 - t) * center.y + t * source_frame.point.y
#                 z = (1 - t) * center.z + t * source_frame.point.z
#                 target_frame = Frame([x, y, z], source_frame.xaxis, source_frame.yaxis)

#             # --------------------------------------------------------------------------
#             # assignment of fabrication data
#             # --------------------------------------------------------------------------
#             fabrication = Fabrication(
#                 fabrication_type=FABRICATION_TYPES.NESTING,
#                 id=cls._id,
#                 frames=[source_frame, target_frame],
#             )
#             e.fabrication[FABRICATION_TYPES.NESTING] = fabrication
#             width[e.name] = width[e.name] + temp_width

#         # --------------------------------------------------------------------------
#         # center the frames
#         # --------------------------------------------------------------------------
#         h = 0
#         for index, (key, value) in enumerate(width.items()):
#             temp_height = height[key]
#             height[key] = h
#             h = h + temp_height

#         for e in cls._elements:  # type: ignore
#             e.fabrication[FABRICATION_TYPES.NESTING].frames[1].point.x = (
#                 e.fabrication[FABRICATION_TYPES.NESTING].frames[1].point.x - width[e.name] * 0.5
#             )
#             e.fabrication[FABRICATION_TYPES.NESTING].frames[1].point.y = height[e.name] - h * 0.5

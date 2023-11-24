from compas.data import json_load
from compas.geometry import Point, Line, Vector

viewer_installed = True

try:
    from compas_view2.app import App
    from compas_view2.objects import Collection
except ImportError:
    viewer_installed = False

if __name__ == "__main__" and viewer_installed:

    #################################################################################
    # Polylines Desiarization
    #################################################################################
    polylines = json_load("src/compas_assembly2/data_sets/polylines/polylines_graphic_statics_0.json")

    #################################################################################
    # Form Diagram
    #################################################################################

    # supports
    left_point = polylines[0].point_at(0.5)
    right_point = polylines[1].point_at(0.4)

    # load points
    loads_points = polylines[2].divide(10)[1:-1]

    # load lines
    loads_lines = []
    for point in loads_points:
        loads_lines.append(Line(Point(point[0], point[1] + 10, point[2]), point))

    #################################################################################
    # Force Diagram
    #################################################################################
    arbitrary_load_start_point = Point(10, 15, 0)
    arbitrary_funicular_point = Point(20, 10, 0)

    forces = [-1.5] * len(loads_lines)  # kN
    forces[5] = -5
    print(forces)
    pass
    loads_lines_funicular = []
    cable_lines_funicular = [Line(arbitrary_funicular_point, arbitrary_load_start_point)]

    sum_forces = 0
    for idx, point in enumerate(loads_points):
        t = Vector(idx * 0.0, 0, 0)
        loads_lines_funicular.append(
            Line(
                arbitrary_load_start_point + t + Vector(0, sum_forces, 0),
                arbitrary_load_start_point + t + Vector(0, forces[idx] + sum_forces, 0),
            )
        )
        cable_lines_funicular.append(
            Line(arbitrary_funicular_point + t, arbitrary_load_start_point + t + Vector(0, forces[idx] + sum_forces, 0))
        )
        sum_forces += forces[idx]

    # perform intersection: cable_lines_funicular and loads_lines

    # get the Nmax

    # get the force string

    # get the new intersection point in the force diagram

    # create new triangle funicular

    # interesect the lines to get the cable at supports

    #################################################################################
    # Viewer
    #################################################################################
    viewer = App(show_grid=False, enable_sceneform=True, enable_propertyform=True, viewmode="lighted")

    # display geometry
    for polyline in polylines:
        viewer.add(polyline, linecolor=(0, 0, 0))  # type: ignore

    # supports
    viewer.add(left_point)  # type: ignore
    viewer.add(right_point)  # type: ignore
    viewer.add(Collection(loads_points))  # type: ignore
    viewer.add(Collection(loads_lines))  # type: ignore
    viewer.add(arbitrary_load_start_point)  # type: ignore
    viewer.add(arbitrary_funicular_point)  # type: ignore
    viewer.add(Collection(loads_lines_funicular))  # type: ignore
    viewer.add(Collection(cable_lines_funicular))  # type: ignore

    viewer.show()

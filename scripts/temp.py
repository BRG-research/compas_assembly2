from compas.datastructures import Mesh

mesh = Mesh.from_polyhedron(6)
V = mesh.number_of_vertices()
E = mesh.number_of_edges()
F = mesh.number_of_faces()
mesh.euler() == V - E + F
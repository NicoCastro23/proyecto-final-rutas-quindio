"""Referencia con SciPy: solo para verificar y medir, nunca dentro del algoritmo propio."""
import numpy
from scipy.spatial import ConvexHull

from rutas.r3.envolvente import normalizar


def vertices_scipy(puntos):
    """Vértices de la envolvente según SciPy (Qhull), normalizados para compararlos con la propia.

    Qhull trabaja en float64; las coordenadas enteras (< 2^53) se representan sin error.
    Lanza scipy.spatial.QhullError si todos los puntos están alineados o hay menos de 3.
    """
    casco = ConvexHull(numpy.array(puntos, dtype=numpy.float64))
    vertices = [(int(x), int(y)) for x, y in casco.points[casco.vertices]]
    return normalizar(vertices)

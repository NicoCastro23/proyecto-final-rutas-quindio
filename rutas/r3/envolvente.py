"""Envolvente convexa por QuickHull (divide y vencerás), con enteros y sin E/S.

Un punto es una tupla (x, y) de int de Python. Los giros se calculan solo con enteros, sin flotantes.
"""
import sys

# QuickHull es recursivo porque sigue la recurrencia del informe. Con particiones parejas la
# profundidad es O(log n), pero en el peor caso llega a O(n) y el límite por defecto de Python
# (~1 000 llamadas) cortaría la ejecución con RecursionError. 20 000 cubre los 8 791 nodos de la
# red y los 5 000 puntos de la parábola de las pruebas.
sys.setrecursionlimit(max(sys.getrecursionlimit(), 20_000))


def cruz(o, a, b):
    """(a.x - o.x)(b.y - o.y) - (a.y - o.y)(b.x - o.x), con enteros.

    > 0: b está a la izquierda de o->a (giro antihorario); 0: alineados; < 0: a la derecha.
    """
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def envolvente(puntos):
    raise NotImplementedError


def _lado(puntos, a, b):
    raise NotImplementedError


def _doble_area_con_signo(vertices):
    """Fórmula del zapato con enteros: positiva si los vértices van en sentido antihorario."""
    total = 0
    for i, (x1, y1) in enumerate(vertices):
        x2, y2 = vertices[(i + 1) % len(vertices)]      # el último vértice se une con el primero
        total += x1 * y2 - x2 * y1
    return total


def area(vertices):
    """Área del polígono. El doble del área es un entero exacto; se divide entre 2 solo al final."""
    if len(vertices) < 3:
        return 0
    return abs(_doble_area_con_signo(vertices)) / 2


def normalizar(vertices):
    """Mismo polígono en sentido antihorario y empezando por el vértice de menor (y, x).

    Sirve para comparar la salida propia con la de SciPy, que puede empezar en otro vértice.
    """
    vertices = list(vertices)
    if _doble_area_con_signo(vertices) < 0:             # horario: se invierte el recorrido
        vertices.reverse()
    inicio = min(range(len(vertices)), key=lambda i: (vertices[i][1], vertices[i][0]), default=0)
    return vertices[inicio:] + vertices[:inicio]

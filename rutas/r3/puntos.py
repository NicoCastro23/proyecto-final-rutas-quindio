"""Preparación de puntos para la envolvente (fuera del cronómetro)."""
import math
import random

SEMILLA = 2026
LADO = 10**6                    # el cuadrado es [0, 10^6) x [0, 10^6), en metros


def redondear(x):
    """Entero más cercano; los empates .5 van hacia +infinito (2.5 -> 3, -0.5 -> 0, -2.5 -> -2)."""
    return math.floor(x + 0.5)


def preparar_puntos(xs, ys):
    """Redondea cada coordenada, quita los repetidos y devuelve los puntos ordenados.

    Ordenar no es parte del algoritmo: solo hace determinista la entrada. zip(strict=True) lanza
    ValueError si xs y ys tienen largos distintos.
    """
    puntos = {(redondear(x), redondear(y)) for x, y in zip(xs, ys, strict=True)}
    return sorted(puntos)


def puntos_de_grafo(G):
    raise NotImplementedError


def puntos_cuadrado(n, semilla=SEMILLA, lado=LADO):
    """n puntos enteros al azar en [0, lado) x [0, lado), sin repetidos y ordenados.

    Cada llamada crea su propio random.Random(semilla), así el conjunto se reproduce solo. Al quitar
    repetidos pueden quedar menos de n.
    """
    azar = random.Random(semilla)
    puntos = {(azar.randrange(lado), azar.randrange(lado)) for _ in range(n)}
    return sorted(puntos)

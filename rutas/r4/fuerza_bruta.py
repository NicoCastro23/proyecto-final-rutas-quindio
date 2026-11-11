"""Fuerza bruta para el TSP asimétrico: prueba las k! permutaciones, sin poda."""
import math

from rutas.r4.permutaciones import permutaciones_lexicograficas
from rutas.r4.recorrido import validar_entrada


def fuerza_bruta(T, s, lugares):
    """Devuelve (tiempo_total_s, recorrido) con recorrido = [s, p1, ..., pk, s].

    La partida s queda fija y se prueban las k! órdenes de `lugares`. El costo de cada
    orden se suma completo (sin poda ni sumas incrementales) para que siga siendo fuerza
    bruta pura: Θ(k · k!). Solo se reemplaza al mejor con `<` estricto, así que en un
    empate gana la primera permutación en orden lexicográfico.
    """
    validar_entrada(T, s, lugares)
    if len(lugares) == 0:
        return 0.0, [s]

    mejor_costo = math.inf
    mejor_orden = None
    for orden in permutaciones_lexicograficas(lugares):
        costo = T[s][orden[0]]                      # salida de la partida
        for t in range(len(orden) - 1):
            costo += T[orden[t]][orden[t + 1]]      # tramos entre lugares
        costo += T[orden[-1]][s]                    # regreso a la partida
        if costo < mejor_costo:
            mejor_costo = costo
            mejor_orden = orden

    if mejor_orden is None:                         # todos los recorridos cuestan inf
        raise ValueError("no hay recorrido finito")
    return float(mejor_costo), [s, *mejor_orden, s]

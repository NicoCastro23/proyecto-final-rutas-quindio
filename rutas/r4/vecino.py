"""Heurística voraz del vecino más cercano para el TSP asimétrico."""
import math

from rutas.r4.recorrido import validar_entrada


def vecino_mas_cercano(T, s, lugares):
    """Devuelve (tiempo_total_s, recorrido) con recorrido = [s, p1, ..., pk, s].

    Desde la partida va, en cada paso, al lugar no visitado con menor T[actual][j]; en un
    empate gana el menor índice de T. Al final regresa a s. Solo lee la fila del lugar
    actual, así que no necesita que la matriz sea simétrica. Cuesta O(k²). Es voraz: decide
    sin mirar lo que falta ni el regreso, por eso puede quedar lejos del óptimo.
    """
    validar_entrada(T, s, lugares)
    if len(lugares) == 0:
        return 0.0, [s]

    orden = sorted(lugares)             # recorrer en orden de índice hace que `<` desempate bien
    visitado = [False] * len(orden)     # visitado[p] corresponde a orden[p]
    recorrido = [s]
    total = 0.0
    actual = s

    for _ in range(len(orden)):
        mejor_pos = None
        mejor_tiempo = math.inf
        for pos, lugar in enumerate(orden):
            # `<` estricto: un empate conserva el candidato de menor índice
            if not visitado[pos] and T[actual][lugar] < mejor_tiempo:
                mejor_pos = pos
                mejor_tiempo = T[actual][lugar]
        if mejor_pos is None:           # solo quedan arcos inf desde el lugar actual
            raise ValueError("no hay recorrido finito")
        visitado[mejor_pos] = True
        actual = orden[mejor_pos]
        recorrido.append(actual)
        total += mejor_tiempo

    total += T[actual][s]               # regreso a la partida
    recorrido.append(s)
    if total == math.inf:
        raise ValueError("no hay recorrido finito")
    return float(total), recorrido

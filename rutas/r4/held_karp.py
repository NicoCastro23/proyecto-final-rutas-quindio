"""Held-Karp (programación dinámica sobre subconjuntos) para el TSP asimétrico."""
import math

from rutas.r4.recorrido import validar_entrada


def tabla_held_karp(T, s, lugares, contador=None):
    """Devuelve (costo, padre): listas de 2^k listas de k elementos.

    Se trabaja con L = sorted(lugares), reindexados 0..k-1, y un subconjunto S de lugares
    se guarda como máscara de bits (bit j encendido = el lugar L[j] está en S).
      costo[mascara][j] = menor tiempo de un camino que sale de s, visita exactamente los
                          lugares de la máscara y termina en L[j] (j debe estar en la máscara).
      padre[mascara][j] = índice local i del lugar visitado justo antes de L[j] en ese
                          camino (None si L[j] es el primero).
    Recurrencia:
      base:  C({j}, j) = T[s][L[j]]
      paso:  C(S, j)   = min sobre i en S sin j de C(S sin j, i) + T[L[i]][L[j]]
    Las celdas que no se usan quedan en inf / None.

    contador: None (lo normal) o una lista [n]. Si se da, n suma las transiciones calculadas:
    k por la base y, una vez por máscara, |S| * (|S| - 1) por el paso.
    """
    L = sorted(lugares)
    k = len(L)
    costo = [[math.inf] * k for _ in range(1 << k)]
    padre = [[None] * k for _ in range(1 << k)]

    # Caso base: ir directo desde la partida hasta un solo lugar.
    for j in range(k):
        costo[1 << j][j] = T[s][L[j]]
    if contador is not None:
        contador[0] += k

    # Las máscaras se recorren en orden creciente: S sin j es un número menor que S,
    # así que su fila ya está calculada cuando se necesita.
    for mascara in range(1, 1 << k):
        bits = [j for j in range(k) if (mascara >> j) & 1]
        if len(bits) < 2:
            continue                                  # las de un solo lugar son la base
        if contador is not None:                      # una vez por máscara, fuera del ciclo interno
            contador[0] += len(bits) * (len(bits) - 1)
        for j in bits:
            previa = mascara ^ (1 << j)               # S sin j
            mejor = math.inf
            mejor_i = None
            for i in bits:                            # i en orden creciente
                if i == j:
                    continue
                candidato = costo[previa][i] + T[L[i]][L[j]]
                if candidato < mejor:                 # `<` estricto: en empate gana el menor i
                    mejor = candidato
                    mejor_i = i
            costo[mascara][j] = mejor
            padre[mascara][j] = mejor_i
    return costo, padre


def held_karp(T, s, lugares, contador=None):
    """Devuelve (tiempo_total_s, recorrido) con recorrido = [s, p1, ..., pk, s].

    Llena la tabla con tabla_held_karp, cierra el ciclo volviendo a s y reconstruye el
    recorrido hacia atrás con `padre`. Θ(k² · 2^k) en tiempo y Θ(k · 2^k) en memoria.
    """
    validar_entrada(T, s, lugares)
    if len(lugares) == 0:
        return 0.0, [s]

    L = sorted(lugares)
    k = len(L)
    completa = (1 << k) - 1                           # todos los lugares visitados
    costo, padre = tabla_held_karp(T, s, lugares, contador)

    # Cierre: el último lugar j se escoge para minimizar (llegar a j) + (volver a s).
    optimo = math.inf
    ultimo = None
    for j in range(k):
        total = costo[completa][j] + T[L[j]][s]
        if total < optimo:                            # `<` estricto: en empate gana el menor j
            optimo = total
            ultimo = j
    if contador is not None:
        contador[0] += k                              # el cierre lee T[L[j]][s] k veces
    if optimo == math.inf:
        raise ValueError("no hay recorrido finito")

    # Reconstrucción: desde el último lugar se retrocede con `padre`, quitando cada lugar de
    # la máscara, hasta llegar al primero (cuyo padre es None). Sale en orden inverso.
    orden = []
    mascara, j = completa, ultimo
    while j is not None:
        orden.append(L[j])
        mascara, j = mascara ^ (1 << j), padre[mascara][j]
    orden.reverse()
    return float(optimo), [s, *orden, s]

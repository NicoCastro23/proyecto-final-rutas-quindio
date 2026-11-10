"""Representación indexada de la red para Dijkstra (preparación de datos, fuera del cronómetro)."""
import math
from typing import NamedTuple


class Red(NamedTuple):
    ids: list          # ids de nodo ordenados de menor a mayor; el índice i es el nodo ids[i]
    indice: dict       # id -> i
    adyacencia: list   # adyacencia[i] = lista de (j, tiempo) con todas las aristas que salen de i


def construir_adyacencia(G, peso="travel_time") -> Red:
    """Renumera los nodos 0..V-1 en el orden de sus ids y arma la lista de adyacencia.

    Se conservan todas las aristas (paralelas y autolazos); Dijkstra se queda con la mejor.
    Como los índices siguen el orden de los ids, desempatar por menor índice es desempatar
    por menor id. O(V log V + E).
    """
    ids = sorted(G.nodes)
    indice = {id_nodo: i for i, id_nodo in enumerate(ids)}
    adyacencia = [[] for _ in ids]
    for u, v, key, datos in G.edges(keys=True, data=True):
        tiempo = float(datos[peso])
        # Dijkstra necesita pesos finitos y no negativos (el invariante no vale con negativos)
        if math.isnan(tiempo) or math.isinf(tiempo) or tiempo < 0:
            raise ValueError(f"arista ({u}, {v}, {key}) con {peso}={tiempo}: "
                             "el peso debe ser finito y no negativo")
        adyacencia[indice[u]].append((indice[v], tiempo))
    return Red(ids, indice, adyacencia)

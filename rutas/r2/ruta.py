"""Detalle de una ruta (tiempo y distancia totales) sobre el grafo original."""
from rutas.r1.aristas import mejor_arista


def detalle_ruta(G, ruta):
    """Devuelve (tiempo_s, distancia_m) de una ruta dada como lista de ids de nodo.

    En cada tramo se usa la misma arista que eligió Dijkstra (la paralela de menor
    travel_time, vía mejor_arista), así el tiempo y la distancia salen de una sola arista.
    Una ruta de un nodo cuesta (0, 0); una ruta vacía no tiene sentido y da ValueError.
    """
    if not ruta:
        raise ValueError("la ruta está vacía")
    tiempo = 0
    distancia = 0
    for u, v in zip(ruta, ruta[1:]):
        arista = mejor_arista(G, u, v)
        tiempo += arista.travel_time
        distancia += arista.length
    return tiempo, distancia

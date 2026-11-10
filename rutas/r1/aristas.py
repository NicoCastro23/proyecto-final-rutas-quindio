"""Elección de la arista entre paralelas."""
from dataclasses import dataclass

from shapely.geometry import LineString


@dataclass(frozen=True)
class AristaElegida:
    u: int
    v: int
    key: int
    length: float
    travel_time: float
    geometry: LineString


def mejor_arista(G, u, v):
    """Entre las aristas paralelas u -> v, la de menor travel_time (empate: menor key).

    Devuelve length, travel_time y geometry de ESA misma arista, para que el tiempo, la
    distancia y el dibujo de una ruta (R2 y R5) siempre coincidan. Si la arista no trae
    geometry se usa el segmento recto entre u y v (en lon/lat, como OSMnx).
    Costo: O(k), con k = número de paralelas.
    """
    if u not in G or v not in G[u]:
        raise KeyError(f"no hay arista de {u} a {v}")

    # Comparar (tiempo, key): la tupla desempata sola por la menor clave.
    key, datos = min(G[u][v].items(), key=lambda par: (par[1]["travel_time"], par[0]))

    geometria = datos.get("geometry")
    if geometria is None:
        geometria = LineString([(G.nodes[u]["x"], G.nodes[u]["y"]),
                                (G.nodes[v]["x"], G.nodes[v]["y"])])
    return AristaElegida(u, v, key, datos["length"], datos["travel_time"], geometria)

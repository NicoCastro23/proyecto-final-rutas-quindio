"""Asociación lugar -> nodo más cercano, con búsqueda lineal propia (sin KD-tree)."""
import math

import pandas as pd

from rutas.config import UMBRAL_ALERTA_M
from rutas.r1.utm import a_utm


def nodo_mas_cercano(x, y, nodos):
    """Nodo más cercano a (x, y). nodos = lista de (id_nodo, x, y), todo en metros UTM.

    Recorre los V nodos una vez (O(V)) guardando el mejor visto. Gana la menor distancia;
    si hay empate exacto, el menor id_nodo, así el resultado no depende del orden de la lista.
    Devuelve (id_nodo, distancia_en_metros).
    """
    mejor_id, mejor_distancia = None, math.inf
    for id_nodo, nx_, ny_ in nodos:
        distancia = math.hypot(nx_ - x, ny_ - y)
        if distancia < mejor_distancia or (distancia == mejor_distancia and id_nodo < mejor_id):
            mejor_id, mejor_distancia = id_nodo, distancia
    return mejor_id, mejor_distancia


def ubicar_lugares(catalogo, G):
    """Asocia cada lugar del catálogo al nodo más cercano de G (que ya tiene x_utm, y_utm).

    Costo O(P * V). Los lugares a más de 500 m se marcan con alerta_500m pero se conservan.
    Las filas salen en el mismo orden del catálogo.
    """
    nodos = [(n, d["x_utm"], d["y_utm"]) for n, d in G.nodes(data=True)]
    xs, ys = a_utm(catalogo["longitud"], catalogo["latitud"])

    filas = []
    for id_lugar, x, y in zip(catalogo["id"], xs, ys):
        id_nodo, distancia = nodo_mas_cercano(float(x), float(y), nodos)
        filas.append({
            "id_lugar": id_lugar,
            "id_nodo": id_nodo,
            "distancia_al_nodo_m": distancia,
            "alerta_500m": distancia > UMBRAL_ALERTA_M,  # estricto: 500 exactos no alerta
        })
    return pd.DataFrame(filas, columns=["id_lugar", "id_nodo", "distancia_al_nodo_m", "alerta_500m"])

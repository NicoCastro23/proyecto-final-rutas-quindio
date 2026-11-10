"""Conversión entre lon/lat (EPSG:4326) y UTM zona 18N (EPSG:32618).

UTM da coordenadas en metros, así la distancia euclidiana es una distancia real
(con lon/lat habría que convertir grados). Se usa pyproj con always_xy=True: el orden
siempre es (lon, lat) y (x, y), nunca (lat, lon).
"""
import numpy as np
from pyproj import Transformer

from rutas.config import EPSG_UTM


def transformador(inverso=False):
    """Transformador EPSG:4326 -> EPSG:32618 (o el contrario si inverso=True)."""
    origen, destino = "EPSG:4326", f"EPSG:{EPSG_UTM}"
    if inverso:
        origen, destino = destino, origen
    return Transformer.from_crs(origen, destino, always_xy=True)


def a_utm(lons, lats):
    """(lons, lats) en grados -> (x, y) en metros UTM 18N."""
    x, y = transformador().transform(np.asarray(lons, dtype=float), np.asarray(lats, dtype=float))
    return np.asarray(x), np.asarray(y)


def a_latlon(xs, ys):
    """(x, y) en metros UTM 18N -> (lons, lats) en grados."""
    lons, lats = transformador(inverso=True).transform(
        np.asarray(xs, dtype=float), np.asarray(ys, dtype=float))
    return np.asarray(lons), np.asarray(lats)


def agregar_utm_a_nodos(G):
    """Guarda x_utm, y_utm (float, sin redondear) en cada nodo. Devuelve el mismo G."""
    ids = list(G.nodes)
    lons = [G.nodes[n]["x"] for n in ids]
    lats = [G.nodes[n]["y"] for n in ids]
    xs, ys = a_utm(lons, lats)
    for id_nodo, x, y in zip(ids, xs, ys):
        G.nodes[id_nodo]["x_utm"] = float(x)
        G.nodes[id_nodo]["y_utm"] = float(y)
    return G

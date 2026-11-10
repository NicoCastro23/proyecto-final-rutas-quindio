"""Pesos de las aristas: velocidad (km/h) y tiempo de viaje (s).

travel_time = length / (speed_kph / 3.6)   (length en m, speed_kph en km/h, tiempo en s)
Los pesos no se redondean.
"""
import math

import numpy as np
import osmnx as ox
import pandas as pd
from osmnx import routing as _routing_osmnx

# Tabla del grupo (km/h). Por debajo de los máximos del Código Nacional de Tránsito
# (arts. 106 y 107) por ser zona montañosa. Cada *_link toma la velocidad de su tipo padre.
VELOCIDADES = {
    "motorway": 80, "motorway_link": 80, "trunk": 80, "trunk_link": 80,
    "primary": 60, "primary_link": 60,
    "secondary": 50, "secondary_link": 50,
    "tertiary": 40, "tertiary_link": 40,
    "unclassified": 30, "residential": 30, "road": 30,
    "living_street": 20, "service": 20, "track": 20,
    # Etiqueta rara en una red "drive" (en OSM es una escalera): la más lenta de la tabla.
    "ladder": 20,
}


def maxspeed_original(valor):
    """True si OSMnx 2.1.1 obtendría una velocidad numérica de este maxspeed.

    Usa las mismas funciones (privadas) que add_edge_speeds para que la marca coincida
    exactamente con lo que hace OSMnx: una lista se promedia; "none", "signals" y otros
    textos no numéricos dan None; mph se convierte a km/h.
    """
    colapsado = _routing_osmnx._collapse_multiple_maxspeed_values(valor, agg=np.mean)
    velocidad = _routing_osmnx._clean_maxspeed(str(colapsado))
    return velocidad is not None and not math.isnan(velocidad)


def verificar_velocidades(G):
    """Error si alguna arista no tiene velocidad finita > 0 o tiempo finito."""
    for u, v, key, datos in G.edges(keys=True, data=True):
        velocidad = datos.get("speed_kph")
        tiempo = datos.get("travel_time")
        if velocidad is None or not math.isfinite(velocidad) or velocidad <= 0:
            raise ValueError(f"arista ({u}, {v}, {key}): speed_kph inválida: {velocidad}")
        if tiempo is None or not math.isfinite(tiempo):
            raise ValueError(f"arista ({u}, {v}, {key}): travel_time inválido: {tiempo}")


def agregar_pesos(G):
    """Agrega maxspeed_original, speed_kph y travel_time a todas las aristas. Devuelve G."""
    # La marca se calcula ANTES de imputar, mientras maxspeed sigue siendo el de OSM.
    for _, _, datos in G.edges(data=True):
        datos["maxspeed_original"] = maxspeed_original(datos.get("maxspeed"))
    ox.add_edge_speeds(G, hwy_speeds=VELOCIDADES)
    ox.add_edge_travel_times(G)
    verificar_velocidades(G)
    return G


def _primer_tipo(highway):
    """Si highway es lista se usa el primer elemento, igual que OSMnx."""
    return highway[0] if isinstance(highway, list) else highway


def resumen_velocidades(G):
    """Tabla por tipo de vía: cuántas aristas traen maxspeed de OSM y cuántas se imputaron.

    Columnas: highway, velocidad_tabla_kmh, aristas, con_maxspeed_osm, pct_osm,
    pct_imputado. Última fila: Total.
    Requiere haber corrido agregar_pesos (usa la marca maxspeed_original).
    """
    conteos = {}  # tipo -> [aristas, con_maxspeed_osm]
    for _, _, datos in G.edges(data=True):
        tipo = _primer_tipo(datos.get("highway"))
        total_y_osm = conteos.setdefault(tipo, [0, 0])
        total_y_osm[0] += 1
        total_y_osm[1] += 1 if datos["maxspeed_original"] else 0

    filas = []
    for tipo in sorted(conteos, key=str):
        filas.append(_fila_resumen(tipo, *conteos[tipo], VELOCIDADES.get(tipo)))
    total = sum(c[0] for c in conteos.values())
    con_osm = sum(c[1] for c in conteos.values())
    filas.append(_fila_resumen("Total", total, con_osm, None))
    return pd.DataFrame(filas)


def _fila_resumen(tipo, aristas, con_osm, velocidad_tabla):
    # velocidad_tabla es None en la fila Total (y en un tipo fuera de la tabla): queda vacía.
    pct_osm = 100.0 * con_osm / aristas if aristas else 0.0
    return {"highway": tipo, "velocidad_tabla_kmh": velocidad_tabla, "aristas": aristas, "con_maxspeed_osm": con_osm,
            "pct_osm": pct_osm, "pct_imputado": 100.0 - pct_osm if aristas else 0.0}

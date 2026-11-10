"""Pruebas de rutas/r1/pesos.py (casos 2, 3, 4, 4b y bordes de pesos)."""
import math

import pandas as pd
import pytest

from rutas.r1.pesos import (VELOCIDADES, agregar_pesos, maxspeed_original,
                            resumen_velocidades, verificar_velocidades)
from tests.conftest import grafo_sintetico

NODOS = {1: (-75.67, 4.53), 2: (-75.66, 4.54)}


def una_arista(**atributos):
    """Grafo de una sola arista 1 -> 2 con los atributos dados."""
    return grafo_sintetico(NODOS, [(1, 2, atributos)])


def datos_arista(G):
    return G.edges[1, 2, 0]


def test_caso_2_maxspeed_36_da_100s():
    G = agregar_pesos(una_arista(length=1000.0, highway="residential", maxspeed="36"))
    assert datos_arista(G)["speed_kph"] == 36.0
    assert datos_arista(G)["travel_time"] == pytest.approx(100.0)


def test_caso_3_maxspeed_30mph():
    G = agregar_pesos(una_arista(length=500.0, highway="residential", maxspeed="30 mph"))
    assert datos_arista(G)["speed_kph"] == pytest.approx(48.2802)
    assert datos_arista(G)["travel_time"] == pytest.approx(37.28, abs=0.1)


@pytest.mark.parametrize("tipo, segundos", [
    ("residential", 120.0), ("primary", 60.0), ("primary_link", 60.0), ("track", 180.0)])
def test_caso_4_tabla_por_tipo(tipo, segundos):
    G = agregar_pesos(una_arista(length=1000.0, highway=tipo))
    assert datos_arista(G)["travel_time"] == pytest.approx(segundos)


def test_caso_4b_maxspeed_lista_y_none():
    G = agregar_pesos(una_arista(length=1000.0, highway="residential", maxspeed=["30", "50"]))
    assert datos_arista(G)["speed_kph"] == pytest.approx(40.0)
    assert datos_arista(G)["travel_time"] == pytest.approx(90.0)
    G = agregar_pesos(una_arista(length=1000.0, highway="tertiary", maxspeed="none"))
    assert datos_arista(G)["travel_time"] == pytest.approx(90.0)


def test_tabla_velocidades_completa():
    # La tabla de la spec tiene 17 tipos (16 más 'ladder', agregado tras la corrida real).
    assert len(VELOCIDADES) == 17
    assert VELOCIDADES["ladder"] == 20
    for padre in ("motorway", "trunk", "primary", "secondary", "tertiary"):
        assert VELOCIDADES[padre + "_link"] == VELOCIDADES[padre]
    assert VELOCIDADES["road"] == 30
    assert VELOCIDADES["motorway"] == 80 and VELOCIDADES["trunk"] == 80
    assert VELOCIDADES["primary"] == 60 and VELOCIDADES["secondary"] == 50
    assert VELOCIDADES["tertiary"] == 40
    assert VELOCIDADES["unclassified"] == VELOCIDADES["residential"] == 30
    assert VELOCIDADES["living_street"] == VELOCIDADES["service"] == VELOCIDADES["track"] == 20


def test_highway_lista_usa_primero():
    G = agregar_pesos(una_arista(length=1000.0, highway=["residential", "tertiary"]))
    assert datos_arista(G)["speed_kph"] == 30.0


def test_longitud_cero_tiempo_cero():
    G = agregar_pesos(una_arista(length=0.0, highway="residential"))
    assert datos_arista(G)["travel_time"] == 0.0


def test_tipo_fuera_de_tabla_se_imputa():
    # 'pedestrian' no está en la tabla y no tiene maxspeed: OSMnx usa el promedio general.
    G = grafo_sintetico(NODOS, [
        (1, 2, 0, {"length": 100.0, "highway": "pedestrian"}),
        (2, 1, 0, {"length": 100.0, "highway": "primary"}),
    ])
    agregar_pesos(G)
    velocidad = G.edges[1, 2, 0]["speed_kph"]
    assert math.isfinite(velocidad) and velocidad > 0


def test_velocidad_invalida_lanza_error():
    G = una_arista(length=100.0, highway="residential", speed_kph=0.0, travel_time=float("inf"))
    with pytest.raises(ValueError):
        verificar_velocidades(G)
    G = una_arista(length=100.0, highway="residential", speed_kph=float("nan"), travel_time=1.0)
    with pytest.raises(ValueError):
        verificar_velocidades(G)


def test_maxspeed_original():
    assert maxspeed_original("36") is True
    assert maxspeed_original(["30", "50"]) is True
    assert maxspeed_original("30 mph") is True
    assert maxspeed_original("none") is False
    assert maxspeed_original("signals") is False
    assert maxspeed_original(None) is False
    assert maxspeed_original(float("nan")) is False


def test_marca_maxspeed_original_en_aristas():
    G = grafo_sintetico(NODOS, [
        (1, 2, 0, {"length": 100.0, "highway": "residential", "maxspeed": "36"}),
        (2, 1, 0, {"length": 100.0, "highway": "residential"}),
    ])
    agregar_pesos(G)
    assert G.edges[1, 2, 0]["maxspeed_original"] is True
    assert G.edges[2, 1, 0]["maxspeed_original"] is False


def test_travel_time_formula_1e9():
    G = grafo_sintetico(NODOS, [
        (1, 2, 0, {"length": 123.456, "highway": "tertiary"}),
        (2, 1, 0, {"length": 987.654, "highway": "primary", "maxspeed": "45"}),
    ])
    agregar_pesos(G)
    for _, _, d in G.edges(data=True):
        assert d["travel_time"] == pytest.approx(d["length"] / (d["speed_kph"] / 3.6), abs=1e-9)


def test_resumen_velocidades():
    # 2 residential (una con maxspeed de OSM) y 1 primary sin maxspeed.
    G = grafo_sintetico(NODOS, [
        (1, 2, 0, {"length": 100.0, "highway": "residential", "maxspeed": "36"}),
        (1, 2, 1, {"length": 100.0, "highway": "residential"}),
        (2, 1, 0, {"length": 100.0, "highway": "primary"}),
    ])
    agregar_pesos(G)
    resumen = resumen_velocidades(G)
    assert list(resumen.columns) == [
        "highway", "velocidad_tabla_kmh", "aristas", "con_maxspeed_osm", "pct_osm",
        "pct_imputado"]
    fila = resumen.set_index("highway")
    assert fila.loc["residential", "velocidad_tabla_kmh"] == 30
    assert fila.loc["primary", "velocidad_tabla_kmh"] == 60
    assert pd.isna(fila.loc["Total", "velocidad_tabla_kmh"])
    assert fila.loc["residential", "aristas"] == 2
    assert fila.loc["residential", "con_maxspeed_osm"] == 1
    assert fila.loc["residential", "pct_osm"] == pytest.approx(50.0)
    assert fila.loc["residential", "pct_imputado"] == pytest.approx(50.0)
    assert fila.loc["primary", "pct_osm"] == pytest.approx(0.0)
    assert fila.loc["primary", "pct_imputado"] == pytest.approx(100.0)
    assert resumen.iloc[-1]["highway"] == "Total"
    assert fila.loc["Total", "aristas"] == 3
    assert fila.loc["Total", "pct_osm"] == pytest.approx(100 / 3)
    assert fila.loc["Total", "pct_imputado"] == pytest.approx(200 / 3)


def test_resumen_highway_lista_usa_primero():
    G = grafo_sintetico(NODOS, [
        (1, 2, 0, {"length": 100.0, "highway": ["tertiary", "residential"]}),
        (2, 1, 0, {"length": 100.0, "highway": "tertiary"}),
    ])
    agregar_pesos(G)
    fila = resumen_velocidades(G).set_index("highway")
    assert fila.loc["tertiary", "aristas"] == 2
    assert "residential" not in fila.index


def test_caso_4d_ladder_20_kmh():
    G = agregar_pesos(una_arista(length=1000.0, highway="ladder"))
    assert datos_arista(G)["speed_kph"] == pytest.approx(20.0)
    assert datos_arista(G)["travel_time"] == pytest.approx(180.0)
    # Con lista, OSMnx usa el primer elemento: residential (30 km/h).
    G = agregar_pesos(una_arista(length=1000.0, highway=["residential", "ladder"]))
    assert datos_arista(G)["speed_kph"] == pytest.approx(30.0)
    assert datos_arista(G)["travel_time"] == pytest.approx(120.0)


def test_resumen_ladder_en_tabla():
    G = grafo_sintetico(NODOS, [
        (1, 2, 0, {"length": 100.0, "highway": "ladder"}),
        (2, 1, 0, {"length": 100.0, "highway": "residential"}),
    ])
    agregar_pesos(G)
    assert resumen_velocidades(G).set_index("highway").loc["ladder", "velocidad_tabla_kmh"] == 20

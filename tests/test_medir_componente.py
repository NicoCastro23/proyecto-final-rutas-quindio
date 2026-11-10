"""Pruebas de rutas/r1/medir_componente.py con redes sintéticas (sin red real)."""
import json

import osmnx as ox
import pandas as pd
import pytest

import rutas.medicion
from rutas.config import ARCHIVOS_CRUDOS
from rutas.medicion import ResultadoMedicion
from rutas.r1 import medir_componente
from tests.conftest import grafo_sintetico

COLUMNAS = ["red", "V", "E", "V_mas_E", "tiempo_ms", "tiempo_por_elemento_us", "repeticiones",
            "ya_fuertemente_conexa"]
NOMBRES = ["Radio de 2 km", "Radio de 5 km", "Radio de 10 km", "Radio de 20 km",
           "Departamento completo"]


def red_pequena():
    nodos = {1: (-75.67, 4.53), 2: (-75.66, 4.54), 3: (-75.65, 4.53), 4: (-75.60, 4.50)}
    return grafo_sintetico(nodos, [(1, 2, {"length": 1.0}), (2, 3, {"length": 1.0}),
                                   (3, 1, {"length": 1.0}), (3, 4, {"length": 1.0})])


def test_fila_tiempos_calcula_us_por_elemento():
    resultado = ResultadoMedicion(tiempo_ms=12.0, repeticiones=5, completada=True,
                                  tiempos_ms=[12.0] * 5)
    fila = medir_componente.fila_tiempos("Radio de 2 km", 100, 300, resultado, True)
    assert list(fila) == COLUMNAS
    assert fila["V_mas_E"] == 400
    assert fila["tiempo_por_elemento_us"] == pytest.approx(12.0 * 1000 / 400)
    assert fila["tiempo_ms"] == 12.0 and fila["repeticiones"] == 5
    assert fila["ya_fuertemente_conexa"] is True


def test_fila_no_completada():
    resultado = ResultadoMedicion(tiempo_ms=None, repeticiones=0, completada=False)
    fila = medir_componente.fila_tiempos("Departamento completo", 10, 20, resultado, False)
    assert fila["tiempo_ms"] == "no completada"
    assert fila["repeticiones"] == 0
    assert fila["tiempo_por_elemento_us"] == ""
    assert fila["ya_fuertemente_conexa"] is False


def test_preparar_copia_da_grafo_nuevo():
    G = red_pequena()
    preparar = medir_componente.preparar_copia(G)
    (primera,), (segunda,) = preparar(), preparar()
    assert primera is not segunda and primera is not G
    assert set(primera.nodes) == set(G.nodes) and set(primera.edges) == set(G.edges)
    primera.remove_node(1)
    assert 1 in G and 1 in segunda


@pytest.fixture
def carpeta_raw(tmp_path):
    raw = tmp_path / "raw"
    raw.mkdir()
    for nombre in NOMBRES:
        ox.save_graphml(red_pequena(), raw / ARCHIVOS_CRUDOS[nombre])
    return raw


def test_main_con_redes_sinteticas(carpeta_raw, tmp_path):
    salida = tmp_path / "results"
    medir_componente.main(raw=carpeta_raw, salida=salida)
    tabla = pd.read_csv(salida / "r1_tiempos_componente.csv")
    assert list(tabla.columns) == COLUMNAS
    assert list(tabla["red"]) == NOMBRES
    assert (tabla["repeticiones"] == 5).all()
    assert (tabla["V"] == 4).all() and (tabla["E"] == 4).all() and (tabla["V_mas_E"] == 8).all()
    # red_pequena tiene el nodo 4 que solo recibe una arista: no es fuertemente conexa
    assert (tabla["ya_fuertemente_conexa"] == False).all()  # noqa: E712
    assert (salida / "maquina.json").exists()
    assert set(json.loads((salida / "maquina.json").read_text())) == {
        "procesador", "ram_gb", "so", "python"}


def test_main_usa_modo_mismo_proceso(carpeta_raw, tmp_path, monkeypatch):
    def prohibido(*args, **kwargs):
        raise AssertionError("R1 se mide en el mismo proceso, no en un hijo")
    monkeypatch.setattr(rutas.medicion, "medir_en_hijo", prohibido)
    monkeypatch.setattr(medir_componente, "medir_en_hijo", prohibido, raising=False)
    medir_componente.main(raw=carpeta_raw, salida=tmp_path / "results")


def test_main_marca_red_ya_fuertemente_conexa(tmp_path):
    """Una red que ya es un ciclo se marca True en el CSV (se calcula fuera del cronómetro)."""
    ciclo = grafo_sintetico({1: (-75.67, 4.53), 2: (-75.66, 4.54), 3: (-75.65, 4.53)},
                            [(1, 2, {"length": 1.0}), (2, 3, {"length": 1.0}),
                             (3, 1, {"length": 1.0})])
    raw = tmp_path / "raw"
    raw.mkdir()
    for nombre in NOMBRES:
        ox.save_graphml(ciclo, raw / ARCHIVOS_CRUDOS[nombre])
    medir_componente.main(raw=raw, salida=tmp_path / "results")
    tabla = pd.read_csv(tmp_path / "results" / "r1_tiempos_componente.csv")
    assert (tabla["ya_fuertemente_conexa"] == True).all()  # noqa: E712

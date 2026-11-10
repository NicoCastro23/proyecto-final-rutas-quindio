"""Pruebas de rutas/r1/construir_red.py con una red cruda sintética (sin internet)."""
import json

import osmnx as ox
import pandas as pd
import pytest

from rutas.config import ARCHIVOS_CRUDOS, CATALOGO
from rutas.r1 import construir_red
from rutas.r1.memoria import estimar_memoria
from rutas.r1.persistencia import cargar_grafo_procesado, cargar_lugares_nodos
from tests.conftest import grafo_sintetico

COLUMNAS_MEMORIA = ["red", "V", "E", "representacion", "supuesto", "bytes", "MB"]
REDES = ["Red descargada", "Componente fuertemente conexa"]


def red_cruda():
    """Cuatro nodos en el Quindío: 1, 2, 3 forman un ciclo (la componente) y el 4 solo recibe
    una arista, así que queda fuera. El 2 -> 3 tiene dos aristas paralelas."""
    nodos = {1: (-75.6716, 4.5339), 2: (-75.6600, 4.5400), 3: (-75.6500, 4.5300),
             4: (-75.6000, 4.5000)}
    return grafo_sintetico(nodos, [
        (1, 2, 0, {"length": 1000.0, "highway": "residential", "maxspeed": "36"}),
        (2, 3, 0, {"length": 1500.0, "highway": "primary"}),
        (2, 3, 1, {"length": 1700.0, "highway": "tertiary"}),
        (3, 1, 0, {"length": 900.0, "highway": "residential"}),
        (3, 4, 0, {"length": 5000.0, "highway": "track"}),
    ])


@pytest.fixture
def carpetas(tmp_path):
    raw = tmp_path / "raw"
    raw.mkdir()
    ox.save_graphml(red_cruda(), raw / ARCHIVOS_CRUDOS["Departamento completo"])
    return dict(raw=raw, processed=tmp_path / "processed", results=tmp_path / "results")


def correr(carpetas, **extra):
    construir_red.main(raw=carpetas["raw"], catalogo=CATALOGO,
                       salida_processed=carpetas["processed"],
                       salida_results=carpetas["results"], **extra)


def test_pipeline_sintetico_escribe_salidas(carpetas):
    correr(carpetas)
    processed, results = carpetas["processed"], carpetas["results"]
    for nombre in ("grafo_componente.graphml", "lugares_nodos.csv", "metadatos.json"):
        assert (processed / nombre).exists()

    tamanos = pd.read_csv(results / "r1_tamanos.csv")
    assert list(tamanos.columns) == ["red", "nodos", "aristas"]
    assert list(tamanos["red"]) == REDES
    assert tamanos["nodos"].tolist() == [4, 3] and tamanos["aristas"].tolist() == [5, 4]

    velocidades = pd.read_csv(results / "r1_velocidades.csv")
    assert {"highway", "aristas", "pct_osm", "pct_imputado"} <= set(velocidades.columns)
    assert velocidades["highway"].iloc[-1] == "Total"
    assert (results / "r1_memoria.csv").exists()

    meta = json.loads((processed / "metadatos.json").read_text(encoding="utf-8"))
    assert meta["V_antes"] > meta["V_despues"]
    G = cargar_grafo_procesado(processed)
    assert (G.number_of_nodes(), G.number_of_edges()) == (meta["V_despues"], meta["E_despues"])


def test_memoria_cuatro_filas_dos_redes(carpetas):
    correr(carpetas)
    memoria = pd.read_csv(carpetas["results"] / "r1_memoria.csv")
    meta = json.loads((carpetas["processed"] / "metadatos.json").read_text(encoding="utf-8"))
    assert list(memoria.columns) == COLUMNAS_MEMORIA
    assert list(memoria["red"]) == [REDES[0], REDES[0], REDES[1], REDES[1]]
    assert list(memoria["representacion"]) == ["Matriz de adyacencia", "Listas de adyacencia"] * 2
    esperado = [(meta["V_antes"], meta["E_antes"])] * 2 + [(meta["V_despues"], meta["E_despues"])] * 2
    assert list(zip(memoria["V"], memoria["E"])) == esperado
    for _, fila in memoria.iterrows():
        estimacion = estimar_memoria(fila["V"], fila["E"])
        clave = "matriz_bytes" if fila["representacion"].startswith("Matriz") else "listas_bytes"
        assert fila["bytes"] == estimacion[clave]


def test_pipeline_con_graphml(carpetas, tmp_path):
    docente = tmp_path / "docente.graphml"
    ox.save_graphml(red_cruda(), docente)
    construir_red.main(raw=carpetas["raw"] / "no_existe", graphml=docente, catalogo=CATALOGO,
                       salida_processed=carpetas["processed"], salida_results=carpetas["results"])
    meta = json.loads((carpetas["processed"] / "metadatos.json").read_text(encoding="utf-8"))
    assert meta["fuente"] == "GraphML del docente"


def test_alertas_se_conservan(carpetas):
    correr(carpetas)
    lugares = cargar_lugares_nodos(carpetas["processed"])
    assert len(lugares) == 42
    assert lugares["alerta_500m"].any()          # con 3 nodos en Armenia casi todos quedan lejos


def test_pipeline_comprime_si_supera_umbral(carpetas):
    correr(carpetas, umbral_gz=0)
    processed = carpetas["processed"]
    assert (processed / "grafo_componente.graphml.gz").exists()
    assert not (processed / "grafo_componente.graphml").exists()
    meta = json.loads((processed / "metadatos.json").read_text(encoding="utf-8"))
    assert meta["comprimido"] is True
    assert cargar_grafo_procesado(processed).number_of_nodes() == 3

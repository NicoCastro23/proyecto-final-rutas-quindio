from pathlib import Path

import networkx as nx

from rutas import config
from tests.conftest import grafo_sintetico


def test_rutas_y_constantes():
    assert config.CATALOGO.exists()
    assert config.EPSG_UTM == 32618
    assert config.RADIOS_M == (2000, 5000, 10000, 20000)
    assert config.UMBRAL_ALERTA_M == 500
    assert config.UMBRAL_GZ_BYTES == 100_000_000


def test_fabrica_grafo_sintetico():
    G = grafo_sintetico({1: (-75.6, 4.5), 2: (-75.7, 4.6)},
                        [(1, 2, {"length": 10.0})])
    assert isinstance(G, nx.MultiDiGraph)
    assert G.graph["crs"] == "epsg:4326"
    assert G.nodes[1]["x"] == -75.6 and G.nodes[1]["y"] == 4.5


def test_gitignore_excluye_data_raw():
    lineas = [l.strip() for l in (config.RAIZ / ".gitignore").read_text().splitlines()]
    # data/raw/ se ignora; data/processed/ se versiona (no debe estar ignorada).
    # Sobre docs/ no se exige nada: su versionado lo decide el grupo.
    assert "data/raw/" in lineas
    assert not any(l.rstrip("/") in ("data/processed", "data") for l in lineas)
    assert not any("data/processed" in l for l in lineas)


def test_rutas_r2():
    assert config.RESULTS_R2 == config.RAIZ / "results" / "r2"
    assert config.MATRIZ_TIEMPOS.name == "matriz_tiempos.csv"
    assert config.MATRIZ_TIEMPOS.parent == config.DATA_PROCESSED


def test_rutas_r3():
    assert config.RESULTS_R3 == config.RAIZ / "results" / "r3"
    assert config.ENVOLVENTE_CSV.name == "envolvente.csv"
    assert config.ENVOLVENTE_GEOJSON.name == "envolvente.geojson"
    assert config.ENVOLVENTE_CSV.parent == config.DATA_PROCESSED
    assert config.ENVOLVENTE_GEOJSON.parent == config.DATA_PROCESSED


def test_rutas_r4():
    assert config.RESULTS_R4 == config.RAIZ / "results" / "r4"

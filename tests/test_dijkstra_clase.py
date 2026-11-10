"""Pruebas con la red de la clase de Dijkstra (R2, casos 19 a 23)."""
import json

import pytest

from rutas.config import RAIZ
from rutas.r2.dijkstra import VERSIONES, consultar, dijkstra_cola
from tests.conftest import cargar_red_clase, red_desde_aristas

ARCHIVO = RAIZ / "tests" / "datos" / "red_clase.json"
ORIGINAL = RAIZ / "estudio" / "casos_prueba.json"


def test_red_clase_versionada():
    assert ARCHIVO.exists()
    datos = json.loads(ARCHIVO.read_text(encoding="utf-8"))
    assert set(datos) == {"_origen", "red", "R2"}
    aristas = datos["red"]["aristas"]
    assert len(aristas) == 24
    assert sorted(a["min"] for a in aristas if (a["u"], a["v"]) == (2, 3)) == [2, 5]

    red, seccion_r2 = cargar_red_clase()
    assert red.ids == [1, 2, 3, 4, 5, 6, 7]
    assert sum(len(a) for a in red.adyacencia) == 22
    assert seccion_r2 == datos["R2"]

    # Si estudio/ existe (no se versiona), la copia debe ser idéntica al original
    if ORIGINAL.exists():
        original = json.loads(ORIGINAL.read_text(encoding="utf-8"))
        assert datos["red"] == original["red"]
        assert datos["R2"] == original["R2"]


VERSION = pytest.mark.parametrize("version", ["lineal", "cola_prioridad"])


@VERSION
def test_caso_19_orden_de_extraccion(version):
    red, _ = cargar_red_clase()
    # El destino que sale en la posición k tiene k explorados al parar en él
    explorados = {d: consultar(red, 1, d, version)[2] for d in range(1, 8)}
    orden = sorted(explorados, key=explorados.get)
    assert orden == [1, 2, 3, 4, 5, 7, 6]
    dist, _, _ = VERSIONES[version](red.adyacencia, red.indice[1])
    assert [dist[red.indice[n]] for n in orden] == [0, 1, 3, 4, 5, 8, 9]


def test_caso_19_orden_observado_en_la_cola(monkeypatch):
    """Observación directa (sin deducir): se espía heappop y la primera salida de cada nodo
    (las posteriores son entradas obsoletas) da el orden de extracción real, sin destino."""
    from rutas.r2 import dijkstra
    red, _ = cargar_red_clase()
    sacados = []
    heappop_real = dijkstra.heapq.heappop

    def heappop_espia(cola):
        entrada = heappop_real(cola)
        sacados.append(entrada)
        return entrada

    monkeypatch.setattr(dijkstra.heapq, "heappop", heappop_espia)
    dijkstra_cola(red.adyacencia, red.indice[1])
    orden, distancias = [], []
    for distancia, u in sacados:
        if red.ids[u] not in orden:
            orden.append(red.ids[u])
            distancias.append(distancia)
    assert orden == [1, 2, 3, 4, 5, 7, 6]
    assert distancias == [0, 1, 3, 4, 5, 8, 9]


@VERSION
def test_caso_21_explorados_con_parada(version):
    red, r2 = cargar_red_clase()
    for caso in r2["explorados_con_parada"]:
        assert consultar(red, caso["origen"], caso["destino"], version)[2] == caso["explorados"]
    assert [c["explorados"] for c in r2["explorados_con_parada"]] == [2, 3, 4, 5, 7, 6]


@VERSION
def test_caso_22_arista_paralela(version):
    red, r2 = cargar_red_clase()
    assert consultar(red, 1, 3, version)[0] == r2["arista_paralela"]["esperado"] == 3


@VERSION
def test_caso_23_matriz_clase(version):
    red, r2 = cargar_red_clase()
    for origen, fila in zip(r2["matriz_min"]["orden"], r2["matriz_min"]["filas"]):
        dist, _, _ = VERSIONES[version](red.adyacencia, red.indice[origen])
        assert [dist[red.indice[n]] for n in r2["matriz_min"]["orden"]] == fila


def test_caso_20_conteo_cola():
    red, r2 = cargar_red_clase()
    estadisticas = {}
    _, _, explorados = dijkstra_cola(red.adyacencia, red.indice[2], estadisticas=estadisticas)
    esperado = r2["cola_origen_2"]
    assert explorados == esperado["explorados"] == 7
    assert estadisticas == {"extracciones": 9, "obsoletas": 2}
    assert estadisticas == {k: esperado[k] for k in ("extracciones", "obsoletas")}


def test_estadisticas_no_cambian_resultado():
    red, _ = cargar_red_clase()
    g1 = red_desde_aristas([(1, 2, 4), (1, 3, 1), (3, 2, 2), (2, 4, 1), (3, 4, 5), (4, 5, 3)],
                           nodos=[6])
    for r in (red, g1):
        for origen in range(len(r.ids)):
            for destino in (None, 0, 3):
                sin = dijkstra_cola(r.adyacencia, origen, destino)
                con = dijkstra_cola(r.adyacencia, origen, destino, estadisticas={})
                assert sin == con

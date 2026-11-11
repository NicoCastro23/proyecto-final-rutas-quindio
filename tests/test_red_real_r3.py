"""Envolvente de la red real (R3, casos 14 y 17). Necesita data/processed/ (se salta si falta)."""
import json
import math

import numpy as np
import pandas as pd
import pytest
from scipy.spatial import ConvexHull

from rutas.r3.envolvente import area, envolvente, normalizar
from rutas.config import RESULTS_R3
from rutas.r3.medir_envolvente import COLUMNAS, NOMBRE_RED, TAMANOS, nombre_cuadrado
from rutas.r3.puntos import puntos_cuadrado, puntos_de_grafo
from rutas.r3.referencia import vertices_scipy
from tests.conftest import comprobar_envolvente

pytestmark = pytest.mark.red


def test_caso_14_red_real(grafo_procesado_real):
    puntos = puntos_de_grafo(grafo_procesado_real)
    assert len(puntos) == 8791
    propios = envolvente(puntos)
    referencia = vertices_scipy(puntos)
    assert set(propios) == set(referencia)          # mismos vértices como conjunto
    assert normalizar(propios) == referencia        # y en el mismo orden y punto de inicio
    assert len(propios) == 14
    area_scipy = ConvexHull(np.array(puntos, dtype=np.float64)).volume
    assert abs(area(propios) - area_scipy) <= 1     # m2
    comprobar_envolvente(propios, puntos)
    assert all(401_796 <= x <= 446_623 and 464_304 <= y <= 520_840 for x, y in puntos)


def test_caso_17_archivos_reales(grafo_procesado_real):
    from rutas.config import ENVOLVENTE_CSV, ENVOLVENTE_GEOJSON
    from tests.test_archivos_r3 import comprobar_archivos
    if not ENVOLVENTE_CSV.exists():
        pytest.skip("falta data/processed/envolvente.csv (python -m rutas.r3.archivos)")
    vertices = envolvente(puntos_de_grafo(grafo_procesado_real))
    assert len(vertices) == 14
    comprobar_archivos(ENVOLVENTE_CSV, ENVOLVENTE_GEOJSON, vertices)
    area_km2 = json.loads(ENVOLVENTE_GEOJSON.read_text(encoding="utf-8"))["features"][0]["properties"]["area_km2"]
    assert abs(area_km2 - 1631.5) <= 1


def comprobar_resultados_r3(df, puntos_json, tamanos=TAMANOS, n_red=8791, vertices_red=14):
    """Revisa r3_envolvente.csv (df, leído con keep_default_na=False) contra r3_puntos.json. AssertionError si algo falla."""
    nombres = [NOMBRE_RED] + [nombre_cuadrado(n) for n in tamanos]
    assert list(df["conjunto"]) == nombres, "faltan filas o están fuera del orden del Anexo"
    assert list(df.columns[:len(COLUMNAS)]) == COLUMNAS, "columnas del Anexo"
    por_nombre = {c["conjunto"]: c for c in puntos_json["conjuntos"]}
    for fila in df.itertuples():
        punto = por_nombre[fila.conjunto]
        assert fila.n == punto["n_obtenido"] and fila.n <= punto["n_pedido"]
        for tiempo in (fila.tiempo_propio_ms, fila.tiempo_scipy_ms):
            assert tiempo == "no completada" or tiempo > 0
        if fila.cociente != "no completada":
            assert math.isclose(fila.cociente, fila.tiempo_propio_ms / fila.tiempo_scipy_ms, rel_tol=1e-9)
        else:
            assert "no completada" in (fila.tiempo_propio_ms, fila.tiempo_scipy_ms)
    red = df.iloc[0]
    assert red.n == n_red and red.vertices == vertices_red, "la red debe tener 8791 puntos y 14 vértices"
    for fila in df.iloc[1:].itertuples():
        pedido = por_nombre[fila.conjunto]["n_pedido"]
        assert fila.vertices == len(envolvente(puntos_cuadrado(pedido))), f"vértices de {fila.conjunto}"


def test_resultados_medidos():
    ruta = RESULTS_R3 / "r3_envolvente.csv"
    if not ruta.exists():
        pytest.skip("falta results/r3/r3_envolvente.csv (python -m rutas.r3.medir_envolvente)")
    df = pd.read_csv(ruta, keep_default_na=False)
    puntos_json = json.loads((RESULTS_R3 / "r3_puntos.json").read_text(encoding="utf-8"))
    comprobar_resultados_r3(df, puntos_json)

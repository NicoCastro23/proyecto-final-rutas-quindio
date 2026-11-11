"""Envolvente de la red real (R3, casos 14 y 17). Necesita data/processed/ (se salta si falta)."""
import json

import numpy as np
import pytest
from scipy.spatial import ConvexHull

from rutas.r3.envolvente import area, envolvente, normalizar
from rutas.r3.puntos import puntos_de_grafo
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

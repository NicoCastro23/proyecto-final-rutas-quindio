"""Pruebas de rutas/r4/calidad.py."""
import random

import pandas as pd
import pytest

from rutas.r2.matriz import guardar_matriz
from rutas.r4 import calidad
from rutas.r4.calidad import COLUMNAS, COLUMNAS_DETALLE, calidad_instancias, main, resumir_calidad
from tests.test_tsp_clase import T_CLASE

IDS_CLASE = ["C01", "A01", "A02", "A03"]


def test_detalle_matriz_clase():
    instancias = [{"k": 3, "semilla": 2026, "ids": ["A01", "A02", "A03"]}]
    filas = calidad_instancias([[float(x) for x in f] for f in T_CLASE], IDS_CLASE, instancias)
    assert len(filas) == 1 and list(filas[0]) == COLUMNAS_DETALLE
    fila = filas[0]
    assert fila["optimo_s"] == 35 and fila["heuristica_s"] == 39
    assert fila["brecha_pct"] == pytest.approx(11.428571, abs=1e-4)
    assert fila["lugares"] == "A01-A02-A03" and fila["k"] == 3 and fila["semilla"] == 2026


def test_caso_20_resumen():
    detalle = pd.DataFrame({"k": [5, 5, 5, 8, 8], "brecha_pct": [0.0, 10.0, 20.0, 5.0, 15.0]})
    resumen = resumir_calidad(detalle)
    assert list(resumen.columns) == COLUMNAS
    fila5, fila8 = resumen.iloc[0], resumen.iloc[1]
    assert (fila5["k"], fila5["instancias"]) == (5, 3)
    assert fila5["brecha_promedio_pct"] == pytest.approx(10.0)
    assert fila5["brecha_maxima_pct"] == pytest.approx(20.0)
    assert (fila8["k"], fila8["instancias"]) == (8, 2)
    assert fila8["brecha_promedio_pct"] == pytest.approx(10.0)
    assert fila8["brecha_maxima_pct"] == pytest.approx(15.0)


def test_brecha_negativa_es_error(monkeypatch):
    monkeypatch.setattr(calidad, "vecino_mas_cercano", lambda T, s, lugares: (1.0, [s, *lugares, s]))
    instancias = [{"k": 3, "semilla": 1, "ids": ["A01", "A02", "A03"]}]
    with pytest.raises(ValueError, match="brecha"):
        calidad_instancias([[float(x) for x in f] for f in T_CLASE], IDS_CLASE, instancias)


def test_main_sintetico(tmp_path):
    n = 13
    ids = [f"C{i + 1:02d}" for i in range(n)]
    azar = random.Random(5)
    T = [[0.0 if i == j else float(azar.randint(1, 100)) for j in range(n)] for i in range(n)]
    matriz = tmp_path / "matriz.csv"
    guardar_matriz(T, ids, matriz)
    catalogo = tmp_path / "catalogo.csv"
    pd.DataFrame({"id": ids}).to_csv(catalogo, index=False)
    salida = tmp_path / "salida"
    main(matriz=matriz, catalogo=catalogo, salida=salida)
    detalle = pd.read_csv(salida / "r4_calidad_detalle.csv")
    resumen = pd.read_csv(salida / "r4_calidad.csv")
    assert len(detalle) == 40 and list(detalle.columns) == COLUMNAS_DETALLE
    assert list(resumen.columns) == COLUMNAS and len(resumen) == 4
    assert (resumen["instancias"] == 10).all()

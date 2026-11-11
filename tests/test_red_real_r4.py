"""R4 con la matriz real de R2 (casos 19a, 19b, 19c). Marcador `red`."""
import json

import pandas as pd
import pytest

from rutas.config import CATALOGO, MATRIZ_TIEMPOS, RESULTS_R4
from rutas.r2.matriz import cargar_matriz
from rutas.r4.fuerza_bruta import fuerza_bruta
from rutas.r4.held_karp import held_karp
from rutas.r4.instancias import muestra_anidada
from rutas.r4.itinerario import ATRACTIVOS_DIA, itinerario_dia, visitas_del_catalogo
from rutas.r4.por_ids import matriz_a_listas
from rutas.r4.recorrido import costo_recorrido

pytestmark = pytest.mark.red


@pytest.fixture(scope="module")
def red_real():
    if not MATRIZ_TIEMPOS.exists():
        pytest.skip("falta data/processed/matriz_tiempos.csv")
    T, ids = matriz_a_listas(cargar_matriz(MATRIZ_TIEMPOS))
    return T, ids


@pytest.mark.parametrize("k", [5, 6, 7, 8])
def test_caso_19a_fb_igual_hk(red_real, k):
    T, ids = red_real
    s = ids.index("C01")
    lugares = [ids.index(i) for i in muestra_anidada(ids)[:k]]
    assert fuerza_bruta(T, s, lugares)[0] == pytest.approx(held_karp(T, s, lugares)[0], abs=1e-6)


def test_caso_19b_hk_k12(red_real):
    T, ids = red_real
    s = ids.index("C01")
    lugares = [ids.index(i) for i in muestra_anidada(ids)]
    valor, recorrido = held_karp(T, s, lugares)
    assert recorrido[0] == s and recorrido[-1] == s
    assert sorted(recorrido[1:-1]) == sorted(lugares)
    assert costo_recorrido(T, recorrido) == pytest.approx(valor, abs=1e-6)


def itinerario_real(T, ids, atractivos=ATRACTIVOS_DIA):
    visitas = visitas_del_catalogo(pd.read_csv(CATALOGO), ids)
    return itinerario_dia(T, ids, ids.index("C01"), [ids.index(a) for a in atractivos], visitas)


def test_caso_19c_itinerario(red_real):
    T, ids = red_real
    filas, quitados, totales = itinerario_real(T, ids)
    assert [q["id"] for q in quitados] == ["A01", "A12"]
    assert quitados[0]["jornada_antes_min"] == pytest.approx(1255.2, abs=0.1)
    assert quitados[0]["jornada_despues_min"] == pytest.approx(809.6, abs=0.1)
    assert totales["jornada_min"] == pytest.approx(613.1, abs=0.1)
    assert totales["atractivos_finales"] == 6
    assert totales["cabe"]


def test_archivos_itinerario_reales(red_real):
    ruta = RESULTS_R4 / "r4_itinerario.json"
    if not ruta.exists():
        pytest.skip("falta results/r4/r4_itinerario.json")
    datos = json.loads(ruta.read_text(encoding="utf-8"))
    _, quitados, totales = itinerario_real(*red_real)
    assert [q["id"] for q in datos["quitados"]] == [q["id"] for q in quitados]
    assert datos["totales"]["jornada_min"] == pytest.approx(totales["jornada_min"], abs=1e-6)
    assert len(datos["atractivos_finales"]) == 6
    assert datos["cabe"] is True

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


# ---- T22: comprobación de los resultados medidos (r4_exactas.csv) ----
from rutas.r4.medir_exactas import COLUMNAS, METODOS_EXACTOS


def comprobar_resultados_r4(df, instancias_json):
    """Lanza AssertionError si r4_exactas.csv (leído con keep_default_na=False) no cumple la spec."""
    assert list(df.columns) == COLUMNAS, "columnas distintas de COLUMNAS"
    esperado = [(k, m) for k in range(5, 13) for m in METODOS_EXACTOS]
    assert len(df) == 16, f"se esperaban 16 filas y hay {len(df)}"
    assert list(zip(df["k"], df["metodo"])) == esperado, "las filas no están en el orden k, método"
    assert set(df["estado"]) <= {"ok", "no_completada", "no_ejecutada"}, "estado inválido"
    muestra = instancias_json["muestra_anidada"]
    partida = instancias_json["partida"]

    for metodo in METODOS_EXACTOS:
        filas = df[df["metodo"] == metodo]
        vista_no_completada = False
        for _, fila in filas.iterrows():
            if vista_no_completada:
                assert fila["estado"] == "no_ejecutada", \
                    f"{metodo} k = {fila['k']}: tras una no_completada solo puede haber no_ejecutada"
            if fila["estado"] == "no_completada":
                vista_no_completada = True
            if fila["estado"] != "ok":
                continue
            k = int(fila["k"])
            assert float(fila["tiempo_ms"]) > 0, f"{metodo} k = {k}: tiempo no positivo"
            assert int(fila["repeticiones"]) in (1, 5), f"{metodo} k = {k}: repeticiones inválidas"
            partes = fila["recorrido"].split("-")
            assert partes[0] == partida and partes[-1] == partida, f"{metodo} k = {k}: no parte y termina en la partida"
            assert sorted(partes[1:-1]) == sorted(muestra[:k]), f"{metodo} k = {k}: lugares distintos de la muestra"

    hk = df[df["metodo"] == "held_karp"]
    assert (hk["estado"] == "ok").all(), "Held-Karp debe resolver todos los k"
    for k in range(5, 13):
        fb_fila = df[(df["k"] == k) & (df["metodo"] == "fuerza_bruta")].iloc[0]
        if fb_fila["estado"] == "ok":
            hk_fila = hk[hk["k"] == k].iloc[0]
            assert abs(float(fb_fila["tiempo_total_s"]) - float(hk_fila["tiempo_total_s"])) <= 1e-6, \
                f"k = {k}: FB y HK dan distinto tiempo total"


def test_resultados_medidos():
    ruta = RESULTS_R4 / "r4_exactas.csv"
    if not ruta.exists():
        pytest.skip("falta results/r4/r4_exactas.csv (corre rutas.r4.medir_exactas)")
    df = pd.read_csv(ruta, keep_default_na=False)
    instancias = json.loads((RESULTS_R4 / "r4_instancias.json").read_text(encoding="utf-8"))
    comprobar_resultados_r4(df, instancias)

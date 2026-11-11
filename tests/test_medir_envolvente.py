"""Pruebas de rutas/r3/medir_envolvente.py. Medidores falsos; el cronómetro real solo con 200 puntos."""
import json

import numpy
import pytest
from scipy.spatial import ConvexHull

from rutas.medicion import NO_COMPLETADA, ResultadoMedicion
from rutas.r3 import medir_envolvente
from rutas.r3.envolvente import envolvente
from rutas.r3.medir_envolvente import (COLUMNAS, NOMBRE_RED, comprobar_iguales, conjuntos, main,
                                       medir_conjunto, nombre_cuadrado)
from rutas.r3.puntos import puntos_cuadrado
from tests.conftest import carpeta_sintetica

PUNTOS_RED = [(0, 0), (4, 0), (4, 4), (0, 4), (2, 2)]     # cuadrado con un punto interior


def resultado(ms, repeticiones=5):
    return ResultadoMedicion(tiempo_ms=ms, repeticiones=repeticiones, completada=True, tiempos_ms=[ms])


def test_nombres_y_orden_del_anexo():
    assert nombre_cuadrado(1000) == "Cuadrado, 1 000 puntos"
    assert nombre_cuadrado(50000) == "Cuadrado, 50 000 puntos"
    lista = conjuntos(PUNTOS_RED, tamanos=(10, 20))
    assert [(nombre, pedido) for nombre, pedido, _ in lista] == [
        (NOMBRE_RED, 5), ("Cuadrado, 10 puntos", 10), ("Cuadrado, 20 puntos", 20)]
    assert lista[0][2] == PUNTOS_RED
    assert lista[1][2] == puntos_cuadrado(10)


def test_comprobar_iguales_error_explicito(monkeypatch):
    monkeypatch.setattr(medir_envolvente, "vertices_scipy", lambda puntos: [(0, 0), (1, 0), (0, 1)])
    with pytest.raises(ValueError, match=NOMBRE_RED) as error:
        comprobar_iguales([(NOMBRE_RED, 5, PUNTOS_RED)])
    assert not isinstance(error.value, AssertionError)


def test_comprobar_iguales_acepta_lo_correcto():
    comprobar_iguales([(NOMBRE_RED, 5, PUNTOS_RED), ("c", 200, puntos_cuadrado(200))])


def test_medir_conjunto_con_medidor_falso():
    llamadas = []

    def falso(funcion, preparar, repeticiones=5):
        llamadas.append((funcion, preparar(), repeticiones))
        return resultado(8.0 if funcion is envolvente else 2.0)

    fila = medir_conjunto(NOMBRE_RED, PUNTOS_RED, repeticiones=3, medir=falso)
    assert [c[0] for c in llamadas] == [envolvente, ConvexHull]
    assert llamadas[0][1][0] == PUNTOS_RED and isinstance(llamadas[0][1][0], list)
    arreglo = llamadas[1][1][0]
    assert isinstance(arreglo, numpy.ndarray) and arreglo.dtype == numpy.float64
    assert arreglo.tolist() == [list(map(float, p)) for p in PUNTOS_RED]
    assert llamadas[0][2] == 3
    assert list(fila) == COLUMNAS
    assert fila["conjunto"] == NOMBRE_RED and fila["n"] == 5 and fila["vertices"] == 4
    assert fila["tiempo_propio_ms"] == 8.0 and fila["tiempo_scipy_ms"] == 2.0
    assert fila["cociente"] == 8.0 / 2.0 and fila["repeticiones"] == 5


def test_no_completada():
    def falso(funcion, preparar, repeticiones=5):
        return NO_COMPLETADA if funcion is envolvente else resultado(2.0)

    fila = medir_conjunto("c", PUNTOS_RED, medir=falso)
    assert fila["tiempo_propio_ms"] == "no completada" and fila["cociente"] == "no completada"
    assert fila["tiempo_scipy_ms"] == 2.0


def test_repeticiones_minimo():
    def falso(funcion, preparar, repeticiones=5):
        return resultado(1.0, 5 if funcion is envolvente else 1)

    assert medir_conjunto("c", PUNTOS_RED, medir=falso)["repeticiones"] == 1


def test_medir_en_proceso_de_verdad():
    fila = medir_conjunto("c", puntos_cuadrado(200), repeticiones=1)
    assert fila["tiempo_propio_ms"] > 0 and fila["tiempo_scipy_ms"] > 0 and fila["repeticiones"] == 1


def test_main_sintetico_escribe_archivos(tmp_path, monkeypatch):
    monkeypatch.setattr(medir_envolvente, "TAMANOS", (50, 100))
    salida = tmp_path / "salida"
    main(carpeta_sintetica(tmp_path / "processed"), salida, repeticiones=1)
    import pandas as pd
    df = pd.read_csv(salida / "r3_envolvente.csv", keep_default_na=False)
    assert list(df["conjunto"]) == [NOMBRE_RED, "Cuadrado, 50 puntos", "Cuadrado, 100 puntos"]
    assert list(df.columns) == COLUMNAS and df["vertices"][0] == 4
    datos = json.loads((salida / "r3_puntos.json").read_text(encoding="utf-8"))
    assert datos["semilla"] == 2026 and datos["lado"] == 10**6
    assert "floor" in datos["redondeo"] and "Random(2026)" in datos["nota"]
    assert [(c["conjunto"], c["n_pedido"]) for c in datos["conjuntos"]] == [
        (NOMBRE_RED, 6), ("Cuadrado, 50 puntos", 50), ("Cuadrado, 100 puntos", 100)]
    assert all(c["n_obtenido"] <= c["n_pedido"] for c in datos["conjuntos"])
    assert list(df["n"]) == [c["n_obtenido"] for c in datos["conjuntos"]]
    assert "procesador" in json.loads((salida / "maquina.json").read_text(encoding="utf-8"))


def test_main_no_escribe_si_difieren(tmp_path, monkeypatch):
    monkeypatch.setattr(medir_envolvente, "TAMANOS", (50,))
    monkeypatch.setattr(medir_envolvente, "vertices_scipy", lambda puntos: [(0, 0), (1, 0), (0, 1)])
    salida = tmp_path / "salida"
    with pytest.raises(ValueError):
        main(carpeta_sintetica(tmp_path / "processed"), salida, repeticiones=1)
    assert not salida.exists() or not list(salida.iterdir())


# ---- T16: comprobar_resultados_r3 con CSV sintéticos ----
import pandas as pd

from tests.test_red_real_r3 import comprobar_resultados_r3

TAMANOS_PRUEBA = (50, 100)


def resultados_correctos():
    """(df, puntos_json) de una medición ficticia pero coherente: 3 filas con n_red = 5, 4 vértices."""
    lista = conjuntos(PUNTOS_RED, tamanos=TAMANOS_PRUEBA)
    filas = [{"conjunto": nombre, "n": len(puntos), "vertices": len(envolvente(puntos)),
              "tiempo_propio_ms": 4.0, "tiempo_scipy_ms": 2.0, "cociente": 2.0, "repeticiones": 5}
             for nombre, _, puntos in lista]
    datos = {"conjuntos": [{"conjunto": nombre, "n_pedido": pedido, "n_obtenido": len(puntos)}
                           for nombre, pedido, puntos in lista]}
    return pd.DataFrame(filas, columns=COLUMNAS), datos


def comprobar(df, datos):
    comprobar_resultados_r3(df, datos, tamanos=TAMANOS_PRUEBA, n_red=5, vertices_red=4)


def test_resultados_correctos_pasan():
    comprobar(*resultados_correctos())


def test_resultados_fila_faltante():
    df, datos = resultados_correctos()
    with pytest.raises(AssertionError):
        comprobar(df.iloc[:-1], datos)


def test_resultados_orden_cambiado():
    df, datos = resultados_correctos()
    with pytest.raises(AssertionError):
        comprobar(df.iloc[[0, 2, 1]].reset_index(drop=True), datos)


def test_resultados_cociente_mal_calculado():
    df, datos = resultados_correctos()
    df.loc[1, "cociente"] = 3.0
    with pytest.raises(AssertionError):
        comprobar(df, datos)


def test_resultados_vertices_de_la_red_distintos():
    df, datos = resultados_correctos()
    df.loc[0, "vertices"] = 5
    with pytest.raises(AssertionError):
        comprobar(df, datos)


def test_resultados_vertices_de_un_cuadrado_distintos():
    df, datos = resultados_correctos()
    df.loc[2, "vertices"] += 1
    with pytest.raises(AssertionError):
        comprobar(df, datos)


def test_resultados_no_completada_es_valida():
    df, datos = resultados_correctos()
    df = df.astype(object)
    df.loc[1, ["tiempo_propio_ms", "cociente"]] = "no completada"
    comprobar(df, datos)

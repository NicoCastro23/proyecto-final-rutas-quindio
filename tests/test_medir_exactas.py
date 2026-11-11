"""Pruebas de rutas/r4/medir_exactas.py con un medidor falso (no se mide tiempo real)."""
import json
import random

import pandas as pd
import pytest

from rutas.medicion import NO_COMPLETADA, ResultadoMedicion
from rutas.r2.matriz import guardar_matriz
from rutas.r4 import medir_exactas as modulo
from rutas.r4.fuerza_bruta import fuerza_bruta
from rutas.r4.held_karp import held_karp
from rutas.r4.medir_exactas import COLUMNAS, main, medir_exactas

PARTIDA = 0


def matriz_aleatoria(n, semilla=7):
    azar = random.Random(semilla)
    return [[0.0 if i == j else float(azar.randint(1, 100)) for j in range(n)] for i in range(n)]


def ids_sinteticos(n):
    return [f"C{i + 1:02d}" for i in range(n)]


class MedidorFalso:
    """Registra (función, args, devolver_valor); corre la función aquí y devuelve un resultado fijo."""

    def __init__(self, alterar=None, no_completa=None):
        self.llamadas = []
        self.alterar = alterar or {}            # {nombre de función: se suma a su valor}
        self.no_completa = no_completa or {}    # {nombre: k mínimo desde el que no se completa}

    def __call__(self, funcion, args=(), repeticiones=5, devolver_valor=False, **resto):
        self.llamadas.append((funcion, args, devolver_valor))
        k = len(args[2])
        if k >= self.no_completa.get(funcion.__name__, 10**9):
            return NO_COMPLETADA
        costo, recorrido = funcion(*args)
        costo += self.alterar.get(funcion.__name__, 0.0)
        return ResultadoMedicion(tiempo_ms=1.5, repeticiones=repeticiones, completada=True,
                                 tiempos_ms=[1.5], valor=(costo, recorrido))


@pytest.fixture
def instancia():
    T = matriz_aleatoria(8)                    # partida + 7 lugares
    ids = ids_sinteticos(8)
    muestra = ids[1:]
    return T, ids, muestra


def test_mide_solo_el_algoritmo(instancia):
    T, ids, muestra = instancia
    medidor = MedidorFalso()
    medir_exactas(T, ids, PARTIDA, muestra, ks=(2, 3), medir=medidor)
    assert len(medidor.llamadas) == 4
    for funcion, args, devolver in medidor.llamadas:
        assert funcion in (fuerza_bruta, held_karp)
        assert args == (T, PARTIDA, args[2]) and isinstance(args[0], list) and isinstance(args[0][0], list)
        assert all(isinstance(i, int) for i in args[2])
        assert devolver is True


def test_filas_y_columnas(instancia):
    T, ids, muestra = instancia
    filas = medir_exactas(T, ids, PARTIDA, muestra, ks=(2, 3), medir=MedidorFalso())
    assert [(f["k"], f["metodo"]) for f in filas] == [
        (2, "fuerza_bruta"), (2, "held_karp"), (3, "fuerza_bruta"), (3, "held_karp")]
    assert all(list(f) == COLUMNAS for f in filas)
    fila = filas[2]
    partes = fila["recorrido"].split("-")
    assert partes[0] == partes[-1] == ids[PARTIDA] and len(partes) == 5
    assert fila["estado"] == "ok" and fila["tiempo_ms"] == 1.5 and fila["repeticiones"] == 5
    assert fila["tiempo_total_s"] == pytest.approx(held_karp(T, PARTIDA, [1, 2, 3])[0], abs=1e-6)


def test_no_completada_y_no_ejecutada(instancia):
    T, ids, muestra = instancia
    medidor = MedidorFalso(no_completa={"fuerza_bruta": 3})
    filas = medir_exactas(T, ids, PARTIDA, muestra, ks=(2, 3, 4), medir=medidor)
    assert len(filas) == 6
    fb = {f["k"]: f for f in filas if f["metodo"] == "fuerza_bruta"}
    assert fb[2]["estado"] == "ok"
    assert fb[3]["estado"] == "no_completada" and fb[3]["tiempo_ms"] == "" and fb[3]["repeticiones"] == 0
    assert fb[3]["tiempo_total_s"] == "" and fb[3]["recorrido"] == ""
    assert fb[4]["estado"] == "no_ejecutada" and fb[4]["repeticiones"] == 0
    assert all(f["estado"] == "ok" for f in filas if f["metodo"] == "held_karp")
    # FB en k = 4 no se llamó: 2 (k=2) + 2 (k=3) + 1 (HK, k=4)
    assert len(medidor.llamadas) == 5


def test_verificacion_previa_k_pequeno(instancia, monkeypatch):
    T, ids, muestra = instancia
    monkeypatch.setattr(modulo, "fuerza_bruta", lambda T, s, lugares: (1.0, [s, *lugares, s]))
    medidor = MedidorFalso()
    with pytest.raises(ValueError, match="k = 3"):
        medir_exactas(T, ids, PARTIDA, muestra, ks=(3,), medir=medidor)
    assert medidor.llamadas == []              # falla ANTES de medir


def test_verificacion_con_valor_del_hijo(instancia, monkeypatch):
    T, ids, muestra = instancia
    monkeypatch.setattr(modulo, "K_VERIFICACION_PREVIA", 0)
    medidor = MedidorFalso(alterar={"fuerza_bruta": 5.0})
    with pytest.raises(ValueError, match="fuerza_bruta"):
        medir_exactas(T, ids, PARTIDA, muestra, ks=(3,), medir=medidor)


def escribir_matriz(carpeta, n=13):
    ruta = carpeta / "matriz.csv"
    guardar_matriz(matriz_aleatoria(n), ids_sinteticos(n), ruta)
    return ruta


def test_main_no_escribe_si_falla(tmp_path, monkeypatch):
    matriz = escribir_matriz(tmp_path)
    salida = tmp_path / "salida"
    salida.mkdir()
    monkeypatch.setattr(modulo, "fuerza_bruta", lambda T, s, lugares: (1.0, [s, *lugares, s]))
    with pytest.raises(ValueError):
        main(matriz=matriz, salida=salida, ks=(2, 3), repeticiones=1)
    assert list(salida.iterdir()) == []


def test_main_sintetico_escribe_archivos(tmp_path):
    matriz = escribir_matriz(tmp_path)
    salida = tmp_path / "salida"
    main(matriz=matriz, salida=salida, ks=(2, 3), repeticiones=1)
    df = pd.read_csv(salida / "r4_exactas.csv", keep_default_na=False)
    assert list(df.columns) == COLUMNAS and len(df) == 4
    assert (df["estado"] == "ok").all() and (df["tiempo_ms"] > 0).all()
    assert "python" in json.loads((salida / "maquina.json").read_text(encoding="utf-8"))


# ---- T22: comprobar_resultados_r4 con CSV sintéticos ----
from tests.test_red_real_r4 import comprobar_resultados_r4

MUESTRA = ["C09", "A10", "F07", "T04", "C08", "A04", "F01", "F06", "F03", "A05", "C02", "A09"]
INSTANCIAS = {"partida": "C01", "muestra_anidada": MUESTRA}


def df_correcto():
    filas = []
    for k in range(5, 13):
        recorrido = "-".join(["C01", *MUESTRA[:k], "C01"])
        if k <= 10:
            filas.append([k, "fuerza_bruta", 2.0, 5, "ok", 100.0 + k, recorrido])
        elif k == 11:
            filas.append([k, "fuerza_bruta", "", 0, "no_completada", "", ""])
        else:
            filas.append([k, "fuerza_bruta", "", 0, "no_ejecutada", "", ""])
        filas.append([k, "held_karp", 1.0, 5, "ok", 100.0 + k, recorrido])
    return pd.DataFrame(filas, columns=COLUMNAS)


def test_comprobar_resultados_correcto():
    comprobar_resultados_r4(df_correcto(), INSTANCIAS)


def test_comprobar_fila_faltante():
    with pytest.raises(AssertionError):
        comprobar_resultados_r4(df_correcto().drop(index=3), INSTANCIAS)


def test_comprobar_ok_despues_de_no_completada():
    df = df_correcto()
    fila = df.index[(df["k"] == 12) & (df["metodo"] == "fuerza_bruta")][0]
    df.loc[fila, ["tiempo_ms", "repeticiones", "estado", "tiempo_total_s", "recorrido"]] = [
        2.0, 1, "ok", 112.0, "-".join(["C01", *MUESTRA, "C01"])]
    with pytest.raises(AssertionError, match="no_completada"):
        comprobar_resultados_r4(df, INSTANCIAS)


def test_comprobar_fb_distinto_de_hk():
    df = df_correcto()
    df.loc[(df["k"] == 7) & (df["metodo"] == "fuerza_bruta"), "tiempo_total_s"] = 999.0
    with pytest.raises(AssertionError, match="distinto tiempo"):
        comprobar_resultados_r4(df, INSTANCIAS)


def test_comprobar_recorrido_con_otros_lugares():
    df = df_correcto()
    df.loc[(df["k"] == 6) & (df["metodo"] == "held_karp"), "recorrido"] = "C01-C09-A10-F07-T04-C08-XXX-C01"
    with pytest.raises(AssertionError, match="lugares"):
        comprobar_resultados_r4(df, INSTANCIAS)

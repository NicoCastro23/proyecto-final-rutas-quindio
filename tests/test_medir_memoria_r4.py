"""Pruebas de rutas/r4/medir_memoria.py (matrices sintéticas)."""
import random
import tracemalloc

import pandas as pd

from rutas.r2.matriz import guardar_matriz
from rutas.r4.conteos import memoria_held_karp
from rutas.r4.medir_memoria import COLUMNAS, filas_memoria, main, pico_tracemalloc


def matriz_aleatoria(n, semilla=3):
    azar = random.Random(semilla)
    return [[0.0 if i == j else float(azar.randint(1, 100)) for j in range(n)] for i in range(n)]


def test_pico_positivo_y_crece():
    T = matriz_aleatoria(9)
    pico_5 = pico_tracemalloc(T, 0, list(range(1, 6)))
    pico_8 = pico_tracemalloc(T, 0, list(range(1, 9)))
    assert pico_5 > 0 and pico_8 > pico_5
    assert not tracemalloc.is_tracing()


def test_pico_mayor_que_estimado():
    # En Python cada fila es un objeto list y cada float calculado otro objeto: pesa más que 12 B/celda
    T = matriz_aleatoria(9)
    assert pico_tracemalloc(T, 0, list(range(1, 9))) >= memoria_held_karp(8)["bytes_estimados"]


def test_filas_columnas():
    T = matriz_aleatoria(8)
    filas = filas_memoria(T, 0, {5: [1, 2, 3, 4, 5], 6: [1, 2, 3, 4, 5, 6]})
    assert [f["k"] for f in filas] == [5, 6]
    for fila in filas:
        assert list(fila) == COLUMNAS
        esperado = memoria_held_karp(fila["k"])
        assert fila["celdas"] == esperado["celdas"]
        assert fila["bytes_estimados"] == esperado["bytes_estimados"]
        assert fila["mb_estimados"] == esperado["mb_estimados"]
        assert fila["pico_tracemalloc_mb"] == fila["pico_tracemalloc_bytes"] / 1e6


def test_main_sintetico(tmp_path):
    ids = [f"C{i + 1:02d}" for i in range(13)]
    matriz = tmp_path / "matriz.csv"
    guardar_matriz(matriz_aleatoria(13), ids, matriz)
    main(matriz=matriz, salida=tmp_path / "salida")
    df = pd.read_csv(tmp_path / "salida" / "r4_memoria.csv")
    assert list(df["k"]) == list(range(5, 13)) and list(df.columns) == COLUMNAS

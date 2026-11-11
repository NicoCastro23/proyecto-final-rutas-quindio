"""Memoria de Held-Karp medida con tracemalloc (NO se cronometra).

Uso (desde la raíz del repo):  .venv/bin/python -m rutas.r4.medir_memoria
tracemalloc registra cada asignación de Python y vuelve el código varias veces más lento:
por eso vive en su propio script y nunca se activa en medir_exactas.
"""
import gc
import tracemalloc
from pathlib import Path

import pandas as pd

from rutas.config import MATRIZ_TIEMPOS, RESULTS_R4
from rutas.r2.matriz import cargar_matriz
from rutas.r4.conteos import memoria_held_karp
from rutas.r4.held_karp import held_karp
from rutas.r4.instancias import K_EXACTAS, PARTIDA, muestra_anidada
from rutas.r4.por_ids import matriz_a_listas

COLUMNAS = ["k", "celdas", "bytes_estimados", "mb_estimados",
            "pico_tracemalloc_bytes", "pico_tracemalloc_mb"]


def pico_tracemalloc(T, s, lugares):
    """Máximo de bytes asignados por Python mientras corre held_karp.
    T ya existía antes de empezar a rastrear, así que no se cuenta."""
    gc.collect()
    tracemalloc.start()
    try:
        held_karp(T, s, lugares)
        _, pico = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()          # siempre se apaga, aunque held_karp falle
    return pico


def filas_memoria(T, s, lugares_por_k):
    """Una fila por k: la estimación teórica (12 B por celda) junto al pico medido."""
    filas = []
    for k, lugares in lugares_por_k.items():
        fila = memoria_held_karp(k)
        pico = pico_tracemalloc(T, s, lugares)
        fila["pico_tracemalloc_bytes"] = pico
        fila["pico_tracemalloc_mb"] = pico / 1e6
        filas.append(fila)
    return filas


def main(matriz=MATRIZ_TIEMPOS, salida=RESULTS_R4):
    T, ids = matriz_a_listas(cargar_matriz(matriz))
    muestra = muestra_anidada(ids)
    lugares_por_k = {k: [ids.index(i) for i in muestra[:k]] for k in K_EXACTAS}
    filas = filas_memoria(T, ids.index(PARTIDA), lugares_por_k)
    salida = Path(salida)
    salida.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(filas, columns=COLUMNAS).to_csv(salida / "r4_memoria.csv", index=False)
    print(f"Escrito {salida / 'r4_memoria.csv'}")


if __name__ == "__main__":
    main()

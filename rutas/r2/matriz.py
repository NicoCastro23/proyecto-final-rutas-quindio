"""Matriz de tiempos entre los 42 lugares (la usa R4) y su asimetría."""
import csv
import json
from pathlib import Path

import pandas as pd

from rutas.config import CATALOGO, DATA_PROCESSED, MATRIZ_TIEMPOS, RESULTS_R2
from rutas.r1.persistencia import cargar_grafo_procesado, cargar_lugares_nodos
from rutas.r2.adyacencia import construir_adyacencia
from rutas.r2.dijkstra import dijkstra_cola


def calcular_matriz(red, nodos):
    """matriz[i][j] = segundos del nodo nodos[i] al nodo nodos[j] (nodos en ids de OSM).

    Una corrida de dijkstra_cola sin destino por fila: 42 corridas bastan para los 42 x 42
    tiempos. Dos lugares en el mismo nodo dan 0. La matriz no es simétrica (calles de un sentido).
    """
    for nodo in nodos:
        if nodo not in red.indice:
            raise KeyError(f"el nodo {nodo} no está en la red")
    matriz = []
    for origen in nodos:
        dist, _, _ = dijkstra_cola(red.adyacencia, red.indice[origen])
        fila = [dist[red.indice[destino]] for destino in nodos]
        if float("inf") in fila:
            culpable = nodos[fila.index(float("inf"))]
            raise ValueError(f"el nodo {culpable} es inalcanzable desde {origen}")
        matriz.append(fila)
    return matriz


def guardar_matriz(matriz, ids, ruta):
    """CSV con la esquina "id", los ids de lugar en la primera fila y columna, y cada celda con
    repr(float): la representación completa, sin redondear, que se lee de vuelta exacta."""
    with open(ruta, "w", newline="", encoding="utf-8") as archivo:
        escritor = csv.writer(archivo, lineterminator="\n")
        escritor.writerow(["id", *ids])
        for id_lugar, fila in zip(ids, matriz):
            escritor.writerow([id_lugar, *(repr(float(x)) for x in fila)])


def cargar_matriz(ruta):
    """DataFrame con índice y columnas = ids de lugar. round_trip lee el float tal como se guardó."""
    return pd.read_csv(ruta, index_col=0, float_precision="round_trip")


def asimetria(matriz, ids, tolerancia=1e-6):
    """Cuenta los pares {i, j} con |M[i][j] - M[j][i]| > tolerancia y reporta el de mayor diferencia."""
    cuenta, mayor = 0, None
    for i in range(len(ids)):
        for j in range(i + 1, len(ids)):         # i < j: cada par {i, j} se mira una vez
            diferencia = abs(matriz[i][j] - matriz[j][i])
            if diferencia > tolerancia:
                cuenta += 1
                if mayor is None or diferencia > mayor[0]:
                    mayor = (diferencia, i, j)
    resultado = {"pares_asimetricos": cuenta, "par_max": None, "diferencia_max": 0.0,
                 "M_ij": None, "M_ji": None, "tolerancia": tolerancia}
    if mayor is not None:
        diferencia, i, j = mayor
        resultado.update(par_max=[ids[i], ids[j]], diferencia_max=diferencia,
                         M_ij=matriz[i][j], M_ji=matriz[j][i])
    return resultado


def main(processed=DATA_PROCESSED, catalogo=CATALOGO, salida=RESULTS_R2):
    """Calcula la matriz con el grafo procesado y la guarda; no es una medición de tiempo.

    Escribe processed/matriz_tiempos.csv (la usa R4) y salida/r2_asimetria.json.
    """
    G = cargar_grafo_procesado(processed)
    red = construir_adyacencia(G)
    ids = list(pd.read_csv(catalogo)["id"])                    # orden del catálogo
    lugares = cargar_lugares_nodos(processed)
    nodo_de = dict(zip(lugares["id_lugar"], lugares["id_nodo"]))
    nodos = [int(nodo_de[id_lugar]) for id_lugar in ids]

    matriz = calcular_matriz(red, nodos)
    guardar_matriz(matriz, ids, Path(processed) / MATRIZ_TIEMPOS.name)

    resultado = asimetria(matriz, ids)
    Path(salida).mkdir(parents=True, exist_ok=True)
    (Path(salida) / "r2_asimetria.json").write_text(
        json.dumps(resultado, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Matriz {len(ids)} x {len(ids)} escrita; pares asimétricos: {resultado['pares_asimetricos']}")


if __name__ == "__main__":
    main()

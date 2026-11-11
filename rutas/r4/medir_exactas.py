"""Medición de las soluciones exactas de R4 (fuerza bruta y Held-Karp), sección 6 del enunciado.

Uso (desde la raíz del repo; es LARGA, enchufar el portátil y cerrar otros programas):
    .venv/bin/python -m rutas.r4.medir_exactas
Opciones para pruebas cortas:  --k-max 8  --salida <carpeta>  --repeticiones 1

Solo se cronometra la llamada al algoritmo (dentro de un proceso hijo, con medir_en_hijo).
Fuera del cronómetro quedan: leer la matriz, sortear la muestra, verificar que FB = HK y
escribir los archivos. Si cualquier verificación falla, no se escribe nada.
"""
import argparse
import json
from pathlib import Path

import pandas as pd

from rutas.config import MATRIZ_TIEMPOS, RESULTS_R4
from rutas.medicion import info_maquina, medir_en_hijo
from rutas.r2.matriz import cargar_matriz
from rutas.r4.fuerza_bruta import fuerza_bruta
from rutas.r4.held_karp import held_karp
from rutas.r4.instancias import K_EXACTAS, PARTIDA, muestra_anidada
from rutas.r4.por_ids import matriz_a_listas

COLUMNAS = ["k", "metodo", "tiempo_ms", "repeticiones", "estado", "tiempo_total_s", "recorrido"]
METODOS_EXACTOS = ("fuerza_bruta", "held_karp")      # orden de las filas dentro de cada k
TOLERANCIA_S = 1e-6      # FB y HK suman en distinto orden: se comparan con tolerancia, no con ==
K_VERIFICACION_PREVIA = 9    # hasta este k la FB también se corre en el proceso principal


def _funcion(nombre):
    """La función se busca por nombre en el momento de usarla (así una prueba puede cambiarla)."""
    return {"fuerza_bruta": fuerza_bruta, "held_karp": held_karp}[nombre]


def _fila(k, metodo, estado, resultado=None, recorrido=""):
    """Una fila con las columnas del archivo; los campos que no aplican quedan vacíos."""
    if estado == "ok":
        return {"k": k, "metodo": metodo, "tiempo_ms": resultado.tiempo_ms,
                "repeticiones": resultado.repeticiones, "estado": estado,
                "tiempo_total_s": resultado.valor[0], "recorrido": recorrido}
    return {"k": k, "metodo": metodo, "tiempo_ms": "", "repeticiones": 0, "estado": estado,
            "tiempo_total_s": "", "recorrido": ""}


def _comprobar_igual(k, metodo, valor, referencia):
    if abs(valor - referencia) > TOLERANCIA_S:
        raise ValueError(f"k = {k}: {metodo} da {valor!r} s y la referencia de Held-Karp "
                         f"{referencia!r} s (tolerancia {TOLERANCIA_S} s)")


def medir_exactas(T, ids, s, muestra, ks=K_EXACTAS, repeticiones=5, medir=medir_en_hijo):
    """Filas (una por k y método, ninguna omitida) con los tiempos de FB y HK.

    T: lista de listas (segundos); ids[i]: id del índice i; s: índice de la partida;
    muestra: ids sorteados (la instancia de tamaño k usa los primeros k).
    """
    indice = {id_lugar: i for i, id_lugar in enumerate(ids)}
    filas = []
    sin_completar = set()                 # métodos que ya pasaron de 5 min en algún k menor
    for k in ks:
        lugares = [indice[i] for i in muestra[:k]]

        # Verificación fuera del cronómetro: Held-Karp (≤ 1 s) es la referencia de este k, y en
        # los k pequeños la fuerza bruta debe dar lo mismo ANTES de medir nada.
        referencia = held_karp(T, s, lugares)[0]
        if k <= K_VERIFICACION_PREVIA:
            _comprobar_igual(k, "fuerza_bruta (verificación previa)",
                             fuerza_bruta(T, s, lugares)[0], referencia)

        for metodo in METODOS_EXACTOS:
            if metodo in sin_completar:   # tras un "no completada" los k mayores no se intentan
                filas.append(_fila(k, metodo, "no_ejecutada"))
                continue
            resultado = medir(_funcion(metodo), (T, s, lugares), repeticiones=repeticiones,
                              devolver_valor=True)
            if not resultado.completada:
                sin_completar.add(metodo)
                filas.append(_fila(k, metodo, "no_completada"))
                continue
            # El valor que devolvió el hijo (el algoritmo medido) debe coincidir con la referencia
            _comprobar_igual(k, metodo, resultado.valor[0], referencia)
            recorrido = "-".join(ids[i] for i in resultado.valor[1])
            filas.append(_fila(k, metodo, "ok", resultado, recorrido))
        print(f"k = {k}: " + ", ".join(f"{f['metodo']} {f['estado']}"
                                       + (f" {f['tiempo_ms']:.3f} ms" if f["estado"] == "ok" else "")
                                       for f in filas[-2:]), flush=True)
    return filas


def main(matriz=MATRIZ_TIEMPOS, salida=RESULTS_R4, ks=K_EXACTAS, repeticiones=5):
    """Mide y, solo si todo salió bien, escribe r4_exactas.csv y maquina.json."""
    T, ids = matriz_a_listas(cargar_matriz(matriz))
    filas = medir_exactas(T, ids, ids.index(PARTIDA), muestra_anidada(ids), ks, repeticiones)
    salida = Path(salida)
    salida.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(filas, columns=COLUMNAS).to_csv(salida / "r4_exactas.csv", index=False)
    with open(salida / "maquina.json", "w", encoding="utf-8") as archivo:
        json.dump(info_maquina(), archivo, ensure_ascii=False, indent=2)
    print(f"Escrito {salida / 'r4_exactas.csv'}")


def _argumentos():
    parser = argparse.ArgumentParser(description="Mide fuerza bruta y Held-Karp (k = 5..12 por defecto).")
    parser.add_argument("--k-max", type=int, default=max(K_EXACTAS), help="k máximo (por defecto 12)")
    parser.add_argument("--salida", default=str(RESULTS_R4), help="carpeta de salida")
    parser.add_argument("--repeticiones", type=int, default=5)
    return parser.parse_args()


if __name__ == "__main__":
    opciones = _argumentos()
    main(salida=opciones.salida, ks=tuple(range(min(K_EXACTAS), opciones.k_max + 1)),
         repeticiones=opciones.repeticiones)

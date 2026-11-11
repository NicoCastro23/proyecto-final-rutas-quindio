"""Calidad del vecino más cercano frente al óptimo de Held-Karp (NO se cronometra).

Uso (desde la raíz del repo; ≈ 10-20 s por los Held-Karp de k = 12):
    .venv/bin/python -m rutas.r4.calidad
Escribe results/r4/r4_calidad_detalle.csv (una fila por instancia) y r4_calidad.csv (resumen por k).
"""
from pathlib import Path

import pandas as pd

from rutas.config import CATALOGO, MATRIZ_TIEMPOS, RESULTS_R4
from rutas.r2.matriz import cargar_matriz
from rutas.r4.held_karp import held_karp
from rutas.r4.instancias import PARTIDA, instancias_calidad
from rutas.r4.por_ids import matriz_a_listas
from rutas.r4.vecino import vecino_mas_cercano

COLUMNAS_DETALLE = ["k", "semilla", "optimo_s", "heuristica_s", "brecha_pct", "lugares"]
COLUMNAS = ["k", "instancias", "brecha_promedio_pct", "brecha_maxima_pct"]
TOLERANCIA_BRECHA = 1e-9    # por redondeo de las sumas, una brecha de -1e-12 no es un error


def calidad_instancias(T, ids, instancias, partida=PARTIDA):
    """Para cada instancia {"k", "semilla", "ids"}: óptimo (Held-Karp), voraz y su brecha en %.
    brecha = (voraz - óptimo) / óptimo × 100."""
    indice = {id_lugar: i for i, id_lugar in enumerate(ids)}
    s = indice[partida]
    filas = []
    for instancia in instancias:
        lugares = [indice[i] for i in instancia["ids"]]
        optimo = held_karp(T, s, lugares)[0]
        heuristica = vecino_mas_cercano(T, s, lugares)[0]
        brecha = (heuristica - optimo) / optimo * 100
        if brecha < -TOLERANCIA_BRECHA:
            # El voraz es un recorrido válido: no puede ser mejor que el óptimo. Si pasa, hay un error.
            raise ValueError(f"brecha negativa ({brecha}) en k = {instancia['k']}, "
                             f"semilla {instancia['semilla']}")
        filas.append({"k": instancia["k"], "semilla": instancia["semilla"], "optimo_s": optimo,
                      "heuristica_s": heuristica, "brecha_pct": brecha,
                      "lugares": "-".join(instancia["ids"])})
    return filas


def resumir_calidad(detalle_df):
    """Por k: número de instancias, brecha promedio y brecha máxima (formato del Anexo)."""
    grupos = detalle_df.groupby("k")["brecha_pct"]
    resumen = pd.DataFrame({"instancias": grupos.count(), "brecha_promedio_pct": grupos.mean(),
                            "brecha_maxima_pct": grupos.max()})
    return resumen.reset_index()[COLUMNAS]


def main(matriz=MATRIZ_TIEMPOS, catalogo=CATALOGO, salida=RESULTS_R4):
    T, ids = matriz_a_listas(cargar_matriz(matriz))
    if list(pd.read_csv(catalogo)["id"]) != ids:
        raise ValueError("los ids de la matriz no coinciden con los del catálogo")
    detalle = pd.DataFrame(calidad_instancias(T, ids, instancias_calidad(ids)),
                           columns=COLUMNAS_DETALLE)
    salida = Path(salida)
    salida.mkdir(parents=True, exist_ok=True)
    detalle.to_csv(salida / "r4_calidad_detalle.csv", index=False)
    resumen = resumir_calidad(detalle)
    resumen.to_csv(salida / "r4_calidad.csv", index=False)
    print(resumen.to_string(index=False))


if __name__ == "__main__":
    main()

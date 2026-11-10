"""Medición de tiempos de ox.truncate.largest_component en las 5 redes crudas (sección 6).

Uso (desde la raíz del repo):  .venv/bin/python -m rutas.r1.medir_componente

Solo se cronometra obtener_componente(G). Quedan FUERA del cronómetro: leer el GraphML,
contar V y E y copiar el grafo (cada repetición recibe una copia nueva, así ninguna
repetición usa un grafo ya procesado por la anterior). Modo (a): mismo proceso.
"""
import json
from pathlib import Path

import networkx as nx

from rutas.config import ARCHIVOS_CRUDOS, DATA_RAW, RESULTS_R1
from rutas.medicion import info_maquina, medir_en_proceso
from rutas.r1.componente import contar, obtener_componente
from rutas.r1.descarga import cargar_red_cruda

COLUMNAS = ["red", "V", "E", "V_mas_E", "tiempo_ms", "tiempo_por_elemento_us", "repeticiones"]


def fila_tiempos(nombre, V, E, resultado):
    """Una fila del CSV. tiempo_por_elemento_us = tiempo_ms * 1000 / (V + E).

    Si la medición no se completó: tiempo "no completada", sin tiempo por elemento.
    """
    if not resultado.completada:
        tiempo, por_elemento = "no completada", ""
    else:
        tiempo = resultado.tiempo_ms
        por_elemento = tiempo * 1000 / (V + E)
    return {"red": nombre, "V": V, "E": E, "V_mas_E": V + E, "tiempo_ms": tiempo,
            "tiempo_por_elemento_us": por_elemento, "repeticiones": resultado.repeticiones}


def preparar_copia(G):
    """Función sin argumentos que da (copia de G,): se llama fuera del cronómetro."""
    def preparar():
        return (G.copy(),)
    return preparar


def main(raw=DATA_RAW, salida=RESULTS_R1):
    import pandas as pd

    raw, salida = Path(raw), Path(salida)
    salida.mkdir(parents=True, exist_ok=True)

    filas = []
    for nombre, archivo in ARCHIVOS_CRUDOS.items():
        G = cargar_red_cruda(raw / archivo)             # fuera del cronómetro
        V, E = contar(G)                                # fuera del cronómetro
        ya_conexa = nx.is_strongly_connected(G)         # solo informativo, fuera del cronómetro
        resultado = medir_en_proceso(obtener_componente, preparar_copia(G))
        filas.append(fila_tiempos(nombre, V, E, resultado))
        print(f"{nombre}: V={V} E={E} mediana={resultado.tiempo_ms} ms "
              f"({resultado.repeticiones} rep.) ya fuertemente conexa: {ya_conexa}")

    pd.DataFrame(filas, columns=COLUMNAS).to_csv(salida / "r1_tiempos_componente.csv", index=False)
    (salida / "maquina.json").write_text(
        json.dumps(info_maquina(), indent=2, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()

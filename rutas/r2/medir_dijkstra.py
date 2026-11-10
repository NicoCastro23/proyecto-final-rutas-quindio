"""Medición de tiempos de Dijkstra en 20 pares de lugares (R2, sección 6).

Uso (desde la raíz del repo, con el portátil enchufado):  .venv/bin/python -m rutas.r2.medir_dijkstra

Solo se cronometra la llamada dijkstra_*(adyacencia, i_origen, i_destino). Quedan FUERA del
cronómetro: leer el grafo y los CSV, construir la adyacencia, elegir los pares, traducir ids a
índices, la corrida con `consultar` que da tiempo/explorados/ruta, detalle_ruta y escribir archivos.
La cola se mide en este proceso (modo a) en los 20 pares; la lineal en un proceso hijo (modo b,
límite de 5 min) solo en los 10 cercanos.
"""
import json
from pathlib import Path

import pandas as pd

from rutas.config import CATALOGO, DATA_PROCESSED, RESULTS_R2
from rutas.medicion import info_maquina, medir_en_hijo, medir_en_proceso
from rutas.r1.persistencia import cargar_grafo_procesado, cargar_lugares_nodos
from rutas.r2.adyacencia import construir_adyacencia
from rutas.r2.dijkstra import consultar, dijkstra_cola, dijkstra_lineal
from rutas.r2.pares import SEMILLA, seleccionar_pares
from rutas.r2.ruta import detalle_ruta

# Las 6 columnas del Anexo primero; luego las ampliadas (tipo, distancia_m, repeticiones)
COLUMNAS = ["origen", "destino", "version", "tiempo_viaje_s", "nodos_explorados", "tiempo_ms",
            "tipo", "distancia_m", "repeticiones"]
TOLERANCIA_S = 1e-6
REGLA = ("10 pares 'cercano' (mismo municipio, un par por municipio por vuelta, municipios "
         "ordenados y barajados) y 10 'lejano' (municipios distintos, al azar); pares ordenados, "
         "sin repetir y con nodos distintos")


def fila(par, version, tiempo_s, explorados, resultado, distancia_m):
    """Una fila del CSV. Si la medición no se completó, tiempo_ms = "no completada"."""
    tiempo_ms = resultado.tiempo_ms if resultado.completada else "no completada"
    return {"origen": par.origen, "destino": par.destino, "version": version,
            "tiempo_viaje_s": tiempo_s, "nodos_explorados": explorados, "tiempo_ms": tiempo_ms,
            "tipo": par.tipo, "distancia_m": distancia_m, "repeticiones": resultado.repeticiones}


def _comprobar_versiones(red, pares):
    """Antes de medir nada: en los pares cercanos lineal y cola deben dar lo mismo.

    Si no, se aborta: no se miden ni se guardan resultados de algo incorrecto.
    """
    for par in pares[pares.tipo == "cercano"].itertuples():
        t_c, _, k_c = consultar(red, par.nodo_origen, par.nodo_destino, "cola_prioridad")
        t_l, _, k_l = consultar(red, par.nodo_origen, par.nodo_destino, "lineal")
        if abs(t_l - t_c) > TOLERANCIA_S or k_l != k_c:
            # Error explícito (no assert): sigue funcionando aunque Python corra con -O
            raise ValueError(
                f"las versiones difieren en el par {par.origen}->{par.destino}: "
                f"lineal ({t_l} s, {k_l} explorados) vs cola ({t_c} s, {k_c} explorados)")


def _argumentos(red, i_o, i_d):
    """Función sin argumentos que da (adyacencia, origen, destino) para medir_en_proceso.
    Es una función aparte (y no un lambda en el ciclo) para que cada par conserve sus índices."""
    return lambda: (red.adyacencia, i_o, i_d)


def medir_pares(G, red, pares, repeticiones=5, medir_cola=medir_en_proceso, medir_lineal=medir_en_hijo):
    """Filas del CSV: por par, primero la cola y, si es cercano, después la lineal (30 filas)."""
    _comprobar_versiones(red, pares)
    filas = []
    for numero, par in enumerate(pares.itertuples(), start=1):
        i_o, i_d = red.indice[par.nodo_origen], red.indice[par.nodo_destino]
        # Corrida fuera del cronómetro: de aquí salen tiempo de viaje, explorados y distancia
        tiempo_s, ruta, explorados = consultar(red, par.nodo_origen, par.nodo_destino)
        distancia_m = detalle_ruta(G, ruta)[1]

        resultado = medir_cola(dijkstra_cola, _argumentos(red, i_o, i_d),
                               repeticiones=repeticiones)
        filas.append(fila(par, "cola_prioridad", tiempo_s, explorados, resultado, distancia_m))
        if par.tipo == "cercano":
            # Cada fila sale de su propia versión: la lineal se corre aparte (fuera del cronómetro)
            tiempo_l, _, explorados_l = consultar(red, par.nodo_origen, par.nodo_destino, "lineal")
            resultado = medir_lineal(dijkstra_lineal, (red.adyacencia, i_o, i_d),
                                     repeticiones=repeticiones)
            filas.append(fila(par, "lineal", tiempo_l, explorados_l, resultado, distancia_m))
        print(f"[{numero}/{len(pares)}] {par.origen}->{par.destino} ({par.tipo}): "
              f"{explorados} explorados, " + ", ".join(
                  f"{f['version']} {f['tiempo_ms']} ms" for f in filas[-2 if par.tipo == 'cercano' else -1:]),
              flush=True)
    return filas


def main(processed=DATA_PROCESSED, catalogo=CATALOGO, salida=RESULTS_R2, repeticiones=5):
    G = cargar_grafo_procesado(processed)
    red = construir_adyacencia(G)
    pares = seleccionar_pares(pd.read_csv(catalogo), cargar_lugares_nodos(processed))

    filas = medir_pares(G, red, pares, repeticiones)    # si las versiones difieren, aborta aquí

    salida = Path(salida)
    salida.mkdir(parents=True, exist_ok=True)
    pares.to_csv(salida / "r2_pares.csv", index=False)
    (salida / "r2_pares.json").write_text(json.dumps(
        {"semilla": SEMILLA, "generador": "random.Random", "cercanos": 10, "lejanos": 10,
         "regla": REGLA}, indent=2, ensure_ascii=False), encoding="utf-8")
    pd.DataFrame(filas, columns=COLUMNAS).to_csv(salida / "r2_dijkstra.csv", index=False)
    (salida / "maquina.json").write_text(
        json.dumps(info_maquina(), indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Resultados escritos en {salida}")


if __name__ == "__main__":
    main()

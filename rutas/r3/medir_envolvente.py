"""Medición de la envolvente convexa: QuickHull propio contra SciPy (R3, sección 6).

Uso (desde la raíz del repo, con el portátil enchufado):  .venv/bin/python -m rutas.r3.medir_envolvente

Solo se cronometra envolvente(puntos) y ConvexHull(arreglo). Quedan FUERA del cronómetro: leer el
grafo, generar y preparar los puntos (redondear, quitar repetidos), convertir la lista a un arreglo
de NumPy, la comprobación previa contra SciPy, contar los vértices y escribir archivos.
"""
import json
from pathlib import Path

import numpy
import pandas as pd
from scipy.spatial import ConvexHull

from rutas.config import DATA_PROCESSED, RESULTS_R3
from rutas.medicion import info_maquina, medir_en_proceso
from rutas.r1.persistencia import cargar_grafo_procesado
from rutas.r3.envolvente import envolvente, normalizar
from rutas.r3.puntos import LADO, SEMILLA, puntos_cuadrado, puntos_de_grafo
from rutas.r3.referencia import vertices_scipy

TAMANOS = (1_000, 10_000, 50_000)
# Las 6 columnas del Anexo primero; luego la ampliada (repeticiones)
COLUMNAS = ["conjunto", "n", "vertices", "tiempo_propio_ms", "tiempo_scipy_ms", "cociente",
            "repeticiones"]
NOMBRE_RED = "Nodos de la red"


def nombre_cuadrado(n):
    """"Cuadrado, 1 000 puntos": el Anexo separa los miles con un espacio."""
    return "Cuadrado, " + f"{n:,}".replace(",", " ") + " puntos"


def conjuntos(puntos_red, semilla=SEMILLA, tamanos=TAMANOS):
    """[(nombre, n_pedido, puntos)] en el orden del Anexo: primero la red y luego los cuadrados.

    Para la red, n_pedido es el número de puntos distintos de la red.
    """
    lista = [(NOMBRE_RED, len(puntos_red), puntos_red)]
    for n in tamanos:
        lista.append((nombre_cuadrado(n), n, puntos_cuadrado(n, semilla)))
    return lista


def comprobar_iguales(lista):
    """Antes de medir: la envolvente propia debe tener los mismos vértices que la de SciPy.

    Si no, se aborta: no se mide ni se guarda nada de algo incorrecto. Error explícito (no assert).
    """
    for nombre, _, puntos in lista:
        propios = envolvente(puntos)
        referencia = vertices_scipy(puntos)
        if set(propios) != set(referencia) or normalizar(propios) != referencia:
            raise ValueError(f"{nombre}: la envolvente propia ({len(propios)} vértices) difiere de "
                             f"SciPy ({len(referencia)} vértices); no se mide ni se escribe nada")


def medir_conjunto(nombre, puntos, repeticiones=5, medir=medir_en_proceso):
    """Una fila del CSV: tiempos (mediana, ms) de la envolvente propia y de SciPy sobre los mismos puntos."""
    arreglo = numpy.array(puntos, dtype=numpy.float64)      # conversión a NumPy: fuera del cronómetro
    propio = medir(envolvente, lambda: (puntos,), repeticiones=repeticiones)
    scipy = medir(ConvexHull, lambda: (arreglo,), repeticiones=repeticiones)
    if propio.completada and scipy.completada:
        propio_ms, scipy_ms = propio.tiempo_ms, scipy.tiempo_ms
        cociente = propio_ms / scipy_ms
    else:
        propio_ms = propio.tiempo_ms if propio.completada else "no completada"
        scipy_ms = scipy.tiempo_ms if scipy.completada else "no completada"
        cociente = "no completada"
    return {"conjunto": nombre, "n": len(puntos), "vertices": len(envolvente(puntos)),
            "tiempo_propio_ms": propio_ms, "tiempo_scipy_ms": scipy_ms, "cociente": cociente,
            "repeticiones": min(propio.repeticiones, scipy.repeticiones)}


def main(processed=DATA_PROCESSED, salida=RESULTS_R3, repeticiones=5):
    lista = conjuntos(puntos_de_grafo(cargar_grafo_procesado(processed)), tamanos=TAMANOS)
    comprobar_iguales(lista)                    # si difieren, aborta aquí y no se escribe nada

    filas = []
    for nombre, _, puntos in lista:
        filas.append(medir_conjunto(nombre, puntos, repeticiones))
        f = filas[-1]
        print(f"{nombre}: n={f['n']}, {f['vertices']} vértices, propia {f['tiempo_propio_ms']} ms, "
              f"SciPy {f['tiempo_scipy_ms']} ms", flush=True)

    salida = Path(salida)
    salida.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(filas, columns=COLUMNAS).to_csv(salida / "r3_envolvente.csv", index=False)
    (salida / "r3_puntos.json").write_text(json.dumps({
        "semilla": SEMILLA, "generador": "random.Random", "lado": LADO,
        "cuadrado": "[0, lado) x [0, lado), enteros, metros", "redondeo": "math.floor(x + 0.5)",
        "nota": "cada cuadrado usa su propio Random(2026): los conjuntos no comparten el flujo de azar",
        "conjuntos": [{"conjunto": nombre, "n_pedido": pedido, "n_obtenido": len(puntos)}
                      for nombre, pedido, puntos in lista]}, indent=2, ensure_ascii=False),
        encoding="utf-8")
    (salida / "maquina.json").write_text(
        json.dumps(info_maquina(), indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Resultados escritos en {salida}")


if __name__ == "__main__":
    main()

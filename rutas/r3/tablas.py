"""Gráfica (y, más adelante, tablas) de R3, generadas desde los archivos.

Uso de la gráfica:  .venv/bin/python -c "from rutas.r3.tablas import grafica_envolvente; print(grafica_envolvente())"
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")           # sin ventana: la gráfica solo se guarda en un archivo
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

from rutas.config import DATA_PROCESSED, RESULTS_R3  # noqa: E402
from rutas.r1.persistencia import cargar_grafo_procesado  # noqa: E402
from rutas.r3.envolvente import area  # noqa: E402
from rutas.r3.puntos import puntos_de_grafo  # noqa: E402


def grafica_envolvente(processed=DATA_PROCESSED, salida=RESULTS_R3):
    """Nodos de la red y polígono de la envolvente, en metros UTM. Devuelve la ruta del PNG."""
    puntos = puntos_de_grafo(cargar_grafo_procesado(processed))
    tabla = pd.read_csv(Path(processed) / "envolvente.csv")
    vertices = list(zip(tabla["x_utm"], tabla["y_utm"]))
    area_km2 = area(vertices) / 1e6

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.scatter([x for x, _ in puntos], [y for _, y in puntos], s=2, color="gray", label="Nodos de la red")
    cerrado = vertices + vertices[:1]               # se repite el primero para cerrar el polígono
    ax.plot([x for x, _ in cerrado], [y for _, y in cerrado], color="red", marker="o", markersize=4,
            label="Envolvente convexa")
    ax.set_xlabel("x UTM (m)")
    ax.set_ylabel("y UTM (m)")
    ax.set_aspect("equal")                          # 1 m en x = 1 m en y: el polígono no se deforma
    ax.set_title(f"Envolvente convexa: {len(puntos)} nodos, {len(vertices)} vértices, "
                 f"área {area_km2:.1f} km²")
    ax.legend(loc="upper left")

    salida = Path(salida)
    salida.mkdir(parents=True, exist_ok=True)
    ruta = salida / "r3_envolvente.png"
    fig.savefig(ruta, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return ruta

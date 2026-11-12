"""Carga única de los datos de la aplicación (se llama una sola vez al arrancar)."""
import json
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from rutas.config import CATALOGO, DATA_PROCESSED, ENVOLVENTE_GEOJSON, MATRIZ_TIEMPOS
from rutas.r1.persistencia import cargar_grafo_procesado, cargar_lugares_nodos
from rutas.r2.adyacencia import construir_adyacencia
from rutas.r2.matriz import cargar_matriz

CATEGORIA_ATRACTIVO = "Atractivo turístico"


class DatosFaltantes(Exception):
    """El mensaje nombra cada archivo faltante y el comando que lo genera."""


@dataclass(frozen=True)
class DatosApp:
    """Todo lo que las peticiones necesitan. Es inmutable: ninguna petición la cambia."""
    G: object            # MultiDiGraph de R1 (para detalle_ruta y mejor_arista)
    red: object          # Red de R2 (adyacencia indexada)
    catalogo: object     # DataFrame de data/catalogo.csv (orden del catálogo)
    nodo_de: dict        # {id_lugar: id_nodo int}
    nombre_de: dict      # {id_lugar: nombre}
    matriz: object       # DataFrame ids x ids en segundos (R2)
    envolvente: dict     # GeoJSON leído con json
    atractivos: list     # ids con categoría "Atractivo turístico", en orden del catálogo
    visita_min: dict     # {id_atractivo: minutos (float)}


COMANDOS_DATOS = {       # archivo -> comando que lo genera
    "grafo_componente.graphml": ".venv/bin/python -m rutas.r1.construir_red",
    "lugares_nodos.csv": ".venv/bin/python -m rutas.r1.construir_red",
    "matriz_tiempos.csv": ".venv/bin/python -m rutas.r2.matriz",
    "envolvente.geojson": ".venv/bin/python -m rutas.r3.archivos",
    "catalogo.csv": "está en el repositorio: restaurarlo con git",
}


def archivos_faltantes(processed, catalogo):
    """[(ruta, comando)] de los archivos que no existen, en el orden de COMANDOS_DATOS.

    El grafo cuenta como presente si está como .graphml o como .graphml.gz (R1 lo comprime
    cuando pasa del umbral de GitHub).
    """
    processed = Path(processed)
    faltan = []
    for nombre, comando in COMANDOS_DATOS.items():
        if nombre == "catalogo.csv":
            ruta = Path(catalogo)
            existe = ruta.exists()
        else:
            ruta = processed / nombre
            existe = ruta.exists() or (nombre.endswith(".graphml") and Path(str(ruta) + ".gz").exists())
        if not existe:
            faltan.append((ruta, comando))
    return faltan


def cargar_datos(processed=DATA_PROCESSED, catalogo=CATALOGO):
    """Lee todo una vez y devuelve DatosApp; si falta algo, lanza DatosFaltantes.

    El mensaje trae una línea por archivo faltante: "falta <ruta>: <comando>".
    """
    faltan = archivos_faltantes(processed, catalogo)
    if faltan:
        raise DatosFaltantes("\n".join(f"falta {ruta}: {comando}" for ruta, comando in faltan))
    processed = Path(processed)

    G = cargar_grafo_procesado(processed)
    red = construir_adyacencia(G)
    lugares = cargar_lugares_nodos(processed)
    # id_nodo llega como numpy.int64; se pasa a int para no arrastrar tipos de NumPy
    nodo_de = {fila.id_lugar: int(fila.id_nodo) for fila in lugares.itertuples()}
    catalogo_df = pd.read_csv(catalogo)
    es_atractivo = catalogo_df["categoria"] == CATEGORIA_ATRACTIVO
    atractivos = list(catalogo_df.loc[es_atractivo, "id"])
    visita_min = {fila.id: float(fila.duracion_visita_min)
                  for fila in catalogo_df[es_atractivo].itertuples()}
    envolvente = json.loads((processed / ENVOLVENTE_GEOJSON.name).read_text(encoding="utf-8"))
    return DatosApp(
        G=G, red=red, catalogo=catalogo_df, nodo_de=nodo_de,
        nombre_de=dict(zip(catalogo_df["id"], catalogo_df["nombre"])),
        matriz=cargar_matriz(processed / MATRIZ_TIEMPOS.name),
        envolvente=envolvente, atractivos=atractivos, visita_min=visita_min)

"""Guardar y cargar el grafo procesado, las asociaciones y los metadatos.

Nada se redondea: OSMnx escribe cada float con str(), que da la representación más corta
que vuelve a leerse exactamente igual, y pandas.to_csv sin float_format hace lo mismo.
Si el .graphml pasa del umbral (100 MB por el límite de GitHub) se guarda comprimido
como .graphml.gz; nunca quedan las dos formas en la carpeta.
"""
import gzip
import json
import shutil
from pathlib import Path

import osmnx as ox
import pandas as pd

from rutas.config import DATA_PROCESSED, UMBRAL_GZ_BYTES

NOMBRE_GRAFO = "grafo_componente.graphml"      # la forma comprimida es NOMBRE_GRAFO + ".gz"
NOMBRE_LUGARES = "lugares_nodos.csv"
NOMBRE_METADATOS = "metadatos.json"


def _texto_a_bool(valor):
    """GraphML guarda los booleanos como "True"/"False"; bool("False") sería True, por eso
    se compara el texto."""
    if isinstance(valor, bool):
        return valor
    return str(valor).strip().lower() == "true"


def _comprimir(origen, destino):
    """gzip del archivo origen. mtime=0 evita escribir la fecha en el encabezado, así dos
    corridas iguales dan el mismo .gz byte a byte (y git no ve cambios falsos)."""
    with open(origen, "rb") as entrada, open(destino, "wb") as crudo:
        with gzip.GzipFile(filename="", fileobj=crudo, mode="wb", mtime=0) as salida:
            shutil.copyfileobj(entrada, salida)


def guardar_grafo(G, carpeta, umbral_bytes=UMBRAL_GZ_BYTES):
    """Guarda G en carpeta; devuelve la ruta del archivo que quedó (.graphml o .graphml.gz)."""
    carpeta = Path(carpeta)
    carpeta.mkdir(parents=True, exist_ok=True)
    plano = carpeta / NOMBRE_GRAFO
    comprimido = carpeta / (NOMBRE_GRAFO + ".gz")

    ox.save_graphml(G, plano)
    if plano.stat().st_size > umbral_bytes:
        _comprimir(plano, comprimido)
        plano.unlink()
        return comprimido
    comprimido.unlink(missing_ok=True)      # un .gz viejo dejaría las dos formas
    return plano


def cargar_grafo_procesado(carpeta=DATA_PROCESSED):
    """Carga el grafo desde la carpeta, esté como .graphml o como .graphml.gz."""
    carpeta = Path(carpeta)
    plano = carpeta / NOMBRE_GRAFO
    comprimido = carpeta / (NOMBRE_GRAFO + ".gz")
    if plano.exists() and comprimido.exists():
        raise ValueError(f"hay dos formas del grafo en {carpeta}; deje solo una")
    if not plano.exists() and not comprimido.exists():
        raise FileNotFoundError(f"no hay {NOMBRE_GRAFO}[.gz] en {carpeta}")

    # Los atributos propios de R1 no están en los tipos por defecto de OSMnx.
    tipos = dict(node_dtypes={"x_utm": float, "y_utm": float},
                 edge_dtypes={"maxspeed_original": _texto_a_bool})
    if plano.exists():
        return ox.load_graphml(plano, **tipos)
    with gzip.open(comprimido, "rt", encoding="utf-8") as archivo:
        return ox.load_graphml(graphml_str=archivo.read(), **tipos)


def guardar_procesado(G, lugares, metadatos, carpeta=DATA_PROCESSED, umbral_bytes=UMBRAL_GZ_BYTES):
    """Guarda grafo, lugares_nodos.csv y metadatos.json. Devuelve la ruta del grafo."""
    carpeta = Path(carpeta)
    ruta = guardar_grafo(G, carpeta, umbral_bytes)
    lugares.to_csv(carpeta / NOMBRE_LUGARES, index=False)
    metadatos = dict(metadatos, archivo_grafo=ruta.name, comprimido=ruta.suffix == ".gz")
    (carpeta / NOMBRE_METADATOS).write_text(
        json.dumps(metadatos, indent=2, ensure_ascii=False), encoding="utf-8")
    return ruta


def cargar_lugares_nodos(carpeta=DATA_PROCESSED):
    """id_nodo int, distancia_al_nodo_m float, alerta_500m bool."""
    return pd.read_csv(Path(carpeta) / NOMBRE_LUGARES,
                       dtype={"id_nodo": "int64", "distancia_al_nodo_m": "float64"},
                       float_precision="round_trip",   # lee el float exactamente como se guardó
                       converters={"alerta_500m": _texto_a_bool})


def cargar_metadatos(carpeta=DATA_PROCESSED):
    return json.loads((Path(carpeta) / NOMBRE_METADATOS).read_text(encoding="utf-8"))

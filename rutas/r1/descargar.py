"""Script de descarga: baja las 5 redes crudas a data/raw/ y escribe descarga.json.

Uso (desde la raíz del repo):  .venv/bin/python -m rutas.r1.descargar
Las respuestas buenas quedan en la caché de OSMnx (cache/), así que repetir el script
no vuelve a descargar lo que ya llegó. Si OSMnx se queda mostrando reintentos cada 55 s
(504/429 de Overpass), corte con Ctrl+C y reintente más tarde o use el Plan B (--graphml
en rutas.r1.construir_red).
"""
import json
import logging
import platform
import time
from datetime import datetime
from pathlib import Path

import networkx as nx
import osmnx as ox

from rutas.config import ARCHIVOS_CRUDOS, DATA_RAW, RADIOS_M
from rutas.r1 import descarga

LOG = logging.getLogger("rutas.r1.descargar")


def _guardar(G, carpeta, nombre, etiqueta):
    ox.save_graphml(G, Path(carpeta) / nombre)
    LOG.info("Red descargada: %s -> %s (%s nodos, %s aristas)",
             etiqueta, nombre, G.number_of_nodes(), G.number_of_edges())


def main(carpeta=DATA_RAW, dormir=time.sleep):
    """Descarga y guarda las 5 redes. Cada una tiene sus propios reintentos."""
    carpeta = Path(carpeta)
    carpeta.mkdir(parents=True, exist_ok=True)

    LOG.info("Geocodificando el polígono de '%s'...", descarga.LUGAR)
    poligono = descarga.comprobar_poligono_departamento(
        descarga.geocodificar_departamento(dormir))
    LOG.info("Polígono correcto: %s", poligono)

    LOG.info("Descargando el departamento completo (puede tardar varios minutos)...")
    G = descarga.descargar_departamento(dormir)
    _guardar(G, carpeta, ARCHIVOS_CRUDOS["Departamento completo"], "Departamento completo")

    for radio in RADIOS_M:
        etiqueta = f"Radio de {radio // 1000} km"
        LOG.info("Descargando %s...", etiqueta)
        G = descarga.descargar_radio(radio, dormir)
        _guardar(G, carpeta, ARCHIVOS_CRUDOS[etiqueta], etiqueta)

    latitud, longitud = descarga.centro_plaza_bolivar()
    info = {
        "fecha_descarga": datetime.now().astimezone().isoformat(timespec="seconds"),
        "versiones": {"osmnx": ox.__version__, "networkx": nx.__version__,
                      "python": platform.python_version()},
        "parametros": {**descarga.PARAMETROS, "dist_type": "bbox", "lugar": descarga.LUGAR,
                       "radios_m": list(RADIOS_M)},
        "centro": {"lugar": "C01", "latitud": latitud, "longitud": longitud},
        "poligono": poligono,
    }
    (carpeta / "descarga.json").write_text(
        json.dumps(info, indent=2, ensure_ascii=False), encoding="utf-8")
    LOG.info("Listo: %s", carpeta / "descarga.json")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s", datefmt="%H:%M:%S")
    main()

"""Pipeline de R1: red cruda -> pesos -> componente fuertemente conexa -> lugares -> archivos.

Uso (desde la raíz del repo):
    .venv/bin/python -m rutas.r1.construir_red                      # usa data/raw/departamento.graphml
    .venv/bin/python -m rutas.r1.construir_red --graphml RUTA       # Plan B: GraphML del docente
"""
import argparse
import json
from pathlib import Path

import networkx as nx
import osmnx as ox
import pandas as pd

from rutas.config import (ARCHIVOS_CRUDOS, CATALOGO, DATA_PROCESSED, DATA_RAW, RESULTS_R1,
                          UMBRAL_GZ_BYTES)
from rutas.r1.catalogo import cargar_catalogo
from rutas.r1.componente import contar, obtener_componente
from rutas.r1.descarga import cargar_red_cruda
from rutas.r1.memoria import filas_memoria
from rutas.r1.persistencia import guardar_procesado
from rutas.r1.pesos import agregar_pesos, resumen_velocidades
from rutas.r1.ubicacion import ubicar_lugares
from rutas.r1.utm import agregar_utm_a_nodos

RED_ANTES = "Red descargada"
RED_DESPUES = "Componente fuertemente conexa"


def _leer_descarga_json(raw):
    """Datos de la descarga (fecha, parámetros) si el script de descarga los dejó en raw/."""
    ruta = Path(raw) / "descarga.json"
    if ruta.exists():
        return json.loads(ruta.read_text(encoding="utf-8"))
    return {}


def main(raw=DATA_RAW, graphml=None, catalogo=CATALOGO, salida_processed=DATA_PROCESSED,
         salida_results=RESULTS_R1, umbral_gz=UMBRAL_GZ_BYTES):
    salida_results = Path(salida_results)
    salida_results.mkdir(parents=True, exist_ok=True)

    # 1. Red cruda: la descargada o el GraphML del docente (Plan B).
    if graphml is not None:
        G = cargar_red_cruda(graphml)
        descarga = {}
        fuente = "GraphML del docente"
    else:
        G = cargar_red_cruda(Path(raw) / ARCHIVOS_CRUDOS["Departamento completo"])
        descarga = _leer_descarga_json(raw)
        fuente = "OSMnx (Overpass)"
    lugares_catalogo = cargar_catalogo(catalogo)

    # 2. Pesos, componente y coordenadas UTM. Los pesos van antes para medir el grafo completo.
    agregar_pesos(G)
    V_antes, E_antes = contar(G)
    componente = obtener_componente(G)
    V_despues, E_despues = contar(componente)
    agregar_utm_a_nodos(componente)

    # 3. Lugares sobre la componente (los alertados se conservan).
    lugares = ubicar_lugares(lugares_catalogo, componente)

    # 4. Guardar grafo, lugares y metadatos.
    metadatos = {
        "fuente": fuente,
        "fecha_descarga": descarga.get("fecha_descarga"),
        "versiones": {"osmnx": ox.__version__, "networkx": nx.__version__},
        "parametros_descarga": descarga.get("parametros"),
        "poligono": descarga.get("poligono"),
        "V_antes": V_antes, "E_antes": E_antes,
        "V_despues": V_despues, "E_despues": E_despues,
    }
    ruta_grafo = guardar_procesado(componente, lugares, metadatos, salida_processed,
                                   umbral_bytes=umbral_gz)

    # 5. Tablas del informe (los CSV son la fuente; las tablas Markdown salen de ellos).
    pd.DataFrame([{"red": RED_ANTES, "nodos": V_antes, "aristas": E_antes},
                  {"red": RED_DESPUES, "nodos": V_despues, "aristas": E_despues}]
                 ).to_csv(salida_results / "r1_tamanos.csv", index=False)
    pd.DataFrame(filas_memoria(RED_ANTES, V_antes, E_antes)
                 + filas_memoria(RED_DESPUES, V_despues, E_despues)
                 ).to_csv(salida_results / "r1_memoria.csv", index=False)
    # Solo el CSV (tabla de resumen) se redondea a 1 decimal; los pesos del grafo no.
    resumen = resumen_velocidades(componente).round({"pct_osm": 1, "pct_imputado": 1})
    resumen["velocidad_tabla_kmh"] = resumen["velocidad_tabla_kmh"].astype("Int64")  # 20, no 20.0
    resumen.to_csv(salida_results / "r1_velocidades.csv", index=False)

    # 6. Resumen en pantalla.
    print(f"Red descargada: {V_antes} nodos, {E_antes} aristas")
    print(f"Componente fuertemente conexa: {V_despues} nodos, {E_despues} aristas")
    for _, fila in lugares[lugares["alerta_500m"]].iterrows():
        print(f"ALERTA >500 m: {fila['id_lugar']} a {fila['distancia_al_nodo_m']:.0f} m de su nodo")
    tamano_mb = ruta_grafo.stat().st_size / 1e6
    comprimido = "comprimido" if ruta_grafo.suffix == ".gz" else "sin comprimir"
    print(f"Grafo guardado: {ruta_grafo} ({tamano_mb:.1f} MB, {comprimido})")


if __name__ == "__main__":
    analizador = argparse.ArgumentParser(description="Construye la red de R1 desde la red cruda.")
    analizador.add_argument("--graphml", help="Plan B: ruta a un GraphML entregado por el docente")
    main(graphml=analizador.parse_args().graphml)

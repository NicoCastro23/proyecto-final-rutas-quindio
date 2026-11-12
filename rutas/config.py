"""Rutas y constantes compartidas. Todas las rutas son relativas a la raíz del repo."""
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

DATA_RAW = RAIZ / "data" / "raw"
DATA_PROCESSED = RAIZ / "data" / "processed"
RESULTS_R1 = RAIZ / "results" / "r1"
RESULTS_R2 = RAIZ / "results" / "r2"
RESULTS_R3 = RAIZ / "results" / "r3"
RESULTS_R4 = RAIZ / "results" / "r4"
MATRIZ_TIEMPOS = DATA_PROCESSED / "matriz_tiempos.csv"
ENVOLVENTE_CSV = DATA_PROCESSED / "envolvente.csv"
ENVOLVENTE_GEOJSON = DATA_PROCESSED / "envolvente.geojson"
CATALOGO = RAIZ / "data" / "catalogo.csv"

EPSG_UTM = 32618                    # UTM zona 18N (el Quindío está en la zona 18)
UMBRAL_ALERTA_M = 500               # un lugar a más de 500 m de su nodo se alerta
RADIOS_M = (2000, 5000, 10000, 20000)
UMBRAL_GZ_BYTES = 100_000_000       # GitHub rechaza archivos de más de 100 MB

# Nombres de las redes crudas en data/raw/ (el orden es el de la tabla de tiempos)
ARCHIVOS_CRUDOS = {
    "Radio de 2 km": "radio_2km.graphml",
    "Radio de 5 km": "radio_5km.graphml",
    "Radio de 10 km": "radio_10km.graphml",
    "Radio de 20 km": "radio_20km.graphml",
    "Departamento completo": "departamento.graphml",
}

# R5: aplicación web local
RESULTS = RAIZ / "results"          # RESULTS_R1..R4 son las subcarpetas r1..r4
HOST_R5 = "127.0.0.1"
PUERTO_R5 = 5050                    # el 5000 lo ocupa AirPlay en macOS

"""Archivos de la envolvente de la red para R5 (no es una medición de tiempo).

Uso (desde la raíz del repo):  .venv/bin/python -m rutas.r3.archivos
Escribe data/processed/envolvente.csv y data/processed/envolvente.geojson.
"""
import csv
import json
from pathlib import Path

from rutas.config import DATA_PROCESSED
from rutas.r1.persistencia import cargar_grafo_procesado
from rutas.r1.utm import a_latlon
from rutas.r3.envolvente import area, envolvente, normalizar
from rutas.r3.puntos import puntos_de_grafo
from rutas.r3.referencia import vertices_scipy


def escribir_envolvente(vertices, carpeta=DATA_PROCESSED):
    """Escribe envolvente.csv y envolvente.geojson; devuelve sus rutas.

    Los vértices vienen en sentido antihorario (como pide el GeoJSON, RFC 7946) y el GeoJSON
    repite el primero al final para cerrar el anillo. Coordenadas del GeoJSON: [lon, lat].
    """
    carpeta = Path(carpeta)
    carpeta.mkdir(parents=True, exist_ok=True)
    lons, lats = a_latlon([x for x, _ in vertices], [y for _, y in vertices])
    lons, lats = [float(v) for v in lons], [float(v) for v in lats]

    ruta_csv = carpeta / "envolvente.csv"
    with open(ruta_csv, "w", newline="", encoding="utf-8") as f:
        escritor = csv.writer(f, lineterminator="\n")
        escritor.writerow(["orden", "x_utm", "y_utm", "lat", "lon"])
        for orden, ((x, y), lat, lon) in enumerate(zip(vertices, lats, lons), start=1):
            escritor.writerow([orden, x, y, repr(lat), repr(lon)])

    anillo = [[lon, lat] for lon, lat in zip(lons, lats)]
    anillo.append(anillo[0])
    geojson = {"type": "FeatureCollection", "features": [{
        "type": "Feature",
        "properties": {"vertices": len(vertices), "area_km2": area(vertices) / 1e6},
        "geometry": {"type": "Polygon", "coordinates": [anillo]},
    }]}
    ruta_geojson = carpeta / "envolvente.geojson"
    ruta_geojson.write_text(json.dumps(geojson, indent=2), encoding="utf-8")
    return ruta_csv, ruta_geojson


def main(processed=DATA_PROCESSED):
    """Envolvente de la red procesada. Si SciPy no da los mismos vértices, no escribe nada."""
    puntos = puntos_de_grafo(cargar_grafo_procesado(processed))
    vertices = envolvente(puntos)
    referencia = vertices_scipy(puntos)
    if set(vertices) != set(referencia) or normalizar(vertices) != referencia:
        raise ValueError(f"la envolvente propia ({len(vertices)} vértices) difiere de SciPy "
                         f"({len(referencia)} vértices); no se escriben archivos")
    escribir_envolvente(vertices, processed)
    print(f"{len(vertices)} vértices, área {area(vertices) / 1e6:.3f} km2")


if __name__ == "__main__":
    main()

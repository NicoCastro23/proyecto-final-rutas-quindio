"""Pruebas de rutas/r3/archivos.py (caso 17): archivos de la envolvente para R5."""
import csv
import json

import pytest

from rutas.r1.utm import a_utm
from rutas.r3 import archivos
from rutas.r3.archivos import escribir_envolvente, main
from rutas.r3.envolvente import area
from tests.conftest import carpeta_sintetica

# Cuadrilátero antihorario en coordenadas UTM del Quindío
VERTICES = [(420_000, 500_000), (430_000, 501_000), (429_000, 510_000), (419_500, 508_000)]


def leer_csv(ruta):
    with open(ruta, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def comprobar_archivos(csv_ruta, geojson_ruta, vertices):
    """Caso 17: polígono cerrado y ida y vuelta UTM -> lat/lon -> UTM con error < 1 m."""
    filas = leer_csv(csv_ruta)
    assert open(csv_ruta, encoding="utf-8").readline().strip() == "orden,x_utm,y_utm,lat,lon"
    assert [int(f["orden"]) for f in filas] == list(range(1, len(vertices) + 1))
    assert [(int(f["x_utm"]), int(f["y_utm"])) for f in filas] == vertices
    gj = json.loads(geojson_ruta.read_text(encoding="utf-8"))
    assert gj["type"] == "FeatureCollection" and len(gj["features"]) == 1
    feature = gj["features"][0]
    assert feature["geometry"]["type"] == "Polygon"
    anillo = feature["geometry"]["coordinates"][0]
    assert len(anillo) == len(vertices) + 1 and anillo[-1] == anillo[0]
    assert feature["properties"]["vertices"] == len(vertices)
    assert feature["properties"]["area_km2"] == area(vertices) / 1e6
    for (x, y), fila, (lon, lat) in zip(vertices, filas, anillo):
        assert (lon, lat) == (float(fila["lon"]), float(fila["lat"]))
        x2, y2 = a_utm(lon, lat)
        assert abs(float(x2) - x) < 1 and abs(float(y2) - y) < 1


def test_caso_17_sintetico(tmp_path):
    ruta_csv, ruta_geojson = escribir_envolvente(VERTICES, tmp_path)
    assert ruta_csv == tmp_path / "envolvente.csv" and ruta_geojson == tmp_path / "envolvente.geojson"
    comprobar_archivos(ruta_csv, ruta_geojson, VERTICES)


def test_main_sintetico(tmp_path):
    main(carpeta_sintetica(tmp_path))
    filas = leer_csv(tmp_path / "envolvente.csv")
    assert len(filas) == 4                      # el nodo 5 es interior y el 6 está sobre un lado
    assert (tmp_path / "envolvente.geojson").exists()


def test_main_no_escribe_si_difiere_de_scipy(tmp_path, monkeypatch):
    monkeypatch.setattr(archivos, "vertices_scipy", lambda puntos: [(0, 0), (1, 0), (0, 1)])
    with pytest.raises(ValueError):
        main(carpeta_sintetica(tmp_path))
    assert not (tmp_path / "envolvente.csv").exists()
    assert not (tmp_path / "envolvente.geojson").exists()

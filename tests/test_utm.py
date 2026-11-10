"""Pruebas de rutas/r1/utm.py (caso 10)."""
import numpy as np
import pytest
from pyproj import Transformer

from rutas.config import EPSG_UTM
from rutas.r1.catalogo import RECUADRO, cargar_catalogo
from rutas.r1.utm import a_latlon, a_utm, agregar_utm_a_nodos
from tests.conftest import grafo_sintetico


def test_caso_10_catalogo_contra_pyproj():
    # Referencia: un transformador creado aquí, independiente del módulo.
    referencia = Transformer.from_crs("EPSG:4326", f"EPSG:{EPSG_UTM}", always_xy=True)
    cat = cargar_catalogo().set_index("id")
    for id_lugar in ("C01", "A03", "A10"):
        lon, lat = cat.loc[id_lugar, "longitud"], cat.loc[id_lugar, "latitud"]
        x_ref, y_ref = referencia.transform(lon, lat)
        x, y = a_utm(np.array([lon]), np.array([lat]))
        assert abs(x[0] - x_ref) < 1e-3 and abs(y[0] - y_ref) < 1e-3


def test_caso_10_ida_y_vuelta():
    cat = cargar_catalogo()
    x, y = a_utm(cat["longitud"].to_numpy(), cat["latitud"].to_numpy())
    lons, lats = a_latlon(x, y)
    # error en metros: 1 grado de latitud ~ 111 km (cota suficiente para < 1 m)
    error_m = np.hypot((lons - cat["longitud"]) * 111_320, (lats - cat["latitud"]) * 110_574)
    assert error_m.max() < 1.0


def test_caso_10_rango_recuadro():
    lons = [RECUADRO["lon"][0], RECUADRO["lon"][1]] * 2
    lats = [RECUADRO["lat"][0]] * 2 + [RECUADRO["lat"][1]] * 2
    x, y = a_utm(np.array(lons), np.array(lats))
    assert x.min() > 389_000 - 1_000 and x.max() < 456_000 + 1_000
    assert y.min() > 442_000 - 1_000 and y.max() < 542_000 + 1_000
    # El Quindío está al oeste del meridiano central (-75): x < 500 000
    assert (x < 500_000).all()
    xp, yp = a_utm(np.array([-75.6716]), np.array([4.5339]))
    assert xp[0] == pytest.approx(425_498, abs=1) and yp[0] == pytest.approx(501_177, abs=1)


def test_agregar_utm_a_nodos():
    G = grafo_sintetico({1: (-75.6716, 4.5339), 2: (-75.5, 4.3)}, [(1, 2, {"length": 1.0})])
    devuelto = agregar_utm_a_nodos(G)
    assert devuelto is G
    x, y = a_utm(np.array([-75.6716]), np.array([4.5339]))
    assert type(G.nodes[1]["x_utm"]) is float and type(G.nodes[1]["y_utm"]) is float
    assert G.nodes[1]["x_utm"] == pytest.approx(x[0], abs=1e-6)
    assert G.nodes[1]["y_utm"] == pytest.approx(y[0], abs=1e-6)

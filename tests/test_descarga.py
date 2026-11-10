"""Pruebas de rutas/r1/descarga.py y rutas/r1/descargar.py (casos 13 y 16).

Ninguna prueba toca internet: osmnx.graph_from_place, graph_from_point, geocode_to_gdf y
save_graphml se sustituyen por dobles, y `dormir` es una función falsa que solo registra
la espera (las pruebas no duermen).
"""
import json

import geopandas as gpd
import osmnx as ox
import pytest
from osmnx._errors import ResponseStatusCodeError
from shapely.geometry import box

from rutas.r1 import descarga, descargar
from rutas.r1.catalogo import cargar_catalogo
from rutas.r1.descarga import (cargar_red_cruda, centro_plaza_bolivar, codigo_http,
                               comprobar_poligono_departamento, con_reintentos)
from tests.conftest import grafo_sintetico

ERROR_502 = "'overpass-api.de' responded: 502 Bad Gateway <html>"
ERROR_504 = "'nominatim.openstreetmap.org' responded: 504 Gateway Timeout"


def gdf_departamento(addresstype="state", ancho=0.4, alto=0.4):
    """Polígono de ~44 x 44 km (≈ 1 950 km²) centrado en el Quindío, como lo devuelve Nominatim."""
    poligono = box(-75.9, 4.3, -75.9 + ancho, 4.3 + alto)
    return gpd.GeoDataFrame({"addresstype": [addresstype]}, geometry=[poligono], crs="EPSG:4326")


class Dobles:
    """Sustituye las funciones de OSMnx que usa la descarga y anota cómo se llamaron."""

    def __init__(self, monkeypatch, fallos_por_dist=None, gdf=None):
        self.place, self.point, self.guardados = [], [], []
        self.fallos_por_dist = dict(fallos_por_dist or {})
        self.gdf = gdf if gdf is not None else gdf_departamento()
        monkeypatch.setattr(ox, "geocode_to_gdf", lambda consulta, **kw: self.gdf)
        monkeypatch.setattr(ox, "graph_from_place", self._place)
        monkeypatch.setattr(ox, "graph_from_point", self._point)
        monkeypatch.setattr(ox, "save_graphml", lambda G, ruta, **kw: self.guardados.append(ruta))

    def _place(self, *args, **kwargs):
        self.place.append((args, kwargs))
        return grafo_sintetico({1: (-75.67, 4.53)}, [])

    def _point(self, *args, **kwargs):
        self.point.append((args, kwargs))
        dist = kwargs.get("dist")
        if self.fallos_por_dist.get(dist, 0) > 0:
            self.fallos_por_dist[dist] -= 1
            raise ResponseStatusCodeError(ERROR_502)
        return grafo_sintetico({1: (-75.67, 4.53)}, [])


def test_caso_13_parametros_de_las_5_descargas(monkeypatch, tmp_path):
    dobles = Dobles(monkeypatch)
    descargar.main(carpeta=tmp_path, dormir=lambda s: None)

    assert len(dobles.place) == 1 and len(dobles.point) == 4
    _, kw = dobles.place[0]
    assert kw["network_type"] == "drive" and kw["retain_all"] is True

    catalogo = cargar_catalogo()
    c01 = catalogo[catalogo["id"] == "C01"].iloc[0]
    esperado = (c01["latitud"], c01["longitud"])
    assert centro_plaza_bolivar() == esperado
    radios = []
    for args, kw in dobles.point:
        centro = kw.get("center_point", args[0] if args else None)
        assert tuple(centro) == esperado
        assert kw["network_type"] == "drive"
        assert kw["retain_all"] is True
        assert kw["dist_type"] == "bbox"
        radios.append(kw["dist"])
    assert sorted(radios) == [2000, 5000, 10000, 20000]
    assert len(dobles.guardados) == 5


def test_poligono_municipio_falla():
    with pytest.raises(ValueError, match="state"):
        comprobar_poligono_departamento(gdf_departamento(addresstype="city"))
    with pytest.raises(ValueError, match="km"):
        comprobar_poligono_departamento(gdf_departamento(ancho=0.1, alto=0.1))  # ≈ 120 km²


def test_poligono_departamento_ok():
    info = comprobar_poligono_departamento(gdf_departamento())
    assert info["addresstype"] == "state"
    assert 1500 <= info["area_km2"] <= 2200


def test_cargar_graphml_docente(tmp_path):
    G = grafo_sintetico({1: (-75.67, 4.53), 2: (-75.66, 4.54)},
                        [(1, 2, {"length": 10.0, "highway": "residential"})])
    ox.save_graphml(G, tmp_path / "docente.graphml")
    H = cargar_red_cruda(tmp_path / "docente.graphml")
    assert H.number_of_nodes() == 2 and H.number_of_edges() == 1


def test_descarga_json_tiene_fecha_y_versiones(monkeypatch, tmp_path):
    Dobles(monkeypatch)
    descargar.main(carpeta=tmp_path, dormir=lambda s: None)
    info = json.loads((tmp_path / "descarga.json").read_text(encoding="utf-8"))
    assert info["fecha_descarga"]
    assert info["versiones"]["osmnx"] == ox.__version__
    assert "networkx" in info["versiones"] and "python" in info["versiones"]
    assert info["parametros"]["network_type"] == "drive"
    assert info["parametros"]["retain_all"] is True
    assert info["parametros"]["dist_type"] == "bbox"
    assert info["parametros"]["radios_m"] == [2000, 5000, 10000, 20000]
    assert info["centro"]["lugar"] == "C01"
    assert info["poligono"]["addresstype"] == "state"


# ---- caso 16: reintentos ----

class Funcion:
    """Función simulada: lanza los errores dados en orden y luego devuelve 'grafo'."""

    def __init__(self, errores):
        self.errores = list(errores)
        self.llamadas = 0

    def __call__(self):
        self.llamadas += 1
        if self.errores:
            raise self.errores.pop(0)
        return "grafo"


def test_codigo_http():
    assert codigo_http(ResponseStatusCodeError(ERROR_502)) == 502
    assert codigo_http(ResponseStatusCodeError(ERROR_504)) == 504

    class ConRespuesta(Exception):
        response = type("R", (), {"status_code": 429})()

    assert codigo_http(ConRespuesta()) == 429
    assert codigo_http(ValueError("sin código")) is None


def test_caso_16a_502_dos_veces_luego_exito():
    esperas = []
    f = Funcion([ResponseStatusCodeError(ERROR_502)] * 2)
    assert con_reintentos(f, dormir=esperas.append) == "grafo"
    assert f.llamadas == 3 and esperas == [30, 60]


def test_caso_16b_502_siempre_se_rinde():
    esperas = []
    f = Funcion([ResponseStatusCodeError(ERROR_502)] * 10)
    with pytest.raises(ResponseStatusCodeError) as excepcion:
        con_reintentos(f, dormir=esperas.append)
    assert f.llamadas == 5 and esperas == [30, 60, 120, 240]
    assert "5 intentos" in str(excepcion.value) and "GraphML" in str(excepcion.value)


def test_caso_16c_504_una_vez():
    esperas = []
    f = Funcion([ResponseStatusCodeError(ERROR_504)])
    assert con_reintentos(f, dormir=esperas.append) == "grafo"
    assert esperas == [30]


@pytest.mark.parametrize("error", [ResponseStatusCodeError("'x' responded: 400 Bad Request"),
                                   ValueError("polígono inválido")])
def test_caso_16d_otros_errores_no_se_reintentan(error):
    esperas = []
    f = Funcion([error])
    with pytest.raises(ValueError) as excepcion:
        con_reintentos(f, dormir=esperas.append)
    assert excepcion.value is error          # se relanza el mismo error, sin mensaje nuevo
    assert f.llamadas == 1 and esperas == []


def test_caso_16e_script_reintenta_solo_la_red_que_fallo(monkeypatch, tmp_path):
    dobles = Dobles(monkeypatch, fallos_por_dist={5000: 1})
    esperas = []
    descargar.main(carpeta=tmp_path, dormir=esperas.append)
    assert len(dobles.point) == 5      # 4 radios + 1 reintento de 5 km
    assert len(dobles.place) == 1      # el departamento no se repite
    assert len(dobles.guardados) == 5
    assert esperas == [30]

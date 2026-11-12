"""Pruebas de la carga de datos de R5 (fixture sintético y cargar_datos)."""
import gzip
import json

import pandas as pd
import pytest

from rutas.r2.matriz import cargar_matriz
from rutas.r5.datos import DatosApp, DatosFaltantes, cargar_datos
from tests.conftest import carpeta_app_sintetica


def test_fixture_sintetico(tmp_path):
    processed, catalogo, results = carpeta_app_sintetica(tmp_path)
    for nombre in ("grafo_componente.graphml", "lugares_nodos.csv", "matriz_tiempos.csv",
                   "envolvente.geojson"):
        assert (processed / nombre).exists(), nombre
    cat = pd.read_csv(catalogo)
    assert len(cat) == 8
    assert (cat["categoria"] == "Atractivo turístico").sum() == 6
    M = cargar_matriz(processed / "matriz_tiempos.csv")
    assert M.shape == (8, 8)
    # M.loc[fila, columna] = segundos de la fila a la columna; la arista 2->1 tarda 90 s
    assert M.loc["A01", "C01"] == 90 and M.loc["C01", "A01"] == 60
    gj = json.loads((processed / "envolvente.geojson").read_text(encoding="utf-8"))
    assert len(gj["features"][0]["geometry"]["coordinates"][0]) == 5
    assert (results / "r2" / "r2_tiempo_vs_explorados.png").exists()
    assert not (results / "r4" / "r4_exactas.csv").exists()


def test_carga_sintetica(tmp_path):
    processed, catalogo, _ = carpeta_app_sintetica(tmp_path)
    datos = cargar_datos(processed, catalogo)
    assert isinstance(datos, DatosApp)
    assert len(datos.nodo_de) == 8
    assert all(type(n) is int for n in datos.nodo_de.values())    # no numpy.int64
    assert datos.nodo_de["C01"] == 1 and datos.nodo_de["A06"] == 3
    assert datos.atractivos == ["A01", "A02", "A03", "A04", "A05", "A06"]
    assert datos.visita_min["A02"] == 60.0 and type(datos.visita_min["A02"]) is float
    assert datos.nombre_de["C01"] == "Cabecera Uno"
    assert datos.envolvente["features"][0]["properties"]["vertices"] == 4
    assert datos.red.ids == sorted(datos.G.nodes)
    assert list(datos.matriz.index) == list(datos.catalogo["id"])
    with pytest.raises(Exception):                 # inmutable: ninguna petición la cambia
        datos.atractivos = []


def test_caso_13_carpeta_vacia(tmp_path):
    vacia = tmp_path / "vacia"
    vacia.mkdir()
    with pytest.raises(DatosFaltantes) as error:
        cargar_datos(vacia, tmp_path / "no_existe.csv")
    mensaje = str(error.value)
    assert "grafo_componente.graphml" in mensaje
    assert "python -m rutas.r1.construir_red" in mensaje


@pytest.mark.parametrize("archivo, comando", [
    ("lugares_nodos.csv", "rutas.r1.construir_red"),
    ("matriz_tiempos.csv", "rutas.r2.matriz"),
    ("envolvente.geojson", "rutas.r3.archivos"),
    ("catalogo.csv", "restaurarlo con git"),
])
def test_cada_faltante_con_su_comando(tmp_path, archivo, comando):
    processed, catalogo, _ = carpeta_app_sintetica(tmp_path)
    ruta = catalogo if archivo == "catalogo.csv" else processed / archivo
    ruta.unlink()
    with pytest.raises(DatosFaltantes) as error:
        cargar_datos(processed, catalogo)
    mensaje = str(error.value)
    assert archivo in mensaje and comando in mensaje
    assert len(mensaje.splitlines()) == 1          # solo falta ese archivo


def test_grafo_comprimido_cuenta(tmp_path):
    processed, catalogo, _ = carpeta_app_sintetica(tmp_path)
    plano = processed / "grafo_componente.graphml"
    with open(plano, "rb") as origen, gzip.open(str(plano) + ".gz", "wb") as destino:
        destino.write(origen.read())
    plano.unlink()
    assert len(cargar_datos(processed, catalogo).nodo_de) == 8

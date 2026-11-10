"""Pruebas de rutas/r1/persistencia.py (casos 4c, 11 sintético, 11b)."""
import shutil

import pandas as pd
import pytest
from shapely.geometry import LineString

from rutas.r1.aristas import mejor_arista
from rutas.r1.componente import contar, obtener_componente
from rutas.r1.persistencia import (NOMBRE_GRAFO, cargar_grafo_procesado, cargar_lugares_nodos,
                                   cargar_metadatos, guardar_grafo, guardar_procesado)
from rutas.r1.pesos import agregar_pesos
from rutas.r1.utm import agregar_utm_a_nodos
from tests.conftest import grafo_sintetico

NODOS = {1: (-75.6716, 4.5339), 2: (-75.6600, 4.5400), 3: (-75.6500, 4.5300), 4: (-75.6000, 4.5000)}
CURVA = LineString([(-75.6716, 4.5339), (-75.666, 4.538), (-75.6600, 4.5400)])


def grafo_procesado_sintetico():
    """Componente {1, 2, 3} con paralelas 1->2 (caso 4c), tipos variados y un nodo 4 sin retorno."""
    G = grafo_sintetico(NODOS, [
        # 500 m a 36 km/h = 50 s; 400 m a 36 km/h = 40 s (caso 4c)
        (1, 2, 0, {"length": 500.0, "highway": "residential", "maxspeed": "36"}),
        (1, 2, 1, {"length": 400.0, "highway": "residential", "maxspeed": "36", "geometry": CURVA}),
        (2, 1, 0, {"length": 433.3333333333333, "highway": "primary"}),
        (2, 3, 0, {"length": 1234.5678901234567, "highway": ["tertiary", "residential"]}),
        (3, 1, 0, {"length": 987.6543210987654, "highway": "track", "maxspeed": "30 mph"}),
        (3, 4, 0, {"length": 10.1, "highway": "service"}),
    ])
    agregar_pesos(G)
    G = obtener_componente(G)
    return agregar_utm_a_nodos(G)


def lugares_ejemplo():
    return pd.DataFrame({
        "id_lugar": ["C01", "A03"],
        "id_nodo": [1, 3],
        "distancia_al_nodo_m": [0.1 + 0.2, 1054.123456789012],
        "alerta_500m": [False, True],
    })


def aristas(G):
    return {(u, v, k): d for u, v, k, d in G.edges(keys=True, data=True)}


def test_caso_4c_paralelas_sobreviven(tmp_path):
    G = grafo_procesado_sintetico()
    guardar_grafo(G, tmp_path)
    H = cargar_grafo_procesado(tmp_path)
    paralelas = H[1][2]
    assert sorted(paralelas) == [0, 1]
    assert paralelas[0]["travel_time"] == pytest.approx(50.0, abs=1e-9)
    assert paralelas[1]["travel_time"] == pytest.approx(40.0, abs=1e-9)


def test_caso_11_guardar_cargar_sintetico(tmp_path):
    G = grafo_procesado_sintetico()
    lugares = lugares_ejemplo()
    guardar_procesado(G, lugares, {"fuente": "prueba"}, tmp_path / "a")
    H = cargar_grafo_procesado(tmp_path / "a")

    assert contar(H) == contar(G)
    suma = lambda g: sum(d["travel_time"] for _, _, d in g.edges(data=True))
    assert suma(H) == pytest.approx(suma(G), abs=1e-6)
    ag, ah = aristas(G), aristas(H)
    assert ag.keys() == ah.keys()
    for clave in ag:
        for atributo in ("travel_time", "length"):
            assert ah[clave][atributo] == pytest.approx(ag[clave][atributo], abs=1e-9)
            assert ah[clave][atributo] == ag[clave][atributo]  # igualdad exacta: sin redondear

    # lugares_nodos.csv idéntico tras cargar y volver a guardar
    guardar_procesado(H, cargar_lugares_nodos(tmp_path / "a"), {"fuente": "prueba"}, tmp_path / "b")
    assert (tmp_path / "a" / "lugares_nodos.csv").read_bytes() == \
           (tmp_path / "b" / "lugares_nodos.csv").read_bytes()


def test_caso_11b_tras_guardar_cargar(tmp_path):
    G = grafo_procesado_sintetico()
    guardar_grafo(G, tmp_path)
    H = cargar_grafo_procesado(tmp_path)
    antes, despues = mejor_arista(G, 1, 2), mejor_arista(H, 1, 2)
    assert (despues.key, despues.length, despues.travel_time) == \
           (antes.key, antes.length, antes.travel_time) == (1, 400.0, 40.0)
    assert despues.geometry.equals(antes.geometry)
    # sin geometría propia: el segmento recto sale igual
    assert mejor_arista(H, 2, 3).geometry.equals(mejor_arista(G, 2, 3).geometry)


def test_tipos_al_cargar(tmp_path):
    guardar_procesado(grafo_procesado_sintetico(), lugares_ejemplo(), {}, tmp_path)
    H = cargar_grafo_procesado(tmp_path)
    for _, datos in H.nodes(data=True):
        assert type(datos["x_utm"]) is float and type(datos["y_utm"]) is float
    for _, _, datos in H.edges(data=True):
        for atributo in ("length", "speed_kph", "travel_time"):
            assert type(datos[atributo]) is float
        assert type(datos["maxspeed_original"]) is bool
    assert [type(n) for n in H.nodes] == [int] * H.number_of_nodes()
    # maxspeed_original conserva su valor: solo las dos paralelas 1->2 y la 3->1 traen maxspeed
    assert [H[1][2][k]["maxspeed_original"] for k in (0, 1)] == [True, True]
    assert H[2][1][0]["maxspeed_original"] is False
    lugares = cargar_lugares_nodos(tmp_path)
    assert lugares["id_nodo"].dtype.kind == "i"
    assert lugares["distancia_al_nodo_m"].dtype.kind == "f"
    assert lugares["alerta_500m"].dtype == bool
    assert lugares.loc[0, "distancia_al_nodo_m"] == 0.1 + 0.2  # sin redondear


def test_metadatos_ida_y_vuelta(tmp_path):
    meta = {"fecha_descarga": "2026-11-10", "V_antes": 10, "E_antes": 20}
    guardar_procesado(grafo_procesado_sintetico(), lugares_ejemplo(), meta, tmp_path)
    leidos = cargar_metadatos(tmp_path)
    assert leidos["V_antes"] == 10 and leidos["fecha_descarga"] == "2026-11-10"
    assert leidos["archivo_grafo"] == NOMBRE_GRAFO and leidos["comprimido"] is False
    guardar_procesado(grafo_procesado_sintetico(), lugares_ejemplo(), meta, tmp_path, umbral_bytes=0)
    leidos = cargar_metadatos(tmp_path)
    assert leidos["archivo_grafo"] == NOMBRE_GRAFO + ".gz" and leidos["comprimido"] is True


def test_gz_y_sin_comprimir_dan_el_mismo_grafo(tmp_path):
    G = grafo_procesado_sintetico()
    guardar_grafo(G, tmp_path / "a")
    guardar_grafo(G, tmp_path / "b", umbral_bytes=0)
    assert [p.name for p in (tmp_path / "a").iterdir()] == [NOMBRE_GRAFO]
    assert [p.name for p in (tmp_path / "b").iterdir()] == [NOMBRE_GRAFO + ".gz"]
    A, B = cargar_grafo_procesado(tmp_path / "a"), cargar_grafo_procesado(tmp_path / "b")
    assert set(A.nodes) == set(B.nodes)
    for n in A.nodes:
        for atributo in ("x_utm", "y_utm"):
            assert B.nodes[n][atributo] == pytest.approx(A.nodes[n][atributo], abs=1e-9)
            assert type(B.nodes[n][atributo]) is type(A.nodes[n][atributo]) is float
    aa, ab = aristas(A), aristas(B)
    assert aa.keys() == ab.keys()
    for clave in aa:
        for atributo in ("length", "speed_kph", "travel_time"):
            assert ab[clave][atributo] == pytest.approx(aa[clave][atributo], abs=1e-9)
            assert type(ab[clave][atributo]) is type(aa[clave][atributo]) is float
        assert type(ab[clave]["maxspeed_original"]) is bool


def test_umbral_no_superado_no_comprime(tmp_path):
    ruta = guardar_grafo(grafo_procesado_sintetico(), tmp_path, umbral_bytes=10**12)
    assert ruta == tmp_path / NOMBRE_GRAFO
    assert not (tmp_path / (NOMBRE_GRAFO + ".gz")).exists()


def test_nunca_quedan_las_dos_formas(tmp_path):
    G = grafo_procesado_sintetico()
    for primero, segundo in ((0, 10**12), (10**12, 0)):
        carpeta = tmp_path / f"{primero}"
        guardar_grafo(G, carpeta, umbral_bytes=primero)
        guardar_grafo(G, carpeta, umbral_bytes=segundo)
        nombres = [p.name for p in carpeta.iterdir()]
        assert len(nombres) == 1 and nombres[0].startswith(NOMBRE_GRAFO)
        assert cargar_grafo_procesado(carpeta).number_of_edges() == G.number_of_edges()


def test_cargar_con_ambas_formas_es_error(tmp_path):
    G = grafo_procesado_sintetico()
    guardar_grafo(G, tmp_path / "plano")
    guardar_grafo(G, tmp_path / "gz", umbral_bytes=0)
    ambas = tmp_path / "ambas"
    ambas.mkdir()
    shutil.copy(tmp_path / "plano" / NOMBRE_GRAFO, ambas)
    shutil.copy(tmp_path / "gz" / (NOMBRE_GRAFO + ".gz"), ambas)
    with pytest.raises(ValueError):
        cargar_grafo_procesado(ambas)
    vacia = tmp_path / "vacia"
    vacia.mkdir()
    with pytest.raises(FileNotFoundError):
        cargar_grafo_procesado(vacia)


def test_gz_reproducible(tmp_path):
    G = grafo_procesado_sintetico()
    guardar_grafo(G, tmp_path / "uno", umbral_bytes=0)
    guardar_grafo(G, tmp_path / "dos", umbral_bytes=0)
    nombre = NOMBRE_GRAFO + ".gz"
    assert (tmp_path / "uno" / nombre).read_bytes() == (tmp_path / "dos" / nombre).read_bytes()

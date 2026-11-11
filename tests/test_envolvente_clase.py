"""Pruebas de R3 con los casos de la clase (copia versionada en tests/datos/red_clase.json)."""
import json

import pytest
from scipy.spatial import QhullError

from rutas.config import RAIZ
from rutas.r3.envolvente import area, envolvente, normalizar
from rutas.r3.referencia import vertices_scipy
from tests.conftest import cargar_casos_r3, comprobar_envolvente

ORIGINAL = RAIZ / "estudio" / "casos_prueba.json"
ARCHIVO = RAIZ / "tests" / "datos" / "red_clase.json"


def test_r3_versionada():
    nodos, r3 = cargar_casos_r3()
    assert set(r3) == {"nodos_red", "empate", "rectangulo", "scipy_falla"}
    assert r3["nodos_red"]["vertices"] == [9, 7, 8, 3, 2]
    assert r3["nodos_red"]["area_m2"] == 585000
    assert len(nodos) == 9 and nodos[9] == (0, 0)

    # Si estudio/ existe (no se versiona), la copia debe ser idéntica al original
    if ORIGINAL.exists():
        original = json.loads(ORIGINAL.read_text(encoding="utf-8"))
        datos = json.loads(ARCHIVO.read_text(encoding="utf-8"))
        for seccion in ("red", "R2", "R3"):
            assert datos[seccion] == original[seccion]


# ---- T7: contraste de los casos a mano con SciPy ----
GRANDE = 3 * 10**9
CASOS_A_MANO = {
    "caso_1": [(0, 0), (4, 0), (4, 4), (0, 4), (2, 2), (2, 0)],
    "caso_2": [(0, 0), (10, 0), (2, 5), (5, 5), (8, 5)],
    "caso_3": [(0, 0), (5, 0), (10, 0), (10, 10), (5, 10), (0, 10), (0, 5), (10, 5), (3, 4)],
    "caso_4": [(0, 0), (5, 0), (6, 3), (3, 6), (-1, 3), (2, 2)],
    "caso_8": [(0, 0), (GRANDE, 0), (0, GRANDE), (1, 1)],
}


@pytest.mark.parametrize("puntos", CASOS_A_MANO.values(), ids=CASOS_A_MANO.keys())
def test_casos_a_mano_contra_scipy(puntos):
    propia = envolvente(puntos)
    referencia = vertices_scipy(puntos)
    assert set(propia) == set(referencia)
    assert normalizar(propia) == referencia
    comprobar_envolvente(propia, puntos)


def test_scipy_falla_en_degenerados():
    _, r3 = cargar_casos_r3()
    degenerados = [[tuple(p) for p in r3["scipy_falla"]["colineales"]],
                   [tuple(p) for p in r3["scipy_falla"]["dos_puntos"]],
                   [(0, 0), (1, 1), (2, 2), (3, 3)]]
    for puntos in degenerados:
        with pytest.raises(QhullError):
            vertices_scipy(puntos)
        resultado = envolvente(puntos)                  # la propia sí responde: los dos extremos
        assert resultado == [min(puntos, key=lambda p: (p[1], p[0])), max(puntos, key=lambda p: (p[1], p[0]))]
        comprobar_envolvente(resultado, puntos)


def test_vertices_scipy_son_int():
    for v in vertices_scipy(CASOS_A_MANO["caso_1"]):
        assert type(v) is tuple and all(type(c) is int for c in v)


# ---- T8: casos de la clase desde la copia versionada ----
def test_caso_10_red_clase():
    nodos, r3 = cargar_casos_r3()
    red = r3["nodos_red"]
    id_de = {coordenada: id_nodo for id_nodo, coordenada in nodos.items()}
    puntos = list(nodos.values())

    vertices = envolvente(puntos)
    assert [id_de[v] for v in vertices] == red["vertices"] == [9, 7, 8, 3, 2]
    assert not {id_de[v] for v in vertices} & set(red["no_vertices_sobre_lado"])
    assert area(vertices) == red["area_m2"] == 585000
    assert vertices == vertices_scipy(puntos)
    comprobar_envolvente(vertices, puntos)


def test_caso_2_empate_json():
    _, r3 = cargar_casos_r3()
    puntos = [tuple(p) for p in r3["empate"]["puntos"]]
    esperado = [tuple(p) for p in r3["empate"]["vertices"]]
    assert envolvente(puntos) == esperado
    comprobar_envolvente(esperado, puntos)


def test_caso_3_rectangulo_json():
    _, r3 = cargar_casos_r3()
    puntos = [tuple(p) for p in r3["rectangulo"]["puntos"]]
    esperado = [tuple(p) for p in r3["rectangulo"]["vertices"]]
    assert envolvente(puntos) == esperado
    comprobar_envolvente(esperado, puntos)

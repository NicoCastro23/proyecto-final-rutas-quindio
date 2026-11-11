"""Envoltorio por ids (caso 18): lo usará R5."""
import pandas as pd
import pytest

from rutas.r2.matriz import cargar_matriz, guardar_matriz
from rutas.r4.por_ids import matriz_a_listas, resolver_por_ids
from tests.test_tsp_clase import T_CLASE

IDS = ["C01", "A01", "A02", "A03"]


def matriz_clase():
    return pd.DataFrame(T_CLASE, index=IDS, columns=IDS)


@pytest.mark.parametrize("metodo, esperado", [
    ("held_karp", (35, ["C01", "A01", "A03", "A02", "C01"])),
    ("fuerza_bruta", (35, ["C01", "A01", "A03", "A02", "C01"])),
    ("vecino_mas_cercano", (39, ["C01", "A01", "A02", "A03", "C01"])),
])
def test_caso_18_por_ids(metodo, esperado):
    assert resolver_por_ids(matriz_clase(), "C01", ["A01", "A02", "A03"], metodo) == esperado


def test_matriz_a_listas_floats_de_python():
    T, ids = matriz_a_listas(matriz_clase())
    assert type(T[0][1]) is float
    assert ids == IDS
    assert T[1][0] == 5


def test_errores():
    m = matriz_clase()
    with pytest.raises(ValueError):
        resolver_por_ids(m, "C01", ["A01"], "no_existe")
    with pytest.raises(ValueError):
        resolver_por_ids(m, "C01", ["A01", "ZZZ"], "held_karp")
    with pytest.raises(ValueError):
        resolver_por_ids(m, "ZZZ", ["A01"], "held_karp")
    with pytest.raises(ValueError):
        matriz_a_listas(pd.DataFrame(T_CLASE, index=IDS, columns=["C01", "A01", "A03", "A02"]))


def test_matriz_csv_ida_y_vuelta(tmp_path):
    ruta = tmp_path / "m.csv"
    guardar_matriz(T_CLASE, IDS, ruta)
    m = cargar_matriz(ruta)
    assert resolver_por_ids(m, "C01", ["A01", "A02", "A03"], "held_karp") == \
        (35, ["C01", "A01", "A03", "A02", "C01"])

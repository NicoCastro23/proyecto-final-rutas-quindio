"""Pruebas del generador propio de permutaciones y guardia de dependencias de R4."""
import itertools

from rutas import config
from rutas.r4.permutaciones import permutaciones_lexicograficas


def test_sin_itertools_ni_networkx():
    # Guardia para todo R4: los algoritmos no pueden usar itertools, NetworkX ni NumPy.
    archivos = sorted((config.RAIZ / "rutas" / "r4").glob("*.py"))
    assert archivos, "no hay módulos en rutas/r4"
    for archivo in archivos:
        texto = archivo.read_text(encoding="utf-8")
        for prohibido in ("itertools", "networkx", "import numpy"):
            assert prohibido not in texto, f"{archivo.name} contiene {prohibido}"


def test_caso_13_orden_lexicografico():
    obtenidas = list(permutaciones_lexicograficas([0, 1, 2, 3]))
    assert obtenidas == list(itertools.permutations([0, 1, 2, 3]))
    assert len(obtenidas) == 24
    assert len(set(obtenidas)) == 24


def test_uno_y_vacio():
    assert list(permutaciones_lexicograficas([5])) == [(5,)]
    assert list(permutaciones_lexicograficas([])) == [()]


def test_no_modifica_entrada():
    entrada = [3, 1, 2]
    list(permutaciones_lexicograficas(entrada))
    assert entrada == [3, 1, 2]


def test_entrada_desordenada():
    obtenidas = list(permutaciones_lexicograficas([3, 1, 2]))
    assert obtenidas[0] == (1, 2, 3)
    assert obtenidas == list(itertools.permutations([1, 2, 3]))


def test_seis_elementos():
    obtenidas = list(permutaciones_lexicograficas(range(6)))
    assert len(obtenidas) == 720
    assert obtenidas == list(itertools.permutations(range(6)))

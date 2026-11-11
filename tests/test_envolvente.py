"""Pruebas de rutas/r3/envolvente.py (QuickHull) con casos resueltos a mano."""
import random
import sys

import pytest

from rutas.r3.envolvente import area, cruz, envolvente, normalizar
from tests.conftest import comprobar_envolvente


def test_cruz_signos():
    izquierda = cruz((0, 0), (1, 0), (0, 1))
    derecha = cruz((0, 0), (1, 0), (0, -1))
    alineados = cruz((0, 0), (1, 1), (2, 2))
    assert (izquierda, derecha, alineados) == (1, -1, 0)
    assert all(type(v) is int for v in (izquierda, derecha, alineados))


def test_cruz_grande():
    # Caso 8: 3*10^9 * 3*10^9 = 9*10^18, exacto (con enteros de Python no hay desborde)
    valor = cruz((0, 0), (3 * 10**9, 0), (0, 3 * 10**9))
    assert valor == 9 * 10**18 and type(valor) is int


def test_area():
    assert area([(0, 0), (4, 0), (4, 4), (0, 4)]) == 16.0
    assert area([(0, 0), (4, 0), (0, 3)]) == 6.0
    assert area([(0, 0), (0, 3), (4, 0)]) == 6.0         # mismo triángulo en sentido horario
    assert area([(0, 0), (1, 0)]) == 0 and area([]) == 0


def test_normalizar():
    esperado = [(0, 0), (4, 0), (4, 4), (0, 4)]
    assert normalizar([(4, 4), (4, 0), (0, 0), (0, 4)]) == esperado    # horario y empieza en (4,4)
    assert normalizar(esperado) == esperado
    # Empate de y mínima: empieza por el de menor x
    assert normalizar([(4, 0), (4, 4), (0, 4), (0, 0)]) == esperado


# ---- T6: QuickHull con los casos resueltos a mano ----
CUADRADO = [(0, 0), (4, 0), (4, 4), (0, 4)]


def comprobar(puntos, esperado):
    """La salida es exactamente `esperado` y cumple los invariantes del caso 13."""
    resultado = envolvente(puntos)
    assert resultado == esperado
    comprobar_envolvente(resultado, puntos)


def test_caso_1_cuadrado_con_extras():
    comprobar([(0, 0), (4, 0), (4, 4), (0, 4), (2, 2), (2, 0)], CUADRADO)


def test_caso_2_desempate():
    puntos = [(0, 0), (10, 0), (2, 5), (5, 5), (8, 5)]
    comprobar(puntos, [(0, 0), (10, 0), (8, 5), (2, 5)])
    assert (5, 5) not in envolvente(puntos)


def test_caso_3_rectangulo_lados():
    puntos = [(0, 0), (5, 0), (10, 0), (10, 10), (5, 10), (0, 10), (0, 5), (10, 5), (3, 4)]
    comprobar(puntos, [(0, 0), (10, 0), (10, 10), (0, 10)])


def test_caso_4_pentagono():
    comprobar([(0, 0), (5, 0), (6, 3), (3, 6), (-1, 3), (2, 2)],
              [(0, 0), (5, 0), (6, 3), (3, 6), (-1, 3)])


def test_caso_5_duplicados():
    comprobar([(0, 0), (0, 0), (1, 0), (0, 1)], [(0, 0), (1, 0), (0, 1)])


def test_caso_6_alineados():
    alineados = [(0, 0), (1, 1), (2, 2), (3, 3)]
    comprobar(alineados, [(0, 0), (3, 3)])
    comprobar(alineados[::-1], [(0, 0), (3, 3)])


def test_caso_7_bordes_pequenos():
    comprobar([], [])
    comprobar([(7, 7)], [(7, 7)])
    comprobar([(7, 7), (7, 7)], [(7, 7)])
    comprobar([(1, 0), (0, 0)], [(0, 0), (1, 0)])


def test_caso_8_coordenadas_grandes():
    grande = 3 * 10**9
    comprobar([(0, 0), (grande, 0), (0, grande), (1, 1)], [(0, 0), (grande, 0), (0, grande)])


def test_coordenadas_negativas():
    d = -10**6
    puntos = [(x + d, y + d) for x, y in [(0, 0), (4, 0), (4, 4), (0, 4), (2, 2), (2, 0)]]
    comprobar(puntos, [(x + d, y + d) for x, y in CUADRADO])


def test_orden_de_entrada_no_importa():
    casos = [([(0, 0), (4, 0), (4, 4), (0, 4), (2, 2), (2, 0)], CUADRADO),
             ([(0, 0), (10, 0), (2, 5), (5, 5), (8, 5)], [(0, 0), (10, 0), (8, 5), (2, 5)]),
             ([(0, 0), (5, 0), (6, 3), (3, 6), (-1, 3), (2, 2)], [(0, 0), (5, 0), (6, 3), (3, 6), (-1, 3)]),
             ([(0, 0), (5, 0), (10, 0), (10, 10), (5, 10), (0, 10), (0, 5), (10, 5), (3, 4)],
              [(0, 0), (10, 0), (10, 10), (0, 10)])]
    azar = random.Random(2026)
    for puntos, esperado in casos:
        for _ in range(10):
            barajados = puntos[:]
            azar.shuffle(barajados)
            assert envolvente(barajados) == esperado


def test_no_modifica_entrada():
    puntos = [(0, 0), (4, 0), (4, 4), (0, 4), (2, 2), (2, 0), (0, 0)]
    copia = list(puntos)
    envolvente(puntos)
    assert puntos == copia


def test_invariantes_detectan_errores():
    puntos = CUADRADO + [(2, 2)]
    comprobar_envolvente(CUADRADO, puntos)                                   # el correcto pasa
    with pytest.raises(AssertionError):
        comprobar_envolvente(CUADRADO[::-1], puntos)                         # sentido horario
    with pytest.raises(AssertionError):
        comprobar_envolvente(CUADRADO + [(2, 0)], puntos + [(2, 0)])        # vértice alineado
    with pytest.raises(AssertionError):
        comprobar_envolvente(CUADRADO, puntos + [(9, 9)])                    # punto por fuera


def test_limite_de_recursion():
    # QuickHull es recursivo: el módulo sube el límite de Python para el peor caso (profundidad O(n))
    assert sys.getrecursionlimit() >= 20_000

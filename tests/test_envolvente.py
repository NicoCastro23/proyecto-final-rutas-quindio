"""Pruebas de rutas/r3/envolvente.py (QuickHull) con casos resueltos a mano."""
from rutas.r3.envolvente import area, cruz, normalizar


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

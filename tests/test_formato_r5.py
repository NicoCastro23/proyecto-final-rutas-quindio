"""Pruebas de formato.numero: coma decimal y espacio de miles."""
import numpy as np
import pytest

from rutas.r5.formato import numero


@pytest.mark.parametrize("valor, decimales, esperado", [
    (29.7239, 1, "29,7"),
    (1783.39, 1, "1 783,4"),
    (1631.4960175, 1, "1 631,5"),
    (6.600187, 2, "6,60"),
    (0, 1, "0,0"),
    (7360, 0, "7 360"),
    (178.6557, 1, "178,7"),
    (190.4473, 1, "190,4"),
    (11.7916, 1, "11,8"),
])
def test_coma_decimal(valor, decimales, esperado):
    assert numero(valor, decimales) == esperado


def test_acepta_numpy():
    assert numero(np.float64(1.25), 2) == "1,25"

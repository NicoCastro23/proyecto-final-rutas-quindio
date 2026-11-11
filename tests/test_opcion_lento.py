"""Prueba del mecanismo de la opción --lento (tests/conftest.py) con pytester."""
from rutas.config import RAIZ

pytest_plugins = ["pytester"]

PRUEBA = """
import pytest

@pytest.mark.lento
def test_pesada():
    pass

def test_normal():
    pass
"""


def _correr(pytester, *opciones):
    # El conftest de la prueba importa los ganchos reales del proyecto (tests/conftest.py)
    pytester.syspathinsert(RAIZ)
    pytester.makeconftest(
        "from tests.conftest import pytest_addoption, pytest_collection_modifyitems  # noqa: F401\n"
        "def pytest_configure(config):\n"
        "    config.addinivalue_line('markers', 'lento: x')\n")
    pytester.makepyfile(PRUEBA)
    return pytester.runpytest(*opciones)


def test_sin_opcion_los_lentos_se_saltan(pytester):
    _correr(pytester).assert_outcomes(passed=1, skipped=1)


def test_con_marcador_filtrado_tampoco_corren(pytester):
    _correr(pytester, "-m", "not red").assert_outcomes(passed=1, skipped=1)


def test_con_opcion_corren(pytester):
    _correr(pytester, "--lento").assert_outcomes(passed=2)

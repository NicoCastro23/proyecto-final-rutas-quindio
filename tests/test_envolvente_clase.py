"""Pruebas de R3 con los casos de la clase (copia versionada en tests/datos/red_clase.json)."""
import json

from rutas.config import RAIZ
from tests.conftest import cargar_casos_r3

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

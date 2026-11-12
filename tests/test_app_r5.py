"""Pruebas de la aplicación de R5 (la guardia de T2; las demás se agregan en el bloque B3)."""
import re

from rutas.config import RAIZ

R5 = RAIZ / "rutas" / "r5"


def test_sin_algoritmos_ni_js_propio():
    """R5 no implementa algoritmos (los importa de R2 y R4) ni lleva JavaScript propio."""
    for archivo in R5.glob("*.py"):
        texto = archivo.read_text(encoding="utf-8")
        for prohibido in ("heapq", "networkx", "scipy", "itertools"):
            assert not re.search(rf"^\s*(import|from)\s+{prohibido}\b", texto, re.M), \
                f"{archivo.name} importa {prohibido}"
    plantillas = list((R5 / "templates").glob("*.html"))
    assert plantillas, "debe haber al menos base.html"
    for plantilla in plantillas:
        assert "<script" not in plantilla.read_text(encoding="utf-8").lower(), plantilla.name
    requisitos = (RAIZ / "requirements.txt").read_text(encoding="utf-8")
    assert "Flask==3.1.3" in requisitos and "folium==0.20.0" in requisitos

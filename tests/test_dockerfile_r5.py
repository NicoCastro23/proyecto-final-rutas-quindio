"""T20: el Dockerfile opcional de R5 (prueba de estructura; no necesita Docker)."""
from pathlib import Path

DOCKERFILE = Path(__file__).resolve().parent.parent / "Dockerfile"


def test_dockerfile():
    texto = DOCKERFILE.read_text(encoding="utf-8")
    assert texto.startswith("FROM python:3.13-slim")
    assert "pip install" in texto and "requirements.txt" in texto
    for fragmento in ("COPY data/processed", "COPY results", "COPY rutas", "0.0.0.0", "5050",
                      "rutas.r5.app"):
        assert fragmento in texto, fragmento
    # No debe copiar datos crudos, el entorno virtual ni las notas privadas.
    for prohibido in ("data/raw", ".venv", "estudio"):
        assert prohibido not in texto, prohibido

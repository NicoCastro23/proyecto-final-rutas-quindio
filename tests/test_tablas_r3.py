"""Pruebas de rutas/r3/tablas.py: la gráfica sale del grafo y de envolvente.csv."""
import pytest

from rutas.r3 import tablas
from rutas.r3.archivos import escribir_envolvente
from tests.test_archivos_r3 import _carpeta_sintetica


@pytest.fixture
def processed(tmp_path):
    carpeta = _carpeta_sintetica(tmp_path / "processed")
    # Cuadrado alrededor de los nodos sintéticos (el valor exacto no importa para la gráfica)
    escribir_envolvente([(420_000, 500_000), (430_000, 500_000), (430_000, 510_000), (420_000, 510_000)],
                        carpeta)
    return carpeta


def test_grafica_crea_png(processed, tmp_path):
    ruta = tablas.grafica_envolvente(processed, tmp_path / "salida" / "r3")   # crea la carpeta
    assert ruta == tmp_path / "salida" / "r3" / "r3_envolvente.png"
    contenido = ruta.read_bytes()
    assert contenido.startswith(b"\x89PNG\r\n\x1a\n") and len(contenido) > 1000


def test_grafica_titulo_con_n_y_vertices(processed, tmp_path, monkeypatch):
    titulos = []
    from matplotlib.axes import Axes
    original = Axes.set_title
    monkeypatch.setattr(Axes, "set_title", lambda self, t, *a, **k: (titulos.append(t), original(self, t, *a, **k))[1])
    tablas.grafica_envolvente(processed, tmp_path)
    assert "6 nodos" in titulos[0] and "4 vértices" in titulos[0] and "km" in titulos[0]
    assert "100.0" in titulos[0]            # área del cuadrado de 10 km x 10 km, en km2

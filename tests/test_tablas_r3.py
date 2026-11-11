"""Pruebas de rutas/r3/tablas.py: la gráfica sale del grafo y de envolvente.csv."""
import pytest

from rutas.r3 import tablas
from rutas.r3.archivos import escribir_envolvente
from tests.conftest import carpeta_sintetica


@pytest.fixture
def processed(tmp_path):
    carpeta = carpeta_sintetica(tmp_path / "processed")
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


# ---- T15: tablas_r3.md desde los archivos ----
import json

import pandas as pd

from rutas.r3.medir_envolvente import COLUMNAS, NOMBRE_RED

FILAS = [
    [NOMBRE_RED, 8791, 14, 12.3456, 1.5, 12.3456 / 1.5, 5],
    ["Cuadrado, 1 000 puntos", 1000, 17, 0.5, 0.1, 5.0, 5],
    ["Cuadrado, 10 000 puntos", 10000, 26, 5.25, 0.5, 10.5, 5],
    ["Cuadrado, 50 000 puntos", 50000, 25, "no completada", 2.2, "no completada", 5],
]


@pytest.fixture
def resultados(tmp_path, processed):
    carpeta = tmp_path / "results"
    carpeta.mkdir()
    pd.DataFrame(FILAS, columns=COLUMNAS).to_csv(carpeta / "r3_envolvente.csv", index=False)
    (carpeta / "r3_puntos.json").write_text(json.dumps({
        "semilla": 2026, "generador": "random.Random", "lado": 10**6,
        "redondeo": "math.floor(x + 0.5)", "nota": "cada cuadrado usa su propio Random(2026)",
        "conjuntos": [{"conjunto": f[0], "n_pedido": f[1] + (0 if i == 0 else 3), "n_obtenido": f[1]}
                      for i, f in enumerate(FILAS)]}), encoding="utf-8")
    (carpeta / "maquina.json").write_text(json.dumps({"procesador": "CPU de prueba", "ram_gb": 16}),
                                          encoding="utf-8")
    return carpeta


def test_tablas_salen_de_los_archivos(resultados, processed):
    tablas.main(resultados, processed)
    md = (resultados / "tablas_r3.md").read_text(encoding="utf-8")
    assert "Tiempo propio (ms)" in md and "Tiempo SciPy (ms)" in md
    assert "12.346" in md and "| 8.2 |" in md                    # tiempos con 3 decimales, cociente con 1
    assert "8.23" not in md
    assert "2026" in md and "CPU de prueba" in md and "100.000" in md
    posiciones = [md.index(f[0]) for f in FILAS]
    assert posiciones == sorted(posiciones)                      # los cuatro nombres en orden
    assert "1 003" in md                                        # n pedido del primer cuadrado


def test_no_completada_se_muestra(resultados, processed):
    tablas.main(resultados, processed)
    md = (resultados / "tablas_r3.md").read_text(encoding="utf-8")
    assert md.count("no completada") >= 2


def test_referencia_renyi_sulanke(resultados, processed):
    assert round(tablas.referencia_renyi_sulanke(1000), 1) == 18.4
    tablas.main(resultados, processed)
    md = (resultados / "tablas_r3.md").read_text(encoding="utf-8")
    assert "Vértices frente a (8/3) ln n" in md and "| 18.4 |" in md


def test_main_genera_todo(resultados, processed):
    tablas.main(resultados, processed)
    assert (resultados / "tablas_r3.md").exists()
    assert (resultados / "r3_envolvente.png").read_bytes().startswith(b"\x89PNG")


def test_n_con_espacio_de_miles_y_frase_con_mayuscula(resultados, processed):
    # Revisión 1: la columna n dice "10 000" como el nombre del conjunto, no "10000"; solo presentación
    tablas.main(resultados, processed)
    md = (resultados / "tablas_r3.md").read_text(encoding="utf-8")
    assert "| 8 791 |" in md and "| 1 000 |" in md and "| 10 000 |" in md and "| 50 000 |" in md
    assert "| 10000 |" not in md and "| 1003 |" not in md and "| 1 003 |" in md   # n pedido también
    assert "Cada cuadrado usa su propio Random(2026)" in md        # la frase empieza en mayúscula

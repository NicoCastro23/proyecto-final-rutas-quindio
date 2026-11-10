"""Pruebas de rutas/r2/tablas.py: cociente, gráfica y tablas salen de los CSV/JSON."""
import json

import pandas as pd
import pytest

from rutas.r2 import tablas

# 3 pares cercanos (lineal 10, 30, 8 ms; cola 2, 3, 4 ms -> cocientes 5, 10, 2) y 1 lejano solo con cola
FILAS = [
    ("C1", "C2", "cola_prioridad", 100.5, 10, 2.0, "cercano", 800.0, 5),
    ("C1", "C2", "lineal", 100.5, 10, 10.0, "cercano", 800.0, 5),
    ("C3", "C4", "cola_prioridad", 200.25, 30, 3.0, "cercano", 1600.0, 5),
    ("C3", "C4", "lineal", 200.25, 30, 30.0, "cercano", 1600.0, 5),
    ("C5", "C6", "cola_prioridad", 50.0, 5, 4.0, "cercano", 400.0, 5),
    ("C5", "C6", "lineal", 50.0, 5, 8.0, "cercano", 400.0, 5),
    ("L1", "L2", "cola_prioridad", 3000.75, 4000, 400.0, "lejano", 30000.0, 5),
]
COLUMNAS = ["origen", "destino", "version", "tiempo_viaje_s", "nodos_explorados", "tiempo_ms",
            "tipo", "distancia_m", "repeticiones"]


def df_sintetico(filas=FILAS):
    return pd.DataFrame(filas, columns=COLUMNAS)


@pytest.fixture
def results(tmp_path):
    df_sintetico().to_csv(tmp_path / "r2_dijkstra.csv", index=False)
    (tmp_path / "r2_pares.json").write_text(json.dumps(
        {"semilla": 2026, "generador": "random.Random", "cercanos": 10, "lejanos": 10,
         "regla": "regla de prueba"}), encoding="utf-8")
    (tmp_path / "r2_asimetria.json").write_text(json.dumps(
        {"pares_asimetricos": 845, "par_max": ["F05", "F06"], "diferencia_max": 383.19,
         "M_ij": 2841.85, "M_ji": 3225.04, "tolerancia": 1e-06}), encoding="utf-8")
    (tmp_path / "maquina.json").write_text(json.dumps(
        {"procesador": "CPU de prueba", "ram_gb": 16.0, "so": "SO", "python": "3.13"}),
        encoding="utf-8")
    return tmp_path


def test_caso_18_cociente():
    assert tablas.cociente(df_sintetico()) == {"mediana": 5.0, "minimo": 2.0, "maximo": 10.0}


def test_cociente_excluye_no_completada():
    filas = list(FILAS)
    filas[3] = ("C3", "C4", "lineal", 200.25, 30, "no completada", "cercano", 1600.0, 0)
    df = pd.DataFrame(filas, columns=COLUMNAS)       # tiempo_ms queda como texto en esa columna
    assert tablas.cociente(df) == {"mediana": 3.5, "minimo": 2.0, "maximo": 5.0}


def test_escala_log():
    assert tablas.usar_escala_log(df_sintetico()) is True          # 400 / 2 = 200 >= 100
    assert tablas.usar_escala_log(df_sintetico(FILAS[:6])) is False   # 30 / 2 = 15
    filas = list(FILAS[:2]) + [("C9", "C8", "lineal", 1.0, 1, "no completada", "cercano", 1.0, 0),
                               ("L1", "L2", "cola_prioridad", 1.0, 1, 200.0, "lejano", 1.0, 5)]
    assert tablas.usar_escala_log(pd.DataFrame(filas, columns=COLUMNAS)) is True   # 200/2; ignora texto


def test_grafica_crea_png(results):
    png = tablas.grafica_tiempo_vs_explorados(results)
    assert png.name == "r2_tiempo_vs_explorados.png"
    assert png.exists() and png.stat().st_size > 0


def test_tablas_salen_de_los_csv(results):
    tablas.main(results=results)
    texto = (results / "tablas_r2.md").read_text(encoding="utf-8")
    for esperado in ("3000.75", "200.25", "Tiempo (ms)", "2026", "regla de prueba",
                     "845", "F05", "383.19", "CPU de prueba", "Mediana", "5.00", "10.00", "2.00"):
        assert esperado in texto, esperado


def test_main_genera_todo(results):
    tablas.main(results=results)
    cociente = pd.read_csv(results / "r2_cociente.csv")
    assert list(cociente.columns) == ["mediana", "minimo", "maximo"]
    assert cociente.iloc[0].tolist() == [5.0, 2.0, 10.0]
    assert (results / "r2_tiempo_vs_explorados.png").stat().st_size > 0
    assert (results / "tablas_r2.md").exists()


def test_main_avisa_si_hay_lineal_no_completada(results):
    filas = list(FILAS)
    filas[3] = ("C3", "C4", "lineal", 200.25, 30, "no completada", "cercano", 1600.0, 0)
    pd.DataFrame(filas, columns=COLUMNAS).to_csv(results / "r2_dijkstra.csv", index=False)
    tablas.main(results=results)
    texto = (results / "tablas_r2.md").read_text(encoding="utf-8")
    assert "no completada" in texto and "excluy" in texto

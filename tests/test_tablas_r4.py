"""Pruebas de rutas/r4/tablas.py con CSV/JSON de ejemplo escritos en tmp_path (nunca los reales)."""
import json

import matplotlib.pyplot as plt
import pandas as pd
import pytest
from matplotlib.axes import Axes

from rutas.r4 import tablas
from rutas.r4.medir_exactas import COLUMNAS as COLUMNAS_EXACTAS

TIEMPOS_FB = {5: 10.0, 6: 60.0, 7: 500.0, 8: 4000.0, 9: 36000.0, 10: 400000.0}
TIEMPOS_HK = {k: 1.0 * 2.5 ** (k - 5) for k in range(5, 13)}


def df_exactas():
    filas = []
    for k in range(5, 13):
        if k <= 10:
            filas.append([k, "fuerza_bruta", TIEMPOS_FB[k], 5, "ok", 9000.5, "C01-A-B-C01"])
        else:
            estado = "no_completada" if k == 11 else "no_ejecutada"
            filas.append([k, "fuerza_bruta", "", 0, estado, "", ""])
        filas.append([k, "held_karp", TIEMPOS_HK[k], 5, "ok", 9000.5, "C01-A-B-C01"])
    return pd.DataFrame(filas, columns=COLUMNAS_EXACTAS)


def escribir_resultados(carpeta, con_exactas=True):
    carpeta.mkdir(parents=True, exist_ok=True)
    if con_exactas:
        df_exactas().to_csv(carpeta / "r4_exactas.csv", index=False)
        (carpeta / "maquina.json").write_text(json.dumps(
            {"procesador": "CPU de prueba", "ram_gb": 16, "so": "SO", "python": "3.13.18"}), encoding="utf-8")
    pd.DataFrame({"k": [5, 8], "celdas": [160, 2048], "bytes_estimados": [1920, 24576],
                  "mb_estimados": [0.00192, 0.024576], "pico_tracemalloc_bytes": [9136, 90824],
                  "pico_tracemalloc_mb": [0.009136, 0.090824]}).to_csv(carpeta / "r4_memoria.csv", index=False)
    pd.DataFrame({"k": [5, 8], "instancias": [10, 10], "brecha_promedio_pct": [6.0, 9.727],
                  "brecha_maxima_pct": [12.09, 19.76]}).to_csv(carpeta / "r4_calidad.csv", index=False)
    pd.DataFrame({"orden": [1, "Regreso"], "id": ["A04", "C01"], "lugar": ["Jardín Botánico", "Plaza"],
                  "desplazamiento_min": [8.48, 4.03], "visita_min": ["180.0", "—"],
                  "acumulado_h": [3.14, 10.22]}).to_csv(carpeta / "r4_itinerario.csv", index=False)
    (carpeta / "r4_itinerario.json").write_text(json.dumps({
        "partida": {"id": "C01", "lugar": "Plaza"}, "atractivos_iniciales": ["A04", "A01"],
        "quitados": [{"id": "A01", "lugar": "Parque Nacional", "jornada_antes_min": 1255.2,
                      "jornada_despues_min": 809.6, "ahorro_min": 445.6}],
        "atractivos_finales": ["A04"],
        "totales": {"visitas_min": 510.0, "desplazamientos_min": 103.1, "jornada_min": 613.1,
                    "jornada_h": 10.22},
        "jornada_max_min": 660, "cabe": True}), encoding="utf-8")
    (carpeta / "r4_instancias.json").write_text(json.dumps({
        "semilla": 2026, "generador": "random.Random(semilla).sample(otros, k)", "partida": "C01",
        "muestra_anidada": ["C09", "A10"], "semillas_calidad": list(range(2026, 2036))}), encoding="utf-8")


def test_caso_20_tabla_exactas():
    md = tablas.tabla_exactas(df_exactas())
    lineas = md.splitlines()
    assert len(lineas) == 2 + 8
    assert "Tiempo fuerza bruta (ms)" in lineas[0] and "Tiempo Held-Karp (ms)" in lineas[0]
    fila_11 = next(l for l in lineas if l.startswith("| 11 |"))
    assert "no completada" in fila_11
    assert "no completada" in next(l for l in lineas if l.startswith("| 12 |"))
    assert "10.000" in next(l for l in lineas if l.startswith("| 5 |"))     # 3 decimales


def test_mayor_k_resuelto():
    md = tablas.tabla_mayor_k(df_exactas())
    assert "| Fuerza bruta | 10 |" in md and "| Held-Karp | 12 |" in md


def test_cocientes_medidos_y_predichos():
    md = tablas.tabla_cocientes(df_exactas())
    fila = next(l for l in md.splitlines() if l.startswith("| 5 a 6 |"))
    celdas = [c.strip() for c in fila.strip("|").split("|")]
    # k, FB medido, FB predicho, HK medido, HK predicho
    assert celdas[1:] == ["6.00", "7.20", "2.50", "2.88"]
    # FB no resuelve 11: no hay cociente de 10 a 11 ni de 11 a 12
    assert "—" in next(l for l in md.splitlines() if l.startswith("| 10 a 11 |"))


def test_grafica_marcas_enteras_en_k(tmp_path, monkeypatch):
    # Con solo k = 5..8 (como en una corrida corta) matplotlib ponía marcas 5,5 / 6,5...
    filas = [[k, m, 1.0 + k, 5, "ok", 9000.5, "C01-A-B-C01"]
             for k in range(5, 9) for m in ("fuerza_bruta", "held_karp")]
    pd.DataFrame(filas, columns=COLUMNAS_EXACTAS).to_csv(tmp_path / "r4_exactas.csv", index=False)
    marcas = []
    savefig = plt.Figure.savefig
    def guardar(fig, *a, **k):
        fig.canvas.draw()
        marcas.extend(fig.axes[0].get_xticks())
        return savefig(fig, *a, **k)
    monkeypatch.setattr(plt.Figure, "savefig", guardar)
    tablas.grafica_tiempo_vs_k(tmp_path)
    visibles = [m for m in marcas if 5 <= m <= 8]
    assert visibles and all(float(m).is_integer() for m in visibles)


def test_caso_20_grafica(tmp_path, monkeypatch):
    escribir_resultados(tmp_path)
    llamadas, escalas, etiquetas_y = [], [], []
    plot, set_yscale, set_ylabel = Axes.plot, Axes.set_yscale, Axes.set_ylabel
    monkeypatch.setattr(Axes, "plot", lambda self, *a, **k: (llamadas.append((a, k)), plot(self, *a, **k))[1])
    monkeypatch.setattr(Axes, "set_yscale", lambda self, e, *a, **k: (escalas.append(e), set_yscale(self, e, *a, **k))[1])
    monkeypatch.setattr(Axes, "set_ylabel", lambda self, t, *a, **k: (etiquetas_y.append(t), set_ylabel(self, t, *a, **k))[1])
    ruta = tablas.grafica_tiempo_vs_k(tmp_path)
    assert len(llamadas) == 2
    (x_fb, y_fb), (x_hk, _) = llamadas[0][0][:2], llamadas[1][0][:2]
    assert list(x_fb) == [5, 6, 7, 8, 9, 10] and list(x_hk) == list(range(5, 13))
    assert list(y_fb) == list(TIEMPOS_FB.values())
    assert escalas == ["log"]
    assert "ms" in etiquetas_y[0] and "logarítmica" in etiquetas_y[0]
    textos = " ".join(str(k.get("label", "")) for _, k in llamadas)
    assert "no completada" in textos
    assert ruta == tmp_path / "r4_tiempo_vs_k.png"
    assert ruta.read_bytes().startswith(b"\x89PNG") and ruta.stat().st_size > 1000


def test_caso_20_calidad_e_itinerario(tmp_path):
    escribir_resultados(tmp_path)
    tablas.main(tmp_path)
    md = (tmp_path / "tablas_r4.md").read_text(encoding="utf-8")
    assert "Brecha promedio (%)" in md and "| 8 | 10 | 9.73 | 19.76 |" in md
    assert "Desplazamiento desde el anterior (min)" in md and "Tiempo acumulado (h)" in md
    assert "| Regreso |" in md and "| 1 | Jardín Botánico | 8.5 | 180.0 | 3.14 |" in md
    assert "A01" in md and "445.6" in md            # atractivo quitado y su ahorro
    assert "613.1" in md and "10.22" in md          # totales


def test_memoria_y_semillas(tmp_path):
    escribir_resultados(tmp_path)
    tablas.main(tmp_path)
    md = (tmp_path / "tablas_r4.md").read_text(encoding="utf-8")
    assert "Pico tracemalloc (MB)" in md and "0.091" in md and "0.025" in md
    assert "2026" in md and "2026..2035" in md
    assert "CPU de prueba" in md
    assert "Transiciones Held-Karp" in md and "135192" in md.replace(" ", "")


def test_archivos_faltantes(tmp_path):
    tablas.main(tmp_path)                          # carpeta vacía: no falla
    md = (tmp_path / "tablas_r4.md").read_text(encoding="utf-8")
    assert "r4_exactas.csv" in md and "todavía no existe" in md
    assert not (tmp_path / "r4_tiempo_vs_k.png").exists()

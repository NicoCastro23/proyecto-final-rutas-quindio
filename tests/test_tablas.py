"""Pruebas de rutas/r1/tablas.py: las tablas salen de los CSV, no se escriben a mano."""
import pandas as pd
import pytest

from rutas.config import CATALOGO
from rutas.r1 import tablas


@pytest.fixture
def carpetas(tmp_path):
    results, processed = tmp_path / "results", tmp_path / "processed"
    results.mkdir()
    processed.mkdir()
    pd.DataFrame({"red": ["Red descargada", "Componente fuertemente conexa"],
                  "nodos": [8877, 8791], "aristas": [20245, 20132]}
                 ).to_csv(results / "r1_tamanos.csv", index=False)
    pd.DataFrame({
        "red": ["Radio de 2 km", "Departamento completo"], "V": [701, 8877], "E": [1502, 20245],
        "V_mas_E": [2203, 29122], "tiempo_ms": [12.5, "no completada"],
        "tiempo_por_elemento_us": [5.675, ""], "repeticiones": [5, 0],
        "ya_fuertemente_conexa": [True, False]}
    ).to_csv(results / "r1_tiempos_componente.csv", index=False)
    memoria = []
    for red, V, E in (("Red descargada", 8877, 20245), ("Componente fuertemente conexa", 8791, 20132)):
        for representacion, bytes_ in (("Matriz de adyacencia", 4 * V * V), ("Listas de adyacencia", 8 * E)):
            memoria.append({"red": red, "V": V, "E": E, "representacion": representacion,
                            "supuesto": f"supuesto de {representacion}", "bytes": bytes_,
                            "MB": bytes_ / 1e6})
    pd.DataFrame(memoria).to_csv(results / "r1_memoria.csv", index=False)
    pd.DataFrame({"highway": ["primary", "Total"], "velocidad_tabla_kmh": [60, None],
                  "aristas": [563, 20132],
                  "con_maxspeed_osm": [166, 1303], "pct_osm": [29.5, 6.5],
                  "pct_imputado": [70.5, 93.5]}).to_csv(results / "r1_velocidades.csv", index=False)
    pd.DataFrame({"id_lugar": ["C01", "A03", "A10"], "id_nodo": [111, 222, 333],
                  "distancia_al_nodo_m": [59.8, 1054.1, 539.2],
                  "alerta_500m": [False, True, True]}
                 ).to_csv(processed / "lugares_nodos.csv", index=False)
    return results, processed


def generar(carpetas):
    results, processed = carpetas
    tablas.main(results=results, processed=processed, catalogo=CATALOGO)
    return (results / "tablas_r1.md").read_text(encoding="utf-8")


def test_a_markdown_forma():
    texto = tablas.a_markdown(pd.DataFrame({"a": [1, 2], "b": [1.5, 2.25]}))
    lineas = texto.splitlines()
    assert lineas[0] == "| a | b |"
    assert lineas[1].replace(" ", "").startswith("|---")
    assert lineas[2] == "| 1 | 1.50 |" and lineas[3] == "| 2 | 2.25 |"


def test_tablas_salen_de_los_csv(carpetas):
    md = generar(carpetas)
    for valor in ("8877", "20245", "8791", "20132",          # tamaños
                  "701", "1502", "12.50", "5.675",           # tiempos
                  "563", "166", "29.5", "93.5",                # velocidades
                  "1054.10", "539.20"):                      # alertas
        assert valor in md, valor


def test_velocidades_muestra_velocidad_de_tabla(carpetas):
    md = generar(carpetas)
    assert "Velocidad de tabla (km/h)" in md
    fila = [l for l in md.splitlines() if l.startswith("| primary")][0]
    assert "| 60 |" in fila


def test_unidades_en_encabezados(carpetas):
    md = generar(carpetas)
    for unidad in ("(ms)", "(µs)", "(MB)", "(m)"):
        assert unidad in md


def test_memoria_muestra_ambas_redes(carpetas):
    md = generar(carpetas)
    filas = [l for l in md.splitlines() if "adyacencia" in l and l.startswith("|")]
    assert len(filas) == 4
    assert sum("Red descargada" in l for l in filas) == 2
    assert sum("Componente fuertemente conexa" in l for l in filas) == 2
    assert sum("Matriz de adyacencia" in l for l in filas) == 2
    assert sum("Listas de adyacencia" in l for l in filas) == 2
    assert any("8877" in l and "20245" in l for l in filas)
    assert any("8791" in l and "20132" in l for l in filas)


def test_tabla_alertas_solo_alertados(carpetas):
    md = generar(carpetas)
    seccion = md.split("## Lugares con alerta")[1]
    assert "A03" in seccion and "A10" in seccion
    assert "C01" not in seccion
    nombre_a03 = pd.read_csv(CATALOGO).set_index("id").loc["A03", "nombre"]
    assert nombre_a03 in seccion


def test_no_completada_se_muestra(carpetas):
    assert "no completada" in generar(carpetas)


def test_tabla_tiempos_muestra_conexidad(carpetas):
    md = generar(carpetas)
    bloque = md.split("## Tiempo de")[1].split("## Memoria")[0]
    filas = [l for l in bloque.splitlines() if l.startswith("|")]
    assert filas[0].endswith("| Ya fuertemente conexa |")
    assert filas[2].endswith("| 5 | sí |")                   # Radio de 2 km
    assert filas[3].endswith("| 0 | no |")                   # Departamento completo


def test_tabla_tiempos_sin_columna_de_conexidad(carpetas):
    """Un CSV viejo (sin ya_fuertemente_conexa) no rompe las tablas: se muestra '—'."""
    results, _ = carpetas
    df = pd.read_csv(results / "r1_tiempos_componente.csv").drop(columns="ya_fuertemente_conexa")
    df.to_csv(results / "r1_tiempos_componente.csv", index=False)
    md = generar(carpetas)
    bloque = md.split("## Tiempo de")[1].split("## Memoria")[0]
    filas = [l for l in bloque.splitlines() if l.startswith("|")]
    assert filas[0].endswith("| Ya fuertemente conexa |")
    assert filas[2].endswith("| 5 | — |") and filas[3].endswith("| 0 | — |")


def test_pendiente_es_la_mediana_de_us_por_elemento():
    """Pendiente de la recta de referencia, en ms por elemento = mediana(µs por elemento) / 1000.
    Las filas 'no completada' (sin tiempo por elemento) no cuentan."""
    df = pd.DataFrame({"tiempo_por_elemento_us": [2.0, 4.0, 10.0, ""],
                       "tiempo_ms": [1.0, 2.0, 3.0, "no completada"]})
    assert tablas.pendiente_referencia_ms(df) == pytest.approx(4.0 / 1000)
    df_par = pd.DataFrame({"tiempo_por_elemento_us": [2.0, 4.0, 6.0, 10.0]})
    assert tablas.pendiente_referencia_ms(df_par) == pytest.approx(5.0 / 1000)


def test_grafica_tiempos_crea_png(carpetas):
    results, _ = carpetas
    salida = tablas.grafica_tiempos(results)
    assert salida == results / "r1_tiempos_componente.png"
    assert salida.exists() and salida.stat().st_size > 0
    assert salida.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"


def test_grafica_funciona_sin_columna_de_conexidad(carpetas):
    results, _ = carpetas
    df = pd.read_csv(results / "r1_tiempos_componente.csv").drop(columns="ya_fuertemente_conexa")
    df.to_csv(results / "r1_tiempos_componente.csv", index=False)
    assert tablas.grafica_tiempos(results).stat().st_size > 0


def test_main_genera_tablas_y_grafica(carpetas):
    generar(carpetas)
    assert (carpetas[0] / "r1_tiempos_componente.png").exists()

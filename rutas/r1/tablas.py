"""Tablas Markdown de R1, generadas desde los CSV (no se escriben a mano).

Uso (desde la raíz del repo):  .venv/bin/python -m rutas.r1.tablas
Lee results/r1/*.csv y data/processed/lugares_nodos.csv; escribe results/r1/tablas_r1.md
y la gráfica results/r1/r1_tiempos_componente.png.
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")           # sin ventana: la gráfica solo se guarda en un archivo
import matplotlib.pyplot as plt
import pandas as pd

from rutas.config import CATALOGO, DATA_PROCESSED, RESULTS_R1


def _celda(valor, decimales):
    """Texto de una celda: enteros tal cual, decimales con formato fijo, vacío si falta."""
    if pd.isna(valor):
        return ""
    if isinstance(valor, bool):
        return "sí" if valor else "no"
    if isinstance(valor, float):
        return f"{valor:.{decimales}f}"
    return str(valor)


def a_markdown(df, decimales=2):
    """DataFrame -> tabla Markdown. `decimales` es un entero o un dict {columna: entero}."""
    def cuantos(columna):
        return decimales.get(columna, 2) if isinstance(decimales, dict) else decimales

    lineas = ["| " + " | ".join(str(c) for c in df.columns) + " |",
              "|" + "|".join("---" for _ in df.columns) + "|"]
    # Por columnas (no iterrows): iterrows convertiría los enteros a float en tablas mixtas.
    columnas = [[_celda(v, cuantos(c)) for v in df[c].tolist()] for c in df.columns]
    for celdas in zip(*columnas):
        lineas.append("| " + " | ".join(celdas) + " |")
    return "\n".join(lineas)


def _tabla_tamanos(results):
    df = pd.read_csv(results / "r1_tamanos.csv")
    df.columns = ["Red", "Nodos (V)", "Aristas (E)"]
    return a_markdown(df)


def _si_no(valor):
    """'True'/'False' (leído como texto con keep_default_na=False) -> 'sí'/'no'."""
    return {"true": "sí", "false": "no"}.get(str(valor).strip().lower(), "—")


def _tabla_tiempos(results):
    # keep_default_na=False: "no completada" y las celdas vacías se leen como texto
    df = pd.read_csv(results / "r1_tiempos_componente.csv", keep_default_na=False)
    for columna in ("tiempo_ms", "tiempo_por_elemento_us"):
        df[columna] = [v if v == "" or v == "no completada" else float(v) for v in df[columna]]
    # Los CSV anteriores a la revisión 1 no traen la conexidad: se muestra "—"
    if "ya_fuertemente_conexa" not in df.columns:
        df["ya_fuertemente_conexa"] = "—"
    else:
        df["ya_fuertemente_conexa"] = [_si_no(v) for v in df["ya_fuertemente_conexa"]]
    df = df.rename(columns={"red": "Red", "V_mas_E": "V + E", "tiempo_ms": "Tiempo (ms)",
                            "tiempo_por_elemento_us": "Tiempo por elemento (µs)",
                            "repeticiones": "Repeticiones",
                            "ya_fuertemente_conexa": "Ya fuertemente conexa"})
    return a_markdown(df, {"Tiempo (ms)": 2, "Tiempo por elemento (µs)": 3})


def _tabla_memoria(results):
    df = pd.read_csv(results / "r1_memoria.csv")
    df = df.rename(columns={"red": "Red", "representacion": "Representación",
                            "supuesto": "Supuesto", "bytes": "Tamaño (B)", "MB": "Tamaño (MB)"})
    return a_markdown(df, {"Tamaño (MB)": 3})


def _tabla_velocidades(results):
    df = pd.read_csv(results / "r1_velocidades.csv")
    # Con la celda vacía del Total pandas la lee como float; se muestra como entero.
    df["velocidad_tabla_kmh"] = df["velocidad_tabla_kmh"].astype("Int64").astype(object)
    df = df.rename(columns={"highway": "Tipo de vía",
                            "velocidad_tabla_kmh": "Velocidad de tabla (km/h)", "aristas": "Aristas",
                            "con_maxspeed_osm": "Con maxspeed de OSM",
                            "pct_osm": "OSM (%)", "pct_imputado": "Imputado (%)"})
    return a_markdown(df, 1)


def _tabla_alertas(processed, catalogo):
    lugares = pd.read_csv(Path(processed) / "lugares_nodos.csv")
    nombres = pd.read_csv(catalogo).set_index("id")["nombre"]
    alertados = lugares[lugares["alerta_500m"].astype(str).str.lower() == "true"]
    df = pd.DataFrame({"Lugar": alertados["id_lugar"],
                       "Nombre": [nombres[i] for i in alertados["id_lugar"]],
                       "Distancia al nodo (m)": alertados["distancia_al_nodo_m"]})
    return a_markdown(df)


def _tiempos_completados(results):
    """Filas de r1_tiempos_componente.csv cuya medición terminó, con columnas numéricas."""
    df = pd.read_csv(Path(results) / "r1_tiempos_componente.csv", keep_default_na=False)
    for columna in ("V_mas_E", "tiempo_ms", "tiempo_por_elemento_us"):
        df[columna] = pd.to_numeric(df[columna], errors="coerce")   # "no completada" / "" -> NaN
    return df.dropna(subset=["tiempo_ms", "tiempo_por_elemento_us"])


def pendiente_referencia_ms(df):
    """Pendiente de la recta de referencia, en ms por elemento (V + E).

    Es la mediana de tiempo_por_elemento_us (µs por elemento) dividida entre 1000.
    Las filas sin tiempo por elemento (no completadas) no se cuentan.
    """
    por_elemento = pd.to_numeric(df["tiempo_por_elemento_us"], errors="coerce").dropna()
    return float(por_elemento.median()) / 1000


def grafica_tiempos(results=RESULTS_R1):
    """Dibuja tiempo (ms) contra V + E, un punto por red, y la recta lineal de referencia.

    Si el tiempo crece como V + E, los puntos caen cerca de la recta que pasa por el origen
    con pendiente = mediana del tiempo por elemento. Devuelve la ruta del PNG.
    """
    results = Path(results)
    df = _tiempos_completados(results)
    figura, ejes = plt.subplots(figsize=(7, 4.5))
    ejes.scatter(df["V_mas_E"], df["tiempo_ms"], color="tab:blue", zorder=3)
    for numero, (_, fila) in enumerate(df.iterrows()):
        # Nombres alternados arriba y abajo: dos redes casi iguales no se pisan el texto
        desplazamiento = (-8, -14) if numero % 2 == 0 else (-8, 8)
        ejes.annotate(fila["red"], (fila["V_mas_E"], fila["tiempo_ms"]),
                      textcoords="offset points", xytext=desplazamiento, ha="right", fontsize=8)
    pendiente = pendiente_referencia_ms(df)
    x_max = float(df["V_mas_E"].max()) * 1.05
    ejes.plot([0, x_max], [0, pendiente * x_max], "--", color="gray",
              label=f"referencia lineal ({pendiente * 1000:.2f} µs por elemento)")
    ejes.set_xlabel("V + E (nodos + aristas de la red cruda)")
    ejes.set_ylabel("Tiempo de largest_component (ms)")
    ejes.set_title("R1: tiempo de largest_component (mediana de 5 repeticiones)")
    ejes.legend()
    ejes.grid(alpha=0.3)
    figura.tight_layout()
    salida = results / "r1_tiempos_componente.png"
    figura.savefig(salida, dpi=150)
    plt.close(figura)
    return salida


def main(results=RESULTS_R1, processed=DATA_PROCESSED, catalogo=CATALOGO):
    results = Path(results)
    partes = [
        "# Tablas de R1\n\nGeneradas por `rutas/r1/tablas.py` desde los CSV de `results/r1/`.",
        "## Tamaño de la red\n\n" + _tabla_tamanos(results),
        "## Tiempo de `largest_component` por red cruda\n\n" + _tabla_tiempos(results),
        "## Memoria: matriz vs listas de adyacencia\n\n" + _tabla_memoria(results),
        "## Velocidades por tipo de vía (componente)\n\n" + _tabla_velocidades(results),
        "## Lugares con alerta (a más de 500 m de su nodo)\n\n"
        + _tabla_alertas(processed, catalogo),
    ]
    (results / "tablas_r1.md").write_text("\n\n".join(partes) + "\n", encoding="utf-8")
    print(f"Tablas escritas en {results / 'tablas_r1.md'}")
    print(f"Gráfica escrita en {grafica_tiempos(results)}")


if __name__ == "__main__":
    main()

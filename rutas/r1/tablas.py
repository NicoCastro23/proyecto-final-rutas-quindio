"""Tablas Markdown de R1, generadas desde los CSV (no se escriben a mano).

Uso (desde la raíz del repo):  .venv/bin/python -m rutas.r1.tablas
Lee results/r1/*.csv y data/processed/lugares_nodos.csv; escribe results/r1/tablas_r1.md.
"""
from pathlib import Path

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


def _tabla_tiempos(results):
    # keep_default_na=False: "no completada" y las celdas vacías se leen como texto
    df = pd.read_csv(results / "r1_tiempos_componente.csv", keep_default_na=False)
    for columna in ("tiempo_ms", "tiempo_por_elemento_us"):
        df[columna] = [v if v == "" or v == "no completada" else float(v) for v in df[columna]]
    df = df.rename(columns={"red": "Red", "V_mas_E": "V + E", "tiempo_ms": "Tiempo (ms)",
                            "tiempo_por_elemento_us": "Tiempo por elemento (µs)",
                            "repeticiones": "Repeticiones"})
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


if __name__ == "__main__":
    main()

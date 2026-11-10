"""Cociente, gráfica y tablas de R2, generados desde los CSV/JSON (no se escriben a mano).

Uso (desde la raíz del repo):  .venv/bin/python -m rutas.r2.tablas
Lee results/r2/r2_dijkstra.csv, r2_pares.json, r2_asimetria.json y maquina.json; escribe
r2_cociente.csv, r2_tiempo_vs_explorados.png y tablas_r2.md en la misma carpeta.
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")           # sin ventana: la gráfica solo se guarda en un archivo
import matplotlib.pyplot as plt
import pandas as pd

from rutas.config import RESULTS_R2
from rutas.r1.tablas import a_markdown

UMBRAL_LOG = 100                # eje y logarítmico si el mayor tiempo es >= 100 veces el menor


def _con_tiempo_numerico(df):
    """Copia con tiempo_ms numérico: "no completada" (texto) pasa a NaN."""
    df = df.copy()
    df["tiempo_ms"] = pd.to_numeric(df["tiempo_ms"], errors="coerce")
    return df


def _leer_mediciones(results):
    # keep_default_na=False: "no completada" se lee como texto
    return pd.read_csv(Path(results) / "r2_dijkstra.csv", keep_default_na=False)


def cociente(df):
    """Mediana, mínimo y máximo de (tiempo_ms lineal / tiempo_ms cola) en los pares cercanos.

    Se empareja por (origen, destino); un par cuya lineal o cola no se completó no cuenta.
    """
    df = _con_tiempo_numerico(df).dropna(subset=["tiempo_ms"])
    lineal = df[df.version == "lineal"].set_index(["origen", "destino"])["tiempo_ms"]
    cola = df[df.version == "cola_prioridad"].set_index(["origen", "destino"])["tiempo_ms"]
    razones = (lineal / cola).dropna()          # solo los pares que tienen ambas
    return {"mediana": float(razones.median()), "minimo": float(razones.min()),
            "maximo": float(razones.max())}


def usar_escala_log(df):
    """True si max(tiempo_ms) / min(tiempo_ms) >= 100 entre las filas completadas."""
    tiempos = _con_tiempo_numerico(df)["tiempo_ms"].dropna()
    return bool(tiempos.max() / tiempos.min() >= UMBRAL_LOG)


def grafica_tiempo_vs_explorados(results=RESULTS_R2):
    """Nodos explorados (x) contra tiempo en ms (y), un color y marcador por versión."""
    results = Path(results)
    df = _con_tiempo_numerico(_leer_mediciones(results)).dropna(subset=["tiempo_ms"])
    figura, ejes = plt.subplots(figsize=(7, 4.5))
    estilos = {"lineal": ("tab:blue", "o"), "cola_prioridad": ("tab:orange", "^")}
    for version, (color, marcador) in estilos.items():
        datos = df[df.version == version]
        ejes.scatter(datos["nodos_explorados"], datos["tiempo_ms"], color=color, marker=marcador,
                     label=version, zorder=3)
    etiqueta_y = "Tiempo (ms)"
    if usar_escala_log(df):
        ejes.set_yscale("log")
        etiqueta_y = "Tiempo (ms, escala logarítmica)"
    ejes.set_xlabel("Nodos explorados")
    ejes.set_ylabel(etiqueta_y)
    ejes.set_title("R2: tiempo de Dijkstra vs nodos explorados (mediana de 5 repeticiones)")
    ejes.legend()
    ejes.grid(alpha=0.3)
    figura.tight_layout()
    salida = results / "r2_tiempo_vs_explorados.png"
    figura.savefig(salida, dpi=150)
    plt.close(figura)
    return salida


def _tabla_mediciones(df):
    df = df.copy()
    df["tiempo_ms"] = [v if v == "no completada" else float(v) for v in df["tiempo_ms"]]
    df = df.rename(columns={"origen": "Origen", "destino": "Destino", "version": "Versión",
                            "tiempo_viaje_s": "Tiempo de viaje (s)",
                            "nodos_explorados": "Nodos explorados", "tiempo_ms": "Tiempo (ms)",
                            "tipo": "Tipo", "distancia_m": "Distancia (m)",
                            "repeticiones": "Repeticiones"})
    return a_markdown(df, {"Tiempo de viaje (s)": 2, "Tiempo (ms)": 3, "Distancia (m)": 1})


def _tabla_cociente(c):
    df = pd.DataFrame({"Mediana": [c["mediana"]], "Mínimo": [c["minimo"]], "Máximo": [c["maximo"]]})
    return a_markdown(df, 2)


def _tabla_asimetria(a):
    df = pd.DataFrame({"Pares asimétricos": [a["pares_asimetricos"]],
                       "Par de mayor diferencia": [" y ".join(a["par_max"] or [])],
                       "Diferencia máxima (s)": [a["diferencia_max"]],
                       "M[i][j] (s)": [a["M_ij"]], "M[j][i] (s)": [a["M_ji"]]})
    return a_markdown(df, 2)


def _leer_json(ruta):
    return json.loads(Path(ruta).read_text(encoding="utf-8"))


def main(results=RESULTS_R2):
    results = Path(results)
    df = _leer_mediciones(results)
    c = cociente(df)
    pd.DataFrame([c], columns=["mediana", "minimo", "maximo"]).to_csv(
        results / "r2_cociente.csv", index=False)
    grafica = grafica_tiempo_vs_explorados(results)

    pares = _leer_json(results / "r2_pares.json")
    maquina = _leer_json(results / "maquina.json")
    no_completadas = int((df["tiempo_ms"] == "no completada").sum())
    aviso = ""
    if no_completadas:
        aviso = (f"\n\nAviso: {no_completadas} medición(es) \"no completada\"; "
                 "los pares correspondientes se excluyen del cociente.")
    partes = [
        "# Tablas de R2\n\nGeneradas por `rutas/r2/tablas.py` desde los CSV/JSON de `results/r2/`.",
        "## Mediciones (mediana de las repeticiones)\n\n" + _tabla_mediciones(df),
        "## Cociente de tiempos lineal / cola de prioridad (10 pares cercanos)\n\n"
        + _tabla_cociente(c) + aviso,
        f"## Pares y semilla\n\nSemilla: {pares['semilla']} (`{pares['generador']}`). "
        f"{pares['regla']}.",
        "## Asimetría de la matriz de tiempos\n\n" + _tabla_asimetria(_leer_json(results / "r2_asimetria.json")),
        "## Máquina\n\n" + "\n".join(f"- {k}: {v}" for k, v in maquina.items()),
    ]
    (results / "tablas_r2.md").write_text("\n\n".join(partes) + "\n", encoding="utf-8")
    print(f"Cociente: {c}")
    print(f"Tablas escritas en {results / 'tablas_r2.md'}")
    print(f"Gráfica escrita en {grafica}")


if __name__ == "__main__":
    main()

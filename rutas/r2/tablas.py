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
import numpy as np
import pandas as pd

from rutas.config import RESULTS_R2
from rutas.r1.tablas import a_markdown

# Unidad y factor con que se muestra la pendiente del ajuste (la cola es tan pequeña que en ms/nodo
# se leería 0.0003; en µs/nodo se lee). ajuste_tiempo_explorados sigue devolviendo ms/nodo.
UNIDAD_PENDIENTE = {"lineal": ("ms/nodo", 1), "cola_prioridad": ("µs/nodo", 1000)}

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


def cociente_por_par(df):
    """Una fila por par cercano: nodos explorados, tiempos lineal y cola (ms) y su cociente.

    Los pares con alguna de las dos versiones "no completada" no aparecen. Orden: por explorados.
    """
    df = _con_tiempo_numerico(df).dropna(subset=["tiempo_ms"])
    clave = ["origen", "destino"]
    lineal = df[df.version == "lineal"].set_index(clave)
    cola = df[df.version == "cola_prioridad"].set_index(clave)
    tabla = pd.DataFrame({"nodos_explorados": cola["nodos_explorados"],
                          "lineal_ms": lineal["tiempo_ms"], "cola_ms": cola["tiempo_ms"]})
    tabla = tabla.dropna(subset=["lineal_ms", "cola_ms"]).reset_index()   # solo pares con ambas
    tabla["cociente"] = tabla["lineal_ms"] / tabla["cola_ms"]
    return tabla.sort_values("nodos_explorados", kind="stable").reset_index(drop=True)


def ajuste_tiempo_explorados(df):
    """Ajuste por mínimos cuadrados tiempo_ms ~ ordenada + pendiente * nodos_explorados, por versión.

    Pendiente en ms/nodo y ordenada en ms (numpy.polyfit de grado 1, solo mediciones completadas).
    """
    df = _con_tiempo_numerico(df).dropna(subset=["tiempo_ms"])
    ajuste = {}
    for version in ("lineal", "cola_prioridad"):
        datos = df[df.version == version]
        pendiente, ordenada = np.polyfit(datos["nodos_explorados"].astype(float),
                                         datos["tiempo_ms"], 1)
        ajuste[version] = {"pendiente": float(pendiente), "ordenada": float(ordenada)}
    return ajuste


def titulo_grafica(df):
    """Título con el número de repeticiones leído del CSV (si varía: "1 a 5"). Ignora las 0."""
    reps = pd.to_numeric(df["repeticiones"], errors="coerce")
    reps = reps[reps > 0]                       # las "no completada" guardan 0 repeticiones
    minimo, maximo = int(reps.min()), int(reps.max())
    cuantas = str(minimo) if minimo == maximo else f"{minimo} a {maximo}"
    return f"R2: tiempo de Dijkstra vs nodos explorados (mediana de {cuantas} repeticiones)"


def usar_escala_log(df):
    """True si max(tiempo_ms) / min(tiempo_ms) >= 100 entre las filas completadas."""
    tiempos = _con_tiempo_numerico(df)["tiempo_ms"].dropna()
    return bool(tiempos.max() / tiempos.min() >= UMBRAL_LOG)


def grafica_tiempo_vs_explorados(results=RESULTS_R2):
    """Nodos explorados (x) contra tiempo en ms (y), un color y marcador por versión."""
    results = Path(results)
    crudo = _leer_mediciones(results)
    df = _con_tiempo_numerico(crudo).dropna(subset=["tiempo_ms"])
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
    ejes.set_title(titulo_grafica(crudo))
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


def _tabla_cociente_por_par(df):
    tabla = cociente_por_par(df).rename(columns={
        "origen": "Origen", "destino": "Destino", "nodos_explorados": "Nodos explorados",
        "lineal_ms": "Lineal (ms)", "cola_ms": "Cola (ms)", "cociente": "Cociente"})
    return a_markdown(tabla, {"Lineal (ms)": 3, "Cola (ms)": 3, "Cociente": 2})


def _tabla_ajuste(ajuste):
    unidades = [UNIDAD_PENDIENTE[version] for version in ajuste]
    df = pd.DataFrame({"Versión": list(ajuste),
                       "Pendiente": [a["pendiente"] * factor
                                     for a, (_, factor) in zip(ajuste.values(), unidades)],
                       "Unidad de la pendiente": [unidad for unidad, _ in unidades],
                       "Ordenada (ms)": [a["ordenada"] for a in ajuste.values()]})
    return a_markdown(df, 4)


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
        "## Cociente por par cercano, con nodos explorados\n\n" + _tabla_cociente_por_par(df),
        "## Ajuste tiempo_ms ≈ a + b · nodos_explorados (mínimos cuadrados, por versión)\n\n"
        + _tabla_ajuste(ajuste_tiempo_explorados(df)),
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

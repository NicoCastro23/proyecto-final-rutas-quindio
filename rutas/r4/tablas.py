"""Tablas y gráfica de R4, generadas desde los archivos (no se escriben a mano).

Uso (desde la raíz del repo):  .venv/bin/python -m rutas.r4.tablas
Lee results/r4/ (r4_exactas.csv, r4_memoria.csv, r4_calidad.csv, r4_itinerario.csv/json,
r4_instancias.json, maquina.json) y escribe tablas_r4.md y r4_tiempo_vs_k.png en esa carpeta.
Si falta un archivo, esa sección se reemplaza por una nota y lo demás se genera igual.
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")           # sin ventana: la gráfica solo se guarda en un archivo
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.ticker import MaxNLocator  # noqa: E402
import pandas as pd  # noqa: E402

from rutas.config import RESULTS_R4  # noqa: E402
from rutas.r1.tablas import a_markdown  # noqa: E402
from rutas.r4.conteos import conteos_teoricos  # noqa: E402

NOMBRES_METODO = {"fuerza_bruta": "Fuerza bruta", "held_karp": "Held-Karp"}
NO_COMPLETADA = "no completada"


def _tiempo(valor):
    """Lo que el CSV guarda vacío (método no completado o no ejecutado) queda como None."""
    return None if valor == "" else float(valor)


def _tiempos_ok(df, metodo):
    """{k: tiempo_ms} de las filas medidas con éxito de un método."""
    filas = df[(df["metodo"] == metodo) & (df["estado"] == "ok")]
    return {int(k): _tiempo(t) for k, t in zip(filas["k"], filas["tiempo_ms"])}


def tabla_exactas(df):
    """Tabla del Anexo: k | tiempo FB (ms) | tiempo HK (ms), más las repeticiones de cada uno."""
    fb, hk = _tiempos_ok(df, "fuerza_bruta"), _tiempos_ok(df, "held_karp")
    repeticiones = {(int(k), m): int(r) for k, m, r in zip(df["k"], df["metodo"], df["repeticiones"])}
    filas = []
    for k in sorted(int(k) for k in df["k"].unique()):
        filas.append({"k": k,
                      "Tiempo fuerza bruta (ms)": fb.get(k, NO_COMPLETADA),   # no_completada y no_ejecutada
                      "Tiempo Held-Karp (ms)": hk.get(k, NO_COMPLETADA),
                      "Repeticiones fuerza bruta": repeticiones[(k, "fuerza_bruta")],
                      "Repeticiones Held-Karp": repeticiones[(k, "held_karp")]})
    return a_markdown(pd.DataFrame(filas), 3)


def tabla_mayor_k(df):
    """El mayor k que cada método resolvió dentro del límite de 5 min."""
    filas = []
    for metodo, nombre in NOMBRES_METODO.items():
        resueltos = _tiempos_ok(df, metodo)
        filas.append({"Método": nombre, "Mayor k resuelto": max(resueltos) if resueltos else "ninguno"})
    return a_markdown(pd.DataFrame(filas))


def tabla_cocientes(df):
    """t(k+1)/t(k) medido frente al predicho: (k+1)²/k para la FB (Θ(k·k!)) y 2((k+1)/k)² para
    Held-Karp (Θ(k²·2^k)). Solo donde ambos k se midieron con éxito."""
    fb, hk = _tiempos_ok(df, "fuerza_bruta"), _tiempos_ok(df, "held_karp")
    ks = sorted(int(k) for k in df["k"].unique())
    filas = []
    for k in ks[:-1]:
        fila = {"k": f"{k} a {k + 1}"}
        for nombre, tiempos, predicho in (("FB", fb, (k + 1) ** 2 / k),
                                          ("HK", hk, 2 * ((k + 1) / k) ** 2)):
            hay_ambos = k in tiempos and k + 1 in tiempos
            fila[f"{nombre} medido"] = tiempos[k + 1] / tiempos[k] if hay_ambos else "—"
            fila[f"{nombre} predicho"] = predicho if hay_ambos else "—"
        filas.append(fila)
    return a_markdown(pd.DataFrame(filas))


def grafica_tiempo_vs_k(results=RESULTS_R4):
    """Tiempo (ms, escala logarítmica) frente a k, una curva por método con las filas `ok`.
    Devuelve la ruta del PNG, o None si todavía no existe r4_exactas.csv."""
    results = Path(results)
    if not (results / "r4_exactas.csv").exists():
        return None
    df = pd.read_csv(results / "r4_exactas.csv", keep_default_na=False)
    fig, ax = plt.subplots(figsize=(8, 5))
    for metodo, nombre in NOMBRES_METODO.items():
        tiempos = _tiempos_ok(df, metodo)
        sin_completar = df[(df["metodo"] == metodo) & (df["estado"] == "no_completada")]
        etiqueta = nombre
        if len(sin_completar):
            etiqueta += f" (no completada desde k = {int(sin_completar['k'].min())})"
        ax.plot(list(tiempos), list(tiempos.values()), marker="o", label=etiqueta)
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))   # k es entero: sin marcas como 5,5
    ax.set_yscale("log")                  # FB crece como k! y HK como 2^k: en lineal no se ve HK
    ax.set_xlabel("k (lugares a visitar)")
    ax.set_ylabel("Tiempo (ms, escala logarítmica)")
    ax.set_title("R4: tiempo de fuerza bruta y Held-Karp frente a k")
    ax.legend()
    ax.grid(True, which="both", alpha=0.3)
    ruta = results / "r4_tiempo_vs_k.png"
    fig.savefig(ruta, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return ruta


def _leer_json(ruta):
    return json.loads(Path(ruta).read_text(encoding="utf-8"))


def _leer_csv(ruta):
    return pd.read_csv(ruta, keep_default_na=False)


def _nota_falta(archivo, que_hacer):
    return f"_El archivo `{archivo}` todavía no existe: {que_hacer}._"


def _seccion_exactas(results):
    ruta = results / "r4_exactas.csv"
    if not ruta.exists():
        return ("## Tiempos de fuerza bruta y Held-Karp\n\n"
                + _nota_falta("r4_exactas.csv", "corre `.venv/bin/python -m rutas.r4.medir_exactas`"))
    df = _leer_csv(ruta)
    return ("## Tiempos de fuerza bruta y Held-Karp\n\n"
            "Mediana de las repeticiones, en milisegundos (ms). «no completada»: pasó el límite de "
            "5 min (o no se ejecutó porque un k menor ya lo pasó).\n\n" + tabla_exactas(df)
            + "\n\n## Mayor k resuelto\n\n" + tabla_mayor_k(df)
            + "\n\n## Cocientes t(k+1)/t(k): medidos y predichos\n\n" + tabla_cocientes(df))


def _seccion_memoria(results):
    ruta = results / "r4_memoria.csv"
    if not ruta.exists():
        return ("## Memoria de Held-Karp\n\n"
                + _nota_falta("r4_memoria.csv", "corre `.venv/bin/python -m rutas.r4.medir_memoria`"))
    df = _leer_csv(ruta).rename(columns={
        "celdas": "Celdas (k·2^k)", "bytes_estimados": "Estimada (B)", "mb_estimados": "Estimada (MB)",
        "pico_tracemalloc_bytes": "Pico tracemalloc (B)", "pico_tracemalloc_mb": "Pico tracemalloc (MB)"})
    return ("## Memoria de Held-Karp: estimada frente a medida\n\n"
            "Estimada: 12 B por celda (8 B del costo y 4 B del predecesor). El pico de `tracemalloc` es "
            "mayor porque en Python cada fila es un objeto `list` y cada costo un objeto `float`.\n\n"
            + a_markdown(df, {"Estimada (MB)": 3, "Pico tracemalloc (MB)": 3}))


def _seccion_conteos():
    filas = []
    for k in range(5, 13):
        c = conteos_teoricos(k)
        filas.append({"k": k, "Transiciones Held-Karp": c["transiciones_hk"],
                      "Permutaciones fuerza bruta (k!)": c["permutaciones_fb"],
                      "Tramos sumados fuerza bruta ((k+1)·k!)": c["tramos_fb"]})
    return "## Conteos teóricos\n\n" + a_markdown(pd.DataFrame(filas))


def _seccion_calidad(results):
    ruta = results / "r4_calidad.csv"
    if not ruta.exists():
        return ("## Calidad del vecino más cercano\n\n"
                + _nota_falta("r4_calidad.csv", "corre `.venv/bin/python -m rutas.r4.calidad`"))
    df = _leer_csv(ruta).rename(columns={
        "instancias": "Instancias", "brecha_promedio_pct": "Brecha promedio (%)",
        "brecha_maxima_pct": "Brecha máxima (%)"})
    return ("## Calidad del vecino más cercano frente a Held-Karp\n\n"
            "Brecha = (voraz − óptimo) / óptimo × 100.\n\n" + a_markdown(df, 2))


def _seccion_itinerario(results):
    ruta_csv, ruta_json = results / "r4_itinerario.csv", results / "r4_itinerario.json"
    if not (ruta_csv.exists() and ruta_json.exists()):
        return ("## Itinerario de un día\n\n"
                + _nota_falta("r4_itinerario.csv` y `r4_itinerario.json",
                              "corre `.venv/bin/python -m rutas.r4.itinerario`"))
    df, datos = _leer_csv(ruta_csv), _leer_json(ruta_json)
    visitas = [v if v == "—" else float(v) for v in df["visita_min"]]    # "—" en la fila Regreso
    tabla = pd.DataFrame({"Orden": df["orden"].astype(str), "Lugar": df["lugar"],
                          "Desplazamiento desde el anterior (min)": df["desplazamiento_min"],
                          "Visita (min)": pd.Series(visitas, dtype=object),
                          "Tiempo acumulado (h)": df["acumulado_h"]})
    tabla = a_markdown(tabla, {"Desplazamiento desde el anterior (min)": 1, "Visita (min)": 1,
                               "Tiempo acumulado (h)": 2})
    partes = [f"## Itinerario de un día\n\nPartida: {datos['partida']['lugar']} ({datos['partida']['id']}). "
              f"Atractivos iniciales: {', '.join(datos['atractivos_iniciales'])}. "
              f"Jornada máxima: {datos['jornada_max_min']} min.", tabla]
    if datos["quitados"]:
        quitados = pd.DataFrame(datos["quitados"]).rename(columns={
            "id": "Id", "lugar": "Atractivo quitado", "jornada_antes_min": "Jornada antes (min)",
            "jornada_despues_min": "Jornada después (min)", "ahorro_min": "Ahorro (min)"})
        partes.append("Atractivos quitados, en orden:\n\n"
                      + a_markdown(quitados[["Id", "Atractivo quitado", "Jornada antes (min)",
                                             "Jornada después (min)", "Ahorro (min)"]], 1))
    t = datos["totales"]
    partes.append(f"- Visitas: {t['visitas_min']:.1f} min\n- Desplazamientos: {t['desplazamientos_min']:.1f} min\n"
                  f"- Jornada: {t['jornada_min']:.1f} min ({t['jornada_h']:.2f} h)\n"
                  f"- Cabe en la jornada: {'sí' if datos['cabe'] else 'no'}")
    return "\n\n".join(partes)


def _seccion_semillas(results):
    ruta = results / "r4_instancias.json"
    if not ruta.exists():
        return ("## Semillas y muestra\n\n"
                + _nota_falta("r4_instancias.json", "corre `.venv/bin/python -m rutas.r4.instancias`"))
    d = _leer_json(ruta)
    semillas = d["semillas_calidad"]
    return ("## Semillas y muestra\n\n"
            f"- Semilla de la muestra anidada: {d['semilla']} (`{d['generador']}`), partida {d['partida']}.\n"
            f"- Muestra anidada (cada k usa los primeros k): {', '.join(d['muestra_anidada'])}.\n"
            f"- Semillas de las instancias de calidad: {min(semillas)}..{max(semillas)}.")


def _seccion_maquina(results):
    ruta = results / "maquina.json"
    if not ruta.exists():
        return "## Máquina\n\n" + _nota_falta("maquina.json", "lo escribe `rutas.r4.medir_exactas`")
    return "## Máquina\n\n" + "\n".join(f"- {k}: {v}" for k, v in _leer_json(ruta).items())


def main(results=RESULTS_R4):
    results = Path(results)
    results.mkdir(parents=True, exist_ok=True)
    grafica = grafica_tiempo_vs_k(results)
    partes = ["# Tablas de R4\n\nGeneradas por `rutas/r4/tablas.py` desde los archivos de `results/r4/`. "
              "Los tiempos están en milisegundos (ms) y los tiempos de recorrido en segundos (s).",
              _seccion_exactas(results), _seccion_memoria(results), _seccion_conteos(),
              _seccion_calidad(results), _seccion_itinerario(results), _seccion_semillas(results),
              _seccion_maquina(results)]
    if grafica is not None:
        partes.insert(2, f"Gráfica: `{grafica.name}` (eje y logarítmico).")
    (results / "tablas_r4.md").write_text("\n\n".join(partes) + "\n", encoding="utf-8")
    print(f"Tablas escritas en {results / 'tablas_r4.md'}")
    if grafica is None:
        print("Aviso: falta r4_exactas.csv; no se generó la gráfica ni la tabla de tiempos.")
    else:
        print(f"Gráfica escrita en {grafica}")


if __name__ == "__main__":
    main()

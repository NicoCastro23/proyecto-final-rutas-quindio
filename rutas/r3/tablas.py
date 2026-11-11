"""Tablas y gráfica de R3, generadas desde los archivos (no se escriben a mano).

Uso (desde la raíz del repo):  .venv/bin/python -m rutas.r3.tablas
Lee results/r3/r3_envolvente.csv, r3_puntos.json, maquina.json y data/processed/envolvente.geojson;
escribe tablas_r3.md y r3_envolvente.png en results/r3/.
"""
import json
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")           # sin ventana: la gráfica solo se guarda en un archivo
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

from rutas.config import DATA_PROCESSED, RESULTS_R3  # noqa: E402
from rutas.r1.persistencia import cargar_grafo_procesado  # noqa: E402
from rutas.r1.tablas import a_markdown  # noqa: E402
from rutas.r3.envolvente import area  # noqa: E402
from rutas.r3.medir_envolvente import NOMBRE_RED  # noqa: E402
from rutas.r3.puntos import puntos_de_grafo  # noqa: E402


def grafica_envolvente(processed=DATA_PROCESSED, salida=RESULTS_R3):
    """Nodos de la red y polígono de la envolvente, en metros UTM. Devuelve la ruta del PNG."""
    puntos = puntos_de_grafo(cargar_grafo_procesado(processed))
    tabla = pd.read_csv(Path(processed) / "envolvente.csv")
    vertices = list(zip(tabla["x_utm"], tabla["y_utm"]))
    area_km2 = area(vertices) / 1e6

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.scatter([x for x, _ in puntos], [y for _, y in puntos], s=2, color="gray", label="Nodos de la red")
    cerrado = vertices + vertices[:1]               # se repite el primero para cerrar el polígono
    ax.plot([x for x, _ in cerrado], [y for _, y in cerrado], color="red", marker="o", markersize=4,
            label="Envolvente convexa")
    ax.set_xlabel("x UTM (m)")
    ax.set_ylabel("y UTM (m)")
    ax.set_aspect("equal")                          # 1 m en x = 1 m en y: el polígono no se deforma
    ax.set_title(f"Envolvente convexa: {len(puntos)} nodos, {len(vertices)} vértices, "
                 f"área {area_km2:.1f} km²")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.1), ncol=2)   # debajo de los ejes: no tapa el polígono

    salida = Path(salida)
    salida.mkdir(parents=True, exist_ok=True)
    ruta = salida / "r3_envolvente.png"
    fig.savefig(ruta, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return ruta


def referencia_renyi_sulanke(n):
    """Número esperado de vértices de n puntos uniformes en un cuadrado: (8/3) ln n (Rényi y Sulanke, 1963)."""
    return 8 / 3 * math.log(n)


def _leer_json(ruta):
    return json.loads(Path(ruta).read_text(encoding="utf-8"))


def _numero_o_texto(valor):
    """"no completada" (texto) se deja igual; lo demás es un número."""
    return valor if valor == "no completada" else float(valor)


def _con_miles(serie):
    """Enteros con espacio de miles ("10 000"), como en el nombre del conjunto. Solo presentación."""
    return [f"{int(v):,}".replace(",", " ") for v in serie]


def _tabla_anexo(df):
    """La tabla del Anexo (conjunto, n, vértices, tiempos en ms y cociente) más las repeticiones."""
    df = df.copy()
    df["n"] = _con_miles(df["n"])
    for columna in ("tiempo_propio_ms", "tiempo_scipy_ms", "cociente"):
        df[columna] = [_numero_o_texto(v) for v in df[columna]]
    df = df.rename(columns={"conjunto": "Conjunto de puntos", "vertices": "Vértices de la envolvente",
                            "tiempo_propio_ms": "Tiempo propio (ms)",
                            "tiempo_scipy_ms": "Tiempo SciPy (ms)", "cociente": "Cociente",
                            "repeticiones": "Repeticiones"})
    return a_markdown(df, {"Tiempo propio (ms)": 3, "Tiempo SciPy (ms)": 3, "Cociente": 1})


def _tabla_vertices_esperados(df):
    """Solo los cuadrados (la red no es uniforme): vértices obtenidos frente a (8/3) ln n."""
    cuadrados = df[df["conjunto"] != NOMBRE_RED]
    tabla = pd.DataFrame({"Conjunto de puntos": cuadrados["conjunto"], "n": _con_miles(cuadrados["n"]),
                          "Vértices obtenidos": cuadrados["vertices"],
                          "(8/3) ln n": [referencia_renyi_sulanke(n) for n in cuadrados["n"]]})
    return a_markdown(tabla, {"(8/3) ln n": 1})


def _tabla_puntos(puntos):
    tabla = pd.DataFrame(puntos["conjuntos"])
    for columna in ("n_pedido", "n_obtenido"):
        tabla[columna] = _con_miles(tabla[columna])
    tabla = tabla.rename(columns={
        "conjunto": "Conjunto de puntos", "n_pedido": "n pedido", "n_obtenido": "n obtenido"})
    return a_markdown(tabla)


def main(results=RESULTS_R3, processed=DATA_PROCESSED):
    results = Path(results)
    # keep_default_na=False: "no completada" se lee como texto
    df = pd.read_csv(results / "r3_envolvente.csv", keep_default_na=False)
    puntos = _leer_json(results / "r3_puntos.json")
    maquina = _leer_json(results / "maquina.json")
    propiedades = _leer_json(Path(processed) / "envolvente.geojson")["features"][0]["properties"]
    grafica = grafica_envolvente(processed, results)

    partes = [
        "# Tablas de R3\n\nGeneradas por `rutas/r3/tablas.py` desde los archivos de `results/r3/`. "
        "Todos los tiempos están en milisegundos (ms): mediana de las repeticiones.",
        "## Envolvente convexa: QuickHull propio frente a SciPy\n\n" + _tabla_anexo(df),
        "## Vértices frente a (8/3) ln n\n\n" + _tabla_vertices_esperados(df),
        f"## Puntos y semilla\n\nSemilla: {puntos['semilla']} (`{puntos['generador']}`). "
        f"Cuadrado [0, {puntos['lado']}) x [0, {puntos['lado']}) m, redondeo `{puntos['redondeo']}`. "
        f"{puntos['nota'][:1].upper() + puntos['nota'][1:]}.\n\n" + _tabla_puntos(puntos),
        "## Envolvente de la red\n\n"
        f"- Vértices: {propiedades['vertices']}\n- Área: {propiedades['area_km2']:.3f} km²",
        "## Máquina\n\n" + "\n".join(f"- {k}: {v}" for k, v in maquina.items()),
    ]
    (results / "tablas_r3.md").write_text("\n\n".join(partes) + "\n", encoding="utf-8")
    print(f"Tablas escritas en {results / 'tablas_r3.md'}")
    print(f"Gráfica escrita en {grafica}")


if __name__ == "__main__":
    main()

"""Lógica de la aplicación: funciones puras sobre DatosApp que devuelven dicts (sin Flask ni HTML)."""
import time
from pathlib import Path

import pandas as pd

from rutas.config import RESULTS
from rutas.r1.aristas import mejor_arista
from rutas.r2.dijkstra import consultar
from rutas.r2.ruta import detalle_ruta
from rutas.r4.itinerario import JORNADA_MAX_MIN, itinerario_dia, visitas_del_catalogo
from rutas.r4.por_ids import matriz_a_listas, resolver_por_ids
from rutas.r5.formato import numero


def coordenadas_de(G, ids_nodos):
    """[(lat, lon)] de la ruta siguiendo la geometría real de cada tramo.

    Cada tramo (u, v) usa la geometría de mejor_arista (la misma arista que dio el tiempo).
    Shapely entrega (lon, lat), por eso se invierte. El primer punto de un tramo es el último
    del anterior, así que desde el segundo tramo se omite para no duplicar la unión.
    Con menos de 2 nodos no hay línea que dibujar.
    """
    puntos = []
    for u, v in zip(ids_nodos, ids_nodos[1:]):
        tramo = [(lat, lon) for lon, lat in mejor_arista(G, u, v).geometry.coords]
        puntos.extend(tramo if not puntos else tramo[1:])
    return puntos


class ErrorEntrada(ValueError):
    """Entrada inválida del usuario; la app la convierte en HTTP 400 con el mensaje."""


def validar_lugar(datos, id_lugar):
    """ErrorEntrada si el id no es uno de los lugares cargados."""
    if id_lugar not in datos.nodo_de:
        raise ErrorEntrada(f"lugar desconocido: {id_lugar}")


def ruta_entre(datos, id_origen, id_destino):
    """Ruta más rápida entre dos lugares, calculada en el momento con Dijkstra (cola de prioridad).

    Solo se cronometra la llamada a consultar; el cómputo es informativo (no es la medición de R2).
    El tiempo y la distancia salen de detalle_ruta sobre la ruta encontrada, y coinciden con los
    de consultar porque las dos eligen la misma arista entre paralelas.
    """
    validar_lugar(datos, id_origen)
    validar_lugar(datos, id_destino)
    nodo_origen, nodo_destino = datos.nodo_de[id_origen], datos.nodo_de[id_destino]

    inicio = time.perf_counter()
    _, ids_nodos, explorados = consultar(datos.red, nodo_origen, nodo_destino, "cola_prioridad")
    computo_ms = (time.perf_counter() - inicio) * 1000

    tiempo_s, distancia_m = detalle_ruta(datos.G, ids_nodos)
    aviso = None
    if id_origen == id_destino:
        aviso = "origen y destino son el mismo lugar"
    elif nodo_origen == nodo_destino:
        aviso = "los dos lugares están en el mismo punto de la red"
    return {"origen": id_origen, "destino": id_destino,
            "tiempo_s": tiempo_s, "tiempo_min": tiempo_s / 60, "distancia_km": distancia_m / 1000,
            "nodos_explorados": explorados, "computo_ms": computo_ms,
            "ids_nodos": ids_nodos, "coordenadas": coordenadas_de(datos.G, ids_nodos),
            "aviso": aviso}


def validar_itinerario(datos, id_partida, ids_atractivos):
    """Comprueba la entrada del itinerario sin calcular nada; lanza ErrorEntrada con el primer fallo.

    Orden de las comprobaciones: partida desconocida, cantidad (6 a 8), repetidos, partida entre
    los atractivos, y que cada id sea un atractivo turístico (un id que no existe tampoco lo es).
    """
    validar_lugar(datos, id_partida)
    if not 6 <= len(ids_atractivos) <= 8:
        raise ErrorEntrada(f"elige entre 6 y 8 atractivos (llegaron {len(ids_atractivos)})")
    vistos = set()
    for id_lugar in ids_atractivos:
        if id_lugar in vistos:
            raise ErrorEntrada(f"atractivo repetido: {id_lugar}")
        vistos.add(id_lugar)
    if id_partida in vistos:
        raise ErrorEntrada(f"la partida {id_partida} no puede estar entre los atractivos")
    for id_lugar in ids_atractivos:
        if id_lugar not in datos.atractivos:
            raise ErrorEntrada(f"{id_lugar} no es un atractivo turístico")


def _tramos(datos, recorrido):
    """Un tramo por par consecutivo del recorrido, con su tiempo y sus coordenadas.

    Cada tramo se calcula con Dijkstra (cola de prioridad); su tiempo coincide con el de la matriz
    de R2 porque ella se calculó con la misma función.
    """
    tramos = []
    for desde, hasta in zip(recorrido, recorrido[1:]):
        tiempo_s, ids_nodos, _ = consultar(datos.red, datos.nodo_de[desde], datos.nodo_de[hasta],
                                           "cola_prioridad")
        tramos.append({"desde": desde, "hasta": hasta, "tiempo_min": tiempo_s / 60,
                       "coordenadas": coordenadas_de(datos.G, ids_nodos)})
    return tramos


def _resolver_metodo(datos, id_partida, ids_atractivos, metodo):
    """Resuelve el recorrido con un método de R4 y arma el resumen que muestra la pantalla."""
    inicio = time.perf_counter()
    tiempo_s, recorrido = resolver_por_ids(datos.matriz, id_partida, ids_atractivos, metodo)
    computo_ms = (time.perf_counter() - inicio) * 1000

    desplazamiento_min = tiempo_s / 60
    visitas_min = sum(datos.visita_min[a] for a in ids_atractivos)
    jornada_min = desplazamiento_min + visitas_min
    return {"recorrido": recorrido, "desplazamiento_min": desplazamiento_min,
            "visitas_min": visitas_min, "jornada_min": jornada_min,
            "cabe": jornada_min <= JORNADA_MAX_MIN, "computo_ms": computo_ms,
            "tramos": _tramos(datos, recorrido)}


def _regla_de_las_11_horas(datos, id_partida, ids_atractivos):
    """Aplica la regla de R4 (itinerario_dia) y traduce sus índices de la matriz a ids de lugar."""
    T, ids = matriz_a_listas(datos.matriz)
    indices = [ids.index(a) for a in ids_atractivos]
    visita_por_indice = visitas_del_catalogo(datos.catalogo, ids)
    filas, quitados, totales = itinerario_dia(T, ids, ids.index(id_partida), indices, visita_por_indice)
    return {"cabe_inicial": False,
            "quitados": [{"id": q["id"], "lugar": datos.nombre_de[q["id"]],
                          "visita_min": q["visita_min"], "desvio_min": q["desvio_min"],
                          "ahorro_min": q["ahorro_min"]} for q in quitados],
            "jornada_final_min": totales["jornada_min"],
            "recorrido_final": [id_partida] + [f["id"] for f in filas if f["orden"] != "Regreso"] + [id_partida],
            "cabe_final": totales["cabe"]}


def itinerario(datos, id_partida, ids_atractivos):
    """Compara Held-Karp (óptimo) y vecino más cercano (voraz) para el itinerario pedido.

    Si Held-Karp no cabe en 11 h, agrega en "jornada" lo que haría la regla de R4 (informativo:
    los recorridos y tramos siguen siendo los de los atractivos elegidos).
    """
    validar_itinerario(datos, id_partida, ids_atractivos)
    held_karp = _resolver_metodo(datos, id_partida, ids_atractivos, "held_karp")
    voraz = _resolver_metodo(datos, id_partida, ids_atractivos, "vecino_mas_cercano")

    diferencia_min = voraz["desplazamiento_min"] - held_karp["desplazamiento_min"]
    if diferencia_min < -1e-9:       # el voraz nunca puede ganarle al óptimo: sería un error de datos
        raise RuntimeError("el vecino más cercano salió mejor que Held-Karp")
    base = held_karp["desplazamiento_min"]
    brecha_pct = diferencia_min / base * 100 if base > 0 else 0.0

    jornada = None if held_karp["cabe"] else _regla_de_las_11_horas(datos, id_partida, ids_atractivos)
    return {"partida": id_partida, "atractivos": list(ids_atractivos),
            "held_karp": held_karp, "voraz": voraz,
            "diferencia_min": diferencia_min, "brecha_pct": brecha_pct, "jornada": jornada}


PY = ".venv/bin/python -m"

# Lista fija de lo que muestra cada requerimiento: (archivo, comando que lo genera).
# Solo estos nombres se muestran y se sirven; nada fuera de la lista llega al navegador.
ARCHIVOS_RESULTADOS = {
    "r1": {"imagenes": [("r1_tiempos_componente.png", f"{PY} rutas.r1.tablas")],
           "tablas": [("r1_tamanos.csv", f"{PY} rutas.r1.construir_red"),
                      ("r1_tiempos_componente.csv", f"{PY} rutas.r1.medir_componente"),
                      ("r1_memoria.csv", f"{PY} rutas.r1.construir_red"),
                      ("r1_velocidades.csv", f"{PY} rutas.r1.construir_red")]},
    "r2": {"imagenes": [("r2_tiempo_vs_explorados.png", f"{PY} rutas.r2.tablas")],
           "tablas": [("r2_dijkstra.csv", f"{PY} rutas.r2.medir_dijkstra"),
                      ("r2_cociente.csv", f"{PY} rutas.r2.tablas"),
                      ("r2_pares.csv", f"{PY} rutas.r2.medir_dijkstra")]},
    "r3": {"imagenes": [("r3_envolvente.png", f"{PY} rutas.r3.tablas")],
           "tablas": [("r3_envolvente.csv", f"{PY} rutas.r3.medir_envolvente")]},
    "r4": {"imagenes": [("r4_tiempo_vs_k.png", f"{PY} rutas.r4.tablas")],
           "tablas": [("r4_exactas.csv", f"{PY} rutas.r4.medir_exactas"),
                      ("r4_calidad.csv", f"{PY} rutas.r4.calidad"),
                      ("r4_memoria.csv", f"{PY} rutas.r4.medir_memoria"),
                      ("r4_itinerario.csv", f"{PY} rutas.r4.itinerario")]},
}


def _tabla_html(ruta):
    """CSV -> tabla HTML. Los textos se escapan, las celdas vacías quedan vacías (no "nan") y
    los decimales llevan coma y 3 cifras."""
    tabla = pd.read_csv(ruta, keep_default_na=False)
    return tabla.to_html(index=False, escape=True, border=0, classes="tabla",
                         float_format=lambda x: numero(x, 3))


def resultados(requerimiento, results=RESULTS):
    """Imágenes y tablas de results/<r>/ que existen, y (archivo, comando) de los que faltan.

    Lanza KeyError si el requerimiento no está en la lista fija. Un archivo faltante nunca es
    un error: se avisa con el comando que lo genera.
    """
    grupos = ARCHIVOS_RESULTADOS[requerimiento]
    carpeta = Path(results) / requerimiento
    imagenes, tablas, faltantes = [], [], []
    for archivo, comando in grupos["imagenes"]:
        if (carpeta / archivo).exists():
            imagenes.append(archivo)
        else:
            faltantes.append((archivo, comando))
    for archivo, comando in grupos["tablas"]:
        if (carpeta / archivo).exists():
            tablas.append((archivo, _tabla_html(carpeta / archivo)))
        else:
            faltantes.append((archivo, comando))
    return {"imagenes": imagenes, "tablas": tablas, "faltantes": faltantes}

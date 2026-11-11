"""Itinerario de un día: Held-Karp sobre los atractivos, quitando hasta que quepa la jornada."""
import csv
import json
from pathlib import Path

import pandas as pd

from rutas.config import CATALOGO, MATRIZ_TIEMPOS, RESULTS_R4
from rutas.r2.matriz import cargar_matriz
from rutas.r4.held_karp import held_karp
from rutas.r4.por_ids import matriz_a_listas

JORNADA_MAX_MIN = 660
ATRACTIVOS_DIA = ["A05", "A08", "A04", "A14", "A06", "A07", "A12", "A01"]


def _jornada_min(T, s, atractivos, visita_min):
    """Jornada en minutos = visitas + desplazamientos óptimos (Held-Karp, T está en segundos)."""
    visitas = sum(visita_min[a] for a in atractivos)
    tiempo_s, recorrido = held_karp(T, s, atractivos)
    return visitas + tiempo_s / 60, recorrido


def _validar_atractivos(s, atractivos, visita_min):
    if not 6 <= len(atractivos) <= 8:
        raise ValueError(f"se piden de 6 a 8 atractivos y llegaron {len(atractivos)}")
    if len(set(atractivos)) != len(atractivos):
        raise ValueError("hay atractivos repetidos")
    if s in atractivos:
        raise ValueError("la partida no puede estar entre los atractivos")
    for a in atractivos:
        if a not in visita_min:
            raise ValueError(f"el índice {a} no es un atractivo (no tiene duración de visita)")


def itinerario_dia(T, ids, s, atractivos, visita_min, jornada_max_min=JORNADA_MAX_MIN):
    """Devuelve (filas, quitados, totales) sin redondear.

    T en segundos; ids[i] es el id del índice i; s y atractivos son índices de T; visita_min es
    {índice: minutos} de todos los atractivos del catálogo.
    Mientras la jornada no quepa y queden al menos 2 atractivos, se quita el que deja la menor
    jornada (se recalcula Held-Karp sin cada uno; en un empate, el de menor índice). Si con
    uno solo todavía no cabe, se entrega ese itinerario con totales["cabe"] falso.
    """
    _validar_atractivos(s, atractivos, visita_min)
    actuales = sorted(atractivos)
    jornada, recorrido = _jornada_min(T, s, actuales, visita_min)
    quitados = []
    while jornada > jornada_max_min and len(actuales) >= 2:
        mejor = None                     # (jornada, atractivo, recorrido) del mejor candidato
        for a in actuales:
            resto = [x for x in actuales if x != a]
            j, r = _jornada_min(T, s, resto, visita_min)
            if mejor is None or j < mejor[0]:          # '<' estricto: empate, gana el menor índice
                mejor = (j, a, r)
        nueva_jornada, quitado, recorrido = mejor
        ahorro = jornada - nueva_jornada
        # El ahorro se explica en dos partes: la visita que ya no se hace y el desvío que se evita.
        quitados.append({"id": ids[quitado], "jornada_antes_min": jornada,
                         "jornada_despues_min": nueva_jornada,
                         "ahorro_min": ahorro,
                         "visita_min": visita_min[quitado],
                         "desvio_min": ahorro - visita_min[quitado]})
        actuales.remove(quitado)
        jornada = nueva_jornada

    # Filas: un atractivo por fila siguiendo el recorrido óptimo, y al final el regreso.
    filas, reloj_min, anterior = [], 0.0, s
    for orden, a in enumerate(recorrido[1:-1], start=1):
        desplazamiento = T[anterior][a] / 60
        reloj_min += desplazamiento + visita_min[a]
        filas.append({"orden": orden, "id": ids[a], "desplazamiento_min": desplazamiento,
                      "visita_min": visita_min[a], "acumulado_h": reloj_min / 60})
        anterior = a
    regreso = T[anterior][s] / 60
    reloj_min += regreso
    filas.append({"orden": "Regreso", "id": ids[s], "desplazamiento_min": regreso,
                  "visita_min": None, "acumulado_h": reloj_min / 60})

    visitas = sum(visita_min[a] for a in actuales)
    totales = {"visitas_min": visitas, "desplazamientos_min": sum(f["desplazamiento_min"] for f in filas),
               "jornada_min": jornada, "jornada_h": jornada / 60,
               "cabe": jornada <= jornada_max_min, "atractivos_finales": len(actuales)}
    return filas, quitados, totales


def visitas_del_catalogo(catalogo_df, ids):
    """{índice en ids: duracion_visita_min} solo de los atractivos turísticos del catálogo."""
    categoria = dict(zip(catalogo_df["id"], catalogo_df["categoria"]))
    duracion = dict(zip(catalogo_df["id"], catalogo_df["duracion_visita_min"]))
    return {i: float(duracion[id_lugar]) for i, id_lugar in enumerate(ids)
            if categoria[id_lugar] == "Atractivo turístico"}


def escribir_itinerario(filas, quitados, totales, ids_iniciales, id_partida, nombres, salida):
    """Escribe r4_itinerario.csv y r4_itinerario.json (valores sin redondear).
    nombres = {id: nombre del lugar}; en Regreso la visita se escribe como «—»."""
    salida = Path(salida)
    salida.mkdir(parents=True, exist_ok=True)
    with open(salida / "r4_itinerario.csv", "w", newline="", encoding="utf-8") as archivo:
        escritor = csv.writer(archivo, lineterminator="\n")
        escritor.writerow(["orden", "id", "lugar", "desplazamiento_min", "visita_min", "acumulado_h"])
        for fila in filas:
            visita = "—" if fila["visita_min"] is None else repr(float(fila["visita_min"]))
            escritor.writerow([fila["orden"], fila["id"], nombres[fila["id"]],
                               repr(fila["desplazamiento_min"]), visita, repr(fila["acumulado_h"])])
    datos = {
        "partida": {"id": id_partida, "lugar": nombres[id_partida]},
        "atractivos_iniciales": list(ids_iniciales),
        "quitados": [{**q, "lugar": nombres[q["id"]]} for q in quitados],
        "atractivos_finales": [f["id"] for f in filas if f["orden"] != "Regreso"],
        "totales": {clave: totales[clave]
                    for clave in ("visitas_min", "desplazamientos_min", "jornada_min", "jornada_h")},
        "jornada_max_min": JORNADA_MAX_MIN,
        "cabe": totales["cabe"],
    }
    with open(salida / "r4_itinerario.json", "w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, ensure_ascii=False, indent=2)


def main(matriz=MATRIZ_TIEMPOS, catalogo=CATALOGO, salida=RESULTS_R4, partida="C01",
         atractivos=ATRACTIVOS_DIA):
    """Itinerario por defecto: lee matriz y catálogo, resuelve y escribe los dos archivos."""
    T, ids = matriz_a_listas(cargar_matriz(matriz))
    catalogo_df = pd.read_csv(catalogo)
    nombres = dict(zip(catalogo_df["id"], catalogo_df["nombre"]))
    s = ids.index(partida)
    indices = [ids.index(a) for a in atractivos]
    visita_min = visitas_del_catalogo(catalogo_df, ids)
    filas, quitados, totales = itinerario_dia(T, ids, s, indices, visita_min)
    escribir_itinerario(filas, quitados, totales, atractivos, partida, nombres, salida)
    for q in quitados:
        print(f"quitado {q['id']}: {q['jornada_antes_min']:.1f} -> {q['jornada_despues_min']:.1f} min "
              f"(ahorro {q['ahorro_min']:.1f})")
    print(f"jornada final: {totales['jornada_min']:.1f} min ({totales['jornada_h']:.2f} h); "
          f"cabe: {totales['cabe']}")


if __name__ == "__main__":
    main()

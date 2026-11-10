"""Selección de los 20 pares de lugares que se miden en R2 (semilla fija).

Todo el sorteo sale de un único random.Random(semilla); por eso la misma semilla da siempre
los mismos pares. Los municipios se ordenan antes de barajar para que el resultado no dependa
del orden de las filas del catálogo.
"""
import random

import pandas as pd

SEMILLA = 2026
COLUMNAS = ["origen", "destino", "tipo", "municipio_origen", "municipio_destino",
            "nodo_origen", "nodo_destino"]
MAX_INTENTOS = 100_000      # tope de sorteos por par, para no quedar en un ciclo infinito


def _fila(origen, destino, tipo, municipio, nodo):
    return {"origen": origen, "destino": destino, "tipo": tipo,
            "municipio_origen": municipio[origen], "municipio_destino": municipio[destino],
            "nodo_origen": nodo[origen], "nodo_destino": nodo[destino]}


def _cuantos_pares_validos(lugares, nodo):
    """Pares ordenados de lugares con nodos distintos (el par {T03, T05} no sirve)."""
    return sum(1 for o in lugares for d in lugares if nodo[o] != nodo[d])


def _sortear_cercanos(rng, municipios, por_municipio, nodo, municipio, cantidad):
    """Un par por municipio en cada vuelta, en el orden barajado, hasta tener `cantidad`."""
    elegidos, vistos = [], set()
    validos = {m: _cuantos_pares_validos(por_municipio[m], nodo) for m in municipios}
    usados = {m: 0 for m in municipios}
    while len(elegidos) < cantidad:
        antes = len(elegidos)
        for m in municipios:
            if len(elegidos) == cantidad:
                break
            if usados[m] == validos[m]:         # sin pares válidos por sortear: se salta
                continue
            while True:
                o, d = rng.sample(por_municipio[m], 2)
                if nodo[o] != nodo[d] and (o, d) not in vistos:
                    break
            vistos.add((o, d))
            usados[m] += 1
            elegidos.append(_fila(o, d, "cercano", municipio, nodo))
        if len(elegidos) == antes:
            raise ValueError(f"no hay {cantidad} pares cercanos válidos distintos")
    return elegidos, vistos


def _sortear_lejanos(rng, ids, nodo, municipio, cantidad, vistos):
    """Pares al azar entre todos los lugares, de municipios distintos y sin repetir."""
    elegidos = []
    for _ in range(MAX_INTENTOS):
        if len(elegidos) == cantidad:
            return elegidos
        o, d = rng.sample(ids, 2)
        if municipio[o] != municipio[d] and nodo[o] != nodo[d] and (o, d) not in vistos:
            vistos.add((o, d))
            elegidos.append(_fila(o, d, "lejano", municipio, nodo))
    raise ValueError(f"no se lograron {cantidad} pares lejanos válidos")


def seleccionar_pares(catalogo, lugares_nodos, semilla=SEMILLA, cercanos=10, lejanos=10):
    """DataFrame con `cercanos` pares del mismo municipio y `lejanos` de municipios distintos.

    Los pares son ordenados (A->B y B->A son distintos), sin repetir y con nodos distintos.
    Primero salen los cercanos y luego los lejanos.
    """
    rng = random.Random(semilla)
    ids = list(catalogo["id"])                                   # orden del catálogo
    municipio = dict(zip(catalogo["id"], catalogo["municipio"]))
    nodo = dict(zip(lugares_nodos["id_lugar"], lugares_nodos["id_nodo"]))
    por_municipio = {}
    for id_lugar in ids:
        por_municipio.setdefault(municipio[id_lugar], []).append(id_lugar)

    municipios = sorted(por_municipio)       # ordenar antes de barajar: sorteo reproducible
    rng.shuffle(municipios)
    pares, vistos = _sortear_cercanos(rng, municipios, por_municipio, nodo, municipio, cercanos)
    pares += _sortear_lejanos(rng, ids, nodo, municipio, lejanos, vistos)
    return pd.DataFrame(pares, columns=COLUMNAS)

"""Instancias de R4 con semilla fija: muestra anidada y lotes de calidad (no se cronometra)."""
import json
import random
from pathlib import Path

import pandas as pd

from rutas.config import CATALOGO, RESULTS_R4

SEMILLA = 2026
SEMILLAS_CALIDAD = tuple(range(2026, 2036))     # 10 instancias por k
PARTIDA = "C01"
K_EXACTAS = tuple(range(5, 13))
K_CALIDAD = (5, 8, 10, 12)
KMAX = 12


def otros_ids(ids, partida=PARTIDA):
    """Los ids distintos de la partida, en el orden del catálogo (41 en el catálogo real)."""
    return [i for i in ids if i != partida]


def muestra_anidada(ids, partida=PARTIDA, semilla=SEMILLA, kmax=KMAX):
    """kmax lugares al azar; la instancia de tamaño k usa los primeros k, así las instancias
    de k distintos están anidadas y la medición de k a k+1 solo agrega un lugar."""
    return random.Random(semilla).sample(otros_ids(ids, partida), kmax)


def instancias_calidad(ids, partida=PARTIDA, ks=K_CALIDAD, semillas=SEMILLAS_CALIDAD):
    """Una instancia por (k, semilla), con k externo y semilla interna. Cada una usa un
    generador nuevo para poder reproducirse sola, sin depender de las demás."""
    otros = otros_ids(ids, partida)
    return [{"k": k, "semilla": semilla, "ids": random.Random(semilla).sample(otros, k)}
            for k in ks for semilla in semillas]


def main(catalogo=CATALOGO, salida=RESULTS_R4):
    """Escribe r4_instancias.json (documentación de las semillas y los ids sorteados)."""
    ids = list(pd.read_csv(catalogo)["id"])
    datos = {
        "semilla": SEMILLA,
        "generador": "random.Random(semilla).sample(otros, k)",
        "partida": PARTIDA,
        "otros": "los ids distintos de la partida, en orden del catálogo",
        "k_exactas": list(K_EXACTAS),
        "muestra_anidada": muestra_anidada(ids),
        "regla_anidada": "cada k usa los primeros k",
        "semillas_calidad": list(SEMILLAS_CALIDAD),
        "calidad": instancias_calidad(ids),
    }
    salida = Path(salida)
    salida.mkdir(parents=True, exist_ok=True)
    with open(salida / "r4_instancias.json", "w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, ensure_ascii=False, indent=2)
    print(f"muestra anidada: {datos['muestra_anidada']}")


if __name__ == "__main__":
    main()

"""Instancias de R4 (caso 19d y semillas fijas). Solo usa el catálogo versionado."""
import json
import random

import pandas as pd

from rutas.config import CATALOGO
from rutas.r4.instancias import (K_CALIDAD, SEMILLAS_CALIDAD, instancias_calidad, main,
                                 muestra_anidada, otros_ids)


def ids_catalogo():
    return list(pd.read_csv(CATALOGO)["id"])


def test_caso_19d_muestra_anidada():
    esperado = ["C09", "A10", "F07", "T04", "C08", "A04", "F01", "F06", "F03", "A05", "C02", "A09"]
    assert muestra_anidada(ids_catalogo()) == esperado


def test_otros_ids():
    ids = ids_catalogo()
    otros = otros_ids(ids)
    assert len(otros) == 41
    assert "C01" not in otros
    assert otros == [i for i in ids if i != "C01"]


def test_instancias_calidad():
    ids = ids_catalogo()
    instancias = instancias_calidad(ids)
    assert len(instancias) == 40
    orden = [(k, semilla) for k in K_CALIDAD for semilla in SEMILLAS_CALIDAD]
    assert [(i["k"], i["semilla"]) for i in instancias] == orden
    for i in instancias:
        assert len(i["ids"]) == i["k"] == len(set(i["ids"]))
        assert "C01" not in i["ids"]
    assert instancias == instancias_calidad(ids)
    la_5_2027 = next(i for i in instancias if i["k"] == 5 and i["semilla"] == 2027)
    assert la_5_2027["ids"] == random.Random(2027).sample(otros_ids(ids), 5)


def test_main_escribe_json(tmp_path):
    main(catalogo=CATALOGO, salida=tmp_path)
    datos = json.loads((tmp_path / "r4_instancias.json").read_text(encoding="utf-8"))
    assert datos["semilla"] == 2026
    assert datos["partida"] == "C01"
    assert len(datos["muestra_anidada"]) == 12
    assert len(datos["calidad"]) == 40
    assert datos["k_exactas"] == [5, 6, 7, 8, 9, 10, 11, 12]
    assert datos["semillas_calidad"] == list(range(2026, 2036))

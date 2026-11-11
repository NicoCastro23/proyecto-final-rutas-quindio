"""Itinerario de un día (caso 16 y bordes). La matriz de frontera se comprueba por enumeración."""
import itertools

import pytest

from rutas.r4.held_karp import held_karp
from rutas.r4.itinerario import itinerario_dia

IDS = ["S", "X1", "X2", "X3", "X4", "X5", "X6"]
VISITA = {i: 60 for i in range(1, 7)}


def matriz_frontera(extra=0):
    """Partida 0 (S); atractivos 1..5 en un punto P (arcos 0 entre ellos); 6 en Q. En minutos,
    sobre una línea S - P - Q: S<->P = 60, P->Q = 90, Q->P = 90 + extra, S->Q = 150 y
    Q->S = 150 + extra. Con extra = 0 todo orden cuesta 300; con extra = 1 todo orden que visita
    a 6 cuesta 301 (volver de Q siempre paga el minuto). Se devuelve en segundos."""
    punto = ["S", "P", "P", "P", "P", "P", "Q"]
    minutos = {("S", "P"): 60, ("P", "S"): 60, ("P", "Q"): 90, ("Q", "P"): 90 + extra,
               ("S", "Q"): 150, ("Q", "S"): 150 + extra}
    T = [[0.0] * 7 for _ in range(7)]
    for i in range(7):
        for j in range(7):
            if punto[i] != punto[j]:
                T[i][j] = minutos[(punto[i], punto[j])] * 60.0
    return T


def optimo_minutos(T, s, lugares):
    """Enumeración independiente con itertools (solo en la prueba)."""
    mejor = float("inf")
    for p in itertools.permutations(lugares):
        ruta = [s, *p, s]
        mejor = min(mejor, sum(T[a][b] for a, b in zip(ruta, ruta[1:])))
    return mejor / 60


def test_matriz_frontera_por_enumeracion():
    assert optimo_minutos(matriz_frontera(), 0, [1, 2, 3, 4, 5, 6]) == 300
    T = matriz_frontera(1)
    assert optimo_minutos(T, 0, [1, 2, 3, 4, 5, 6]) == 301
    assert optimo_minutos(T, 0, [1, 2, 3, 4, 5]) == 120
    for quitado in range(1, 6):
        resto = [i for i in range(1, 7) if i != quitado]
        assert optimo_minutos(T, 0, resto) == 301


def test_caso_16_cabe_justo():
    filas, quitados, totales = itinerario_dia(matriz_frontera(), IDS, 0, [1, 2, 3, 4, 5, 6], VISITA)
    assert totales["jornada_min"] == pytest.approx(660.0)
    assert totales["cabe"]
    assert quitados == []


def test_caso_16_quita_uno():
    filas, quitados, totales = itinerario_dia(matriz_frontera(1), IDS, 0, [1, 2, 3, 4, 5, 6], VISITA)
    assert len(quitados) == 1
    q = quitados[0]
    assert q["id"] == "X6"
    assert q["jornada_antes_min"] == pytest.approx(661)
    assert q["jornada_despues_min"] == pytest.approx(420)
    assert q["ahorro_min"] == pytest.approx(241)
    assert totales["cabe"]
    assert totales["atractivos_finales"] == 5


def test_filas_y_acumulado():
    T = matriz_frontera()
    filas, _, totales = itinerario_dia(T, IDS, 0, [1, 2, 3, 4, 5, 6], VISITA)
    assert [f["orden"] for f in filas] == [1, 2, 3, 4, 5, 6, "Regreso"]
    regreso = filas[-1]
    assert regreso["id"] == "S" and regreso["visita_min"] is None
    acumulados = [f["acumulado_h"] for f in filas]
    assert acumulados == sorted(acumulados) and len(set(acumulados)) == len(acumulados)
    assert regreso["acumulado_h"] == pytest.approx(totales["jornada_min"] / 60)
    desplazamientos = sum(f["desplazamiento_min"] for f in filas)
    assert desplazamientos == pytest.approx(totales["desplazamientos_min"])
    assert desplazamientos == pytest.approx(held_karp(T, 0, [1, 2, 3, 4, 5, 6])[0] / 60)
    assert totales["visitas_min"] == 360


def test_cabe_de_entrada_no_quita():
    _, quitados, totales = itinerario_dia(matriz_frontera(), IDS, 0, [1, 2, 3, 4, 5, 6], VISITA,
                                          jornada_max_min=1000)
    assert quitados == [] and totales["cabe"]


def test_errores():
    T = matriz_frontera()
    with pytest.raises(ValueError):
        itinerario_dia(T, IDS, 0, [1, 2, 3, 4, 5], VISITA)             # 5 atractivos
    grande = [[1.0] * 10 for _ in range(10)]
    visita9 = {i: 60 for i in range(1, 10)}
    with pytest.raises(ValueError):
        itinerario_dia(grande, [str(i) for i in range(10)], 0, list(range(1, 10)), visita9)
    with pytest.raises(ValueError):
        itinerario_dia(T, IDS, 0, [1, 2, 3, 4, 5, 6], {i: 60 for i in range(1, 6)})  # 6 sin visita
    with pytest.raises(ValueError):
        itinerario_dia(T, IDS, 0, [1, 2, 3, 4, 5, 5], VISITA)           # repetidos
    with pytest.raises(ValueError):
        itinerario_dia(T, IDS, 1, [1, 2, 3, 4, 5, 6], VISITA)           # partida entre ellos


def test_queda_uno_si_nunca_cabe():
    filas, quitados, totales = itinerario_dia(matriz_frontera(), IDS, 0, [1, 2, 3, 4, 5, 6], VISITA,
                                              jornada_max_min=10)
    assert totales["atractivos_finales"] == 1
    assert len(quitados) == 5
    assert not totales["cabe"]


# ---- T15: archivos y catálogo ----
import csv
import json

import pandas as pd

from rutas.config import CATALOGO
from rutas.r2.matriz import guardar_matriz
from rutas.r4.itinerario import escribir_itinerario, main, visitas_del_catalogo

NOMBRES = {i: f"Lugar {i}" for i in IDS}


def test_visitas_del_catalogo():
    catalogo = pd.read_csv(CATALOGO)
    ids = list(catalogo["id"])
    visitas = visitas_del_catalogo(catalogo, ids)
    assert len(visitas) == 15
    assert visitas[ids.index("A01")] == 420
    assert visitas[ids.index("A05")] == 60
    assert ids.index("C01") not in visitas


def test_escribir_itinerario(tmp_path):
    filas, quitados, totales = itinerario_dia(matriz_frontera(1), IDS, 0, [1, 2, 3, 4, 5, 6], VISITA)
    escribir_itinerario(filas, quitados, totales, IDS[1:], "S", NOMBRES, tmp_path)
    with open(tmp_path / "r4_itinerario.csv", encoding="utf-8", newline="") as f:
        lector = list(csv.reader(f))
    assert lector[0] == ["orden", "id", "lugar", "desplazamiento_min", "visita_min", "acumulado_h"]
    assert len(lector) == 1 + 6       # 5 atractivos finales + Regreso
    assert lector[-1][0] == "Regreso" and lector[-1][4] == "—" and lector[-1][2] == "Lugar S"
    datos = json.loads((tmp_path / "r4_itinerario.json").read_text(encoding="utf-8"))
    assert datos["quitados"][0]["id"] == "X6"
    assert datos["quitados"][0]["ahorro_min"] == pytest.approx(241)
    assert datos["cabe"] is True
    assert datos["totales"]["jornada_min"] == pytest.approx(420)
    assert datos["totales"]["jornada_h"] == pytest.approx(7.0)
    assert datos["partida"] == {"id": "S", "lugar": "Lugar S"}
    assert datos["atractivos_iniciales"] == IDS[1:]


def test_main_sintetico(tmp_path):
    ids = ["C01", "A01", "A02", "A03", "A04", "A05", "A06"]
    matriz = tmp_path / "matriz.csv"
    guardar_matriz(matriz_frontera(), ids, matriz)
    catalogo = tmp_path / "catalogo.csv"
    pd.DataFrame({"id": ids, "nombre": [f"N {i}" for i in ids],
                  "categoria": ["Cabecera municipal"] + ["Atractivo turístico"] * 6,
                  "duracion_visita_min": [None] + [60] * 6}).to_csv(catalogo, index=False)
    salida = tmp_path / "salida"
    main(matriz=matriz, catalogo=catalogo, salida=salida, partida="C01", atractivos=ids[1:])
    assert (salida / "r4_itinerario.csv").exists()
    assert (salida / "r4_itinerario.json").exists()

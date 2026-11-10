"""Selección de pares con semilla 2026 (caso 17 de la spec de R2)."""
import pandas as pd
import pytest

from rutas.config import DATA_PROCESSED
from rutas.r1.catalogo import cargar_catalogo
from rutas.r1.persistencia import cargar_lugares_nodos
from rutas.r2.pares import COLUMNAS, SEMILLA, seleccionar_pares


def _sintetico(lugares):
    """lugares: lista de (id, municipio, nodo) -> (catalogo, lugares_nodos)."""
    catalogo = pd.DataFrame([{"id": i, "municipio": m} for i, m, _ in lugares])
    nodos = pd.DataFrame([{"id_lugar": i, "id_nodo": n} for i, _, n in lugares])
    return catalogo, nodos


def _pares_ordenados(pares):
    return list(zip(pares["origen"], pares["destino"]))


def test_caso_17_catalogo_real():
    if not (DATA_PROCESSED / "lugares_nodos.csv").exists():
        pytest.skip("falta data/processed/lugares_nodos.csv")
    catalogo, nodos = cargar_catalogo(), cargar_lugares_nodos()
    pares = seleccionar_pares(catalogo, nodos)
    assert SEMILLA == 2026
    assert list(pares.columns) == COLUMNAS
    assert len(pares) == 20

    cercanos, lejanos = pares[pares.tipo == "cercano"], pares[pares.tipo == "lejano"]
    assert len(cercanos) == 10 and len(lejanos) == 10
    assert list(pares.tipo) == ["cercano"] * 10 + ["lejano"] * 10   # cercanos primero
    # 10 cercanos: del mismo municipio, de 10 municipios distintos, en nodos distintos
    assert (cercanos.municipio_origen == cercanos.municipio_destino).all()
    assert cercanos.municipio_origen.nunique() == 10
    assert (pares.nodo_origen != pares.nodo_destino).all()
    # 10 lejanos: municipios distintos
    assert (lejanos.municipio_origen != lejanos.municipio_destino).all()
    # sin pares ordenados repetidos y sin el par {T03, T05} (comparten nodo)
    assert len(set(_pares_ordenados(pares))) == 20
    assert not {("T03", "T05"), ("T05", "T03")} & set(_pares_ordenados(pares))
    # municipios y nodos coinciden con el catálogo y lugares_nodos.csv
    municipio = dict(zip(catalogo["id"], catalogo["municipio"]))
    nodo = dict(zip(nodos["id_lugar"], nodos["id_nodo"]))
    for fila in pares.itertuples():
        assert fila.municipio_origen == municipio[fila.origen]
        assert fila.municipio_destino == municipio[fila.destino]
        assert fila.nodo_origen == nodo[fila.origen]
        assert fila.nodo_destino == nodo[fila.destino]


def test_misma_semilla_mismos_pares():
    if not (DATA_PROCESSED / "lugares_nodos.csv").exists():
        pytest.skip("falta data/processed/lugares_nodos.csv")
    catalogo, nodos = cargar_catalogo(), cargar_lugares_nodos()
    a = seleccionar_pares(catalogo, nodos)
    b = seleccionar_pares(catalogo, nodos)
    pd.testing.assert_frame_equal(a, b)
    otra = seleccionar_pares(catalogo, nodos, semilla=7)
    assert not a.equals(otra)


def test_mismo_nodo_excluido_sintetico():
    # a1 y a2 comparten nodo: nunca deben aparecer juntos, con ninguna semilla
    catalogo, nodos = _sintetico([
        ("a1", "A", 1), ("a2", "A", 1), ("a3", "A", 2),
        ("b1", "B", 3), ("b2", "B", 4), ("c1", "C", 5), ("c2", "C", 6)])
    juntos = {("a1", "a2"), ("a2", "a1")}
    for semilla in range(30):
        pares = seleccionar_pares(catalogo, nodos, semilla=semilla, cercanos=3, lejanos=5)
        assert (pares.nodo_origen != pares.nodo_destino).all()
        assert not juntos & set(_pares_ordenados(pares))
        assert len(set(_pares_ordenados(pares))) == len(pares)
        assert list(pares.tipo).count("cercano") == 3
        assert list(pares.tipo).count("lejano") == 5


def test_varias_vueltas_si_hay_menos_municipios_que_cercanos():
    # 3 municipios, 5 cercanos: hacen falta dos vueltas y no se repite ningún par
    catalogo, nodos = _sintetico([
        ("a1", "A", 1), ("a2", "A", 2), ("a3", "A", 3),
        ("b1", "B", 4), ("b2", "B", 5), ("c1", "C", 6), ("c2", "C", 7)])
    pares = seleccionar_pares(catalogo, nodos, cercanos=5, lejanos=2)
    cercanos = pares[pares.tipo == "cercano"]
    assert len(cercanos) == 5
    assert len(set(_pares_ordenados(cercanos))) == 5
    assert (cercanos.municipio_origen == cercanos.municipio_destino).all()


def test_municipio_sin_pares_validos_se_salta():
    # B tiene 2 lugares pero en el mismo nodo: ningún par válido, se salta
    catalogo, nodos = _sintetico([
        ("a1", "A", 1), ("a2", "A", 2), ("b1", "B", 3), ("b2", "B", 3),
        ("c1", "C", 4), ("c2", "C", 5), ("d1", "D", 6), ("d2", "D", 7)])
    pares = seleccionar_pares(catalogo, nodos, cercanos=3, lejanos=3)
    cercanos = pares[pares.tipo == "cercano"]
    assert len(cercanos) == 3
    assert "B" not in set(cercanos.municipio_origen)
    assert set(cercanos.municipio_origen) == {"A", "C", "D"}

"""Adyacencia de la red real (R2, caso 15). Necesita data/processed/ (se salta si falta)."""
import math
import random

import pytest

from rutas.r2.adyacencia import construir_adyacencia
from rutas.r2.dijkstra import consultar
from rutas.r2.matriz import asimetria, cargar_matriz, guardar_matriz
from rutas.r2.ruta import detalle_ruta

pytestmark = pytest.mark.red


def test_caso_15_adyacencia_real(grafo_procesado_real):
    G = grafo_procesado_real
    red = construir_adyacencia(G)
    V = 8791
    assert len(red.ids) == len(red.adyacencia) == V
    assert red.ids == sorted(G.nodes)
    assert all(red.indice[red.ids[i]] == i for i in range(V))
    assert sum(len(vecinos) for vecinos in red.adyacencia) == 20132
    for vecinos in red.adyacencia:
        for j, tiempo in vecinos:
            assert 0 <= j < V
            assert math.isfinite(tiempo) and tiempo >= 0


# ---- B3: casos 14 y 16 sobre la red real -------------------------------------------------

@pytest.fixture(scope="module")
def datos_reales():
    """Grafo, red indexada, catálogo y los 20 pares medidos; se salta si falta data/processed."""
    from rutas.config import DATA_PROCESSED
    if not (DATA_PROCESSED / "grafo_componente.graphml").exists():
        pytest.skip("falta data/processed/grafo_componente.graphml")
    from rutas.r1.catalogo import cargar_catalogo
    from rutas.r1.persistencia import cargar_grafo_procesado, cargar_lugares_nodos
    from rutas.r2.pares import seleccionar_pares
    G = cargar_grafo_procesado(DATA_PROCESSED)
    catalogo, lugares = cargar_catalogo(), cargar_lugares_nodos()
    return G, construir_adyacencia(G), catalogo, lugares, seleccionar_pares(catalogo, lugares)


def test_caso_14_lineal_igual_a_cola(datos_reales):
    _, red, _, _, pares = datos_reales
    for par in pares[pares.tipo == "cercano"].itertuples():
        t_l, ruta_l, k_l = consultar(red, par.nodo_origen, par.nodo_destino, "lineal")
        t_c, ruta_c, k_c = consultar(red, par.nodo_origen, par.nodo_destino, "cola_prioridad")
        assert abs(t_l - t_c) <= 1e-6, (par.origen, par.destino)
        assert k_l == k_c and ruta_l == ruta_c, (par.origen, par.destino)


def test_caso_14_ruta_y_networkx(datos_reales):
    import networkx as nx
    G, red, _, _, pares = datos_reales
    for par in pares.itertuples():
        tiempo, ruta, _ = consultar(red, par.nodo_origen, par.nodo_destino, "cola_prioridad")
        assert math.isfinite(tiempo) and ruta[0] == par.nodo_origen and ruta[-1] == par.nodo_destino
        assert abs(detalle_ruta(G, ruta)[0] - tiempo) <= 1e-6, (par.origen, par.destino)
        esperado = nx.dijkstra_path_length(G, par.nodo_origen, par.nodo_destino,
                                           weight="travel_time")
        assert abs(esperado - tiempo) <= 1e-6, (par.origen, par.destino)


def test_caso_16_matriz_real(datos_reales, tmp_path):
    from rutas.config import MATRIZ_TIEMPOS
    if not MATRIZ_TIEMPOS.exists():
        pytest.skip("falta data/processed/matriz_tiempos.csv")
    _, red, catalogo, lugares, pares = datos_reales
    ids = list(catalogo["id"])
    nodo = dict(zip(lugares["id_lugar"], lugares["id_nodo"]))
    matriz = cargar_matriz(MATRIZ_TIEMPOS)

    assert matriz.shape == (42, 42)
    assert list(matriz.index) == ids and list(matriz.columns) == ids      # orden del catálogo
    valores = matriz.values
    assert (valores.diagonal() == 0).all()
    assert (valores < math.inf).all()
    assert matriz.loc["T03", "T05"] == 0 and matriz.loc["T05", "T03"] == 0
    assert asimetria(valores.tolist(), ids)["pares_asimetricos"] >= 1

    # M[i][j] coincide con Dijkstra con destino: 20 pares al azar (semilla 2026) y los 20 medidos
    rng = random.Random(2026)
    al_azar = [tuple(rng.sample(ids, 2)) for _ in range(20)]
    medidos = list(zip(pares["origen"], pares["destino"]))
    for origen, destino in al_azar + medidos:
        tiempo, _, _ = consultar(red, nodo[origen], nodo[destino], "cola_prioridad")
        assert abs(matriz.loc[origen, destino] - tiempo) <= 1e-6, (origen, destino)

    # el CSV conserva todos los decimales: reescribirlo da los mismos bytes
    copia = tmp_path / "copia.csv"
    guardar_matriz(valores.tolist(), ids, copia)
    assert copia.read_bytes() == MATRIZ_TIEMPOS.read_bytes()

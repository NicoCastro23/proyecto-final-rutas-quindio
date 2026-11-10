"""Pruebas de rutas/r2/medir_dijkstra.py. Ningún cronómetro real salvo un grafo diminuto."""
import json
from types import SimpleNamespace

import pandas as pd
import pytest

from rutas.medicion import NO_COMPLETADA, ResultadoMedicion
from rutas.r2 import medir_dijkstra
from rutas.r2.adyacencia import construir_adyacencia
from rutas.r2.dijkstra import dijkstra_cola, dijkstra_lineal
from rutas.r2.medir_dijkstra import COLUMNAS, fila, main, medir_pares
from rutas.r2.pares import COLUMNAS as COLUMNAS_PARES
from tests.conftest import grafo_sintetico

NODOS = {100: (-75.6, 4.5), 200: (-75.7, 4.6), 300: (-75.8, 4.7), 400: (-75.9, 4.8)}
ARISTAS = [(100, 200, {"travel_time": 10.0, "length": 100.0}),
           (200, 300, {"travel_time": 20.0, "length": 300.0}),
           (100, 300, {"travel_time": 50.0, "length": 600.0}),
           (300, 400, {"travel_time": 5.0, "length": 50.0}),
           (400, 100, {"travel_time": 7.0, "length": 70.0})]


def par_de(origen, destino, tipo, nodo_o, nodo_d):
    return {"origen": origen, "destino": destino, "tipo": tipo, "municipio_origen": "M",
            "municipio_destino": "M" if tipo == "cercano" else "N",
            "nodo_origen": nodo_o, "nodo_destino": nodo_d}


def pares_a_mano():
    # cercano 100 -> 300: 30 s por 200, 400 m, 3 explorados. lejano 300 -> 200: 22 s, 220 m, 4 explorados
    return pd.DataFrame([par_de("L1", "L2", "cercano", 100, 300),
                         par_de("L3", "L4", "lejano", 300, 200)], columns=COLUMNAS_PARES)


@pytest.fixture
def mundo():
    G = grafo_sintetico(NODOS, ARISTAS)
    return G, construir_adyacencia(G)


def test_fila_columnas_y_no_completada():
    par = SimpleNamespace(**par_de("L1", "L2", "cercano", 100, 300))
    ok = ResultadoMedicion(tiempo_ms=1.25, repeticiones=5, completada=True, tiempos_ms=[1.25])
    f = fila(par, "lineal", 30.0, 3, ok, 400.0)
    assert list(f) == COLUMNAS
    assert f["origen"] == "L1" and f["destino"] == "L2" and f["version"] == "lineal"
    assert f["tiempo_ms"] == 1.25 and f["repeticiones"] == 5 and f["tipo"] == "cercano"
    nc = fila(par, "lineal", 30.0, 3, NO_COMPLETADA, 400.0)
    assert nc["tiempo_ms"] == "no completada" and nc["repeticiones"] == 0


class Falso:
    """Medidor falso: anota con qué se lo llamó (y en `orden`, quién) y devuelve un resultado fijo."""
    def __init__(self, nombre, tiempo_ms, orden=None):
        self.nombre, self.tiempo_ms = nombre, tiempo_ms
        self.orden = orden if orden is not None else []
        self.llamadas = []

    def __call__(self, funcion, segundo, repeticiones=5):
        self.orden.append(self.nombre)
        self.llamadas.append((funcion, segundo, repeticiones))
        return ResultadoMedicion(self.tiempo_ms, repeticiones, True, [self.tiempo_ms])


def test_medir_pares_con_medidores_falsos(mundo):
    G, red = mundo
    orden = []
    cola, lineal = Falso("cola", 2.0, orden), Falso("lineal", 8.0, orden)

    filas = medir_pares(G, red, pares_a_mano(), repeticiones=3, medir_cola=cola, medir_lineal=lineal)

    assert orden == ["cola", "lineal", "cola"]
    assert [(f["origen"], f["version"]) for f in filas] == [
        ("L1", "cola_prioridad"), ("L1", "lineal"), ("L3", "cola_prioridad")]
    assert all(list(f) == COLUMNAS for f in filas)
    i = red.indice
    funcion, preparar, repeticiones = cola.llamadas[0]
    assert funcion is dijkstra_cola and repeticiones == 3
    assert preparar() == (red.adyacencia, i[100], i[300])           # índices, no ids
    funcion, args, repeticiones = lineal.llamadas[0]
    assert funcion is dijkstra_lineal and args == (red.adyacencia, i[100], i[300])
    assert cola.llamadas[1][1]() == (red.adyacencia, i[300], i[200])
    assert len(lineal.llamadas) == 1                                  # el lejano no se mide lineal
    resumen = [(f["tiempo_viaje_s"], f["nodos_explorados"], f["distancia_m"]) for f in filas]
    assert resumen == [(30.0, 3, 400.0), (30.0, 3, 400.0), (22.0, 4, 220.0)]
    assert filas[0]["tiempo_ms"] == 2.0 and filas[1]["tiempo_ms"] == 8.0
    assert filas[2]["tipo"] == "lejano"


def test_versiones_distintas_abortan(mundo, monkeypatch):
    G, red = mundo
    from rutas.r2 import dijkstra
    original = dijkstra.VERSIONES["lineal"]
    monkeypatch.setitem(dijkstra.VERSIONES, "lineal",
                        lambda *a, **k: (lambda r: (r[0] + 1.0, r[1], r[2]))(original(*a, **k)))
    cola, lineal = Falso("cola", 1.0), Falso("lineal", 1.0)
    with pytest.raises(ValueError, match="L1.*L2"):
        medir_pares(G, red, pares_a_mano(), medir_cola=cola, medir_lineal=lineal)
    assert cola.llamadas == [] and lineal.llamadas == []      # se comprueba ANTES de medir nada


def test_comprobacion_previa_no_depende_de_assert(mundo, monkeypatch):
    # La comprobación debe ser un error explícito (sobrevive a python -O) y nombrar los valores
    G, red = mundo
    from rutas.r2 import dijkstra
    original = dijkstra.VERSIONES["lineal"]
    monkeypatch.setitem(dijkstra.VERSIONES, "lineal",
                        lambda *a, **k: (lambda r: (r[0] + 1.0, r[1], r[2]))(original(*a, **k)))
    with pytest.raises(ValueError) as error:
        medir_pares(G, red, pares_a_mano(), medir_cola=Falso("c", 1.0), medir_lineal=Falso("l", 1.0))
    assert not isinstance(error.value, AssertionError)
    assert "31.0" in str(error.value) and "30.0" in str(error.value)    # lineal vs cola


def test_explorados_distintos_abortan(mundo, monkeypatch):
    G, red = mundo
    from rutas.r2 import dijkstra
    original = dijkstra.VERSIONES["lineal"]
    monkeypatch.setitem(dijkstra.VERSIONES, "lineal",
                        lambda *a, **k: (lambda r: (r[0], r[1], r[2] + 1))(original(*a, **k)))
    with pytest.raises(ValueError):
        medir_pares(G, red, pares_a_mano(), medir_cola=Falso("cola", 1.0), medir_lineal=Falso("lineal", 1.0))


def test_fila_lineal_lleva_sus_propios_valores(mundo, monkeypatch):
    # Lineal "saboteada" pero dentro de la tolerancia (5e-7 s < 1e-6): pasa la comprobación previa,
    # y su fila del CSV debe traer SU tiempo de viaje, no el de la cola.
    G, red = mundo
    from rutas.r2 import dijkstra
    original = dijkstra.VERSIONES["lineal"]
    monkeypatch.setitem(dijkstra.VERSIONES, "lineal",
                        lambda *a, **k: (lambda r: (r[0] + 5e-7, r[1], r[2]))(original(*a, **k)))
    filas = medir_pares(G, red, pares_a_mano(), medir_cola=Falso("cola", 2.0),
                        medir_lineal=Falso("lineal", 8.0))
    por_version = {f["version"]: f for f in filas if f["origen"] == "L1"}
    assert por_version["cola_prioridad"]["tiempo_viaje_s"] == 30.0
    assert por_version["lineal"]["tiempo_viaje_s"] == pytest.approx(30.0 + 5e-7, abs=1e-12)
    assert por_version["lineal"]["tiempo_viaje_s"] != por_version["cola_prioridad"]["tiempo_viaje_s"]


def test_fila_lineal_lleva_sus_propios_explorados(mundo, monkeypatch):
    # La lineal se consulta con consultar(..., "lineal") y no con el resultado de la cola
    G, red = mundo
    from rutas.r2 import medir_dijkstra as modulo
    llamadas = []
    real = modulo.consultar

    def espia(red_, origen, destino, version="cola_prioridad"):
        llamadas.append((origen, destino, version))
        return real(red_, origen, destino, version)

    monkeypatch.setattr(modulo, "consultar", espia)
    medir_pares(G, red, pares_a_mano(), medir_cola=Falso("cola", 2.0), medir_lineal=Falso("lineal", 8.0))
    assert (100, 300, "lineal") in llamadas[2:]       # además de la comprobación previa


def test_medir_en_hijo_de_verdad(mundo):
    G, red = mundo
    filas = medir_pares(G, red, pares_a_mano().iloc[:1], repeticiones=1)
    assert [f["version"] for f in filas] == ["cola_prioridad", "lineal"]
    for f in filas:
        assert f["repeticiones"] == 1 and f["tiempo_ms"] > 0


def test_main_sintetico_escribe_archivos(tmp_path, monkeypatch):
    from rutas.r1.persistencia import guardar_procesado
    G = grafo_sintetico(NODOS, ARISTAS + [(200, 100, {"travel_time": 9.0, "length": 90.0})])
    lugares = pd.DataFrame({"id_lugar": ["L1", "L2", "L3", "L4"], "id_nodo": [100, 300, 300, 200],
                            "distancia_al_nodo_m": [1.0, 2.0, 3.0, 4.0],
                            "alerta_500m": [False] * 4})
    processed, salida = tmp_path / "processed", tmp_path / "r2"
    guardar_procesado(G, lugares, {}, carpeta=processed)
    catalogo = tmp_path / "catalogo.csv"
    pd.DataFrame({"id": ["L1", "L2", "L3", "L4"], "municipio": ["M", "M", "N", "N"]}
                 ).to_csv(catalogo, index=False)
    monkeypatch.setattr(medir_dijkstra, "seleccionar_pares", lambda cat, lug: pares_a_mano())

    main(processed=processed, catalogo=catalogo, salida=salida, repeticiones=1)

    assert sorted(p.name for p in salida.iterdir()) == [
        "maquina.json", "r2_dijkstra.csv", "r2_pares.csv", "r2_pares.json"]
    assert json.loads((salida / "r2_pares.json").read_text(encoding="utf-8"))["semilla"] == 2026
    assert "procesador" in json.loads((salida / "maquina.json").read_text(encoding="utf-8"))
    df = pd.read_csv(salida / "r2_dijkstra.csv")
    assert list(df.columns) == COLUMNAS and len(df) == 3
    assert list(pd.read_csv(salida / "r2_pares.csv").columns) == COLUMNAS_PARES


def test_main_no_escribe_si_las_versiones_difieren(tmp_path, monkeypatch):
    from rutas.r1.persistencia import guardar_procesado
    from rutas.r2 import dijkstra
    G = grafo_sintetico(NODOS, ARISTAS)
    lugares = pd.DataFrame({"id_lugar": ["L1", "L2"], "id_nodo": [100, 300],
                            "distancia_al_nodo_m": [1.0, 2.0], "alerta_500m": [False] * 2})
    guardar_procesado(G, lugares, {}, carpeta=tmp_path / "p")
    catalogo = tmp_path / "c.csv"
    pd.DataFrame({"id": ["L1", "L2"], "municipio": ["M", "M"]}).to_csv(catalogo, index=False)
    monkeypatch.setattr(medir_dijkstra, "seleccionar_pares", lambda cat, lug: pares_a_mano().iloc[:1])
    monkeypatch.setitem(dijkstra.VERSIONES, "lineal", lambda *a, **k: (0.0, [], 0))
    with pytest.raises(ValueError):
        main(processed=tmp_path / "p", catalogo=catalogo, salida=tmp_path / "s", repeticiones=1)
    assert not (tmp_path / "s").exists() or list((tmp_path / "s").iterdir()) == []


# ---- T14: la comprobación de resultados medidos debe poder fallar (CSV sintético alterado) ----

def csv_medido_sintetico():
    filas = []
    for k in range(20):
        tipo = "cercano" if k < 10 else "lejano"
        base = {"origen": f"A{k}", "destino": f"B{k}", "tiempo_viaje_s": 100.0 + k,
                "nodos_explorados": 10 + k, "tipo": tipo, "distancia_m": 1000.0, "repeticiones": 5}
        filas.append({**base, "version": "cola_prioridad", "tiempo_ms": 1.5})
        if tipo == "cercano":
            filas.append({**base, "version": "lineal", "tiempo_ms": 20.0})
    return pd.DataFrame(filas, columns=COLUMNAS)


def test_comprobar_resultados_acepta_csv_correcto():
    from tests.test_red_real_r2 import comprobar_resultados
    comprobar_resultados(csv_medido_sintetico())
    df = csv_medido_sintetico()
    df["tiempo_ms"] = df["tiempo_ms"].astype(object)
    df.loc[df.version == "lineal", "tiempo_ms"] = "no completada"     # también es válido
    comprobar_resultados(df)


@pytest.mark.parametrize("alteracion", ["tiempo_distinto", "explorados_distintos", "faltan_filas",
                                        "tiempo_ms_texto_raro", "columnas_desordenadas",
                                        "lineal_en_lejano"])
def test_comprobar_resultados_detecta_alteraciones(alteracion):
    from tests.test_red_real_r2 import comprobar_resultados
    df = csv_medido_sintetico()
    lineal = df.version == "lineal"
    if alteracion == "tiempo_distinto":
        df.loc[df[lineal].index[0], "tiempo_viaje_s"] += 0.01
    elif alteracion == "explorados_distintos":
        df.loc[df[lineal].index[0], "nodos_explorados"] += 1
    elif alteracion == "faltan_filas":
        df = df.iloc[:-1]
    elif alteracion == "tiempo_ms_texto_raro":
        df["tiempo_ms"] = df["tiempo_ms"].astype(object)
        df.loc[df.index[0], "tiempo_ms"] = "lento"
    elif alteracion == "columnas_desordenadas":
        df = df[["destino", "origen"] + COLUMNAS[2:]]
    elif alteracion == "lineal_en_lejano":
        df.loc[df.index[-1], "version"] = "lineal"
    with pytest.raises(AssertionError):
        comprobar_resultados(df)


def test_comprobar_resultados_tolerancia_entre_lineal_y_cola():
    # La fila lineal se compara con la de cola del mismo par: 5e-7 s pasa, 2e-6 s no
    from tests.test_red_real_r2 import comprobar_resultados
    df = csv_medido_sintetico()
    indice = df[df.version == "lineal"].index[0]
    df.loc[indice, "tiempo_viaje_s"] += 5e-7
    comprobar_resultados(df)
    df.loc[indice, "tiempo_viaje_s"] += 1.5e-6
    with pytest.raises(AssertionError):
        comprobar_resultados(df)

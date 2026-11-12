"""Fixtures y helpers compartidos por las pruebas (R1 a R5)."""
import json

import networkx as nx
import pandas as pd
import pytest
from shapely.geometry import LineString

from rutas.config import DATA_PROCESSED, DATA_RAW, RAIZ
from rutas.r1.persistencia import guardar_grafo
from rutas.r1.utm import agregar_utm_a_nodos
from rutas.r2.adyacencia import construir_adyacencia


def pytest_addoption(parser):
    parser.addoption("--lento", action="store_true", default=False,
                     help="corre también las pruebas marcadas como lento (p. ej. el peor caso de R3)")


def pytest_collection_modifyitems(config, items):
    """Las pruebas `lento` se saltan salvo con --lento, sin importar el filtro -m que se use."""
    if config.getoption("--lento"):
        return
    saltar = pytest.mark.skip(reason="prueba lenta: se corre con --lento")
    for prueba in items:
        if "lento" in prueba.keywords:
            prueba.add_marker(saltar)


def grafo_sintetico(nodos, aristas):
    """Construye un MultiDiGraph pequeño con el formato que deja OSMnx.

    nodos:   dict {id: (lon, lat)}
    aristas: lista de tuplas (u, v, atributos) o (u, v, key, atributos)
    Se pone crs y x, y en cada nodo porque ox.add_edge_speeds llama a graph_to_gdfs.
    """
    G = nx.MultiDiGraph()
    G.graph["crs"] = "epsg:4326"
    for id_nodo, (lon, lat) in nodos.items():
        G.add_node(id_nodo, x=lon, y=lat)
    for arista in aristas:
        if len(arista) == 3:
            u, v, atributos = arista
            G.add_edge(u, v, **atributos)
        else:
            u, v, key, atributos = arista
            G.add_edge(u, v, key=key, **atributos)
    return G


def red_desde_aristas(aristas, nodos=None):
    """Red indexada de R2 desde tuplas (u, v, travel_time) con ids enteros pequeños.

    nodos: ids extra sin aristas (p. ej. un nodo aislado). Pasa por construir_adyacencia,
    igual que la red real (aristas paralelas y autolazos incluidos).
    """
    G = nx.MultiDiGraph()
    G.add_nodes_from(nodos or [])
    for u, v, tiempo in aristas:
        G.add_edge(u, v, travel_time=tiempo)
    return construir_adyacencia(G)


def cargar_red_clase():
    """Red de la clase de Dijkstra (tests/datos/red_clase.json) restringida a la componente 1-7.

    Pesos en minutos, con la arista paralela 2->3 incluida. Devuelve (red, seccion R2 del JSON).
    """
    datos = json.loads((RAIZ / "tests" / "datos" / "red_clase.json").read_text(encoding="utf-8"))
    aristas = [(a["u"], a["v"], float(a["min"])) for a in datos["red"]["aristas"]
               if a["u"] <= 7 and a["v"] <= 7]
    return red_desde_aristas(aristas), datos["R2"]


def cargar_casos_r3():
    """Casos de la envolvente (tests/datos/red_clase.json): (nodos {id: (x, y)} como int, sección R3)."""
    datos = json.loads((RAIZ / "tests" / "datos" / "red_clase.json").read_text(encoding="utf-8"))
    nodos = {int(i): (int(n["x"]), int(n["y"])) for i, n in datos["red"]["nodos"].items()}
    return nodos, datos["R3"]


def comprobar_envolvente(vertices, puntos):
    """Invariantes geométricos de una envolvente (caso 13), sin usar SciPy. Lanza AssertionError."""
    from rutas.r3.envolvente import cruz
    puntos = set(puntos)
    h = len(vertices)
    assert len(set(vertices)) == h, "vértices repetidos"
    assert set(vertices) <= puntos, "hay vértices que no son puntos de la entrada"
    if h:
        assert vertices[0] == min(vertices, key=lambda p: (p[1], p[0])), "no empieza por el menor (y, x)"
    if h >= 3:
        for i in range(h):
            # Tres vértices seguidos giran siempre a la izquierda: antihorario y sin alineados
            assert cruz(vertices[i], vertices[(i + 1) % h], vertices[(i + 2) % h]) > 0, "no es convexo estricto"
        if set(vertices) != puntos:       # si todos son vértices no hay nada que comprobar (y sería O(n*h))
            for i in range(h):
                lado = (vertices[i], vertices[(i + 1) % h])
                assert all(cruz(*lado, p) >= 0 for p in puntos), "hay un punto fuera del polígono"
    if h == 2:
        a, b = vertices
        assert all(cruz(a, b, p) == 0 for p in puntos), "con 2 vértices todos deben estar alineados"
        assert all(a <= p <= b for p in puntos), "los puntos deben estar entre los dos extremos"


def carpeta_sintetica(tmp_path):
    """Carpeta processed con un grafo de 6 nodos (cerca de Armenia) con x_utm, y_utm."""
    nodos = {1: (-75.70, 4.50), 2: (-75.60, 4.50), 3: (-75.60, 4.60), 4: (-75.70, 4.60),
             5: (-75.65, 4.55), 6: (-75.65, 4.50)}
    G = agregar_utm_a_nodos(grafo_sintetico(nodos, [(1, 2, {}), (2, 3, {})]))
    guardar_grafo(G, tmp_path)
    return tmp_path


def _ruta_grafo_procesado():
    for nombre in ("grafo_componente.graphml", "grafo_componente.graphml.gz"):
        if (DATA_PROCESSED / nombre).exists():
            return DATA_PROCESSED / nombre
    return None


@pytest.fixture
def grafo_procesado_real():
    """Grafo procesado real (.graphml o .graphml.gz); se salta si no existe."""
    if _ruta_grafo_procesado() is None:
        pytest.skip("falta data/processed/grafo_componente.graphml[.gz]")
    from rutas.r1.persistencia import cargar_grafo_procesado
    return cargar_grafo_procesado(DATA_PROCESSED)


@pytest.fixture
def red_radio_2km():
    """Red cruda de radio 2 km; se salta si no se ha descargado."""
    ruta = DATA_RAW / "radio_2km.graphml"
    if not ruta.exists():
        pytest.skip("falta data/raw/radio_2km.graphml")
    import osmnx as ox
    return ox.load_graphml(ruta)


# ---------------------------------------------------------------------------
# Datos sintéticos de R5: una carpeta pequeña con todo lo que lee la aplicación
# ---------------------------------------------------------------------------
NODOS_APP = {1: (-75.70, 4.50), 2: (-75.68, 4.50), 3: (-75.66, 4.50),
             4: (-75.66, 4.52), 5: (-75.68, 4.52), 6: (-75.70, 4.52)}
# (id, nombre, categoría, nodo): A05 comparte nodo con C02 y A06 con A02 (caso del mismo punto)
LUGARES_APP = [("C01", "Cabecera Uno", "Cabecera municipal", 1),
               ("C02", "Cabecera Dos", "Cabecera municipal", 4),
               ("A01", "Atractivo Uno", "Atractivo turístico", 2),
               ("A02", "Atractivo Dos", "Atractivo turístico", 3),
               ("A03", "Atractivo Tres", "Atractivo turístico", 5),
               ("A04", "Atractivo Cuatro", "Atractivo turístico", 6),
               ("A05", "Atractivo Cinco", "Atractivo turístico", 4),
               ("A06", "Atractivo Seis", "Atractivo turístico", 3)]
VISITAS_APP = [30, 60, 30, 60, 30, 60]       # 270 min: la jornada cabe en 11 h


def carpeta_app_sintetica(tmp_path, visitas=None):
    """Escribe en tmp_path los datos de prueba de R5 y devuelve (processed, catalogo, results).

    Grafo de 6 nodos en anillo (1->2->...->6->1 y su inverso, 60 s y 500 m cada arista), salvo
    2->1 que tarda 90 s (asimetría). La arista 1->2 lleva una geometría curva de 3 puntos.
    Hay 8 lugares (2 cabeceras y 6 atractivos). Con visitas=[120] * 6 la jornada no cabe en 11 h.
    """
    from rutas.r2.matriz import calcular_matriz, guardar_matriz

    visitas = visitas or VISITAS_APP
    aristas = []
    for u in range(1, 7):
        v = u % 6 + 1
        directa = {"travel_time": 60.0, "length": 500.0}
        inversa = {"travel_time": 90.0 if (v, u) == (2, 1) else 60.0, "length": 500.0}
        if (u, v) == (1, 2):
            directa["geometry"] = LineString([(-75.70, 4.50), (-75.69, 4.505), (-75.68, 4.50)])
        aristas.append((u, v, directa))
        aristas.append((v, u, inversa))
    G = agregar_utm_a_nodos(grafo_sintetico(NODOS_APP, aristas))

    processed = tmp_path / "processed"
    processed.mkdir()
    guardar_grafo(G, processed)

    ids = [lugar[0] for lugar in LUGARES_APP]
    nodos = [lugar[3] for lugar in LUGARES_APP]
    pd.DataFrame({"id_lugar": ids, "id_nodo": nodos, "distancia_al_nodo_m": 10.0,
                  "alerta_500m": False}).to_csv(processed / "lugares_nodos.csv", index=False)
    matriz = calcular_matriz(construir_adyacencia(G), nodos)
    guardar_matriz(matriz, ids, processed / "matriz_tiempos.csv")

    # catálogo: las visitas se asignan en orden a los 6 atractivos; las cabeceras no tienen
    duraciones = [None, None] + list(visitas)
    pd.DataFrame({
        "id": ids, "nombre": [l[1] for l in LUGARES_APP], "municipio": "Armenia",
        "categoria": [l[2] for l in LUGARES_APP],
        "latitud": [NODOS_APP[n][1] for n in nodos], "longitud": [NODOS_APP[n][0] for n in nodos],
        "duracion_visita_min": duraciones,
    }).to_csv(tmp_path / "catalogo.csv", index=False)

    cuadrado = [[-75.71, 4.49], [-75.65, 4.49], [-75.65, 4.53], [-75.71, 4.53]]
    envolvente = {"type": "FeatureCollection", "features": [{
        "type": "Feature", "properties": {"vertices": 4, "area_km2": 29.6},
        "geometry": {"type": "Polygon", "coordinates": [cuadrado + [cuadrado[0]]]}}]}
    (processed / "envolvente.geojson").write_text(json.dumps(envolvente), encoding="utf-8")

    results = tmp_path / "results"
    (results / "r2").mkdir(parents=True)
    (results / "r2" / "r2_tiempo_vs_explorados.png").write_bytes(b"\x89PNG\r\n\x1a\n")
    (results / "r2" / "r2_cociente.csv").write_text("mediana,minimo,maximo\n1.5,1.0,2.0\n", encoding="utf-8")
    (results / "r2" / "r2_dijkstra.csv").write_text("nodos,tiempo_ms\n10,1.0\n", encoding="utf-8")
    (results / "r2" / "r2_pares.csv").write_text("origen,destino,tiempo_s\nC01,C02,60\n", encoding="utf-8")
    (results / "r4").mkdir()
    (results / "r4" / "r4_calidad.csv").write_text("k,brecha_pct\n6,0.0\n", encoding="utf-8")
    (results / "r4" / "r4_memoria.csv").write_text("k,bytes\n6,100\n", encoding="utf-8")
    (results / "r4" / "r4_itinerario.csv").write_text("orden,lugar\n1,A01\n", encoding="utf-8")
    return processed, tmp_path / "catalogo.csv", results


@pytest.fixture
def datos_app(tmp_path):
    """DatosApp sobre los datos sintéticos (carga con cargar_datos, igual que la app real)."""
    from rutas.r5.datos import cargar_datos
    processed, catalogo, _ = carpeta_app_sintetica(tmp_path)
    return cargar_datos(processed, catalogo)


@pytest.fixture
def cliente_app(tmp_path):
    """Cliente de pruebas de Flask sobre los datos sintéticos."""
    from rutas.r5.app import crear_app
    from rutas.r5.datos import cargar_datos
    processed, catalogo, results = carpeta_app_sintetica(tmp_path)
    return crear_app(cargar_datos(processed, catalogo), results).test_client()

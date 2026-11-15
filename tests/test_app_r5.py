"""Pruebas de la aplicación de R5 con el cliente de pruebas de Flask (datos sintéticos)."""
import re
import socket

import pytest

from rutas.config import RAIZ, RESULTS
from rutas.r5.app import crear_app, main
from rutas.r5.datos import cargar_datos
from rutas.r5.formato import numero
from rutas.r5.servicios import itinerario
from tests.conftest import carpeta_app_sintetica

R5 = RAIZ / "rutas" / "r5"


def test_sin_algoritmos_ni_js_propio():
    """R5 no implementa algoritmos (los importa de R2 y R4) ni lleva JavaScript propio."""
    for archivo in R5.glob("*.py"):
        texto = archivo.read_text(encoding="utf-8")
        for prohibido in ("heapq", "networkx", "scipy", "itertools"):
            assert not re.search(rf"^\s*(import|from)\s+{prohibido}\b", texto, re.M), \
                f"{archivo.name} importa {prohibido}"
    plantillas = list((R5 / "templates").glob("*.html"))
    assert plantillas, "debe haber al menos base.html"
    for plantilla in plantillas:
        texto = plantilla.read_text(encoding="utf-8").lower()
        esperados = 2 if plantilla.name == "base.html" else 0     # solo base.html carga motion.js y app.js
        assert texto.count("<script") == esperados, plantilla.name
    requisitos = (RAIZ / "requirements.txt").read_text(encoding="utf-8")
    assert "Flask==3.1.3" in requisitos and "folium==0.20.0" in requisitos


ATRACTIVOS = ["A01", "A02", "A03", "A04", "A05", "A06"]
QUERY_ITINERARIO = "partida=C01&" + "&".join(f"atractivos={a}" for a in ATRACTIVOS)


def _cliente(tmp_path, visitas=None, results=None):
    """Cliente de Flask sobre datos sintéticos propios (para variar las visitas o los resultados)."""
    processed, catalogo, results_sinteticos = carpeta_app_sintetica(tmp_path, visitas)
    datos = cargar_datos(processed, catalogo)
    return crear_app(datos, results or results_sinteticos).test_client(), datos


# ---- T13: inicio y menú ----
def test_inicio_y_menu(cliente_app):
    r = cliente_app.get("/")
    assert r.status_code == 200
    html = r.get_data(as_text=True)
    for enlace in ("/ruta", "/envolvente", "/itinerario", "/resultados/r1"):
        assert f'href="{enlace}"' in html
    assert re.findall(r"<script[^>]*>", html.lower()) == ['<script src="/static/vendor/motion.js" defer>',
                                                          '<script src="/static/app.js" defer>']


# ---- T14: /ruta ----
def test_ruta_formulario(cliente_app):
    html = cliente_app.get("/ruta").get_data(as_text=True)
    assert "<select" in html
    assert html.count("<option") == 16          # 8 lugares en origen y 8 en destino


def test_ruta_sintetica_app(tmp_path):
    cliente, datos_app = _cliente(tmp_path)     # no se mezcla con datos_app: ambos escriben en tmp_path
    r = cliente.get("/ruta?origen=C01&destino=A02")
    html = r.get_data(as_text=True)
    assert r.status_code == 200
    assert numero(datos_app.matriz.loc["C01", "A02"] / 60, 1) in html
    assert "leaflet" in html
    # el nombre debe estar en el bloque del resultado, no solo en las <option> del formulario
    resultado = html.split('id="resultado-ruta"', 1)[1]
    assert "C01 Cabecera Uno → A02 Atractivo Dos" in resultado


def test_caso_3_ruta_mismo_lugar(cliente_app):
    r = cliente_app.get("/ruta?origen=C01&destino=C01")
    html = r.get_data(as_text=True)
    assert r.status_code == 200
    assert "0,0" in html and "origen y destino son el mismo lugar" in html


def test_ruta_lugar_desconocido(cliente_app):
    r = cliente_app.get("/ruta?origen=X99&destino=C01")
    assert r.status_code == 400
    assert "lugar desconocido: X99" in r.get_data(as_text=True)


def test_ruta_incompleta(cliente_app):
    r = cliente_app.get("/ruta?origen=C01")
    html = r.get_data(as_text=True)
    assert r.status_code == 200
    assert "Tiempo de viaje" not in html and "desconocido" not in html


# ---- T15: /envolvente ----
def test_caso_10_envolvente(cliente_app):
    r = cliente_app.get("/envolvente")
    html = r.get_data(as_text=True)
    assert r.status_code == 200
    assert "4 vértices" in html and "29,6 km²" in html and "leaflet" in html
    for valor in (4.49, -75.71, 4.53, -75.65):
        assert numero(valor, 6) in html


# ---- T16: /itinerario ----
def test_itinerario_sin_parametros(cliente_app):
    html = cliente_app.get("/itinerario").get_data(as_text=True)
    assert html.count('name="atractivos"') == 6
    assert re.search(r'<option value="C01"[^>]*selected', html)


def test_itinerario_sintetico_app(tmp_path):
    cliente, datos_app = _cliente(tmp_path)
    r = cliente.get("/itinerario?" + QUERY_ITINERARIO)
    html = r.get_data(as_text=True)
    it = itinerario(datos_app, "C01", ATRACTIVOS)
    assert r.status_code == 200
    for valor in (it["held_karp"]["desplazamiento_min"], it["voraz"]["desplazamiento_min"],
                  it["diferencia_min"]):
        assert numero(valor, 1) in html
    for nombre in it["held_karp"]["recorrido"]:
        assert datos_app.nombre_de[nombre] in html
    assert "Held-Karp" in html and "Vecino más cercano" in html and "leaflet" in html


def test_itinerario_bloque_regla_no_aparece_si_cabe(cliente_app):
    html = cliente_app.get("/itinerario?" + QUERY_ITINERARIO).get_data(as_text=True)
    assert "Regla de las 11 h" not in html


def test_itinerario_bloque_regla_si_no_cabe(tmp_path):
    cliente, datos = _cliente(tmp_path, visitas=[120] * 6)
    html = cliente.get("/itinerario?" + QUERY_ITINERARIO).get_data(as_text=True)
    primero = itinerario(datos, "C01", ATRACTIVOS)["jornada"]["quitados"][0]
    assert "Regla de las 11 h" in html and primero["lugar"] in html


ENTRADAS_INVALIDAS = [
    ("C01", ATRACTIVOS[:5], "entre 6 y 8"),
    ("C01", ATRACTIVOS + ["C02", "C03", "C04"], "entre 6 y 8"),
    ("C01", [], "(llegaron 0)"),
    ("C01", ["A01", "A01", "A02", "A03", "A04", "A05"], "repetido: A01"),
    ("A01", ATRACTIVOS, "la partida A01"),
    ("C01", ATRACTIVOS[:5] + ["C02"], "C02 no es un atractivo turístico"),
    ("X99", ATRACTIVOS, "lugar desconocido: X99"),
]


@pytest.mark.parametrize("partida,atractivos,mensaje", ENTRADAS_INVALIDAS)
def test_caso_8_itinerario_400(cliente_app, monkeypatch, partida, atractivos, mensaje):
    llamadas = []
    monkeypatch.setattr("rutas.r5.servicios.resolver_por_ids",
                        lambda *a, **k: llamadas.append(1))
    consulta = f"partida={partida}&" + "&".join(f"atractivos={a}" for a in atractivos)
    r = cliente_app.get("/itinerario?" + consulta)
    html = r.get_data(as_text=True)
    assert r.status_code == 400 and mensaje in html
    assert llamadas == []
    for a in set(atractivos) & set(ATRACTIVOS):      # lo que llegó sigue marcado
        assert re.search(rf'value="{a}" checked', html)


def test_caso_14_carga_unica(cliente_app, monkeypatch):
    llamadas = {"cargar_datos": 0, "grafo": 0}

    def contar(nombre):
        def falso(*a, **k):
            llamadas[nombre] += 1
            raise AssertionError("no debe recargar datos")
        return falso
    monkeypatch.setattr("rutas.r5.app.cargar_datos", contar("cargar_datos"))
    monkeypatch.setattr("rutas.r5.datos.cargar_grafo_procesado", contar("grafo"))
    for _ in range(3):
        assert cliente_app.get("/ruta?origen=C01&destino=A02").status_code == 200
        assert cliente_app.get("/itinerario?" + QUERY_ITINERARIO).status_code == 200
    assert llamadas == {"cargar_datos": 0, "grafo": 0}


# ---- T17: resultados ----
def test_caso_11_resultados_r2(cliente_app):
    r = cliente_app.get("/resultados/r2")
    html = r.get_data(as_text=True)
    assert r.status_code == 200
    assert re.search(r'src="[^"]*r2_tiempo_vs_explorados\.png"', html)
    assert "r2_cociente.csv" in html and "<table" in html and "mediana" in html


def test_caso_11_r4_sin_exactas(cliente_app):
    r = cliente_app.get("/resultados/r4")
    html = r.get_data(as_text=True)
    assert r.status_code == 200
    assert "r4_exactas.csv" in html and "python -m rutas.r4.medir_exactas" in html


def test_caso_11_cuatro_paginas_reales(tmp_path):
    cliente, _ = _cliente(tmp_path, results=RESULTS)
    for r in ("r1", "r2", "r3", "r4"):
        assert cliente.get(f"/resultados/{r}").status_code == 200
    for r in ("r2", "r3"):
        assert "Faltan" not in cliente.get(f"/resultados/{r}").get_data(as_text=True)


def test_caso_12_imagen_permitida(cliente_app):
    r = cliente_app.get("/resultados/r2/archivo/r2_tiempo_vs_explorados.png")
    assert r.status_code == 200 and r.mimetype == "image/png"


@pytest.mark.parametrize("url", [
    "/resultados/r2/archivo/..%2F..%2FCLAUDE.md",
    "/resultados/r2/archivo/otro.png",
    "/resultados/r2/archivo/r2_cociente.csv",
    "/resultados/r9",
    "/resultados/r9/archivo/x.png",
])
def test_caso_12_rechazos(cliente_app, url):
    assert cliente_app.get(url).status_code == 404


# ---- T18: main ----
def test_caso_13_main_sin_datos(tmp_path, capsys):
    vacia = tmp_path / "vacia"
    vacia.mkdir()
    assert main([], processed=vacia) == 1
    salida = capsys.readouterr()
    texto = salida.out + salida.err
    assert "grafo_componente.graphml" in texto and "python -m rutas.r1.construir_red" in texto
    assert "Traceback" not in texto


def test_puerto_ocupado(tmp_path, capsys, monkeypatch):
    processed, catalogo, _ = carpeta_app_sintetica(tmp_path)
    monkeypatch.setattr("flask.Flask.run", lambda *a, **k: pytest.fail("no debe arrancar"))
    with socket.socket() as ocupado:
        ocupado.bind(("127.0.0.1", 0))
        puerto = ocupado.getsockname()[1]
        assert main(["--puerto", str(puerto)], processed=processed, catalogo=catalogo) == 1
    salida = capsys.readouterr()
    assert "--puerto" in salida.out + salida.err


def _main_con_run_falso(tmp_path, monkeypatch, argv):
    processed, catalogo, _ = carpeta_app_sintetica(tmp_path)
    guardado = []
    monkeypatch.setattr("flask.Flask.run", lambda self, **k: guardado.append(k))
    # El puerto se da por libre: la prueba no debe depender de lo que haya abierto en el equipo
    monkeypatch.setattr("rutas.r5.app.puerto_libre", lambda host, puerto: True)
    return main(argv, processed=processed, catalogo=catalogo), guardado


def test_main_arranca(tmp_path, monkeypatch, capsys):
    codigo, guardado = _main_con_run_falso(tmp_path, monkeypatch, ["--puerto", "5099"])
    assert codigo == 0
    assert guardado == [{"host": "127.0.0.1", "port": 5099, "debug": False}]
    salida = capsys.readouterr().out
    assert "Datos cargados en" in salida and "http://127.0.0.1:5099" in salida


def test_puerto_por_defecto(tmp_path, monkeypatch):
    codigo, guardado = _main_con_run_falso(tmp_path, monkeypatch, [])
    assert codigo == 0 and guardado[0]["port"] == 5050

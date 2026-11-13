"""Pruebas del ajuste visual de R5 (spec «Ajuste visual», casos A1 a A11).

Usan el cliente de Flask con datos sintéticos; ninguna lleva la marca `red`.
"""
import re

import pytest

from rutas.config import RAIZ
from tests.test_app_r5 import QUERY_ITINERARIO, _cliente

R5 = RAIZ / "rutas" / "r5"
PLANTILLAS = ["base", "inicio", "ruta", "envolvente", "itinerario", "resultados"]


def _leer(ruta):
    return ruta.read_text(encoding="utf-8")


def _css():
    return _leer(R5 / "static" / "estilos.css")


# ---- T25: A9, sin JavaScript propio ----
def test_a9_sin_js_propio():
    """Ni las plantillas ni la hoja de estilos llevan <script ni javascript:."""
    archivos = [R5 / "templates" / f"{nombre}.html" for nombre in PLANTILLAS]
    archivos.append(R5 / "static" / "estilos.css")
    for archivo in archivos:
        assert archivo.exists(), f"falta {archivo.name}"
        texto = _leer(archivo).lower()
        assert "<script" not in texto and "javascript:" not in texto, archivo.name


# ---- T26: paleta (A11, V0) ----
PALETA = {"guadua": "#2F4A3A", "hoja": "#5E8C61", "niebla": "#F3F6F4", "bahareque": "#D5DDD7",
          "tinta": "#1D2521", "cocora": "#1F5F8B", "cereza": "#B8322A"}


def _variable(css, nombre):
    """Valor hexadecimal de la variable --nombre, en minúsculas (None si no está definida)."""
    encontrado = re.search(rf"--{nombre}:\s*(#[0-9a-fA-F]{{6}})", css)
    return encontrado.group(1).lower() if encontrado else None


def test_a11_paleta_en_css():
    css = _css()
    for nombre, valor in PALETA.items():
        assert _variable(css, nombre) == valor.lower(), nombre


def test_a11_sin_transition_all_ni_externos():
    css = _css()
    assert not re.search(r"transition\s*:\s*all", css)
    assert "@import" not in css and "url(http" not in css


def test_a11_colores_de_mapas():
    from rutas.r5.mapas import COLORES
    css = _css()
    assert COLORES["ruta"].lower() == _variable(css, "cocora")
    assert COLORES["held_karp"].lower() == _variable(css, "cocora")
    assert COLORES["voraz"].lower() == _variable(css, "cereza")
    assert COLORES["envolvente"].lower() == _variable(css, "hoja")


# ---- T27: base, hoja enlazada, saltar al contenido, menú (A1, A2, A3, V0) ----
def test_a1_estilos_servidos(cliente_app):
    r = cliente_app.get("/static/estilos.css")
    assert r.status_code == 200 and r.mimetype == "text/css"


def test_a1_base_sin_style():
    base = _leer(R5 / "templates" / "base.html")
    assert "<style" not in base and "estilos.css" in base


PAGINAS = ["/", "/ruta", "/ruta?origen=C01&destino=A02", "/ruta?origen=X99&destino=C01", "/envolvente",
           "/itinerario", "/itinerario?" + QUERY_ITINERARIO, "/itinerario?partida=C01",
           "/resultados/r1", "/resultados/r2", "/resultados/r3", "/resultados/r4"]


@pytest.mark.parametrize("url", PAGINAS)
def test_a2_viewport_y_saltar(cliente_app, url):
    html = cliente_app.get(url).get_data(as_text=True)
    for fragmento in ('name="viewport"', "Saltar al contenido", 'href="#contenido"', 'id="contenido"'):
        assert fragmento in html, fragmento


@pytest.mark.parametrize("url,texto", [("/ruta", "Ruta"), ("/envolvente", "Envolvente"),
                                       ("/itinerario", "Itinerario"), ("/resultados/r2", "Resultados")])
def test_a3_aria_current(cliente_app, url, texto):
    html = cliente_app.get(url).get_data(as_text=True)
    assert html.count('aria-current="page"') == 1
    assert re.search(rf'aria-current="page"[^>]*>{texto}<', html)


def test_v0_tipos_firma_y_movimiento():
    css = _css()
    for fragmento in ('"Iowan Old Style"', "system-ui", "ui-monospace", "repeating-radial-gradient",
                      ":focus-visible", "scale(0.97)", "160ms ease-out",
                      "(hover: hover) and (pointer: fine)", "prefers-reduced-motion: reduce", "flex-wrap"):
        assert fragmento in css, fragmento


def test_v0_cifras_tabulares():
    """Las cifras de las tarjetas, de las celdas y la duración de visita de las casillas usan dígitos de ancho fijo, para que las columnas alineen."""
    css = _css()
    assert re.search(r"\.tarjeta dd\s*\{[^}]*font-variant-numeric:\s*tabular-nums", css), \
        "el bloque «.tarjeta dd» debe aplicar font-variant-numeric: tabular-nums"
    # `^td` al inicio de línea: evita confundirlo con el bloque «th, td».
    assert re.search(r"(?m)^td\s*\{[^}]*font-variant-numeric:\s*tabular-nums", css), \
        "el bloque «td» debe aplicar font-variant-numeric: tabular-nums"
    # La duración de visita de las casillas (`.visita`) también lleva cifras tabulares.
    assert re.search(r"(?m)^\.visita\s*\{[^}]*font-variant-numeric:\s*tabular-nums", css), \
        "el bloque «.visita» debe aplicar font-variant-numeric: tabular-nums"


def test_v0_contorno_select():
    """El contorno del «select» usa var(--hoja): Bahareque sobre blanco da 1,39:1 y el criterio WCAG 1.4.11 (componentes de interfaz) pide al menos 3:1; Hoja da 3,89:1."""
    css = _css()
    assert re.search(r"(?m)^select\s*\{[^}]*border(-color)?:[^;}]*var\(--hoja\)", css), \
        "el contorno del «select» debe usar var(--hoja): Bahareque sobre blanco da 1,39:1 y WCAG 1.4.11 pide ≥ 3:1"


# ---- T28: formularios y mensajes (A4, A6, V3, V6) ----
def test_a4_labels_y_botones(cliente_app):
    ruta = cliente_app.get("/ruta").get_data(as_text=True)
    for fragmento in ('<label for="origen">', '<label for="destino">', 'id="origen"', 'id="destino"',
                      ">Calcular ruta</button>"):
        assert fragmento in ruta, fragmento
    itinerario = cliente_app.get("/itinerario").get_data(as_text=True)
    for fragmento in ('<label for="partida">', 'id="partida"', "<fieldset",
                      "<legend>Atractivos (elige de 6 a 8)</legend>", ">Calcular itinerario</button>"):
        assert fragmento in itinerario, fragmento


def test_v3_fieldset_y_cuadricula(cliente_app):
    html = cliente_app.get("/itinerario").get_data(as_text=True)
    campo = html[html.index("<fieldset"):html.index("</fieldset>")]
    assert campo.count('name="atractivos"') == 6
    assert 'class="casillas"' in campo
    assert campo.count('class="visita"') == 6
    assert re.search(r"\.casillas\s*\{[^}]*grid-template-columns", _css())


def test_a6_alert_y_status(cliente_app):
    html = cliente_app.get("/itinerario?partida=C01&atractivos=A01")
    assert html.status_code == 400
    assert re.search(r'role="alert"[^>]*>[^<]*entre 6 y 8', html.get_data(as_text=True))
    html = cliente_app.get("/ruta?origen=X99&destino=C01").get_data(as_text=True)
    assert re.search(r'role="alert"[^>]*>[^<]*lugar desconocido: X99', html)
    html = cliente_app.get("/ruta?origen=C01&destino=C01").get_data(as_text=True)
    assert re.search(r'role="status"[^>]*>origen y destino son el mismo lugar', html)
    assert 'role="alert"' not in cliente_app.get("/ruta?origen=C01&destino=A02").get_data(as_text=True)


# ---- T29 a T31: tarjetas de resumen (V4) y mapas con título (A5, V7) ----
def _bloque(html, inicio, fin):
    """Texto entre la primera aparición de `inicio` y el `fin` que le sigue."""
    desde = html.index(inicio)
    return html[desde:html.index(fin, desde)]


def test_v4_tarjetas_ruta(tmp_path):
    from rutas.r5.formato import numero
    cliente, datos = _cliente(tmp_path)
    html = cliente.get("/ruta?origen=C01&destino=A02").get_data(as_text=True)
    tarjetas = _bloque(html, '<dl class="resumen"', "</dl>")
    minutos = numero(datos.matriz.loc["C01", "A02"] / 60, 1)
    for texto in ("Tiempo de viaje", f"{minutos} min", "Distancia", "Nodos explorados"):
        assert texto in tarjetas, texto


def test_v4_tarjetas_envolvente(cliente_app):
    html = cliente_app.get("/envolvente").get_data(as_text=True)
    tarjetas = _bloque(html, '<dl class="resumen"', "</dl>")
    assert "4 vértices" in tarjetas and "29,6 km²" in tarjetas


def test_v8_tabla_envolvente(cliente_app):
    html = cliente_app.get("/envolvente").get_data(as_text=True)
    assert "<caption>Vértices de la envolvente (grados)</caption>" in html
    assert "<thead>" in html
    assert html.count('scope="col"') == 3 and html.count('scope="row"') == 4
    assert "<th></th>" not in html


def test_v4_tarjetas_itinerario(tmp_path):
    from rutas.r5.formato import numero
    from rutas.r5.servicios import itinerario
    cliente, datos = _cliente(tmp_path)
    html = cliente.get("/itinerario?" + QUERY_ITINERARIO).get_data(as_text=True)
    it = itinerario(datos, "C01", ["A01", "A02", "A03", "A04", "A05", "A06"])
    tarjetas = _bloque(html, '<dl class="resumen"', "</dl>")
    esperados = [numero(it["held_karp"]["desplazamiento_min"], 1), numero(it["voraz"]["desplazamiento_min"], 1),
                 numero(it["diferencia_min"], 1), numero(it["brecha_pct"], 2) + " %"]
    for valor in esperados:
        assert valor in tarjetas, valor


def test_a7_leyenda_con_colores(cliente_app):
    from rutas.r5.mapas import COLORES
    html = cliente_app.get("/itinerario?" + QUERY_ITINERARIO).get_data(as_text=True)
    leyenda = _bloque(html, 'class="leyenda"', "</ul>")
    for texto in (COLORES["held_karp"], COLORES["voraz"], "Held-Karp", "Vecino más cercano"):
        assert texto in leyenda, texto


def test_v5_tabla_comparacion(cliente_app):
    html = cliente_app.get("/itinerario?" + QUERY_ITINERARIO).get_data(as_text=True)
    tabla = _bloque(html, 'class="comparacion"', "</table>")
    assert "<caption>Held-Karp frente al vecino más cercano</caption>" in tabla
    assert '<th scope="col">Medida</th>' in tabla
    assert tabla.count('scope="row"') == 6
    assert "<th></th>" not in tabla
    assert re.search(r'<th scope="col" class="metodo-hk">', tabla)
    assert re.search(r'<th scope="col" class="metodo-voraz">', tabla)


def test_v5_colores_encabezado_metodos():
    """El encabezado de cada método en la tabla de comparación usa el mismo color que su línea en el mapa."""
    css = _css()
    # `^thead` al inicio de línea y regex limitada al bloque (`[^}]*`): no se confunde con las tarjetas.
    assert re.search(r"(?m)^thead \.metodo-hk\s*\{[^}]*background(-color)?:\s*var\(--cocora\)", css), \
        "el encabezado «thead .metodo-hk» debe tener de fondo var(--cocora), el color de Held-Karp en el mapa"
    assert re.search(r"(?m)^thead \.metodo-voraz\s*\{[^}]*background(-color)?:\s*var\(--cereza\)", css), \
        "el encabezado «thead .metodo-voraz» debe tener de fondo var(--cereza), el color del vecino más cercano en el mapa"


def test_v5_orden_de_la_pagina(tmp_path):
    cliente, _ = _cliente(tmp_path, visitas=[120] * 6)
    html = cliente.get("/itinerario?" + QUERY_ITINERARIO).get_data(as_text=True)
    posiciones = [html.index(marca) for marca in
                  ('class="resumen"', 'class="leyenda"', "<iframe", 'class="comparacion"', 'class="regla"')]
    assert posiciones == sorted(posiciones)


IFRAMES = [("/ruta?origen=C01&destino=A02", "Mapa de la ruta"),
          ("/envolvente", "Mapa de la envolvente"),
          ("/itinerario?" + QUERY_ITINERARIO, "Mapa del itinerario")]


@pytest.mark.parametrize("url,titulo", IFRAMES)
def test_a5_iframes_con_title(cliente_app, url, titulo):
    html = cliente_app.get(url).get_data(as_text=True)
    assert html.count("<iframe") == len(re.findall(r'<iframe[^>]*title="', html)) >= 1
    assert f'title="{titulo}"' in html


# ---- T32: resultados con títulos, imágenes descritas y navegación (V8, V9, A3, A8) ----
def test_titulos_cubren_la_lista_fija():
    from rutas.r5.app import TITULOS_RESULTADOS
    from rutas.r5.servicios import ARCHIVOS_RESULTADOS
    archivos = {a for g in ARCHIVOS_RESULTADOS.values() for a, _ in g["imagenes"] + g["tablas"]}
    assert set(TITULOS_RESULTADOS) == archivos and len(archivos) == 16
    titulos = [titulo for titulo, _ in TITULOS_RESULTADOS.values()]
    assert all(titulos) and len(set(titulos)) == len(titulos)
    for archivo, (titulo, descripcion) in TITULOS_RESULTADOS.items():
        assert titulo != archivo
        assert descripcion.endswith(".")
        assert "Faltan" not in titulo + descripcion and "Regla de las 11 h" not in titulo + descripcion
    assert TITULOS_RESULTADOS["r2_cociente.csv"][0] == "Cociente lineal / cola de prioridad (10 pares cercanos)"


def _tamano_png(ruta):
    """(ancho, alto) de la cabecera IHDR de una PNG: bytes 16-24 del archivo."""
    import struct
    return struct.unpack(">II", ruta.read_bytes()[16:24])


def test_tamanos_de_imagenes():
    from rutas.config import RESULTS
    from rutas.r5.app import TAMANOS_IMAGENES
    assert set(TAMANOS_IMAGENES) == {"r1_tiempos_componente.png", "r2_tiempo_vs_explorados.png",
                                     "r3_envolvente.png", "r4_tiempo_vs_k.png"}
    for r, archivo in (("r2", "r2_tiempo_vs_explorados.png"), ("r3", "r3_envolvente.png")):
        assert TAMANOS_IMAGENES[archivo] == _tamano_png(RESULTS / r / archivo)


def test_tabla_con_titulo():
    from markupsafe import Markup
    from rutas.r5.app import tabla_con_titulo
    entrada = '<table class="dataframe tabla"><thead><tr><th>a</th><th>b</th></tr></thead><tbody><tr><td>1</td><td>2</td></tr></tbody></table>'
    salida = tabla_con_titulo(entrada, "x < y.", "archivo.csv")
    assert isinstance(salida, Markup)
    assert salida.startswith('<table class="dataframe tabla"><caption>')
    assert "x &lt; y." in salida and "<code>archivo.csv</code>" in salida
    assert salida.count('<th scope="col">') == 2 and "<th>" not in salida
    assert "<td>1</td><td>2</td>" in salida


def test_a8_imagen_y_titulo(cliente_app):
    html = cliente_app.get("/resultados/r2").get_data(as_text=True)
    imagen = re.search(r"<img[^>]*>", html).group(0)
    alt = re.search(r'alt="([^"]+)"', imagen).group(1)
    assert alt != "r2_tiempo_vs_explorados.png"
    for atributo in ('width="1050"', 'height="675"', 'loading="lazy"'):
        assert atributo in imagen, atributo
    assert "Cociente lineal / cola de prioridad (10 pares cercanos)" in html


def test_v8_tablas_de_resultados(cliente_app):
    html = cliente_app.get("/resultados/r2").get_data(as_text=True)
    tablas = html.count("<table")
    assert tablas == 3
    assert len(re.findall(r"<table[^>]*><caption>", html)) == tablas
    assert html.count('class="tabla-ancha"') == tablas
    assert 'scope="col"' in html


def test_v9_navegacion_requerimientos(cliente_app):
    html = cliente_app.get("/resultados/r3").get_data(as_text=True)
    nav = _bloque(html, 'class="requerimientos"', "</nav>")
    for r in ("r1", "r2", "r3", "r4"):
        assert f'href="/resultados/{r}"' in nav
    assert re.search(r'href="/resultados/r3"[^>]*aria-current="true"|aria-current="true"[^>]*href="/resultados/r3"', nav)
    assert nav.count('aria-current="true"') == 1
    assert html.count('aria-current="page"') == 1


def test_faltantes_con_titulo(cliente_app):
    from rutas.r5.app import TITULOS_RESULTADOS
    html = cliente_app.get("/resultados/r4").get_data(as_text=True)
    faltantes = _bloque(html, 'class="faltantes"', "</section>")
    for texto in (TITULOS_RESULTADOS["r4_exactas.csv"][0], "r4_exactas.csv", "python -m rutas.r4.medir_exactas"):
        assert texto in faltantes, texto


# ---- T33: inicio con cuatro tarjetas (V10) ----
def test_v10_inicio_tarjetas(cliente_app):
    html = cliente_app.get("/").get_data(as_text=True)
    assert html.count('class="tarjeta-seccion"') == 4
    tarjetas = _bloque(html, 'class="secciones"', "</ul>")
    for enlace in ("/ruta", "/envolvente", "/itinerario", "/resultados/r1"):
        assert f'href="{enlace}"' in tarjetas
    for texto in ("Dijkstra con cola de prioridad", "QuickHull", "Held-Karp", "vecino más cercano"):
        assert texto in tarjetas, texto
    assert "nodos de la red" in html and "envolvente convexa de los 42 lugares" not in html
    assert re.search(r'class="marca"[^>]*aria-current="page"', html)

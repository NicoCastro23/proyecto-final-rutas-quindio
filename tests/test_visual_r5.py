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


# ---- T26: sin transition: all ni recursos externos (A11) ----
def test_a11_sin_transition_all_ni_externos():
    css = _css()
    assert not re.search(r"transition\s*:\s*all", css)
    assert "@import" not in css and "url(http" not in css


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
                                       ("/itinerario", "Itinerario")])
def test_a3_aria_current(cliente_app, url, texto):
    html = cliente_app.get(url).get_data(as_text=True)
    assert html.count('aria-current="page"') == 1
    assert re.search(rf'aria-current="page"[^>]*>{texto}<', html)


def _css_sin_comentarios():
    """El CSS sin comentarios, para que un fragmento escrito solo en un comentario no cuente."""
    return re.sub(r"/\*.*?\*/", "", _css(), flags=re.S)


def _bloque_media(css, consulta):
    """Contenido del bloque «@media consulta { ... }» o None si no existe.

    Las llaves se anidan (el @media contiene reglas con sus propias llaves), así que se
    cuenta la profundidad desde la «{» que abre el @media hasta la «}» que la cierra.
    """
    inicio = css.find("@media " + consulta)
    if inicio == -1:
        return None
    apertura = css.find("{", inicio)
    if apertura == -1:
        return None
    profundidad = 0
    for posicion in range(apertura, len(css)):
        if css[posicion] == "{":
            profundidad += 1
        elif css[posicion] == "}":
            profundidad -= 1
            if profundidad == 0:
                return css[apertura + 1:posicion]
    return None


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


# ---- T28: formularios y mensajes (A4, A6, V3, V6) ----
def test_a4_labels_y_botones(cliente_app):
    ruta = cliente_app.get("/ruta").get_data(as_text=True)
    for fragmento in ('<label for="origen">', '<label for="destino">', 'id="origen"', 'id="destino"',
                      ">Calcular ruta</button>"):
        assert fragmento in ruta, fragmento
    itinerario = cliente_app.get("/itinerario").get_data(as_text=True)
    for fragmento in ('<label for="partida">', 'id="partida"', "<fieldset",
                      "<legend>Atractivos</legend>", ">Calcular itinerario</button>"):
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


# ======================================================================================
# Diseño v2 (apple-design). Casos B1 a B8 de la spec; ninguna prueba lleva la marca `red`.
# ======================================================================================
import hashlib

STATIC = R5 / "static"
SHA256_MOTION = "521cfef8910fdd997463ea9881d4b790e017331e3d2f79c02adfc4d5fe1f2cae"


# ---- T36: Motion en vendor/ con su hash (B3) ----
def test_b3_motion_con_hash_y_licencia():
    motion = STATIC / "vendor" / "motion.js"
    licencia = STATIC / "vendor" / "LICENSE.md"
    assert motion.exists(), "falta static/vendor/motion.js"
    assert hashlib.sha256(motion.read_bytes()).hexdigest() == SHA256_MOTION
    assert licencia.exists() and "MIT" in _leer(licencia)
    assert "Motion" in _leer(motion)


@pytest.mark.parametrize("url", ["/static/vendor/motion.js", "/static/app.js"])
def test_b3_js_servidos(cliente_app, url):
    assert cliente_app.get(url).status_code == 200


# ---- T37: guardia de JavaScript (B2) ----
SCRIPT_MOTION = '<script src="/static/vendor/motion.js" defer></script>'
SCRIPT_APP = '<script src="/static/app.js" defer></script>'


def _plantillas():
    return {nombre: _leer(R5 / "templates" / f"{nombre}.html") for nombre in PLANTILLAS}


def test_b2_scripts_solo_en_base():
    """base.html tiene exactamente los dos <script> permitidos, en <head> y en ese orden; las demás, ninguno."""
    plantillas = _plantillas()
    base = plantillas["base"]
    head = base[base.index("<head>"):base.index("</head>")]
    assert base.lower().count("<script") == 2
    assert head.index(SCRIPT_MOTION) < head.index(SCRIPT_APP)
    for nombre, texto in plantillas.items():
        if nombre != "base":
            assert "<script" not in texto.lower(), nombre


def test_b2_sin_js_en_linea():
    """Todo <script> lleva src= y se cierra vacío; sin atributos on…= ni javascript: en plantillas ni en el CSS."""
    for nombre, texto in _plantillas().items():
        for etiqueta in re.findall(r"<script[^>]*>.*?</script>", texto, flags=re.S | re.I):
            assert re.fullmatch(r'<script src="[^"]+" defer></script>', etiqueta), (nombre, etiqueta)
        assert not re.search(r"\son[a-z]+\s*=", texto, flags=re.I), f"{nombre} tiene un atributo on…="
        assert "javascript:" not in texto.lower(), nombre
    assert "javascript:" not in _css().lower()


def test_b2_solo_dos_archivos_js():
    encontrados = {ruta.relative_to(STATIC).as_posix() for ruta in STATIC.rglob("*.js")}
    assert encontrados == {"app.js", "vendor/motion.js"}


def test_b2_app_js_limites():
    texto = _leer(STATIC / "app.js")
    assert len(texto.splitlines()) <= 150
    for prohibido in ("fetch(", "XMLHttpRequest", "eval(", "innerHTML", "document.write", "http"):
        assert prohibido not in texto, prohibido
    assert "matchMedia" in texto and "prefers-reduced-motion" in texto


@pytest.mark.parametrize("url", PAGINAS)
def test_b2_html_servido_solo_dos_scripts(cliente_app, url):
    """Los <script> de Folium van escapados dentro de srcdoc, así que el HTML servido tiene solo 2."""
    html = cliente_app.get(url).get_data(as_text=True)
    assert html.lower().count("<script") == 2


# ---- T38: colores, tipografía, contraste y movimiento M1 (B4, B5, D1, D2, D6, D8) ----
CLARO = {"fondo": "#F5F5F7", "superficie": "#FFFFFF", "texto": "#1D1D1F", "texto-secundario": "#6E6E73",
         "separador": "rgba(0,0,0,.1)", "acento": "#0071E3", "metodo-hk": "#007AFF",
         "metodo-voraz": "#FF9500", "metodo-envolvente": "#34C759"}
OSCURO = {"fondo": "#000000", "superficie": "#1C1C1E", "texto": "#F5F5F7", "texto-secundario": "#98989D",
          "separador": "rgba(255,255,255,.15)", "acento": "#2997FF"}
SELECTORES_M1 = r"\.boton-principal{}\s*,\s*\.ficha{}\s*,\s*\.segmentado a{}"


def _normal(valor):
    """Valor de una variable sin espacios, en minúsculas y con «.1» en lugar de «0.1» (para comparar)."""
    return re.sub(r"(?<!\d)0\.", ".", valor.replace(" ", "").lower())


def _variables(bloque):
    """Diccionario {nombre: valor} de las variables «--nombre: valor;» de un bloque de CSS."""
    return {n: _normal(v) for n, v in re.findall(r"--([a-z-]+)\s*:\s*([^;]+);", bloque)}


def _variables_claro_y_oscuro():
    css = _css_sin_comentarios()
    oscuro = _bloque_media(css, "(prefers-color-scheme: dark)")
    assert oscuro is not None, "falta el bloque «@media (prefers-color-scheme: dark)»"
    primero = re.search(r":root\s*\{([^}]*)\}", css.replace(oscuro, "")).group(1)
    return _variables(primero), _variables(oscuro)


def _regla(css, selector):
    """Cuerpo de la regla cuyo selector empieza una línea (None si no existe)."""
    encontrada = re.search(r"(?m)^" + re.escape(selector) + r"\s*\{([^}]*)\}", css)
    return encontrada.group(1) if encontrada else None


def _luminancia(hexadecimal):
    canales = [int(hexadecimal.lstrip("#")[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    lineales = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in canales]
    return 0.2126 * lineales[0] + 0.7152 * lineales[1] + 0.0722 * lineales[2]


def _contraste(a, b):
    """Razón de contraste WCAG 2.x entre dos colores «#RRGGBB»."""
    claro, oscuro = sorted((_luminancia(a), _luminancia(b)), reverse=True)
    return (claro + 0.05) / (oscuro + 0.05)


def test_b4_variables_claro_y_oscuro():
    claro, oscuro = _variables_claro_y_oscuro()
    for nombre, valor in CLARO.items():
        assert claro.get(nombre) == _normal(valor), f"claro --{nombre}"
    for nombre, valor in OSCURO.items():
        assert oscuro.get(nombre) == _normal(valor), f"oscuro --{nombre}"


def test_b4_color_scheme():
    assert "color-scheme: light dark" in _css_sin_comentarios()
    assert '<meta name="color-scheme" content="light dark">' in _leer(R5 / "templates" / "base.html")


def test_b4_tipografia():
    css = _css_sin_comentarios()
    assert '-apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, sans-serif' in css
    assert "font-optical-sizing: auto" in css and "ui-monospace" in css and ":focus-visible" in css
    h1 = _regla(css, "h1")
    assert h1 and "clamp(" in h1 and "line-height: 1.05" in h1 and "letter-spacing: -0.02em" in h1
    for familia in re.findall(r"font-family\s*:\s*([^;]+);", css):
        assert not re.search(r"(?<!sans-)\bserif\b", familia), familia


def test_b4_contraste():
    claro, oscuro = _variables_claro_y_oscuro()
    for modo, variables in (("claro", claro), ("oscuro", {**claro, **oscuro})):
        for fondo in ("fondo", "superficie"):
            for texto in ("texto", "texto-secundario"):
                assert _contraste(variables[texto].upper(), variables[fondo].upper()) >= 4.5, (modo, texto, fondo)
        assert _contraste(variables["acento"].upper(), variables["superficie"].upper()) >= 4.5, modo
        assert _contraste(variables["texto-boton"].upper(), variables["relleno-boton"].upper()) >= 4.5, modo
        assert _contraste(variables["borde-control"].upper(), variables["superficie"].upper()) >= 3, modo


def test_b4_contorno_de_controles():
    regla = _regla(_css_sin_comentarios(), "select")
    assert regla and re.search(r"border(-color)?:[^;}]*var\(--borde-control\)", regla)


def test_b5_colores_de_metodos():
    from rutas.r5.mapas import COLORES
    claro, oscuro = _variables_claro_y_oscuro()
    esperados = {"ruta": "#007AFF", "held_karp": "#007AFF", "voraz": "#FF9500", "envolvente": "#34C759"}
    assert COLORES == esperados
    for clave, variable in (("held_karp", "metodo-hk"), ("voraz", "metodo-voraz"), ("envolvente", "metodo-envolvente")):
        assert claro[variable] == COLORES[clave].lower(), variable
        assert variable not in oscuro, f"--{variable} no cambia en modo oscuro (el mapa sigue claro)"


def test_b5_encabezados_de_metodo():
    """Franja y no fondo: blanco sobre #007AFF da 4,02:1 (DV-7)."""
    css = _css_sin_comentarios()
    for selector, variable in (("thead .metodo-hk", "--metodo-hk"), ("thead .metodo-voraz", "--metodo-voraz")):
        regla = _regla(css, selector)
        assert regla and f"var({variable})" in regla and "background" not in regla, selector


def test_d8_sin_rastros_de_v1():
    from rutas.r5.mapas import COLORES
    css = _css_sin_comentarios()
    for prohibido in ("Iowan", "Palatino", "Georgia", "repeating-radial-gradient"):
        assert prohibido not in css, prohibido
    assert "serif" not in css.replace("sans-serif", "")
    for variable in ("guadua", "hoja", "niebla", "bahareque", "tinta", "cocora", "cereza"):
        assert f"--{variable}" not in css, variable
    assert not set(COLORES.values()) & {"#1F5F8B", "#B8322A", "#5E8C61"}
    for nombre, texto in _plantillas().items():
        assert 'class="cabecera"' not in texto, nombre


def test_b4_movimiento_m1():
    css = _css_sin_comentarios()
    assert re.search(SELECTORES_M1.format("", "", "") + r"\s*\{[^}]*transition:\s*transform 100ms ease-out", css)
    assert re.search(SELECTORES_M1.format(":active", ":active", ":active") + r"\s*\{[^}]*transform:\s*scale\(0\.97\)", css)
    for declaracion in re.findall(r"transition\s*:\s*([^;}]+)", css):
        for parte in declaracion.split(","):
            assert parte.split()[0] in ("transform", "opacity"), declaracion


def test_b4_movimiento_reducido():
    bloque = _bloque_media(_css_sin_comentarios(), "(prefers-reduced-motion: reduce)")
    assert bloque is not None, "falta el bloque «@media (prefers-reduced-motion: reduce)»"
    assert re.search(SELECTORES_M1.format(":active", ":active", ":active") + r"\s*\{[^}]*transform:\s*none", bloque)


# ---- T39: barra translúcida, superficies y preferencias del sistema (D3, D4, B4) ----
def _cuerpo_de(css, selector):
    """Cuerpos de todas las reglas cuya lista de selectores incluye `selector`, unidos (vacío si no hay)."""
    cuerpos = []
    for lista, cuerpo in re.findall(r"([^{}]+)\{([^{}]*)\}", css):
        if selector in [s.strip() for s in lista.split(",")]:
            cuerpos.append(cuerpo)
    return " ".join(cuerpos)


def test_b4_barra_translucida():
    css = _css_sin_comentarios()
    barra = _regla(css, ".barra")        # la regla principal (las de @media y @supports van indentadas)
    assert barra, "falta la regla «.barra {»"
    assert "position: sticky" in barra
    assert "backdrop-filter: blur(20px) saturate(180%)" in barra
    assert "-webkit-backdrop-filter: blur(20px) saturate(180%)" in barra
    assert "border-bottom" not in barra, "en lugar de una línea divisoria, un desvanecido"
    assert "linear-gradient" in _cuerpo_de(css, ".barra::after")


def test_b4_preferencias():
    css = _css_sin_comentarios()
    transparencia = _bloque_media(css, "(prefers-reduced-transparency: reduce)")
    assert transparencia is not None and "backdrop-filter: none" in _cuerpo_de(transparencia, ".barra")
    contraste = _bloque_media(css, "(prefers-contrast: more)")
    assert contraste is not None and "backdrop-filter: none" in _cuerpo_de(contraste, ".barra")
    assert re.search(r"border(-bottom)?:\s*1px solid", contraste)
    soporte = re.search(r"@supports not[^{]*\{(.*?)\}\s*\}", css, flags=re.S)
    assert soporte and "background: var(--fondo)" in soporte.group(1)


def test_d3_superficies():
    css = _css_sin_comentarios()
    assert "--radio: 18px" in css
    tarjeta = _cuerpo_de(css, ".tarjeta")
    assert "var(--radio)" in tarjeta and "var(--sombra-chica)" in tarjeta
    for selector in ("iframe.mapa", ".tarjeta-seccion"):
        assert "var(--sombra-grande)" in _cuerpo_de(css, selector), selector
    assert "color-scheme: light" in _cuerpo_de(css, "iframe.mapa")


@pytest.mark.parametrize("url", PAGINAS)
def test_d4_menu(cliente_app, url):
    html = cliente_app.get(url).get_data(as_text=True)
    barra = _bloque(html, '<header class="barra">', "</header>")
    assert 'class="marca"' in barra
    menu = _bloque(barra, '<nav class="menu"', "</nav>")
    assert re.findall(r"<a [^>]*>([^<]+)</a>", menu) == ["Ruta", "Envolvente", "Itinerario", "Resultados"]


# ---- T40: lista agrupada, botón píldora y errores con su siguiente paso (D5) ----
def test_d5_lista_agrupada(cliente_app):
    ruta = cliente_app.get("/ruta").get_data(as_text=True)
    grupo = _bloque(ruta, '<div class="grupo">', "<button")
    filas = re.findall(r'<div class="fila">(.*?)</div>', grupo, flags=re.S)
    assert len(filas) == 2
    for fila, campo in zip(filas, ("origen", "destino")):
        assert f'<label for="{campo}">' in fila and f'<select id="{campo}" name="{campo}">' in fila
    itinerario = cliente_app.get("/itinerario").get_data(as_text=True)
    grupo = _bloque(itinerario, '<div class="grupo">', "<fieldset")
    filas = re.findall(r'<div class="fila">(.*?)</div>', grupo, flags=re.S)
    assert len(filas) == 1 and '<label for="partida">' in filas[0] and '<select id="partida"' in filas[0]
    assert "var(--radio)" in _cuerpo_de(_css_sin_comentarios(), ".grupo")


def test_d5_boton_principal(cliente_app):
    assert 'class="boton-principal">Calcular ruta</button>' in cliente_app.get("/ruta").get_data(as_text=True)
    assert 'class="boton-principal">Calcular itinerario</button>' in cliente_app.get("/itinerario").get_data(as_text=True)
    boton = _cuerpo_de(_css_sin_comentarios(), ".boton-principal")
    for variable in ("--radio-pildora", "--relleno-boton", "--texto-boton"):
        assert f"var({variable})" in boton, variable


def test_d5_error_con_siguiente_paso(cliente_app):
    html = cliente_app.get("/ruta?origen=X99&destino=C01").get_data(as_text=True)
    assert re.search(r'role="alert"[^>]*>[^<]*lugar desconocido: X99[^<]*Elige el origen y el destino', html)
    html = cliente_app.get("/itinerario?partida=C01&atractivos=A01").get_data(as_text=True)
    assert re.search(r'role="alert"[^>]*>[^<]*entre 6 y 8[^<]*vuelve a calcular', html)


# ---- T41: fichas de atractivos y contador renderizado por el servidor (D5, M3, B6) ----
@pytest.mark.parametrize("n,cuenta,estado,en_rango", [
    (0, "0 elegidos", "faltan 6", False), (1, "1 elegido", "faltan 5", False),
    (5, "5 elegidos", "falta 1", False), (6, "6 elegidos", "listo para calcular", True),
    (8, "8 elegidos", "listo para calcular", True), (9, "9 elegidos", "sobra 1", False),
    (10, "10 elegidos", "sobran 2", False)])
def test_contador_elegidos(n, cuenta, estado, en_rango):
    from rutas.r5.app import contador_elegidos
    assert contador_elegidos(n) == {"cuenta": cuenta, "estado": estado, "en_rango": en_rango}


def test_contador_limites_iguales_a_servicios(tmp_path):
    from rutas.r5.app import MAX_ATRACTIVOS, MIN_ATRACTIVOS
    from rutas.r5.servicios import ErrorEntrada, validar_itinerario
    _, datos = _cliente(tmp_path)
    with pytest.raises(ErrorEntrada) as error:
        validar_itinerario(datos, "C01", [])
    assert f"entre {MIN_ATRACTIVOS} y {MAX_ATRACTIVOS}" in str(error.value)


@pytest.mark.parametrize("consulta,texto,estado", [
    ("", "! 0 elegidos (elige de 6 a 8) · faltan 6", "fuera"),
    (QUERY_ITINERARIO, "✓ 6 elegidos (elige de 6 a 8) · listo para calcular", "en-rango"),
    ("?partida=C01&atractivos=A01", "! 1 elegido (elige de 6 a 8) · faltan 5", "fuera"),
    ("?partida=C01&atractivos=A01&atractivos=A01&atractivos=C02", "! 1 elegido (elige de 6 a 8) · faltan 5", "fuera")])
def test_b6_contador_en_la_pagina(cliente_app, consulta, texto, estado):
    url = "/itinerario" + (consulta if consulta.startswith("?") or not consulta else "?" + consulta)
    html = cliente_app.get(url).get_data(as_text=True)
    contador = re.search(r'<p id="contador"([^>]*)>(.*?)</p>', html, flags=re.S)
    assert contador, "falta el contador"
    assert 'aria-live="polite"' in contador.group(1) and f'data-estado="{estado}"' in contador.group(1)
    assert " ".join(re.sub(r"<[^>]+>", " ", contador.group(2)).split()) == texto
    assert '<fieldset aria-describedby="contador">' in html


def test_d5_fichas(tmp_path):
    cliente, datos = _cliente(tmp_path)
    html = cliente.get("/itinerario").get_data(as_text=True)
    fichas = re.findall(r'<label class="ficha">(.*?)</label>', html, flags=re.S)
    assert len(fichas) == 6
    for ficha in fichas:
        assert ficha.count('<input type="checkbox" name="atractivos"') == 1
        id_atractivo = re.search(r'value="([^"]+)"', ficha).group(1)
        assert datos.nombre_de[id_atractivo] in ficha and 'class="visita"' in ficha


# ---- T42: app.js, entrada de las tarjetas (M2) y contador en vivo (M3) ----
def test_b2_app_js_m2_m3():
    """Las pruebas no ejecutan JavaScript: se comprueba el texto. El comportamiento real se ve en B9."""
    js = _leer(STATIC / "app.js")
    for fragmento in ('type: "spring"', "duration: 0.4", "stagger(0.04)", "opacity: [0, 1]", "y: [8, 0]",
                      "duration: 0.2", 'getElementById("contador")', '"change"', "textContent",
                      "MINIMO = 6", "MAXIMO = 8"):
        assert fragmento in js, fragmento
    rebotes = re.findall(r"bounce:\s*([\d.]+)", js)
    assert rebotes and all(valor == "0" for valor in rebotes), f"nada se lanza con un gesto: sin rebote ({rebotes})"
    for texto in ("elegido", "elegidos", "falta", "faltan", "sobra", "sobran", "listo para calcular"):
        assert f'"{texto}"' in js, texto


# ---- T43: control segmentado en Resultados y transición entre páginas (D4, M4, B7) ----
@pytest.mark.parametrize("r", ["r2", "r3"])
def test_b7_control_segmentado(cliente_app, r):
    html = cliente_app.get(f"/resultados/{r}").get_data(as_text=True)
    nav = _bloque(html, '<nav class="segmentado"', "</nav>")
    assert re.findall(r'<a href="/resultados/(r\d)"', nav) == ["r1", "r2", "r3", "r4"]
    assert re.search(rf'aria-current="page"[^>]*>{r.upper()}<', nav)
    assert html.count('aria-current="page"') == 1, "un solo «page» en la página: el segmento actual"
    assert re.search(r'aria-current="true"[^>]*>Resultados<', html), "el menú marca la sección, no la página"
    assert html.count('class="indicador"') == 1
    assert re.search(rf'<a href="/resultados/{r}" aria-current="page">{r.upper()}<span class="indicador"', nav)


def test_b4_view_transition():
    css = _css_sin_comentarios()
    bloque = _bloque_media(css, "(prefers-reduced-motion: no-preference)")
    assert bloque is not None and re.search(r"@view-transition\s*\{\s*navigation:\s*auto;\s*\}", bloque)
    assert "@view-transition" not in css.replace(bloque, "")
    assert "view-transition-name: indicador-segmento" in _cuerpo_de(css, ".segmentado .indicador")
    assert "::view-transition-group(indicador-segmento)" in css


# ---- T44: encabezado de cada página e inicio (D0, D7) ----
@pytest.mark.parametrize("url", ["/", "/ruta", "/envolvente", "/itinerario", "/resultados/r1"])
def test_d0_titulo_y_entradilla(cliente_app, url):
    html = cliente_app.get(url).get_data(as_text=True)
    assert html.count("<h1") == 1
    entradilla = re.search(r'</h1>\s*<p class="entradilla">(.*?)</p>', html, flags=re.S)
    assert entradilla, "la entradilla va justo después del <h1>"
    for prohibido in ("Tiempo de viaje", "desconocido", "Faltan", "Regla de las 11 h"):
        assert prohibido not in entradilla.group(1), prohibido
    for marca in ("<form", '<nav class="segmentado"', "<dl"):
        if marca in html:
            assert html.index(marca) > entradilla.end(), marca


def test_d7_inicio(cliente_app):
    html = cliente_app.get("/").get_data(as_text=True)
    tarjetas = re.findall(r'<li class="tarjeta-seccion">(.*?)</li>', html, flags=re.S)
    assert len(tarjetas) == 4 and all(t.count("<a ") == 1 for t in tarjetas)
    enlace = _cuerpo_de(_css_sin_comentarios(), ".tarjeta-seccion h2 a::after")
    assert "inset: 0" in enlace

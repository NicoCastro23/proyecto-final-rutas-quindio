"""Pruebas de los mapas de R5: se busca texto en el HTML que genera Folium (no se abre navegador)."""
from rutas.r5.mapas import COLORES, mapa_envolvente, mapa_itinerario, mapa_ruta
from rutas.r5.servicios import itinerario, ruta_entre

ATRACTIVOS = ["A01", "A02", "A03", "A04", "A05", "A06"]


def test_mapa_ruta(datos_app):
    html = mapa_ruta(datos_app, ruta_entre(datos_app, "C01", "A02"))
    assert "leaflet" in html and "L.polyline" in html
    assert "4.505" in html          # punto intermedio de la geometría curva


def test_mapa_ruta_sin_linea(datos_app):
    html = mapa_ruta(datos_app, ruta_entre(datos_app, "C01", "C01"))
    assert "leaflet" in html and "L.polyline" not in html


def test_mapa_envolvente(datos_app):
    html = mapa_envolvente(datos_app)
    assert "L.polygon" in html
    for valor in ("-75.71", "-75.65", "4.49", "4.53"):
        assert valor in html
    for id_lugar in datos_app.nodo_de:
        assert f"{id_lugar} ·" in html


def test_mapa_itinerario(datos_app):
    it = itinerario(datos_app, "C01", ATRACTIVOS)
    html = mapa_itinerario(datos_app, it)
    # Folium escribe los nombres de las capas como JSON: la tilde sale como \u00e1
    assert '"Held-Karp"' in html and '"Vecino m\\u00e1s cercano"' in html
    assert "L.control.layers" in html
    assert COLORES["held_karp"] in html and COLORES["voraz"] in html
    for numero in range(1, 7):
        assert f"\\u003e{numero}\\u003c/div" in html      # el HTML del DivIcon sale escapado

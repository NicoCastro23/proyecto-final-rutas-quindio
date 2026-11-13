"""Mapas con Folium: cada función devuelve el HTML del mapa como texto.

La plantilla lo mete en un <iframe srcdoc>. El JavaScript del mapa lo genera Folium (Leaflet);
el grupo no escribe JavaScript.
"""
import folium

COLORES = {"ruta": "#1F5F8B", "held_karp": "#1F5F8B", "voraz": "#B8322A", "envolvente": "#5E8C61"}


def centro(datos):
    """(lat, lon) promedio de los lugares del catálogo."""
    return datos.catalogo["latitud"].mean(), datos.catalogo["longitud"].mean()


def _mapa_base(datos, zoom=10):
    return folium.Map(location=centro(datos), zoom_start=zoom)


def _como_html(mapa):
    # get_root().render() da un documento completo; _repr_html_ está pensado para Jupyter
    return mapa.get_root().render()


def _ubicacion(datos, id_lugar):
    """(lat, lon) de un lugar según el catálogo."""
    fila = datos.catalogo[datos.catalogo["id"] == id_lugar].iloc[0]
    return float(fila["latitud"]), float(fila["longitud"])


def mapa_ruta(datos, ruta):
    """Línea de la ruta (si tiene al menos 2 puntos) y marcadores de origen y destino."""
    mapa = _mapa_base(datos)
    for id_lugar in (ruta["origen"], ruta["destino"]):
        folium.Marker(_ubicacion(datos, id_lugar),
                      tooltip=f"{id_lugar} · {datos.nombre_de[id_lugar]}").add_to(mapa)
    coordenadas = ruta["coordenadas"]
    if len(coordenadas) >= 2:
        folium.PolyLine(coordenadas, color=COLORES["ruta"], weight=5).add_to(mapa)
        mapa.fit_bounds(coordenadas)
    return _como_html(mapa)


def mapa_envolvente(datos):
    """Polígono de la envolvente (el GeoJSON trae [lon, lat]) y un punto por cada lugar."""
    mapa = _mapa_base(datos, zoom=9)
    anillo = datos.envolvente["features"][0]["geometry"]["coordinates"][0]
    folium.Polygon([(lat, lon) for lon, lat in anillo], color=COLORES["envolvente"],
                   fill=True, fill_opacity=0.15).add_to(mapa)
    for id_lugar in datos.nodo_de:
        folium.CircleMarker(_ubicacion(datos, id_lugar), radius=4, color="#444",
                            tooltip=f"{id_lugar} · {datos.nombre_de[id_lugar]}").add_to(mapa)
    return _como_html(mapa)


def _numero_en_mapa(numero):
    """Icono con el número de orden de visita."""
    estilo = ("background:#fff;border:2px solid #333;border-radius:50%;width:22px;height:22px;"
              "text-align:center;line-height:18px;font-weight:bold;")
    return folium.DivIcon(html=f'<div style="{estilo}">{numero}</div>', icon_size=(22, 22))


def mapa_itinerario(datos, it):
    """Una capa por método (alternables con el control de capas) y marcadores numerados
    según el orden de Held-Karp."""
    mapa = _mapa_base(datos)
    capas = (("held_karp", "Held-Karp"), ("voraz", "Vecino más cercano"))
    for clave, nombre in capas:
        grupo = folium.FeatureGroup(name=nombre)
        for tramo in it[clave]["tramos"]:
            if len(tramo["coordenadas"]) >= 2:
                folium.PolyLine(tramo["coordenadas"], color=COLORES[clave], weight=4).add_to(grupo)
        grupo.add_to(mapa)

    partida = it["partida"]
    folium.Marker(_ubicacion(datos, partida), tooltip=f"Partida: {partida} · {datos.nombre_de[partida]}",
                  icon=folium.Icon(color="green")).add_to(mapa)
    visitas = it["held_karp"]["recorrido"][1:-1]
    for orden, id_lugar in enumerate(visitas, start=1):
        folium.Marker(_ubicacion(datos, id_lugar), icon=_numero_en_mapa(orden),
                      tooltip=f"{orden}. {id_lugar} · {datos.nombre_de[id_lugar]}").add_to(mapa)
    folium.LayerControl(collapsed=False).add_to(mapa)
    return _como_html(mapa)

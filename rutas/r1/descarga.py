"""Descarga de las redes viales crudas con OSMnx (sección 4 del enunciado).

Decisiones del grupo, comunes a las 5 descargas:
  - network_type="drive"  (en graph_from_point el defecto sería "all")
  - retain_all=True       (la red "descargada" es la cruda, sin quitar componentes)
  - dist_type="bbox"      (el "radio" r es un cuadrado de lado 2r)
Toda llamada de red pasa por con_reintentos, que espera y reintenta si el servidor
responde 502 o 504.
"""
import logging
import re
import time

import osmnx as ox

from rutas.r1.catalogo import cargar_catalogo

LOG = logging.getLogger("rutas.r1.descarga")

LUGAR = "Quindío, Colombia"
PARAMETROS = {"network_type": "drive", "retain_all": True}
ERRORES_REINTENTABLES = (502, 504)      # servidor saturado: vale la pena esperar
AREA_DEPARTAMENTO_KM2 = (1500, 2200)    # el Quindío tiene ~1 845 km²; un municipio es mucho menor


def codigo_http(error):
    """Código HTTP de un error, o None si no se puede saber.

    Primero e.response.status_code (errores de requests); si no existe, el número que sigue
    a "responded:" en el mensaje de osmnx._errors.ResponseStatusCodeError.
    """
    respuesta = getattr(error, "response", None)
    codigo = getattr(respuesta, "status_code", None)
    if codigo is not None:
        return int(codigo)
    encontrado = re.search(r"responded:\s*(\d{3})", str(error))
    return int(encontrado.group(1)) if encontrado else None


def con_reintentos(funcion, esperas=(30, 60, 120, 240), dormir=time.sleep):
    """Llama funcion(); si falla con 502/504 espera y reintenta.

    Las esperas se duplican (30, 60, 120, 240 s): son 4 reintentos, 5 intentos en total.
    Cualquier otro error se relanza de inmediato. `dormir` se recibe como parámetro para
    que las pruebas no esperen de verdad.
    """
    for numero_intento in range(1, len(esperas) + 2):
        try:
            return funcion()
        except Exception as error:
            if codigo_http(error) not in ERRORES_REINTENTABLES:
                raise
            if numero_intento > len(esperas):      # ya se gastaron todos los reintentos
                mensaje = (f"La descarga falló tras {numero_intento} intentos "
                           f"(último error: {error}). Use el Plan B: el GraphML del docente "
                           f"(--graphml ruta).")
                raise type(error)(mensaje) from error
            espera = esperas[numero_intento - 1]
            LOG.warning("Error %s del servidor; espera %s s y reintenta (intento %s de %s)",
                        codigo_http(error), espera, numero_intento + 1, len(esperas) + 1)
            dormir(espera)


def centro_plaza_bolivar():
    """(latitud, longitud) de C01, la plaza de Bolívar de Armenia, tomada del catálogo."""
    catalogo = cargar_catalogo()
    c01 = catalogo[catalogo["id"] == "C01"].iloc[0]
    return float(c01["latitud"]), float(c01["longitud"])


def geocodificar_departamento(dormir=time.sleep):
    """Polígono de "Quindío, Colombia" según Nominatim (con reintentos)."""
    return con_reintentos(lambda: ox.geocode_to_gdf(LUGAR), dormir=dormir)


def comprobar_poligono_departamento(gdf):
    """Verifica que el polígono geocodificado sea el departamento y no un municipio.

    Debe tener addresstype "state" y un área entre 1 500 y 2 200 km². Devuelve un dict
    para descarga.json; si algo no cuadra lanza ValueError.
    """
    # El área se calcula en UTM 18N (metros); en grados no tendría sentido.
    proyectado = gdf.set_crs(4326) if gdf.crs is None else gdf
    area_km2 = float(proyectado.to_crs(32618).area.iloc[0]) / 1e6
    addresstype = gdf["addresstype"].iloc[0] if "addresstype" in gdf.columns else None

    if addresstype is not None and addresstype != "state":
        raise ValueError(f"'{LUGAR}' se geocodificó como addresstype='{addresstype}', "
                         f"se esperaba 'state' (departamento)")
    minimo, maximo = AREA_DEPARTAMENTO_KM2
    if not minimo <= area_km2 <= maximo:
        raise ValueError(f"el polígono de '{LUGAR}' mide {area_km2:.0f} km², "
                         f"fuera de {minimo}-{maximo} km²: no parece el departamento")
    nombre = gdf["display_name"].iloc[0] if "display_name" in gdf.columns else None
    return {"addresstype": addresstype, "area_km2": area_km2, "nombre": nombre}


def descargar_departamento(dormir=time.sleep):
    """Red cruda de todo el departamento."""
    return con_reintentos(lambda: ox.graph_from_place(LUGAR, **PARAMETROS), dormir=dormir)


def descargar_radio(radio_m, dormir=time.sleep):
    """Red cruda del cuadrado de lado 2*radio_m centrado en la plaza de Bolívar."""
    centro = centro_plaza_bolivar()
    return con_reintentos(
        lambda: ox.graph_from_point(centro, dist=radio_m, dist_type="bbox", **PARAMETROS),
        dormir=dormir)


def cargar_red_cruda(ruta):
    """Lee un GraphML (descargado antes o entregado por el docente: Plan B)."""
    return ox.load_graphml(ruta)

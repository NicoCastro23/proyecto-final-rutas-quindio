"""Aplicación web de R5: lee parámetros, llama a servicios y mapas, y elige plantilla y código HTTP."""
import argparse
import socket
import sys
import time

from flask import Flask, abort, render_template, request, send_from_directory

from rutas.config import CATALOGO, DATA_PROCESSED, HOST_R5, PUERTO_R5, RESULTS
from rutas.r5.datos import DatosFaltantes, cargar_datos
from rutas.r5.formato import numero
from rutas.r5.mapas import mapa_envolvente, mapa_itinerario, mapa_ruta
from rutas.r5.servicios import (ARCHIVOS_RESULTADOS, ErrorEntrada, itinerario, resultados,
                                ruta_entre)


def crear_app(datos, results=RESULTS):
    """Fábrica: las pruebas le pasan datos sintéticos; main le pasa los reales.

    Los datos se cargan una sola vez fuera de aquí; ninguna petición los vuelve a leer.
    """
    app = Flask(__name__)
    app.jinja_env.filters["num"] = numero          # {{ x|num(1) }} -> coma decimal
    lugares = [(id_lugar, nombre) for id_lugar, nombre in datos.nombre_de.items()]

    @app.get("/")
    def inicio():
        return render_template("inicio.html")

    @app.get("/ruta")
    def ruta():
        origen, destino = request.args.get("origen", ""), request.args.get("destino", "")
        contexto = {"lugares": lugares, "origen": origen, "destino": destino,
                    "ruta": None, "mapa": None, "error": None}
        if not (origen and destino):               # sin los dos parámetros: solo el formulario
            return render_template("ruta.html", **contexto)
        try:
            contexto["ruta"] = ruta_entre(datos, origen, destino)
        except ErrorEntrada as error:
            contexto["error"] = str(error)
            return render_template("ruta.html", **contexto), 400
        contexto["mapa"] = mapa_ruta(datos, contexto["ruta"])
        return render_template("ruta.html", **contexto)

    @app.get("/envolvente")
    def envolvente():
        feature = datos.envolvente["features"][0]
        anillo = feature["geometry"]["coordinates"][0][:-1]     # el último punto repite el primero
        vertices = [(lat, lon) for lon, lat in anillo]
        return render_template("envolvente.html", mapa=mapa_envolvente(datos), vertices=vertices,
                               n_vertices=feature["properties"]["vertices"],
                               area_km2=feature["properties"]["area_km2"])

    @app.get("/itinerario")
    def vista_itinerario():
        partida = request.args.get("partida", "")
        elegidos = request.args.getlist("atractivos")
        contexto = {"lugares": lugares, "atractivos": datos.atractivos, "nombre_de": datos.nombre_de,
                    "visita_min": datos.visita_min, "elegidos": elegidos,
                    "partida": partida or ("C01" if "C01" in datos.nombre_de else lugares[0][0]),
                    "it": None, "mapa": None, "error": None}
        if not partida:                            # sin partida: solo el formulario
            return render_template("itinerario.html", **contexto)
        try:
            contexto["it"] = itinerario(datos, partida, elegidos)
        except ErrorEntrada as error:
            contexto["error"] = str(error)
            return render_template("itinerario.html", **contexto), 400
        contexto["mapa"] = mapa_itinerario(datos, contexto["it"])
        return render_template("itinerario.html", **contexto)

    @app.get("/resultados/<r>")
    def vista_resultados(r):
        if r not in ARCHIVOS_RESULTADOS:
            abort(404)
        return render_template("resultados.html", r=r, **resultados(r, results))

    @app.get("/resultados/<r>/archivo/<nombre>")
    def imagen(r, nombre):
        # lista blanca: solo las imágenes de la lista fija, nunca una ruta arbitraria
        permitidas = [archivo for archivo, _ in ARCHIVOS_RESULTADOS.get(r, {}).get("imagenes", [])]
        if nombre not in permitidas:
            abort(404)
        return send_from_directory(results / r, nombre, mimetype="image/png")

    return app


def puerto_libre(host, puerto):
    """True si se puede abrir el puerto (lo intenta y lo cierra)."""
    with socket.socket() as prueba:
        try:
            prueba.bind((host, puerto))
        except OSError:
            return False
    return True


def main(argv=None, processed=DATA_PROCESSED, catalogo=CATALOGO):
    """Carga los datos una vez y arranca el servidor. Devuelve el código de salida (0 o 1)."""
    analizador = argparse.ArgumentParser(description="Rutas del Paisaje Cultural Cafetero")
    analizador.add_argument("--puerto", type=int, default=PUERTO_R5)
    analizador.add_argument("--host", default=HOST_R5)
    args = analizador.parse_args(argv)

    inicio = time.perf_counter()
    try:
        datos = cargar_datos(processed, catalogo)
    except DatosFaltantes as error:
        print(error, file=sys.stderr)
        return 1
    segundos = time.perf_counter() - inicio
    print(f"Datos cargados en {numero(segundos, 1)} s ({numero(len(datos.red.ids), 0)} nodos)")

    if not puerto_libre(args.host, args.puerto):
        print(f"el puerto {args.puerto} está ocupado; prueba con --puerto {args.puerto + 1}",
              file=sys.stderr)
        return 1
    print(f"Abre http://{args.host}:{args.puerto}")
    crear_app(datos).run(host=args.host, port=args.puerto, debug=False)
    return 0


if __name__ == "__main__":
    sys.exit(main())

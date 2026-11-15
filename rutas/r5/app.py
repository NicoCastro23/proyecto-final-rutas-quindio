"""Aplicación web de R5: lee parámetros, llama a servicios y mapas, y elige plantilla y código HTTP."""
import argparse
import re
import socket
import sys
import time

from flask import Flask, abort, render_template, request, send_from_directory
from markupsafe import Markup, escape

from rutas.config import CATALOGO, DATA_PROCESSED, HOST_R5, PUERTO_R5, RESULTS
from rutas.r5.datos import DatosFaltantes, cargar_datos
from rutas.r5.formato import numero
from rutas.r5.mapas import COLORES, mapa_envolvente, mapa_itinerario, mapa_ruta
from rutas.r5.servicios import (ARCHIVOS_RESULTADOS, ErrorEntrada, itinerario, resultados,
                                ruta_entre)


MIN_ATRACTIVOS, MAX_ATRACTIVOS = 6, 8   # los mismos límites que valida servicios.validar_itinerario


def contador_elegidos(n):
    """Texto del contador de atractivos (M3). app.js arma el mismo texto al marcar y desmarcar.

    0 -> «0 elegidos», «faltan 6»; 1 -> «1 elegido», «faltan 5»; 5 -> «falta 1»;
    6 a 8 -> «listo para calcular»; 9 -> «sobra 1»; 10 -> «sobran 2».
    """
    cuenta = f"{n} elegido" if n == 1 else f"{n} elegidos"
    if n < MIN_ATRACTIVOS:
        faltan = MIN_ATRACTIVOS - n
        estado = f"falta {faltan}" if faltan == 1 else f"faltan {faltan}"
    elif n > MAX_ATRACTIVOS:
        sobran = n - MAX_ATRACTIVOS
        estado = f"sobra {sobran}" if sobran == 1 else f"sobran {sobran}"
    else:
        estado = "listo para calcular"
    return {"cuenta": cuenta, "estado": estado, "en_rango": MIN_ATRACTIVOS <= n <= MAX_ATRACTIVOS}


# Título legible y descripción de cada archivo de resultados (la descripción sirve de alt y de caption).
TITULOS_RESULTADOS = {
    # R1 · red vial
    "r1_tiempos_componente.png": (
        "Tiempo de la componente fuertemente conexa frente a V + E",
        "Gráfica de la mediana de 5 repeticiones, en ms, del cálculo de la componente fuertemente conexa en redes de 2, 5, 10 y 20 km de radio y en el departamento completo."),
    "r1_tamanos.csv": (
        "Tamaño de la red vial",
        "Nodos y aristas de la red descargada y de su componente fuertemente conexa, que es la red que usan R2 a R5."),
    "r1_tiempos_componente.csv": (
        "Tiempo de la componente fuertemente conexa por red",
        "Cinco redes de tamaño creciente: V, E, V + E, mediana en ms, microsegundos por elemento y repeticiones."),
    "r1_memoria.csv": (
        "Memoria: matriz frente a listas de adyacencia",
        "Bytes estimados de cada representación para la red descargada y para la componente, con el supuesto de cada cálculo."),
    "r1_velocidades.csv": (
        "Velocidades por tipo de vía",
        "Velocidad asignada a cada tipo de vía (highway) y porcentaje de tramos con velocidad de OpenStreetMap o imputada."),
    # R2 · Dijkstra
    "r2_tiempo_vs_explorados.png": (
        "Tiempo de Dijkstra frente a nodos explorados",
        "Gráfica de la versión lineal y la versión con cola de prioridad: cada punto es un par origen-destino, con la mediana de sus repeticiones en ms."),
    "r2_dijkstra.csv": (
        "Mediciones de Dijkstra por par",
        "10 pares cercanos y 10 lejanos: tiempo de viaje, nodos explorados y mediana en ms; la versión lineal se mide solo en los cercanos."),
    "r2_cociente.csv": (
        "Cociente lineal / cola de prioridad (10 pares cercanos)",
        "Mediana, mínimo y máximo de cuántas veces más tarda la versión lineal que la de cola de prioridad."),
    "r2_pares.csv": (
        "Pares origen-destino medidos",
        "Los 20 pares de lugares (10 cercanos y 10 lejanos), con su municipio y su nodo en la red."),
    # R3 · envolvente convexa
    "r3_envolvente.png": (
        "Envolvente convexa de los nodos de la red",
        "Gráfica de los nodos de la componente en coordenadas UTM (m) y del polígono que calcula QuickHull."),
    "r3_envolvente.csv": (
        "QuickHull propio frente a SciPy",
        "Nodos de la red y cuadrados de 1 000, 10 000 y 50 000 puntos: vértices, mediana en ms de cada implementación y cociente propio / SciPy."),
    # R4 · ruta óptima
    "r4_tiempo_vs_k.png": (
        "Tiempo de fuerza bruta y Held-Karp frente a k",
        "Gráfica de la mediana en ms para k = 5 a 12 lugares, con el eje y en escala logarítmica."),
    "r4_exactas.csv": (
        "Fuerza bruta y Held-Karp por número de lugares",
        "Para k = 5 a 12: mediana en ms de cada método, estado (completada o no en 5 min), tiempo del recorrido óptimo y el recorrido."),
    "r4_calidad.csv": (
        "Brecha del vecino más cercano frente al óptimo",
        "10 instancias por cada k (5, 8, 10 y 12): brecha promedio y máxima, en %, frente a Held-Karp."),
    "r4_memoria.csv": (
        "Memoria de la tabla de Held-Karp",
        "Para k = 5 a 12: celdas y bytes estimados de la tabla frente al pico medido con tracemalloc."),
    "r4_itinerario.csv": (
        "Itinerario del día desde Armenia",
        "Recorrido que queda después de quitar atractivos hasta caber en 11 h: desplazamiento y visita de cada parada y horas acumuladas."),
}

# (ancho, alto) en px de cada imagen, para reservar espacio antes de que cargue (el CSS la escala).
TAMANOS_IMAGENES = {
    "r1_tiempos_componente.png": (1050, 675),
    "r2_tiempo_vs_explorados.png": (1050, 675),
    "r3_envolvente.png": (914, 1126),
    "r4_tiempo_vs_k.png": (1200, 750),      # aproximado: la imagen aún no existe; corregir cuando exista
}


def tabla_con_titulo(html, descripcion, archivo):
    """Agrega un <caption> justo después de <table ...> y scope="col" a cada <th> de la tabla de pandas.

    Con index=False todos los <th> son encabezados de columna. No cambia ninguna celda.
    """
    caption = f"<caption>{escape(descripcion)} <code>{escape(archivo)}</code></caption>"
    html = re.sub(r"(<table[^>]*>)", lambda m: m.group(1) + caption, html, count=1)
    return Markup(html.replace("<th>", '<th scope="col">'))


def presentar_resultados(crudo):
    """Agrega título y descripción a lo que devuelve servicios.resultados (KeyError si falta un título)."""
    imagenes = []
    for archivo in crudo["imagenes"]:
        titulo, descripcion = TITULOS_RESULTADOS[archivo]
        ancho, alto = TAMANOS_IMAGENES[archivo]
        imagenes.append({"archivo": archivo, "titulo": titulo, "descripcion": descripcion,
                         "ancho": ancho, "alto": alto})
    tablas = []
    for archivo, html in crudo["tablas"]:
        titulo, descripcion = TITULOS_RESULTADOS[archivo]
        tablas.append({"archivo": archivo, "titulo": titulo, "descripcion": descripcion,
                       "html": tabla_con_titulo(html, descripcion, archivo)})
    faltantes = [{"archivo": archivo, "titulo": TITULOS_RESULTADOS[archivo][0], "comando": comando}
                 for archivo, comando in crudo["faltantes"]]
    return {"imagenes": imagenes, "tablas": tablas, "faltantes": faltantes}


def crear_app(datos, results=RESULTS):
    """Fábrica: las pruebas le pasan datos sintéticos; main le pasa los reales.

    Los datos se cargan una sola vez fuera de aquí; ninguna petición los vuelve a leer.
    """
    app = Flask(__name__)
    app.jinja_env.filters["num"] = numero          # {{ x|num(1) }} -> coma decimal
    lugares = [(id_lugar, nombre) for id_lugar, nombre in datos.nombre_de.items()]

    @app.get("/")
    def inicio():
        return render_template("inicio.html", seccion="inicio")

    @app.get("/ruta")
    def ruta():
        origen, destino = request.args.get("origen", ""), request.args.get("destino", "")
        contexto = {"lugares": lugares, "nombre_de": datos.nombre_de, "origen": origen, "destino": destino,
                    "ruta": None, "mapa": None, "error": None, "seccion": "ruta"}
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
        return render_template("envolvente.html", seccion="envolvente", mapa=mapa_envolvente(datos), vertices=vertices,
                               n_vertices=feature["properties"]["vertices"],
                               area_km2=feature["properties"]["area_km2"])

    @app.get("/itinerario")
    def vista_itinerario():
        partida = request.args.get("partida", "")
        elegidos = request.args.getlist("atractivos")
        contexto = {"lugares": lugares, "atractivos": datos.atractivos, "nombre_de": datos.nombre_de,
                    "visita_min": datos.visita_min, "elegidos": elegidos,
                    "partida": partida or ("C01" if "C01" in datos.nombre_de else lugares[0][0]),
                    "it": None, "mapa": None, "error": None, "seccion": "itinerario", "colores": COLORES}
        # Se cuentan las casillas que quedan marcadas (sin repetidos ni ids que no son atractivos):
        # es lo mismo que contaría app.js sobre esta página.
        n_marcadas = sum(1 for id_atractivo in datos.atractivos if id_atractivo in elegidos)
        contexto["contador"] = contador_elegidos(n_marcadas)
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
        return render_template("resultados.html", r=r, seccion="resultados", requerimientos=list(ARCHIVOS_RESULTADOS),
                               **presentar_resultados(resultados(r, results)))

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

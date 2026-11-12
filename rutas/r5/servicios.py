"""Lógica de la aplicación: funciones puras sobre DatosApp que devuelven dicts (sin Flask ni HTML)."""


class ErrorEntrada(ValueError):
    """Entrada inválida del usuario; la app la convierte en HTTP 400 con el mensaje."""


def validar_lugar(datos, id_lugar):
    raise NotImplementedError


def coordenadas_de(G, ids_nodos):
    raise NotImplementedError


def ruta_entre(datos, id_origen, id_destino):
    raise NotImplementedError


def validar_itinerario(datos, id_partida, ids_atractivos):
    raise NotImplementedError


def itinerario(datos, id_partida, ids_atractivos):
    raise NotImplementedError


def resultados(requerimiento, results=None):
    raise NotImplementedError

"""Carga y validación del catálogo de lugares (sección 4 del enunciado)."""
import re

import pandas as pd

from rutas.config import CATALOGO

CATEGORIAS = {
    "Cabecera municipal": 12,
    "Atractivo turístico": 15,
    "Finca u hotel rural": 9,
    "Centro de acopio o trilladora": 6,
}
MINIMOS = {
    "Cabecera municipal": 12,
    "Atractivo turístico": 15,
    "Finca u hotel rural": 8,
    "Centro de acopio o trilladora": 5,
}
RECUADRO = {"lat": (4.0, 4.9), "lon": (-76.0, -75.4)}
COLUMNAS = ["id", "nombre", "municipio", "categoria", "latitud", "longitud",
            "duracion_visita_min", "fuente_duracion", "mapa", "verificado", "notas"]
TOTAL_LUGARES = 42


class CatalogoInvalido(ValueError):
    """El catálogo viola alguna regla de la spec."""


def _error(fila, id_lugar, regla):
    """Mensaje con la fila (línea del CSV) y la regla violada."""
    donde = f"fila {fila}" if fila is not None else "fila —"
    if id_lugar is not None:
        donde += f" (id {id_lugar})"
    return CatalogoInvalido(f"{donde}: {regla}")


def _linea_csv(indice):
    # El encabezado es la línea 1, así que el índice 0 del DataFrame es la línea 2
    return int(indice) + 2


def _es_verdadero(valor):
    return valor is True or str(valor).strip().upper() == "TRUE"


def validar_catalogo(df):
    """Lanza CatalogoInvalido con la fila y la regla si algo no se cumple."""
    faltantes = [c for c in COLUMNAS if c not in df.columns]
    if faltantes:
        raise _error(None, None, f"faltan columnas {faltantes}")
    if len(df) != TOTAL_LUGARES:
        raise _error(None, None, f"se esperaban {TOTAL_LUGARES} lugares y hay {len(df)}")

    repetidos = df[df["id"].duplicated(keep="first")]
    if not repetidos.empty:
        i = repetidos.index[0]
        raise _error(_linea_csv(i), df.loc[i, "id"], "id repetido")

    for i, fila in df.iterrows():
        if fila["categoria"] not in CATEGORIAS:
            raise _error(_linea_csv(i), fila["id"], f"categoría inválida '{fila['categoria']}'")

    conteos = df["categoria"].value_counts().to_dict()
    for categoria, esperado in CATEGORIAS.items():
        if conteos.get(categoria, 0) < MINIMOS[categoria]:
            raise _error(None, None, f"'{categoria}' no alcanza el mínimo {MINIMOS[categoria]}")
        if conteos.get(categoria, 0) != esperado:
            raise _error(None, None, f"'{categoria}' debe tener {esperado} lugares "
                                     f"y tiene {conteos.get(categoria, 0)}")

    for i, fila in df.iterrows():
        linea, id_lugar = _linea_csv(i), fila["id"]
        if fila["categoria"] == "Atractivo turístico":
            duracion = fila["duracion_visita_min"]
            if pd.isna(duracion) or duracion <= 0:
                raise _error(linea, id_lugar, "atractivo sin duracion_visita_min > 0")
            fuente = fila["fuente_duracion"]
            if not isinstance(fuente, str) or not re.match(r"Criterio [1-4]", fuente):
                raise _error(linea, id_lugar, "atractivo sin fuente_duracion con criterio 1 a 4")
        if not _es_verdadero(fila["verificado"]):
            raise _error(linea, id_lugar, "lugar no verificado (verificado debe ser TRUE)")
        lat_min, lat_max = RECUADRO["lat"]
        lon_min, lon_max = RECUADRO["lon"]
        if not lat_min <= fila["latitud"] <= lat_max:
            raise _error(linea, id_lugar, f"latitud {fila['latitud']} fuera del recuadro {lat_min} a {lat_max}")
        if not lon_min <= fila["longitud"] <= lon_max:
            raise _error(linea, id_lugar, f"longitud {fila['longitud']} fuera del recuadro {lon_min} a {lon_max}")


def cargar_catalogo(ruta=CATALOGO):
    """Lee el CSV y lo valida; devuelve el DataFrame."""
    df = pd.read_csv(ruta)
    validar_catalogo(df)
    return df

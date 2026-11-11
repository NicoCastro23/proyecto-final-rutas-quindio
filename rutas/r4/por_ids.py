"""Traducción entre ids de lugar e índices de la matriz (fuera del cronómetro)."""
from rutas.r4.fuerza_bruta import fuerza_bruta
from rutas.r4.held_karp import held_karp
from rutas.r4.vecino import vecino_mas_cercano

METODOS = {"fuerza_bruta": fuerza_bruta, "held_karp": held_karp,
           "vecino_mas_cercano": vecino_mas_cercano}


def matriz_a_listas(matriz_df):
    """(T, ids): T como lista de listas de float de Python (no numpy.float64) e ids en el
    orden del índice. La matriz debe ser cuadrada con las mismas etiquetas en filas y columnas."""
    ids = list(matriz_df.index)
    if list(matriz_df.columns) != ids:
        raise ValueError("las columnas de la matriz no coinciden con el índice")
    return matriz_df.to_numpy(dtype=float).tolist(), ids


def resolver_por_ids(matriz_df, id_partida, ids_lugares, metodo):
    """Corre `metodo` con ids y devuelve (tiempo en segundos, recorrido en ids)."""
    if metodo not in METODOS:
        raise ValueError(f"método desconocido: {metodo!r}")
    T, ids = matriz_a_listas(matriz_df)
    indice = {id_lugar: i for i, id_lugar in enumerate(ids)}
    for id_lugar in [id_partida, *ids_lugares]:
        if id_lugar not in indice:
            raise ValueError(f"el id {id_lugar!r} no está en la matriz")
    s = indice[id_partida]
    lugares = [indice[i] for i in ids_lugares]
    costo, recorrido = METODOS[metodo](T, s, lugares)
    return costo, [ids[i] for i in recorrido]

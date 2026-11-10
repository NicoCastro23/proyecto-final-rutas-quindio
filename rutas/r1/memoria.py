"""Estimación de memoria de las dos representaciones del grafo (punto 1 de R1).

Supuestos del grupo: cada conexión guarda dos pesos float64 (distancia y tiempo,
8 B cada uno) y un destino de 8 B; cada nodo guarda una referencia de 8 B a su lista.
Es un arreglo compacto: con objetos de Python el consumo real es mayor.
"""

SUPUESTOS = {
    "Matriz de adyacencia": "V x V celdas, cada una con 2 float64 (distancia y tiempo) = 16 B",
    "Listas de adyacencia": "por arista: 2 pesos float64 + 1 destino = 24 B; por nodo: 8 B de referencia",
}


def estimar_memoria(V, E):
    """Bytes (enteros exactos) y MB (1 MB = 10^6 B) de matriz y listas."""
    matriz_bytes = 16 * V * V          # cada celda guarda dos float64
    listas_bytes = 24 * E + 8 * V      # 24 B por arista + 8 B por nodo
    return {
        "matriz_bytes": matriz_bytes,
        "listas_bytes": listas_bytes,
        "matriz_mb": matriz_bytes / 1e6,
        "listas_mb": listas_bytes / 1e6,
    }


def filas_memoria(red, V, E):
    """Dos filas para r1_memoria.csv: matriz y listas de una misma red."""
    estimacion = estimar_memoria(V, E)
    filas = []
    for representacion, clave in (("Matriz de adyacencia", "matriz"),
                                  ("Listas de adyacencia", "listas")):
        filas.append({
            "red": red,
            "V": V,
            "E": E,
            "representacion": representacion,
            "supuesto": SUPUESTOS[representacion],
            "bytes": estimacion[clave + "_bytes"],
            "MB": estimacion[clave + "_mb"],
        })
    return filas

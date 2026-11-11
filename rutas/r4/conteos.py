"""Memoria estimada de Held-Karp y conteos teóricos de operaciones."""
import math

BYTES_POR_CELDA = 12        # 8 B del costo (float64) + 4 B del predecesor


def memoria_held_karp(k):
    """{"k", "celdas", "bytes_estimados", "mb_estimados"}.

    La tabla tiene 2^k máscaras × k lugares = k·2^k celdas; MB = 10^6 bytes.
    """
    celdas = k * 2 ** k
    bytes_estimados = BYTES_POR_CELDA * celdas
    return {"k": k, "celdas": celdas, "bytes_estimados": bytes_estimados,
            "mb_estimados": bytes_estimados / 1e6}


def conteos_teoricos(k):
    """{"k", "transiciones_hk", "permutaciones_fb", "tramos_fb"}.

    Held-Karp: k (base) + k(k-1)·2^(k-2) (paso: Σ |S|(|S|-1) sobre todos los S) + k (cierre).
    Con k = 1 no hay paso (queda 2) y con k = 0 no hay nada.
    Fuerza bruta: k! permutaciones y (k+1)·k! tramos sumados (salida, k-1 intermedios, regreso).
    """
    if k == 0:
        transiciones = 0
    elif k == 1:
        transiciones = 2
    else:
        transiciones = k + k * (k - 1) * 2 ** (k - 2) + k
    permutaciones = math.factorial(k)
    return {"k": k, "transiciones_hk": transiciones,
            "permutaciones_fb": permutaciones, "tramos_fb": (k + 1) * permutaciones}

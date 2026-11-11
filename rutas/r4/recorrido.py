"""Validación de la entrada y costo de un recorrido (comunes a los tres métodos de R4)."""


def validar_entrada(T, s, lugares):
    """ValueError si s o algún lugar no está en range(len(T)) (negativos incluidos), si hay
    lugares repetidos o si s está en lugares. No lee T: solo mira su tamaño."""
    n = len(T)
    if not 0 <= s < n:
        raise ValueError(f"la partida {s} está fuera de rango (0..{n - 1})")
    vistos = set()
    for lugar in lugares:
        if not 0 <= lugar < n:
            raise ValueError(f"el lugar {lugar} está fuera de rango (0..{n - 1})")
        if lugar == s:
            raise ValueError(f"la partida {s} no puede estar entre los lugares")
        if lugar in vistos:
            raise ValueError(f"el lugar {lugar} está repetido")
        vistos.add(lugar)


def costo_recorrido(T, recorrido):
    """float con la suma de T[a][b] para cada par consecutivo del recorrido.
    [s] da 0.0; si algún arco es inf, el resultado es inf."""
    total = 0.0
    for a, b in zip(recorrido, recorrido[1:]):
        total += T[a][b]
    return float(total)

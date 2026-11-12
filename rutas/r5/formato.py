"""Formato de números para la pantalla: coma decimal y espacio como separador de miles."""


def numero(valor, decimales=1):
    """Texto con coma decimal y espacio de miles: 1631.496 -> "1 631,5", 29.72 -> "29,7", 0 -> "0,0".

    Python escribe 1,631.5 (coma de miles, punto decimal). Primero la coma de miles pasa a espacio
    y después el punto decimal pasa a coma; en ese orden no se confunden.
    """
    texto = f"{float(valor):,.{decimales}f}"
    return texto.replace(",", " ").replace(".", ",")

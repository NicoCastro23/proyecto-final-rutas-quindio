"""Generador propio de permutaciones en orden lexicográfico (algoritmo L de Knuth)."""


def permutaciones_lexicograficas(elementos):
    """Genera todas las permutaciones de `elementos` (distintos) en orden lexicográfico,
    a partir de sorted(elementos), como tuplas. No modifica `elementos`.

    Algoritmo L (Knuth, TAOCP vol. 4A, sección 7.2.1.2): se parte de la permutación
    ordenada y, para pasar a la siguiente, se avanza lo mínimo posible:
      1. i = último índice con a[i] < a[i+1]. Si no existe, a es la última: terminar.
      2. j = último índice con a[j] > a[i]; se intercambian a[i] y a[j].
      3. Se invierte la cola a[i+1:] (estaba en orden decreciente, queda creciente).
    """
    a = sorted(elementos)          # copia: la lista de entrada no se toca
    n = len(a)
    while True:
        yield tuple(a)

        # Paso 1: buscar el pivote i desde la derecha.
        i = n - 2
        while i >= 0 and a[i] >= a[i + 1]:
            i -= 1
        if i < 0:                  # toda la lista está en orden decreciente: ya se generaron todas
            return

        # Paso 2: el sucesor de a[i] en la cola; existe porque a[i] < a[i+1].
        j = n - 1
        while a[j] <= a[i]:
            j -= 1
        a[i], a[j] = a[j], a[i]

        # Paso 3: la cola queda en orden creciente al invertirla.
        a[i + 1:] = a[i + 1:][::-1]

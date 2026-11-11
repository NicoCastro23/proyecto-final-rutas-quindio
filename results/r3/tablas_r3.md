# Tablas de R3

Generadas por `rutas/r3/tablas.py` desde los archivos de `results/r3/`. Todos los tiempos están en milisegundos (ms): mediana de las repeticiones.

## Envolvente convexa: QuickHull propio frente a SciPy

| Conjunto de puntos | n | Vértices de la envolvente | Tiempo propio (ms) | Tiempo SciPy (ms) | Cociente | Repeticiones |
|---|---|---|---|---|---|---|
| Nodos de la red | 8791 | 14 | 4.491 | 0.388 | 11.6 | 5 |
| Cuadrado, 1 000 puntos | 1000 | 16 | 0.558 | 0.064 | 8.7 | 5 |
| Cuadrado, 10 000 puntos | 10000 | 26 | 6.181 | 0.493 | 12.5 | 5 |
| Cuadrado, 50 000 puntos | 50000 | 25 | 27.509 | 2.180 | 12.6 | 5 |

## Vértices frente a (8/3) ln n

| Conjunto de puntos | n | Vértices obtenidos | (8/3) ln n |
|---|---|---|---|
| Cuadrado, 1 000 puntos | 1000 | 16 | 18.4 |
| Cuadrado, 10 000 puntos | 10000 | 26 | 24.6 |
| Cuadrado, 50 000 puntos | 50000 | 25 | 28.9 |

## Puntos y semilla

Semilla: 2026 (`random.Random`). Cuadrado [0, 1000000) x [0, 1000000) m, redondeo `math.floor(x + 0.5)`. cada cuadrado usa su propio Random(2026): los conjuntos no comparten el flujo de azar.

| Conjunto de puntos | n pedido | n obtenido |
|---|---|---|
| Nodos de la red | 8791 | 8791 |
| Cuadrado, 1 000 puntos | 1000 | 1000 |
| Cuadrado, 10 000 puntos | 10000 | 10000 |
| Cuadrado, 50 000 puntos | 50000 | 50000 |

## Envolvente de la red

- Vértices: 14
- Área: 1631.496 km²

## Máquina

- procesador: Apple M5
- ram_gb: 16.0
- so: macOS-26.6.2-arm64-arm-64bit-Mach-O
- python: 3.13.8

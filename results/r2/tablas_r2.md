# Tablas de R2

Generadas por `rutas/r2/tablas.py` desde los CSV/JSON de `results/r2/`.

## Mediciones (mediana de las repeticiones)

| Origen | Destino | Versión | Tiempo de viaje (s) | Nodos explorados | Tiempo (ms) | Tipo | Distancia (m) | Repeticiones |
|---|---|---|---|---|---|---|---|---|
| T05 | T02 | cola_prioridad | 29.06 | 8 | 0.032 | cercano | 467.3 | 5 |
| T05 | T02 | lineal | 29.06 | 8 | 1.440 | cercano | 467.3 | 5 |
| F08 | C07 | cola_prioridad | 1106.71 | 106 | 0.062 | cercano | 12296.8 | 5 |
| F08 | C07 | lineal | 1106.71 | 106 | 18.752 | cercano | 12296.8 | 5 |
| C03 | F04 | cola_prioridad | 448.99 | 1375 | 0.504 | cercano | 5558.2 | 5 |
| C03 | F04 | lineal | 448.99 | 1375 | 255.699 | cercano | 5558.2 | 5 |
| C04 | A14 | cola_prioridad | 94.31 | 261 | 0.113 | cercano | 1235.2 | 5 |
| C04 | A14 | lineal | 94.31 | 261 | 46.385 | cercano | 1235.2 | 5 |
| A09 | C11 | cola_prioridad | 573.19 | 517 | 0.218 | cercano | 6731.6 | 5 |
| A09 | C11 | lineal | 573.19 | 517 | 95.374 | cercano | 6731.6 | 5 |
| A11 | C05 | cola_prioridad | 784.32 | 97 | 0.058 | cercano | 6933.5 | 5 |
| A11 | C05 | lineal | 784.32 | 97 | 17.458 | cercano | 6933.5 | 5 |
| F06 | C08 | cola_prioridad | 483.65 | 276 | 0.111 | cercano | 7560.3 | 5 |
| F06 | C08 | lineal | 483.65 | 276 | 50.361 | cercano | 7560.3 | 5 |
| A03 | F01 | cola_prioridad | 2042.23 | 133 | 0.065 | cercano | 18368.8 | 5 |
| A03 | F01 | lineal | 2042.23 | 133 | 23.561 | cercano | 18368.8 | 5 |
| A15 | F07 | cola_prioridad | 113.68 | 110 | 0.059 | cercano | 947.3 | 5 |
| A15 | F07 | lineal | 113.68 | 110 | 19.674 | cercano | 947.3 | 5 |
| A01 | F02 | cola_prioridad | 586.73 | 495 | 0.189 | cercano | 8582.3 | 5 |
| A01 | F02 | lineal | 586.73 | 495 | 90.450 | cercano | 8582.3 | 5 |
| F06 | T05 | cola_prioridad | 792.15 | 763 | 0.279 | lejano | 12926.1 | 5 |
| C05 | A10 | cola_prioridad | 2190.99 | 3951 | 1.819 | lejano | 28167.3 | 5 |
| C06 | F09 | cola_prioridad | 2776.92 | 6880 | 2.719 | lejano | 44269.5 | 5 |
| F08 | A07 | cola_prioridad | 4520.24 | 7950 | 3.421 | lejano | 62503.9 | 5 |
| A07 | F03 | cola_prioridad | 2911.61 | 7491 | 2.999 | lejano | 38392.0 | 5 |
| C10 | T06 | cola_prioridad | 3956.58 | 7876 | 3.210 | lejano | 50600.9 | 5 |
| C02 | A12 | cola_prioridad | 2419.27 | 5209 | 2.131 | lejano | 31578.3 | 5 |
| A12 | F03 | cola_prioridad | 2455.98 | 7390 | 2.985 | lejano | 30887.6 | 5 |
| F01 | C06 | cola_prioridad | 1863.55 | 5317 | 2.104 | lejano | 21157.8 | 5 |
| A14 | T02 | cola_prioridad | 981.00 | 3316 | 1.279 | lejano | 15102.7 | 5 |

## Cociente de tiempos lineal / cola de prioridad (10 pares cercanos)

| Mediana | Mínimo | Máximo |
|---|---|---|
| 385.70 | 44.66 | 506.96 |

## Pares y semilla

Semilla: 2026 (`random.Random`). 10 pares 'cercano' (mismo municipio, un par por municipio por vuelta, municipios ordenados y barajados) y 10 'lejano' (municipios distintos, al azar); pares ordenados, sin repetir y con nodos distintos.

## Asimetría de la matriz de tiempos

| Pares asimétricos | Par de mayor diferencia | Diferencia máxima (s) | M[i][j] (s) | M[j][i] (s) |
|---|---|---|---|---|
| 845 | F05 y F06 | 383.19 | 2841.85 | 3225.04 |

## Máquina

- procesador: Apple M5
- ram_gb: 16.0
- so: macOS-26.6.2-arm64-arm-64bit-Mach-O
- python: 3.13.8

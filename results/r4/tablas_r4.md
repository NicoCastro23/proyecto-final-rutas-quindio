# Tablas de R4

Generadas por `rutas/r4/tablas.py` desde los archivos de `results/r4/`. Los tiempos están en milisegundos (ms) y los tiempos de recorrido en segundos (s).

## Tiempos de fuerza bruta y Held-Karp

_El archivo `r4_exactas.csv` todavía no existe: corre `.venv/bin/python -m rutas.r4.medir_exactas`._

## Memoria de Held-Karp: estimada frente a medida

Estimada: 12 B por celda (8 B del costo y 4 B del predecesor). El pico de `tracemalloc` es mayor porque en Python cada fila es un objeto `list` y cada costo un objeto `float`.

| k | Celdas (k·2^k) | Estimada (B) | Estimada (MB) | Pico tracemalloc (B) | Pico tracemalloc (MB) |
|---|---|---|---|---|---|
| 5 | 160 | 1920 | 0.002 | 9136 | 0.009 |
| 6 | 384 | 4608 | 0.005 | 19480 | 0.019 |
| 7 | 896 | 10752 | 0.011 | 42024 | 0.042 |
| 8 | 2048 | 24576 | 0.025 | 90824 | 0.091 |
| 9 | 4608 | 55296 | 0.055 | 195352 | 0.195 |
| 10 | 10240 | 122880 | 0.123 | 419672 | 0.420 |
| 11 | 22528 | 270336 | 0.270 | 897184 | 0.897 |
| 12 | 49152 | 589824 | 0.590 | 1901640 | 1.902 |

## Conteos teóricos

| k | Transiciones Held-Karp | Permutaciones fuerza bruta (k!) | Tramos sumados fuerza bruta ((k+1)·k!) |
|---|---|---|---|
| 5 | 170 | 120 | 720 |
| 6 | 492 | 720 | 5040 |
| 7 | 1358 | 5040 | 40320 |
| 8 | 3600 | 40320 | 362880 |
| 9 | 9234 | 362880 | 3628800 |
| 10 | 23060 | 3628800 | 39916800 |
| 11 | 56342 | 39916800 | 479001600 |
| 12 | 135192 | 479001600 | 6227020800 |

## Calidad del vecino más cercano frente a Held-Karp

Brecha = (voraz − óptimo) / óptimo × 100.

| k | Instancias | Brecha promedio (%) | Brecha máxima (%) |
|---|---|---|---|
| 5 | 10 | 6.00 | 12.09 |
| 8 | 10 | 9.73 | 19.76 |
| 10 | 10 | 10.57 | 20.74 |
| 12 | 10 | 11.81 | 28.18 |

## Itinerario de un día

Partida: Plaza de Bolívar de Armenia (C01). Atractivos iniciales: A05, A08, A04, A14, A06, A07, A12, A01. Jornada máxima: 660 min.

| Orden | Lugar | Desplazamiento desde el anterior (min) | Visita (min) | Tiempo acumulado (h) |
|---|---|---|---|---|
| 1 | Jardín Botánico del Quindío | 8.5 | 180.0 | 3.14 |
| 2 | Mirador Alto de la Cruz | 28.0 | 30.0 | 4.11 |
| 3 | Mirador de Filandia (Colina Iluminada) | 27.2 | 30.0 | 5.06 |
| 4 | Cementerio Libre de Circasia | 23.9 | 30.0 | 5.96 |
| 5 | Museo del Oro Quimbaya | 7.4 | 60.0 | 7.08 |
| 6 | Parque de la Vida | 4.2 | 180.0 | 10.15 |
| Regreso | Plaza de Bolívar de Armenia | 4.0 | — | 10.22 |

Atractivos quitados, en orden:

| Id | Atractivo quitado | Jornada antes (min) | Jornada después (min) | Ahorro (min) |
|---|---|---|---|---|
| A01 | Parque Nacional del Café | 1255.2 | 809.6 | 445.6 |
| A12 | Ecoparque Peñas Blancas | 809.6 | 613.1 | 196.5 |

- Visitas: 510.0 min
- Desplazamientos: 103.1 min
- Jornada: 613.1 min (10.22 h)
- Cabe en la jornada: sí

## Semillas y muestra

- Semilla de la muestra anidada: 2026 (`random.Random(semilla).sample(otros, k)`), partida C01.
- Muestra anidada (cada k usa los primeros k): C09, A10, F07, T04, C08, A04, F01, F06, F03, A05, C02, A09.
- Semillas de las instancias de calidad: 2026..2035.

## Máquina

_El archivo `maquina.json` todavía no existe: lo escribe `rutas.r4.medir_exactas`._

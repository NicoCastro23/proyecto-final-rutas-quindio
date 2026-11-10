# Tablas de R1

Generadas por `rutas/r1/tablas.py` desde los CSV de `results/r1/`.

## Tamaño de la red

| Red | Nodos (V) | Aristas (E) |
|---|---|---|
| Red descargada | 8877 | 20245 |
| Componente fuertemente conexa | 8791 | 20132 |

## Tiempo de `largest_component` por red cruda

| Red | V | E | V + E | Tiempo (ms) | Tiempo por elemento (µs) | Repeticiones |
|---|---|---|---|---|---|---|
| Radio de 2 km | 1659 | 3670 | 5329 | 12.32 | 2.311 | 5 |
| Radio de 5 km | 4316 | 9717 | 14033 | 34.05 | 2.426 | 5 |
| Radio de 10 km | 6010 | 13508 | 19518 | 46.12 | 2.363 | 5 |
| Radio de 20 km | 8850 | 20141 | 28991 | 71.47 | 2.465 | 5 |
| Departamento completo | 8877 | 20245 | 29122 | 70.88 | 2.434 | 5 |

## Memoria: matriz vs listas de adyacencia

| Red | V | E | Representación | Supuesto | Tamaño (B) | Tamaño (MB) |
|---|---|---|---|---|---|---|
| Red descargada | 8877 | 20245 | Matriz de adyacencia | V x V celdas, cada una con 2 float64 (distancia y tiempo) = 16 B | 1260818064 | 1260.818 |
| Red descargada | 8877 | 20245 | Listas de adyacencia | por arista: 2 pesos float64 + 1 destino = 24 B; por nodo: 8 B de referencia | 556896 | 0.557 |
| Componente fuertemente conexa | 8791 | 20132 | Matriz de adyacencia | V x V celdas, cada una con 2 float64 (distancia y tiempo) = 16 B | 1236506896 | 1236.507 |
| Componente fuertemente conexa | 8791 | 20132 | Listas de adyacencia | por arista: 2 pesos float64 + 1 destino = 24 B; por nodo: 8 B de referencia | 553496 | 0.553 |

## Velocidades por tipo de vía (componente)

| Tipo de vía | Velocidad de tabla (km/h) | Aristas | Con maxspeed de OSM | OSM (%) | Imputado (%) |
|---|---|---|---|---|---|
| ladder | 20 | 4 | 0 | 0.0 | 100.0 |
| primary | 60 | 563 | 166 | 29.5 | 70.5 |
| primary_link | 60 | 36 | 0 | 0.0 | 100.0 |
| residential | 30 | 13488 | 304 | 2.3 | 97.7 |
| secondary | 50 | 1282 | 157 | 12.2 | 87.8 |
| secondary_link | 50 | 48 | 4 | 8.3 | 91.7 |
| tertiary | 40 | 1843 | 318 | 17.3 | 82.7 |
| tertiary_link | 40 | 5 | 0 | 0.0 | 100.0 |
| trunk | 80 | 414 | 116 | 28.0 | 72.0 |
| trunk_link | 80 | 37 | 1 | 2.7 | 97.3 |
| unclassified | 30 | 2412 | 237 | 9.8 | 90.2 |
| Total |  | 20132 | 1303 | 6.5 | 93.5 |

## Lugares con alerta (a más de 500 m de su nodo)

| Lugar | Nombre | Distancia al nodo (m) |
|---|---|---|
| A03 | Valle de Cocora | 1054.28 |
| A10 | RECUCA, Recorrido de la Cultura Cafetera | 538.58 |
| A11 | Reserva Cascadas del Río Verde | 1473.32 |

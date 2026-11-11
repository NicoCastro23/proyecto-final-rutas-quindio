# Ruta óptima de recorrido (TSP asimétrico) — Requerimiento 4
Enunciado: sección 5, Requerimiento 4 (puntos 1 a 5 y párrafo inicial); protocolo en sección 6; formatos en Anexo, Requerimiento 4 (tabla de soluciones exactas, gráfica, calidad de la heurística, itinerario de un día). Peso: 25 % (40 % implementación verificada, 30 % teoría, 30 % experimental).
Estado: ☑ spec (aprobada en Puerta 1, 2026-11-11) · ☐ pruebas · ☐ código · ☐ verificado
Depende de: `r2-dijkstra` (cerrado): `data/processed/matriz_tiempos.csv` (42 × 42, segundos, sin redondear, orden del catálogo) y `rutas.r2.matriz.cargar_matriz`; `r1-red-vial` (cerrado): `data/catalogo.csv` (`duracion_visita_min` de los 15 atractivos) y `rutas.r1.catalogo`; `rutas.medicion` (`medir_en_hijo`, `info_maquina`).

## Propósito
Dado un lugar de partida `s` y k lugares más, encontrar el recorrido de menor tiempo que sale de `s`, visita los k lugares y regresa a `s`, usando la matriz asimétrica de R2 (TSP asimétrico). Se implementan tres algoritmos propios: **fuerza bruta** y **Held-Karp** (exactos) y la heurística voraz del **vecino más cercano**. Se comparan en tiempo y en calidad y se arma el itinerario de un día. R5 llama a Held-Karp y al voraz en vivo.

## Datos reales (2026-11-11, para dimensionar)
- Matriz 42 × 42; 845 pares asimétricos (`results/r2/r2_asimetria.json`); T03↔T05 = 0 s (mismo nodo). Armenia = `C01` = índice 0.
- Muestra anidada de los experimentos exactos (semilla 2026, `random.Random(2026).sample(otros, 12)` con `otros` = los 41 ids distintos de C01 en orden del catálogo): `C09, A10, F07, T04, C08, A04, F01, F06, F03, A05, C02, A09`. Cada k usa los primeros k.
- Itinerario por defecto (simulado por enumeración con la matriz real; ver caso 16): 8 atractivos → 1 255,2 min; se quita A01 → 809,6 min; se quita A12 → **613,1 min (10,2 h), cabe** con 6 atractivos.

## Entradas y salidas
**Representación (implementación propia, NetworkX/itertools solo en pruebas):**
- `T`: lista de listas de float (segundos), `T[i][j]` = tiempo de i a j; diagonal 0; puede contener `math.inf`. Los índices son las posiciones en la matriz (orden del catálogo).
- `s`: índice de partida. `lugares`: lista de k índices distintos, sin `s`.

**Funciones** (módulo `rutas/r4/`, las tres con la misma firma):
- `fuerza_bruta(T, s, lugares) -> (tiempo_total_s, recorrido)`
- `held_karp(T, s, lugares) -> (tiempo_total_s, recorrido)`
- `vecino_mas_cercano(T, s, lugares) -> (tiempo_total_s, recorrido)`
- `recorrido` = lista de índices `[s, p1, …, pk, s]` (incluye el regreso). `tiempo_total_s` = float, la suma de `T` a lo largo del recorrido.
- `costo_recorrido(T, recorrido) -> float`: función auxiliar (la usan las pruebas y la verificación).
- `permutaciones_lexicograficas(elementos)`: generador propio (siguiente permutación lexicográfica sobre un solo arreglo). Lo usa la fuerza bruta.
- Envoltorio por ids para los scripts y R5 (la traducción queda fuera de la medición): `resolver_por_ids(matriz_df, id_partida, ids_lugares, metodo)` → `(tiempo_total_s, [ids…])`.
- `itinerario_dia(T, ids, s, atractivos, visita_min, jornada_max_min=660)` → filas del itinerario final, lista de atractivos quitados con su justificación (ahorro en min) y totales.
- `memoria_held_karp(k)` → celdas `k·2^k`, bytes estimados (`12·k·2^k`) y MB (10⁶ B).

**Archivos** (bajo `results/r4/`; todos se generan con scripts, y las tablas y gráficas salen de estos CSV/JSON):
- `r4_instancias.json`: semillas, partida, muestra anidada (ids), instancias de calidad (k, semilla, ids).
- `r4_exactas.csv`: `k, metodo (fuerza_bruta|held_karp), tiempo_ms, repeticiones, estado (ok|no_completada|no_ejecutada), tiempo_total_s, recorrido` (recorrido = ids separados por `-`). `tiempo_ms` vacío si no está en `ok`. Columnas ampliadas del anexo (k, tiempo FB, tiempo HK); la tabla del anexo se arma pivoteando este CSV.
- `r4_memoria.csv`: `k, celdas, bytes_estimados, mb_estimados, pico_tracemalloc_bytes, pico_tracemalloc_mb`, para k = 5..12.
- `r4_calidad_detalle.csv`: `k, semilla, optimo_s, heuristica_s, brecha_pct, lugares`.
- `r4_calidad.csv`: `k, instancias, brecha_promedio_pct, brecha_maxima_pct` (formato del anexo), calculado desde el detalle.
- `r4_itinerario.csv`: `orden, id, lugar, desplazamiento_min, visita_min, acumulado_h` (formato del anexo). Última fila: `Regreso`, lugar de partida, desplazamiento, visita `—` y acumulado. `r4_itinerario.json`: partida, atractivos iniciales, atractivos quitados en orden (id, jornada antes, jornada después, ahorro en min), totales (visitas, desplazamientos, jornada, en min y h) y si cabe.
- `r4_tiempo_vs_k.png`: k en x, tiempo (ms) en y, una curva por método. Eje y logarítmico, indicado en la etiqueta. Los k no completados no se dibujan y se anotan en el título o la leyenda.
- `maquina.json` y `tablas_r4.md` (las tablas del anexo, el mayor k resuelto por cada método, la memoria y los conteos teóricos).

## Comportamiento
1. **Fuerza bruta** (punto 1): `s` queda fijo y se recorren las k! permutaciones de `lugares` con el generador propio, en orden lexicográfico de índices a partir de la lista ordenada. Para cada permutación se suma su costo completo en O(k) (sin poda ni sumas incrementales, para que siga siendo fuerza bruta pura). Solo reemplaza al mejor si el costo es **estrictamente menor**, así que en un empate gana la primera permutación en orden lexicográfico. `itertools` no aparece en `rutas/r4/` (solo en las pruebas).
2. **Subestructura óptima** (punto 1, a justificar en el informe antes de Held-Karp): sea P un camino óptimo que sale de `s`, visita exactamente el conjunto S y termina en j, y sea i el lugar justo antes de j. Entonces el tramo de P de `s` a i es un camino óptimo que sale de `s`, visita S∖{j} y termina en i. Si existiera uno más corto, al pegarle el arco i→j se obtendría un camino sobre S que termina en j y es más corto que P (argumento de cortar y pegar). La asimetría no afecta el argumento, porque solo se usan arcos en su sentido.
3. **Held-Karp** (recurrencia), sobre los lugares reindexados 0..k−1 (`L[0..k−1]`), con la máscara de bits `S` ⊆ {0..k−1}:
   - Caso base: `C({j}, j) = T[s][L[j]]`.
   - Paso: `C(S, j) = min_{i ∈ S∖{j}} ( C(S∖{j}, i) + T[L[i]][L[j]] )` para |S| ≥ 2, j ∈ S.
   - Cierre: óptimo = `min_j ( C(L completo, j) + T[L[j]][s] )`.
   - Las tablas son `costo` y `padre`, listas de 2^k listas de k elementos (`costo[mascara][j]`, `padre[mascara][j]`), con `inf`/`None` en las celdas que no se usan. Las máscaras se recorren en orden creciente, lo que garantiza que `S∖{j}` ya está calculada. Para cada j, los i se prueban en orden creciente y solo se reemplaza con `<` estricto, así que en un empate gana el menor i. El cierre también usa `<` estricto, así que gana el menor j.
   - **Devuelve el recorrido:** se reconstruye hacia atrás con `padre` desde el j del cierre hasta la máscara de un solo elemento, se invierte y se traduce a índices de `T`.
4. **Vecino más cercano** (punto 2, elegido por el grupo): parte de `s` y repite: va al lugar no visitado con menor `T[actual][j]` (empate: menor índice de `T`). Al terminar vuelve a `s`. Cuesta O(k²) y solo lee la fila del lugar actual, así que no necesita que la matriz sea simétrica. Justificación para el informe: es la voraz más simple de explicar, se calcula al instante en R5 y su punto débil (decide sin mirar lo que falta ni el regreso) es justo lo que el punto 5 pide discutir. No tiene factor de aproximación constante en el TSP asimétrico general. La cota (1/2)⌈log₂ n⌉ + 1/2 de Rosenkrantz, Stearns y Lewis (1977) vale solo en instancias métricas simétricas.
5. **Experimento de soluciones exactas** (punto 1): `s` = C01. Para k = 5, 6, …, 12, cada método resuelve la instancia anidada de k lugares (ver «Datos reales»). Antes de medir un k se verifica fuera del cronómetro que FB y HK den el mismo `tiempo_total_s` (±1e-6 s) cuando FB es viable (ver punto 10). Si un método marca `no_completada` en un k, los k mayores de **ese** método no se ejecutan y quedan con `estado = no_ejecutada`, y la tabla muestra «no completada» en los dos casos. Se reporta el mayor k resuelto por cada método.
6. **Memoria de Held-Karp** (punto 1): estimación `k · 2^k` celdas × 12 B (8 B de costo float64 + 4 B de predecesor), con MB = 10⁶ B. Además, en una corrida aparte **fuera del cronómetro**, se mide el pico con `tracemalloc` durante `held_karp` para k = 5..12. El informe explica por qué el pico real es mayor (cada float de Python es un objeto, cada lista guarda punteros de 8 B y hay una lista por máscara).
7. **Calidad de la heurística** (punto 3): k ∈ {5, 8, 10, 12}; **10 instancias por k**, con semillas 2026..2035: `random.Random(semilla).sample(otros, k)`, `s` = C01. `brecha_pct = (heurística − óptimo_HK) / óptimo_HK × 100`. Se reportan el promedio y el máximo por k. La calidad no es una medición de tiempo, así que no se cronometra.
8. **Itinerario de un día** (punto 4): partida por defecto C01 y, para el documento técnico, los 8 atractivos `A05, A08, A04, A14, A06, A07, A12, A01` (decisión del grupo; R5 deja elegir otros, entre 6 y 8, y otra partida). El orden se calcula con Held-Karp. Jornada (min) = Σ visitas + Σ desplazamientos, incluido el regreso (desplazamientos = `tiempo_total_s / 60`). **Cabe si la jornada es ≤ 660 min.** Si no cabe, se quita el atractivo que más reduce la jornada: para cada atractivo se recalcula Held-Karp sin él y se quita el que deje la jornada más corta (empate: menor índice). Se repite hasta que quepa o quede un solo atractivo. Cada salida se justifica con su ahorro en minutos (visita + desvío) y se reporta la duración final. En la tabla, `acumulado_h` de cada fila es la suma de los desplazamientos y las visitas hasta salir de ese lugar, y la fila «Regreso» tiene la jornada total.
9. **Voraz frente a óptimo** (punto 5): el informe usa los casos 4 y 4b como ejemplos. Explica que Dijkstra también es voraz pero su elección es segura: con pesos ≥ 0, el nodo de menor distancia tentativa no puede mejorar después (invariante de nodos finalizados, R2). Aquí elegir el lugar más cercano no se puede corregir después: el costo de lo que falta y del regreso depende de todo el orden, y no hay propiedad de elección voraz ni subestructura que la respalde.
10. **Ejecución del experimento exacto**: los dos métodos se miden con `medir_en_hijo` (mismo modo para que sean comparables, y el límite de 5 min interrumpe la fuerza bruta). La verificación FB = HK antes de medir se corre en el proceso principal solo para los k en que FB tarde poco (k ≤ 9). Para k ≥ 10, el valor de FB que se compara es el que devuelve el proceso hijo de la medición. Si FB completa, su `tiempo_total_s` se compara con el de HK y una diferencia detiene el script sin escribir resultados.

## Casos borde
- k = 0 → `(0.0, [s])` en los tres métodos.
- k = 1 → `T[s][a] + T[a][s]`, recorrido `[s, a, s]`.
- k = 2 → se comparan los dos órdenes.
- Empates de costo → mismo tiempo total. Las pruebas comparan tiempos (±1e-6 s) y que el recorrido sea una permutación válida cuyo `costo_recorrido` coincide con el reportado. En la fuerza bruta, el desempate lexicográfico es exacto y se prueba aparte (caso 17).
- Dos lugares en el mismo nodo (T03, T05: costo 0 entre ellos) → válido, sin error.
- Matriz simétrica → el recorrido inverso cuesta lo mismo, sin errores.
- Lugar repetido en `lugares`, `s` dentro de `lugares` o un índice fuera de rango → `ValueError`.
- `T[i][j] = inf` → ningún recorrido que use ese arco puede ser el elegido. Si todos los recorridos son `inf` → `ValueError("no hay recorrido finito")`. En el vecino más cercano, si desde el actual solo quedan arcos `inf` → `ValueError`.
- Itinerario con menos de 6 o más de 8 atractivos de entrada, con un id que no es atractivo o con la partida entre los atractivos → `ValueError`.
- Itinerario que cabe de entrada → no se quita nada (lista de quitados vacía).
- Ejecución de más de 1 min → se mide una sola vez. Más de 5 min → `no_completada`, y la fila no se omite.

## Casos de prueba
Matriz de clase (4 lugares, segundos, partida 0, lugares [1, 2, 3]):

|   | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| **0** | 0 | 10 | 15 | 20 |
| **1** | 5 | 0 | 9 | 10 |
| **2** | 6 | 13 | 0 | 12 |
| **3** | 8 | 8 | 9 | 0 |

1. Los 6 recorridos (resueltos a mano y por enumeración): 1-2-3 → 39; **1-3-2 → 35**; 2-1-3 → 46; 2-3-1 → 40; 3-1-2 → 43; 3-2-1 → 47. Óptimo **35**, `[0, 1, 3, 2, 0]`.
2. `fuerza_bruta` y `held_karp` → `(35, [0, 1, 3, 2, 0])`.
3. Tabla de Held-Karp (máscara con bit 0 = lugar 1, bit 1 = lugar 2, bit 2 = lugar 3; formato lugar: (C, padre)), calculada a mano y por script:
   - 001 {1: (10, —)}; 010 {2: (15, —)}; 100 {3: (20, —)}
   - 011 {1: (28, 2), 2: (19, 1)}; 101 {1: (28, 3), 3: (20, 1)}; 110 {2: (29, 3), 3: (27, 2)}
   - 111 {1: (35, 3), 2: (29, 3), 3: (31, 2)}; cierre: 1 → 35 + 5 = 40, 2 → 29 + 6 = **35**, 3 → 31 + 8 = 39.
   La prueba lee `costo` y `padre` (Held-Karp las expone con una función interna `tabla_held_karp`) y compara las 12 celdas usadas.
4. **Voraz no óptimo:** `vecino_mas_cercano` → `(39, [0, 1, 2, 3, 0])` (10 + 9 + 12 + 8) frente a 35: brecha = 4/35 × 100 = **11,43 %**.
4b. **Voraz no óptimo, ejemplo simétrico a mano (documento técnico):** lugares en una vía, en minutos: C = −2, A = 0, B = 1, D = 5; `T` = |posición_i − posición_j|; partida A. El voraz da A→B→C→D→A = 1 + 3 + 7 + 5 = **16**. Óptimo **14** (p. ej. A→B→D→C→A = 1 + 4 + 7 + 2); brecha 14,29 %. De los 6 recorridos, 4 cuestan 14 y 2 cuestan 16 (verificado por enumeración).
5. Asimetría: el inverso `[0, 2, 3, 1, 0]` cuesta 15 + 12 + 8 + 5 = 40 ≠ 35.
6. k = 1, lugares [1] → `(15, [0, 1, 0])` en los tres métodos.
7. k = 2, lugares [1, 2]: 0-1-2-0 = 25; 0-2-1-0 = 33 → `(25, [0, 1, 2, 0])` en los tres.
8. k = 0 → `(0.0, [0])` en los tres.
9. Arco imposible: con `T[1][3] = inf`, el recorrido 1-3-2 (35) deja de servir. FB y HK → `(39, [0, 1, 2, 3, 0])`, y el voraz también da 39. Con `T[0][j] = inf` para todo j → `ValueError`.
10. Errores: `lugares = [1, 1]`, `lugares = [0, 1]` (con s = 0) y `lugares = [7]` (fuera de rango) → `ValueError`.
11. Propiedad (semilla 2026): 100 matrices asimétricas con enteros de 1 a 100 y k entre 1 y 8 → FB = HK en el tiempo total; el recorrido de HK empieza y termina en `s`, visita cada lugar una vez y su `costo_recorrido` es igual al reportado; voraz ≥ óptimo, con brecha ≥ 0.
12. Propiedad contra referencia: en esas mismas instancias, FB es igual al mínimo calculado con `itertools.permutations` (solo en la prueba).
13. Generador propio: para [0, 1, 2, 3] produce las 24 permutaciones en orden lexicográfico exacto (igual, como lista, a `list(itertools.permutations(...))`), sin repetir, y no modifica la lista de entrada. Para [5] → una permutación; para [] → una (la vacía).
14. Memoria: `memoria_held_karp(k)` → k = 5: 160 celdas, 1 920 B; k = 8: 2 048, 24 576 B; k = 10: 10 240, 122 880 B; k = 12: 49 152 celdas, **589 824 B (0,590 MB)**.
15. Conteos (para el informe; una prueba instrumenta HK con un contador opcional que solo se activa en las pruebas): transiciones de HK = k (base) + k(k−1)·2^(k−2) (paso) + k (cierre) → k = 3: 18; k = 5: 170; k = 8: 3 600; k = 10: 23 060; k = 12: 135 192. Fuerza bruta: k! permutaciones, (k+1)·k! tramos sumados → k = 12: 479 001 600 y 6 227 020 800.
16. Itinerario de clase (frontera de jornada), con 6 atractivos de 60 min (360 min) y una matriz cuyo recorrido óptimo suma 300 min → 660 min, **cabe** y no se quita nada. Con 301 min → 661 min, **no cabe**: se quita exactamente un atractivo y el que se quita es el que más ahorra (la matriz de la prueba se arma para que ese atractivo sea único).
17. Desempate lexicográfico de FB: con T de 4 lugares, todos los arcos = 1 (todos los recorridos cuestan 4) → `fuerza_bruta` → `[0, 1, 2, 3, 0]`; HK → costo 4 y recorrido válido.
18. Envoltorio por ids: `resolver_por_ids` con una matriz con ids `["C01", "A01", "A02", "A03"]` y los valores de la matriz de clase → `(35, ["C01", "A01", "A03", "A02", "C01"])`.
19. **Red real** (marca `red`): (a) FB = HK (±1e-6 s) para la instancia anidada con k = 5..8; (b) la instancia anidada de k = 12 da el recorrido de HK como permutación válida y su costo coincide con `costo_recorrido`; (c) el itinerario por defecto quita **A01 y luego A12**, en ese orden, y termina en **613,1 min ± 0,1** con 6 atractivos, calculado aparte por enumeración (script de exploración del coordinador, 2026-11-11); (d) la muestra anidada con semilla 2026 coincide con la lista de «Datos reales».
20. Archivos: `tablas_r4.md` y la gráfica se generan desde CSV de ejemplo escritos por la prueba (no desde los resultados reales). La fila `no_completada`/`no_ejecutada` aparece como «no completada». `r4_calidad.csv` es el promedio y el máximo del detalle.

## Complejidad esperada
- Fuerza bruta: Θ(k!) permutaciones × O(k) para sumar cada una → **O(k · k!)** en tiempo; **O(k)** de memoria (un arreglo y el mejor recorrido). El generador lexicográfico cuesta O(1) amortizado por permutación (Knuth, *TAOCP* vol. 4A, §7.2.1.2, algoritmo L), así que no cambia el orden.
- Held-Karp: k·2^(k−1) estados útiles, cada uno con O(k) transiciones → **O(k² · 2^k)** en tiempo; tabla de k·2^k celdas → **O(k · 2^k)** de memoria. Recurrencia en el punto 3 de «Comportamiento». Fuentes: Held y Karp (1962), *A dynamic programming approach to sequencing problems*, J. SIAM 10(1); Bellman (1962), *Dynamic programming treatment of the travelling salesman problem*, J. ACM 9(1).
- Vecino más cercano: **O(k²)** en tiempo y **O(k)** de memoria. Sin garantía de calidad en el ATSP; la cota de Rosenkrantz, Stearns y Lewis (1977), *An analysis of several heuristics for the traveling salesman problem*, SIAM J. Comput. 6(3), es para el caso métrico simétrico.
- Itinerario: en cada ronda de quitar se corren m Held-Karp de m−1 lugares, con m ≤ 8 → despreciable.
- Contexto: el TSP es NP-difícil (Cormen et al., *Introduction to Algorithms*, 3.ª ed., §34.5.4), y por eso los métodos exactos son exponenciales.
- Predicción para el informe: de k a k+1, la fuerza bruta crece ≈ (k+1)·(k+1)/k veces (≈ 13 de 11 a 12) y Held-Karp ≈ 2·((k+1)/k)² veces (≈ 2,4).

## Verificación (sección 6, punto 6)
- Casos 1 a 10 y 17 resueltos a mano (las tablas de enumeración y la de Held-Karp están en esta spec).
- FB frente a HK: mismo tiempo total en todos los k que FB alcance a resolver. Lo hacen las pruebas (casos 11 y 19a) y el script de medición antes de escribir resultados (punto 10 de «Comportamiento»).
- FB frente a `itertools.permutations` (caso 12, solo en las pruebas).
- Recorrido de HK: permutación válida cuyo costo, recalculado desde `T`, coincide con el reportado.
- Heurística: brecha ≥ 0 siempre. Los casos 4 y 4b muestran que puede ser > 0.
- Itinerario real: comparado con la enumeración independiente (caso 19c).

## Medición (sección 6)
- Qué: solo la llamada a `fuerza_bruta(T, s, lugares)` o `held_karp(T, s, lugares)`. Cargar la matriz, sortear las instancias y escribir archivos quedan fuera.
- Cómo: `medir_en_hijo` para los dos métodos (5 repeticiones y mediana; si la primera pasa de 60 s, una sola; si pasa de 300 s, `no_completada`). Tiempos en ms, semilla 2026 documentada en `r4_instancias.json`, misma máquina (`maquina.json`), portátil enchufado. La corrida real la lanza el usuario (puede tardar más de 10 min: la fuerza bruta debería llegar al límite cerca de k = 11 o 12).
- Calidad e itinerario no se cronometran.
- Informe: tabla del anexo, gráfica de tiempo frente a k (escala logarítmica) y un párrafo que compare los cocientes medidos entre k consecutivos con los predichos (k·k! frente a k²·2^k) y explique el mayor k de cada método. Además, la memoria estimada frente al pico de `tracemalloc`.

## Pendientes para el documento técnico
Subestructura óptima y recurrencia (Comportamiento 2 y 3, ilustradas con la tabla del caso 3), justificación del vecino más cercano, complejidades con fuentes, tabla de exactas y mayor k resuelto, gráfica, memoria estimada frente a la medida, tabla de calidad y su discusión, itinerario con la justificación de cada atractivo quitado, el voraz frente al óptimo y la comparación con Dijkstra (casos 4 y 4b), y cómo se verificó cada algoritmo. Uso de IA en `docs/anexo-ia.md`.

## Decisiones
Resueltas por el grupo (2026-11-11): heurística del vecino más cercano (desempate por menor índice); fuerza bruta con generador propio de la siguiente permutación lexicográfica, sin poda; instancias anidadas para el experimento exacto (una sola muestra con semilla 2026, los primeros k); quitar del itinerario el atractivo que más reduce la jornada, recalculando con Held-Karp; itinerario del documento con A05, A08, A04, A14, A06, A07, A12 y A01 desde C01; memoria = estimación de 12 B por celda + pico de `tracemalloc` aparte; 10 instancias por k en la calidad (semillas 2026..2035); tabla de Held-Karp como listas 2^k × k.

Puerta 2 (2026-11-11): se aprueba agregar `devolver_valor` a `medir_en_hijo` (compatible con R1–R3), las decisiones menores del plan y Python 3.13.18 en `.venv` (ver plan.md).

Puerta 1 (2026-11-11), aprobadas por el usuario junto con la spec: resultados en `results/r4/`; los dos métodos exactos medidos con `medir_en_hijo`; tolerancia de 1e-6 s entre FB y HK; tras un `no_completada`, los k mayores de ese método no se ejecutan (`no_ejecutada`, se muestra como «no completada»); gráfica en escala logarítmica; no modificar `.gitignore` sin preguntar.

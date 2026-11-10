# Envolvente convexa de la red vial — Requerimiento 3
Enunciado: sección 5, Requerimiento 3 (párrafo «Coordenadas», punto 1 Algoritmo y punto 2 Experimento); protocolo en sección 6; formato en Anexo, Requerimiento 3. Peso: 20 % (40 % implementación verificada, 30 % teoría, 30 % experimental).
Estado: ☑ spec (aprobada en Puerta 1, 2026-11-10) · ☐ pruebas · ☐ código · ☐ verificado
Depende de: `r1-red-vial` (cerrado): nodos de la componente con `x_utm`, `y_utm` (EPSG:32618) en `data/processed/grafo_componente.graphml`, `rutas.r1.persistencia`, `rutas.r1.utm`; `rutas.medicion.medir_en_proceso`.

## Propósito
Calcular la envolvente convexa de los nodos de la componente con un algoritmo propio de **divide y vencerás** (QuickHull), verificar que da los mismos vértices que `scipy.spatial.ConvexHull` en todas las pruebas, y medir ambos con los nodos de la red y con puntos al azar en un cuadrado. La envolvente se dibuja en R5.

## Datos reales (2026-11-10, para dimensionar)
8 791 nodos → 8 791 puntos enteros distintos tras redondear; la envolvente tiene **14 vértices** y área ≈ 1 631,5 km² (SciPy, solo exploración). Extensión: x 401 796–446 623 m, y 464 304–520 840 m.

## Entradas y salidas
**Preparación de puntos** `preparar_puntos(xs, ys) -> list[tuple[int, int]]` (fuera de la medición)
1. Coordenadas en metros UTM zona 18N: se usan `x_utm`, `y_utm` de los nodos (R1 ya las calculó con EPSG:32618); para otros datos, `rutas.r1.utm`.
2. Cada coordenada al entero más cercano con `math.floor(x + 0.5)` (empates en .5 hacia +∞; regla documentada y la misma para ambas implementaciones).
3. Se eliminan los repetidos y se devuelven ordenados lexicográficamente (orden determinista; no es parte del algoritmo).
4. En Python los enteros no desbordan; se usan `int` de Python en todo el cálculo geométrico (sin flotantes). Equivale a lo que el enunciado pide con enteros de 64 bits.

**Algoritmo** `envolvente(puntos) -> list[tuple[int, int]]`: vértices en sentido **antihorario**, empezando por el de menor y y, en empate, menor x. Los puntos alineados sobre un lado **no** son vértices.

**Utilidades**: `area(vertices)` (fórmula del zapato, con enteros → área exacta ×2), `normalizar(vertices)` (rota al punto de inicio y orden antihorario, para comparar con SciPy), `vertices_scipy(puntos)` (solo para verificar y medir).

**Archivos**
- `data/processed/envolvente.csv`: `orden, x_utm, y_utm, lat, lon` (vértices en orden antihorario; lat/lon con la conversión inversa de `pyproj`, para R5).
- `data/processed/envolvente.geojson`: polígono cerrado en lat/lon (EPSG:4326) para el mapa de R5, con propiedades `vertices`, `area_km2`.
- `results/r3/r3_envolvente.csv`: columnas del Anexo `conjunto, n, vertices, tiempo_propio_ms, tiempo_scipy_ms, cociente`, ampliadas con `repeticiones`; filas en el orden del Anexo: «Nodos de la red», «Cuadrado, 1 000 puntos», «Cuadrado, 10 000 puntos», «Cuadrado, 50 000 puntos». `n` = puntos tras eliminar repetidos; `cociente` = propio / SciPy.
- `results/r3/r3_puntos.json`: semilla, tamaño del cuadrado y n pedidos/obtenidos.
- `results/r3/maquina.json`, `results/r3/tablas_r3.md` (generada desde el CSV) y `results/r3/r3_envolvente.png` (nodos de la red y polígono, en metros UTM, desde los CSV/GraphML).

## Comportamiento
1. **Predicado de giro** `cruz(o, a, b) = (a.x − o.x)(b.y − o.y) − (a.y − o.y)(b.x − o.x)` con enteros: > 0 giro a la izquierda (b a la izquierda de o→a), 0 alineados, < 0 a la derecha.
2. **QuickHull** (decisión del grupo):
   - Extremos iniciales A = mínimo y B = máximo lexicográfico (x, luego y). Con un solo punto distinto → `[p]`; con todos alineados → `[A, B]` (en el orden de salida).
   - Se reparten los puntos en los que están **estrictamente** a la izquierda de A→B y de B→A (cruz > 0); los alineados se descartan.
   - `_lado(puntos, a, b)` (recursiva): si no hay puntos, no hay vértices entre a y b. Si no, toma el punto c con **mayor** `cruz(a, b, c)` (el más lejano de la recta ab); en empate, el **menor lexicográfico** del grupo empatado (los empatados están sobre una recta paralela a ab y el elegido es uno de sus extremos; el otro extremo saldrá en la recursión y los intermedios quedan alineados y se descartan). Recurre con los puntos estrictamente a la izquierda de a→c y de c→b; los de dentro del triángulo a, c, b se descartan. Devuelve los vértices entre a y b en orden.
   - Se ensamblan los vértices y se rotan al punto de inicio de la salida (menor y, luego menor x), antihorario.
   - **Recurrencia:** T(n) = T(n₁) + T(n₂) + O(n), con n₁ + n₂ ≤ n − 1 (n = puntos del subproblema). Particiones parejas: T(n) = 2T(n/2) + O(n) = O(n log n) (teorema maestro); peor caso T(n) = T(n − 1) + O(n) = O(n²).
3. **Recursión (decisión del grupo):** implementación recursiva, porque sigue la recurrencia del informe. Como protección, el módulo sube el límite con `sys.setrecursionlimit(20_000)` y lo documenta en un comentario: con particiones parejas la profundidad es O(log n), pero en el peor caso puede llegar a O(n) y el límite por defecto de Python (~1 000) cortaría la ejecución.
4. **Justificación de QuickHull (informe):** la red se concentra en cabeceras y corredores viales y solo 14 de 8 791 nodos son vértices; QuickHull descarta en cada nivel los puntos interiores al triángulo, así que con pocos vértices h trabaja mucho menos que n log n (comportamiento cercano a O(n log h) en la práctica). Es además de la misma familia que Qhull, de modo que la comparación con SciPy resalta el efecto del lenguaje. El informe menciona el peor caso (casos 15 y 16).
5. **Comparación con SciPy:** SciPy recibe exactamente los mismos puntos enteros (como `numpy.array` de `int64`). Se comparan los **conjuntos** de vértices y, además, las salidas normalizadas (mismo punto de inicio y sentido). `ConvexHull` no reporta colineales como vértices con sus opciones por defecto.
6. **Experimento (decisión del grupo):** puntos enteros uniformes en el cuadrado [0, 10⁶) × [0, 10⁶) con `random.Random(2026)`, n pedido = 1 000, 10 000 y 50 000; se eliminan repetidos (se reporta n obtenido; se esperan muy pocos). Referencia para detectar errores: el número esperado de vértices crece como (8/3) ln n (Rényi y Sulanke, 1963) ≈ 18, 25 y 29.
7. **Por qué SciPy es más rápido (informe):** `scipy.spatial.ConvexHull` llama a la biblioteca Qhull (algoritmo Quickhull, escrita en C) a través de un envoltorio en Cython (`scipy/spatial/_qhull.pyx`); el código propio es Python interpretado. Se comprueba en el código fuente de la versión instalada (SciPy 1.18.1) y se cita.

## Casos borde
- 0 puntos → `[]`. 1 punto → `[p]`. 2 puntos distintos → ambos en el orden de salida.
- Todos alineados → los dos extremos. SciPy lanza `QhullError` en ese caso y con 2 puntos: la prueba lo comprueba y no compara contra SciPy ahí.
- Repetidos, o puntos que coinciden tras redondear → cuentan como uno (los quita `preparar_puntos`; `envolvente` también tolera repetidos).
- Punto sobre un lado → no es vértice.
- Todos los puntos son vértices (círculo, parábola) → devuelve los n, sin `RecursionError`.
- Coordenadas negativas o grandes (3 · 10⁹) → correctas (enteros de Python, sin flotantes).

## Casos de prueba
1. Cuadrado con extras: (0,0), (4,0), (4,4), (0,4), (2,2), (2,0) → (0,0), (4,0), (4,4), (0,4).
2. Desempate (del documento técnico y de `casos_prueba.json`): (0,0), (10,0), (2,5), (5,5), (8,5) → (0,0), (10,0), (8,5), (2,5); (5,5) está alineado sobre el lado superior y no es vértice.
3. Rectángulo con puntos en los lados (de `casos_prueba.json`): (0,0), (5,0), (10,0), (10,10), (5,10), (0,10), (0,5), (10,5), (3,4) → (0,0), (10,0), (10,10), (0,10).
4. Pentágono con interior: (0,0), (5,0), (6,3), (3,6), (−1,3), (2,2) → (0,0), (5,0), (6,3), (3,6), (−1,3).
5. Duplicados: (0,0), (0,0), (1,0), (0,1) → (0,0), (1,0), (0,1).
6. Alineados: (0,0), (1,1), (2,2), (3,3) → (0,0), (3,3); SciPy lanza `QhullError` (`casos_prueba.json`, «colineales»).
7. Un punto (7,7) → [(7,7)]; vacío → []; dos puntos (0,0), (1,0) → ambos; SciPy lanza `QhullError` con dos puntos.
8. Coordenadas grandes: (0,0), (3·10⁹, 0), (0, 3·10⁹), (1,1) → los tres primeros (cruz = 9·10¹⁸, cabe en 64 bits; en Python no hay desborde).
9. Redondeo: x = 2,5 → 3; x = −0,5 → 0; x = 2,4999 → 2; y repetidos tras redondear se fusionan.
10. Red de la clase (copia versionada en `tests/datos/red_clase.json`, sección `R3` agregada con el mismo origen que `red` y `R2`): los 9 nodos con sus coordenadas → vértices los nodos **9, 7, 8, 3, 2**; los nodos 4 y 6 quedan sobre lados y **no** son vértices; área = **585 000 m²**. (Verificado con SciPy.)
11. Propiedad con semilla 2026: 100 conjuntos aleatorios (n entre 3 y 200, coordenadas enteras pequeñas para forzar colineales y repetidos) → mismos vértices que SciPy (normalizados); los conjuntos degenerados se saltan la comparación con SciPy pero se comprueban con el caso 13.
12. Cuadrados de 1 000 / 10 000 / 50 000 puntos con semilla 2026: mismos vértices que SciPy; número de vértices del mismo orden que (8/3) ln n.
13. Invariantes geométricos (para toda salida de las pruebas): convexidad estricta (cada tres vértices consecutivos giran a la izquierda, cruz > 0) y todos los puntos dentro o sobre el borde (cruz ≥ 0 respecto de cada lado).
14. Red real (`red`): vértices propios = SciPy; 14 vértices; área = la de SciPy (`volume`) ± 1 m²; invariantes del caso 13 con los 8 791 puntos.
15. Círculo (decisión del usuario): 2 000 puntos redondeados sobre la circunferencia de radio 10⁶ centrada en el origen → los **2 000** son vértices (comprobado con SciPy), sin `RecursionError`.
16. Parábola: puntos (k, k²) para k = 0 … 4 999 → los 5 000 son vértices (convexidad estricta exacta con enteros), sin `RecursionError`.
17. Archivos: `envolvente.csv` y `envolvente.geojson` tienen el polígono cerrado; la ida y vuelta UTM → lat/lon → UTM de cada vértice da error < 1 m.

## Complejidad esperada
- QuickHull: tiempo O(n log n) con particiones parejas y O(n²) en el peor caso (recurrencias del punto 2); memoria O(n) para las listas de cada nivel más la pila de recursión, O(log n) con particiones parejas y O(n) en el peor caso.
- Preparación (redondeo, conjunto para quitar repetidos, `sorted`): O(n log n), fuera de la medición. `sorted` de Python (Timsort) es O(n log n) en el peor caso (documentación de Python, `list.sort`).
- Fuentes: C. B. Barber, D. P. Dobkin y H. Huhdanpaa, «The Quickhull algorithm for convex hulls», *ACM Transactions on Mathematical Software* 22(4):469–483, 1996 (Qhull; su análisis de O(n log r) es empírico); W. F. Eddy, «A new convex hull algorithm for planar sets», *ACM TOMS* 3(4):398–403, 1977 (QuickHull en el plano); Rényi y Sulanke, «Über die konvexe Hülle von n zufällig gewählten Punkten», *Z. Wahrscheinlichkeitstheorie* 2:75–84, 1963 (número esperado de vértices); documentación y código de SciPy 1.18.1 (`scipy.spatial.ConvexHull`, `_qhull.pyx`) y de Qhull. Cormen et al. queda pendiente, como en R2.

## Verificación
- Casos 1 a 10 resueltos a mano (y 2, 3, 6, 7, 10 contrastados con SciPy).
- Contra `scipy.spatial.ConvexHull` en todas las pruebas no degeneradas (lo exige el enunciado).
- Invariantes geométricos independientes de SciPy (caso 13).

## Medición (sección 6)
- Qué: `envolvente(puntos)` con la lista ya preparada y `ConvexHull(arreglo)` con el `numpy.array` ya construido (decisión del grupo: la conversión a numpy es preparación y queda fuera, como la de la propia). Ambas con `medir_en_proceso`, 5 repeticiones, mediana en ms; una sola si pasa de 1 min; "no completada" si pasa de 5 min.
- Conjuntos: nodos de la red (n = 8 791) y cuadrados de 1 000, 10 000 y 50 000 con semilla 2026.
- Antes de medir, el script comprueba que propia y SciPy dan los mismos vértices en cada conjunto; si no, se detiene sin escribir.
- Misma máquina, portátil enchufado; `maquina.json`. La medición real la corre el usuario.
- Discusión: cociente propio/SciPy por conjunto; si el tiempo propio crece como n log n (o menos, por los pocos vértices); diferencia C/Cython vs Python.

## Pendientes para el documento técnico
Justificación de QuickHull con la distribución real (14 de 8 791), recurrencia y complejidad con fuentes, regla de redondeo y de empates, tabla del Anexo, explicación de Qhull/C/Cython, gráfica del polígono, área de la envolvente frente al área del departamento (≈ 1 632 km² frente a ≈ 1 935 km²). Uso de IA en `docs/anexo-ia.md` (local).

## Decisiones
Puerta 1 (2026-11-10): se agrega la sección `R3` de `estudio/casos_prueba.json` a la copia versionada `tests/datos/red_clase.json`, con nota de origen. Tarea pequeña de R2 incluida en el primer bloque de R3 (aprobada por el usuario): en `results/r2/tablas_r2.md` la pendiente del ajuste de la cola se muestra en **µs por nodo** y la de la lineal en **ms por nodo** (columna con la unidad explícita), regenerando solo `tablas_r2.md` con `rutas.r2.tablas` desde los CSV ya medidos (no se repite la medición).

Resueltas por el grupo (2026-11-10): QuickHull recursivo con `sys.setrecursionlimit(20_000)` documentado y pruebas del círculo y la parábola; cuadrado de 10⁶ × 10⁶ con semilla 2026; en SciPy solo se mide `ConvexHull(arreglo)`; redondeo `floor(x + 0.5)`; resultados en `results/r3/`; la medición real la corre el usuario con el portátil enchufado; no modificar `.gitignore` sin preguntar.

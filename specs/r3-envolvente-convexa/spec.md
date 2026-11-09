# Envolvente convexa de la red vial — Requerimiento 3
Enunciado: sección 5, Requerimiento 3; protocolo en sección 6; formato en Anexo, Requerimiento 3. Peso: 20 %.
Estado: ☐ spec (borrador, pendiente de aprobación del grupo) · ☐ pruebas · ☐ código · ☐ verificado
Depende de: `r1-red-vial` (nodos de la componente con coordenadas).

## Propósito
Calcular la envolvente convexa de los nodos de la componente con un algoritmo propio de **divide y vencerás**, verificar que da los mismos vértices que `scipy.spatial.ConvexHull`, y medir ambos con los nodos de la red y con puntos aleatorios.

## Entradas y salidas
**Entradas:** lista de puntos `(lat, lon)` de los nodos de la componente, o puntos ya en metros.

**Pipeline de coordenadas (`preparar_puntos`)**
1. Convertir a UTM zona 18N (EPSG:32618), en metros.
2. Redondear cada coordenada al entero más cercano. **Empates en .5: se redondea hacia +∞ (`floor(x + 0.5)`)**, igual para las dos implementaciones (decisión de esta spec; documentarla).
3. Eliminar puntos repetidos.
4. Enteros de 64 bits en lenguajes de enteros fijos.

**Salida** `envolvente(puntos) -> lista de vértices (x, y)` en sentido antihorario, empezando por el punto más abajo y, en empate, más a la izquierda. Los puntos alineados sobre un lado **no** son vértices.

**Archivos**
- `data/processed/envolvente.csv` (vértices en UTM) y `envolvente.geojson` (lat/lon, para el mapa de R5).
- `results/r3_envolvente.csv`: `conjunto, n, vertices, tiempo_propio_ms, tiempo_scipy_ms, cociente`.
- Filas: nodos de la red; cuadrado con 1 000, 10 000 y 50 000 puntos.

## Comportamiento
1. **Predicado de giro (producto cruzado)** `cruz(o, a, b) = (a.x−o.x)(b.y−o.y) − (a.y−o.y)(b.x−o.x)`: > 0 giro a la izquierda, 0 alineados, < 0 giro a la derecha. Se calcula con enteros, sin flotantes.
2. **Algoritmo: QuickHull** (propuesta del documento técnico, **[DECISIÓN, confirmar con el equipo antes de implementar]**). Razón: la red se concentra en cabeceras y corredores viales, se espera que pocos nodos sean vértices, y QuickHull descarta pronto los puntos interiores; además es de la misma familia que Qhull (SciPy), de modo que la comparación resalta el efecto del lenguaje. El informe menciona su peor caso (particiones muy desbalanceadas en cada nivel) aunque no se espere aquí.
   **Reglas de desempate** (con coordenadas enteras los empates son frecuentes):
   1. Extremos iniciales: el menor y el mayor en orden lexicográfico (x, luego y). Tomar cualquier punto con x mínima puede elegir uno alineado sobre un lado vertical.
   2. Punto más lejano de un lado: si varios empatan, se toma el extremo lexicográfico del grupo (los empatados forman un lado; uno intermedio no es vértice).
   3. Lado exterior: solo se conservan puntos con producto cruzado **estrictamente positivo**; los alineados se descartan.
   Sin estas reglas un punto alineado puede aparecer como vértice falso (caso 1b).
3. Los vértices se comparan con SciPy como **conjuntos** de puntos (el orden/punto de inicio de SciPy puede diferir): se normalizan ambas salidas al mismo orden antihorario y mismo punto inicial antes de comparar.
4. SciPy recibe exactamente los mismos puntos enteros ya preparados. `ConvexHull` no devuelve los colineales como vértices; si Qhull los incluyera con una opción, se descartan para comparar.
5. Experimento: puntos al azar uniformes en un cuadrado de 1 000 000 × 1 000 000 unidades (**[DECISIÓN]**, deja muy pocos puntos repetidos; n se reporta después de eliminarlos) con **semilla fija** (documentada), coordenadas enteras. Para puntos uniformes en un cuadrado el número esperado de vértices crece como (8/3) ln n (Rényi y Sulanke, 1963, citados por Guo, Li y Pei): ≈ 18, 25 y 29 para 1 000, 10 000 y 50 000 puntos. Es solo una referencia para detectar errores. Cada medición cubre solo el cálculo de la envolvente (conversión UTM, redondeo, generación de datos y lectura quedan fuera del cronómetro).
6. El informe explica la diferencia de tiempos investigando el algoritmo y el lenguaje de SciPy: `scipy.spatial.ConvexHull` usa la librería Qhull (QuickHull, escrita en C) a través de un envoltorio en Cython (`_qhull.pyx`). Como el algoritmo es de la misma familia y el código propio es Python, gran parte del cociente debería venir de C compilado frente a Python (el cociente propio/SciPy será grande). Se justifica la elección según la distribución de los nodos (muy agrupados en ciudades, pocos vértices respecto a n; **[PENDIENTE: confirmar con n y vértices reales]**).

## Casos borde
- 0 puntos → `[]`. 1 punto → `[p]`. 2 puntos distintos → ambos. 
- Todos los puntos alineados → los dos extremos (no hay polígono). SciPy lanza error en ese caso: la prueba lo comprueba y no compara contra SciPy en esa situación.
- Puntos repetidos → se eliminan antes.
- Puntos que tras redondear coinciden → cuentan como uno.
- Punto sobre un lado (colineal entre dos vértices) → no es vértice.
- Todos los puntos en un círculo (todos son vértices) → devuelve los n.
- Coordenadas grandes (~3·10⁹) → sin desbordar 64 bits (el producto cruzado llega a ~9·10¹⁸, por debajo de 2⁶³ ≈ 9,22·10¹⁸). Es una prueba de estrés: las coordenadas UTM reales están por debajo de 10⁷, así que cada producto queda por debajo de 10¹⁴. En Python los enteros no desbordan, pero la prueba se conserva para que el algoritmo no use flotantes.
- Coordenadas negativas → válidas.

## Casos de prueba
1b. **Desempate (del documento técnico):** (0,0), (10,0), (2,5), (5,5), (8,5) → 4 vértices: (0,0), (10,0), (8,5), (2,5). El punto (5,5) está alineado sobre el lado superior y **no** es vértice.
1. Cuadrado con puntos extra: (0,0), (4,0), (4,4), (0,4), (2,2), (2,0) → vértices (0,0), (4,0), (4,4), (0,4). (2,2) es interior y (2,0) está alineado sobre un lado.
2. Pentágono con un punto interior: (0,0), (5,0), (6,3), (3,6), (−1,3), (2,2) → (0,0), (5,0), (6,3), (3,6), (−1,3). Comprobado a mano con productos cruzados positivos en los cinco giros.
3. Duplicados: (0,0), (0,0), (1,0), (0,1) → triángulo (0,0), (1,0), (0,1).
4. Alineados: (0,0), (1,1), (2,2), (3,3) → (0,0), (3,3).
5. Un punto: (7,7) → (7,7). Vacío → vacío. Dos puntos: (0,0), (5,5) → ambos.
6. Triángulo grande (desborde de 32 bits): (0,0), (3 000 000 000, 0), (0, 3 000 000 000), (1,1) → los tres primeros; el producto cruzado es 9·10¹⁸ y no desborda con 64 bits.
7. Redondeo: lat/lon que convierte a (2,5; −0,5) → se prepara como (3, 0) con la regla de empates documentada.
8. Rectángulo con muchos puntos sobre sus lados → solo las 4 esquinas.
9. Aleatorio con semilla fija: 100 conjuntos pequeños (n entre 3 y 200) → mismos vértices que SciPy.
10. Red real: los vértices de la envolvente propia = los de SciPy; todos los nodos de la componente quedan dentro o sobre el polígono (comprobación con el predicado de giro).
11. Invariante geométrico: en todo par de vértices consecutivos del resultado, el giro con el siguiente vértice es estrictamente a la izquierda (convexidad estricta, sin colineales).
12. Cuadrado de 1 000 / 10 000 / 50 000 puntos con semilla fija: mismos vértices que SciPy y número de vértices reportado.

## Complejidad esperada
(Citar fuente con autor y título; el informe incluye la recurrencia.)
- Mezcla de envolventes (Preparata–Hong): T(n) = 2T(n/2) + O(n) → O(n log n) en el peor caso.
- QuickHull propio: T(n) = T(n₁) + T(n₂) + O(n) con n₁ + n₂ ≤ n; balanceado (T(n) = 2T(n/2) + O(n), teorema maestro) O(n log n); peor caso T(n) = T(n−1) + O(n) = O(n²). Barber, Dobkin y Huhdanpaa (1996) dan O(n log r) para r puntos procesados bajo condiciones de equilibrio y aclaran que su análisis es empírico.
- Memoria: O(n) (más la pila de recursión: O(log n) en promedio, hasta O(n) en el peor caso de Quickhull).
- Fuentes candidatas: Cormen et al., *Introduction to Algorithms* (envolvente convexa); Preparata y Hong (1977), *Convex hulls of finite sets of points in two and three dimensions*; Barber, Dobkin y Huhdanpaa (1996), *The Quickhull algorithm for convex hulls*.
- Ordenar los puntos por x (si el algoritmo lo necesita) cuesta O(n log n) y debe incluirse en el análisis.

## Verificación
- Casos 1 a 8 resueltos a mano.
- Contra `scipy.spatial.ConvexHull` en todos los conjuntos de prueba (exigido por el enunciado): mismo conjunto de vértices.
- Comprobación geométrica independiente (caso 10 y 11): todos los puntos dentro y convexidad estricta.

## Medición
- Qué: tiempo de `envolvente(...)` propia y de `ConvexHull(...)` sobre los mismos puntos preparados.
- Conjuntos: nodos de la red; cuadrado de 1 000, 10 000 y 50 000 puntos con semilla fija.
- Protocolo: 5 repeticiones y mediana, ms, misma máquina (CPU, RAM, SO, versión del lenguaje), límite de 5 min. Tabla del anexo con el cociente propio / SciPy y un párrafo que explique la diferencia (C vs. el lenguaje del grupo, Qhull y sus optimizaciones) y compare con la complejidad.

## Decisiones
Propuestas del documento técnico, pendientes de confirmar: QuickHull frente a la mezcla de envolventes de Preparata y Hong (garantiza O(n log n); se procesan y ordenan todos los puntos interiores); cuadrado de 10⁶ × 10⁶ con semilla documentada.

Propuesta de esta spec: regla de empate de redondeo `floor(x + 0.5)`.

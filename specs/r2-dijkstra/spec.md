# Caminos mínimos (Dijkstra y matriz de tiempos) — Requerimiento 2
Enunciado: sección 5, Requerimiento 2; protocolo en sección 6; formatos en Anexo, Requerimiento 2. Peso: 20 %.
Estado: ☐ spec (borrador, pendiente de aprobación del grupo) · ☐ pruebas · ☐ código · ☐ verificado
Depende de: `r1-red-vial` (componente con `tiempo_s` y asociación lugar → nodo).

## Propósito
Implementar dos versiones propias de Dijkstra (recorrido lineal y cola de prioridad), medirlas, verificar que coinciden y calcular la matriz de tiempos entre todos los lugares del catálogo, que usa R4.

## Entradas y salidas
**Entradas:** grafo dirigido de la componente (lista de adyacencia, peso = `tiempo_s` ≥ 0); nodo origen; nodo destino (opcional); asociación lugar → nodo.

**Salidas de cada versión** `dijkstra(grafo, origen, destino) -> (tiempo_s, ruta, nodos_explorados)`
- `tiempo_s`: tiempo mínimo (`inf`/`None` si el destino no es alcanzable).
- `ruta`: lista de nodos origen → destino reconstruida con el predecesor de cada nodo (vacía si no hay camino).
- `nodos_explorados`: nodos extraídos de la cola por primera vez, incluido el destino.

Sin destino (`destino = None`) calcula todas las distancias (para la matriz) y devuelve `dist` y `pred`.

**Archivos**
- `results/r2_dijkstra.csv`: `origen, destino, version, tiempo_viaje_s, nodos_explorados, tiempo_ms` (una fila por consulta y versión; `version ∈ {lineal, cola_prioridad}`).
- `results/r2_cociente.csv`: `mediana, minimo, maximo` del cociente tiempo lineal / tiempo cola en los 10 pares comunes.
- `results/r2_grafica.png`: nodos explorados (eje x) vs. tiempo en ms (eje y), una marca/color por versión.
- `data/processed/matriz_tiempos.csv`: primera fila y primera columna = ids de lugares; celda (i, j) = segundos para ir de i a j; sin encabezados extra.

## Comportamiento
0. **Aristas paralelas:** el grafo de R1 puede venir como MultiDiGraph; el grafo de trabajo conserva, por par de nodos y sentido, la arista de menor tiempo (con su distancia y geometría juntas). La ruta devuelta usa esas aristas. El tiempo reportado **no incluye** el tramo entre el lugar y su nodo.
1. **Lineal, O(V²):** en cada iteración se busca el mínimo entre los no visitados con un recorrido lineal.
2. **Cola de prioridad, O((V + E) log V):** montículo binario (`heapq` si el lenguaje es Python). `heapq` no permite cambiar una prioridad: su documentación propone marcar la entrada vieja e insertar otra, así que la cola guarda hasta E + 1 entradas y la memoria es O(V + E). Una entrada obsoleta (nodo ya extraído) se descarta sin contarla. El tiempo no empeora: tras dejar una arista por par, E ≤ V², luego log E ≤ 2 log V.
3. Ambas se detienen **al sacar el destino**. Un nodo se cuenta como explorado **una sola vez**, la primera vez que sale de la cola.
4. Relajación: si `dist[u] + w < dist[v]`, se actualizan `dist[v]` y `pred[v] = u`.
5. Ruta = seguir `pred` desde el destino hasta el origen y invertir.
6. Los pesos deben ser ≥ 0; un peso negativo lanza error (el invariante deja de valer).
7. **Matriz de tiempos:** para cada lugar, una corrida de la versión con cola **sin destino** y se leen las distancias hacia los demás nodos-lugar. No es simétrica. Diagonal = 0. Si dos lugares comparten nodo, su tiempo mutuo es 0. Un par inalcanzable se marca `inf` (no debería ocurrir dentro de una componente fuertemente conexa; se prueba que no ocurra).
8. **Argumentos de correctitud que el informe debe incluir:** el invariante (cuando un nodo sale de la cola, su distancia es la mínima; todos los nodos ya extraídos tienen distancia final), por qué se puede parar al sacar el destino, y por qué exige pesos ≥ 0.

## Casos borde
- Origen = destino → tiempo 0, ruta `[origen]`, explorados = 1.
- Destino inalcanzable → tiempo `inf`, ruta vacía; explora todo lo alcanzable.
- Arista de peso 0 → permitida.
- Peso negativo → error.
- Varios caminos de igual costo → el tiempo es el mismo; la ruta puede diferir, pero debe ser un camino válido de ese costo (la prueba compara el costo, no la secuencia exacta, salvo en los casos con camino único).
- Nodo origen inexistente → error claro.
- Entradas obsoletas en la cola (el nodo B entra con 4 y luego con 3) → B se cuenta una vez.

## Casos de prueba
Grafo dirigido G1 (pesos en segundos): A→B 4, A→C 1, C→B 2, B→D 1, C→D 5, D→E 3; F aislado (sin aristas).

| # | Consulta | Tiempo | Ruta | Explorados (orden de extracción) |
|---|---|---|---|---|
| 1 | A→B | 3 | A, C, B | 3 (A, C, B) |
| 2 | A→D | 4 | A, C, B, D | 4 (A, C, B, D) |
| 3 | A→E | 7 | A, C, B, D, E | 5 (A, C, B, D, E) |
| 4 | A→A | 0 | A | 1 (A) |
| 5 | A→F | inf | (vacía) | 5 (A, C, B, D, E) |
| 6 | E→A | inf | (vacía) | 1 (E) |

7. Todas las distancias desde cada nodo de G1 (matriz asimétrica; `inf` donde no hay camino), orden A, B, C, D, E:
   - desde A: 0, 3, 1, 4, 7
   - desde B: inf, 0, inf, 1, 4
   - desde C: inf, 2, 0, 3, 6
   - desde D: inf, inf, inf, 0, 3
   - desde E: inf, inf, inf, inf, 0
8. Peso 0: añadir B→E con peso 0 → A→E pasa a costar 3 por A, C, B, E.
9. Peso negativo (A→F con −1) → lanza error.
10. Las dos versiones devuelven el mismo tiempo en 1 a 6 y en el caso 8.
11. Propiedad (aleatoria con semilla fija): en 200 grafos aleatorios pequeños dirigidos con pesos enteros 0 a 20, ambas versiones coinciden entre sí y con `networkx.single_source_dijkstra` (solo en la prueba).
12. Red real: en los 10 pares medidos con ambas versiones, los tiempos coinciden con **tolerancia de 0,001 s** (son sumas de decimales; **[DECISIÓN del documento técnico]**); el tiempo de la ruta devuelta, sumando los pesos de sus aristas, es igual a `tiempo_s` con la misma tolerancia.
12b. Aristas paralelas: grafo con dos aristas A→B de 50 s y 40 s → el tiempo de A→B es 40 s y la ruta usa la de 40 s.
12c. Pesos del grafo real: ningún `tiempo_s` es negativo, nulo por error ni infinito (se comprueba al cargar).
13. Matriz: ≥ 40 × 40, diagonal 0, sin `inf`, no simétrica en al menos un par; `M[i][j]` coincide con `dijkstra(i, j)` en una muestra de 20 pares.

## Complejidad esperada
- Versión lineal: O(V²) tiempo, O(V) memoria adicional (más el grafo).
- Versión con cola binaria: O((V + E) log V) tiempo, O(V + E) memoria. Con inserciones perezosas la cola puede tener hasta E entradas: documentarlo.
- Matriz: P ejecuciones de Dijkstra con cola → O(P · (V + E) log V) con P ≈ 40.
- Fuentes: Cormen et al., *Introduction to Algorithms*, 3.ª ed., sección 24.3 (**pendiente de confirmar en el libro**: el documento técnico la marca como no consultada); notas de la clase 16 de MIT 6.006 (2011); Dijkstra, «A note on two problems in connexion with graphs», *Numerische Mathematik* 1, 1959; documentación de `heapq`.
- Costo de la librería de cola de prioridad (`heapq` o equivalente): investigar e incluir en el análisis (`push`/`pop` O(log n)).

## Verificación
- Casos 1 a 9 resueltos a mano.
- Entre versiones: igualdad de tiempos en todos los pares medidos con ambas (exigido por el enunciado).
- Contra NetworkX (`single_source_dijkstra_path_length`), solo en pruebas.
- Suma de pesos de la ruta devuelta = tiempo reportado.

## Medición
- Qué: tiempo de `dijkstra(...)` solamente (sin leer el grafo ni escribir resultados) y `nodos_explorados` de cada consulta. **La inicialización de los arreglos (O(V) por consulta) queda dentro de la medición** porque es parte del algoritmo, y la discusión explica el piso de tiempo que produce en la gráfica **[DECISIÓN del documento técnico]**.
- Predicción a contrastar (no es un resultado): en ambas versiones el tiempo debería crecer casi linealmente con los nodos explorados; la pendiente de la lineal depende de V (cada extracción recorre toda la red) y la de la cola del grado promedio y log V, así que el cociente lineal/cola debería crecer con los nodos explorados mientras domine el piso de inicialización.
- Pares: ≥ 20 pares origen-destino del catálogo con la versión de cola; 10 de esos pares, entre lugares cercanos (mismo municipio o vecinos), también con la lineal.
- Protocolo: 5 repeticiones y mediana; si una consulta pasa de 1 min se mide una sola vez; si pasa de 5 min se detiene y se marca "no completada". Pares elegidos con semilla fija documentada. Tiempo en ms. Mismo equipo para todo el requerimiento; reportar CPU, RAM, SO y versión del lenguaje.
- Reportar el cociente lineal / cola (mediana, mínimo, máximo) en los 10 pares comunes, y comentar si la gráfica de tiempo vs. nodos explorados coincide con lo que predice la teoría.

## Decisiones
Resuelta: el lenguaje es Python, así que la cola es `heapq`.

Propuestas del documento técnico, pendientes de confirmar: inicialización dentro de la medición; tolerancia de 0,001 s.

Abiertas:
- Cómo elegir los 20 y 10 pares (criterio y semilla).
- Reportar en el informe cuántos pares (i, j) de la matriz difieren de (j, i) y la mayor diferencia.

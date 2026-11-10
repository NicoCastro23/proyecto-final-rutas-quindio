# Modelo de la red vial — Requerimiento 1
Enunciado: sección 4 (Datos) y sección 5, Requerimiento 1 (puntos 1 a 5); formato en Anexo, Requerimiento 1; protocolo de la sección 6. Peso: 15 % (40 % implementación verificada, 30 % teoría, 30 % experimental).
Estado: ☑ spec (aprobada en Puerta 1, 2026-11-10, con precisiones de aristas paralelas y pesos sin redondear) · ☐ pruebas · ☐ código · ☐ verificado

## Propósito
Descargar la red vial del Quindío, modelarla como grafo ponderado (distancia y tiempo), quedarse con la componente fuertemente conexa más grande, ubicar el catálogo de lugares sobre ella y guardar todo para que R2 a R5 no vuelvan a descargar nada.

## Versiones fijadas
Python 3.13.8, **OSMnx 2.1.1**, **NetworkX 3.7** (las del `.venv`; se fijan en `requirements.txt` junto con pyproj, SciPy, pandas, numpy y pytest). La versión de NetworkX determina el algoritmo de componentes (ver punto 3): si alguien la cambia, se actualiza esta spec.

## Entradas y salidas
**Entradas**
- Red del departamento: `ox.graph_from_place("Quindío, Colombia", network_type="drive", retain_all=True)`. Se registran versión de OSMnx y **fecha de descarga**, y se comprueba que el polígono geocodificado sea el departamento (no un municipio). Plan B: GraphML entregado por el docente; el código acepta una ruta a GraphML en lugar de descargar.
- Redes de escalamiento: `ox.graph_from_point(PLAZA_BOLIVAR, dist=r, network_type="drive", retain_all=True)` con r = 2 000, 5 000, 10 000 y 20 000 m; `PLAZA_BOLIVAR` = coordenadas de C01 en el catálogo. **Decisiones del grupo:**
  - `network_type="drive"` en **todas** las descargas (en `graph_from_point` el defecto es `"all"`).
  - `retain_all=True` en **todas** las descargas: la "red descargada" es la red cruda, no la mayor componente débilmente conexa (lo que haría el defecto `retain_all=False`). Así la tabla antes/después es honesta y `largest_component` hace todo su trabajo.
  - `dist_type="bbox"` (defecto): el "radio" r es un cuadrado de lado 2r (2 km ≈ 4 × 4 km). Se aclara en el informe.
  - El cuadrado de 20 km puede salirse del departamento: esa red no tiene por qué ser menor que la completa. La tabla se analiza por V + E, no por el nombre de la fila.
  - `simplify=True` (defecto de OSMnx): los nodos son intersecciones y extremos de vía.
- Catálogo `data/catalogo.csv` (lo exporta el grupo de la hoja "Catalogo"): columnas `id, nombre, municipio, categoria, latitud, longitud, duracion_visita_min, fuente_duracion, mapa, verificado, notas`. **42 lugares**: 12 cabeceras (C01–C12), 15 atractivos (A01–A15), 9 fincas (F01–F09), 6 trilladoras (T01–T06). Coordenadas de Google Places consultadas el 2 de noviembre de 2026, todas verificadas en mapa. `C01` (plaza de Bolívar de Armenia) es la partida por defecto. `duracion_visita_min` y `fuente_duracion` solo se llenan en atractivos, con estos criterios:
  1. Fuente directa de la duración (si es rango, punto medio).
  2. Parque de día completo: tiempo entre apertura y cierre.
  3. Visita corta: 30 min mirador o monumento; 60 min museo o casa.
  4. Estimación del grupo sin fuente (A12 Ecoparque Peñas Blancas, 180 min), a reemplazar si aparece una fuente.

**Salidas** (bajo `data/processed/`; resultados de experimentos bajo `results/r1/`)
- `data/processed/grafo_componente.graphml`: MultiDiGraph de la componente, **con todas sus aristas paralelas**. Nodos con `y` (lat), `x` (lon), `x_utm`, `y_utm`; aristas con `length` (m, = distancia), `speed_kph`, `travel_time` (s), `highway`, `maxspeed_original` (bool: si la velocidad vino de OSM). Se guarda con `ox.save_graphml` y se lee con `ox.load_graphml`.
- `data/processed/lugares_nodos.csv`: `id_lugar, id_nodo, distancia_al_nodo_m, alerta_500m`.
- `data/processed/metadatos.json`: fecha de descarga, versiones, parámetros de descarga, V y E antes y después.
- `results/r1/r1_tamanos.csv`: columnas `red, nodos, aristas` (filas "Red descargada", "Componente fuertemente conexa"), formato del Anexo.
- `results/r1/r1_tiempos_componente.csv`: `red, V, E, V_mas_E, tiempo_ms, tiempo_por_elemento_us, repeticiones`, filas Radio de 2/5/10/20 km y Departamento completo (columnas del Anexo ampliadas, no reducidas).
- `results/r1/r1_memoria.csv`: `representacion, supuesto, bytes, MB` con los V y E reales de la componente.
- `results/r1/r1_velocidades.csv`: porcentaje de aristas con `maxspeed` de OSM y porcentaje imputado, por tipo de vía.
- `results/r1/maquina.json`: procesador, RAM, SO, versión de Python.
- Tablas (Markdown) generadas **desde** esos CSV por un script, nunca a mano.

## Comportamiento
1. **Representación (punto 1).** `estimar_memoria(V, E)` devuelve, bajo los supuestos del grupo (cada conexión guarda dos pesos de 8 B —distancia y tiempo, `float64`— y un destino de 8 B; cada nodo una referencia de 8 B a su lista):
   - matriz de adyacencia: `16 · V²` bytes (cada celda: dos `float64`);
   - listas de adyacencia: `24 · E + 8 · V` bytes.
   Se reporta en MB (1 MB = 10⁶ B), se aclara que con objetos de Python el consumo real es mayor (supuesto de un arreglo compacto), y se eligen **listas de adyacencia** por: red dispersa (E crece como V, no como V²); Dijkstra recorre vecinos en O(grado) y la matriz obliga a revisar V celdas por nodo; una celda de matriz guarda una sola conexión y la red conserva aristas paralelas.
2. **Pesos (punto 2).** `travel_time = length / (speed_kph / 3.6)`. Se usan `ox.add_edge_speeds(G, hwy_speeds=VELOCIDADES)` y `ox.add_edge_travel_times(G)`. Orden de OSMnx 2.1.1 (verificado en `osmnx/routing.py`): (a) `maxspeed` de OSM si es numérico (mph → km/h con 1,60934; lista → promedio; `"none"`, `"signals"` y otros no numéricos → faltante; no hay velocidades implícitas para Colombia); (b) si falta, el valor de `hwy_speeds` del tipo; (c) tipo no presente en la tabla → promedio de `maxspeed` observado de ese tipo; (d) sin observaciones → promedio general. Si `highway` es una lista, OSMnx usa el primer elemento. **Tabla del grupo** (por debajo de los máximos del Código Nacional de Tránsito, arts. 106 y 107, por ser zona montañosa); cada `*_link` toma la velocidad de su tipo padre:

   | `highway` en OSM | km/h |
   |---|---|
   | motorway, motorway_link, trunk, trunk_link | 80 |
   | primary, primary_link | 60 |
   | secondary, secondary_link | 50 |
   | tertiary, tertiary_link | 40 |
   | unclassified, residential, road | 30 |
   | living_street, service, track | 20 |

   Todo tramo termina con velocidad finita > 0 (se comprueba; si no, error). Se reportan porcentajes con `maxspeed` de OSM e imputados. El tiempo es una estimación del modelo (sin tráfico, pendientes ni estado de la vía).
   - **Aristas paralelas: se conservan todas** (decisión del grupo). Dijkstra (R2) las relaja todas y queda la de menor tiempo de forma natural.
   - **Arista elegida entre paralelas (precisión de la Puerta 1):** R1 expone una única función `mejor_arista(G, u, v)` que devuelve, entre todas las aristas u→v, la de **menor `travel_time`** (empate: menor `key`) con **su propia** `length`, `travel_time` y `geometry` (si no tiene `geometry`, el segmento recto entre u y v). R2 la usa para reconstruir la ruta (tiempo y distancia de la ruta = suma sobre esas aristas) y R5 para dibujarla, de modo que coincidan. Nunca se mezcla la distancia de una arista con el tiempo o la geometría de otra.
3. **Componente (punto 3).** `ox.truncate.largest_component(G, strongly=True)`. En OSMnx 2.1.1: (i) `nx.is_strongly_connected(G)`; (ii) si no lo es, `max(nx.strongly_connected_components(G), key=len)`; (iii) `nx.MultiDiGraph(G.subgraph(cc))`. En **NetworkX 3.7**, `strongly_connected_components` es una versión **iterativa del algoritmo de Tarjan con las mejoras de Tarjan y Zwick** (2024), con un truco tomado de WebGraph (docstring de `networkx/algorithms/components/strongly_connected.py`). El informe explica brevemente cómo funciona: DFS que asigna a cada nodo su número de preorden y su `lowlink` (el menor preorden alcanzable por aristas de árbol más una de retroceso/cruce dentro de la pila); cuando un nodo termina con `lowlink` igual a su preorden, es raíz de una componente y se sacan de la pila sus nodos. **Lo medido incluye los tres pasos.** Si una red ya fuera fuertemente conexa, (ii) y (iii) no se ejecutan; decirlo en la discusión.
   - **Por qué conviene la componente** (párrafo del informe): entre dos nodos de la componente siempre existe ruta en ambos sentidos, así que Dijkstra (R2) siempre llega al destino, la matriz de tiempos 42 × 42 no tiene infinitos y todo recorrido de R4 es factible; sin ella, un lugar asociado a un nodo sin salida (o sin entrada) daría tiempos infinitos.
4. **Ubicación de lugares (punto 4).** Lugares y nodos → UTM zona 18N (EPSG:32618) con `pyproj` (`always_xy=True`), indicando la proyección explícitamente. Cada lugar se asocia al nodo de la componente con menor distancia euclidiana en metros, con búsqueda lineal propia O(P · V). Empate: menor `id_nodo`. Si distancia > 500 m: `alerta_500m = true` y se reporta. **Decisión del grupo:** como los 42 lugares están verificados en mapa, los alertados **se conservan** con su alerta y distancia, y el informe explica por qué la vía no llega más cerca. Referencia de una corrida anterior (no es prueba estricta: depende de la fecha de descarga): A03 Valle de Cocora ≈ 1 054 m (la vía llega al parqueadero), A10 RECUCA ≈ 539 m (dentro de una finca), A11 Cascadas del Río Verde ≈ 1 473 m (se entra a pie).
5. **Grafo procesado (punto 5).** Guardar componente, pesos y asociaciones; reportar V y E antes y después de filtrar (E cuenta aristas del MultiDiGraph, paralelas incluidas). Cargar los archivos guardados sin internet debe dar el mismo grafo (V, E, pesos) y las mismas asociaciones. **Los pesos se guardan sin redondear** (precisión de la Puerta 1): `length`, `speed_kph`, `travel_time`, `x_utm`, `y_utm` y `distancia_al_nodo_m` se escriben con su representación completa de `float` (no se llama a `round` ni se usa un formato con pocos decimales; verificado: `osmnx/routing.py` e `io.py` de OSMnx 2.1.1 no redondean, a diferencia de versiones 1.x; una prueba comprueba que `travel_time` guardado = `length / (speed_kph / 3.6)` con tolerancia 1e-9 y que `save_graphml`/`load_graphml` devuelve exactamente el mismo `float`). Al cargar, los atributos numéricos se convierten de nuevo a `float`.
6. **Catálogo (sección 4).** Validación al cargar: 42 filas; conteos por categoría exactamente (12, 15, 9, 6), que cumplen los mínimos (12, 15, 8, 5); `id` únicos; categoría dentro de las 4; todo atractivo con `duracion_visita_min > 0` y `fuente_duracion` con criterio 1 a 4; `verificado = TRUE` en todas; coordenadas dentro del recuadro lat 4,0 a 4,9 y lon −76,0 a −75,4. Cualquier violación → error con mensaje que diga la fila y la regla.

## Casos borde
- Arista sin `maxspeed` ni `highway` de la tabla → la imputa OSMnx (promedio), nunca 0 ni `NaN`; se comprueba velocidad finita > 0 en todas.
- `maxspeed = ["30", "50"]` → 40 km/h. `maxspeed = "none"` o `"signals"` → faltante, usa la tabla.
- `highway = ["residential", "tertiary"]` → usa `residential` (primer elemento).
- Aristas paralelas → se conservan; el GraphML las guarda con su `key`.
- Arista de longitud 0 → `travel_time = 0` (se conserva; Dijkstra admite pesos 0).
- Lugar exactamente sobre un nodo → distancia 0.
- Dos nodos equidistantes → gana el menor `id_nodo`.
- Lugar a > 500 m → alertado y reportado, nunca descartado en silencio.
- Red ya fuertemente conexa → `largest_component` la devuelve igual.
- Descarga falla → se usa el GraphML del docente.
- Catálogo con `id` repetido, categoría inválida, conteo distinto o coordenada fuera del recuadro → error claro.

## Casos de prueba
1. Memoria, V = 1 000, E = 2 500 → matriz 16 000 000 B (16 MB); listas 24 × 2 500 + 8 × 1 000 = 68 000 B (0,068 MB).
1b. Memoria, V = 30 000, E = 75 000 → matriz 14 400 000 000 B (14 400 MB); listas 1 800 000 + 240 000 = 2 040 000 B (2,04 MB).
2. Tiempo: 1 000 m a 36 km/h → 100 s.
3. Tiempo: 500 m con `maxspeed = "30 mph"` → 48,2802 km/h → ≈ 37,28 s (tolerancia 0,1 s).
4. Tiempo, grafo sintético sin `maxspeed`, 1 000 m: `residential` → 120 s; `primary` → 60 s; `primary_link` → 60 s; `track` → 180 s.
4b. `maxspeed = ["30", "50"]`, 1 000 m → 40 km/h → 90 s. `maxspeed = "none"`, `highway = tertiary`, 1 000 m → 40 km/h → 90 s.
4c. Aristas paralelas: grafo con dos aristas A→B (claves 0 y 1, tiempos 50 s y 40 s) → tras pesos, componente y guardar/cargar, siguen existiendo las 2 aristas con sus tiempos.
5. Componente: aristas A→B, B→C, C→A, C→D, D→E → componente {A, B, C}: 3 nodos, 3 aristas. Igual a `max(nx.strongly_connected_components)`.
6. Componente: grafo ya fuertemente conexo (ciclo A→B→C→A) → mismos V = 3 y E = 3.
7. Vecino más cercano (coordenadas UTM): lugar (100, 100); nodos 1 en (103, 104) y 2 en (200, 100) → nodo 1, 5,0 m, `alerta_500m = false`.
8. Alerta: lugar (0, 0); único nodo en (600, 0) → 600 m, `alerta_500m = true`. Frontera: nodo a exactamente 500 m → `false`.
9. Empate: nodos 7 y 3 a la misma distancia → 3.
10. UTM: para C01, A03 y A10 del catálogo, `x_utm, y_utm` coinciden con `pyproj` EPSG:4326 → EPSG:32618 (< 1 mm) y la ida y vuelta da error < 1 m; con el recuadro del caso 12, x_utm cae entre ≈ 389 000 y 456 000 m e y_utm entre ≈ 442 000 y 542 000 m (el Quindío está al oeste del meridiano central −75°, por eso x < 500 000; p. ej. lon −75,6716, lat 4,5339 → (425 498, 501 177)).
11. Persistencia: guardar y cargar → mismos V, E, suma de `travel_time` (tolerancia 1e-6), cada `travel_time` y `length` igual arista por arista (tolerancia 1e-9, pesos sin redondear) y `lugares_nodos.csv` idéntico.
11b. Arista elegida: con las aristas paralelas del caso 4c (A→B, clave 0: 50 s y 800 m; clave 1: 40 s y 900 m con geometría propia) → `mejor_arista(G, A, B)` devuelve clave 1, 40 s, 900 m y su geometría. Empate en tiempo → menor `key`. Sin `geometry` → segmento recto A–B.
12. Catálogo real (`data/catalogo.csv`): 42 filas, conteos (12, 15, 9, 6), ids únicos, 15 atractivos con duración > 0 y fuente, todas verificadas, coordenadas dentro del recuadro (Cocora lon −75,489 y PANACA −75,819 adentro). Catálogos sintéticos con un id repetido, una categoría inválida o una latitud 5,5 → error.
13. Parámetros de descarga: con la función de descarga sustituida por un doble (mock), las 5 descargas se piden con `network_type="drive"` y `retain_all=True`; la prueba falla si alguna usa los valores por defecto.
14. Velocidades: en el grafo procesado real, toda arista tiene `speed_kph` finito > 0 y `travel_time` = `length / (speed_kph / 3.6)` (tolerancia 1e-6).
15. Asociación real: los 42 lugares tienen nodo y ese nodo pertenece a la componente; la distancia propia coincide con `scipy.spatial.cKDTree` (< 1e-6 m) para todos.

## Complejidad esperada
- Memoria de la representación: matriz Θ(V²); listas Θ(V + E).
- Componentes fuertemente conexas: Θ(V + E) en tiempo y Θ(V) de memoria adicional (diccionario `lowlink`, pilas DFS y de componente). Fuentes: R. E. Tarjan, «Depth-first search and linear graph algorithms», *SIAM J. Computing* 1(2):146–160, 1972; R. E. Tarjan y U. Zwick, «Finding strong components using depth-first search», *European J. Combinatorics* 119, 2024, doi:10.1016/j.ejc.2023.103815; código de NetworkX 3.7 (`networkx/algorithms/components/strongly_connected.py`) y OSMnx 2.1.1 (`osmnx/truncate.py`). `largest_component` completo también es Θ(V + E): `is_strongly_connected` y la construcción del subgrafo son lineales y `max` recorre las componentes una vez.
- Pesos: Θ(E). Conversión UTM: Θ(V + P).
- Vecino más cercano por búsqueda lineal: Θ(P · V) tiempo y Θ(1) adicional, con P = 42 (con V del orden de decenas de miles son ~10⁶ operaciones: suficiente, no se necesita índice espacial).

## Verificación
- Casos 1 a 9 resueltos a mano (arriba).
- Componente: igual a `nx.strongly_connected_components` (la más grande) en los casos 5 y 6 y en la red de radio 2 km.
- Vecino más cercano: contra `scipy.spatial.cKDTree` (solo en pruebas), caso 15.
- UTM: contra `pyproj`, caso 10.
- Catálogo: coordenadas ya revisadas en mapa por el grupo; validación automática del caso 12.

## Medición (sección 6)
- Qué: solo la llamada `ox.truncate.largest_component(G, strongly=True)`; la red se descarga y carga antes del cronómetro (`time.perf_counter_ns`), y se pasa una copia nueva en cada repetición por si la función mutara algo.
- Redes: radios 2, 5, 10 y 20 km y departamento completo, todas con `retain_all=True`.
- 5 repeticiones, mediana, en **ms**; si una repetición pasa de 1 min se mide una vez; si pasa de 5 min se reporta "no completada".
- Misma máquina para todo R1; se guardan procesador, RAM, SO y versión de Python en `maquina.json`.
- Análisis: columna `tiempo_por_elemento_us` = tiempo / (V + E) en µs, que debe ser aproximadamente constante si el tiempo es lineal. Párrafo de discusión que compare esa razón entre filas y explique desviaciones (redes pequeñas dominadas por costos fijos, caché, red ya conexa).
- Sin datos aleatorios en R1 (no aplica semilla).

## Pendientes para el documento técnico
Tabla antes/después, tabla de tiempos, estimación de memoria con la elección justificada, explicación del algoritmo de componentes con sus fuentes, tratamiento de velocidades con porcentajes, lugares a > 500 m con su explicación, párrafo de por qué conviene la componente, fecha de descarga. Uso de IA anotado en `docs/anexo-ia.md`.

## Decisiones
Resueltas por el grupo: Python 3.13; OSMnx 2.1.1 y NetworkX 3.7 fijadas; listas de adyacencia; tabla de velocidades de arriba con `*_link` = tipo padre y `road` = 30; aristas paralelas conservadas; `network_type="drive"` y `retain_all=True` en todas las descargas; `dist_type="bbox"` aclarado; lugares a > 500 m conservados y reportados; catálogo de 42 lugares (12, 15, 9, 6) exportado a `data/catalogo.csv`; criterios 1 a 4 de duración de visita.

Abierta (no bloquea): fuente para A12 (Ecoparque Peñas Blancas, hoy estimación del grupo, criterio 4).

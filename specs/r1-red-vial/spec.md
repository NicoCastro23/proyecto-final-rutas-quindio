# Modelo de la red vial — Requerimiento 1
Enunciado: sección 4 (Datos) y sección 5, Requerimiento 1 (puntos 1 a 5); formato en Anexo, Requerimiento 1. Peso: 15 %.
Estado: ☐ spec (borrador, pendiente de aprobación del grupo) · ☐ pruebas · ☐ código · ☐ verificado

## Propósito
Descargar la red vial del Quindío, modelarla como grafo ponderado (distancia y tiempo), quedarse con la componente fuertemente conexa más grande, ubicar el catálogo de lugares sobre ella y guardar todo para que R2 a R5 no vuelvan a descargar nada.

## Entradas y salidas
**Entradas**
- Red OSM: `ox.graph_from_place("Quindío, Colombia", network_type="drive")` (OSMnx 2.1.1; registrar versión y **fecha de descarga**; comprobar que el polígono sea el departamento). Plan B: GraphML entregado por el docente.
- Redes de escalamiento: `ox.graph_from_point` centrada en la plaza de Bolívar de Armenia con radios 2, 5, 10 y 20 km. Valores por defecto de OSMnx 2.1.1 que afectan los datos (`documento técnico`, sección Datos):
  - `network_type` en `graph_from_point` es `"all"` por defecto: se pasa `network_type="drive"` en **todas** las descargas.
  - `dist_type` es `"bbox"`: el "radio" es un cuadrado (2 km cubre ≈ 4 × 4 km). Se mantiene y se aclara. **[DECISIÓN, confirmar]**
  - `retain_all=False`: la "red descargada" ya es la mayor componente débilmente conexa, no la red cruda. Se aclara en la tabla de R1 o se pasa `retain_all=True`. **[DECISIÓN, confirmar]**
  - El cuadrado de 20 km puede salirse del departamento: esa red no tiene por qué ser menor que la completa. Las tablas se analizan por V + E, no por el nombre de la fila.
- Catálogo `data/catalogo.csv`, exportado de la hoja "Catalogo" del Google Sheet del grupo (Archivo > Descargar > CSV): `id, nombre, municipio, categoria, latitud, longitud, duracion_visita_min, fuente_duracion, mapa, verificado, notas`. La pestaña "Criterios y control" declara **42 lugares** (12 cabeceras C01–C12, 15 atractivos A01–A15, 9 fincas F01–F09, 6 trilladoras), pero la lectura de la pestaña "Catalogo" solo muestra T01–T05 (41 filas con datos). **Discrepancia a resolver al exportar el CSV**: falta una fila T06 o el control cuenta una de más; la prueba 12 usa el conteo real del CSV. Coordenadas de Google Places consultadas el 2 de noviembre de 2026, todas verificadas en mapa. `C01` (plaza de Bolívar de Armenia) es la partida por defecto. `duracion_visita_min` y `fuente_duracion` solo se llenan en atractivos, con estos criterios:
  1. Fuente directa de la duración (si es rango, punto medio).
  2. Parque de día completo: tiempo entre apertura y cierre.
  3. Visita corta: 30 min mirador o monumento; 60 min museo o casa.
  4. Estimación del grupo sin fuente (A12 Ecoparque Peñas Blancas, 180 min), a reemplazar si aparece una fuente.

**Salidas** (todas bajo `data/processed/`, formatos reproducibles; si los algoritmos no están en Python se exportan a archivos legibles desde su lenguaje)
- `grafo_componente.graphml` (o equivalente): nodos con `lat`, `lon`, `x_utm`, `y_utm`; aristas con `distancia_m`, `velocidad_kmh`, `tiempo_s`, `highway`.
- `lugares_nodos.csv`: `id_lugar, id_nodo, distancia_al_nodo_m, alerta_500m`.
- `r1_tamanos.csv` (tabla "antes/después") y `r1_tiempos_componente.csv` (tabla de escalamiento), con las columnas del Anexo; `r1_memoria.csv` con la estimación de memoria.

## Comportamiento
1. **Representación (punto 1).** Con V y E reales, `estimar_memoria(V, E)` devuelve, bajo los supuestos del grupo (dos pesos de 8 B por conexión —distancia y tiempo— y un destino de 8 B):
   - matriz de adyacencia: `16 · V²` bytes;
   - listas de adyacencia: `24 · E + 8 · V` bytes.
   El informe reporta MB (1 MB = 10⁶ B), avisa de que con listas de objetos de Python el consumo real es mayor, y elige **listas de adyacencia** por tres razones: red dispersa (E crece como V, no como V²); Dijkstra recorre los vecinos en O(grado), la matriz obliga a revisar V celdas; una celda de matriz guarda una sola conexión y la red puede tener aristas paralelas.
2. **Pesos (punto 2).** `tiempo_s = distancia_m / (velocidad_kmh / 3.6)`. La velocidad se obtiene con `ox.add_edge_speeds` y el tiempo con `ox.add_edge_travel_times` (OSMnx 2.1.1), que aplican este orden: (a) `maxspeed` de OSM si existe (mph → km/h); (b) si no, el valor de `hwy_speeds` para su tipo de vía; (c) si el tipo no está, el promedio de los `maxspeed` de ese tipo; (d) si no hay ninguno, `fallback` o, sin él, el promedio de todos los tipos. Se pasa una **tabla propia `hwy_speeds`** (criterio del grupo, por debajo de los máximos legales del Código Nacional de Tránsito, arts. 106 y 107, porque la zona es montañosa) **[DECISIÓN, confirmar con el equipo]**:

   | `highway` en OSM | km/h |
   |---|---|
   | motorway, trunk | 80 |
   | primary | 60 |
   | secondary | 50 |
   | tertiary | 40 |
   | unclassified, residential | 30 |
   | living_street, service, track | 20 |

   Todo tramo termina con velocidad > 0. Se reporta el porcentaje de aristas con `maxspeed` en OSM y el porcentaje imputado. El tiempo es una estimación del modelo (sin tráfico, pendientes ni estado de la vía).
   - **Aristas paralelas:** OSMnx entrega un MultiDiGraph; para el modelo de rutas se conserva, entre cada par de nodos y sentido, la arista de **menor tiempo**, con su distancia y geometría juntas.
3. **Componente (punto 3).** `ox.truncate.largest_component(G, strongly=True)`. En OSMnx 2.1.1 hace tres pasos: `nx.is_strongly_connected(G)` (termina antes si basta la primera componente); si no lo es, recorre todas las componentes y toma la mayor con `max(..., key=len)`; construye un MultiDiGraph nuevo. **Lo medido incluye los tres pasos** (si la red ya es fuertemente conexa no se ejecutan los pasos 2 y 3 y el tiempo cambia: decirlo en la discusión). El algoritmo de NetworkX **depende de la versión**: 2.8.8, 3.2.1, 3.4.2, 3.5 y 3.6.1 usan Tarjan con las modificaciones de Nuutila; 3.7 usa Tarjan iterativo con mejoras de Tarjan y Zwick. Se **fija la versión de NetworkX en `requirements.txt`** y el informe conserva solo la fila que aplique. Se mide en las 4 redes por radio y en la red completa; la tabla agrega la columna `tiempo / (V+E)` en µs, que debería ser casi constante si el algoritmo es lineal.
4. **Ubicación de lugares (punto 4).** Coordenadas del lugar y de los nodos → UTM zona 18N (EPSG:32618), indicando la proyección de forma explícita con `to_crs` (`ox.project_graph` sin argumento elige la proyección por su cuenta). Cada lugar se asocia al nodo de la componente con menor distancia euclidiana en metros. Empate: menor `id_nodo`. Si la distancia > 500 m: `alerta_500m = true`, se reporta con su distancia y **[DECISIÓN]** si el lugar está bien ubicado se conserva y se reporta; si la coordenada estaba mal, se corrige y se documenta.
5. **Grafo procesado (punto 5).** Guardar componente, pesos y asociaciones. Reportar V y E antes y después de filtrar. Cargar el archivo guardado debe dar un grafo idéntico (mismos V, E y pesos) sin red de internet.
6. **Catálogo.** ≥ 40 lugares (hoy 41 o 42, ver discrepancia): 12 cabeceras municipales (plaza principal; Armenia = plaza de Bolívar, partida por defecto), ≥ 15 atractivos, ≥ 8 fincas/hoteles rurales, ≥ 5 centros de acopio/trilladoras. `id` único; todo atractivo con `duracion_visita_min > 0` y `fuente_duracion` con su criterio (1 a 4); `verificado = TRUE` en todas las filas.

## Casos borde
- Arista sin `maxspeed` ni `highway` reconocible → la imputa OSMnx (promedio o `fallback`), nunca 0 ni `NaN`.
- `maxspeed = ["30", "50"]` → lo resuelve `ox.add_edge_speeds`; verificar el valor resultante en una prueba y documentarlo.
- `maxspeed = "none"` o `"signals"` → tratada como faltante.
- Aristas paralelas entre dos nodos → queda la de menor tiempo.
- Arista de longitud 0 → `tiempo_s = 0` (se conserva; Dijkstra admite pesos 0).
- Lugar exactamente sobre un nodo → distancia 0.
- Dos nodos equidistantes al lugar → gana el menor `id_nodo`.
- Lugar a > 500 m → alertado y reportado, no descartado en silencio.
- Descarga falla → usar el GraphML del docente; el código lo acepta como entrada.
- Catálogo con `id` repetido, categoría fuera de las 4, o coordenadas fuera del departamento → falla con mensaje claro.

## Casos de prueba
1. Memoria, V = 1 000, E = 2 500 → matriz = 16 × 1 000² = 16 000 000 B (16 MB); listas = 24 × 2 500 + 8 × 1 000 = 68 000 B (0,068 MB).
1b. Memoria, V = 30 000, E = 75 000 (ejemplo del documento técnico, solo para mostrar escala) → matriz = 14 400 MB; listas = 2,04 MB.
2. Tiempo: 1 000 m a 36 km/h (10 m/s) → 100 s.
3. Tiempo: 500 m a `"30 mph"` (48,28 km/h ≈ 13,41 m/s) → ≈ 37,3 s (tolerancia 0,1 s).
4. Tiempo: 1 000 m, sin `maxspeed`, `highway = residential` y la tabla `hwy_speeds` del grupo (30 km/h) → 120 s; con `highway = primary` (60 km/h) → 60 s; nunca infinito.
4b. Aristas paralelas: dos aristas A→B con tiempos 50 s y 40 s → queda la de 40 s con su propia distancia.
5. Componente: grafo dirigido de 5 nodos con aristas A→B, B→C, C→A, C→D, D→E (D y E no regresan) → la componente fuerte más grande es {A, B, C}: 3 nodos, 3 aristas.
6. Componente: grafo ya fuertemente conexo → devuelve los mismos V y E.
7. Vecino más cercano: lugar en (100, 100) m; nodos en (103, 104) y (200, 100) → elige el primero a 5,0 m; `alerta_500m = false`.
8. Alerta: lugar en (0, 0); único nodo en (600, 0) → distancia 600 m, `alerta_500m = true`.
9. Empate: nodos 7 y 3 a la misma distancia → elige 3.
10. Conversión UTM: los valores esperados se calculan con `pyproj` (EPSG:4326 → EPSG:32618) para 3 lugares del catálogo, e ida y vuelta con error < 1 m.
11. Persistencia: guardar y volver a cargar → mismos V, E, suma de `tiempo_s` y asociaciones idénticas.
12. Catálogo (`data/catalogo.csv`): cuenta por categoría ≥ (12, 15, 8, 5) y coincidentes con la pestaña de control (12, 15, 9, 6 según ella; ver discrepancia arriba); total ≥ 40; ids únicos; los 15 atractivos con `duracion_visita_min > 0` y `fuente_duracion`; ninguna fila con `verificado` distinto de TRUE; coordenadas dentro de un recuadro razonable del Quindío (lat 4,0 a 4,9; lon −76,0 a −75,4). El valle de Cocora (lon −75,489) y PANACA (−75,819) caen dentro; un recuadro que termine en −75,5 excluiría Cocora.
13. Parámetros de descarga: las 4 redes por radio se piden con `network_type="drive"`; una prueba falla si alguna descarga usa el valor por defecto `"all"`.

## Complejidad esperada
- Matriz: Θ(V²) memoria; listas: Θ(V + E) memoria.
- Componentes fuertemente conexas: Θ(V + E) tiempo y Θ(V) memoria adicional (diccionarios y pilas). Fuentes: Tarjan, «Depth-first search and linear graph algorithms», *SIAM J. Computing* 1(2), 1972; Nuutila y Soisalon-Soininen, *Information Processing Letters* 49(1), 1994; Tarjan y Zwick, «Finding strong components using depth-first search», *European J. Combinatorics* 119, 2024 (solo si NetworkX ≥ 3.7); y el código de la versión de NetworkX/OSMnx usada (citar versión y enlace).
- Vecino más cercano ingenuo: O(P · V) con P lugares (≈ 40), suficiente; si se usa índice espacial, citar su costo.

## Verificación
- Casos 1 a 9 resueltos a mano (arriba).
- Componente: comparar con `nx.strongly_connected_components` y verificar a mano en el grafo pequeño del caso 5.
- Vecino más cercano: comparar con `scipy.spatial.cKDTree` (solo en pruebas).
- Mapa: revisar visualmente las coordenadas del catálogo.

## Medición
Qué: tiempo de `largest_component(strongly=True)` (solo esa llamada) en radios 2, 5, 10, 20 km y departamento completo. 5 repeticiones, mediana, ms; la red se descarga y construye antes del cronómetro. Reportar procesador, RAM, SO y versión del lenguaje. Comprobar si el tiempo crece como V + E (razón tiempo/(V+E) aproximadamente constante).

## Decisiones
Resueltas por el grupo (en el documento técnico y en el catálogo): lenguaje **Python** (todo el proyecto, descarga y algoritmos, sin archivos de intercambio entre lenguajes); listas de adyacencia; criterios 1 a 4 de duración de visita; descarga con `network_type="drive"`.

Propuestas, pendientes de confirmar:
- Tabla de velocidades por `highway` (arriba).
- `dist_type="bbox"` (radio como cuadrado) y `retain_all` (False con aclaración, o True).
- Tratamiento de lugares a > 500 m.

Abiertas:
- Versión exacta de NetworkX y OSMnx a fijar en `requirements.txt` (la de NetworkX cambia la respuesta sobre qué algoritmo de componentes se usa).
- Fuente para A12 (Ecoparque Peñas Blancas, hoy estimación del grupo).

# Revisión — R1 Modelo de la red vial

Fuentes contrastadas: `CLAUDE.md`, `estudio/Proyecto final 2026-2.pdf` (secciones 3, 4, 5-R1, 6, 7 y 8), `estudio/Anexo proyecto.pdf` (Requerimiento 1), `spec.md`, `plan.md`, `tasks.md`, el código de `rutas/` y `tests/`, y los artefactos de `data/processed/` y `results/r1/`. Las decisiones del usuario que están en la spec (paralelas conservadas, `retain_all=True`, `dist_type="bbox"`, tabla de velocidades con `ladder` = 20, pesos sin redondear, memoria con 4 filas, `data/raw` fuera de git, reintentos 502/504, medición en el mismo proceso, lugares a > 500 m conservados, `docs/` ignorado) se respetan y no se reabren.

## Ronda 1: APROBADO

Pruebas: ✅
- `.venv/bin/python -m pytest -q` → **112 passed in 6.61s** (incluye las 8 `red` con los datos reales; ninguna saltada).
- `.venv/bin/python -m pytest -m "not red" -q` → **104 passed, 8 deselected in 3.07s**.

Comprobaciones adicionales del revisor (solo lectura, sin regenerar nada):
- `grep` de imports en `rutas/`: `networkx` aparece solo en `construir_red.py`, `descargar.py` y `medir_componente.py` para versiones e `is_strongly_connected` informativo **fuera** del cronómetro; `shapely` solo como contenedor de geometría en `aristas.py`; `scipy`/`cKDTree` solo en `tests/test_red_real.py`. La búsqueda del vecino más cercano (`rutas/r1/ubicacion.py:10-22`) es lineal y propia. Sin uso indebido de librerías.
- Código de las versiones fijadas: `osmnx/truncate.py` (2.1.1) hace exactamente `is_strongly_connected` → `max(strongly_connected_components, key=len)` → `nx.MultiDiGraph(G.subgraph(cc))`; el docstring de `networkx/algorithms/components/strongly_connected.py` (3.7) dice "Iterative version of Tarjan's algorithm using the improvements described by Tarjan and Zwick … plus a trick borrowed from … WebGraph". Coincide con la spec.
- Leí las 5 redes crudas de `data/raw/`: **ninguna** es fuertemente conexa (20, 38, 39, 48 y 41 componentes), así que en las 5 filas de la tabla de tiempos se ejecutaron los tres pasos de `largest_component`. La mayor componente del departamento (8 791 nodos) coincide con `r1_tamanos.csv`.

| Caso / punto del enunciado | Cumplido | Test |
|---|---|---|
| Caso 1 (V=1 000, E=2 500 → 16 000 000 B / 68 000 B) | ✅ | `tests/test_memoria.py::test_caso_1_v1000_e2500` |
| Caso 1b (V=30 000, E=75 000 → 14 400 000 000 B / 2 040 000 B) | ✅ | `tests/test_memoria.py::test_caso_1b_v30000_e75000` |
| Caso 2 (1 000 m a 36 km/h → 100 s) | ✅ | `tests/test_pesos.py::test_caso_2_maxspeed_36_da_100s` |
| Caso 3 (500 m, "30 mph" → 48,2802 km/h → 37,28 s) | ✅ | `tests/test_pesos.py::test_caso_3_maxspeed_30mph` |
| Caso 4 (residential 120 s, primary 60 s, primary_link 60 s, track 180 s) | ✅ | `tests/test_pesos.py::test_caso_4_tabla_por_tipo` (4 parámetros) |
| Caso 4b (lista ["30","50"] → 90 s; "none" + tertiary → 90 s) | ✅ | `tests/test_pesos.py::test_caso_4b_maxspeed_lista_y_none` |
| Caso 4c (2 paralelas 50 s / 40 s sobreviven pesos + componente + guardar/cargar) | ✅ | `tests/test_persistencia.py::test_caso_4c_paralelas_sobreviven` |
| Caso 4d (ladder 20 km/h → 180 s; ["residential","ladder"] → 120 s; real: todas a 20) | ✅ | `tests/test_pesos.py::test_caso_4d_ladder_20_kmh`, `tests/test_red_real.py::test_caso_4d_ladder_real_20_kmh` |
| Caso 4e (columnas exactas, residential = 30, ladder = 20, 1 decimal, suma 100 ± 0,1, Total = E componente) | ✅ | `tests/test_construir_red.py::test_caso_4e_formato_de_velocidades_csv`, `::test_velocidades_se_calculan_sobre_la_componente`, `tests/test_pesos.py::test_resumen_ladder_en_tabla` |
| Caso 5 (A→B→C→A, C→D→E → {A,B,C}, 3 y 3, igual a NetworkX) | ✅ | `tests/test_componente.py::test_caso_5_componente_abc` |
| Caso 6 (ciclo ya fuertemente conexo → 3 y 3) | ✅ | `tests/test_componente.py::test_caso_6_ya_fuertemente_conexa` |
| Caso 7 (nodo 1 a 5,0 m) | ✅ | `tests/test_ubicacion.py::test_caso_7_vecino_mas_cercano` |
| Caso 8 (600 m → alerta; 500 m exactos → sin alerta) | ✅ | `tests/test_ubicacion.py::test_caso_8_alerta_y_frontera_500` |
| Caso 9 (empate → menor id, independiente del orden) | ✅ | `tests/test_ubicacion.py::test_caso_9_empate_menor_id` |
| Caso 10 (C01, A03, A10 contra pyproj < 1 mm; ida y vuelta < 1 m; rango; (425 498, 501 177)) | ✅ | `tests/test_utm.py::test_caso_10_*` (3 pruebas) |
| Caso 11 (V, E, suma de tiempos, arista por arista 1e-9, lugares idénticos) | ✅ | `tests/test_persistencia.py::test_caso_11_guardar_cargar_sintetico`, `tests/test_red_real.py::test_caso_11_guardar_cargar_real` |
| Caso 11b (clave 1, 40 s, 900 m, su geometría; empate → menor key; sin geometría → recta) | ✅ | `tests/test_aristas.py::test_caso_11b_*`, `tests/test_persistencia.py::test_caso_11b_tras_guardar_cargar` |
| Caso 12 (catálogo real 42 / 12-15-9-6; id repetido, categoría inválida, lat 5,5 → error) | ✅ | `tests/test_catalogo.py::test_caso_12_*` (+ conteo, duración, verificado, mensaje con fila) |
| Caso 13 (5 descargas con `drive`, `retain_all=True`, `bbox`, centro C01) | ✅ | `tests/test_descarga.py::test_caso_13_parametros_de_las_5_descargas` |
| Caso 14 (red real: velocidad finita > 0 y fórmula ± 1e-6) | ✅ | `tests/test_red_real.py::test_caso_14_velocidades_y_tiempos` |
| Caso 15 (42 lugares en la componente; distancia = cKDTree < 1e-6) | ✅ | `tests/test_red_real.py::test_caso_15_asociacion_contra_ckdtree` |
| Caso 16a–e (reintentos 502/504, esperas 30/60/120/240, rendición con Plan B, 400 sin reintento, script reintenta solo 5 km) | ✅ | `tests/test_descarga.py::test_caso_16a…16e_*` |
| Componente radio 2 km igual a NetworkX | ✅ | `tests/test_red_real.py::test_componente_radio_2km_igual_a_networkx` |
| R1.1 Representación: MB matriz vs listas con supuestos, 2 redes | ✅ | `results/r1/r1_memoria.csv` (4 filas), `tests/test_construir_red.py::test_memoria_cuatro_filas_dos_redes`, `tests/test_red_real.py::test_memoria_real_coincide_con_tamanos` |
| R1.2 Pesos: distancia (m) y tiempo (s) en cada arista; tratamiento de faltantes | ✅ | `rutas/r1/pesos.py`; `results/r1/r1_velocidades.csv` (93,5 % imputado) |
| R1.3 Componente con `largest_component(G, strongly=True)` y medición 2/5/10/20 km + departamento | ✅ | `rutas/r1/componente.py:13`, `results/r1/r1_tiempos_componente.csv`, `tests/test_medir_componente.py::*` |
| R1.4 Ubicación UTM 18N, nodo más cercano, reporte > 500 m | ✅ | `data/processed/lugares_nodos.csv` (A03 1 054 m, A10 539 m, A11 1 473 m), tabla de alertas en `tablas_r1.md` |
| R1.5 Grafo procesado y V/E antes y después | ✅ | `data/processed/*` versionado, `results/r1/r1_tamanos.csv` (8 877/20 245 → 8 791/20 132), `tests/test_red_real.py::test_metadatos_antes_despues` |
| Sección 4: fecha de descarga, polígono = departamento, Plan B GraphML | ✅ | `metadatos.json` (`2026-11-10T13:38:59-05:00`, `addresstype: state`, 1 934,6 km²), `tests/test_descarga.py::test_poligono_*`, `tests/test_construir_red.py::test_pipeline_con_graphml` |
| Sección 6.1 máquina | ✅ | `results/r1/maquina.json` (Apple M5, 16 GB, macOS 26.6.2, Python 3.13.8) |
| Sección 6.2 solo el algoritmo (carga, conteo y copia fuera) | ✅ | `rutas/medicion.py:44-50`, `rutas/r1/medir_componente.py:51-54`, `tests/test_medicion.py::test_en_proceso_preparar_fuera_del_cronometro`, `::test_en_proceso_preparar_en_cada_repeticion` |
| Sección 6.3 5 repeticiones, mediana, una sola si > 1 min | ✅ | `tests/test_medicion.py::test_en_proceso_cinco_repeticiones_y_mediana`, `::test_en_proceso_una_sola_repeticion_si_supera_umbral` |
| Sección 6.4 unidad (ms) | ✅ | columnas `tiempo_ms`, encabezados "(ms)" y "(µs)" (`tests/test_tablas.py::test_unidades_en_encabezados`) |
| Sección 6.5 semilla | n/a | R1 no usa datos aleatorios (documentado en spec) |
| Sección 6.6 verificación antes de medir | ✅ | casos 5, 6 y radio 2 km contra NetworkX |
| Sección 6.7 límite de 5 min / "no completada" | ✅ | `tests/test_medicion.py::test_en_proceso_no_completada_si_supera_limite`, `tests/test_medir_componente.py::test_fila_no_completada`, `tests/test_tablas.py::test_no_completada_se_muestra` |
| Sección 6.8 tablas desde CSV con columnas del anexo (ampliadas) | ✅ | `rutas/r1/tablas.py`, `results/r1/tablas_r1.md`, `tests/test_tablas.py::test_tablas_salen_de_los_csv` |

### Bloqueantes
Ninguno.

### Sugerencias (no bloquean)
- `docs/anexo-ia.md:18`: dice "el tratamiento de aristas paralelas (se conserva la mejor)", pero la spec (punto 2) y el código conservan **todas** las paralelas y `mejor_arista` solo elige una al reconstruir la ruta → corregir la frase para que el anexo no contradiga la spec (el archivo es local por la decisión sobre `docs/`; corregirlo igual antes de pasarlo al documento técnico).
- `specs/r1-red-vial/spec.md:3`: la línea de estado sigue en "☐ pruebas · ☐ código · ☐ verificado" → marcarla según el resultado de esta revisión.
- `specs/r1-red-vial/tasks.md:132`: la marca de T20 está modificada en el árbol de trabajo y no se ha hecho commit (`git status`: `M specs/r1-red-vial/tasks.md`) → hacer el commit.
- `rutas/r1/medir_componente.py:53`: `ya_conexa` solo se imprime; no queda en ningún CSV ni JSON, y `plan.md:241` prometía `ya_fuertemente_conexa` en `metadatos.json` (no existe; `rutas/r1/construir_red.py:65-72`) → o se agrega una columna `ya_fuertemente_conexa` a `r1_tiempos_componente.csv` (y el dato del departamento a `metadatos.json`), o se corrige el plan. Hoy el dato (ninguna de las 5 es fuertemente conexa) solo lo confirma esta revisión, y la spec pide decirlo en la discusión.
- `tests/test_red_real.py`: ninguna prueba `red` lee el `results/r1/r1_velocidades.csv` real. Con agregar una que compruebe `Total.aristas == meta["E_despues"]`, `ladder = 20` y suma 100 ± 0,1, el caso 4e quedaría verificado también sobre el artefacto que va al informe (hoy se cubre con el pipeline sintético).
- `tests/test_catalogo.py:30`: `df["longitud"].max() < -75.48` no comprueba lo que dice el comentario (que Cocora y PANACA estén dentro); lo cubre ya la línea 29 (`between(-76.0, -75.4)`). Conviene buscarlas por id (A03 y PANACA) y comprobar su longitud, o quitar la línea.
- Coherencia `plan.md` ↔ código (el código es lo correcto; actualizar el plan): `plan.md:98` lista las columnas de `resumen_velocidades` sin `velocidad_tabla_kmh`; `plan.md:168` pone `"simplify": True` en `PARAMETROS` (el código usa el valor por defecto, que es el mismo); `plan.md:169` y `:174` dan firmas `centro_plaza_bolivar(catalogo)` y `descargar_radio(centro, dist_m)` distintas de las reales (`rutas/r1/descarga.py:64`, `:103`); `plan.md:20` todavía describe el `.gitignore` inicial.
- `rutas/r1/descarga.py:57`: `raise type(error)(mensaje)` supone que la clase del error acepta un solo argumento de texto. Vale para `ResponseStatusCodeError` y para `requests.HTTPError`, pero no para cualquier excepción. Como solo se llega ahí con 502/504, el riesgo es bajo: basta un comentario que lo diga.
- `metadatos.json` no guarda la versión de Python (sí la guarda `data/raw/descarga.json`, que no se versiona) → copiarla, para que el repositorio registre las tres versiones.
- Opcional para el análisis experimental: una gráfica `tiempo_ms` frente a `V + E` generada desde `r1_tiempos_componente.csv` (el enunciado de R1 solo pide la tabla, pero la gráfica hace evidente la linealidad).

Comentario sobre la complejidad del código: el código es corto, con un módulo por idea, docstrings en español y sin abstracciones de sobra. El único punto delicado es `maxspeed_original` (`rutas/r1/pesos.py:27-36`), que usa funciones privadas de OSMnx. Es una decisión aceptada en la Puerta 2 y está fijada por `test_maxspeed_original`. En la sustentación hay que poder explicar por qué se marca **antes** de imputar. `rutas/medicion.py` incluye el modo con proceso hijo, que R1 no usa: se justifica porque el módulo es compartido con R2 y R4.

### Pendiente para el documento técnico
Esto no bloquea el código. Para la nota de R1 pesa el 60 % (30 % de teoría y 30 % de análisis experimental).
1. **Tabla de tamaños** (desde `tablas_r1.md`) con la fecha de descarga (2026-11-10) y la aclaración de que E cuenta aristas paralelas.
2. **Memoria (punto 1):** los supuestos (16 B por celda, 24 B por arista y 8 B por nodo; 1 MB = 10⁶ B), los números reales (≈ 1 261 MB la matriz frente a ≈ 0,56 MB las listas en la red descargada), la elección de listas de adyacencia con sus tres razones (red dispersa, Dijkstra recorre vecinos en O(grado), la matriz no admite paralelas) y la advertencia de que con objetos de Python el consumo real es mayor.
3. **Velocidades (punto 2):** la tabla del grupo con su justificación (por debajo del Código Nacional de Tránsito, arts. 106 y 107, por ser zona montañosa), el orden de imputación de OSMnx 2.1.1, el **93,5 % de aristas imputadas** (solo 6,5 % trae `maxspeed`), el caso `ladder` (4 aristas en la componente, etiqueta rara de OSM, 20 km/h) y la aclaración de que el tiempo es una estimación del modelo.
4. **Algoritmo de componentes (punto 3):** explicar Tarjan (preorden, `lowlink`, pila, raíz de componente cuando `lowlink == preorden`), que en NetworkX 3.7 es **iterativo** con las mejoras de Tarjan–Zwick (sin límite de recursión), y qué hace `largest_component` en sus tres pasos. Complejidad Θ(V + E) en tiempo y Θ(V) de memoria adicional, más Θ(V' + E') de la copia del subgrafo, con las fuentes citadas en el texto: Tarjan 1972 (*SIAM J. Computing* 1(2):146–160), Tarjan y Zwick 2024 (*European J. Combinatorics* 119, doi:10.1016/j.ejc.2023.103815) y el código de `networkx/algorithms/components/strongly_connected.py` 3.7 y `osmnx/truncate.py` 2.1.1. Precisar que `is_strongly_connected` en NetworkX 3.7 es `len(next(strongly_connected_components(G))) == len(G)`, o sea, una pasada parcial adicional del mismo algoritmo, que sigue siendo lineal.
5. **Discusión de tiempos (punto 3, sección 6.8):** `tiempo_por_elemento_us` queda casi constante (2,31; 2,43; 2,36; 2,47; 2,43 µs), lo que es coherente con Θ(V + E). Explicar las pequeñas desviaciones (costos fijos en la red de 2 km, caché). Señalar que **ninguna** de las 5 redes era fuertemente conexa, así que siempre se ejecutaron los tres pasos.
6. **Radio de 20 km ≈ departamento:** con `dist_type="bbox"` el radio de 20 km es un cuadrado de 40 × 40 km (1 600 km²), comparable al Quindío (≈ 1 845 km²; el polígono medido da 1 934,6 km²). Por eso sus V + E (28 991) casi coinciden con los del departamento (29 122) y el tiempo es prácticamente igual (71,5 frente a 70,9 ms). Explicar que la tabla se lee por V + E y no por el nombre de la fila.
7. **Por qué conviene la componente:** rutas en ambos sentidos entre cualquier par de nodos, Dijkstra siempre llega, la matriz 42 × 42 de R2 no tiene infinitos y todo recorrido de R4 es factible.
8. **Lugares a más de 500 m (punto 4):** tabla de A03 Valle de Cocora (1 054 m), A10 RECUCA (539 m) y A11 Cascadas del Río Verde (1 473 m), con la explicación de cada uno (la vía llega al parqueadero, el lugar está dentro de una finca, se entra a pie) y de por qué se conservan (están verificados en mapa).
9. **Verificación (sección 6.6):** cómo se verificó cada pieza (casos a mano 1–9, NetworkX en los casos 5 y 6 y en la red de 2 km, cKDTree en el caso 15, pyproj en el caso 10).
10. **Complejidad del resto:** pesos Θ(E), UTM Θ(V + P), vecino más cercano Θ(P · V) con Θ(1) adicional (P = 42), `mejor_arista` O(k). Indicar que R1 no tiene recurrencias.
11. **Anexo de IA:** el contenido de `docs/anexo-ia.md` (herramienta, propósito, verificación) debe pasar al anexo del documento técnico. Santiago y Nicolás tienen pendiente decidir si se versiona o va solo en el documento; corregir antes la frase sobre las aristas paralelas señalada arriba.

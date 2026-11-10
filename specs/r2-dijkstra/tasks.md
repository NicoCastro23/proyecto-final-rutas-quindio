# Tareas — R2 Caminos mínimos (Dijkstra y matriz de tiempos)

Spec: `spec.md` · Plan: `plan.md`. Todas las órdenes se corren desde la raíz del repositorio (`/Users/santiagopolaniapinzon/proyecto-final-rutas-quindio`) con `.venv/bin/python` (Python 3.13.8; no hay que instalar nada).

Cada tarea en la que se use IA termina con: **anotar en `docs/anexo-ia.md`** (fecha, integrante, herramienta, qué se generó, cómo se verificó).

> **Reglas del usuario:**
> 1. Cada bloque termina con todas sus pruebas en verde y el trabajo se **DETIENE** hasta que el usuario haga su commit. No se empieza el bloque siguiente antes.
> 2. Test primero **tarea por tarea**: escribir la prueba de una tarea, verla fallar por la razón correcta (el módulo existe con funciones que hacen `raise NotImplementedError`; no un `ModuleNotFoundError` global) y solo entonces escribir el código. El reporte de cada bloque lo confirma tarea por tarea.
> 3. No modificar `.gitignore` sin preguntar (conserva `docs/` y `.DS_Store`). `docs/` está ignorada: `docs/anexo-ia.md` se mantiene en local.
> 4. Nunca `git add`, `git commit` ni `git push`.
> 5. Las mediciones finales sobre la red real las corre el usuario con el portátil enchufado: las tareas de medición real terminan **entregándole el comando exacto**, no ejecutándolo.

> **Simplicidad:** código legible que cada integrante pueda explicar. `dijkstra_lineal` y `dijkstra_cola` van una debajo de la otra en `rutas/r2/dijkstra.py`, con la misma estructura (ver el esqueleto del plan) y cortas: **misma inicialización** (`dist`, `pred`, `visitado` como listas de tamaño V) y solo cambia la búsqueda del mínimo. Trabajan con **índices**; la traducción ids ↔ índices vive solo en `consultar` y en los scripts. Los archivos de salida llevan siempre ids. NetworkX solo aparece en las pruebas.

## B1 · Adyacencia y las dos versiones de Dijkstra (casos a mano y de la clase)

- [x] T1 · Paquete `rutas/r2` y rutas de R2 en la configuración
  - Archivos: `rutas/r2/__init__.py` (vacío), `rutas/config.py` (agregar `RESULTS_R2 = RAIZ / "results" / "r2"` y `MATRIZ_TIEMPOS = DATA_PROCESSED / "matriz_tiempos.csv"`; no tocar lo demás)
  - Test primero: `tests/test_config.py::test_rutas_r2` (`RESULTS_R2 == RAIZ / "results" / "r2"`; `MATRIZ_TIEMPOS.name == "matriz_tiempos.csv"` y su carpeta es `DATA_PROCESSED`)
  - Verificar: `.venv/bin/python -m pytest tests/test_config.py`

- [x] T2 · Representación indexada propia (`Red`) con todas las aristas, validación de pesos y helper de pruebas (Entradas/Puerta 2; casos 8, 9, 12; bordes de pesos)
  - Archivos: `rutas/r2/adyacencia.py` (`Red(NamedTuple: ids, indice, adyacencia)` y `construir_adyacencia(G, peso="travel_time") -> Red`: `ids = sorted(G.nodes)`, `indice = {id: i}`, `adyacencia` lista de V listas de `(j, travel_time)` con todas las aristas `(u, v, key)`); `tests/conftest.py` (agregar `red_desde_aristas(aristas, nodos=None)`: arma un `nx.MultiDiGraph` con `travel_time` desde tuplas `(u, v, w)` más los nodos aislados de `nodos`, y lo pasa por `construir_adyacencia`)
  - Test primero: `tests/test_adyacencia.py::test_g1_red_indexada` (G1 con `red_desde_aristas`, ids A = 1 … F = 6: `ids == [1, …, 6]`, `indice[k] == k − 1`, `len(adyacencia) == 6`, `adyacencia[5] == []` (F aislado), 6 entradas en total, `adyacencia[0]` contiene `(1, 4.0)` y `(2, 1.0)`), `::test_ids_ordenados_e_indice` (nodos agregados en el orden 30, 10, 20 con aristas 30→10 y 10→20: `ids == [10, 20, 30]`, `adyacencia[2] == [(0, w)]`, `adyacencia[0] == [(1, w')]`), `::test_paralelas_y_autolazo_se_conservan` (multigrafo del caso 12: `adyacencia[0]` contiene `(1, 50.0)`, `(1, 40.0)` y `(0, 5.0)`; 4 entradas en total), `::test_peso_cero_permitido`, `::test_caso_9_peso_invalido` (parametrizada: −1, `float("nan")`, `math.inf` → `ValueError` cuyo mensaje contiene los **ids** `u`, `v` y la `key` de la arista culpable). El multigrafo del caso 12 (con `length` y claves) se arma con `grafo_sintetico`
  - Verificar: `.venv/bin/python -m pytest tests/test_adyacencia.py`
  - anotar en `docs/anexo-ia.md`

- [x] T3 · Copia versionada de la red de la clase (casos 19–23, sin depender de `estudio/`)
  - Archivos: `tests/datos/red_clase.json` (copiar **solo** las secciones `red` y `R2` de `estudio/casos_prueba.json`, sin cambiar valores, y agregar `"_origen": "Copia de las secciones red y R2 de estudio/casos_prueba.json (grafo de la clase de Dijkstra, resuelto a mano y verificado con NetworkX 3.7 y SciPy 1.18.1), 2026-11-10. estudio/ no se versiona."`); `tests/conftest.py` (agregar `cargar_red_clase()` → `(red, seccion_R2)`: `red_desde_aristas` con las aristas cuyos dos extremos están en 1–7, peso = minutos del JSON, paralela 2→3 incluida)
  - Test primero: `tests/test_dijkstra_clase.py::test_red_clase_versionada` (el archivo existe; claves exactamente `_origen`, `red`, `R2`; 24 aristas con dos 2→3 de 2 y 5 min; `cargar_red_clase()` da `red.ids == [1, …, 7]` y 22 entradas en total; si existe `estudio/casos_prueba.json`, `red` y `R2` son iguales a las de allí, si no se omite esa comparación)
  - Verificar: `.venv/bin/python -m pytest tests/test_dijkstra_clase.py -k versionada`
  - Decisión del usuario (Puerta 2, confirmada): se versiona `tests/datos/red_clase.json` (no hace falta tocar `.gitignore`)

- [x] T4 · `dijkstra_lineal`, `reconstruir_ruta` y el envoltorio `consultar` (casos 1–8, 11, 12, 19, 21, 22, 23; bordes)
  - Archivos: `rutas/r2/dijkstra.py` (crear con `dijkstra_lineal`, `dijkstra_cola`, `reconstruir_ruta` y `consultar` como stubs `raise NotImplementedError`; implementar aquí `reconstruir_ruta`, `dijkstra_lineal` y `consultar`. Lineal sobre índices según el esqueleto del plan: `dist = [inf]*V`, `pred = [None]*V`, `visitado = [False]*V`; recorrido de 0 a V−1 cambiando de candidato solo si `dist[i] < mejor` (estricto); parada al sacar el destino; relajación estricta; sin destino devuelve `(dist, pred, explorados)` con listas de largo V. `VERSIONES = {"lineal": dijkstra_lineal, "cola_prioridad": dijkstra_cola}` y `consultar(red, id_origen, id_destino, version="cola_prioridad")` → `(tiempo_s, ruta en ids, explorados)`, `KeyError` claro si un id no está en `red.indice`, `ValueError` si la versión no existe)
  - Test primero: `tests/test_dijkstra.py`, con G1/G2/caso 12 armados con `red_desde_aristas` (ids 1 … 6) y todas parametrizadas con `version` en `["lineal", "cola_prioridad"]`: vía `consultar(red, o, d, version)` (ids): `::test_caso_1_a_b` (3, [1, 3, 2], 3), `::test_caso_2_a_d_entrada_obsoleta` (4, [1, 3, 2, 4], 4), `::test_caso_3_a_e` (7, [1, 3, 2, 4, 5], 5), `::test_caso_4_origen_igual_destino` (0, [1], 1), `::test_caso_5_a_f_inalcanzable` (inf, [], 5), `::test_caso_6_e_a_inalcanzable` (inf, [], 1), `::test_caso_8_peso_cero` (G1 + 2→5 de 0 s: 3, [1, 3, 2, 5]), `::test_caso_11_desempate_por_id` (G2: 2, [1, 2, 4], 4), `::test_caso_12_paralelas_y_autolazo` (40, [1, 2]); directo sobre índices con `VERSIONES[version](red.adyacencia, red.indice[o])`: `::test_caso_7_sin_destino` (las 5 filas de distancias de la spec leyendo `dist[red.indice[x]]`; no alcanzados = `inf`), `::test_sin_destino_listas_tamano_V` (`len(dist) == len(pred) == 6`; `pred[origen] is None`; `pred` = `None` en los no alcanzados; con destino la ruta directa es de índices, p. ej. A→B da `[0, 2, 1]`), `::test_no_modifica_adyacencia` (copia profunda antes y comparación después); sin parametrizar: `::test_reconstruir_ruta` (cadena de `pred`, origen = destino, destino sin predecesor → []), `::test_consultar_traduce_ids` (red con ids 30, 10, 20 y aristas 30→10, 10→20: `consultar(red, 30, 20, v)` da ruta `[30, 10, 20]` en ids, ambas versiones), `::test_consultar_id_inexistente_keyerror` (origen y destino, mensaje con el id), `::test_consultar_version_desconocida` (`ValueError`); `tests/test_dijkstra_clase.py`, parametrizadas igual sobre `cargar_red_clase()`: `::test_caso_19_orden_de_extraccion` (desde 1: ordenar los nodos 1–7 por los explorados con parada (`consultar`) da 1, 2, 3, 4, 5, 7, 6, y `dist` sin destino leída en ese orden = 0, 1, 3, 4, 5, 8, 9), `::test_caso_21_explorados_con_parada` (2 → 2, 3 → 3, 4 → 4, 5 → 5, 6 → 7, 7 → 6), `::test_caso_22_arista_paralela` (d(1, 3) = 3), `::test_caso_23_matriz_clase` (sin destino desde cada nodo 1–7, `dist` leída por `red.indice` = `R2.matriz_min.filas`)
  - Ver fallar: `-k lineal` falla con `NotImplementedError` (no con `ModuleNotFoundError`); las de `cola_prioridad` siguen en rojo hasta T5
  - Verificar: `.venv/bin/python -m pytest tests/test_dijkstra.py tests/test_dijkstra_clase.py -k "lineal or reconstruir or consultar or versionada"`
  - Nota: `dijkstra_*` no devuelve el orden de extracción; el caso 19 lo deduce de los explorados con parada (el destino que sale en la posición k da k explorados) y de las distancias, sin agregar un valor de retorno
  - anotar en `docs/anexo-ia.md`

- [x] T5 · `dijkstra_cola` con `heapq` e inserción perezosa, y contador opcional (casos 1–8, 10, 11, 12, 19–23)
  - Archivos: `rutas/r2/dijkstra.py` (implementar `dijkstra_cola(adyacencia, origen, destino=None, estadisticas=None)` con **la misma inicialización que la lineal** (`dist = [inf]*V`, `pred = [None]*V`, `visitado = [False]*V`) y lo único distinto: montículo `heapq` de `(distancia, índice)`, entrada obsoleta (`visitado[u]`) descartada sin contarla, inserción solo si mejora estrictamente; si `estadisticas` es un `dict` se le escriben `"extracciones"` y `"obsoletas"` al terminar)
  - Test primero: las parametrizadas `cola_prioridad` de T4 (ya escritas, en rojo con `NotImplementedError`); además `tests/test_dijkstra.py::test_caso_10_versiones_coinciden` (casos 1–8 y 11 con y sin destino, llamando a las dos funciones directo sobre índices: mismo tiempo exacto, misma ruta, mismos explorados, **mismas listas `dist` y `pred` completas**), `tests/test_dijkstra_clase.py::test_caso_20_conteo_cola` (`dijkstra_cola(red.adyacencia, red.indice[2], estadisticas=e)`: 7 explorados, `e == {"extracciones": 9, "obsoletas": 2}`), `::test_estadisticas_no_cambian_resultado` (mismo resultado con y sin `estadisticas`, en G1 y la red de la clase)
  - Verificar: `.venv/bin/python -m pytest tests/test_dijkstra.py tests/test_dijkstra_clase.py`
  - anotar en `docs/anexo-ia.md`

**Fin de B1:** `.venv/bin/python -m pytest -m "not red"` en verde. **Detenerse** y entregar el reporte (tarea por tarea: prueba escrita, fallo visto y su razón, prueba en verde). Esperar el commit del usuario.

## B2 · Verificación contra NetworkX y detalle de la ruta

- [ ] T6 · `detalle_ruta(G, ruta)` con `mejor_arista` (caso 12 y bordes de ruta)
  - Archivos: `rutas/r2/ruta.py` (stub primero; luego suma tramo a tramo de `mejor_arista(G, u, v).travel_time` y `.length`)
  - Test primero: `tests/test_ruta.py::test_caso_12_detalle_usa_mejor_arista` (multigrafo del caso 12 con `grafo_sintetico` y su red con `construir_adyacencia`: la ruta en ids de `consultar(red, 1, 2, "cola_prioridad")` es [1, 2] y `detalle_ruta(G, ruta)` = (40.0, 900.0)), `::test_ruta_g1` (ruta del caso 3 en G1 con `length` conocidos → suma exacta de tiempos = 7 y suma de longitudes a mano), `::test_ruta_de_un_nodo` ((0.0, 0.0)), `::test_ruta_vacia_error` (`ValueError`)
  - Verificar: `.venv/bin/python -m pytest tests/test_ruta.py`
  - anotar en `docs/anexo-ia.md`

- [ ] T7 · Propiedad: 200 grafos aleatorios contra NetworkX (caso 13)
  - Archivos: `tests/test_dijkstra_propiedad.py` (solo prueba; el generador usa `random.Random(2026)`: 5 a 30 nodos con ids enteros **no consecutivos y en orden aleatorio** (para ejercitar la traducción), pesos enteros 0–20, algunas paralelas y autolazos; se construye un `nx.MultiDiGraph` y su `Red` con `construir_adyacencia`)
  - Test primero: `::test_caso_13_sin_destino` (para cada grafo y cada origen: `dist` de ambas versiones, traducida a ids con `red.ids`, en los alcanzados = `nx.single_source_dijkstra_path_length(G, o, weight="travel_time")` exacto, `inf` exactamente en los no alcanzados, mismos explorados entre versiones), `::test_caso_13_con_destino` (pares con destino vía `consultar`: mismo tiempo, misma ruta y mismos explorados entre versiones; tiempo = NetworkX o `inf` si no hay camino; la ruta suma el tiempo con la arista mínima de cada tramo)
  - Ver fallar: el código ya existe; se valida con una **mutación temporal** en `dijkstra.py` (p. ej. `<=` en la búsqueda del mínimo de la lineal, que rompe el desempate, o `<=` en la relajación) que la hace fallar, y se restaura
  - Verificar: `.venv/bin/python -m pytest tests/test_dijkstra_propiedad.py`
  - anotar en `docs/anexo-ia.md`

- [ ] T8 · Adyacencia de la red real (caso 15, marcador `red`)
  - Archivos: `tests/test_red_real_r2.py` (crear con `pytestmark = pytest.mark.red`; usa la fixture `grafo_procesado_real`)
  - Test primero: `::test_caso_15_adyacencia_real` (`len(ids) == len(adyacencia) == 8 791`, `ids == sorted(G.nodes)`, `indice[ids[i]] == i`, 20 132 entradas en total, todos los índices de vecino en 0..V−1, todos los pesos finitos y ≥ 0)
  - Ver fallar: mutación temporal (p. ej. saltarse los autolazos en `construir_adyacencia` → 20 108 entradas) y restaurar
  - Verificar: `.venv/bin/python -m pytest tests/test_red_real_r2.py -k caso_15`
  - anotar en `docs/anexo-ia.md`

**Fin de B2:** `.venv/bin/python -m pytest` en verde (incluidas las `red` de R1 y la de T8). **Detenerse** y entregar el reporte. Esperar el commit del usuario.

## B3 · Pares, matriz de tiempos y asimetría

- [ ] T9 · Selección de pares con semilla 2026 (caso 17)
  - Archivos: `rutas/r2/pares.py` (`SEMILLA = 2026`, `seleccionar_pares(catalogo, lugares_nodos, semilla=SEMILLA)` con el procedimiento exacto del plan: `sorted` + `shuffle` de municipios, un par por municipio por vuelta con `rng.sample(lugares, 2)` repetido hasta válido, luego 10 lejanos con `rng.sample(ids, 2)`)
  - Test primero: `tests/test_pares.py::test_caso_17_catalogo_real` (con `cargar_catalogo()` y `cargar_lugares_nodos()`; se salta si falta `lugares_nodos.csv`: 20 filas, columnas del plan; 10 `cercano` de 10 municipios distintos con `municipio_origen == municipio_destino` y `nodo_origen != nodo_destino`; 10 `lejano` con municipios distintos; sin pares ordenados repetidos; ningún par {T03, T05}; nodos = los de `lugares_nodos.csv`), `::test_misma_semilla_mismos_pares` (dos llamadas → `DataFrame` iguales; con otra semilla cambian), `::test_mismo_nodo_excluido_sintetico` (catálogo sintético de 3 municipios donde dos lugares comparten nodo: nunca aparecen juntos), `::test_municipio_sin_pares_validos_se_salta` (municipio de 2 lugares en el mismo nodo)
  - Verificar: `.venv/bin/python -m pytest tests/test_pares.py`
  - anotar en `docs/anexo-ia.md`

- [ ] T10 · Matriz: cálculo, guardado sin redondear, lectura y asimetría (casos 16 sintético y 23; bordes)
  - Archivos: `rutas/r2/matriz.py` (stubs primero; `calcular_matriz(red, nodos)` (nodos en ids; `dijkstra_cola(red.adyacencia, red.indice[n])` sin destino por fila y lectura `dist[red.indice[m]]`), `guardar_matriz(matriz, ids, ruta)` con el módulo `csv`, encabezado `id` y `repr(float)`, `cargar_matriz(ruta)` con `index_col=0` y `float_precision="round_trip"`, `asimetria(matriz, ids, tolerancia=1e-6)`)
  - Test primero: `tests/test_matriz.py::test_caso_23_asimetria_clase` (matriz 7 × 7 calculada con `calcular_matriz(red, [1, …, 7])` sobre `cargar_red_clase()` = `R2.matriz_min.filas`; `asimetria` → 9 pares, `par_max` = [4, 7] (o [7, 4] normalizado a i < j por el orden de `ids`), `diferencia_max` = 10, `M_ij` = 4, `M_ji` = 14), `::test_mismo_nodo_da_cero` (dos ids con el mismo nodo → celdas 0 y diagonal 0), `::test_inf_es_error` (G1 con `red_desde_aristas` y F como lugar → `ValueError`), `::test_nodo_ausente_keyerror` (un id que no está en la red → `KeyError`), `::test_guardar_cargar_round_trip_byte_a_byte` (valores como `0.1 + 0.2` y `1/3`: lo leído es igual exacto al `float` original; guardar lo leído en otro archivo → mismos bytes; encabezado e índice en el orden dado)
  - Verificar: `.venv/bin/python -m pytest tests/test_matriz.py`
  - anotar en `docs/anexo-ia.md`

- [ ] T11 · Script de la matriz y pruebas con la red real (casos 14 y 16, marcador `red`)
  - Archivos: `rutas/r2/matriz.py` (`main(processed=DATA_PROCESSED, catalogo=CATALOGO, salida=RESULTS_R2)`: carga grafo, catálogo y lugares; construye la `Red` con `construir_adyacencia`; calcula la matriz en el orden del catálogo; escribe `MATRIZ_TIEMPOS` y `results/r2/r2_asimetria.json`; imprime cuántos pares son asimétricos); `tests/test_red_real_r2.py`
  - Test primero: `tests/test_matriz.py::test_main_sintetico` (carpeta `processed` sintética en `tmp_path` con un grafo de `grafo_sintetico` fuertemente conexo guardado con `guardar_procesado` de R1 y un catálogo/lugares de 3 lugares: escribe la matriz 3 × 3 y el JSON con las claves del plan); `tests/test_red_real_r2.py::test_caso_14_lineal_igual_a_cola` (10 cercanos de `seleccionar_pares`, con `consultar(red, nodo_o, nodo_d, version)`: |Δt| ≤ 1e-6, misma ruta y mismos explorados), `::test_caso_14_ruta_y_networkx` (20 pares con `consultar(..., "cola_prioridad")`: `detalle_ruta(G, ruta)[0]` = tiempo ± 1e-6 y `nx.dijkstra_path_length(G, o, d, weight="travel_time")` = tiempo ± 1e-6), `::test_caso_16_matriz_real` (se salta si falta `matriz_tiempos.csv`: 42 × 42, ids en el orden del catálogo, diagonal 0, sin `inf`, T03↔T05 = 0, al menos un par asimétrico; `M[i][j]` = `consultar(red, nodo_i, nodo_j, "cola_prioridad")[0]` ± 1e-6 en 20 pares de `random.Random(2026)` y en los 20 de `seleccionar_pares`; reescribir con `guardar_matriz` en `tmp_path` da los mismos bytes)
  - Ejecutar (no es una medición de tiempo; decisión 3 de la Puerta 2: la corre el implementer): `.venv/bin/python -m rutas.r2.matriz` para generar `data/processed/matriz_tiempos.csv` y `results/r2/r2_asimetria.json`
  - Ver fallar: `test_main_sintetico` con el stub; las `red` con una mutación temporal (p. ej. escribir la matriz con `round(x, 2)` → falla el caso 16) y restaurar
  - Verificar: `.venv/bin/python -m pytest tests/test_matriz.py && .venv/bin/python -m pytest tests/test_red_real_r2.py`
  - anotar en `docs/anexo-ia.md`

**Fin de B3:** `.venv/bin/python -m pytest` en verde (ninguna `red` saltada). **Detenerse** y entregar el reporte con el número de pares asimétricos y el par de mayor diferencia. Esperar el commit del usuario.

## B4 · Medición, cociente, gráfica y tablas

- [ ] T12 · Script de medición con la comprobación entre versiones (sección 6; viñeta 2 y verificación de R2)
  - Archivos: `rutas/r2/medir_dijkstra.py` (`COLUMNAS`, `fila`, `medir_pares(G, red, pares, repeticiones=5, medir_cola=medir_en_proceso, medir_lineal=medir_en_hijo)` con la secuencia del plan: traducción a índices y corrida con `consultar` fuera del cronómetro, medición de `dijkstra_*(red.adyacencia, i_o, i_d)`, `main(processed=..., catalogo=..., salida=RESULTS_R2, repeticiones=5)` que escribe `r2_pares.csv`, `r2_pares.json`, `r2_dijkstra.csv` y `maquina.json`; `if __name__ == "__main__":`)
  - Test primero: `tests/test_medir_dijkstra.py::test_fila_columnas_y_no_completada` (`list(fila) == COLUMNAS`; resultado no completado → `tiempo_ms == "no completada"`), `::test_medir_pares_con_medidores_falsos` (grafo sintético de `grafo_sintetico` con ids **no consecutivos** (p. ej. 100, 200, 300, 400) y su `Red`; `pares` a mano, 1 cercano + 1 lejano; medidores falsos que registran sus argumentos y devuelven `ResultadoMedicion` fijo: 3 filas en orden cola, lineal, cola; la cola se mide con `dijkstra_cola` y `preparar()` → `(red.adyacencia, red.indice[o], red.indice[d])` (índices, no ids); la lineal con `dijkstra_lineal` y `args == (red.adyacencia, red.indice[o], red.indice[d])`; las filas llevan los **ids** de lugar; `tiempo_viaje_s`, `nodos_explorados` y `distancia_m` correctos a mano), `::test_versiones_distintas_abortan` (monkeypatch de `VERSIONES["lineal"]` (o de `dijkstra_lineal` en el módulo) que devuelve otro tiempo → `AssertionError` con el par y no se escribe nada), `::test_medir_en_hijo_de_verdad` (red diminuta, `repeticiones=1`, medidores reales: `repeticiones == 1` y `tiempo_ms > 0`; comprueba que la función se puede enviar al hijo), `::test_main_sintetico_escribe_archivos` (carpeta sintética como en T11 con 4 lugares de 2 municipios y `monkeypatch` de `seleccionar_pares` para devolver 2 pares; `repeticiones=1`: existen los 4 archivos, `r2_pares.json` con `"semilla": 2026`)
  - Verificar: `.venv/bin/python -m pytest tests/test_medir_dijkstra.py`
  - anotar en `docs/anexo-ia.md`

- [ ] T13 · Cociente, gráfica y tablas desde los CSV (caso 18; viñeta 3)
  - Archivos: `rutas/r2/tablas.py` (`cociente(df)`, `usar_escala_log(df)`, `grafica_tiempo_vs_explorados(results)`, `main(results=RESULTS_R2)`; reutiliza `a_markdown` de `rutas.r1.tablas`; `matplotlib.use("Agg")`)
  - Test primero: `tests/test_tablas_r2.py::test_caso_18_cociente` (CSV sintético con 3 pares cercanos: lineal 10, 30, 8 ms y cola 2, 3, 4 ms → cocientes 5, 10, 2 → mediana 5, mínimo 2, máximo 10; más una fila de un par lejano solo con cola que no cuenta; `r2_cociente.csv` con columnas exactas `mediana, minimo, maximo`), `::test_cociente_excluye_no_completada`, `::test_escala_log` (`usar_escala_log(df)` es `True` si `max(tiempo_ms) / min(tiempo_ms) ≥ 100` entre las filas completadas, `False` si no), `::test_grafica_crea_png` (el PNG existe y no está vacío), `::test_tablas_salen_de_los_csv` (`tablas_r2.md` contiene los valores del CSV sintético, la semilla de `r2_pares.json`, el cociente, la asimetría de `r2_asimetria.json` y la unidad "ms" en los encabezados), `::test_main_genera_todo` (cociente, PNG y Markdown en `tmp_path`)
  - Verificar: `.venv/bin/python -m pytest tests/test_tablas_r2.py`
  - anotar en `docs/anexo-ia.md`

- [ ] T14 · Prueba de los resultados medidos y entrega del comando de medición real al usuario
  - Archivos: `tests/test_red_real_r2.py::test_resultados_medidos_versiones_coinciden` (se salta si falta `results/r2/r2_dijkstra.csv`: 30 filas, 20 `cola_prioridad` y 10 `lineal`; en cada par cercano `tiempo_viaje_s` igual ± 1e-6 y `nodos_explorados` igual entre versiones; `tiempo_ms` numérico o `"no completada"`; columnas del Anexo presentes y en ese orden al inicio)
  - Test primero: la prueba se ve fallar con un CSV de prueba alterado en `tmp_path` (o mutación temporal) y se restaura; con el CSV ausente queda saltada
  - **No ejecutar la medición.** Entregar al usuario el comando exacto, para correr con el portátil enchufado y sin otros procesos pesados:
    ```bash
    cd /Users/santiagopolaniapinzon/proyecto-final-rutas-quindio && .venv/bin/python -m rutas.r2.medir_dijkstra && .venv/bin/python -m rutas.r2.tablas && .venv/bin/python -m pytest tests/test_red_real_r2.py
    ```
  - Verificar (lo hace el usuario): `results/r2/` tiene `r2_pares.csv`, `r2_pares.json`, `r2_dijkstra.csv` (30 filas), `maquina.json`, `r2_cociente.csv`, `r2_tiempo_vs_explorados.png`, `tablas_r2.md`; la prueba de resultados medidos pasa
  - anotar en `docs/anexo-ia.md`

**Fin de B4:** `.venv/bin/python -m pytest -m "not red"` en verde y el comando de T14 entregado. **Detenerse.** El usuario corre la medición y hace su commit.

## Cierre

- [ ] T15 · Anexo de IA y "Reproducir R2" en el README
  - Archivos: `docs/anexo-ia.md` (entradas de R2: plan y tareas con el agente planner, incluida la revisión de la Puerta 2 (representación indexada); código y pruebas con el implementer; cómo se verificó: casos a mano 1–12, red de la clase 19–23, propiedad contra NetworkX, red real contra `nx.dijkstra_path_length`, matriz releída del CSV, mutaciones temporales); `README.md` (sección "Reproducir R2" después de "Reproducir R1": requisito de haber corrido R1; los comandos `rutas.r2.matriz`, `rutas.r2.medir_dijkstra`, `rutas.r2.tablas` con lo que deja cada uno; semilla 2026; nota de medir enchufado; `pytest -m "not red"` y `pytest`)
  - Test primero: no aplica (documentación)
  - Verificar: `grep -n "R2" docs/anexo-ia.md && grep -n "rutas.r2.medir_dijkstra" README.md`
  - anotar en `docs/anexo-ia.md`

- [ ] T16 · Suite completa y regeneración de todos los resultados de R2 (la ejecuta el usuario con el portátil enchufado)
  - Archivos: ninguno nuevo (regenera `data/processed/matriz_tiempos.csv` y `results/r2/*`)
  - Test primero: no aplica
  - Comando que se entrega al usuario:
    ```bash
    cd /Users/santiagopolaniapinzon/proyecto-final-rutas-quindio && .venv/bin/python -m rutas.r2.matriz && .venv/bin/python -m rutas.r2.medir_dijkstra && .venv/bin/python -m rutas.r2.tablas && .venv/bin/python -m pytest
    ```
  - Verificar: todas pasan y ninguna `red` saltada; `data/processed/matriz_tiempos.csv` sin cambios respecto a B3 (mismo grafo → mismos bytes); `results/r2/` con los 8 archivos de la spec (`r2_pares.csv`, `r2_pares.json`, `r2_dijkstra.csv`, `r2_cociente.csv`, `r2_tiempo_vs_explorados.png`, `r2_asimetria.json`, `maquina.json`, `tablas_r2.md`)

## Cobertura

| Caso / punto | Tarea |
|---|---|
| Representación indexada y `consultar` (Entradas y Funciones, Puerta 2) | T2, T4, T8 |
| Inicialización igual en ambas (Comportamiento, punto 0) | T4, T5 (`test_caso_10_versiones_coinciden` compara `dist` y `pred` completas) |
| 1, 2, 3, 4, 5, 6, 7 | T4, T5 |
| 8 | T2, T4, T5 |
| 9 | T2 |
| 10 | T5 |
| 11 | T4, T5 |
| 12 | T2, T4, T5, T6 |
| 13 | T7 |
| 14 | T11 |
| 15 | T8 |
| 16 | T10 (sintético), T11 (real) |
| 17 | T9 |
| 18 | T13 |
| 19, 21, 22 | T3, T4, T5 |
| 20 | T5 |
| 23 | T3, T4, T5, T10 |
| Bordes: `KeyError` (vía `consultar` y `calcular_matriz`), no modifica la adyacencia, ruta vacía/un nodo, mismo nodo en la matriz, `inf` en la matriz | T4, T5, T6, T10 |
| R2 punto 1: dos versiones propias, parada al sacar el destino, ruta por predecesores, explorados una vez | T4, T5, T6 |
| R2 punto 1, viñeta 1: invariante, parada y pesos ≥ 0 (informe; validación de pesos en código) | T2 (pesos), T4/T5 (caso 19 ilustra el invariante); texto en el informe |
| R2 punto 1, viñeta 2: 20 pares con cola, 10 cercanos con lineal, tiempo y explorados | T9, T12, T14 |
| R2 punto 1, viñeta 3: gráfica tiempo vs explorados y cociente (mediana, mín., máx.) | T13, T14 |
| R2 matriz de tiempos (42 × 42, cola sin destino, no simétrica) | T10, T11, T16 |
| R2 verificación (mismos tiempos en los pares medidos con ambas) | T5, T7, T11, T12, T14 |
| Sección 6.1 misma máquina y `maquina.json` | T12, T14 |
| Sección 6.2 solo el algoritmo | T12 |
| Sección 6.3 5 repeticiones, mediana, una si > 1 min | T12 (vía `rutas.medicion`) |
| Sección 6.4 unidad ms | T12, T13 |
| Sección 6.5 semilla fija documentada | T9, T12 (`r2_pares.json`) |
| Sección 6.6 verificación antes de medir | T4–T8, T11, T12 |
| Sección 6.7 límite de 5 min → "no completada" | T12 (`medir_en_hijo`), T13 |
| Sección 6.8 tablas y gráficas desde CSV/JSON | T13 |
| Anexo de IA | T15 (y cada tarea con IA) |

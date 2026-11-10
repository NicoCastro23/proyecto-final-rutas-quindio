# Revisión — R2 Caminos mínimos (Dijkstra y matriz de tiempos)

Fuentes contrastadas: `CLAUDE.md`, enunciado (`estudio/Proyecto final 2026-2.pdf`, sección 5 R2 y sección 6), anexo (`estudio/Anexo proyecto.pdf`, Requerimiento 2), `spec.md`, `plan.md` y `tasks.md` (T1–T16 marcadas). Las decisiones del usuario escritas en la spec (representación indexada, inicialización O(V) igual en ambas, desempate (distancia, índice), tolerancia 1e-6 s, matriz sin redondear, pares con semilla 2026, lineal en proceso hijo, fuentes sin Cormen, `docs/` ignorada) se respetan y no se reabren.

## Ronda 1: APROBADO

Pruebas: ✅
- `.venv/bin/python -m pytest -q` → **213 passed** en 10,8 s (ninguna saltada; `-rs` no reporta saltos).
- `.venv/bin/python -m pytest -m "not red" -q` → **199 passed, 14 deselected** en 4,4 s.
- `.venv/bin/python -m pytest tests/test_red_real_r2.py -v` → 5 passed (casos 14, 15, 16 y resultados medidos).
- Mutaciones hechas por el revisor sobre una **copia** de `rutas/r2/dijkstra.py` en el scratchpad (el repositorio no se tocó), corriendo `test_dijkstra*.py` y `test_matriz.py`: contar las entradas obsoletas como exploradas → 14 fallan; desempate `<=` en la lineal → 6 fallan; quitar la parada de la lineal → 8 fallan; parar la cola al descubrir el destino → 9 fallan; relajar con `<=` en la cola → 4 fallan; prioridad sin desempate por índice → 4 fallan. La copia sin mutar: 49 passed. Las pruebas sí tocan el comportamiento.

Recalculado por el revisor desde `results/r2/r2_dijkstra.csv`: cocientes por par 44,66; 300,13; 300,43; 333,21; 360,16; 411,25; 437,74; 454,39; 478,25; 506,96 → mediana 385,70, mínimo 44,66, máximo 506,96, iguales a `r2_cociente.csv` y a `tablas_r2.md`. Ajuste lineal tiempo–explorados: lineal 0,1864 ms/nodo (= 21,2 ns × V), cola 0,408 µs/nodo; límite c_lin·V/c_cola ≈ 457. Coincide con lo que dice la spec.

| Caso / punto del enunciado | Cumplido | Test |
|---|---|---|
| Caso 1 A→B = 3, ruta A,C,B, 3 explorados | ✅ | `tests/test_dijkstra.py::test_caso_1_a_b` (ambas versiones) |
| Caso 2 A→D = 4, entrada obsoleta, 4 explorados | ✅ | `tests/test_dijkstra.py::test_caso_2_a_d_entrada_obsoleta` |
| Caso 3 A→E = 7, 5 explorados | ✅ | `tests/test_dijkstra.py::test_caso_3_a_e`; `tests/test_ruta.py::test_ruta_g1` |
| Caso 4 A→A = 0, ruta [A], 1 explorado | ✅ | `tests/test_dijkstra.py::test_caso_4_origen_igual_destino` |
| Caso 5 A→F inf, ruta vacía, 5 explorados | ✅ | `tests/test_dijkstra.py::test_caso_5_a_f_inalcanzable` |
| Caso 6 E→A inf, 1 explorado | ✅ | `tests/test_dijkstra.py::test_caso_6_e_a_inalcanzable` |
| Caso 7 distancias sin destino desde A…E | ✅ | `tests/test_dijkstra.py::test_caso_7_sin_destino` |
| Caso 8 peso 0, A→E = 3 por A,C,B,E | ✅ | `tests/test_dijkstra.py::test_caso_8_peso_cero`; `tests/test_adyacencia.py::test_peso_cero_permitido` |
| Caso 9 peso −1, NaN, inf → error con la arista | ✅ | `tests/test_adyacencia.py::test_caso_9_peso_invalido` |
| Caso 10 ambas versiones idénticas en 1–8 y 11 | ✅ | `tests/test_dijkstra.py::test_caso_10_versiones_coinciden` (todas las parejas, con y sin destino, incluidas `dist` y `pred`) |
| Caso 11 desempate G2: ruta A,B,D, 4 explorados | ✅ | `tests/test_dijkstra.py::test_caso_11_desempate_por_id` |
| Caso 12 paralelas + autolazo: 40 s, ruta A,B; detalle 40 s / 900 m | ✅ | `tests/test_dijkstra.py::test_caso_12_paralelas_y_autolazo`; `tests/test_ruta.py::test_caso_12_detalle_usa_mejor_arista`; `tests/test_adyacencia.py::test_paralelas_y_autolazo_se_conservan` |
| Caso 13 propiedad: 200 grafos, semilla 2026, contra NetworkX | ✅ | `tests/test_dijkstra_propiedad.py::test_caso_13_sin_destino`, `::test_caso_13_con_destino` |
| Caso 14 red real: lineal = cola (1e-6 s, explorados, ruta) en 10 cercanos; detalle y `nx.dijkstra_path_length` en 20 | ✅ | `tests/test_red_real_r2.py::test_caso_14_lineal_igual_a_cola`, `::test_caso_14_ruta_y_networkx` |
| Caso 15 adyacencia real V = 8 791, 20 132 entradas finitas ≥ 0 | ✅ | `tests/test_red_real_r2.py::test_caso_15_adyacencia_real` |
| Caso 16 matriz 42×42 real (orden, diagonal, T03↔T05, asimetría, 40 pares contra Dijkstra, bytes) | ✅ | `tests/test_red_real_r2.py::test_caso_16_matriz_real`; `tests/test_matriz.py::test_guardar_cargar_round_trip_byte_a_byte` |
| Caso 17 selección de pares con semilla 2026 | ✅ | `tests/test_pares.py::test_caso_17_catalogo_real`, `::test_misma_semilla_mismos_pares` y los tres sintéticos |
| Caso 18 cociente con CSV sintético (5, 2, 10) | ✅ | `tests/test_tablas_r2.py::test_caso_18_cociente`, `::test_main_genera_todo` |
| Caso 19 orden de extracción 1,2,3,4,5,7,6 y distancias 0,1,3,4,5,8,9 | ✅ | `tests/test_dijkstra_clase.py::test_caso_19_orden_de_extraccion` |
| Caso 20 cola desde 2: 7 explorados, 9 extracciones, 2 obsoletas | ✅ | `tests/test_dijkstra_clase.py::test_caso_20_conteo_cola`, `::test_estadisticas_no_cambian_resultado` |
| Caso 21 explorados con parada 2,3,4,5,7,6 | ✅ | `tests/test_dijkstra_clase.py::test_caso_21_explorados_con_parada` |
| Caso 22 arista paralela d(1,3) = 3 | ✅ | `tests/test_dijkstra_clase.py::test_caso_22_arista_paralela` |
| Caso 23 matriz 7×7, 9 asimétricos, {4,7} = 10 (M[4][7] = 4, M[7][4] = 14) | ✅ | `tests/test_dijkstra_clase.py::test_caso_23_matriz_clase`; `tests/test_matriz.py::test_caso_23_asimetria_clase` |
| Copia versionada `tests/datos/red_clase.json` idéntica al original | ✅ | `tests/test_dijkstra_clase.py::test_red_clase_versionada` |
| Bordes: `KeyError` claro, no modifica la adyacencia, ruta vacía / de un nodo, `inf` en la matriz | ✅ | `test_dijkstra.py::test_consultar_id_inexistente_keyerror`, `::test_no_modifica_adyacencia`; `test_ruta.py`; `test_matriz.py::test_inf_es_error`, `::test_nodo_ausente_keyerror`, `::test_mismo_nodo_da_cero` |
| R2.1 dos versiones propias (lineal O(V²) y `heapq`) | ✅ | `rutas/r2/dijkstra.py:25-90`; ninguna importación de NetworkX/SciPy/Shapely en `rutas/r2/` (grep vacío) |
| R2.1 parada al sacar el destino | ✅ | `rutas/r2/dijkstra.py:46` y `:80`; casos 21 y mutaciones |
| R2.1 ruta por predecesores | ✅ | `rutas/r2/dijkstra.py:11-22`; `test_reconstruir_ruta` |
| R2.1 explorados contados una vez (obsoletas descartadas sin contar) | ✅ | `rutas/r2/dijkstra.py:75-79`; casos 2 y 20 |
| R2 viñeta 2: ≥ 20 pares con cola, 10 cercanos con lineal, tiempo y explorados | ✅ | `results/r2/r2_dijkstra.csv` (30 filas); `test_red_real_r2.py::test_resultados_medidos_versiones_coinciden` |
| R2 viñeta 3: gráfica tiempo vs explorados con ambas versiones | ✅ | `results/r2/r2_tiempo_vs_explorados.png` (color y marcador por versión, eje log indicado en la etiqueta); `test_tablas_r2.py::test_grafica_crea_png` |
| R2 viñeta 3: cociente mediana / mín. / máx. | ✅ | `results/r2/r2_cociente.csv`, recalculado por el revisor |
| Matriz ≥ 40×40, cola sin destino desde cada lugar, ids en primera fila/columna | ✅ | `rutas/r2/matriz.py:14-41`; `data/processed/matriz_tiempos.csv` (43 líneas, esquina `id`) |
| Verificación: mismos tiempos en los pares medidos con ambas | ✅ | `rutas/r2/medir_dijkstra.py:41-51` (aborta antes de medir); `test_caso_14_lineal_igual_a_cola`; `test_medir_dijkstra.py::test_versiones_distintas_abortan` |
| Anexo: columnas `origen, destino, version, tiempo_viaje_s, nodos_explorados, tiempo_ms` primero | ✅ | `rutas/r2/medir_dijkstra.py:25`; `comprobar_resultados` |
| 6.1 misma máquina, `maquina.json` (CPU, RAM, SO, Python) | ✅ | `results/r2/maquina.json` |
| 6.2 solo se mide el algoritmo | ✅ | `rutas/medicion.py:46-49` y `:85-87`; `test_medir_pares_con_medidores_falsos` |
| 6.3 5 repeticiones, mediana; una sola si > 1 min | ✅ | `rutas/medicion.py`; columna `repeticiones` = 5 en las 30 filas |
| 6.4 unidad ms | ✅ | `tiempo_ms`, encabezados "Tiempo (ms)" |
| 6.5 semilla fija documentada | ✅ | `results/r2/r2_pares.json` (2026, `random.Random`, regla) |
| 6.6 verificación antes de medir | ✅ | `_comprobar_versiones` + suite |
| 6.7 límite 5 min → "no completada" | ✅ | `rutas/medicion.py:97-101`; `test_fila_columnas_y_no_completada`, `test_cociente_excluye_no_completada` |
| 6.8 tablas y gráfica desde CSV/JSON | ✅ | `rutas/r2/tablas.py`; `test_tablas_salen_de_los_csv`; el cociente guardado se compara con el CSV en `test_resultados_medidos_versiones_coinciden` |

### Bloqueantes
- Ninguno.

### Sugerencias (no bloquean)
- `rutas/r2/medir_dijkstra.py:67` y `:76`: la fila `lineal` del CSV copia `tiempo_viaje_s` y `nodos_explorados` de la corrida con **cola** (`consultar` usa `cola_prioridad` por defecto), no del resultado de la lineal. La igualdad sí se comprueba antes (`_comprobar_versiones`) y en `test_caso_14_lineal_igual_a_cola`, así que no hay error. Pero el CSV no deja evidencia propia de la lineal, y `comprobar_resultados` (`tests/test_red_real_r2.py:122-127`), que compara lineal y cola dentro del CSV, sobre los datos reales es una comprobación **tautológica**: siempre pasa por construcción. Haría falta registrar en la fila lineal sus propios `t_l, k_l` (los que ya calcula `_comprobar_versiones`) para que el archivo demuestre por sí mismo la verificación que pide el enunciado. Si se cambia, la medición se tendría que repetir; si no, basta explicarlo en el informe.
- `rutas/r2/medir_dijkstra.py:49`: la comprobación previa usa `assert`, que desaparece con `python -O`. Sería más robusto un `raise ValueError(...)` explícito (la prueba `test_versiones_distintas_abortan` espera `AssertionError` y habría que ajustarla).
- `specs/r2-dijkstra/spec.md:3`: la línea de estado sigue en "☐ pruebas · ☐ código · ☐ verificado" aunque T1–T16 están cerradas. Actualizarla (y hacer commit junto con los cambios pendientes de `README.md`, `spec.md` y `tasks.md`, que siguen sin commit).
- `results/r2/` no tiene una tabla del cociente **por par con sus nodos explorados**. La discusión de la spec ("cociente de 44,7 con 8 nodos a 507 con 1 375, cerca del límite ≈ 457") y las pendientes de 0,186 ms/nodo y 0,41 µs/nodo salen de cálculos sobre el CSV que hoy no genera ningún script. Por la regla 6.8, convendría que `rutas/r2/tablas.py` escriba en `tablas_r2.md` una tabla "par, k, lineal (ms), cola (ms), cociente" y las pendientes del ajuste. Así cada número del informe saldría de un archivo.
- `rutas/r2/tablas.py:68`: el título de la gráfica dice "mediana de 5 repeticiones" fijo. Si alguna medición pasara de 1 min (una sola repetición), el título mentiría. Conviene derivarlo de la columna `repeticiones` o decir "mediana de las repeticiones".
- Condiciones de medición distintas entre versiones (decisión del usuario, no se reabre): la lineal corre en un hijo `spawn` recién creado (sin calentamiento) y la cola en el proceso padre, ya calentado por `consultar` y `_comprobar_versiones`. Conviene mencionarlo en el informe como posible sesgo pequeño del cociente. El punto de 8 nodos (1,44 ms frente a 8 × 0,186 ≈ 1,49 ms predichos) sugiere que el efecto es despreciable.
- `tests/test_dijkstra_clase.py:41-43`: el caso 19 deduce el orden de extracción del número de explorados con parada, no lo observa directamente en una corrida sin destino. Es válido porque el algoritmo es determinista. Si se quiere la prueba literal, `estadisticas` podría guardar también la lista de extracción.
- `tests/test_pares.py:22-59`: las dos pruebas con el catálogo real dependen de `data/processed/lugares_nodos.csv` pero no llevan la marca `red` (se saltan si falta el archivo). Como el CSV está versionado, no pasa nada; es solo por coherencia con el criterio de `-m "not red"`.
- `docs/anexo-ia.md` (local, línea 41) menciona `test_rutas_r2` como si fuera un archivo de pruebas; es la función `tests/test_config.py::test_rutas_r2`. Precisarlo.

### Pendiente para el documento técnico
- **Invariante** (spec, punto 9): enunciado formal, prueba por inducción, ilustrada con la tabla de extracción del caso 19 (orden 1, 2, 3, 4, 5, 7, 6 con distancias 0, 1, 3, 4, 5, 8, 9).
- **Parada al sacar el destino**: por qué la distancia ya es final al extraerlo y por qué parar al **descubrirlo** sería incorrecto (contraejemplo del caso 2: D se descubre con 6 y termina en 4).
- **Pesos ≥ 0**: dónde usa la prueba la no negatividad, con un contraejemplo pequeño con peso negativo; validación en `construir_adyacencia` (peso 0 permitido).
- **Complejidad con fuentes**: lineal O(V²) tiempo y O(V) memoria; cola O((V + E) log V) tiempo y O(V + E) memoria por la inserción perezosa (hasta E + 1 entradas), con el argumento log E = O(log V) aunque haya paralelas. Costo de `heappush`/`heappop` O(log n) según la documentación de `heapq` de Python 3.13 y las «Priority Queue Implementation Notes». Citar Dijkstra (1959) y las diapositivas de clase; Cormen solo si se consulta.
- **Matriz**: 42 corridas sin destino, O(42 · (V + E) log V), y por qué basta una corrida por fila.
- **Gráfica** (`r2_tiempo_vs_explorados.png`, eje y logarítmico): discutir el modelo lineal ≈ a + c_lin·V·k frente a cola ≈ a + c_cola·k, con las pendientes medidas (≈ 0,186 ms/nodo ≈ 21 ns × V para la lineal; ≈ 0,41 µs/nodo para la cola) y el piso común por la inicialización O(V).
- **Cociente**: mediana 385,7, mínimo 44,7 (T05→T02, 8 nodos, donde pesa el costo fijo a) y máximo 507,0 (C03→F04, 1 375 nodos). Explicar por qué crece con k y se acerca a c_lin·V/c_cola ≈ 457 (y por qué el máximo lo supera un poco: en k pequeños la cola cuesta menos por nodo que su pendiente global, que dominan los pares lejanos con montículos más grandes).
- **Asimetría**: 845 de los 861 pares {i, j} son asimétricos (> 1e-6 s); el de mayor diferencia es F05–F06, con 383,2 s (2 841,9 s frente a 3 225,0 s). Explicarlo por las vías de un sentido y la relevancia para R4 (TSP asimétrico).
- **Por qué la lineal solo en 10 pares**: lo pide el enunciado. Con la pendiente medida, una consulta lineal que explore la componente entera (8 791 nodos) tardaría ≈ 1,6 s, no minutos; el aviso del enunciado aplica a redes mayores.
- **Cómo se verificó**: casos a mano 1–12, red de la clase 19–23, propiedad con 200 grafos contra NetworkX, red real contra `nx.dijkstra_path_length`, matriz releída del CSV byte a byte, comprobación entre versiones antes de medir y mutaciones.
- **Tiempo del lugar al nodo**: aclarar que el tiempo reportado es de nodo a nodo y no incluye el tramo lugar–nodo de R1.
- **Anexo de IA**: trasladar al documento las entradas de R2 de `docs/anexo-ia.md` (herramienta, propósito, verificación).

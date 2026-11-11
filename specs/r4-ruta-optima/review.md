# Revisión — R4 Ruta óptima de recorrido (TSP asimétrico)

## Ronda 1: APROBADO

Revisado sobre `main` en 053ef74 (bloques B1 a B4: 5f42530, 56c858e, 987eeab y 053ef74; T1 a T22 marcadas). Fuentes: `spec.md`, `plan.md` y `tasks.md` (con las Puertas 1 y 2), el enunciado (sección 5, Requerimiento 4, y sección 6) y el anexo (Requerimiento 4), leídos con `pdftotext -layout`.

Pruebas: ✅
- `.venv/bin/python -m pytest -m "not red" -q` → **408 passed, 1 skipped, 27 deselected** (8,1 s). El único salto es `tests/test_envolvente.py:136` (prueba lenta de R3, `--lento`).
- `.venv/bin/python -m pytest -m red -q -rs` → **25 passed, 2 skipped**. Saltos: `tests/test_red_real.py:79` (falta `data/raw/radio_2km.graphml`, de R1) y `tests/test_red_real_r4.py:118` (`test_resultados_medidos`: falta `results/r4/r4_exactas.csv`, pendiente a propósito).
- Python 3.13.18 en `.venv` (aprobado en la Puerta 2).

Comprobaciones propias, además de las suites:
- **Mutaciones** en una copia del repositorio en el scratchpad, con `PYTHONDONTWRITEBYTECODE=1` para que ningún `.pyc` viejo contaminara el resultado. El repositorio no se tocó y `git status` sigue limpio.

  | Mutación | Sin `red` | `red` de R4 |
  |---|---|---|
  | HK con `T[L[j]][L[i]]` en el paso (asimetría) | 17 fallan | 7 fallan |
  | HK con la base invertida (`T[L[j]][s]`) | 17 fallan | 7 fallan |
  | HK con el cierre invertido (`T[s][L[j]]`) | 17 fallan | 7 fallan |
  | HK sin `orden.reverse()` | 9 fallan | 1 falla |
  | Contador con `\|S\|²` en lugar de `\|S\|(\|S\|−1)` | 8 fallan | — |
  | FB con `<=` (desempate) | 3 fallan (caso 17) | — |
  | FB sin el regreso | 16 fallan | 4 fallan |
  | Permutaciones sin invertir la cola | 7 fallan | 4 fallan |
  | Voraz con `<=` | 1 falla | — |
  | Voraz sin el regreso | 10 fallan | — |
  | Itinerario que quita el de **menor** ahorro | 2 fallan | 2 fallan (19c) |
  | Itinerario con `>=` en la frontera de 660 | 2 fallan (caso 16) | — |
  | `medir_exactas` sin comparar el valor del hijo | 1 falla | — |
  | `medir_exactas` sin la verificación previa | 2 fallan | — |
  | `medicion.py` sin devolver el valor | 3 fallan | — |
  | Calidad con `min` en lugar de `max` | 1 falla | — |
  | Gráfica sin escala logarítmica | 1 falla | — |

  Sobreviven tres: el desempate por menor i y por menor j de HK (sugerencia 2) y el orden de las filas del itinerario (sugerencia 1).
- **Itinerario real por enumeración independiente** (`itertools.permutations` sobre `matriz_tiempos.csv`, script propio, fuera del repositorio):
  - 1 255,22 min con los 8 atractivos.
  - Se quita **A01** → 809,6 min. Siguientes candidatos: A12 con 1 058,7 y A08 con 1 070,3.
  - Se quita **A12** → **613,13 min**. Siguientes candidatos: A04 con 627,3 y A08 con 628,4.
  - Coincide con `r4_itinerario.json` y con el caso 19c, y los márgenes frente al segundo candidato son amplios.
- **Muestra anidada** recalculada a mano con `random.Random(2026).sample(...)`: C09, A10, F07, T04, C08, A04, F01, F06, F03, A05, C02, A09. Igual a la spec. Con k = 5 ya trae las cuatro categorías del catálogo (C, A, F y T), como pide el párrafo inicial de R4.
- **Humo del script de medición** (`--k-max 8 --repeticiones 5`, salida en el scratchpad, no en `results/r4/`):
  - FB = HK en k = 5..8.
  - Tiempos de FB: 0,056 / 0,29 / 2,11 / 17,6 ms. Tiempos de HK: 0,038 / 0,077 / 0,159 / 0,367 ms.
  - `maquina.json` registra Apple M4, 16 GB y Python 3.13.18.
  - `tablas.main` sobre esa carpeta generó la tabla del anexo, el mayor k, los cocientes y una gráfica PNG correcta, con el eje y logarítmico y la unidad en la etiqueta.
  - Extrapolación con los cocientes medidos: FB con k = 12 ≈ 4 min. Queda cerca del límite, como ya se sabía; cualquiera de los dos resultados es válido para el protocolo.

| Caso / punto del enunciado | Cumplido | Test |
|---|---|---|
| Caso 1: los 6 recorridos de la matriz de clase | ✅ | `tests/test_tsp_clase.py::test_caso_1_seis_recorridos`, `::test_caso_1_2_fuerza_bruta` |
| Caso 2: FB y HK → (35, [0, 1, 3, 2, 0]) | ✅ | `tests/test_tsp_clase.py::test_caso_1_2_fuerza_bruta`, `::test_caso_2_held_karp` |
| Caso 3: tabla de HK (12 celdas, `inf`/`None` en las demás) | ✅ | `tests/test_held_karp.py::test_caso_3_tabla`, `::test_tabla_celdas_no_usadas` |
| Caso 4: voraz 39 frente a 35 (11,43 %) | ✅ | `tests/test_tsp_clase.py::test_caso_4_voraz_no_optimo` |
| Caso 4b: la vía (16 frente a 14; 4 recorridos de 14 y 2 de 16) | ✅ | `tests/test_tsp_clase.py::test_caso_4b_via` |
| Caso 5: asimetría (el inverso cuesta 40) | ✅ | `tests/test_tsp_clase.py::test_caso_5_asimetria` |
| Casos 6, 7 y 8: k = 1, 2 y 0 en los tres métodos | ✅ | `tests/test_tsp_clase.py::test_caso_6_k1`, `::test_caso_7_k2`, `::test_caso_8_k0` |
| Caso 9: arco `inf` y sin recorrido finito | ✅ | `tests/test_tsp_clase.py::test_caso_9_arco_inf`, `::test_caso_9_sin_recorrido_finito`, `::test_vecino_regreso_inf` |
| Caso 10: errores de entrada | ✅ | `tests/test_tsp_clase.py::test_caso_10_errores`, `::test_validar_entrada_errores` |
| Caso 11: propiedad FB = HK, recorrido válido y brecha ≥ 0 (100 instancias, semilla 2026) | ✅ | `tests/test_tsp_propiedad.py::test_caso_11_fb_igual_hk_y_voraz` |
| Caso 12: FB igual a `itertools.permutations` | ✅ | `tests/test_tsp_propiedad.py::test_caso_12_fb_contra_itertools` |
| Caso 13: generador lexicográfico propio | ✅ | `tests/test_permutaciones.py::test_caso_13_orden_lexicografico`, `::test_uno_y_vacio`, `::test_no_modifica_entrada`, `::test_entrada_desordenada`, `::test_seis_elementos` |
| Caso 14: memoria estimada | ✅ | `tests/test_conteos_r4.py::test_caso_14_memoria`, `::test_caso_14_memoria_k12_en_mb` |
| Caso 15: conteos (contador de HK, fórmula y lecturas reales de `T`) | ✅ | `tests/test_held_karp.py::test_caso_15_contador`, `::test_contador_igual_a_lecturas_de_T`, `::test_sin_contador_por_defecto`; `tests/test_conteos_r4.py::test_caso_15_conteos_teoricos`, `::test_caso_15_fuerza_bruta_k12` |
| Caso 16: itinerario en la frontera (660 cabe; con 661 se quita X6, ahorro 241) | ✅ | `tests/test_itinerario.py::test_matriz_frontera_por_enumeracion`, `::test_caso_16_cabe_justo`, `::test_caso_16_quita_uno` |
| Caso 17: desempate lexicográfico de FB | ✅ | `tests/test_tsp_clase.py::test_caso_17_desempate` |
| Caso 18: envoltorio por ids | ✅ | `tests/test_por_ids.py::test_caso_18_por_ids` |
| Caso 19a: FB = HK en la red real, k = 5..8 | ✅ | `tests/test_red_real_r4.py::test_caso_19a_fb_igual_hk` |
| Caso 19b: HK con k = 12 en la red real | ✅ | `tests/test_red_real_r4.py::test_caso_19b_hk_k12` |
| Caso 19c: itinerario real (A01, luego A12; 613,1 min) | ✅ | `tests/test_red_real_r4.py::test_caso_19c_itinerario`, `::test_archivos_itinerario_reales` |
| Caso 19d: muestra anidada | ✅ | `tests/test_instancias_r4.py::test_caso_19d_muestra_anidada` |
| Caso 20: tablas y gráfica desde CSV de ejemplo; calidad = promedio y máximo | ✅ | `tests/test_tablas_r4.py::test_caso_20_tabla_exactas`, `::test_caso_20_grafica`, `::test_caso_20_calidad_e_itinerario`; `tests/test_calidad_r4.py::test_caso_20_resumen` |
| Bordes: costo 0 (T03/T05), matriz simétrica, bordes del itinerario | ✅ | `tests/test_tsp_propiedad.py::test_costo_cero_entre_lugares`, `::test_matriz_simetrica`; `tests/test_itinerario.py::test_errores`, `::test_cabe_de_entrada_no_quita`, `::test_queda_uno_si_nunca_cabe` |
| R4.1: FB y HK con implementación propia (sin itertools, NetworkX, NumPy ni SciPy en `rutas/r4/`) | ✅ | `grep` limpio (solo `math`); guardia en `tests/test_permutaciones.py::test_sin_itertools_ni_networkx` |
| R4.1: HK devuelve el recorrido | ✅ | casos 2, 11, 17 y 19b |
| R4.1: k de 5 a 12 o hasta el límite, mayor k resuelto, gráfica | ✅ código / ⏳ medición | `tests/test_medir_exactas.py::test_no_completada_y_no_ejecutada`, `tests/test_tablas_r4.py::test_mayor_k_resuelto`, `::test_caso_20_grafica` |
| R4.1: memoria según el tamaño de la tabla, más `tracemalloc` | ✅ | `tests/test_medir_memoria_r4.py`; `results/r4/r4_memoria.csv` (k = 12: 0,590 MB estimados y 1,90 MB medidos) |
| R4.1: FB = HK en los k que FB resuelve | ✅ | casos 11 y 19a; `medir_exactas` lo verifica antes de escribir (`tests/test_medir_exactas.py::test_verificacion_previa_k_pequeno`, `::test_verificacion_con_valor_del_hijo`, `::test_main_no_escribe_si_falla`) |
| R4.2: heurística voraz propia y su justificación | ✅ | `rutas/r4/vecino.py`; justificación en spec, Comportamiento 4 |
| R4.3: calidad con k = 5, 8, 10 y 12, ≥ 5 instancias (hay 10), promedio y máximo | ✅ | `tests/test_calidad_r4.py`; `results/r4/r4_calidad.csv` |
| R4.4: itinerario de 6 a 8 atractivos, HK, 11 h, quitar justificando, duración final | ✅ | casos 16 y 19c; `results/r4/r4_itinerario.csv`/`.json` |
| R4.5: voraz frente a óptimo y comparación con Dijkstra | ✅ (texto en la spec) | casos 4 y 4b |
| 6.2: solo el algoritmo | ✅ | `tests/test_medir_exactas.py::test_mide_solo_el_algoritmo`; el cronómetro solo rodea `funcion(*args)` en el hijo (`rutas/medicion.py:86-88`); el valor se envía después de `fin` |
| 6.3: 5 repeticiones y mediana, una sola si pasa de 1 min | ✅ | `tests/test_medicion.py` (modo en hijo) |
| 6.4: unidad ms | ✅ | columnas y encabezados en ms |
| 6.5: semilla fija documentada | ✅ | `results/r4/r4_instancias.json`; `tests/test_instancias_r4.py::test_main_escribe_json` |
| 6.7: límite de 5 min → «no completada», fila no omitida | ✅ | `tests/test_medicion.py::test_en_hijo_valor_no_completada`; `tests/test_medir_exactas.py::test_no_completada_y_no_ejecutada`; `tests/test_tablas_r4.py::test_caso_20_tabla_exactas` |
| 6.8: tablas y gráfica desde CSV/JSON, con la unidad | ✅ | `tests/test_tablas_r4.py` (CSV de ejemplo en `tmp_path`) |
| Cambio en `rutas/medicion.py`, compatible con R1–R3 | ✅ | suites de R1–R3 en verde sin cambios; `tests/test_medicion.py::test_en_hijo_sin_valor_por_defecto` |
| Anexo: columnas de las tres tablas, fila «Regreso» con «—» y totales | ✅ | `results/r4/tablas_r4.md`; `tests/test_itinerario.py::test_escribir_itinerario` |

Correctitud frente a la spec (lectura del código):
- **Fuerza bruta** (`rutas/r4/fuerza_bruta.py:22-29`): k! permutaciones en orden lexicográfico, costo completo en O(k) por permutación, reemplazo con `<` estricto y sin poda. Si todo es `inf`, `mejor_orden` queda en `None` y lanza `ValueError`.
- **Held-Karp** (`rutas/r4/held_karp.py`):
  - La base (l. 31), el paso con máscaras en orden creciente y los i en orden creciente con `<` (l. 37-55) y el cierre con `<` (l. 77-81) son los de la spec, punto 3.
  - La reconstrucción (l. 89-94) recorre `padre` hasta `None` e invierte.
  - El contador solo hace una comparación `is not None` por máscara. En la medición no se pasa contador, así que no afecta el tiempo.
- **Vecino más cercano** (`rutas/r4/vecino.py`): O(k²), desempate por menor índice al recorrer `sorted(lugares)` con `<`. El regreso `inf` da `ValueError`.
- **Script de medición** (`rutas/r4/medir_exactas.py`):
  - HK del proceso principal como referencia y FB previa para k ≤ 9, las dos fuera del cronómetro.
  - El valor del hijo se compara con la referencia para los dos métodos.
  - Tras `no_completada`, los k mayores de ese método quedan `no_ejecutada`.
  - Solo escribe al final, si todo pasó.
  - Cumple los puntos 5 y 10 de la spec y la sección 6.

### Bloqueantes
Ninguno.

### Sugerencias (no bloquean)
1. `tests/test_itinerario.py:67-79` (`test_filas_y_acumulado`): en la matriz de frontera cualquier orden de los atractivos cuesta 300 min, así que la prueba no detecta filas que no sigan el recorrido de HK. La mutación `enumerate(sorted(recorrido[1:-1]))` en `rutas/r4/itinerario.py:65` pasó las dos suites. Falta una prueba con una matriz donde el orden importe, por ejemplo la de clase con 6 atractivos, o una aserción en `test_caso_19c_itinerario` (`tests/test_red_real_r4.py:50`) de que `[f["id"] for f in filas[:-1]]` es el recorrido de `held_karp` sobre los atractivos finales y de que la suma de `desplazamiento_min` es `jornada_min − visitas_min`. Hoy el archivo real es coherente (103,13 + 510 = 613,13), pero ninguna prueba lo ata.
2. `rutas/r4/held_karp.py:51` y `:79`: los desempates «menor i» y «menor j» de la spec (Comportamiento 3) no tienen prueba. Las mutaciones a `<=` sobreviven, porque la spec decidió comparar solo tiempos en los empates de HK. Es coherente con la spec, pero si el informe afirma esos desempates, convendría una prueba pequeña con la matriz del caso 17, todos los arcos iguales, que fije el recorrido de HK.
3. `tests/test_permutaciones.py:14`: la guardia busca `"import numpy"`, así que `from numpy import …` pasaría, y no incluye `scipy`. Sugerencia: buscar `numpy` y `scipy` como palabras.
4. `rutas/r4/tablas.py:89-95`: el eje x muestra marcas fraccionarias (5,5; 6,5…). `ax.xaxis.set_major_locator(MaxNLocator(integer=True))` deja solo los k enteros.
5. `rutas/r4/itinerario.py:57-59`: la spec (Comportamiento 8) justifica cada salida con su ahorro «visita + desvío». El JSON solo trae el ahorro total. Agregar `visita_min` del atractivo quitado (y `desvio_min = ahorro − visita`) ayudaría al párrafo del informe. En los datos reales, A01 ahorra 445,6 min, de los cuales 420 son de visita, y A12 ahorra 196,5.
6. `specs/r4-ruta-optima/spec.md:3`: la línea «Estado» todavía marca ☐ pruebas · ☐ código. Actualizarla al cerrar.

### Pendiente para el documento técnico
- **Cierre de R4 (pendientes a propósito, no son hallazgos):**
  - La medición real de las soluciones exactas (`.venv/bin/python -m rutas.r4.medir_exactas`, con el portátil enchufado). Produce `results/r4/r4_exactas.csv` y `maquina.json`.
  - Después, `python -m rutas.r4.tablas` para la gráfica `r4_tiempo_vs_k.png` y la tabla de tiempos.
  - Luego `pytest -m red` para que `test_resultados_medidos` deje de saltarse.
  - T23 (README «Reproducir R4», nota de Python 3.13.18 y la entrada final del anexo de IA).
  - T24 (suite completa y regeneración).
  - El humo confirma que el script y las tablas producen el formato del anexo.
- Tabla del anexo con los tiempos de FB y HK, el mayor k de cada método y un párrafo con los cocientes medidos frente a los predichos. En el humo, HK da ≈ 2,0–2,3 frente a 2,6–2,9 predicho en k pequeños: el informe debe explicar que con k pequeño el costo fijo de Python pesa más que el término k²·2^k.
- Gráfica de tiempo frente a k con eje logarítmico y unidad.
- Memoria estimada frente al pico de `tracemalloc` (0,590 frente a 1,90 MB en k = 12), con la explicación de los objetos `list` y `float`. La estimación del plan, ≈ 2 MB, acierta.
- Subestructura óptima y recurrencia, ilustradas con la tabla del caso 3.
- Complejidades con sus fuentes: Held y Karp (1962), Bellman (1962), Knuth (TAOCP 4A, §7.2.1.2), Cormen §34.5.4 y Rosenkrantz, Stearns y Lewis (1977). Ya están en la spec y en el plan; hay que pasarlas al documento.
- Tabla de calidad (5,9 / 9,7 / 10,6 / 11,8 % de promedio; máximo 28,2 % con k = 12) y su discusión.
- Itinerario con la justificación de A01 y A12 y la duración final de 613,1 min (10,22 h).
- Voraz frente a óptimo (casos 4 y 4b) y comparación con el invariante de Dijkstra de R2.
- Cómo se verificó cada algoritmo: a mano, con FB = HK, con `itertools` y con la enumeración independiente del itinerario.

# Tareas — R4 Ruta óptima de recorrido (TSP asimétrico)

Spec: `spec.md` · Plan: `plan.md`. Todas las órdenes se corren desde la raíz del repositorio (`/Users/nicolascastro/Desktop/proyecto-final-rutas-quindio`) con `.venv/bin/python` (lo crea o comprueba T1).

Cada tarea en la que se use IA termina con: **anotar en `docs/anexo-ia.md`** (fecha, integrante, herramienta, qué se generó, cómo se verificó).

> **Reglas del usuario:**
> 1. Cada bloque termina con todas sus pruebas en verde y el trabajo se **DETIENE** hasta que el usuario haga su commit. No se empieza el bloque siguiente antes.
> 2. Test primero **tarea por tarea**: escribir la prueba de una tarea, verla fallar por la razón correcta (el módulo existe con funciones que hacen `raise NotImplementedError`; no un `ModuleNotFoundError` global) y solo entonces escribir el código. El reporte de cada bloque lo confirma tarea por tarea.
> 3. No modificar `.gitignore` sin preguntar (conserva `docs/` y `.DS_Store`). `docs/` está ignorada: `docs/anexo-ia.md` se mantiene en local.
> 4. Nunca `git add`, `git commit` ni `git push`.
> 5. La medición de tiempos real (`rutas.r4.medir_exactas`) la corre el usuario con el portátil enchufado: la tarea termina **entregándole el comando exacto**. El implementer solo hace corridas cortas de humo con salida en una carpeta temporal (la del *scratchpad* de su sesión), nunca en `results/r4/`.

> **Simplicidad:** código legible que cada integrante pueda explicar. Un algoritmo por módulo, corto y fiel a la spec: la FB es un ciclo sobre el generador que suma cada recorrido completo; Held-Karp sigue el esqueleto del plan (máscaras crecientes, `<` estricto, reconstrucción con `padre`); el vecino es un ciclo de k pasos. Los algoritmos trabajan con **índices** y `T` como lista de listas de `float`; la traducción por ids vive solo en `por_ids.py` y en los scripts. `itertools` y NetworkX no aparecen en `rutas/r4/` (solo `itertools` en las pruebas). Los scripts leen el catálogo con `pandas.read_csv(catalogo)` (como `rutas.r2.matriz.main`; el catálogo ya lo valida R1), así las pruebas pueden pasarles catálogos pequeños.

Matriz de clase usada en varias pruebas (segundos, partida 0, lugares `[1, 2, 3]`), definida una vez como constante `T_CLASE` en `tests/test_tsp_clase.py` y reutilizada por import en los demás archivos:

```python
T_CLASE = [[0, 10, 15, 20], [5, 0, 9, 10], [6, 13, 0, 12], [8, 8, 9, 0]]
```

Las pruebas de los casos 6–10 de `tests/test_tsp_clase.py` están parametrizadas con la lista `METODOS_CLASE`, que **crece** con los bloques: T5 la crea con `fuerza_bruta`, T6 agrega `vecino_mas_cercano` y T8 agrega `held_karp`. Así cada bloque termina en verde sin `xfail`.

## B1 · Entorno, configuración, generador, fuerza bruta y vecino más cercano (casos de clase)

- [x] T1 · Entorno virtual según el README
  - Archivos: ninguno versionado (crea `.venv/`; **no** tocar `.gitignore`)
  - Pasos: si existe `.venv/bin/python` y su versión es 3.13.x, solo comprobar. Si no existe: comprobar `command -v python3.13`. **Si `python3.13` no está instalado (hoy no lo está: `python3` es 3.14.6), detenerse y preguntar al usuario** (opciones en el plan, «Decisiones para el usuario», 3); no instalar Python ni usar otra versión sin su respuesta. Con 3.13 disponible: `python3.13 -m venv .venv && .venv/bin/pip install -r requirements.txt`
  - Test primero: no aplica (entorno)
  - Verificar: `.venv/bin/python --version && .venv/bin/python -c "import networkx, osmnx, scipy, pandas, matplotlib, psutil, pytest; print('ok')" && .venv/bin/python -m pytest -m "not red" -q` (la suite actual de R1–R3 en verde antes de empezar R4)

- [x] T2 · Paquete `rutas/r4`, `RESULTS_R4` y guardia de dependencias
  - Archivos: `rutas/r4/__init__.py` (vacío); `rutas/config.py` (agregar `RESULTS_R4 = RAIZ / "results" / "r4"`; no tocar lo demás); stubs con `raise NotImplementedError` y sus docstrings del plan en `rutas/r4/permutaciones.py`, `recorrido.py`, `fuerza_bruta.py`, `held_karp.py`, `vecino.py`, `conteos.py`
  - Test primero: `tests/test_config.py::test_rutas_r4` (`RESULTS_R4 == RAIZ / "results" / "r4"`); `tests/test_permutaciones.py::test_sin_itertools_ni_networkx` (lee el texto de cada `rutas/r4/*.py` y comprueba que no contiene `itertools`, `networkx` ni `import numpy`). La primera falla con `ImportError` de `RESULTS_R4`; la segunda pasa con los stubs y queda como guardia para todo R4
  - Verificar: `.venv/bin/python -m pytest tests/test_config.py tests/test_permutaciones.py -k "r4 or itertools"`
  - anotar en `docs/anexo-ia.md`

- [x] T3 · Generador propio de permutaciones lexicográficas (caso 13; Comportamiento 1)
  - Archivos: `rutas/r4/permutaciones.py` (implementar `permutaciones_lexicograficas` con el algoritmo L, como en el plan: copia ordenada, buscar i, buscar j, intercambiar, invertir la cola; entrega tuplas)
  - Test primero: `tests/test_permutaciones.py::test_caso_13_orden_lexicografico` (`list(permutaciones_lexicograficas([0, 1, 2, 3])) == list(itertools.permutations([0, 1, 2, 3]))`, 24 elementos, `len(set(...)) == 24`), `::test_uno_y_vacio` (`[5]` → `[(5,)]`; `[]` → `[()]`), `::test_no_modifica_entrada` (lista `[3, 1, 2]`: después de consumir el generador sigue `[3, 1, 2]`), `::test_entrada_desordenada` (`[3, 1, 2]` → empieza en `(1, 2, 3)` y es igual a `itertools.permutations([1, 2, 3])`), `::test_seis_elementos` (720 permutaciones iguales a `itertools.permutations(range(6))`)
  - Verificar: `.venv/bin/python -m pytest tests/test_permutaciones.py`
  - anotar en `docs/anexo-ia.md`

- [x] T4 · Validación de la entrada y costo de un recorrido (casos 1, 5, 10)
  - Archivos: `rutas/r4/recorrido.py` (`validar_entrada(T, s, lugares)`: `ValueError` si `s` o un lugar no está en `range(len(T))` (negativos incluidos), si hay repetidos o si `s` está en `lugares`, con mensaje que nombra el problema; `costo_recorrido(T, recorrido)` → `float`, `[s]` → `0.0`)
  - Test primero: `tests/test_tsp_clase.py::test_caso_1_seis_recorridos` (`costo_recorrido` de los 6 recorridos `[0, a, b, c, 0]` de la spec: 39, 35, 46, 40, 43, 47), `::test_caso_5_asimetria` (`costo_recorrido(T_CLASE, [0, 2, 3, 1, 0]) == 40` y ≠ 35), `::test_costo_recorrido_bordes` (`[0]` → `0.0` y es `float`; con un arco `inf` → `inf`), `::test_validar_entrada` (parametrizada: `[1, 1]`, `[0, 1]` con s = 0, `[7]`, `[-1]` y `s = 9` → `ValueError`; `[1, 2, 3]` no lanza)
  - Verificar: `.venv/bin/python -m pytest tests/test_tsp_clase.py -k "caso_1_seis or caso_5 or costo_recorrido or validar"`
  - Nota: `test_validar_entrada` quedó como dos pruebas, `test_validar_entrada_errores` (parametrizada) y `test_validar_entrada_correcta`; ambas contienen «validar» en el nombre.
  - anotar en `docs/anexo-ia.md`

- [x] T5 · Fuerza bruta (casos 1, 2, 4b, 6, 7, 8, 9, 10, 17; Comportamiento 1)
  - Archivos: `rutas/r4/fuerza_bruta.py` (implementar según el plan: `validar_entrada`; k = 0 → `(0.0, [s])`; ciclo sobre `permutaciones_lexicograficas(lugares)` sumando el costo completo en un ciclo; reemplazo solo con `<`; `ValueError("no hay recorrido finito")` si el mejor sigue en `inf`)
  - Test primero (en `tests/test_tsp_clase.py`; crear `METODOS_CLASE = [fuerza_bruta]` y parametrizar con ella las de los casos 6–10): `::test_caso_1_2_fuerza_bruta` (`(35, [0, 1, 3, 2, 0])`), `::test_caso_4b_via` (posiciones A = 0, B = 1, C = −2, D = 5 con índices A = 0, B = 1, C = 2, D = 3; `T[i][j] = |pos_i − pos_j|`; enumerando con `itertools.permutations([1, 2, 3])`: 4 recorridos de 14 y 2 de 16; FB → `(14, [0, 1, 3, 2, 0])`), `::test_caso_6_k1` (`[1]` → `(15, [0, 1, 0])`), `::test_caso_7_k2` (`[1, 2]` → `(25, [0, 1, 2, 0])`), `::test_caso_8_k0` (`[]` → `(0.0, [0])`), `::test_caso_9_arco_inf` (copia con `T[1][3] = inf` → `(39, [0, 1, 2, 3, 0])`), `::test_caso_9_sin_recorrido_finito` (`T[0][j] = inf` para j = 1, 2, 3 → `ValueError`), `::test_caso_10_errores` (método × `[1, 1]`, `[0, 1]`, `[7]` → `ValueError`), `::test_caso_17_desempate` (todos los arcos fuera de la diagonal = 1: FB → `[0, 1, 2, 3, 0]` y costo 4), `::test_no_modifica_entradas` (método × copia profunda de `T` y de `lugares` antes y comparación después)
  - Ver fallar: con `NotImplementedError` del stub
  - Verificar: `.venv/bin/python -m pytest tests/test_tsp_clase.py`
  - anotar en `docs/anexo-ia.md`

- [x] T6 · Vecino más cercano (casos 4, 4b, 6–10; Comportamiento 4; puntos 2 y 5)
  - Archivos: `rutas/r4/vecino.py` (implementar según el plan: `validar_entrada`; k = 0 → `(0.0, [s])`; `orden = sorted(lugares)` y `visitado` como lista de `bool` paralela; en cada paso se recorre `orden` y se cambia de candidato solo con `<` (empate → menor índice); mínimo `inf` → `ValueError`; regreso a `s`; total `inf` → `ValueError("no hay recorrido finito")`)
  - Test primero: agregar `vecino_mas_cercano` a `METODOS_CLASE` (casos 6–10: k = 1 → 15; k = 2 → 25; k = 0; `T[1][3] = inf` → 39; todo `inf` desde 0 → `ValueError`; errores); `tests/test_tsp_clase.py::test_caso_4_voraz_no_optimo` (`(39, [0, 1, 2, 3, 0])`; brecha `(39 − 35) / 35 × 100` = `pytest.approx(11.428571, abs=1e-4)`), `::test_caso_4b_via` (ampliar: voraz → `(16, [0, 1, 2, 3, 0])`, brecha ≈ 14,29 %), `::test_vecino_desempate_menor_indice` (fila de la partida con dos mínimos iguales: elige el de menor índice), `::test_vecino_regreso_inf` (todos los arcos hacia la partida `inf` → `ValueError`)
  - Ver fallar: con `NotImplementedError` del stub
  - Verificar: `.venv/bin/python -m pytest tests/test_tsp_clase.py`
  - anotar en `docs/anexo-ia.md`

**Fin de B1:** `.venv/bin/python -m pytest -m "not red"` en verde. **Detenerse** y entregar el reporte (tarea por tarea: prueba escrita, fallo visto y su razón, prueba en verde). Esperar el commit del usuario.

## B2 · Held-Karp con su tabla, contador, conteos, memoria y propiedades

- [x] T7 · Tabla de Held-Karp (caso 3; Comportamiento 3)
  - Archivos: `rutas/r4/held_karp.py` (implementar `tabla_held_karp(T, s, lugares, contador=None)` según el plan: `L = sorted(lugares)`; `costo` y `padre` de 2^k listas de k elementos con `math.inf`/`None`; base `costo[1 << j][j] = T[s][L[j]]`; máscaras crecientes con ≥ 2 bits; para cada j del conjunto, i en orden creciente con `<` estricto; lectura `T[L[i]][L[j]]` una vez por transición; el contador todavía no se usa; `held_karp` sigue como stub)
  - Test primero: `tests/test_held_karp.py::test_caso_3_tabla` (`T_CLASE`, s = 0, lugares `[1, 2, 3]`: las 12 celdas usadas de la spec, escritas como `{(mascara, lugar): (C, padre_lugar)}` y traducidas en la prueba con índice local = lugar − 1; p. ej. `costo[0b001][0] == 10` y `padre[0b001][0] is None`; `costo[0b011][0] == 28` y `padre[0b011][0] == 1` (lugar 2); `costo[0b111][1] == 29` y `padre[0b111][1] == 2` (lugar 3)), `::test_tabla_celdas_no_usadas` (máscara 0 y las celdas con j ∉ S quedan `inf` / `None`; dimensiones 8 × 3), `::test_tabla_lugares_desordenados` (lugares `[3, 1, 2]` → misma tabla que `[1, 2, 3]`)
  - Verificar: `.venv/bin/python -m pytest tests/test_held_karp.py -k "tabla"`
  - anotar en `docs/anexo-ia.md`

- [x] T8 · `held_karp`: cierre y reconstrucción del recorrido (casos 2, 4b, 5–10, 17; punto 1 «devolver el recorrido»)
  - Archivos: `rutas/r4/held_karp.py` (implementar `held_karp` según el esqueleto del plan: `validar_entrada`; k = 0 → `(0.0, [s])`; cierre con `<` estricto (gana el menor j); `ValueError("no hay recorrido finito")` si el óptimo es `inf`; reconstrucción con `padre` hacia atrás, invertida, traducida con `L`)
  - Test primero: agregar `held_karp` a `METODOS_CLASE` (casos 6–10); `tests/test_tsp_clase.py::test_caso_2_held_karp` (`(35, [0, 1, 3, 2, 0])`), `::test_caso_4b_via` (ampliar: HK → costo 14 y recorrido válido con `costo_recorrido` = 14), `::test_caso_5_asimetria` (ampliar: el recorrido de HK no es el inverso `[0, 2, 3, 1, 0]`), `::test_caso_17_desempate` (ampliar: HK → costo 4, recorrido permutación válida de `[1, 2, 3]` con `costo_recorrido` = 4)
  - Ver fallar: con `NotImplementedError` del stub
  - Verificar: `.venv/bin/python -m pytest tests/test_tsp_clase.py tests/test_held_karp.py`
  - anotar en `docs/anexo-ia.md`

- [x] T9 · Contador opcional de transiciones (caso 15, parte medida; sección 6.2)
  - Archivos: `rutas/r4/held_karp.py` (en `tabla_held_karp`, si `contador is not None`: `contador[0] += k` en la base y `+= len(bits) * (len(bits) - 1)` **una vez por máscara**, nunca dentro del ciclo interno; en `held_karp`, `+= k` en el cierre)
  - Test primero: `tests/test_held_karp.py::test_caso_15_contador` (parametrizada k = 3, 5, 8, 10, 12 con matrices aleatorias de enteros 1..100, `random.Random(2026)`: `c = [0]; held_karp(T, 0, list(range(1, k + 1)), contador=c)` → `c[0]` = 18, 170, 3 600, 23 060, 135 192), `::test_contador_igual_a_lecturas_de_T` (k = 3, 5, 8: cada fila envuelta en `class FilaContada(list)` cuyo `__getitem__` suma 1 a un contador compartido; las lecturas de `T` durante `held_karp` son iguales a `c[0]`), `::test_sin_contador_por_defecto` (`inspect.signature(held_karp).parameters["contador"].default is None` y `held_karp(T, s, lugares)` con 3 argumentos funciona)
  - Ver fallar: `c[0]` queda en 0 con el código de T8 (el contador aún no se incrementa)
  - Verificar: `.venv/bin/python -m pytest tests/test_held_karp.py -k "contador or lecturas"`
  - anotar en `docs/anexo-ia.md`

- [x] T10 · Memoria estimada y conteos teóricos (casos 14 y 15, parte teórica; punto 1 «estimar memoria»)
  - Archivos: `rutas/r4/conteos.py` (`memoria_held_karp(k)` y `conteos_teoricos(k)` según el plan; `math.factorial` está permitido: no es un algoritmo del enunciado)
  - Test primero: `tests/test_conteos_r4.py::test_caso_14_memoria` (k = 5: 160 celdas, 1 920 B; k = 8: 2 048, 24 576; k = 10: 10 240, 122 880; k = 12: 49 152 celdas, 589 824 B, `mb_estimados == pytest.approx(0.589824)`), `::test_caso_15_conteos_teoricos` (transiciones k = 3, 5, 8, 10, 12 → 18, 170, 3 600, 23 060, 135 192; k = 12: `permutaciones_fb == 479_001_600`, `tramos_fb == 6_227_020_800`), `::test_conteos_bordes` (k = 0 → 0 transiciones; k = 1 → 2)
  - Verificar: `.venv/bin/python -m pytest tests/test_conteos_r4.py`
  - anotar en `docs/anexo-ia.md`

- [x] T11 · Propiedades: FB = HK, FB = `itertools`, voraz ≥ óptimo y bordes (casos 11, 12; bordes de la spec)
  - Archivos: `tests/test_tsp_propiedad.py` (solo pruebas)
  - Test primero: `::test_caso_11_fb_igual_hk_y_voraz` (`random.Random(2026)`; 100 instancias: n = k + 1 con k entre 1 y 8, `T[i][j]` entero de 1 a 100 para i ≠ j (asimétrica), s = 0, `lugares = list(range(1, n))` barajados; FB y HK con el mismo tiempo (±1e-6); el recorrido de HK empieza y termina en `s`, contiene cada lugar una vez y su `costo_recorrido` coincide (±1e-6); voraz ≥ óptimo − 1e-9), `::test_caso_12_fb_contra_itertools` (mismas instancias, regeneradas con la misma semilla: el tiempo de FB = `min` de los costos de `itertools.permutations(lugares)`), `::test_costo_cero_entre_lugares` (dos lugares con `T` = 0 entre ellos, como T03/T05: los tres métodos sin error y FB = HK), `::test_matriz_simetrica` (matriz simétrica aleatoria: el inverso del recorrido de HK cuesta lo mismo; FB = HK)
  - Ver fallar: el código ya existe; se valida con una **mutación temporal** en `tabla_held_karp` (sumar `T[L[j]][L[i]]` en lugar de `T[L[i]][L[j]]`) que debe hacer fallar el caso 11, y se restaura. Anotar en el reporte el resultado de la mutación
  - Verificar: `.venv/bin/python -m pytest tests/test_tsp_propiedad.py`
  - anotar en `docs/anexo-ia.md`

**Fin de B2:** `.venv/bin/python -m pytest -m "not red"` en verde. **Detenerse** y entregar el reporte. Esperar el commit del usuario.

## B3 · Instancias, envoltorio por ids, itinerario y pruebas con la red real

- [x] T12 · Instancias con semilla fija y `r4_instancias.json` (caso 19d; párrafo inicial de R4; sección 6.5)
  - Archivos: `rutas/r4/instancias.py` (constantes, `otros_ids`, `muestra_anidada`, `instancias_calidad` y `main(catalogo=CATALOGO, salida=RESULTS_R4)` según el plan; `if __name__ == "__main__": main()`)
  - Test primero: `tests/test_instancias_r4.py::test_caso_19d_muestra_anidada` (ids de `data/catalogo.csv`: `muestra_anidada(ids) == ["C09", "A10", "F07", "T04", "C08", "A04", "F01", "F06", "F03", "A05", "C02", "A09"]`; sin marcador `red`, solo usa el catálogo versionado), `::test_otros_ids` (41 ids, sin `C01`, en orden del catálogo), `::test_instancias_calidad` (40 instancias, 10 por k en el orden `K_CALIDAD` × `SEMILLAS_CALIDAD`; cada una con k ids distintos sin `C01`; reproducible: dos llamadas dan lo mismo; la de k = 5 y semilla 2027 es `random.Random(2027).sample(otros, 5)`), `::test_main_escribe_json` (`tmp_path`: claves del plan, `"semilla": 2026`, 12 ids en `muestra_anidada`, 40 en `calidad`)
  - Ejecutar (no es medición): `.venv/bin/python -m rutas.r4.instancias` → `results/r4/r4_instancias.json`
  - Verificar: `.venv/bin/python -m pytest tests/test_instancias_r4.py`
  - anotar en `docs/anexo-ia.md`

- [x] T13 · Envoltorio por ids (caso 18; consumidor R5)
  - Archivos: `rutas/r4/por_ids.py` (`METODOS`, `matriz_a_listas`, `resolver_por_ids` según el plan)
  - Test primero: `tests/test_por_ids.py::test_caso_18_por_ids` (`DataFrame` con índice y columnas `["C01", "A01", "A02", "A03"]` y los valores de `T_CLASE`: `resolver_por_ids(df, "C01", ["A01", "A02", "A03"], "held_karp") == (35, ["C01", "A01", "A03", "A02", "C01"])`; igual con `"fuerza_bruta"`; con `"vecino_mas_cercano"` → `(39, ["C01", "A01", "A02", "A03", "C01"])`), `::test_matriz_a_listas_floats_de_python` (`type(T[0][1]) is float`, no `numpy.float64`; ids en el orden del índice), `::test_errores` (método desconocido, id desconocido y columnas ≠ índice → `ValueError`), `::test_matriz_csv_ida_y_vuelta` (escribir la matriz con `rutas.r2.matriz.guardar_matriz` en `tmp_path`, leerla con `cargar_matriz` y resolver: mismo resultado)
  - Verificar: `.venv/bin/python -m pytest tests/test_por_ids.py`
  - anotar en `docs/anexo-ia.md`

- [x] T14 · Itinerario de un día (caso 16; bordes del itinerario; punto 4)
  - Archivos: `rutas/r4/itinerario.py` (`JORNADA_MAX_MIN`, `ATRACTIVOS_DIA` e `itinerario_dia` según el plan; `visitas_del_catalogo`, `escribir_itinerario` y `main` quedan como stubs hasta T15)
  - Test primero: `tests/test_itinerario.py` con la matriz del plan (partida 0; atractivos 1..5 en un punto P con arcos 0 entre ellos; 6 en Q; en minutos 0↔P = 60, P↔Q = 90, 0↔Q = 150; `T` en segundos; `visita_min = {1: 60, …, 6: 60}`; `ids = ["S", "X1", …, "X6"]`): `::test_matriz_frontera_por_enumeracion` (con `itertools.permutations` el óptimo es 300 min, y 301 en la variante con 0↔Q = 151; en la variante, quitar 6 deja 120 min y quitar cualquiera de 1..5 deja 301), `::test_caso_16_cabe_justo` (jornada 660,0 → `cabe` y `quitados == []`), `::test_caso_16_quita_uno` (variante 301: jornada inicial 661; `quitados` tiene un solo elemento con id `X6`, `jornada_antes_min == 661`, `jornada_despues_min == 420`, `ahorro_min == 241` (todos con `pytest.approx`); `totales["cabe"]`), `::test_filas_y_acumulado` (en el caso 660: 6 filas numeradas 1..6 y la fila `Regreso` con `id == "S"` y `visita_min is None`; `acumulado_h` creciente; el de `Regreso` = `jornada_min / 60`; Σ `desplazamiento_min` = `totales["desplazamientos_min"]` = `held_karp(...)[0] / 60`), `::test_cabe_de_entrada_no_quita`, `::test_errores` (5 atractivos, 9 atractivos, un índice que no está en `visita_min`, repetidos, partida entre los atractivos → `ValueError`), `::test_queda_uno_si_nunca_cabe` (`jornada_max_min` muy pequeña: termina con un atractivo y `cabe` falso, sin error)
  - Verificar: `.venv/bin/python -m pytest tests/test_itinerario.py`
  - Nota: la matriz de frontera del plan (0↔Q = 151 simétrica) no da 301 por enumeración: 0→P→Q→P→0 cuesta 300 sin importar 0↔Q. Se usó una línea S–P–Q con Q→P = 91 y Q→S = 151 (asimétrica), que da 300 en el caso base, 301 en la variante, 120 sin el 6 y 301 sin cualquiera de 1..5; la propia prueba lo comprueba por enumeración. `totales["atractivos_finales"]` es el número de atractivos (el JSON trae la lista de ids).
  - anotar en `docs/anexo-ia.md`

- [x] T15 · Archivos del itinerario por defecto (`r4_itinerario.csv` y `.json`; Anexo, Requerimiento 4)
  - Archivos: `rutas/r4/itinerario.py` (implementar `visitas_del_catalogo(catalogo_df, ids)` (solo filas con `categoria == "Atractivo turístico"`), `escribir_itinerario(...)` y `main(matriz=MATRIZ_TIEMPOS, catalogo=CATALOGO, salida=RESULTS_R4, partida=PARTIDA, atractivos=ATRACTIVOS_DIA)` (lee el catálogo con `pd.read_csv`); `if __name__ == "__main__": main()`; imprime los quitados, la jornada final y si cabe)
  - Test primero: `tests/test_itinerario.py::test_visitas_del_catalogo` (con el catálogo real: 15 entradas; A01 → 420, A05 → 60; C01 no está), `::test_escribir_itinerario` (`tmp_path`, datos del caso 16 variante 301: CSV con encabezado `orden,id,lugar,desplazamiento_min,visita_min,acumulado_h`, 6 filas, la última `Regreso` con visita `—`; JSON con `quitados[0]["id"] == "X6"`, `ahorro_min == 241`, `cabe` verdadero, totales en min y h), `::test_main_sintetico` (matriz escrita con `guardar_matriz` y catálogo mínimo de 7 filas en `tmp_path`: escribe los dos archivos)
  - Ejecutar (no es medición): `.venv/bin/python -m rutas.r4.itinerario` → `results/r4/r4_itinerario.csv` y `.json`
  - Verificar: `.venv/bin/python -m pytest tests/test_itinerario.py`
  - anotar en `docs/anexo-ia.md`

- [x] T16 · Pruebas con la red real (casos 19a, 19b, 19c; marcador `red`)
  - Archivos: `tests/test_red_real_r4.py` (crear con `pytestmark = pytest.mark.red`; fixture que carga `MATRIZ_TIEMPOS` con `cargar_matriz` y `matriz_a_listas`, y se salta si el archivo no existe)
  - Test primero: `::test_caso_19a_fb_igual_hk` (parametrizada k = 5..8: muestra anidada, s = índice de C01; FB y HK con el mismo tiempo ±1e-6), `::test_caso_19b_hk_k12` (k = 12: recorrido de HK empieza y termina en C01, visita los 12 una vez y `costo_recorrido` = valor ±1e-6), `::test_caso_19c_itinerario` (partida C01 y `ATRACTIVOS_DIA` con `visitas_del_catalogo`: `[q["id"] for q in quitados] == ["A01", "A12"]`, `abs(totales["jornada_min"] − 613.1) ≤ 0.1`, 6 atractivos finales, `cabe`; la jornada inicial ≈ 1 255,2 y tras quitar A01 ≈ 809,6, ±0,1), `::test_archivos_itinerario_reales` (se salta si falta `results/r4/r4_itinerario.json`: coincide con 19c)
  - Ver fallar: el código ya existe; se valida con una **mutación temporal** en `itinerario_dia` (quitar el atractivo con **menor** ahorro) que debe hacer fallar el 19c, y se restaura
  - Verificar: `.venv/bin/python -m pytest tests/test_red_real_r4.py`
  - anotar en `docs/anexo-ia.md`

**Fin de B3:** `.venv/bin/python -m pytest` en verde (incluidas las `red` de R1–R4, ninguna de R4 saltada); `results/r4/r4_instancias.json`, `r4_itinerario.csv` y `r4_itinerario.json` generados. **Detenerse** y entregar el reporte con los atractivos quitados, su ahorro y la jornada final. Esperar el commit del usuario.

## B4 · Medición, memoria, calidad, tablas y gráfica

- [x] T17 · `medir_en_hijo` devuelve el valor de la función (opcional, compatible; spec punto 10) — **requiere la confirmación de la Puerta 2** (plan, «Decisiones para el usuario», 1)
  - Archivos: `rutas/medicion.py` (campo `valor: object = None` al final de `ResultadoMedicion`; `_cronometrar_en_hijo(funcion, args, cola, devolver_valor=False)` pone `(ns, resultado)` en la cola **después** de detener el cronómetro; `medir_en_hijo(..., devolver_valor=False)` guarda el valor de la primera repetición; con `False` todo igual que hoy)
  - Test primero: `tests/test_medicion.py::test_en_hijo_devuelve_valor` (`medir_en_hijo(math.sqrt, (16.0,), repeticiones=2, devolver_valor=True)` → `valor == 4.0`, `completada`), `::test_en_hijo_sin_valor_por_defecto` (sin el parámetro: `valor is None`), `::test_en_hijo_valor_no_completada` (`time.sleep` que pasa del límite con `devolver_valor=True` → `completada` falso, `valor is None`), `::test_en_hijo_devuelve_tupla_con_lista` (`held_karp` con `T_CLASE` en el hijo → `valor == (35.0, [0, 1, 3, 2, 0])`)
  - Verificar: `.venv/bin/python -m pytest tests/test_medicion.py && .venv/bin/python -m pytest -m "not red" -q` (las pruebas de R1–R3 que usan `ResultadoMedicion` siguen en verde sin cambios)
  - anotar en `docs/anexo-ia.md`

- [x] T18 · Script de medición de las soluciones exactas (punto 1; spec Comportamiento 5 y 10; sección 6)
  - Archivos: `rutas/r4/medir_exactas.py` (stubs primero; luego `COLUMNAS`, `METODOS_EXACTOS`, `TOLERANCIA_S`, `K_VERIFICACION_PREVIA`, `medir_exactas(T, ids, s, muestra, ks=K_EXACTAS, repeticiones=5, medir=medir_en_hijo)` y `main(matriz=MATRIZ_TIEMPOS, salida=RESULTS_R4, ks=K_EXACTAS, repeticiones=5)` según el plan; `if __name__ == "__main__": main()`; errores explícitos con `ValueError`, no `assert`; escribe `r4_exactas.csv` y `maquina.json` solo al final)
  - Test primero: `tests/test_medir_exactas.py` con un medidor falso que registra `(funcion, args, devolver_valor)`, corre la función en el proceso y devuelve un `ResultadoMedicion` fijo con su valor: `::test_mide_solo_el_algoritmo` (cada llamada recibe `fuerza_bruta` o `held_karp` y `args == (T, s, lugares)` con `T` lista de listas e índices; `devolver_valor=True`), `::test_filas_y_columnas` (matriz aleatoria de 7 lugares, `ks=(2, 3)`: 4 filas en orden k y luego `fuerza_bruta`, `held_karp`; `list(fila) == COLUMNAS`; `recorrido` con ids unidos por `-`, empieza y termina en la partida), `::test_no_completada_y_no_ejecutada` (medidor que devuelve `NO_COMPLETADA` para FB desde k = 3 con `ks=(2, 3, 4)`: FB k = 3 `no_completada` con `tiempo_ms` vacío y `repeticiones == 0`; FB k = 4 `no_ejecutada` **sin** llamar al medidor; HK de todos los k `ok`; ninguna fila omitida), `::test_verificacion_previa_k_pequeno` (monkeypatch de `fuerza_bruta` en el módulo para devolver otro valor con k ≤ 9 → `ValueError` **antes** de la primera llamada al medidor), `::test_verificacion_con_valor_del_hijo` (`K_VERIFICACION_PREVIA` parcheado a 0 y medidor que devuelve un valor alterado para FB → `ValueError`), `::test_main_no_escribe_si_falla` (`tmp_path`, matriz sintética, FB alterada → `ValueError` y la carpeta sin archivos), `::test_main_sintetico_escribe_archivos` (matriz sintética de 13 lugares con ids `C01`… escrita con `guardar_matriz` en `tmp_path`, `ks=(2, 3)`, `repeticiones=1`, medidor real `medir_en_hijo`: existen `r4_exactas.csv` (4 filas `ok`, tiempos > 0) y `maquina.json`)
  - Humo (sin escribir en `results/r4/`): `.venv/bin/python -c "from rutas.r4.medir_exactas import main; main(salida='<carpeta scratchpad>/r4_humo', ks=(5, 6, 7, 8), repeticiones=1)"`; reportar los tiempos de FB y HK por k y la extrapolación a k = 10, 11 y 12 (estimación del plan: FB k = 11 ≈ 1,5–2,5 min, k = 12 > 5 min)
  - Verificar: `.venv/bin/python -m pytest tests/test_medir_exactas.py`
  - Nota: el script acepta `--k-max`, `--salida` y `--repeticiones` (valores por defecto = medición real). Los argumentos por línea de comandos no estaban en el plan; `main` conserva la firma del plan. La FB se busca por nombre en el módulo (`_funcion`) para que las pruebas puedan cambiarla.
  - anotar en `docs/anexo-ia.md`

- [x] T19 · Memoria de Held-Karp con `tracemalloc` (punto 1 «estimar memoria»; spec Comportamiento 6)
  - Archivos: `rutas/r4/medir_memoria.py` (`COLUMNAS`, `pico_tracemalloc(T, s, lugares)`, `filas_memoria(T, s, lugares_por_k)`, `main(matriz=MATRIZ_TIEMPOS, salida=RESULTS_R4)` según el plan; `if __name__ == "__main__": main()`)
  - Test primero: `tests/test_medir_memoria_r4.py::test_pico_positivo_y_crece` (matrices aleatorias con k = 5 y k = 8: pico > 0 y el de k = 8 > el de k = 5; `tracemalloc.is_tracing()` es falso al terminar), `::test_pico_mayor_que_estimado` (k = 8: pico ≥ `bytes_estimados`, por la sobrecarga de los objetos de Python explicada en el plan), `::test_filas_columnas` (`list(fila) == COLUMNAS`; `celdas`, `bytes_estimados` y `mb_estimados` = `memoria_held_karp(k)`), `::test_main_sintetico` (matriz sintética de 13 lugares con ids `C01`… en `tmp_path`: escribe `r4_memoria.csv` con 8 filas, k = 5..12)
  - Ejecutar (no es medición de tiempo; unos segundos): `.venv/bin/python -m rutas.r4.medir_memoria` → `results/r4/r4_memoria.csv`
  - Verificar: `.venv/bin/python -m pytest tests/test_medir_memoria_r4.py`
  - anotar en `docs/anexo-ia.md`

- [x] T20 · Calidad de la heurística (punto 3; caso 20, resumen)
  - Archivos: `rutas/r4/calidad.py` (`COLUMNAS_DETALLE`, `COLUMNAS`, `calidad_instancias`, `resumir_calidad`, `main(matriz=MATRIZ_TIEMPOS, catalogo=CATALOGO, salida=RESULTS_R4)` según el plan; `if __name__ == "__main__": main()`)
  - Test primero: `tests/test_calidad_r4.py::test_detalle_matriz_clase` (matriz con ids `C01, A01, A02, A03` y valores de `T_CLASE`, una instancia `["A01", "A02", "A03"]`: `optimo_s == 35`, `heuristica_s == 39`, `brecha_pct ≈ 11.43`, `lugares == "A01-A02-A03"`), `::test_caso_20_resumen` (detalle sintético de dos k con brechas conocidas → `instancias`, promedio y máximo exactos; columnas = `COLUMNAS`), `::test_brecha_negativa_es_error` (monkeypatch de `vecino_mas_cercano` en el módulo para devolver menos que el óptimo → `ValueError`), `::test_main_sintetico` (matriz sintética de 13 lugares y catálogo con sus ids en `tmp_path`: escribe los dos CSV; 40 filas de detalle, 4 de resumen con `instancias == 10`)
  - Ejecutar (no se cronometra; ≈ 10–20 s por los HK de k = 12): `.venv/bin/python -m rutas.r4.calidad` → `results/r4/r4_calidad_detalle.csv` y `r4_calidad.csv`; reportar la tabla
  - Verificar: `.venv/bin/python -m pytest tests/test_calidad_r4.py`
  - Nota: `main` comprueba que los ids del catálogo coinciden con los de la matriz (para eso se usa el parámetro `catalogo`). Resultado: brecha promedio 6,00 / 9,73 / 10,57 / 11,81 % y máxima 12,09 / 19,76 / 20,74 / 28,18 % para k = 5 / 8 / 10 / 12.
  - anotar en `docs/anexo-ia.md`

- [x] T21 · Tablas y gráfica de R4 desde los archivos (caso 20; sección 6.8; Anexo, Requerimiento 4)
  - Archivos: `rutas/r4/tablas.py` (stubs primero; luego `grafica_tiempo_vs_k(results=RESULTS_R4)` y `main(results=RESULTS_R4)` según el plan; `matplotlib.use("Agg")`; reutiliza `a_markdown` de `rutas/r1/tablas.py` y `conteos_teoricos`; cada CSV se lee con `keep_default_na=False`; una sección cuyo archivo falta se reemplaza por una nota)
  - Test primero (todas con CSV/JSON de ejemplo escritos por la prueba en `tmp_path`, nunca los reales): `tests/test_tablas_r4.py::test_caso_20_tabla_exactas` (CSV con FB `ok` en k = 5..10, `no_completada` en 11 y `no_ejecutada` en 12, HK `ok` en todos: la tabla del Anexo tiene 8 filas, «no completada» en FB k = 11 y 12, los tiempos del CSV con 3 decimales y «ms» en los encabezados), `::test_mayor_k_resuelto` (FB 10, HK 12), `::test_cocientes_medidos_y_predichos` (con tiempos construidos a mano: el cociente medido de 5 a 6 y el predicho (6²/5 = 7,2 para FB; 2·(6/5)² = 2,88 para HK) aparecen), `::test_caso_20_grafica` (espiando `Axes.plot` y `Axes.set_yscale` como en `tests/test_tablas_r3.py`: dos curvas, la de FB con x = 5..10 (sin 11 ni 12), escala `"log"`, la etiqueta del eje y dice «ms» y «logarítmica», la leyenda o el título mencionan «no completada»; el PNG existe y no está vacío), `::test_caso_20_calidad_e_itinerario` (las tablas de calidad e itinerario salen de `r4_calidad.csv` y `r4_itinerario.csv/json`: valores, fila «Regreso», atractivos quitados con su ahorro, totales), `::test_memoria_y_semillas` (memoria estimada frente al pico, semillas 2026 y 2026..2035, procesador de `maquina.json`), `::test_archivos_faltantes` (sin `r4_exactas.csv` ni `maquina.json`: genera el Markdown con una nota y sin error)
  - Ejecutar (no es medición): `.venv/bin/python -m rutas.r4.tablas` → `tablas_r4.md` parcial (sin `r4_exactas.csv` todavía, y por eso sin PNG)
  - Verificar: `.venv/bin/python -m pytest tests/test_tablas_r4.py`
  - Nota: sin `r4_exactas.csv` la gráfica no se genera (`grafica_tiempo_vs_k` devuelve `None`) y `main` avisa sin fallar. Funciones públicas extra: `tabla_exactas`, `tabla_mayor_k`, `tabla_cocientes`.
  - anotar en `docs/anexo-ia.md`

- [x] T22 · Prueba de los resultados medidos y entrega del comando de medición real al usuario
  - Archivos: `tests/test_red_real_r4.py` (agregar `comprobar_resultados_r4(df, instancias_json)` y `::test_resultados_medidos`: se salta si falta `results/r4/r4_exactas.csv`; 16 filas en orden; columnas = `COLUMNAS`; estados válidos; tras un `no_completada` solo `no_ejecutada` en ese método; filas `ok` con `tiempo_ms > 0` y `repeticiones` ∈ {1, 5}; en los k con FB y HK `ok`, mismo `tiempo_total_s` ±1e-6; los recorridos empiezan y terminan en C01 y sus lugares son los primeros k de `muestra_anidada` del JSON; HK `ok` hasta k = 12); `tests/test_medir_exactas.py` (pruebas de `comprobar_resultados_r4` con CSV sintéticos alterados: fila faltante, `ok` después de `no_completada`, FB ≠ HK, recorrido con otros lugares → `AssertionError`; CSV correcto → pasa)
  - Test primero: las de CSV alterados se ven fallar con el stub antes de escribir `comprobar_resultados_r4`; con el CSV real ausente, `test_resultados_medidos` queda saltada
  - **No ejecutar la medición.** Entregar al usuario el comando exacto, para correr con el portátil enchufado y sin otros procesos pesados (≈ 10–15 min; dar la estimación medida en el humo de T18):
    ```bash
    cd /Users/nicolascastro/Desktop/proyecto-final-rutas-quindio && .venv/bin/python -m rutas.r4.medir_exactas && .venv/bin/python -m rutas.r4.tablas && .venv/bin/python -m pytest tests/test_red_real_r4.py
    ```
  - Verificar (lo hace el usuario): `results/r4/` tiene `r4_exactas.csv` (16 filas), `maquina.json`, `tablas_r4.md` completo y `r4_tiempo_vs_k.png`; `tests/test_red_real_r4.py` pasa sin saltadas
  - Nota: las pruebas de `comprobar_resultados_r4` con CSV alterados se pusieron en `tests/test_medir_exactas.py` (importan la función de `tests/test_red_real_r4.py`). `test_resultados_medidos` se salta mientras no exista `results/r4/r4_exactas.csv`.
  - anotar en `docs/anexo-ia.md`

### Ronda 1, sugerencias del reviewer (aplicadas después de la aprobación)
- [x] S1 Orden del itinerario: `tests/test_itinerario.py::test_filas_siguen_el_recorrido_de_held_karp` (anillo dirigido donde el orden importa) y aserciones nuevas en el caso 19c (`A04, A07, A06, A14, A05, A08`, igual al recorrido de Held-Karp, y desplazamientos = jornada − visitas). La mutación `sorted(recorrido[1:-1])` ahora falla.
- [x] S2 Desempates de HK: `tests/test_tsp_clase.py::test_held_karp_desempates_menor_i_y_menor_j`. Nota: con todos los arcos = 1, HK devuelve `[0, 3, 2, 1, 0]` (no `[0, 1, 2, 3, 0]`): el cierre elige el menor j (el lugar 1 queda de último) y el paso el menor i, y la reconstrucción va hacia atrás. Es coherente con la spec; se fijó ese recorrido. Cambiar `<` por `<=` en el paso o en el cierre hace fallar la prueba.
- [x] S3 Guardia de librerías: busca `itertools`, `networkx` y `scipy` como texto, y `numpy`/`scipy`/`networkx`/`itertools` como `import`/`from` (por_ids.py nombra `numpy.float64` en un comentario, por eso numpy no se busca como texto).
- [x] S4 Gráfica con `MaxNLocator(integer=True)`; prueba `test_grafica_marcas_enteras_en_k` con k = 5..8.
- [x] S5 `quitados` del itinerario con `visita_min` y `desvio_min` (= ahorro − visita); `results/r4/r4_itinerario.json` regenerado; el CSV y `tablas_r4.md` no cambian.

**Fin de B4:** `.venv/bin/python -m pytest -m "not red"` en verde, `r4_memoria.csv`, `r4_calidad*.csv` y `tablas_r4.md` (parcial) generados, y el comando de T22 entregado. **Detenerse.** El usuario corre la medición y hace su commit.

## Cierre

- [ ] T23 · Anexo de IA y «Reproducir R4» en el README
  - Archivos: `docs/anexo-ia.md` (local; entradas de R4: plan y tareas con el agente planner; código y pruebas con el implementer; cómo se verificó: casos a mano 1–10 y 17, tabla del caso 3, FB contra `itertools` y FB = HK (11, 12, 19a), contador contra lecturas reales (15), itinerario contra la enumeración del coordinador (19c), mutaciones temporales); `README.md` (sección «Reproducir R4» después de «Reproducir R3»: requisito de haber corrido R1 y R2; tabla con `rutas.r4.instancias`, `rutas.r4.itinerario`, `rutas.r4.calidad`, `rutas.r4.medir_memoria`, `rutas.r4.medir_exactas` (larga, enchufado, ≈ 10–15 min) y `rutas.r4.tablas`, y lo que deja cada uno; semillas 2026 y 2026..2035; pruebas `pytest -m "not red"`, `pytest tests/test_red_real_r4.py` y `pytest`)
  - Test primero: no aplica (documentación)
  - Verificar: `grep -n "R4" docs/anexo-ia.md && grep -n "rutas.r4.medir_exactas" README.md`
  - anotar en `docs/anexo-ia.md`

- [ ] T24 · Suite completa y regeneración de todos los resultados de R4 (la ejecuta el usuario con el portátil enchufado)
  - Archivos: ninguno nuevo (regenera `results/r4/*`)
  - Test primero: no aplica
  - Comando que se entrega al usuario:
    ```bash
    cd /Users/nicolascastro/Desktop/proyecto-final-rutas-quindio && .venv/bin/python -m rutas.r4.instancias && .venv/bin/python -m rutas.r4.itinerario && .venv/bin/python -m rutas.r4.calidad && .venv/bin/python -m rutas.r4.medir_memoria && .venv/bin/python -m rutas.r4.medir_exactas && .venv/bin/python -m rutas.r4.tablas && .venv/bin/python -m pytest
    ```
  - Verificar: todas pasan y ninguna `red` saltada; `results/r4/` con los 10 archivos de la spec (`r4_instancias.json`, `r4_exactas.csv`, `r4_memoria.csv`, `r4_calidad_detalle.csv`, `r4_calidad.csv`, `r4_itinerario.csv`, `r4_itinerario.json`, `r4_tiempo_vs_k.png`, `maquina.json`, `tablas_r4.md`); `r4_instancias.json`, `r4_itinerario.*` y `r4_calidad*.csv` sin cambios respecto a B3/B4 (deterministas)

## Cobertura

| Caso / punto | Tarea |
|---|---|
| 1 Seis recorridos de la matriz de clase | T4, T5 |
| 2 FB y HK → 35, `[0, 1, 3, 2, 0]` | T5, T8 |
| 3 Tabla de Held-Karp | T7 |
| 4 Voraz no óptimo (11,43 %) | T6 |
| 4b Ejemplo en una vía (16 frente a 14) | T5, T6, T8 |
| 5 Asimetría | T4, T8 |
| 6 k = 1 · 7 k = 2 · 8 k = 0 | T5, T6, T8 |
| 9 Arco `inf` y sin recorrido finito | T5, T6, T8 |
| 10 Errores de entrada | T4, T5, T6, T8 |
| 11 Propiedad FB = HK, recorrido válido, brecha ≥ 0 | T11 |
| 12 FB contra `itertools.permutations` | T11 |
| 13 Generador propio | T3 |
| 14 Memoria estimada | T10, T19 |
| 15 Conteos (contador y teóricos) | T9, T10 |
| 16 Itinerario en la frontera | T14, T15 |
| 17 Desempate lexicográfico de FB | T5, T8 |
| 18 Envoltorio por ids | T13 |
| 19a, 19b, 19c Red real | T16 |
| 19d Muestra anidada | T12 |
| 20 Tablas, gráfica y resumen de calidad desde CSV de ejemplo | T20, T21 |
| Bordes: costo 0 (T03/T05), matriz simétrica, no modifica entradas | T5, T11 |
| Bordes del itinerario | T14 |
| Bordes de medición (> 1 min una vez; > 5 min `no_completada`; `no_ejecutada`) | T17, T18, T21, T22 |
| R4 párrafo inicial (Armenia, azar con semilla, todas las categorías) | T12, T18 |
| R4.1 FB y HK propios, recorrido, k de 5 a 12, mayor k, gráfica, memoria, FB = HK | T3, T5, T7–T11, T16, T18, T19, T21, T22 |
| R4.2 Heurística voraz propia | T6 |
| R4.3 Calidad | T12, T20, T21 |
| R4.4 Itinerario de un día | T14, T15, T16, T21 |
| R4.5 Voraz frente a óptimo (casos 4 y 4b) | T6 (y el informe) |
| Sección 6.1 misma máquina, `maquina.json` | T1, T18, T22 |
| Sección 6.2 solo el algoritmo | T9, T17, T18, T19 |
| Sección 6.3 5 repeticiones, mediana, una si > 1 min | T17, T18 |
| Sección 6.4 unidad ms | T18, T21 |
| Sección 6.5 semilla fija documentada | T12, T21 |
| Sección 6.6 verificación antes de medir | T3–T11, T16, T18, T20 |
| Sección 6.7 límite de 5 min | T18, T21, T22 |
| Sección 6.8 tablas y gráficas desde CSV/JSON | T21 |
| Anexo, Requerimiento 4 | T15, T20, T21 |
| R5 (consumidor) | T13, T14 |
| Anexo de IA | T23 (y cada tarea con IA) |

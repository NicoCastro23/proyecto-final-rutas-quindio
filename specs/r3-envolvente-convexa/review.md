# Revisión — R3 Envolvente convexa (QuickHull)

## Ronda 1: APROBADO

Revisado el 2026-11-10 contra `spec.md`, `plan.md`, `tasks.md` (T1–T18 marcadas), el enunciado (sección 5, Requerimiento 3; sección 6; sección 8) y el Anexo (tabla del Requerimiento 3). No se ejecutó ninguna descarga ni medición, y no se regeneró nada en `data/` ni en `results/`.

Pruebas: ✅
- `.venv/bin/python -m pytest -q` → **294 passed** en 10,5 s (ninguna saltada; las 19 `red` corren con `data/processed/`).
- `.venv/bin/python -m pytest -q -m "not red"` → **275 passed, 19 deselected** en 4,3 s.
- Solo R3 (`test_envolvente*.py`, `test_puntos_r3.py`, `test_archivos_r3.py`, `test_medir_envolvente.py`, `test_tablas_r3.py`, `test_red_real_r3.py`) → 68 passed.

Mutaciones (hechas sobre una copia de `rutas/r3/envolvente.py` en el scratchpad; el repo no se tocó):

| Mutación | Detectada por |
|---|---|
| `cruz(a, b, p) >= 0` al repartir (alineados entran) | sí (casos 1–3) |
| `>= 0` en `fuera_ac` dentro de `_lado` | sí |
| Elegir c con `max` sin desempate (primer máximo según el orden de entrada) | sí, `test_orden_de_entrada_no_importa` |
| Quitar `ciclo.reverse()` (sale horario) | sí |
| Rotar al menor (x, y) en vez de (y, x) | sí |
| Olvidar la rama `c → b` | sí |
| Quitar `sys.setrecursionlimit` | sí, pero **solo** `test_limite_de_recursion` (ver sugerencias) |
| `area` sin `abs` | sí |
| Signo de `cruz` invertido / `cruz` con `float` | sí (`test_cruz_*`, tipo `int`) |
| Un punto → `[]` | sí |
| Desempate «mayor lexicográfico» en lugar de «menor» | no, pero es un **mutante equivalente**: ambos extremos del grupo empatado son vértices y la salida final es la misma. No es un hueco de las pruebas. |

| Caso / punto del enunciado | Cumplido | Test |
|---|---|---|
| 1 Cuadrado con extras | ✅ | `tests/test_envolvente.py::test_caso_1_cuadrado_con_extras`; contra SciPy en `tests/test_envolvente_clase.py::test_casos_a_mano_contra_scipy[caso_1]` |
| 2 Desempate (5,5) alineado | ✅ | `test_envolvente.py::test_caso_2_desempate`, `test_envolvente_clase.py::test_caso_2_empate_json`, `[caso_2]` |
| 3 Rectángulo con puntos en los lados | ✅ | `test_envolvente.py::test_caso_3_rectangulo_lados`, `test_envolvente_clase.py::test_caso_3_rectangulo_json`, `[caso_3]` |
| 4 Pentágono con interior | ✅ | `test_envolvente.py::test_caso_4_pentagono`, `[caso_4]` |
| 5 Duplicados | ✅ | `test_envolvente.py::test_caso_5_duplicados`, `tests/test_puntos_r3.py::test_preparar_quita_repetidos` |
| 6 Alineados + `QhullError` | ✅ | `test_envolvente.py::test_caso_6_alineados`, `test_envolvente_clase.py::test_scipy_falla_en_degenerados` |
| 7 Vacío, un punto, dos puntos + `QhullError` | ✅ | `test_envolvente.py::test_caso_7_bordes_pequenos`, `test_scipy_falla_en_degenerados` (`dos_puntos`) |
| 8 Coordenadas 3·10⁹ (cruz 9·10¹⁸ entero) | ✅ | `test_envolvente.py::test_cruz_grande`, `test_caso_8_coordenadas_grandes`, `[caso_8]` |
| 9 Redondeo floor(x+0,5) y fusión | ✅ | `test_puntos_r3.py::test_caso_9_redondeo`, `test_preparar_quita_repetidos`, `test_puntos_de_grafo_sintetico` |
| 10 Red de la clase: 9, 7, 8, 3, 2; 4 y 6 no; 585 000 m² | ✅ | `test_envolvente_clase.py::test_caso_10_red_clase` (también contra SciPy), `test_r3_versionada` (copia = original) |
| 11 100 conjuntos aleatorios (semilla 2026) contra SciPy | ✅ | `tests/test_envolvente_propiedad.py::test_caso_11_aleatorios_vs_scipy` (≥ 90 comparados; degenerados con invariantes) |
| 12 Cuadrados 1 000/10 000/50 000 contra SciPy y (8/3) ln n | ✅ | `test_envolvente_propiedad.py::test_caso_12_cuadrados[1000/10000/50000]` |
| 13 Invariantes (convexidad estricta, todos dentro) | ✅ | `tests/conftest.py::comprobar_envolvente` en cada salida; `test_envolvente.py::test_invariantes_detectan_errores` comprueba que el helper falla cuando debe |
| 14 Red real: 8 791 puntos, 14 vértices = SciPy, área ± 1 m² | ✅ | `tests/test_red_real_r3.py::test_caso_14_red_real` |
| 15 Círculo de 2 000 puntos, todos vértices | ✅ | `test_envolvente_propiedad.py::test_caso_15_circulo` |
| 16 Parábola de 5 000 puntos, todos vértices | ✅ | `test_envolvente_propiedad.py::test_caso_16_parabola` |
| 17 `envolvente.csv` / `.geojson` cerrados; ida y vuelta < 1 m | ✅ | `tests/test_archivos_r3.py::test_caso_17_sintetico`, `test_red_real_r3.py::test_caso_17_archivos_reales` (área 1 631,5 ± 1 km²) |
| Enunciado: UTM 18N | ✅ | `puntos_de_grafo` usa `x_utm`, `y_utm` (EPSG:32618) de R1; `test_puntos_de_grafo_sintetico` |
| Enunciado: entero más cercano, sin repetidos, enteros en los giros | ✅ | `rutas/r3/puntos.py:9-21`; `cruz` solo con `int` (`rutas/r3/envolvente.py:14-19`); mutación a `float` detectada |
| Enunciado: alineados no son vértices | ✅ | casos 2, 3, 6, 10 y la propiedad del caso 13 (cruz > 0 entre vértices consecutivos) |
| Enunciado: D&C propio, sin librerías en el algoritmo | ✅ | `rutas/r3/envolvente.py` solo importa `sys`; SciPy/NumPy solo en `referencia.py` y `medir_envolvente.py` (verificación y medición) |
| Enunciado: mismos vértices que `ConvexHull` en todas las pruebas | ✅ | conjunto y orden normalizado en casos 1–4, 8, 10, 11, 12, 14, 15; degenerados documentados (`QhullError`) |
| Enunciado: experimento red + 1 000/10 000/50 000 con semilla | ✅ | `rutas/r3/medir_envolvente.py`; `results/r3/r3_puntos.json` (semilla 2026, `random.Random`, lado 10⁶) |
| Anexo: tabla con las 6 columnas y las 4 filas en orden | ✅ | `test_red_real_r3.py::test_resultados_medidos` sobre el CSV real; `test_medir_envolvente.py::test_resultados_*` (detecta fila faltante, orden, cociente y vértices erróneos) |
| 6.1 Misma máquina, `maquina.json` | ✅ | Apple M5, 16 GB, macOS 26.6.2, Python 3.13.8 |
| 6.2 Solo el algoritmo | ✅ | `medir_conjunto`: `numpy.array` y preparación fuera; `test_medir_conjunto_con_medidor_falso` comprueba qué se pasa al cronómetro |
| 6.3 5 repeticiones, mediana | ✅ | `medir_en_proceso`; columna `repeticiones` = 5 |
| 6.4 Unidad (ms) | ✅ | columnas `_ms` y encabezados «(ms)» en `tablas_r3.md` |
| 6.5 Semilla documentada | ✅ | `r3_puntos.json`, README |
| 6.6 Verificación antes de medir | ✅ | `comprobar_iguales` con `ValueError`; `test_main_no_escribe_si_difieren` |
| 6.7 Límite de 5 min / «no completada» | ✅ | `test_no_completada`, `test_resultados_no_completada_es_valida` |
| 6.8 Tablas y gráfica desde los archivos | ✅ | `rutas/r3/tablas.py`; `test_tablas_r3.py` |
| Cociente recalculado desde el CSV | ✅ | 11,562 / 8,689 / 12,536 / 12,618: coincide con la columna `cociente` |
| SciPy usa Qhull (C) mediante Cython | ✅ | Verificado en la instalación (ver más abajo) |

Lo que verifiqué en SciPy 1.18.1 instalado (`.venv/lib/python3.13/site-packages/scipy/spatial/`): el `.pyx` no viene instalado, pero `_qhull.cpython-313-darwin.so` contiene la ruta `scipy/spatial/_qhull.pyx`, los símbolos de Cython 3.2.9 (`_cython_3_2_9`, `__pyx_…`) y la versión de Qhull que trae: **`qhull_r 8.0.2 (2020.2.r 2020/08/31)`**. La llamada que lo inicia es `qh_new_qhull`. `qhull_src/COPYING_QHULL.txt` atribuye Qhull a C. B. Barber y The Geometry Center. El docstring de `ConvexHull` remite a la «Qhull library» (http://www.qhull.org/) y dice «Option "Qt" is always enabled» (para 2-D no se pasan otras opciones). Lo que dice la spec (Qhull en C, envoltorio Cython `_qhull.pyx`) es correcto. En el informe conviene citar la versión exacta de Qhull (2020.2 / qhull_r 8.0.2).

Profundidad de recursión (medida en la copia): círculo 2 000 → 11, parábola 5 000 → 14, cuadrado 50 000 → 7, como reportó el coordinator. Peor caso real: puntos (2ᵏ, 4ᵏ) dan profundidad n − 1 (50 → 49, 200 → 199, 1 500 → 1 499, sin `RecursionError` gracias al límite de 20 000).

Estado de los archivos: los resultados **ya están commiteados**. `git ls-files` lista `results/r3/{maquina.json, r3_envolvente.csv, r3_puntos.json, tablas_r3.md, r3_envolvente.png}` y `data/processed/envolvente.{csv,geojson}`, y el commit `d91af6d` («R3: medición real…») añadió los cuatro primeros. Lo único sin commitear es `README.md` («Reproducir R3») y `specs/r3-envolvente-convexa/tasks.md` (T17/T18 marcadas). Queda pendiente para el usuario commitear esos dos archivos y este `review.md`.

### Bloqueantes
- Ninguno.

### Sugerencias (no bloquean)
- `specs/r3-envolvente-convexa/spec.md:39` (Comportamiento 4: «El informe menciona el peor caso (casos 15 y 16)») y `rutas/r3/envolvente.py:9-10` (comentario «20 000 cubre … los 5 000 puntos de la parábola»): el círculo y la parábola **no** son el peor caso de QuickHull. Tienen h = n, pero las particiones salen parejas (profundidad 11 y 14), así que trabajan en Θ(n log n). El propio `plan.md:243` lo dice bien. Haría falta corregir la frase de la spec y el comentario para que remitan a un peor caso real, como (2ᵏ, 4ᵏ), con profundidad n − 1.
- `tests/test_envolvente.py:131-133`: la protección de `sys.setrecursionlimit` solo se prueba mirando el valor del límite. Ninguna prueba pasa de 1 000 niveles (los casos 15 y 16 llegan a 14). Se puede añadir un caso con (2ᵏ, 4ᵏ), k < 1 100, comprobado solo con `comprobar_envolvente`, porque SciPy pierde exactitud por encima de 2⁵³. Tarda unos 15–20 s por los enteros grandes, así que conviene un marcador `lento`. Así quedaría verificada la decisión de la Puerta 1 y no solo el valor del límite.
- `specs/r3-envolvente-convexa/spec.md` (sección «Complejidad esperada»): la memoria «O(n)» solo vale con particiones parejas (n + n/2 + … = O(n)). En el peor caso, cada marco de `_lado` conserva sus listas `puntos`, `fuera_ac` y `fuera_cb`, y la pila tiene profundidad O(n), así que el pico es O(n²). Medido con `tracemalloc` sobre (2ᵏ, 4ᵏ): 1,2 MB con n = 500, 4,5 MB con n = 1 000 y 17,5 MB con n = 2 000 (×4 al duplicar n). Hay que corregirlo en la spec y en el informe. El código no tiene que cambiar.
- `specs/r3-envolvente-convexa/spec.md:3`: la línea de estado sigue en «☐ pruebas · ☐ código · ☐ verificado». Hay que actualizarla al cerrar R3.
- `rutas/r3/tablas.py:106-108`: la frase de la nota empieza en minúscula («… m, redondeo `…`. cada cuadrado usa…») y la columna `n` sale como «1000» mientras el nombre del conjunto dice «1 000». Son detalles de presentación.
- `rutas/medicion.py:36-56` (`medir_en_proceso`): no puede interrumpir una ejecución a los 5 min; solo la marca como «no completada» cuando termina. Con tiempos de milisegundos no afecta a R3. Basta con decirlo en el informe, igual que en R1 y R2.

### Pendiente para el documento técnico
- **Justificación de QuickHull según la distribución:** 14 de 8 791 nodos son vértices (0,16 %). La red se concentra en cabeceras y corredores, así que QuickHull descarta casi todo en los primeros niveles (profundidad 7 en el cuadrado de 50 000). Comportamiento cercano a O(n log h), con h ≪ n. Mencionar que es de la misma familia que Qhull.
- **Recurrencia y complejidad con fuentes:** T(n) = T(n₁) + T(n₂) + O(n), n₁ + n₂ ≤ n − 1. Con particiones parejas, 2T(n/2) + O(n) = O(n log n) por el teorema maestro. En el peor caso, T(n − 1) + O(n) = O(n²), con un ejemplo concreto (2ᵏ, 4ᵏ) y no el círculo ni la parábola. Memoria: O(n) con particiones parejas y O(n²) en el peor caso con esta implementación (ver sugerencias). Citar a Eddy (1977) y a Barber, Dobkin y Huhdanpaa (1996); Cormen sigue pendiente.
- **Argumento de correctitud:** el punto más lejano de la cuerda es vértice; los puntos dentro del triángulo a-c-b no pueden ser vértices; con cruz > 0 estricta, los alineados nunca entran. Explicar también las reglas de desempate y de redondeo.
- **Tabla del Anexo** (de `results/r3/tablas_r3.md`, en ms) con un párrafo de discusión:
  - Crecimiento del tiempo propio: 0,558 → 6,181 → 27,509 ms para n = 1 000 → 10 000 → 50 000. Es ×11,1 cuando n crece ×10 y ×4,45 cuando crece ×5. Comparar con n log n (×13,3 y ×5,9) y con n log h (≈ ×11,7 y ×4,9): los datos se ajustan mejor a O(n log h).
  - Cociente propio/SciPy de 8,7 a 12,6 (11,6 en la red). Es menor de lo que se esperaría entre Python interpretado y C. Hipótesis que se pueden comprobar: (a) el tiempo de SciPy incluye un costo fijo de Python/Cython (validar la entrada, crear el objeto `ConvexHull`, construir `simplices`/`equations`/`neighbors` y calcular `area`/`volume`), que pesa más con n pequeño (por eso 8,7 con 1 000); (b) Qhull hace más trabajo por punto que el QuickHull plano (es general para d dimensiones, usa aritmética en `double` con control de errores de redondeo y la opción `Qt`); (c) el propio descarta casi todo en dos o tres pasadas con comprensiones de listas, que en CPython ya son relativamente eficientes. Para probarlas: medir `ConvexHull` con n muy pequeño (costo fijo) y comparar la pendiente de ambos.
  - Explicar qué usa SciPy: `scipy/spatial/_qhull.pyx` (Cython) llama a Qhull 2020.2 (`qhull_r` 8.0.2, en C, algoritmo Quickhull). Verificado en el `.so` instalado y en `COPYING_QHULL.txt`.
- **Vértices frente a (8/3) ln n** (Rényi y Sulanke, 1963): 16/18,4, 26/24,6 y 25/28,9. Están dentro de la variabilidad de una sola muestra; comentar que el valor es una esperanza y no una cota.
- **Área de la envolvente** (1 631,5 km²) frente a la del departamento (≈ 1 935 km², con fuente): la envolvente cubre ≈ 84 % del departamento. Discutir por qué: la red no llega a la cordillera oriental y el polígono, por ser convexo, tapa entrantes del límite departamental.
- **Gráfica** `results/r3/r3_envolvente.png` (en metros UTM) con su pie, y explicación de cómo se verificó cada caso (sección 6.6): a mano (1–10), contra SciPy (todos los no degenerados), invariantes (13) y mutaciones.
- **Anexo de IA:** `docs/anexo-ia.md` (local, ignorado por decisión del usuario) ya tiene las entradas de R3 (B1–B4 y el resumen). Hay que pasarlas al anexo del documento técnico.

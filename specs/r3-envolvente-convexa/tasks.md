# Tareas — R3 Envolvente convexa de la red vial (QuickHull)

Spec: `spec.md` · Plan: `plan.md`. Todas las órdenes se corren desde la raíz del repositorio (`/Users/santiagopolaniapinzon/proyecto-final-rutas-quindio`) con `.venv/bin/python` (Python 3.13.8; no hay que instalar nada).

Cada tarea en la que se use IA termina con: **anotar en `docs/anexo-ia.md`** (fecha, integrante, herramienta, qué se generó, cómo se verificó).

> **Reglas del usuario:**
> 1. Cada bloque termina con todas sus pruebas en verde y el trabajo se **DETIENE** hasta que el usuario haga su commit. No se empieza el bloque siguiente antes.
> 2. Test primero **tarea por tarea**: escribir la prueba de una tarea, verla fallar por la razón correcta (el módulo existe con funciones que hacen `raise NotImplementedError`; no un `ModuleNotFoundError` global) y solo entonces escribir el código. El reporte de cada bloque lo confirma tarea por tarea.
> 3. No modificar `.gitignore` sin preguntar (conserva `docs/` y `.DS_Store`). `docs/` está ignorada: `docs/anexo-ia.md` se mantiene en local.
> 4. Nunca `git add`, `git commit` ni `git push`.
> 5. Las mediciones finales sobre la red real las corre el usuario con el portátil enchufado: las tareas de medición real terminan **entregándole el comando exacto**, no ejecutándolo.

> **Simplicidad:** código legible que cada integrante pueda explicar. QuickHull va en `rutas/r3/envolvente.py`, corto y siguiendo la recurrencia (ver el esqueleto del plan): `envolvente` reparte los puntos a la izquierda de A→B y de B→A y llama dos veces a `_lado`; `_lado` elige el punto más lejano, reparte en dos listas y se llama dos veces. Solo enteros de Python y tuplas; nada de NumPy ni SciPy en el algoritmo. `vertices_scipy` vive aparte (`rutas/r3/referencia.py`) y solo se usa para verificar y medir.

## B1 · Copia de R3, unidades de la tabla de R2 y piezas básicas (cruz, redondeo, área)

- [x] T1 · Paquete `rutas/r3` y rutas de R3 en la configuración
  - Archivos: `rutas/r3/__init__.py` (vacío), `rutas/config.py` (agregar `RESULTS_R3 = RAIZ / "results" / "r3"`, `ENVOLVENTE_CSV = DATA_PROCESSED / "envolvente.csv"`, `ENVOLVENTE_GEOJSON = DATA_PROCESSED / "envolvente.geojson"`; no tocar lo demás)
  - Test primero: `tests/test_config.py::test_rutas_r3` (`RESULTS_R3 == RAIZ / "results" / "r3"`; `ENVOLVENTE_CSV.name == "envolvente.csv"` y `ENVOLVENTE_GEOJSON.name == "envolvente.geojson"`, ambos en `DATA_PROCESSED`)
  - Verificar: `.venv/bin/python -m pytest tests/test_config.py`

- [x] T2 · Sección `R3` en la copia versionada de la red de la clase (casos 2, 3, 6, 7, 10)
  - Archivos: `tests/datos/red_clase.json` (agregar **solo** la sección `R3` de `estudio/casos_prueba.json`, sin cambiar valores; `red` y `R2` intactas; `_origen` pasa a decir: `"Copia de las secciones red, R2 y R3 de estudio/casos_prueba.json (grafo de la clase de Dijkstra y casos de la envolvente, resueltos a mano y verificados con NetworkX 3.7 y SciPy 1.18.1), 2026-11-10. estudio/ no se versiona."`); `tests/conftest.py` (agregar `cargar_casos_r3()` → `(nodos, seccion_R3)` con `nodos = {id: (x, y)}` en `int` desde `red.nodos`); `tests/test_dijkstra_clase.py::test_red_clase_versionada` (cambiar la aserción de claves a `{"_origen", "red", "R2", "R3"}`; lo demás igual)
  - Test primero: `tests/test_envolvente_clase.py::test_r3_versionada` (claves de `R3` exactamente `nodos_red`, `empate`, `rectangulo`, `scipy_falla`; `R3.nodos_red.vertices == [9, 7, 8, 3, 2]`, `area_m2 == 585000`; `cargar_casos_r3()` da 9 nodos con `nodos[9] == (0, 0)`; si existe `estudio/casos_prueba.json`, `red`, `R2` **y** `R3` son iguales a las de allí, si no se omite esa comparación). Se ve fallar con `KeyError: 'R3'` (el JSON aún no tiene la sección) antes de editarlo
  - Verificar: `.venv/bin/python -m pytest tests/test_envolvente_clase.py tests/test_dijkstra_clase.py -k versionada`
  - anotar en `docs/anexo-ia.md`

- [x] T3 · Tarea pequeña de R2: unidad de la pendiente por versión en `tablas_r2.md` (aprobada en Puerta 1)
  - Archivos: `rutas/r2/tablas.py` (agregar `UNIDAD_PENDIENTE = {"lineal": ("ms/nodo", 1), "cola_prioridad": ("µs/nodo", 1000)}` y cambiar **solo** `_tabla_ajuste`: columnas `Versión | Pendiente | Unidad de la pendiente | Ordenada (ms)`, la pendiente de cada versión multiplicada por su factor; `ajuste_tiempo_explorados` no cambia); `tests/test_tablas_r2.py`
  - Test primero: `tests/test_tablas_r2.py::test_tabla_ajuste_unidad_por_version` (`_tabla_ajuste({"lineal": {"pendiente": 0.5, "ordenada": 1.0}, "cola_prioridad": {"pendiente": 0.0003, "ordenada": 0.5}})`: la fila `lineal` contiene `0.5000` y `ms/nodo`; la fila `cola_prioridad` contiene `0.3000` y `µs/nodo`; el encabezado tiene `Unidad de la pendiente` y ya no `Pendiente (ms/nodo)`); actualizar `::test_tablas_md_incluye_cociente_por_par_y_ajuste` (con `FILAS_AJUSTE` la cola da 0,1 ms/nodo = `100.0000` µs/nodo: cambiar `"0.1000"` por `"100.0000"` y comprobar `"µs/nodo"`). Ver fallar las dos antes de cambiar `_tabla_ajuste`
  - Regenerar (no es medición: lee los CSV ya medidos): `.venv/bin/python -m rutas.r2.tablas`, y luego `git status --porcelain results/r2` debe mostrar **solo** ` M results/r2/tablas_r2.md`. Se espera así porque `r2_cociente.csv` y la PNG salen de los mismos CSV de forma determinista; si alguno de los dos cambia, **reportarlo** al usuario (no restaurarlo ni tocar git) para que decida
  - Verificar: `.venv/bin/python -m pytest tests/test_tablas_r2.py && git status --porcelain results/r2 && git diff --stat results/r2`
  - anotar en `docs/anexo-ia.md`

- [x] T4 · Algoritmo (stubs), predicado de giro, área y normalización (Comportamiento 1; caso 8; utilidades)
  - Archivos: `rutas/r3/envolvente.py` (crear con `cruz`, `envolvente`, `_lado`, `area`, `normalizar` como stubs `raise NotImplementedError`, y el `sys.setrecursionlimit(max(sys.getrecursionlimit(), 20_000))` con su comentario (ver plan); implementar aquí `cruz`, `area` (doble del área con enteros, `abs(...) / 2`; 0 con < 3 vértices) y `normalizar` (si el área con signo es negativa se invierte la lista; luego se rota al vértice de menor `(y, x)`))
  - Test primero: `tests/test_envolvente.py::test_cruz_signos` (`cruz((0,0), (1,0), (0,1)) == 1` izquierda, `cruz((0,0), (1,0), (0,-1)) == -1` derecha, `cruz((0,0), (1,1), (2,2)) == 0` alineados; resultado `int`), `::test_cruz_grande` (caso 8: `cruz((0,0), (3*10**9, 0), (0, 3*10**9)) == 9 * 10**18`, exacto e `int`), `::test_area` (cuadrado 4 × 4 → 16.0; triángulo (0,0), (4,0), (0,3) → 6.0; mismo valor en sentido horario; 2 vértices → 0), `::test_normalizar` (el cuadrado en horario y empezando en (4,4) → `[(0,0), (4,0), (4,4), (0,4)]`; ya normalizado → igual; empate de `y` mínima: empieza por el de menor `x`)
  - Verificar: `.venv/bin/python -m pytest tests/test_envolvente.py -k "cruz or area or normalizar"`
  - Nota: `puntos_de_grafo` y `envolvente`/`_lado` siguen como stubs (T11 y T6). `normalizar` usa `min(..., default=0)` para tolerar la lista vacía.
  - anotar en `docs/anexo-ia.md`

- [x] T5 · Preparación de puntos: redondeo, repetidos y cuadrado aleatorio (casos 5, 9; preparación del 12)
  - Archivos: `rutas/r3/puntos.py` (crear con stubs; luego `SEMILLA = 2026`, `LADO = 10**6`, `redondear(x)` = `math.floor(x + 0.5)`, `preparar_puntos(xs, ys)` (redondea, `set`, `sorted`; `zip(..., strict=True)`), `puntos_cuadrado(n, semilla=SEMILLA, lado=LADO)` (un `random.Random(semilla)` nuevo por llamada; `n` veces `(rng.randrange(lado), rng.randrange(lado))`; `set`, `sorted`); `puntos_de_grafo` queda como stub hasta T11)
  - Test primero: `tests/test_puntos_r3.py::test_caso_9_redondeo` (`redondear(2.5) == 3`, `redondear(-0.5) == 0`, `redondear(2.4999) == 2`, `redondear(-2.5) == -2`; tipo `int`, también con `numpy.float64`), `::test_preparar_quita_repetidos` (caso 5 y fusión tras redondear: `preparar_puntos([0, 0, 1, 0, 0.4], [0, 0, 0, 1, 0.4]) == [(0, 0), (0, 1), (1, 0)]`; todos `int` de Python), `::test_preparar_ordena` (salida = `sorted` y sin repetidos), `::test_preparar_largos_distintos` (`ValueError`), `::test_puntos_cuadrado_semilla` (misma semilla → misma lista; otra semilla → otra; `n = 1000` → `len ≤ 1000` y `> 990`; todas las coordenadas en `[0, 10**6)`; ordenada y sin repetidos)
  - Verificar: `.venv/bin/python -m pytest tests/test_puntos_r3.py`
  - anotar en `docs/anexo-ia.md`

**Fin de B1:** `.venv/bin/python -m pytest -m "not red"` en verde y `results/r2/tablas_r2.md` regenerado (y solo él, o reportado lo contrario). **Detenerse** y entregar el reporte (tarea por tarea: prueba escrita, fallo visto y su razón, prueba en verde). Esperar el commit del usuario.

## B2 · QuickHull, casos a mano y de la clase, invariantes y comparación con SciPy

- [ ] T6 · QuickHull recursivo (`envolvente` y `_lado`) con los casos a mano (casos 1–8; bordes; invariantes del caso 13)
  - Archivos: `rutas/r3/envolvente.py` (implementar `envolvente` y `_lado` según el esqueleto del plan: A = `min`, B = `max`; listas estrictas `cruz > 0`; en `_lado`, mayor `cruz(a, b, c)` y en empate el menor lexicográfico; ciclo horario `[A] + _lado(izq_AB, A, B) + [B] + _lado(izq_BA, B, A)`, invertido y rotado al de menor `(y, x)`); `tests/conftest.py` (agregar `comprobar_envolvente(vertices, puntos)` con los invariantes del plan)
  - Test primero: `tests/test_envolvente.py` (cada caso compara la lista exacta y llama a `comprobar_envolvente`): `::test_caso_1_cuadrado_con_extras` → `[(0,0), (4,0), (4,4), (0,4)]`, `::test_caso_2_desempate` → `[(0,0), (10,0), (8,5), (2,5)]` y `(5,5)` no está, `::test_caso_3_rectangulo_lados` → `[(0,0), (10,0), (10,10), (0,10)]`, `::test_caso_4_pentagono` → `[(0,0), (5,0), (6,3), (3,6), (-1,3)]`, `::test_caso_5_duplicados` (con el repetido, **sin** pasar por `preparar_puntos`) → `[(0,0), (1,0), (0,1)]`, `::test_caso_6_alineados` → `[(0,0), (3,3)]` (y en orden inverso de entrada, igual), `::test_caso_7_bordes_pequenos` (`[]` → `[]`; `[(7,7)]` → `[(7,7)]`; `[(7,7), (7,7)]` → `[(7,7)]`; `[(1,0), (0,0)]` → `[(0,0), (1,0)]`), `::test_caso_8_coordenadas_grandes` → `[(0,0), (3*10**9, 0), (0, 3*10**9)]`, `::test_coordenadas_negativas` (el cuadrado del caso 1 trasladado a (−10⁶, −10⁶)), `::test_orden_de_entrada_no_importa` (casos 1–4 con la entrada barajada con `random.Random(2026)` → misma salida), `::test_no_modifica_entrada` (copia antes y comparación después), `::test_invariantes_detectan_errores` (`comprobar_envolvente` lanza `AssertionError` con un polígono en sentido horario, con un vértice alineado y con un punto por fuera)
  - Ver fallar: todas con `NotImplementedError` del stub (salvo la de invariantes, que prueba solo el helper)
  - Verificar: `.venv/bin/python -m pytest tests/test_envolvente.py`
  - anotar en `docs/anexo-ia.md`

- [ ] T7 · Referencia SciPy y contraste de los casos a mano (casos 1–4, 6, 7, 8)
  - Archivos: `rutas/r3/referencia.py` (stub primero; luego `vertices_scipy(puntos)`: `ConvexHull(numpy.array(puntos, dtype=numpy.float64))`, vértices `hull.vertices` → tuplas de `int` de Python → `normalizar`; deja pasar `QhullError`)
  - Test primero: `tests/test_envolvente_clase.py::test_casos_a_mano_contra_scipy` (parametrizada con los puntos de los casos 1, 2, 3, 4 y 8: `set(envolvente(p)) == set(vertices_scipy(p))` y `normalizar(envolvente(p)) == vertices_scipy(p)`), `::test_scipy_falla_en_degenerados` (con `R3.scipy_falla.colineales`, `dos_puntos` y los alineados del caso 6: `pytest.raises(scipy.spatial.QhullError)` en `vertices_scipy`, y `envolvente` da los dos extremos sin error), `::test_vertices_scipy_son_int` (tipo `int` de Python, no `numpy.int64`)
  - Verificar: `.venv/bin/python -m pytest tests/test_envolvente_clase.py -k "scipy"`
  - anotar en `docs/anexo-ia.md`

- [ ] T8 · Casos de la clase desde la copia versionada (casos 2, 3, 10)
  - Archivos: solo pruebas en `tests/test_envolvente_clase.py` (usan `cargar_casos_r3()`)
  - Test primero: `::test_caso_10_red_clase` (los 9 nodos de `red.nodos`: `envolvente` traducida a ids con un `dict` coordenada → id da `R3.nodos_red.vertices` = `[9, 7, 8, 3, 2]`; los nodos 4 y 6 (`no_vertices_sobre_lado`) no están; `area(vertices) == R3.nodos_red.area_m2 == 585000`; igual a `vertices_scipy`; `comprobar_envolvente`), `::test_caso_2_empate_json` (`R3.empate.puntos` → `R3.empate.vertices` como tuplas), `::test_caso_3_rectangulo_json` (`R3.rectangulo`)
  - Ver fallar: el código ya existe; se valida con una **mutación temporal** en `_lado` (desempatar por el **mayor** lexicográfico, o repartir con `>= 0`) que debe hacer fallar al menos el caso 2 o el 10, y se restaura
  - Verificar: `.venv/bin/python -m pytest tests/test_envolvente_clase.py`
  - anotar en `docs/anexo-ia.md`

- [ ] T9 · Propiedad contra SciPy y cuadrados aleatorios (casos 11, 12, 13)
  - Archivos: `tests/test_envolvente_propiedad.py` (solo pruebas)
  - Test primero: `::test_caso_11_aleatorios_vs_scipy` (`random.Random(2026)`; 100 conjuntos con `n` entre 3 y 200 y coordenadas enteras en `[-10, 10]` (pequeñas para forzar alineados y repetidos), pasados **sin** `preparar_puntos` para ejercitar los repetidos; cada uno: `comprobar_envolvente`; si `len(envolvente(p)) ≥ 3` → `set` igual y normalizado igual a `vertices_scipy(p)`; si no (degenerado) se salta SciPy y se cuenta; al final al menos 90 conjuntos comparados con SciPy), `::test_caso_12_cuadrados` (parametrizada con 1 000, 10 000 y 50 000: `puntos_cuadrado(n)` → `envolvente` = `vertices_scipy` normalizado; `comprobar_envolvente`; `0.5 * e ≤ h ≤ 2 * e` con `e = (8/3) * math.log(len(puntos))`)
  - Ver fallar: mutación temporal en `envolvente.py` (repartir con `>= 0` en lugar de `> 0`, que mete alineados como vértices) que debe hacer fallar el caso 11; restaurar
  - Verificar: `.venv/bin/python -m pytest tests/test_envolvente_propiedad.py -k "caso_11 or caso_12"`
  - anotar en `docs/anexo-ia.md`

- [ ] T10 · Todos los puntos son vértices: círculo y parábola sin `RecursionError` (casos 15, 16)
  - Archivos: `tests/test_envolvente_propiedad.py`, `tests/test_envolvente.py`
  - Test primero: `tests/test_envolvente_propiedad.py::test_caso_15_circulo` (2 000 puntos `(redondear(10**6 * cos(2πk/2000)), redondear(10**6 * sin(2πk/2000)))`, `k = 0 … 1999`: los 2 000 son distintos y la salida tiene 2 000 vértices; igual a `vertices_scipy`; `comprobar_envolvente`), `::test_caso_16_parabola` (`(k, k*k)` para `k = 0 … 4 999`: 5 000 vértices, el primero `(0, 0)`, `comprobar_envolvente` (convexidad estricta exacta con enteros; la contención se omite porque todos son vértices)); `tests/test_envolvente.py::test_limite_de_recursion` (tras `import rutas.r3.envolvente`, `sys.getrecursionlimit() >= 20_000`)
  - Ver fallar: el código ya existe; se valida comentando temporalmente el `setrecursionlimit` y corriendo `test_limite_de_recursion` (falla); restaurar. Anotar en el reporte la profundidad máxima observada en el círculo y la parábola (se espera O(log n) por particiones parejas, ver plan)
  - Verificar: `.venv/bin/python -m pytest tests/test_envolvente_propiedad.py tests/test_envolvente.py`
  - anotar en `docs/anexo-ia.md`

**Fin de B2:** `.venv/bin/python -m pytest -m "not red"` en verde. **Detenerse** y entregar el reporte. Esperar el commit del usuario.

## B3 · Red real, archivos de la envolvente y gráfica

- [ ] T11 · Puntos de la red y envolvente real (caso 14, marcador `red`)
  - Archivos: `rutas/r3/puntos.py` (implementar `puntos_de_grafo(G)`: `x_utm`, `y_utm` de `sorted(G.nodes)` → `preparar_puntos`); `tests/test_red_real_r3.py` (crear con `pytestmark = pytest.mark.red`; usa la fixture `grafo_procesado_real`)
  - Test primero: `tests/test_puntos_r3.py::test_puntos_de_grafo_sintetico` (no `red`: `grafo_sintetico` de 3 nodos con `x_utm`/`y_utm` puestos a mano, dos de ellos iguales tras redondear → 2 puntos `int`), `tests/test_red_real_r3.py::test_caso_14_red_real` (8 791 puntos distintos; `envolvente` = `vertices_scipy` (por conjunto y normalizados); **14** vértices; `abs(area(v) − ConvexHull(numpy.array(puntos)).volume) ≤ 1`; `comprobar_envolvente` con los 8 791 puntos; todas las coordenadas dentro de x 401 796–446 623, y 464 304–520 840)
  - Ver fallar: `puntos_de_grafo` con `NotImplementedError`; la `red` con una mutación temporal (repartir con `>= 0` en lugar de `> 0` en `_lado`, que agrega alineados como vértices o rompe la igualdad con SciPy) y restaurar
  - Verificar: `.venv/bin/python -m pytest tests/test_puntos_r3.py && .venv/bin/python -m pytest tests/test_red_real_r3.py -k caso_14`
  - anotar en `docs/anexo-ia.md`

- [ ] T12 · Archivos de la envolvente para R5 (caso 17; Requerimiento 5 «ver la envolvente»)
  - Archivos: `rutas/r3/archivos.py` (stubs primero; luego `escribir_envolvente(vertices, carpeta=DATA_PROCESSED)` y `main(processed=DATA_PROCESSED)` como en el plan; `if __name__ == "__main__": main()`); `tests/test_archivos_r3.py`; `tests/test_red_real_r3.py`
  - Test primero: `tests/test_archivos_r3.py::test_caso_17_sintetico` (un polígono de 4 vértices en coordenadas UTM del Quindío (p. ej. alrededor de x 420 000, y 500 000) en `tmp_path`: el CSV tiene encabezado `orden,x_utm,y_utm,lat,lon`, 4 filas, `orden` 1..4, `x_utm`/`y_utm` enteros; el GeoJSON es `FeatureCollection` con un `Polygon` cuyo anillo tiene 5 posiciones y la última = la primera, `properties.vertices == 4` y `area_km2 == area(v) / 1e6`; ida y vuelta `a_utm(lon, lat)` vs `x_utm`, `y_utm` con error < 1 m en cada vértice), `::test_main_sintetico` (carpeta `processed` en `tmp_path` con un grafo de `grafo_sintetico` + `agregar_utm_a_nodos` guardado con `guardar_grafo`: escribe los dos archivos), `::test_main_no_escribe_si_difiere_de_scipy` (`monkeypatch` de `vertices_scipy` en el módulo para devolver otra lista → `ValueError` y no existe ningún archivo), `tests/test_red_real_r3.py::test_caso_17_archivos_reales` (se salta si falta `data/processed/envolvente.csv`: 14 filas = vértices de `envolvente` sobre la red; GeoJSON cerrado con 15 posiciones; ida y vuelta < 1 m; `area_km2` ≈ 1 631,5 ± 1)
  - Ejecutar (no es una medición de tiempo; lo corre el implementer, como la matriz de R2): `.venv/bin/python -m rutas.r3.archivos` para generar `data/processed/envolvente.csv` y `data/processed/envolvente.geojson`
  - Verificar: `.venv/bin/python -m pytest tests/test_archivos_r3.py && .venv/bin/python -m pytest tests/test_red_real_r3.py`
  - anotar en `docs/anexo-ia.md`

- [ ] T13 · Gráfica del polígono desde los datos (`r3_envolvente.png`)
  - Archivos: `rutas/r3/tablas.py` (crear con `grafica_envolvente` y `main` como stubs; implementar aquí `grafica_envolvente(processed=DATA_PROCESSED, salida=RESULTS_R3)`: crea la carpeta si no existe, lee el grafo y `envolvente.csv`, dibuja nodos grises pequeños, polígono cerrado en rojo con marcadores, ejes «x UTM (m)» / «y UTM (m)», aspecto igual, título con n y número de vértices; `matplotlib.use("Agg")`)
  - Test primero: `tests/test_tablas_r3.py::test_grafica_crea_png` (carpeta sintética como en `test_main_sintetico` de T12, con `escribir_envolvente`: el PNG existe y no está vacío), `::test_grafica_titulo_con_n_y_vertices` (espiando `Axes.set_title` como en `tests/test_tablas_r2.py`: el título contiene n y el número de vértices)
  - Ejecutar (no es medición): `.venv/bin/python -c "from rutas.r3.tablas import grafica_envolvente; print(grafica_envolvente())"` → `results/r3/r3_envolvente.png`
  - Verificar: `.venv/bin/python -m pytest tests/test_tablas_r3.py -k grafica`
  - anotar en `docs/anexo-ia.md`

**Fin de B3:** `.venv/bin/python -m pytest` en verde (incluidas las `red` de R1, R2 y R3; ninguna de R3 saltada salvo `test_resultados_medidos`, que aún no existe). **Detenerse** y entregar el reporte con el número de vértices y el área de la red (km²) y la imagen generada. Esperar el commit del usuario.

## B4 · Medición, tablas y comando para el usuario

- [ ] T14 · Script de medición con comprobación previa (punto 2; sección 6)
  - Archivos: `rutas/r3/medir_envolvente.py` (stubs primero; luego `TAMANOS`, `COLUMNAS`, `NOMBRE_RED`, `nombre_cuadrado`, `conjuntos`, `comprobar_iguales`, `medir_conjunto(nombre, puntos, repeticiones=5, medir=medir_en_proceso)`, `main(processed=DATA_PROCESSED, salida=RESULTS_R3, repeticiones=5)` como en el plan; `if __name__ == "__main__": main()`)
  - Test primero: `tests/test_medir_envolvente.py::test_nombres_y_orden_del_anexo` (`nombre_cuadrado(1000) == "Cuadrado, 1 000 puntos"`, `nombre_cuadrado(50000) == "Cuadrado, 50 000 puntos"`; `conjuntos(puntos_red, tamanos=(10, 20))` da `["Nodos de la red", "Cuadrado, 10 puntos", "Cuadrado, 20 puntos"]` con sus `n_pedido`), `::test_comprobar_iguales_error_explicito` (`monkeypatch` de `vertices_scipy` en el módulo que devuelve otra lista → `ValueError` cuyo mensaje contiene el nombre del conjunto; no es `AssertionError`), `::test_medir_conjunto_con_medidor_falso` (medidor falso que registra `(funcion, preparar())` y devuelve un `ResultadoMedicion` fijo: se llama primero con `envolvente` y la **lista** de puntos, luego con `scipy.spatial.ConvexHull` y un `numpy.ndarray` de `float64` con los mismos valores; la fila tiene `list(fila) == COLUMNAS`, `n`, `vertices` correctos y `cociente == propio / scipy`), `::test_no_completada` (medidor falso que devuelve `NO_COMPLETADA` para la propia → `tiempo_propio_ms == "no completada"` y `cociente == "no completada"`), `::test_repeticiones_minimo`, `::test_medir_en_proceso_de_verdad` (cuadrado de 200 puntos, `repeticiones=1`: tiempos > 0), `::test_main_sintetico_escribe_archivos` (carpeta sintética como en T12, `monkeypatch` de `TAMANOS` a `(50, 100)` y `repeticiones=1`: existen `r3_envolvente.csv` (3 filas en orden, columnas del Anexo al inicio), `r3_puntos.json` (`"semilla": 2026`, `n_pedido`/`n_obtenido` por conjunto, regla de redondeo) y `maquina.json`), `::test_main_no_escribe_si_difieren` (`vertices_scipy` alterado → `ValueError` y la carpeta de salida sin archivos)
  - Verificar: `.venv/bin/python -m pytest tests/test_medir_envolvente.py`
  - anotar en `docs/anexo-ia.md`

- [ ] T15 · Tablas de R3 desde los archivos (`tablas_r3.md`; punto 2 y sección 6.8)
  - Archivos: `rutas/r3/tablas.py` (implementar `main(results=RESULTS_R3, processed=DATA_PROCESSED)`: lee `r3_envolvente.csv` con `keep_default_na=False`, `r3_puntos.json`, `maquina.json` y `envolvente.geojson`; escribe `tablas_r3.md` con la tabla del Anexo (`Conjunto de puntos | n | Vértices de la envolvente | Tiempo propio (ms) | Tiempo SciPy (ms) | Cociente | Repeticiones`, tiempos con 3 decimales y cociente con 1), la tabla «Vértices frente a (8/3) ln n» de los cuadrados, semilla y n pedidos/obtenidos, envolvente de la red (vértices y área en km²) y máquina; llama a `grafica_envolvente`; reutiliza `a_markdown`)
  - Test primero: `tests/test_tablas_r3.py::test_tablas_salen_de_los_archivos` (CSV/JSON sintéticos en `tmp_path` + carpeta `processed` sintética: el Markdown contiene los valores del CSV, la semilla 2026, los cuatro nombres en orden, «ms» en los encabezados, el área del GeoJSON y el procesador de `maquina.json`), `::test_no_completada_se_muestra` (una fila «no completada» aparece como texto y no rompe la tabla), `::test_referencia_renyi_sulanke` (para `n = 1000` la columna de referencia muestra `18.4`), `::test_main_genera_todo` (Markdown y PNG en `tmp_path`)
  - Verificar: `.venv/bin/python -m pytest tests/test_tablas_r3.py`
  - anotar en `docs/anexo-ia.md`

- [ ] T16 · Prueba de los resultados medidos y entrega del comando de medición real al usuario
  - Archivos: `tests/test_red_real_r3.py` (agregar `comprobar_resultados_r3(df, puntos_json)` y `::test_resultados_medidos`: se salta si falta `results/r3/r3_envolvente.csv`; 4 filas en el orden del Anexo; las 6 columnas del Anexo al inicio y en ese orden; fila de la red con `n == 8791` y `vertices == 14`; `n` de cada cuadrado = `n_obtenido` de `r3_puntos.json` y ≤ pedido; tiempos numéricos > 0 o `"no completada"`; `cociente` = propio / SciPy (relativo 1e-9) cuando ambos son numéricos; `vertices` de cada cuadrado = `len(envolvente(puntos_cuadrado(n_pedido)))`); `tests/test_medir_envolvente.py` (pruebas de `comprobar_resultados_r3` con CSV sintéticos alterados: fila faltante, orden cambiado, cociente mal calculado, vértices de la red ≠ 14 → `AssertionError`; CSV correcto → pasa)
  - Test primero: las pruebas con CSV alterados se ven fallar antes de escribir `comprobar_resultados_r3` (stub); con el CSV real ausente, `test_resultados_medidos` queda saltada
  - **No ejecutar la medición.** Entregar al usuario el comando exacto, para correr con el portátil enchufado y sin otros procesos pesados:
    ```bash
    cd /Users/santiagopolaniapinzon/proyecto-final-rutas-quindio && .venv/bin/python -m rutas.r3.medir_envolvente && .venv/bin/python -m rutas.r3.tablas && .venv/bin/python -m pytest tests/test_red_real_r3.py
    ```
  - Estimación para el usuario (dar en el reporte, medida con una corrida de prueba de `envolvente` sobre los cuatro conjuntos, 1 repetición, **sin** escribir en `results/`): se esperan décimas de segundo por conjunto en la propia y milisegundos en SciPy; la corrida completa (con la carga del grafo) debería tardar menos de 1 minuto
  - Verificar (lo hace el usuario): `results/r3/` tiene `r3_envolvente.csv` (4 filas), `r3_puntos.json`, `maquina.json`, `tablas_r3.md`, `r3_envolvente.png`; `tests/test_red_real_r3.py` pasa sin saltadas
  - anotar en `docs/anexo-ia.md`

**Fin de B4:** `.venv/bin/python -m pytest -m "not red"` en verde y el comando de T16 entregado. **Detenerse.** El usuario corre la medición y hace su commit.

## Cierre

- [ ] T17 · Anexo de IA y «Reproducir R3» en el README
  - Archivos: `docs/anexo-ia.md` (local; entradas de R3: plan y tareas con el agente planner; código y pruebas con el implementer; cómo se verificó: casos a mano 1–9, red de la clase (10), propiedad y cuadrados contra SciPy (11, 12), invariantes (13), red real contra SciPy y área (14), círculo y parábola (15, 16), ida y vuelta de coordenadas (17), mutaciones temporales); `README.md` (sección «Reproducir R3» después de «Reproducir R2»: requisito de haber corrido R1; tabla con `rutas.r3.archivos`, `rutas.r3.medir_envolvente`, `rutas.r3.tablas` y lo que deja cada uno; semilla 2026 y regla de redondeo; nota de medir enchufado; pruebas `pytest -m "not red"`, `pytest tests/test_red_real_r3.py` y `pytest`)
  - Test primero: no aplica (documentación)
  - Verificar: `grep -n "R3" docs/anexo-ia.md && grep -n "rutas.r3.medir_envolvente" README.md`
  - anotar en `docs/anexo-ia.md`

- [ ] T18 · Suite completa y regeneración de todos los resultados de R3 (la ejecuta el usuario con el portátil enchufado)
  - Archivos: ninguno nuevo (regenera `data/processed/envolvente.csv`, `data/processed/envolvente.geojson` y `results/r3/*`)
  - Test primero: no aplica
  - Comando que se entrega al usuario:
    ```bash
    cd /Users/santiagopolaniapinzon/proyecto-final-rutas-quindio && .venv/bin/python -m rutas.r3.archivos && .venv/bin/python -m rutas.r3.medir_envolvente && .venv/bin/python -m rutas.r3.tablas && .venv/bin/python -m pytest
    ```
  - Verificar: todas pasan y ninguna `red` saltada; `envolvente.csv` y `.geojson` sin cambios respecto a B3 (mismo grafo → mismos bytes); `results/r3/` con los 5 archivos de la spec (`r3_envolvente.csv`, `r3_puntos.json`, `maquina.json`, `tablas_r3.md`, `r3_envolvente.png`)

## Cobertura

| Caso / punto | Tarea |
|---|---|
| Copia de la sección `R3` en `tests/datos/red_clase.json` (Decisiones, Puerta 1) | T2 |
| Tarea pequeña de R2: unidad de la pendiente por versión (Decisiones, Puerta 1) | T3 |
| Predicado de giro (Comportamiento 1) | T4 |
| 1 cuadrado con extras | T6, T7 |
| 2 desempate | T6, T7, T8 |
| 3 rectángulo con puntos en los lados | T6, T7, T8 |
| 4 pentágono con interior | T6, T7 |
| 5 duplicados | T5, T6 |
| 6 alineados (+ `QhullError` en SciPy) | T6, T7 |
| 7 un punto, vacío, dos puntos (+ `QhullError`) | T6, T7 |
| 8 coordenadas grandes | T4, T6, T7 |
| 9 redondeo | T5 |
| 10 red de la clase (vértices 9, 7, 8, 3, 2; área 585 000 m²) | T2, T8 |
| 11 propiedad contra SciPy (100 conjuntos, semilla 2026) | T9 |
| 12 cuadrados 1 000 / 10 000 / 50 000 contra SciPy y (8/3) ln n | T5, T9, T16 |
| 13 invariantes geométricos | T6 (helper), T7–T12 (en cada salida) |
| 14 red real (14 vértices, área ± 1 m²) | T11 |
| 15 círculo (2 000 vértices, sin `RecursionError`) | T10 |
| 16 parábola (5 000 vértices, sin `RecursionError`) | T10 |
| 17 archivos (`envolvente.csv`, `.geojson`, ida y vuelta < 1 m) | T12 |
| Recursión con `sys.setrecursionlimit(20_000)` documentado (Comportamiento 3) | T4, T10 |
| Bordes: 0/1/2 puntos, todos alineados, repetidos, punto sobre un lado, todos vértices, negativas y grandes | T6, T7, T10 |
| Enunciado R3, párrafo «Coordenadas»: UTM 18N, entero más cercano, quitar repetidos, giros con enteros (64 bits → `int` de Python), alineados no son vértices | T4, T5, T6, T11 |
| Enunciado R3, punto 1: divide y vencerás propio (QuickHull), justificación por la distribución (informe), `scipy.spatial.ConvexHull` con los mismos vértices en todas las pruebas | T6–T12 (y texto del informe) |
| Enunciado R3, punto 2: medir ambas con la red y con 1 000 / 10 000 / 50 000 al azar con semilla fija; tabla; comparar y explicar (Qhull en C vía Cython) | T5, T14, T15, T16 (explicación en el informe) |
| Sección 6.1 misma máquina y `maquina.json` | T14, T16 |
| Sección 6.2 solo el algoritmo (preparación y conversión a NumPy fuera) | T14 |
| Sección 6.3 5 repeticiones, mediana, una si > 1 min | T14 (vía `medir_en_proceso`) |
| Sección 6.4 unidad ms | T14, T15 |
| Sección 6.5 semilla fija documentada (`r3_puntos.json`) | T5, T14 |
| Sección 6.6 verificación antes de medir (`comprobar_iguales`, `ValueError`) | T6–T12, T14 |
| Sección 6.7 límite de 5 min → «no completada» | T14, T15 |
| Sección 6.8 tablas y gráficas desde CSV/JSON | T13, T15 |
| Anexo, Requerimiento 3 (columnas y filas en orden) | T14, T15, T16 |
| Requerimiento 5 «ver la envolvente sobre el mapa» (archivo que consume) | T12 |
| Anexo de IA | T17 (y cada tarea con IA) |

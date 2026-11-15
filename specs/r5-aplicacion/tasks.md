# Tareas — R5 Aplicación (Flask + Folium)

Spec: `spec.md` · Plan: `plan.md`. Todas las órdenes se corren desde la raíz del repositorio (`/Users/nicolascastro/Desktop/proyecto-final-rutas-quindio`) con `.venv/bin/python` (Python 3.13.18, Flask 3.1.3 y Folium 0.20.0 ya instalados; no hay que instalar nada).

Cada tarea en la que se use IA termina con: **anotar en `docs/anexo-ia.md`** (fecha, integrante, herramienta, qué se generó, cómo se verificó).

> **Reglas del usuario:**
> 1. Cada bloque termina con todas sus pruebas en verde y el trabajo se **DETIENE** hasta que el usuario haga su commit. No se empieza el bloque siguiente antes.
> 2. Test primero **tarea por tarea**: escribir la prueba de una tarea, verla fallar por la razón correcta (el módulo existe con funciones que hacen `raise NotImplementedError`; no un `ModuleNotFoundError` global) y solo entonces escribir el código. El reporte de cada bloque lo confirma tarea por tarea.
> 3. No modificar `.gitignore` sin preguntar. `docs/` está ignorada: `docs/anexo-ia.md` se mantiene en local.
> 4. Nunca `git add`, `git commit` ni `git push`.
> 5. **R5 no modifica `rutas/r1..r4/`** (Puerta 1). Si algo no encaja, se detiene y se pregunta; no se “arregla” R1–R4.
> 6. No se agregan dependencias: `requirements.txt` no cambia.

> **Simplicidad:** código legible que cada integrante pueda explicar en la sustentación. `servicios.py` no importa Flask ni produce HTML; `mapas.py` solo arma Folium; `app.py` solo lee parámetros, llama a servicios y mapas, y elige plantilla y código HTTP. Cada ruta de `app.py` cabe en una pantalla. Las plantillas heredan de `base.html` y no llevan `<script>`. Ningún archivo de `rutas/r5/` implementa un algoritmo: Dijkstra, Held-Karp, el voraz y la regla de las 11 h se importan de R2 y R4.

Orden de la suite al cerrar cada bloque: `.venv/bin/python -m pytest -m "not red" -q` (hoy: 412 pasan y 1 se salta; cada bloque solo debe sumar pruebas en verde).

## B1 · Configuración, formato, datos sintéticos y carga única

- [x] T1 · Comprobar el entorno
  - Archivos: ninguno
  - Pasos: `.venv/bin/python --version` (3.13.x) y que importan `flask`, `folium`, `jinja2`; la suite sin `red` en verde antes de empezar
  - Test primero: no aplica (entorno)
  - Verificar: `.venv/bin/python --version && .venv/bin/python -c "import flask, folium, jinja2; print('ok')" && .venv/bin/python -m pytest -m "not red" -q`

- [x] T2 · Paquete `rutas/r5`, constantes y guardia de “sin algoritmos ni JS propio”
  - Archivos: `rutas/config.py` (agregar al final `RESULTS = RAIZ / "results"`, `HOST_R5 = "127.0.0.1"`, `PUERTO_R5 = 5050`; no tocar lo demás); `rutas/r5/__init__.py` (vacío); stubs con docstrings del plan y `raise NotImplementedError` en `rutas/r5/formato.py`, `datos.py` (`DatosFaltantes` y `DatosApp` ya definidas; `archivos_faltantes`, `cargar_datos` como stubs), `servicios.py`, `mapas.py`, `app.py`; carpeta `rutas/r5/templates/` con `base.html` mínimo (sin `<script>`)
  - Test primero: `tests/test_config.py::test_rutas_r5` (`RESULTS == RAIZ / "results"`; `RESULTS_R1.parent == RESULTS` … `RESULTS_R4.parent == RESULTS`; `PUERTO_R5 == 5050`; `HOST_R5 == "127.0.0.1"`); `tests/test_app_r5.py::test_sin_algoritmos_ni_js_propio` (lee el texto de cada `rutas/r5/*.py`: no contiene `import heapq`, `networkx`, `scipy`, `itertools`; lee cada `rutas/r5/templates/*.html`: no contiene `<script`; `requirements.txt` sigue teniendo `Flask==3.1.3` y `folium==0.20.0`). La primera falla con `ImportError` de `RESULTS`; la segunda pasa con los stubs y queda como guardia
  - Verificar: `.venv/bin/python -m pytest tests/test_config.py tests/test_app_r5.py -k "r5 or algoritmos"`
  - anotar en `docs/anexo-ia.md`

- [x] T3 · Números con coma decimal (Puerta 1: coma decimal)
  - Archivos: `rutas/r5/formato.py` (`numero(valor, decimales=1)` como en el plan)
  - Test primero: `tests/test_formato_r5.py::test_coma_decimal` (parametrizada: `(29.7239, 1) → "29,7"`, `(1783.39, 1) → "1 783,4"`, `(1631.4960175, 1) → "1 631,5"`, `(6.600187, 2) → "6,60"`, `(0, 1) → "0,0"`, `(7360, 0) → "7 360"`, `(178.6557, 1) → "178,7"`, `(190.4473, 1) → "190,4"`, `(11.7916, 1) → "11,8"`), `::test_acepta_numpy` (`numpy.float64(1.25)` con 2 → `"1,25"`)
  - Verificar: `.venv/bin/python -m pytest tests/test_formato_r5.py`
  - anotar en `docs/anexo-ia.md`

- [x] T4 · Datos sintéticos de prueba (fixture compartido)
  - Archivos: `tests/conftest.py` (agregar al final, sin tocar lo existente: `carpeta_app_sintetica(tmp_path, visitas=None)` → `(processed, catalogo, results)` exactamente como en el plan, «Datos sintéticos de prueba»: 6 nodos, anillo con 2→1 = 90 s, arista 1→2 con geometría curva de 3 puntos, 8 lugares C01, C02, A01..A06 con sus nodos, visitas 30/60/30/60/30/60 o `visitas`, matriz con `calcular_matriz` + `guardar_matriz` de R2, `envolvente.geojson` cuadrado con `vertices: 4`, y `results/r2`, `results/r4` (sin `r4_exactas.csv` ni `r4_tiempo_vs_k.png`); fixtures `datos_app` y `cliente_app` que dependen de `cargar_datos` y `crear_app` y por eso se usan desde T5 y T13)
  - Test primero: `tests/test_datos_r5.py::test_fixture_sintetico` (la carpeta tiene los 4 archivos de `processed`, el catálogo con 8 filas y 6 atractivos, `matriz_tiempos.csv` 8 × 8 con `M["A01"]["C01"] == 90` y `M["C01"]["A01"] == 60`, el GeoJSON con 5 puntos en el anillo). Falla antes de escribir el helper (`ImportError`/`AttributeError` del helper en `tests.conftest`)
  - Verificar: `.venv/bin/python -m pytest tests/test_datos_r5.py -k fixture`
  - Nota: la prueba usa `M.loc[fila, columna]` en vez de la forma `M[...][...]`, porque en pandas `M[col][fila]` invierte el sentido; el valor comprobado es el mismo (A01 -> C01 = 90 s, C01 -> A01 = 60 s).
  - anotar en `docs/anexo-ia.md`

- [x] T5 · `cargar_datos` y `DatosFaltantes` (caso 13; Comportamiento 1; casos borde «Archivo procesado faltante»)
  - Archivos: `rutas/r5/datos.py` (`COMANDOS_DATOS`, `archivos_faltantes`, `cargar_datos` según el plan; `nodo_de` con `int()`; `atractivos` en orden del catálogo; `visita_min` como `float`)
  - Test primero: `tests/test_datos_r5.py::test_carga_sintetica` (`DatosApp` con `len(datos.nodo_de) == 8`, todos los valores `int` de Python, `datos.atractivos == ["A01", …, "A06"]`, `datos.visita_min["A02"] == 60.0`, `datos.nombre_de["C01"]`, `datos.envolvente["features"][0]["properties"]["vertices"] == 4`, `datos.red.ids == sorted(datos.G.nodes)`), `::test_caso_13_carpeta_vacia` (`processed` vacía en `tmp_path` → `DatosFaltantes` cuyo mensaje contiene `grafo_componente.graphml` y `python -m rutas.r1.construir_red`), `::test_cada_faltante_con_su_comando` (parametrizada: se borra uno a uno `lugares_nodos.csv`, `matriz_tiempos.csv`, `envolvente.geojson` y el catálogo de la carpeta sintética → el mensaje nombra ese archivo y su comando: `rutas.r1.construir_red`, `rutas.r2.matriz`, `rutas.r3.archivos`, «restaurarlo con git»), `::test_grafo_comprimido_cuenta` (renombrar a `.graphml.gz` comprimido con `gzip` → no falta)
  - Verificar: `.venv/bin/python -m pytest tests/test_datos_r5.py`
  - Cierre de B1: `.venv/bin/python -m pytest -m "not red" -q` en verde. **DETENERSE** hasta el commit del usuario
  - Nota: `DatosFaltantes` lleva una línea por archivo (`falta <ruta>: <comando>`); `cargar_datos` se probó también con los datos reales (42 lugares, 15 atractivos).
  - anotar en `docs/anexo-ia.md`

## B2 · Servicios: ruta, itinerario y resultados (sin Flask) y pruebas con la red real

- [x] T6 · Coordenadas que siguen la geometría (caso 15)
  - Archivos: `rutas/r5/servicios.py` (`coordenadas_de(G, ids_nodos)`)
  - Test primero: `tests/test_servicios_r5.py::test_caso_15_geometria_curva` (nodos 1→2 → `[(4.50, -75.70), (4.505, -75.69), (4.50, -75.68)]` en ese orden), `::test_sin_duplicar_uniones` (1→2→3 → 4 puntos, el último `(4.50, -75.66)`; ningún par consecutivo repetido), `::test_segmento_recto_sin_geometria` (2→3 → `[(4.50, -75.68), (4.50, -75.66)]`), `::test_un_nodo_sin_linea` (`[1]` → `[]`)
  - Ver fallar: con `NotImplementedError` del stub
  - Verificar: `.venv/bin/python -m pytest tests/test_servicios_r5.py -k "caso_15 or uniones or recto or un_nodo"`
  - Nota: las pruebas de T6 a T10 usan `M.loc[fila, columna]` en vez de `M[...][...]` (pandas invierte el sentido con la segunda forma).
  - anotar en `docs/anexo-ia.md`

- [x] T7 · `ruta_entre` y `validar_lugar` (casos 3 y 4 sintéticos; borde «lugar desconocido»)
  - Archivos: `rutas/r5/servicios.py` (`ErrorEntrada`, `validar_lugar`, `ruta_entre` según el plan: `consultar(..., "cola_prioridad")` con `perf_counter` alrededor, `detalle_ruta`, `coordenadas_de`, `aviso`)
  - Test primero: `tests/test_servicios_r5.py::test_ruta_sintetica` (C01→A02: `tiempo_s == M["C01"]["A02"]` ± 1e-6, `ids_nodos == [1, 2, 3]`, `distancia_km == 1.0`, `tiempo_min == tiempo_s / 60`, `nodos_explorados > 0`, `computo_ms >= 0`, 4 coordenadas, `aviso is None`), `::test_caso_3_mismo_lugar` (C01→C01: `tiempo_s == 0`, `coordenadas == []`, `aviso == "origen y destino son el mismo lugar"`), `::test_mismo_punto_sintetico` (A02→A06: `tiempo_s == 0`, `aviso == "los dos lugares están en el mismo punto de la red"`), `::test_lugar_desconocido` (`ruta_entre(datos, "X99", "C01")` → `ErrorEntrada` con mensaje `"lugar desconocido: X99"`; igual con el destino), `::test_asimetria_sintetica` (A01→C01 = 90 y C01→A01 = 60)
  - Verificar: `.venv/bin/python -m pytest tests/test_servicios_r5.py -k "ruta or mismo or desconocido or asimetria"`
  - anotar en `docs/anexo-ia.md`

- [x] T8 · Validación del itinerario (caso 8 a nivel de servicio)
  - Archivos: `rutas/r5/servicios.py` (`validar_itinerario` con los mensajes y el orden del plan)
  - Test primero: `tests/test_servicios_r5.py::test_caso_8_validacion` (parametrizada, partida y lista → fragmento del mensaje: `C01` + 5 atractivos → «entre 6 y 8»; `C01` + 9 ids → «entre 6 y 8»; `C01` + `[]` → «(llegaron 0)»; `C01` + `A01, A01, A02, A03, A04, A05` → «repetido: A01»; `A01` + `A01..A06` → «la partida A01»; `C01` + `A01..A05, C02` → «C02 no es un atractivo turístico»; `X99` + `A01..A06` → «lugar desconocido: X99»), `::test_validacion_correcta` (`C01` + `A01..A06` no lanza; partida `C02` también vale: cualquier lugar)
  - Verificar: `.venv/bin/python -m pytest tests/test_servicios_r5.py -k "caso_8 or validacion"`
  - anotar en `docs/anexo-ia.md`

- [x] T9 · `itinerario`: Held-Karp, voraz, tramos y regla de las 11 h (casos 5, 6 y 7 en sintéticos)
  - Archivos: `rutas/r5/servicios.py` (`itinerario` según el plan: `validar_itinerario`; `resolver_por_ids` para `"held_karp"` y `"vecino_mas_cercano"`; tiempos; tramos con `consultar` + `coordenadas_de`; `diferencia_min`, `brecha_pct` (0 si HK = 0); si HK no cabe, adaptador a `itinerario_dia` con `matriz_a_listas` y `visitas_del_catalogo`, y el dict `jornada` del plan)
  - Test primero: `tests/test_servicios_r5.py::test_itinerario_cabe_sintetico` (C01 + A01..A06: `held_karp.desplazamiento_min * 60 == resolver_por_ids(M, …, "held_karp")[0]` ± 1e-6; `recorrido` igual al de `resolver_por_ids`; `visitas_min == 270` en los dos; `jornada_min == desplazamiento + 270`; `cabe` verdadero; `diferencia_min >= 0`; `jornada is None`), `::test_tramos_igual_a_matriz_sintetico` (por método: un tramo por par consecutivo del recorrido, `tiempo_min * 60 == M[desde][hasta]` ± 1e-6; suma de tramos = desplazamiento ± 1e-6 × 60), `::test_itinerario_no_cabe_sintetico` (carpeta con `visitas=[120] * 6`: `held_karp.cabe` falso, `jornada["quitados"]` no vacío y cada quitado con `id`, `lugar` (nombre del catálogo), `visita_min == 120`, `desvio_min`, `ahorro_min`; `jornada_final_min <= 660`; `recorrido_final` empieza y termina en C01 y **no** contiene los quitados; los tramos y el recorrido de HK siguen siendo los de los 6 elegidos), `::test_no_llama_resolver_si_invalido` (monkeypatch de `rutas.r5.servicios.resolver_por_ids` con contador; 5 atractivos → `ErrorEntrada` y contador en 0)
  - Verificar: `.venv/bin/python -m pytest tests/test_servicios_r5.py -k "itinerario or tramos or resolver"`
  - anotar en `docs/anexo-ia.md`

- [x] T10 · `resultados` con la lista fija (caso 11 a nivel de servicio)
  - Archivos: `rutas/r5/servicios.py` (`ARCHIVOS_RESULTADOS` con un comando por archivo, la tabla del plan; `resultados(requerimiento, results=RESULTS)`)
  - Test primero: `tests/test_servicios_r5.py::test_caso_11_resultados_sinteticos` (con `results` sintético: `resultados("r2", results)["imagenes"] == ["r2_tiempo_vs_explorados.png"]`, una tabla con nombre `r2_cociente.csv` cuyo HTML contiene `<table` y la columna `mediana`; `resultados("r4", results)["faltantes"]` contiene `("r4_exactas.csv", ".venv/bin/python -m rutas.r4.medir_exactas")` y `("r4_tiempo_vs_k.png", ".venv/bin/python -m rutas.r4.tablas")`), `::test_texto_escapado` (CSV con una celda `<b>x</b>` → aparece `&lt;b&gt;`), `::test_celdas_vacias` (CSV con una celda vacía no da `nan`), `::test_requerimiento_desconocido` (`"r9"` → `KeyError`), `::test_lista_fija_existe_en_results` (sin `red`, contra `RESULTS` real: todo archivo de `ARCHIVOS_RESULTADOS` existe salvo exactamente `r1_tiempos_componente.png`, `r4_exactas.csv` y `r4_tiempo_vs_k.png`; si el usuario ya corrió alguno, la prueba admite que exista: el conjunto de faltantes ⊆ esos tres)
  - Verificar: `.venv/bin/python -m pytest tests/test_servicios_r5.py -k "resultados or escapado or vacias or desconocido or lista_fija"`
  - Nota: para ver fallar las pruebas por `NotImplementedError` (y no por `ImportError`) se dejó primero `ARCHIVOS_RESULTADOS = {}` en el stub; `test_lista_fija_existe_en_results` pasaba en vacío hasta llenar la tabla y ahora comprueba los 15 archivos contra `results/` real.
  - anotar en `docs/anexo-ia.md`

- [x] T11 · Servicios con la red real (casos 1, 4, 5, 6 y 7; `red`)
  - Archivos: `tests/test_red_real_r5.py` (`pytestmark = pytest.mark.red`; fixture `datos_reales` con `scope="module"` que hace `pytest.skip` si falta `data/processed/grafo_componente.graphml[.gz]` y llama a `cargar_datos()` una vez)
  - Test primero (verifican código ya hecho: se validan con mutación temporal, ver Verificar): `::test_caso_1_ruta_real` (C01→C12: `tiempo_s == M["C01"]["C12"]` ± 1e-6 y ≈ 1 783,39; `ids_nodos[0] == nodo_de["C01"]`, `ids_nodos[-1] == nodo_de["C12"]`; `detalle_ruta(G, ids_nodos)[0]` igual ± 1e-6; `coordenadas[0]` a menos de 1e-6° de `(G.nodes[n]["y"], G.nodes[n]["x"])` del nodo de C01; `nodos_explorados > 0`), `::test_caso_1_asimetria` (C12→C01 ≈ 1 708,19 ± 0,01 y = matriz ± 1e-6), `::test_caso_3_mismo_lugar_real` (C01→C01 → 0 y aviso), `::test_caso_4_mismo_nodo` (T03→T05 → `tiempo_s == 0` y aviso del mismo punto), `::test_caso_5_itinerario_cabe` (C01 + `A05, A14, A06, A07, A13, A15`: HK 178,66 ± 0,01 min y recorrido `C01, A15, A13, A07, A06, A14, A05, C01`; voraz 190,45 ± 0,01 y `C01, A05, A14, A07, A06, A13, A15, C01`; diferencia 11,79 ± 0,01; brecha 6,60 ± 0,01; visitas 240; jornadas 418,66 y 430,45 ± 0,01, las dos caben; `jornada is None`), `::test_caso_6_itinerario_no_cabe` (C01 + `A05, A08, A04, A14, A06, A07, A12, A01`: HK 145,22 ± 0,01, jornada 1 255,22 ± 0,01, no cabe; voraz 155,39 ± 0,01; diferencia 10,17; brecha 7,01; `[q["id"] for q in jornada["quitados"]] == ["A01", "A12"]`; `jornada_final_min` = `totales.jornada_min` de `results/r4/r4_itinerario.json` ± 1e-6 y ≈ 613,13), `::test_caso_7_tramos` (caso 5, los dos métodos: cada tramo `tiempo_min * 60 == M[desde][hasta]` ± 1e-6; suma = desplazamiento ± 1e-6 × 60)
  - Verificar: `.venv/bin/python -m pytest tests/test_red_real_r5.py -k "caso_1 or caso_3 or caso_4 or caso_5 or caso_6 or caso_7"`; mutaciones temporales que deben hacer fallar y luego se restauran: invertir origen y destino en `ruta_entre` (caso 1), usar el recorrido del voraz en los dos métodos (caso 5)
  - Nota: mutaciones vistas fallar y restauradas: origen/destino invertidos en `ruta_entre` (fallan `test_caso_1_ruta_real` y `test_caso_1_asimetria`) y recorrido del voraz usado para Held-Karp (fallan casos 5 y 6).
  - Cierre de B2: `.venv/bin/python -m pytest -m "not red" -q` y `.venv/bin/python -m pytest tests/test_red_real_r5.py` en verde. **DETENERSE** hasta el commit del usuario
  - anotar en `docs/anexo-ia.md`

## B3 · Mapas, aplicación Flask y plantillas (cliente de pruebas de Flask)

- [x] T12 · Mapas con Folium (apoyan los casos 2, 9 y 10)
  - Archivos: `rutas/r5/mapas.py` (`COLORES`, `centro`, `mapa_ruta`, `mapa_envolvente`, `mapa_itinerario` según el plan; cada una devuelve `mapa.get_root().render()`)
  - Test primero: `tests/test_mapas_r5.py::test_mapa_ruta` (ruta C01→A02 sintética: el texto contiene `leaflet`, `L.polyline` y la coordenada intermedia `4.505`), `::test_mapa_ruta_sin_linea` (C01→C01: contiene `leaflet` y no `L.polyline`), `::test_mapa_envolvente` (contiene `L.polygon`, las 4 latitudes/longitudes del cuadrado (`-75.71`, `-75.65`, `4.49`, `4.53`) y 8 marcadores: el texto `C01 ·` … `A06 ·` en los tooltips), `::test_mapa_itinerario` (contiene `Held-Karp`, `Vecino más cercano`, `L.control.layers`, los dos colores de `COLORES` y los números de orden `1` … `6` en los `DivIcon`)
  - Ver fallar: con `NotImplementedError` del stub
  - Verificar: `.venv/bin/python -m pytest tests/test_mapas_r5.py`
  - Nota: Folium escapa en el HTML los textos de las capas (`Vecino m\u00e1s cercano`) y el HTML de los `DivIcon` (`\u003e1\u003c/div`); la prueba busca esas formas. Mutación vista fallar: sin `LayerControl` falla `test_mapa_itinerario`. Las pruebas y el código de mapas se escribieron juntos (no se vio el rojo con `NotImplementedError` en T12).
  - anotar en `docs/anexo-ia.md`

- [x] T13 · Fábrica `crear_app`, `base.html` e inicio (Comportamiento 6)
  - Archivos: `rutas/r5/app.py` (`crear_app(datos, results=RESULTS)`: filtro `num`, `app.config["DATOS"]`, `app.config["RESULTS"]`, ruta `/`); `rutas/r5/templates/base.html` (menú: Inicio, Ruta, Envolvente, Itinerario, Resultados r1..r4; `<style>` en línea; `lang="es"`), `inicio.html`
  - Test primero: `tests/test_app_r5.py::test_inicio_y_menu` (`GET /` → 200; contiene enlaces a `/ruta`, `/envolvente`, `/itinerario` y `/resultados/r1`; sin `<script` en el HTML propio fuera de los mapas)
  - Verificar: `.venv/bin/python -m pytest tests/test_app_r5.py -k "inicio or algoritmos"`
  - anotar en `docs/anexo-ia.md`

- [x] T14 · `/ruta` (caso 3; bordes: id desconocido e incompleto)
  - Archivos: `rutas/r5/app.py` (vista `/ruta`); `rutas/r5/templates/ruta.html` (formulario con dos `<select>` de los lugares «id · nombre», conservando lo elegido; resultado: tiempo en min y s, distancia, origen y destino, nodos explorados, cómputo en ms («informativo»), aviso y `<iframe srcdoc="{{ mapa }}">`)
  - Test primero: `tests/test_app_r5.py::test_ruta_formulario` (`GET /ruta` → 200 con `<select` y las 8 opciones), `::test_ruta_sintetica_app` (`GET /ruta?origen=C01&destino=A02` → 200; contiene el tiempo formateado con `numero(M["C01"]["A02"] / 60, 1)`, `leaflet` y el nombre de A02), `::test_caso_3_ruta_mismo_lugar` (`?origen=C01&destino=C01` → 200, «0,0» y «origen y destino son el mismo lugar»), `::test_ruta_lugar_desconocido` (`?origen=X99&destino=C01` → 400 y «lugar desconocido: X99»), `::test_ruta_incompleta` (`?origen=C01` → 200, sin «Tiempo de viaje» y sin mensaje de error)
  - Verificar: `.venv/bin/python -m pytest tests/test_app_r5.py -k ruta`
  - Nota: `test_ruta_sintetica_app` y `test_itinerario_sintetico_app` usan un helper `_cliente(tmp_path)` en vez de pedir `cliente_app` y `datos_app` juntos, porque ambos fixtures escriben la carpeta sintética en el mismo `tmp_path` (`FileExistsError`).
  - anotar en `docs/anexo-ia.md`

- [x] T15 · `/envolvente` (caso 10 con datos sintéticos)
  - Archivos: `rutas/r5/app.py` (vista `/envolvente`); `rutas/r5/templates/envolvente.html` («N vértices», «Área: X km²», tabla de vértices (lat, lon) con 6 decimales, mapa)
  - Test primero: `tests/test_app_r5.py::test_caso_10_envolvente` (`GET /envolvente` → 200; contiene «4 vértices», «29,6 km²», las 4 coordenadas de la tabla (`numero(4.49, 6)`, `numero(-75.71, 6)`, `numero(4.53, 6)`, `numero(-75.65, 6)`) y `leaflet`)
  - Verificar: `.venv/bin/python -m pytest tests/test_app_r5.py -k envolvente`
  - anotar en `docs/anexo-ia.md`

- [x] T16 · `/itinerario` (casos 8 y 14; bordes del itinerario)
  - Archivos: `rutas/r5/app.py` (vista `/itinerario`); `rutas/r5/templates/itinerario.html` (formulario: `<select name="partida">` con los lugares, C01 por defecto; casillas `name="atractivos"` de `datos.atractivos` con nombre y visita; resultado: tabla con una columna por método y las filas del plan, diferencia y brecha, bloque «Regla de las 11 h (R4, informativo)» si `jornada`, y el mapa)
  - Test primero: `tests/test_app_r5.py::test_itinerario_sin_parametros` (`GET /itinerario` → 200, formulario con 6 casillas y C01 `selected`), `::test_itinerario_sintetico_app` (C01 + A01..A06 → 200; contiene `numero(hk_min, 1)`, `numero(voraz_min, 1)`, `numero(diferencia, 1)`, los nombres en orden de HK, «Held-Karp», «Vecino más cercano» y `leaflet`), `::test_itinerario_bloque_regla` (parametrizada: visitas por defecto → sin «Regla de las 11 h»; carpeta con `visitas=[120] * 6` → con «Regla de las 11 h» y el nombre del primer quitado), `::test_caso_8_itinerario_400` (parametrizada con las mismas 7 entradas de T8 → 400, el mensaje en el HTML, las casillas que llegaron siguen marcadas, y un contador en `rutas.r5.servicios.resolver_por_ids` (monkeypatch) en 0), `::test_caso_14_carga_unica` (monkeypatch con contador de `rutas.r5.app.cargar_datos` y de `rutas.r5.datos.cargar_grafo_procesado` **después** de crear la app; 3 peticiones a `/ruta?origen=C01&destino=A02` y 3 a `/itinerario?partida=C01&atractivos=…` → 200 y los dos contadores en 0)
  - Verificar: `.venv/bin/python -m pytest tests/test_app_r5.py -k "itinerario or caso_8 or caso_14"`
  - Nota: en `test_caso_8_itinerario_400` la entrada de 9 atractivos usa `C02, C03, C04` extra (los datos sintéticos solo tienen 6 atractivos). Mutación vista fallar: quitar el control de la lista blanca hizo fallar el rechazo de `r2_cociente.csv` (T17).
  - anotar en `docs/anexo-ia.md`

- [x] T17 · `/resultados/<r>` y `/resultados/<r>/archivo/<nombre>` (casos 11 y 12)
  - Archivos: `rutas/r5/app.py` (las dos vistas del plan; `abort(404)` fuera de la lista; `send_from_directory` solo para imágenes de la lista); `rutas/r5/templates/resultados.html` (un `<h2>` por archivo, `<img src="{{ url_for(...) }}">`, tablas con `|safe`, lista «Faltan» con `archivo: comando`)
  - Test primero: `tests/test_app_r5.py::test_caso_11_resultados_r2` (cliente con `results` sintético: `GET /resultados/r2` → 200, contiene `r2_tiempo_vs_explorados.png` en un `src` y la tabla de `r2_cociente.csv`), `::test_caso_11_r4_sin_exactas` (`GET /resultados/r4` → 200, contiene `r4_exactas.csv` y `python -m rutas.r4.medir_exactas`), `::test_caso_11_cuatro_paginas_reales` (cliente con `results=RESULTS` real, sin `red`: `/resultados/r1` … `/resultados/r4` → 200; r2 y r3 sin «Faltan»), `::test_caso_12_imagen_permitida` (`/resultados/r2/archivo/r2_tiempo_vs_explorados.png` → 200 y `mimetype == "image/png"`), `::test_caso_12_rechazos` (parametrizada: `/resultados/r2/archivo/..%2F..%2FCLAUDE.md`, `/resultados/r2/archivo/otro.png`, `/resultados/r2/archivo/r2_cociente.csv`, `/resultados/r9`, `/resultados/r9/archivo/x.png` → 404)
  - Verificar: `.venv/bin/python -m pytest tests/test_app_r5.py -k "caso_11 or caso_12"`
  - anotar en `docs/anexo-ia.md`

- [x] T18 · `main`: carga única, datos faltantes y puerto ocupado (caso 13; Comportamiento 1; borde del puerto)
  - Archivos: `rutas/r5/app.py` (`puerto_libre`, `main` según el plan, con `--puerto` y `--host`; bloque `if __name__ == "__main__": sys.exit(main())`)
  - Test primero: `tests/test_app_r5.py::test_caso_13_main_sin_datos` (`main([], processed=tmp_path_vacio)` → `1`; `capsys` contiene `grafo_componente.graphml` y `python -m rutas.r1.construir_red`, y **no** contiene `Traceback`), `::test_puerto_ocupado` (socket abierto en `127.0.0.1:0`; `main(["--puerto", str(p)], processed=…, catalogo=…)` con la carpeta sintética → `1` y la salida contiene `--puerto`; `Flask.run` reemplazado por un falso que falla si se llama), `::test_main_arranca` (monkeypatch de `flask.Flask.run` que guarda sus argumentos; `main(["--puerto", "5099"], …)` → `0`; se llamó una vez con `host="127.0.0.1"`, `port=5099`, `debug=False`; la salida contiene «Datos cargados en» y `http://127.0.0.1:5099`), `::test_puerto_por_defecto` (sin `--puerto` → `port=5050`)
  - Verificar: `.venv/bin/python -m pytest tests/test_app_r5.py -k "main or puerto"`
  - anotar en `docs/anexo-ia.md`

- [x] T19 · La app con la red real (casos 2, 3, 9 y 10; `red`)
  - Archivos: `tests/test_red_real_r5.py` (agregar un fixture `cliente_real` de módulo con `crear_app(datos_reales).test_client()`)
  - Test primero (código ya hecho: validar con mutación temporal): `::test_caso_2_ruta_en_la_app` (`GET /ruta?origen=C01&destino=C12` → 200, contiene «29,7» y `leaflet`), `::test_caso_3_ruta_mismo_lugar_real` (`?origen=C01&destino=C01` → 200, «origen y destino son el mismo lugar»), `::test_caso_9_itinerario_en_la_app` (`/itinerario?partida=C01&atractivos=A05&atractivos=A14&atractivos=A06&atractivos=A07&atractivos=A13&atractivos=A15` → 200; contiene «178,7», «190,4» y «11,8»; no contiene «Regla de las 11 h»), `::test_itinerario_no_cabe_en_la_app` (los 8 del caso 6 → 200 y contiene «Regla de las 11 h», «Parque Nacional del Café» y «613,1»), `::test_caso_10_envolvente_real` (`/envolvente` → 200, «14 vértices» y «1 631,5»), `::test_formulario_42_lugares_15_atractivos` (`/itinerario` → 42 `<option` en la partida y 15 casillas)
  - Verificar: `.venv/bin/python -m pytest tests/test_red_real_r5.py`; mutación temporal: mostrar el desplazamiento con `numero(x, 2)` hace fallar el caso 9; restaurar
  - Cierre de B3: `.venv/bin/python -m pytest -m "not red" -q` y `.venv/bin/python -m pytest tests/test_red_real_r5.py` en verde. **DETENERSE** hasta el commit del usuario
  - anotar en `docs/anexo-ia.md`

## B4 · Docker, README, anexo de IA, comprobación manual y cierre

- [x] T20 · `Dockerfile` opcional (Comportamiento 7; apoya el caso 17)
  - Archivos: `Dockerfile` (en la raíz):
    ```dockerfile
    FROM python:3.13-slim
    WORKDIR /app
    COPY requirements.txt .
    RUN pip install --no-cache-dir -r requirements.txt
    COPY rutas/ rutas/
    COPY data/catalogo.csv data/catalogo.csv
    COPY data/processed/ data/processed/
    COPY results/ results/
    EXPOSE 5050
    CMD ["python", "-m", "rutas.r5.app", "--host", "0.0.0.0", "--puerto", "5050"]
    ```
  - Test primero: `tests/test_dockerfile_r5.py::test_dockerfile` (lee el texto: empieza con `FROM python:3.13-slim`; contiene `pip install` con `requirements.txt`, `COPY data/processed`, `COPY results`, `COPY rutas`, `0.0.0.0`, `5050` y `rutas.r5.app`; no copia `data/raw`, `.venv` ni `estudio`). Falla porque el archivo no existe
  - Verificar: `.venv/bin/python -m pytest tests/test_dockerfile_r5.py`
  - anotar en `docs/anexo-ia.md`
  - Nota: el Dockerfile lleva un comentario después de `FROM` (la prueba exige que el texto empiece por `FROM python:3.13-slim`). Se probó `tests/test_dockerfile_r5.py` (rojo por archivo inexistente, luego verde). `docker build -t rutas-quindio .` OK (unos 10 min por osmnx/geopandas/scipy; imagen de 1,02 GB). `docker run -d -p 5055:5050`: `/` y `/ruta?origen=C01&destino=C12` responden 200 (con «29,7»); contenedor detenido y borrado. Caso 17 solo con curl; el navegador queda pendiente del usuario. Sin `.dockerignore` (el Dockerfile copia solo `rutas/`, `data/catalogo.csv`, `data/processed/` y `results/`).

- [x] T21 · README: «Ejecutar la aplicación (R5)» (enunciado: ejecutable localmente siguiendo el README; caso 16)
  - Archivos: `README.md` (sección nueva al final, después de «Reproducir R3» —o de «Reproducir R4» si ya existe—, sin tocar las demás): requisito (`data/processed/` y `data/catalogo.csv` versionados; no hace falta correr R1–R4 para abrir la app); entorno (`python3.13 -m venv .venv` y `.venv/bin/pip install -r requirements.txt`, igual que R1); arranque `.venv/bin/python -m rutas.r5.app` y abrir `http://127.0.0.1:5050`; opción `--puerto` (por qué no 5000 en macOS); qué muestra cada sección; nota: el mapa necesita internet (Leaflet y teselas de OpenStreetMap); los avisos de archivos faltantes y sus comandos; alternativa Docker (`docker build -t rutas-quindio .` y `docker run -p 5050:5050 rutas-quindio`), opcional; pruebas `pytest -m "not red"` y `pytest tests/test_red_real_r5.py`
  - Test primero: no aplica (documentación)
  - Verificar: `grep -n "rutas.r5.app" README.md && grep -n "127.0.0.1:5050" README.md && grep -n "docker run -p 5050:5050" README.md`
  - anotar en `docs/anexo-ia.md`
  - Nota: sección «Ejecutar la aplicación (R5)» agregada al final de `README.md`; no se escribió «Reproducir R4» (es la T23 de R4). Incluye la nota de Python 3.13.18 (R4 y R5) frente a 3.13.8 (R1 a R3) y la de los archivos que pueden faltar (R1 `.png`, R4 `r4_exactas.csv` y `r4_tiempo_vs_k.png`). Los tres `grep` de verificación dan resultado.

- [x] T22 · Anexo de IA de R5
  - Archivos: `docs/anexo-ia.md` (local; entradas de R5: plan y tareas con el agente planner; código, plantillas y pruebas con el implementer; cómo se verificó: casos 1, 5, 6 y 7 contra la matriz de R2 y `r4_itinerario.json`; datos sintéticos con valores a mano (casos 3, 8, 10–15); guardias sin algoritmos ni JS propio; mutaciones temporales; comprobación manual de los casos 16 y 17)
  - Test primero: no aplica (documentación)
  - Verificar: `grep -n "R5" docs/anexo-ia.md`

- [x] T23 · Comprobación manual: arranque con el README y Docker (casos 16 y 17)
  - Archivos: ninguno de código; el resultado lo escribe el reviewer o el usuario en `specs/r5-aplicacion/review.md`
  - Test primero: no aplica (manual)
  - Lista de pasos (caso 16, obligatorio):
    1. Abrir una terminal **nueva** en la raíz del repositorio y seguir **solo** el README, sección «Ejecutar la aplicación (R5)» (si `.venv` ya existe, basta `.venv/bin/pip install -r requirements.txt`, que no debe cambiar nada).
    2. `.venv/bin/python -m rutas.r5.app` → imprime «Datos cargados en …» (≈ 1–2 s) y la dirección; no hay traza.
    3. Abrir `http://127.0.0.1:5050`: el inicio muestra los 4 enlaces.
    4. Caso 2: Ruta, origen C01 y destino C12 → mapa con la línea por las vías y «29,7» min; probar también C12 → C01 (28,5 min) y C01 → C01 (aviso).
    5. Caso 9: Itinerario, partida C01 y las casillas A05, A14, A06, A07, A13, A15 → tabla con «178,7», «190,4» y «11,8»; el control de capas alterna Held-Karp y voraz. Probar los 8 del caso 6 → bloque de la regla (quita A01 y A12; 613,1 min). Probar 5 casillas → mensaje de error.
    6. Caso 10: Envolvente → polígono con los lugares como marcadores en el mapa, «14 vértices» y «1 631,5 km²» (el texto no cuenta los lugares; la spec no lo pide).
    7. Caso 11: Resultados r1..r4 → imágenes y tablas; r1 y r4 muestran el aviso de lo que falta con su comando.
    8. Con la app abierta, en otra terminal `.venv/bin/python -m rutas.r5.app` → mensaje de puerto ocupado que sugiere `--puerto`; luego `--puerto 5051` arranca.
    9. Ctrl+C detiene la app.
  - Lista de pasos (caso 17, opcional; si Docker no está, se anota «no comprobado» y no bloquea):
    1. `docker build -t rutas-quindio .`
    2. `docker run --rm -p 5050:5050 rutas-quindio`
    3. Abrir `http://127.0.0.1:5050` y repetir los pasos 4 y 6.
  - Verificar: `review.md` registra fecha, quién lo hizo, navegador y el resultado de cada paso
  - Resultado automatizado del caso 16 (2026-11-12, implementer, con `curl` y el `.venv` existente, puerto 5061; el navegador no se usó). Para copiar a `review.md`:
    1. [OK] `.venv/bin/pip install -r requirements.txt`: no instaló nada (ya estaba todo).
    2. [OK] `.venv/bin/python -m rutas.r5.app --puerto 5061`: «Datos cargados en 0,4 s (8 791 nodos)» y «Abre http://127.0.0.1:5061», sin traza. Se usó 5061 y no 5050 para no chocar con nada del usuario; el arranque en 5050 está probado en B3.
    3. [OK] `/` 200 con los 4 enlaces (`/ruta`, `/itinerario`, `/envolvente`, resultados). [pendiente del usuario: verlo en el navegador]
    4. [OK] Caso 2: C01 -> C12 200 con «29,7» y la polilínea; C12 -> C01 200 con «28,5»; C01 -> C01 200 con el aviso «origen y destino son el mismo lugar». [pendiente del usuario: que la línea siga las vías y el mapa se vea bien]
    5. [OK] Caso 9: partida C01 con A05, A14, A06, A07, A13, A15 -> 200 con «178,7», «190,4» y «11,8» y el control de capas en el HTML; con los 8 del caso 6 -> 200 con «145,2», «155,4», «613,1» y el bloque de la regla de las 11 h; con 5 atractivos -> 400 «elige entre 6 y 8 atractivos (llegaron 5)». [pendiente del usuario: que el control de capas alterne Held-Karp y voraz en el navegador]
    6. [OK, con una diferencia] Caso 10: `/envolvente` 200 con «14 vértices» y «1 631,5» (km²) y el mapa en un iframe. La página **no** dice «42 lugares» (la spec del caso 10 tampoco lo exige; solo pide vértices y área): el paso 6 de esta lista lo supone y habría que quitar esa expresión. [pendiente del usuario: ver el polígono]
    7. [OK] Caso 11: `/resultados/r1..r4` 200. r2: 1 imagen y 3 tablas; r3: 1 imagen y 1 tabla; r1: 4 tablas y aviso de `r1_tiempos_componente.png` con `.venv/bin/python -m rutas.r1.tablas`; r4: 3 tablas y avisos de `r4_tiempo_vs_k.png` (`rutas.r4.tablas`) y `r4_exactas.csv` (`rutas.r4.medir_exactas`). `/resultados/r2/archivo/r2_tiempo_vs_explorados.png` 200. [pendiente del usuario: ver imágenes y tablas]
    8. [OK] Con la app corriendo, un segundo arranque en el mismo puerto imprime «el puerto 5061 está ocupado; prueba con --puerto 5062» y sale sin traza. No se probó `--puerto 5062` a mano (cubierto por pruebas de B3).
    9. [OK] Detenida con Ctrl+C (SIGINT) y con `kill`; sin proceso restante. Nota: la primera vez un servidor lanzado en segundo plano no recibió el SIGINT del shell y hubo que matarlo por PID; no es fallo de la app.
  - Caso 17 (Docker): ver la nota de T20. [OK] build, run y curl; [pendiente del usuario] abrir en navegador y repetir los pasos 4 y 6.
  - Pendiente del usuario: todo lo que exige ver el navegador (mapas, capas, imágenes) y la ejecución en una terminal realmente nueva.

- [x] T24 · Suite completa y cierre de R5
  - Archivos: ninguno nuevo (R5 no genera resultados: no hay archivos que regenerar)
  - Test primero: no aplica
  - Comando:
    ```bash
    cd /Users/nicolascastro/Desktop/proyecto-final-rutas-quindio && .venv/bin/python -m pytest && git diff --stat -- rutas/r1 rutas/r2 rutas/r3 rutas/r4 requirements.txt .gitignore
    ```
  - Verificar: todas las pruebas pasan (las `red` de R5 sin saltar, porque `data/processed/` existe); el `git diff --stat` de R1–R4, `requirements.txt` y `.gitignore` está vacío; actualizar el «Estado» de la spec (☑ pruebas · ☑ código; «verificado» lo marca el reviewer tras T23); anotar como pendientes del documento técnico: diagrama de arquitectura (sección 7.1), capturas de las cuatro secciones y el comando de arranque
  - anotar en `docs/anexo-ia.md`
  - Resultado (2026-11-12): `-m "not red"`: 497 pasan, 1 se salta, 41 deseleccionadas (suma la prueba del Dockerfile). `-m red`: 39 pasan, 2 se saltan (`test_red_real.py:79` por `data/raw/radio_2km.graphml` y `test_red_real_r4.py:126` por `results/r4/r4_exactas.csv`; ninguno es de R5, las `red` de R5 corren). Suite completa `pytest`: 536 pasan, 3 se saltan. `git diff --stat -- rutas/r1 rutas/r2 rutas/r3 rutas/r4 requirements.txt .gitignore`: vacío.
  - Pendiente: el «Estado» de la spec y la lista de pendientes del documento técnico (diagrama de arquitectura, capturas de las cuatro secciones y comando de arranque) no se tocaron: la spec es del coordinator/reviewer.

## Ronda 1, sugerencias del reviewer

- [x] Sugerencia 1: nombres de origen y destino en el resultado de `/ruta`
  - Nota: la plantilla `ruta.html` envuelve el resultado en `<div id="resultado-ruta">` y muestra «C01 Nombre → A02 Nombre»; `app.py` pasa `nombre_de` al contexto. Las pruebas (`test_app_r5.py`, `test_red_real_r5.py`) buscan el texto solo dentro de ese bloque; con la plantilla sin nombres la prueba sintética falló (`'C01 Cabecera Uno → A02 Atractivo Dos'` no estaba en el resultado, solo `C01 → A02`).
- [x] Sugerencia 3: README, sección «Ejecutar la aplicación (R5)»: «de 6 a 8 atractivos», partida por defecto Armenia (C01) y requisito de `python3.13` instalado antes de crear `.venv`.

## B5 · Ajuste visual (spec «Ajuste visual», V0–V10 y A1–A11; plan «Ajuste visual»)

> **Reglas propias de B5** (además de las reglas del usuario de arriba):
> 1. **No se toca** `rutas/r1..r4/`, `rutas/r5/servicios.py`, `rutas/r5/datos.py`, `rutas/r5/formato.py`, `requirements.txt`, `.gitignore` ni el `Dockerfile`. En `rutas/r5/mapas.py` solo cambia `COLORES`.
> 2. **Sin JavaScript propio** (ni `<script`, ni `javascript:`, en plantillas ni en `estilos.css`) y **sin dependencias nuevas** (ni fuentes externas, ni `@import`, ni `url(http`).
> 3. **Las pruebas actuales no se modifican.** Si una falla, se corrige la plantilla. Los fragmentos de los que dependen están en `plan.md`, «Pruebas actuales que dependen del HTML»; los más frágiles: el `<h2>` de `#resultado-ruta` en texto plano y en una línea; `value="…" checked` seguidos; «N vértices» y «X km²» en un mismo texto; «Regla de las 11 h» y «Faltan» solo en sus bloques condicionales; el nombre del archivo sigue visible en resultados.
> 4. Las pruebas nuevas van en `tests/test_visual_r5.py` (sin marca `red`; usan `cliente_app`, `datos_app` o el helper `_cliente(tmp_path, …)` de `tests/test_app_r5.py`, que se importa o se copia). Cada una se ve fallar contra el HTML actual antes de cambiar la plantilla.
> 5. Regresión de cada tarea (además de su prueba): `.venv/bin/python -m pytest tests/test_app_r5.py tests/test_mapas_r5.py -q`; y cuando la tarea toca ruta, envolvente o itinerario, también `.venv/bin/python -m pytest tests/test_red_real_r5.py -q` (contiene «29,7», «178,7», «190,4», «11,8», «14 vértices» y «1 631,5»).

- [x] T25 · Línea base y guardia sin JavaScript propio (A9; restricciones)
  - Archivos: `tests/test_visual_r5.py` (crear)
  - Pasos: correr la suite y anotar la línea base (esperado, según T24: `-m "not red"` 497 pasan y 1 se salta; suite completa 536 pasan y 3 se saltan); comprobar que el árbol de lo prohibido está limpio con `git status --short -- rutas/r1 rutas/r2 rutas/r3 rutas/r4 rutas/r5/servicios.py requirements.txt .gitignore Dockerfile` (vacío)
  - Test primero: `tests/test_visual_r5.py::test_a9_sin_js_propio` (recorre las 6 plantillas de `rutas/r5/templates/` y `rutas/r5/static/*.css`; ninguna contiene `<script` ni `javascript:` (en minúsculas); exige que existan las 6 plantillas y `rutas/r5/static/estilos.css`). Rojo esperado: falta `estilos.css`. La guardia actual `tests/test_app_r5.py::test_sin_algoritmos_ni_js_propio` no se cambia
  - Verificar: `.venv/bin/python -m pytest -q` (línea base) y `.venv/bin/python -m pytest tests/test_visual_r5.py -k a9` (rojo por la razón correcta; pasa a verde en T26)
  - anotar en `docs/anexo-ia.md`
  - Nota: línea base 2026-11-12 (antes de cambiar nada): suite completa 535 pasan, 3 se saltan y 1 falla: `test_puerto_por_defecto`, porque un proceso ajeno (`python -m rutas.r5.app`, PID 71719) ya escucha en el puerto 5050; no es un fallo del código. `git status` de lo prohibido: vacío. `test_a9_sin_js_propio` rojo por `falta estilos.css`.

- [x] T26 · Paleta: `COLORES` de `mapas.py` y variables de `estilos.css` (V0 paleta, V1, A11; deja A9 en verde)
  - Archivos: `rutas/r5/mapas.py` (solo `COLORES = {"ruta": "#1F5F8B", "held_karp": "#1F5F8B", "voraz": "#B8322A", "envolvente": "#5E8C61"}`); `rutas/r5/static/estilos.css` (crear con los 15 encabezados de sección del plan; llenar la sección 1 «Paleta y escala»: las 7 variables de color, `--fuente-titulos`, `--fuente-texto`, `--fuente-ids` y los 4 tamaños)
  - Test primero: `::test_a11_paleta_en_css` (regex `--guadua:\s*#2F4A3A`, `--hoja:\s*#5E8C61`, `--niebla:\s*#F3F6F4`, `--bahareque:\s*#D5DDD7`, `--tinta:\s*#1D2521`, `--cocora:\s*#1F5F8B`, `--cereza:\s*#B8322A`, sin distinguir mayúsculas), `::test_a11_sin_transition_all_ni_externos` (no `transition\s*:\s*all`, no `@import`, no `url(http`), `::test_a11_colores_de_mapas` (`COLORES["ruta"]` y `COLORES["held_karp"]` = valor de `--cocora`, `COLORES["voraz"]` = `--cereza`, `COLORES["envolvente"]` = `--hoja`, leídos del CSS y comparados en minúsculas). Rojo: falta el archivo y `COLORES` aún vale `#1f77b4`/`#ff7f0e`
  - Verificar: `.venv/bin/python -m pytest tests/test_visual_r5.py -k "a9 or a11" && .venv/bin/python -m pytest tests/test_mapas_r5.py tests/test_app_r5.py -q`
  - anotar en `docs/anexo-ia.md`
  - Nota: `estilos.css` se creó con las 15 secciones y se fue llenando por tarea (T26 la 1; T27 las 2 a 6, 14 y 15; T28 la 7 y 8; T29 la 9 y 10; T30 la 11; T32 la 12; T33 la 13).

- [x] T27 · `base.html`: hoja enlazada, viewport, saltar al contenido, cabecera con curvas de nivel y menú con `aria-current` (V0 tipos/firma/movimiento, V1, V2, A1, A2, A3)
  - Archivos: `rutas/r5/templates/base.html` (como en el plan, «Sección activa»: sin `<style>`; `<meta name="viewport" content="width=device-width, initial-scale=1">`; `<link rel="stylesheet" href="{{ url_for('static', filename='estilos.css') }}">`; `.saltar`; `.cabecera` con la marca y el menú de 4 enlaces; `<main id="contenido">`); `rutas/r5/app.py` (pasar `seccion` en las 5 vistas que renderizan plantilla: en `/ruta` y `/itinerario` dentro de `contexto`, para que también lo lleven las respuestas 400); `rutas/r5/static/estilos.css` (secciones 2 Base, 3 Foco visible, 4 Saltar al contenido, 5 Cabecera y menú, 6 Contenido, 14 Movimiento, 15 Pantallas angostas)
  - Test primero: `::test_a1_estilos_servidos` (`GET /static/estilos.css` → 200 y `mimetype == "text/css"`), `::test_a1_base_sin_style` (el texto de `base.html` no contiene `<style` y contiene `estilos.css`), `::test_a2_viewport_y_saltar` (parametrizada con `/`, `/ruta`, `/ruta?origen=C01&destino=A02`, `/ruta?origen=X99&destino=C01` (400), `/envolvente`, `/itinerario`, `/itinerario?` + 6 atractivos, `/itinerario?partida=C01` (400), `/resultados/r1` … `/resultados/r4`: contiene `name="viewport"`, «Saltar al contenido», `href="#contenido"` e `id="contenido"`), `::test_a3_aria_current` (parametrizada `(url, texto_del_enlace)`: `/ruta`→«Ruta», `/envolvente`→«Envolvente», `/itinerario`→«Itinerario», `/resultados/r2`→«Resultados»: `html.count('aria-current="page"') == 1` y regex `aria-current="page"[^>]*>{texto}<`), `::test_v0_tipos_firma_y_movimiento` (el CSS contiene `"Iowan Old Style"`, `system-ui`, `ui-monospace`, `repeating-radial-gradient`, `:focus-visible`, `scale(0.97)`, `160ms ease-out`, `(hover: hover) and (pointer: fine)`, `prefers-reduced-motion: reduce`, `flex-wrap`). `test_a3` en `/resultados/r2` queda en verde solo cuando la vista pase `seccion` (aquí) y la navegación de R1–R4 use `aria-current="true"` (T32 lo mantiene)
  - Verificar: `.venv/bin/python -m pytest tests/test_visual_r5.py -k "a1 or a2 or a3 or v0" && .venv/bin/python -m pytest tests/test_app_r5.py tests/test_mapas_r5.py -q` (en especial `test_inicio_y_menu`)
  - anotar en `docs/anexo-ia.md`
  - Nota: `seccion` se pasa en las 5 vistas (en `/ruta` y `/itinerario` dentro de `contexto`, así las respuestas 400 también lo llevan).
  - Nota (ronda 2, sugerencia 8): en la sección 14 Movimiento, `.menu a:hover` usa Bahareque y `button:hover` Cocora (`estilos.css:133-134`), no Niebla y Guadua como decía el plan: Niebla casi no se distingue del blanco del menú y el botón ya es Guadua. `plan.md` quedó actualizado con los colores reales y el motivo.

- [x] T28 · Formularios y mensajes de Ruta e Itinerario (V3, V6, A4, A6)
  - Archivos: `rutas/r5/templates/ruta.html` y `itinerario.html` (solo el formulario y los mensajes: `<label for>` + `id` en cada `<select>`; `<fieldset>`/`<legend>` «Atractivos (elige de 6 a 8)» con `<div class="casillas">`; casilla `<label class="casilla"><input type="checkbox" name="atractivos" value="{{ id }}"{% if id in elegidos %} checked{% endif %}> <span class="id">…</span> nombre <span class="visita">… min</span></label>`; botones «Calcular ruta» y «Calcular itinerario»; `<p class="error" role="alert">`; en `ruta.html` `<p class="aviso" role="status">`); `rutas/r5/static/estilos.css` (secciones 7 Formularios y 8 Mensajes)
  - Test primero: `::test_a4_labels_y_botones` (`/ruta`: `<label for="origen">`, `<label for="destino">`, `id="origen"`, `id="destino"`, `>Calcular ruta</button>`; `/itinerario`: `<label for="partida">`, `id="partida"`, `<fieldset`, `<legend>Atractivos (elige de 6 a 8)</legend>`, `>Calcular itinerario</button>`), `::test_v3_fieldset_y_cuadricula` (las 6 casillas `name="atractivos"` están entre `<fieldset` y `</fieldset>`, dentro de `class="casillas"`; cada casilla con `class="visita"`; el CSS tiene `grid-template-columns` en `.casillas`), `::test_a6_alert_y_status` (`/itinerario?partida=C01&atractivos=A01` → 400 y regex `role="alert"[^>]*>[^<]*entre 6 y 8`; `/ruta?origen=X99&destino=C01` → `role="alert"` con «lugar desconocido: X99»; `/ruta?origen=C01&destino=C01` → regex `role="status"[^>]*>origen y destino son el mismo lugar`; `/ruta?origen=C01&destino=A02` → sin `role="alert"`)
  - Verificar: `.venv/bin/python -m pytest tests/test_visual_r5.py -k "a4 or a6 or v3" && .venv/bin/python -m pytest tests/test_app_r5.py tests/test_mapas_r5.py -q && .venv/bin/python -m pytest tests/test_red_real_r5.py -q` (en especial `test_caso_8_itinerario_400`, `test_ruta_formulario`, `test_itinerario_sin_parametros`, `test_ruta_incompleta`, `test_formulario_42_lugares_15_atractivos`)
  - anotar en `docs/anexo-ia.md`
  - Nota: ninguna desviación; el `<h2>` y los `<option>` no cambiaron.

- [x] T29 · Ruta: tarjetas de resumen y mapa con título (V4, V7, A5 en `/ruta`)
  - Archivos: `rutas/r5/templates/ruta.html` (el resultado sigue dentro de `<div id="resultado-ruta">`; el `<h2>` queda en texto plano y en una línea; `<dl class="resumen">` con «Tiempo de viaje» (`… min` y `<small>(… s)</small>`), «Distancia» (`… km`) y «Nodos explorados»; cómputo en `<p class="nota">`; `<iframe class="mapa" title="Mapa de la ruta" srcdoc="{{ mapa }}">`); `rutas/r5/static/estilos.css` (secciones 9 Tarjetas de resumen y 10 Mapas y leyenda: `iframe.mapa` con `height: clamp(320px, 60vh, 560px)`; `tabular-nums` en `dl.resumen dd`)
  - Test primero: `::test_v4_tarjetas_ruta` (`/ruta?origen=C01&destino=A02` con `_cliente`: el bloque entre `<dl class="resumen"` y `</dl>` contiene «Tiempo de viaje», `numero(M.loc["C01","A02"] / 60, 1) + " min"`, «Distancia», «Nodos explorados»), `::test_a5_iframes_con_title` (parametrizada por página; aquí solo `("/ruta?origen=C01&destino=A02", "Mapa de la ruta")`: el número de `<iframe` es igual al de `<iframe[^>]*title="` y aparece `title="Mapa de la ruta"`; T30 y T31 agregan sus parámetros). Rojo: hoy no hay `<dl>` ni `title`
  - Verificar: `.venv/bin/python -m pytest tests/test_visual_r5.py -k "v4_tarjetas_ruta or a5" && .venv/bin/python -m pytest tests/test_app_r5.py -k ruta -q && .venv/bin/python -m pytest tests/test_red_real_r5.py -k "caso_2 or caso_3" -q` («29,7» y el texto de `#resultado-ruta`)
  - anotar en `docs/anexo-ia.md`
  - Nota: el `<h2>` de `#resultado-ruta` sigue en texto plano y en una línea.

- [x] T30 · Envolvente: tarjetas, tabla accesible y mapa con título (V4, V7, V8, A5 en `/envolvente`)
  - Archivos: `rutas/r5/templates/envolvente.html` (`<dl class="resumen">` con «Polígono» → `{{ n_vertices }} vértices` y «Área» → `{{ area_km2|num(1) }} km²`, cada uno en una sola línea; `<iframe class="mapa" title="Mapa de la envolvente">`; tabla con `<caption>Vértices de la envolvente (grados)</caption>`, `<thead>` con tres `<th scope="col">`, y en cada fila `<th scope="row">{{ loop.index }}</th>`); `rutas/r5/static/estilos.css` (sección 11 Tablas: caption, filas alternadas, `tabular-nums` en `td`, `.tabla-ancha { overflow-x: auto }`)
  - Test primero: `::test_v4_tarjetas_envolvente` (dentro de `<dl class="resumen"`: «4 vértices» y «29,6 km²»), `::test_v8_tabla_envolvente` (`<caption>`, `<thead>`, 3 `scope="col"`, 4 `scope="row"`, sin `<th></th>`), `::test_a5_iframes_con_title` (agrega `("/envolvente", "Mapa de la envolvente")`)
  - Verificar: `.venv/bin/python -m pytest tests/test_visual_r5.py -k "envolvente or a5" && .venv/bin/python -m pytest tests/test_app_r5.py -k envolvente -q && .venv/bin/python -m pytest tests/test_red_real_r5.py -k caso_10 -q` («14 vértices» y «1 631,5»)
  - anotar en `docs/anexo-ia.md`
  - Nota: el `<dd>` del área solo lleva `{{ area }} km²`; la etiqueta «Área» está en el `<dt>`.

- [x] T31 · Itinerario: resumen, leyenda con los colores del mapa, tabla y orden de la página (V4, V5, V7, A5, A7)
  - Archivos: `rutas/r5/app.py` (la vista de itinerario pasa `colores=COLORES` dentro de `contexto`; importar `COLORES` de `rutas.r5.mapas`); `rutas/r5/templates/itinerario.html` (orden: `<dl class="resumen">` (Held-Karp `metodo-hk`, voraz `metodo-voraz`, diferencia, brecha) → `<ul class="leyenda">` con `<span class="muestra" style="background: {{ colores.held_karp }}">` y `{{ colores.voraz }}` + `<iframe class="mapa" title="Mapa del itinerario">` → `<table class="comparacion">` con `<caption>Held-Karp frente al vecino más cercano</caption>`, `<thead>` «Medida» / «Held-Karp (óptimo)» (`class="metodo-hk"`) / «Vecino más cercano (voraz)» (`class="metodo-voraz"`) con `scope="col"` y filas con `<th scope="row">` → `<section class="regla">` si `it.jornada`, con su tabla con `<caption>`); `rutas/r5/static/estilos.css` (`.metodo-hk` y `.metodo-voraz` con `var(--cocora)` y `var(--cereza)`; `.leyenda`, `.muestra`)
  - Test primero: `::test_v4_tarjetas_itinerario` (con `_cliente`, C01 + A01..A06: dentro de `<dl class="resumen"`: `numero(hk, 1)`, `numero(voraz, 1)`, `numero(diferencia, 1)`, `numero(brecha, 2) + " %"`), `::test_a7_leyenda_con_colores` (el bloque entre `class="leyenda"` y `</ul>` contiene `COLORES["held_karp"]`, `COLORES["voraz"]`, «Held-Karp» y «Vecino más cercano»), `::test_v5_tabla_comparacion` (`<caption>Held-Karp frente al vecino más cercano</caption>`, `<th scope="col">Medida</th>`, 6 `scope="row"` en la tabla de comparación, sin `<th></th>`, encabezados con `metodo-hk` y `metodo-voraz`), `::test_v5_orden_de_la_pagina` (carpeta con `visitas=[120] * 6`: posición de `class="resumen"` < `class="leyenda"` < `<iframe` < `class="comparacion"` < `class="regla"`), `::test_a5_iframes_con_title` (agrega el itinerario, «Mapa del itinerario»). Rojo: hoy el mapa va al final y no hay leyenda
  - Verificar: `.venv/bin/python -m pytest tests/test_visual_r5.py -k "itinerario or a7 or v5 or a5" && .venv/bin/python -m pytest tests/test_app_r5.py -k "itinerario or caso_8 or caso_14" -q && .venv/bin/python -m pytest tests/test_mapas_r5.py -q && .venv/bin/python -m pytest tests/test_red_real_r5.py -k "caso_9 or no_cabe or formulario" -q` («178,7», «190,4», «11,8»; sin «Regla de las 11 h» cuando cabe)
  - anotar en `docs/anexo-ia.md`
  - Nota: `<dl class="resumen">` usa `<div class="tarjeta">` por cada par `dt`/`dd` (HTML válido). La tabla de la regla usa `<th scope="row">` para el lugar. En la tarjeta y en el encabezado de cada método el color sale de `.metodo-hk` / `.metodo-voraz` (CSS), y la leyenda usa `COLORES` con `style` en línea.

- [x] T32 · Resultados: títulos legibles, imágenes descritas, tablas con `<caption>` y navegación R1–R4 (V8, V9, A3 en resultados, A8)
  - Archivos: `rutas/r5/app.py` (`TITULOS_RESULTADOS` con los 15 títulos y descripciones del plan; `TAMANOS_IMAGENES`; `tabla_con_titulo(html, descripcion, archivo)` con `markupsafe.escape`; `presentar_resultados(crudo)`; la vista pasa `seccion="resultados"`, `requerimientos=list(ARCHIVOS_RESULTADOS)` y `**presentar_resultados(resultados(r, results))`); `rutas/r5/templates/resultados.html` (como en el plan: `<nav class="requerimientos" aria-label="Resultados por requerimiento">` con R1–R4 y `aria-current="true"` en el actual; `<figure class="grafica">` con `<h2>`, `<p class="descripcion">` + `<code>archivo</code>` e `<img … alt="{{ descripcion }}" width height loading="lazy">`; tablas en `<div class="tabla-ancha">`; `<section class="faltantes">` con `<h2>Faltan</h2>` solo si hay); `rutas/r5/static/estilos.css` (sección 12 Resultados)
  - Test primero: `::test_titulos_cubren_la_lista_fija` (las claves de `TITULOS_RESULTADOS` son exactamente los 15 archivos de `ARCHIVOS_RESULTADOS`; títulos no vacíos, distintos entre sí y distintos del nombre del archivo; cada descripción termina en «.» y no contiene «Faltan» ni «Regla de las 11 h»; `TITULOS_RESULTADOS["r2_cociente.csv"][0] == "Cociente lineal / cola de prioridad (10 pares cercanos)"`), `::test_tamanos_de_imagenes` (claves = las 4 imágenes; para `r2_tiempo_vs_explorados.png` y `r3_envolvente.png` de `results/` real, `(ancho, alto)` = los enteros de la cabecera IHDR de la PNG, leídos con `struct` en la prueba), `::test_tabla_con_titulo` (entrada `<table class="dataframe tabla"><thead><tr><th>a</th></tr></thead>…` y descripción `"x < y."` → el `<caption>` va justo después de la etiqueta `<table …>`, contiene `x &lt; y.` y `<code>archivo.csv</code>`; todos los `<th>` llevan `scope="col"`; las celdas no cambian), `::test_a8_imagen_y_titulo` (`/resultados/r2` sintético: la etiqueta `<img` tiene `alt` no vacío y distinto de `r2_tiempo_vs_explorados.png`, `width="1050"`, `height="675"` y `loading="lazy"`; aparece «Cociente lineal / cola de prioridad (10 pares cercanos)»), `::test_v8_tablas_de_resultados` (en `/resultados/r2` sintético: cada `<table` va seguida de `<caption>` y está dentro de `class="tabla-ancha"`; número de `class="tabla-ancha"` = número de tablas; hay `scope="col"`), `::test_v9_navegacion_requerimientos` (`/resultados/r3`: enlaces `href="/resultados/r1"` … `r4` dentro de `class="requerimientos"`; `aria-current="true"` en el de r3; un solo `aria-current="page"`, en «Resultados»), `::test_faltantes_con_titulo` (`/resultados/r4` sintético: el bloque `class="faltantes"` contiene el título de `r4_exactas.csv`, `r4_exactas.csv` y `python -m rutas.r4.medir_exactas`)
  - Verificar: `.venv/bin/python -m pytest tests/test_visual_r5.py -k "titulos or tamanos or tabla_con_titulo or a8 or v8_tablas or v9 or faltantes or a3" && .venv/bin/python -m pytest tests/test_app_r5.py -k "caso_11 or caso_12" -q && .venv/bin/python -m pytest tests/test_servicios_r5.py -k "resultados or lista_fija" -q` (en especial `test_caso_11_resultados_r2` («r2_cociente.csv» visible) y `test_caso_11_cuatro_paginas_reales` (sin «Faltan» en r2 y r3))
  - Nota para después: cuando exista `results/r4/r4_tiempo_vs_k.png`, actualizar su tamaño en `TAMANOS_IMAGENES` (hoy aproximado) y agregarlo a `test_tamanos_de_imagenes`.
  - anotar en `docs/anexo-ia.md`
  - Nota: DESVIACIÓN DE CONTEO: la lista fija `ARCHIVOS_RESULTADOS` tiene **16** archivos (5 + 4 + 2 + 5), no 15 como dice el plan; `TITULOS_RESULTADOS` tiene los 16 y la prueba exige `== 16`. Se cambió además «origen–destino» por «origen-destino» (guion simple) en dos descripciones. Sigue pendiente actualizar el tamaño de `r4_tiempo_vs_k.png` cuando exista.

- [x] T33 · Inicio con cuatro tarjetas (V10)
  - Archivos: `rutas/r5/templates/inicio.html` (`<ul class="secciones">` con 4 `<li class="tarjeta-seccion">`, los textos del plan; corrige «envolvente convexa de los 42 lugares» por los nodos de la red); `rutas/r5/static/estilos.css` (sección 13 Inicio)
  - Test primero: `::test_v10_inicio_tarjetas` (`GET /`: 4 `class="tarjeta-seccion"`; dentro de ellas `href="/ruta"`, `href="/envolvente"`, `href="/itinerario"`, `href="/resultados/r1"`; textos «Dijkstra con cola de prioridad», «QuickHull», «Held-Karp», «vecino más cercano»; contiene «nodos de la red» y no «envolvente convexa de los 42 lugares»; `aria-current="page"` en la marca)
  - Verificar: `.venv/bin/python -m pytest tests/test_visual_r5.py -k v10 && .venv/bin/python -m pytest tests/test_app_r5.py -k "inicio or algoritmos" -q`
  - anotar en `docs/anexo-ia.md`
  - Nota: sin desviaciones.

- [x] T34 · Suite completa y restricciones del ajuste (cierre automático de B5)
  - Nota (ronda 2, sugerencia 8): la desviación de los colores al pasar el mouse (Bahareque y Cocora en lugar de Niebla y Guadua) queda anotada en T27 y corregida en `plan.md`; spec, plan y código dicen lo mismo.
  - Nota: `_main_con_run_falso` en `tests/test_app_r5.py` simula ahora `rutas.r5.app.puerto_libre` (devuelve `True`); antes `test_puerto_por_defecto` y `test_main_arranca` fallaban si la app ya escuchaba en 5050. `test_puerto_ocupado` sigue con un socket real ocupado en puerto efímero (determinista). Código de la app sin tocar.
  - Archivos: ninguno nuevo (R5 no genera resultados: no hay archivos que regenerar)
  - Test primero: no aplica
  - Comando:
    ```bash
    cd /Users/nicolascastro/Desktop/proyecto-final-rutas-quindio && .venv/bin/python -m pytest && git diff --stat -- rutas/r1 rutas/r2 rutas/r3 rutas/r4 rutas/r5/servicios.py rutas/r5/datos.py rutas/r5/formato.py requirements.txt .gitignore Dockerfile && git diff --stat -- tests/test_app_r5.py tests/test_red_real_r5.py tests/test_mapas_r5.py && grep -c "<style" rutas/r5/templates/base.html; wc -l rutas/r5/static/estilos.css
    ```
  - Verificar: todas las pruebas pasan (las de antes más las de `tests/test_visual_r5.py`; las `red` de R5 corren sin saltar); los dos `git diff --stat` están vacíos (nada prohibido tocado y las pruebas actuales sin cambios); `grep -c "<style"` da 0; `estilos.css` tiene unas 200 líneas (orientativo). Anotar el conteo final de pruebas aquí
  - Cierre de B5 (automático): en verde → seguir con T35
  - anotar en `docs/anexo-ia.md`
  - Resultado (2026-11-12, implementer): `-m "not red"`: 540 pasan, 1 se salta, 1 falla (`test_app_r5.py::test_puerto_por_defecto`, porque el puerto 5050 está ocupado por un proceso ajeno, PID 71719, que ya corría antes de empezar B5; con el puerto libre no depende del ajuste: no toca la plantilla ni `main`). `-m red`: 39 pasan y 2 se saltan (los dos conocidos: `test_red_real.py:79` y `test_red_real_r4.py:126`; las `red` de R5 corren). Suite completa: 579 pasan, 3 se saltan, 1 falla (la misma). Pruebas nuevas: 44 en `tests/test_visual_r5.py`. Los dos `git diff --stat` (prohibidos y pruebas actuales) salen vacíos; `grep -c "<style" base.html` = 0; `estilos.css` tiene 148 líneas; sin `<script`, `javascript:`, `@import` ni `url(http`. `curl` con la app en el puerto 5071 (ya detenida): `/static/estilos.css` (text/css), `/`, `/ruta`, `/ruta?origen=C01&destino=C12`, `/envolvente`, `/itinerario?...` (caso 5) y `/resultados/r1..r4` dan 200. Mutaciones vistas fallar y restauradas: `COLORES["voraz"]` distinto del CSS, `<style>` en base, sin `scope="row"` en la tabla de la envolvente, `<span>` en el `<h2>` de la ruta (falla la prueba actual del texto de `#resultado-ruta`) y `transition: all`.
  - Pendiente para el usuario: **«El puerto 5050 está ocupado»**: cerrar el servidor viejo (PID 71719) para que `test_puerto_por_defecto` pase; ese servidor usa las plantillas anteriores hasta que se reinicie.

- [ ] T35 · Revisión manual en el navegador (A10) → `review.md` · **sustituida por B9 (v2)** el 2026-11-15: no se hace; ver T46
  - Archivos: ninguno de código; el resultado lo escribe el usuario (o el reviewer con el usuario) en `specs/r5-aplicacion/review.md`, sección «Ajuste visual (A10)»
  - Test primero: no aplica (manual)
  - URLs a revisar (con la app en el puerto 5050, cerrando antes el servidor viejo): `/`, `/ruta?origen=C01&destino=C12`, `/ruta?origen=C01&destino=C01`, `/envolvente`, `/itinerario?partida=C01&atractivos=A05&atractivos=A14&atractivos=A06&atractivos=A07&atractivos=A13&atractivos=A15`, el mismo con los 8 del caso 6 (`A05, A08, A04, A14, A06, A07, A12, A01`), `/itinerario?partida=C01&atractivos=A01` (error) y `/resultados/r1` a `/resultados/r4`.
  - Preparación: `.venv/bin/python -m rutas.r5.app` y abrir `http://127.0.0.1:5050` en el navegador; tener a mano las herramientas de desarrollo (modo de diseño adaptable)
  - Lista de pasos, **a ancho de escritorio (≈ 1280 px)** y **a ≈ 375 px** (modo adaptable, p. ej. iPhone SE 375 × 667):
    1. Cabecera: se ven las curvas de nivel; el texto del menú se lee bien sobre ellas (contraste); a 375 px el menú se parte en dos líneas y **no hay desplazamiento horizontal** en ninguna página.
    2. Teclado: con Tab desde la barra de direcciones aparece «Saltar al contenido» y lleva a `main`; el foco se ve en enlaces, selects, casillas y botones; la sección actual del menú se distingue.
    3. Inicio: cuatro tarjetas legibles; «Resultados» lleva a R1 con la navegación R1–R4.
    4. Ruta C01 → C12: etiquetas encima de los selects; botón «Calcular ruta» (se hunde un poco al presionarlo); tarjetas con «29,7 min», km y nodos; el mapa ocupa el ancho y una altura cómoda en las dos anchuras. C01 → C01: el aviso se ve como aviso.
    5. Envolvente: tarjetas con «14 vértices» y «1 631,5 km²»; polígono en Hoja; tabla con título.
    6. Itinerario con C01 y A05, A14, A06, A07, A13, A15: casillas en 2–3 columnas en escritorio y 1 a 375 px, con la duración alineada; resumen → leyenda y mapa → tabla; **los colores de la leyenda coinciden con las líneas del mapa** (Held-Karp azul Cocora, voraz rojo Cereza) y con el encabezado de la tabla. Con los 8 del caso 6, el bloque de la regla aparece al final. Con 5 casillas, el error se ve como error.
    7. Resultados R1–R4: títulos legibles con su línea de descripción; imágenes escaladas sin deformarse; a 375 px las tablas anchas se desplazan **dentro** de su contenedor; R1 y R4 muestran los faltantes con su comando.
    8. Movimiento: con el mouse, los cambios de color son suaves; en las herramientas de desarrollo, emular `prefers-reduced-motion: reduce` y comprobar que el botón ya no se escala.
    9. Capturas para el documento técnico (sección 7.1): las cuatro secciones a ancho de escritorio (y, si se quiere, una a 375 px).
  - Verificar: `review.md` registra fecha, quién, navegador y versión, las dos anchuras y el resultado de cada paso. Si algo obliga a cambiar el CSS o una plantilla, se corrige y se vuelve a correr el comando de T34 antes de cerrar
  - Opcional, en la misma sesión: los pasos de navegador pendientes de los casos 16 y 17 (T23)
  - Cierre de B5: suite en verde (T34) y A10 anotado. **DETENERSE** hasta el commit del usuario
  - anotar en `docs/anexo-ia.md` (si se usó IA para revisar las capturas o redactar `review.md`)
  - Nota (2026-11-15): el usuario reemplazó el diseño v1 por el v2 (spec «Diseño visual v2: apple-design») antes de hacer esta revisión. Revisar v1 en el navegador ya no tiene sentido: la revisión manual del diseño vigente es B9 (T46). La tarea queda sin marcar y sin borrar, como historia.

## Ronda 2, sugerencias del reviewer

- [x] Sugerencia 1: cifras tabulares también en `.tarjeta dd`, `td` y `.visita`
  - Nota: prueba `test_v0_cifras_tabulares` en `tests/test_visual_r5.py`, que exige `font-variant-numeric: tabular-nums` en los tres bloques.
- [x] Sugerencia 2: el encabezado de cada método usa su color de fondo
  - Nota: prueba `test_v5_colores_encabezado_metodos`, con regex que exigen `background` y no solo el color.
- [x] Sugerencia 3: contorno del `<select>` con `var(--hoja)` (WCAG 1.4.11, ≥ 3:1)
  - Nota: prueba nueva `test_v0_contorno_select`, falló antes (Bahareque sobre blanco da 1,39:1) y pasa después (Hoja da 3,89:1); cambio en `rutas/r5/static/estilos.css:66`; `spec.md` ya actualizada. Fieldset, tarjetas y tablas siguen en Bahareque (bordes decorativos).
- [x] Sugerencia 4: las pruebas de movimiento no se dejan engañar por comentarios
  - Nota: `_css_sin_comentarios()` (sin cambiar `_css()`) y `_bloque_media()`, que cuenta llaves anidadas. `test_v0_tipos_firma_y_movimiento` busca los fragmentos sin comentarios, y la prueba nueva `test_v0_movimiento_reducido_quita_la_escala` exige `button:active { transform: none; }` dentro de `@media (prefers-reduced-motion: reduce)`. Mutaciones que fallan: el bloque cambiado por un comentario (con la prueba anterior pasaba) y quitar solo `button:active { transform: none; }`.
- [x] Sugerencia 8: colores al pasar el mouse en el plan
  - Nota: `plan.md` (sección 14 Movimiento) decía Niebla para `.menu a:hover` y Guadua para `button:hover`; el código usa Bahareque y Cocora (`estilos.css:133-134`). Se actualizó el plan con el motivo (Niebla casi no se distingue del blanco del menú y el botón ya es Guadua) y se anotó en T27 y T34. Sin cambios de código ni de pruebas.

## B6 · Diseño visual v2 (spec «Diseño visual v2: apple-design», D0–D8 y B1–B9; plan «Diseño visual v2 (bloque B6)»)

> Reemplaza por completo al ajuste visual v1 (B5, arriba, que queda como historia). La T35 de B5 queda sustituida por B9 (T46).

> **Reglas propias de B6** (además de las reglas del usuario de arriba; sustituyen a las de B5):
> 1. **No se tocan** `rutas/r1..r4/`, `rutas/r5/servicios.py`, `rutas/r5/datos.py`, `rutas/r5/formato.py`, `requirements.txt`, `.gitignore` ni el `Dockerfile`. En `rutas/r5/mapas.py` solo cambian `COLORES` y el docstring del módulo. En `rutas/r5/app.py` solo se agregan `MIN_ATRACTIVOS`, `MAX_ATRACTIVOS`, `contador_elegidos` y la clave `"contador"` del contexto de `/itinerario`.
> 2. **JavaScript:** solo `rutas/r5/static/vendor/motion.js` (copia sin cambios, con su hash) y `rutas/r5/static/app.js` (propio, ≤ 150 líneas), cargados con `defer` desde `base.html`. No se permiten `<script>` en línea, atributos `on…=`, `javascript:` ni CDN. No se crean `package.json` ni `node_modules` en el repositorio.
> 3. **Pruebas de v1:** solo se borran o reescriben las de la tabla «Pruebas de v1: qué se reescribe, qué se borra y qué se conserva» del plan, en la tarea que indica la tabla. Cada sustituta se escribe antes y se ve fallar. Ninguna otra prueba se modifica: si una conservada o una funcional falla, se corrige la plantilla, el CSS o `app.js`, no la prueba.
> 4. Las pruebas nuevas van en `tests/test_visual_r5.py`, en una sección «Diseño v2» (sin la marca `red`), y reutilizan `_css_sin_comentarios`, `_bloque_media`, `_bloque` y `_cliente`.
> 5. **Regresión de cada tarea**, además de su prueba: `.venv/bin/python -m pytest tests/test_app_r5.py tests/test_mapas_r5.py tests/test_visual_r5.py -q`. Si la tarea toca `base.html`, ruta, envolvente o itinerario, también `.venv/bin/python -m pytest tests/test_red_real_r5.py -q` (contiene «29,7», «178,7», «190,4», «11,8», «14 vértices» y «1 631,5»).
> 6. B6 es un solo bloque: T36 a T45. Al cerrar T45 el trabajo se **DETIENE** hasta el commit del usuario. T46 (B9) es del usuario.

- [ ] T36 · Línea base y Motion en `vendor/` con su hash (B3)
  - Archivos: `rutas/r5/static/vendor/motion.js` y `rutas/r5/static/vendor/LICENSE.md` (copias sin cambios); `tests/test_visual_r5.py` (abrir la sección «Diseño v2»)
  - Pasos previos:
    1. `git rev-parse --short HEAD` → anotar aquí como `BASE_B6` (lo usa T45);
    2. `.venv/bin/python -m pytest -q` → anotar la línea base (según la ronda 2: `-m "not red"` 541 pasan y 1 se salta);
    3. `git status --short -- rutas/r1 rutas/r2 rutas/r3 rutas/r4 rutas/r5/servicios.py rutas/r5/datos.py rutas/r5/formato.py requirements.txt .gitignore Dockerfile` → vacío.
  - Copia: con los comandos del plan, «Motion: copia del paquete y hash», desde `/private/tmp/claude-501/-Users-nicolascastro-Desktop-proyecto-final-rutas-quindio/7659aacf-74cc-4238-84a5-ec57e0bde412/scratchpad/motion/package/`. Si el scratchpad ya no existe: `npm pack motion@14.14.0` en una carpeta temporal **fuera** del repositorio. Si el hash no coincide, **DETENERSE** y preguntar.
  - Test primero:
    - `::test_b3_motion_con_hash_y_licencia`: el SHA-256 de `static/vendor/motion.js` es `521cfef8910fdd997463ea9881d4b790e017331e3d2f79c02adfc4d5fe1f2cae` (con `hashlib`); `vendor/LICENSE.md` existe y contiene «MIT»; `motion.js` contiene `Motion`.
    - `::test_b3_js_servidos`: parametrizada; en esta tarea solo `/static/vendor/motion.js` → 200.
    - Rojo esperado: la carpeta `vendor/` no existe.
  - Verificar: `.venv/bin/python -m pytest tests/test_visual_r5.py -k b3 && shasum -a 256 rutas/r5/static/vendor/motion.js && ! git check-ignore -q rutas/r5/static/vendor/motion.js`
  - anotar en `docs/anexo-ia.md`

- [ ] T37 · Guardia de JavaScript nueva, `app.js` mínimo y los dos `<script>` en `base.html` (B2; D8, «ausencia total de `<script`»)
  - Archivos:
    - `tests/test_visual_r5.py`: borrar `test_a9_sin_js_propio`; agregar las `test_b2_*` de abajo; agregar `/static/app.js` a `test_b3_js_servidos`.
    - `tests/test_app_r5.py`: cambiar **solo** el bucle de plantillas de `test_sin_algoritmos_ni_js_propio` y la última línea de `test_inicio_y_menu`, como dice el plan. Las aserciones de algoritmos, de `requirements.txt` y de los `href` no cambian.
    - `rutas/r5/static/app.js`: crear solo la cabecera comentada, la IIFE con `"use strict"` y `const movimientoReducido = window.matchMedia("(prefers-reduced-motion: reduce)");`. M2 y M3 llegan en T42.
    - `rutas/r5/templates/base.html`: las dos etiquetas en `<head>`, primero la de Motion.
  - Test primero:
    - `::test_b2_scripts_solo_en_base`
    - `::test_b2_sin_js_en_linea`
    - `::test_b2_solo_dos_archivos_js`
    - `::test_b2_app_js_limites`
    - `::test_b2_html_servido_solo_dos_scripts` (parametrizada con `PAGINAS`)
    - `::test_b3_js_servidos[/static/app.js]`
    - las 2 reescritas de `tests/test_app_r5.py`, que ahora exigen los dos `<script>` permitidos.
    - Rojo esperado: `base.html` no tiene scripts y `app.js` no existe.
  - Verificar: `.venv/bin/python -m pytest tests/test_visual_r5.py -k "b2 or b3" && .venv/bin/python -m pytest tests/test_app_r5.py -q && git diff -- tests/test_app_r5.py`. El diff muestra solo las 2 aserciones.
  - Mutaciones que deben fallar y luego se restauran: `onclick="x"` en `ruta.html`; `fetch(` en un comentario de `app.js`; un `rutas/r5/static/x.js` vacío.
  - anotar en `docs/anexo-ia.md`

- [ ] T38 · `estilos.css` v2: colores claro y oscuro, tipografía, contraste, M1 y `COLORES` (D1, D2, D6 M1 y movimiento reducido, D8; parte de B4 y B5)
  - Archivos:
    - `rutas/r5/static/estilos.css`: reescribirlo completo con las 20 secciones del plan. En esta tarea se llenan:
      - las secciones 1 a 6;
      - lo mínimo de la 9 (`.tarjeta dd {` con `tabular-nums`);
      - la 10 (`select`);
      - lo mínimo de la 11 (`.casillas {` con `grid-template-columns` y `.visita {` con `tabular-nums`);
      - la 15 (tablas, `td {` con `tabular-nums` y `thead .metodo-*` con franja);
      - la 18 (M1);
      - el bloque `prefers-reduced-motion: reduce` de la 19.

      Las demás secciones quedan con su comentario y se llenan entre T39 y T44.
    - `rutas/r5/mapas.py`: solo `COLORES` y el docstring de las líneas 1 a 5.
    - `rutas/r5/templates/base.html`: solo `<meta name="color-scheme" content="light dark">`.
    - `tests/test_visual_r5.py`.
  - Test primero:
    - **Borrar** `test_a11_paleta_en_css` (con `PALETA`) y `test_v0_tipos_firma_y_movimiento`.
    - **Reescribir**:
      - `test_a11_colores_de_mapas` → `::test_b5_colores_de_metodos`;
      - `test_v0_contorno_select` → `::test_b4_contorno_de_controles`;
      - `test_v5_colores_encabezado_metodos` → `::test_b5_encabezados_de_metodo`;
      - `test_v0_movimiento_reducido_quita_la_escala` → `::test_b4_movimiento_reducido`.
    - **Agregar** `::test_b4_variables_claro_y_oscuro`, `::test_b4_color_scheme`, `::test_b4_tipografia`, `::test_b4_contraste`, `::test_d8_sin_rastros_de_v1` y `::test_b4_movimiento_m1`.
    - Rojo esperado: el CSS y `COLORES` todavía son los de v1.
  - Verificar: `.venv/bin/python -m pytest tests/test_visual_r5.py -k "b4 or b5 or d8 or cifras or cuadricula or transition_all or a7" && .venv/bin/python -m pytest tests/test_app_r5.py tests/test_mapas_r5.py tests/test_visual_r5.py -q && .venv/bin/python -m pytest tests/test_red_real_r5.py -q`. Fijarse en las conservadas `test_v0_cifras_tabulares`, `test_v3_fieldset_y_cuadricula`, `test_a7_leyenda_con_colores`, `test_a11_sin_transition_all_ni_externos` y en `test_mapas_r5.py::test_mapa_itinerario`.
  - Mutación que debe fallar y luego se restaura: `--texto-secundario: #8E8E93` en claro (falla `test_b4_contraste`).
  - anotar en `docs/anexo-ia.md`

- [ ] T39 · Barra translúcida, superficies y preferencias del sistema (D3, menú de D4; B4)
  - Archivos:
    - `rutas/r5/templates/base.html`: `<header class="barra">` en lugar de `class="cabecera"`; el resto igual.
    - `rutas/r5/static/estilos.css`: secciones 7, 8, 9 completa y 14 (mapas y leyenda, con `color-scheme: light` en `iframe.mapa`), más el resto de la 19 (`prefers-reduced-transparency`, `prefers-contrast: more`) y el `@supports not` de la barra.
  - Test primero:
    - `::test_b4_barra_translucida`
    - `::test_b4_preferencias`
    - `::test_d3_superficies`
    - `::test_d4_menu` (parametrizada con `PAGINAS`)
    - Rojo esperado: no hay `.barra` ni bloques de preferencias.
  - Verificar: `.venv/bin/python -m pytest tests/test_visual_r5.py -k "b4 or d3 or d4 or a2 or a3 or v10" && .venv/bin/python -m pytest tests/test_app_r5.py tests/test_mapas_r5.py tests/test_visual_r5.py -q && .venv/bin/python -m pytest tests/test_red_real_r5.py -q`
  - anotar en `docs/anexo-ia.md`

- [ ] T40 · Lista agrupada, botón píldora y errores con su siguiente paso (D5; Ruta y la partida del Itinerario)
  - Archivos:
    - `rutas/r5/templates/ruta.html`: `.grupo` y `.fila`; `class="boton-principal"`; el error con su siguiente paso. El bloque `#resultado-ruta` no cambia.
    - `rutas/r5/templates/itinerario.html`: solo el grupo de la partida, el botón y el error. Las fichas son de T41.
    - `rutas/r5/static/estilos.css`: secciones 10, 12, 13 y 20.
  - Test primero:
    - `::test_d5_lista_agrupada`
    - `::test_d5_boton_principal`
    - `::test_d5_error_con_siguiente_paso`
    - Rojo esperado: no hay `.grupo` ni `.boton-principal`, y el error no trae el siguiente paso.
  - Verificar: `.venv/bin/python -m pytest tests/test_visual_r5.py -k "d5 or a4 or a6" && .venv/bin/python -m pytest tests/test_app_r5.py tests/test_mapas_r5.py tests/test_visual_r5.py -q && .venv/bin/python -m pytest tests/test_red_real_r5.py -q`. Fijarse en:
    - `test_ruta_formulario` (16 `<option`);
    - `test_ruta_lugar_desconocido`;
    - `test_ruta_incompleta` (sin resultado no aparecen «desconocido» ni «Tiempo de viaje»);
    - `test_caso_8_itinerario_400`;
    - `test_ruta_sintetica_app` (el `<h2>` en texto plano).
  - anotar en `docs/anexo-ia.md`

- [ ] T41 · Fichas de atractivos y contador renderizado por el servidor (fichas de D5, M3 en el servidor; B6)
  - Archivos:
    - `rutas/r5/app.py`: `MIN_ATRACTIVOS`, `MAX_ATRACTIVOS` y `contador_elegidos(n)`; primero como stub con `raise NotImplementedError`, para que la prueba falle por la razón correcta. En la vista `/itinerario`, `contexto["contador"] = contador_elegidos(n)`, donde `n` es el número de casillas que quedan marcadas, en las tres salidas: formulario vacío, 200 y 400.
    - `rutas/r5/templates/itinerario.html`: `fieldset` con `aria-describedby="contador"`; `<legend>` según DV-2; `<p id="contador" class="contador" aria-live="polite" data-estado=…>` con ícono, cuenta, regla y estado; fichas `<label class="ficha">` con `checked` justo después de `value`.
    - `rutas/r5/static/estilos.css`: la sección 11 completa.
  - Test primero:
    - `::test_contador_elegidos`
    - `::test_contador_limites_iguales_a_servicios`
    - `::test_b6_contador_en_la_pagina`
    - `::test_d5_fichas`
    - Con la opción A de DV-2, ajustar en `::test_a4_labels_y_botones` **solo** el fragmento de la leyenda (`<legend>Atractivos</legend>`).
    - Rojo esperado: `NotImplementedError` del stub, y la página todavía no tiene contador ni fichas.
  - Verificar: `.venv/bin/python -m pytest tests/test_visual_r5.py -k "contador or b6 or d5 or a4 or v3" && .venv/bin/python -m pytest tests/test_app_r5.py tests/test_mapas_r5.py tests/test_visual_r5.py -q && .venv/bin/python -m pytest tests/test_red_real_r5.py -k "caso_9 or no_cabe or formulario" -q`. Fijarse en:
    - `test_itinerario_sin_parametros` (6 `name="atractivos"`);
    - `test_caso_8_itinerario_400` (`value="A01" checked`);
    - `test_formulario_42_lugares_15_atractivos`;
    - `test_itinerario_bloque_regla_no_aparece_si_cabe`.
  - anotar en `docs/anexo-ia.md`

- [ ] T42 · `app.js`: M2, entrada de las tarjetas, y M3, contador en vivo (D6 M2 y M3, movimiento reducido; B2)
  - Archivos: `rutas/r5/static/app.js`, completo como el esbozo del plan y de ≤ 150 líneas
  - Test primero:
    - `::test_b2_app_js_m2_m3`
    - `::test_b2_app_js_limites` sigue en verde.
    - Rojo esperado: `app.js` solo tiene el esqueleto de T37.
  - Verificar: `.venv/bin/python -m pytest tests/test_visual_r5.py -k b2 && wc -l rutas/r5/static/app.js && .venv/bin/python -m pytest tests/test_app_r5.py tests/test_mapas_r5.py tests/test_visual_r5.py -q`. `wc -l` debe dar ≤ 150.
  - Mutación que debe fallar y luego se restaura: `bounce: 0.2`.
  - Prueba de humo opcional: `.venv/bin/python -m rutas.r5.app --puerto 5061`; abrir `/itinerario`, marcar y desmarcar fichas, y ver que el contador cambia. Detener el servidor. La comprobación formal es B9 (T46).
  - anotar en `docs/anexo-ia.md`

- [ ] T43 · Control segmentado en Resultados y transición entre páginas (D4 y M4 de D6; B7 y B4)
  - Archivos:
    - `rutas/r5/templates/resultados.html`: `<nav class="segmentado">` con `aria-current="page"` en el actual y el `<span class="indicador" aria-hidden="true">` **después** del texto.
    - `rutas/r5/templates/base.html`: en Resultados, el menú usa `aria-current="true"` (DV-1).
    - `rutas/r5/static/estilos.css`: la sección 16 y la parte M4 de la 18, con `@view-transition` dentro de `@media (prefers-reduced-motion: no-preference)`.
  - Test primero:
    - **Reescribir** `test_v9_navegacion_requerimientos` → `::test_b7_control_segmentado`, parametrizada con r2 y r3.
    - **Quitar** el parámetro `("/resultados/r2", "Resultados")` de `::test_a3_aria_current`.
    - **Agregar** `::test_b4_view_transition`.
    - Rojo esperado: la navegación todavía es la de v1, con `aria-current="true"` en el actual.
  - Verificar: `.venv/bin/python -m pytest tests/test_visual_r5.py -k "b7 or view_transition or a3 or a8 or v8 or faltantes or titulos" && .venv/bin/python -m pytest tests/test_app_r5.py -k "caso_11 or caso_12" -q && .venv/bin/python -m pytest tests/test_app_r5.py tests/test_mapas_r5.py tests/test_visual_r5.py -q`. Fijarse en `test_caso_11_cuatro_paginas_reales`: sin «Faltan» en r2 y r3.
  - Mutaciones que deben fallar y luego se restauran: `aria-current="page"` en «Resultados» del menú; `@view-transition` fuera de `no-preference`.
  - anotar en `docs/anexo-ia.md`

- [ ] T44 · Encabezado de cada página e inicio (D0, D7)
  - Archivos:
    - `rutas/r5/templates/inicio.html`, `ruta.html`, `envolvente.html`, `itinerario.html` y `resultados.html`: `<p class="entradilla">` justo después del `<h1>`, con los textos del plan (DV-12).
    - `inicio.html`: un solo enlace por tarjeta.
    - `rutas/r5/static/estilos.css`: secciones 5 (`.entradilla`), 8 y 17.
  - Test primero:
    - `::test_d0_titulo_y_entradilla`
    - `::test_d7_inicio`
    - Rojo esperado: no hay entradillas ni el enlace extendido.
  - Verificar: `.venv/bin/python -m pytest tests/test_visual_r5.py -k "d0 or d7 or v10" && .venv/bin/python -m pytest tests/test_app_r5.py tests/test_mapas_r5.py tests/test_visual_r5.py -q && .venv/bin/python -m pytest tests/test_red_real_r5.py -q`. Fijarse en `test_ruta_incompleta`, `test_caso_11_cuatro_paginas_reales` y `test_itinerario_bloque_regla_no_aparece_si_cabe`: las entradillas no pueden decir «desconocido», «Tiempo de viaje», «Faltan» ni «Regla de las 11 h».
  - anotar en `docs/anexo-ia.md`

- [ ] T45 · Suite completa, restricciones y mutaciones (cierre automático de B6; B8)
  - Archivos: ninguno nuevo. R5 no genera resultados, así que no hay archivos que regenerar.
  - Test primero: no aplica
  - Comando (reemplazar `BASE_B6` por el hash anotado en T36):
    ```bash
    cd /Users/nicolascastro/Desktop/proyecto-final-rutas-quindio && .venv/bin/python -m pytest \
      && git diff --stat BASE_B6 -- rutas/r1 rutas/r2 rutas/r3 rutas/r4 rutas/r5/servicios.py rutas/r5/datos.py rutas/r5/formato.py requirements.txt .gitignore Dockerfile \
      && git diff --stat BASE_B6 -- tests/test_red_real_r5.py tests/test_mapas_r5.py tests/test_servicios_r5.py tests/test_datos_r5.py tests/test_formato_r5.py tests/test_dockerfile_r5.py tests/conftest.py \
      && git diff BASE_B6 -- tests/test_app_r5.py \
      && shasum -a 256 rutas/r5/static/vendor/motion.js \
      && find rutas/r5/static -name '*.js' | sort \
      && wc -l rutas/r5/static/app.js rutas/r5/static/estilos.css \
      && git status --short
    ```
  - Verificar:
    - todas las pruebas pasan, y las `red` de R5 corren sin saltarse;
    - los dos `git diff --stat` salen vacíos;
    - el diff de `test_app_r5.py` muestra solo las 2 aserciones de «sin `<script`»;
    - el hash es el de la spec;
    - hay exactamente 2 `.js`, y `app.js` tiene ≤ 150 líneas;
    - `git status` no muestra `package.json` ni `node_modules`.
  - Mutaciones de la tabla «Verificación del diseño v2» del plan: cada una debe hacer fallar al menos una prueba, y luego se restaura.
  - Anotar aquí el conteo final de pruebas.
  - Cierre de B6: en verde, el trabajo se **DETIENE** hasta el commit del usuario. Después sigue T46, que hace el usuario.
  - anotar en `docs/anexo-ia.md`

- [ ] T46 · B9: revisión manual del usuario en Chrome y Safari → `review.md` y capturas en `evidencias/r5/`
  - Archivos: ninguno de código. El usuario, o el reviewer con el usuario, escribe el resultado en `specs/r5-aplicacion/review.md`, sección «Diseño v2 (B9)», y guarda las capturas en `evidencias/r5/`.
  - Test primero: no aplica (manual)
  - Preparación:
    - cerrar cualquier instancia vieja en el puerto 5050, porque serviría las plantillas de v1;
    - arrancar con `.venv/bin/python -m rutas.r5.app` y abrir `http://127.0.0.1:5050`;
    - anotar la versión de Chrome y la de Safari.
  - Matriz: {Chrome, Safari} × {claro, oscuro} × {≈ 1280 px, ≈ 375 px}, más una pasada con movimiento reducido en cada navegador. Cómo emular:
    - **Modo oscuro**: en Chrome, DevTools → Rendering → «Emulate CSS media feature prefers-color-scheme»; en Safari, Ajustes del Sistema → Apariencia.
    - **Movimiento reducido**: en Chrome, Rendering → `prefers-reduced-motion: reduce`; en Safari, Ajustes del Sistema → Accesibilidad → Pantalla → Reducir movimiento.
    - **375 px**: en Chrome, el modo de dispositivo (iPhone SE); en Safari, Desarrollo → Entrar en el modo de diseño adaptable.
    - **Transparencia y contraste**, en el mismo panel de Accesibilidad: Reducir transparencia y Aumentar contraste.
  - URLs:
    - `/`;
    - `/ruta?origen=C01&destino=C12`, `/ruta?origen=C01&destino=C01` y `/ruta?origen=X99&destino=C01`;
    - `/envolvente`;
    - `/itinerario`;
    - el itinerario del caso 5: `/itinerario?partida=C01&atractivos=A05&atractivos=A14&atractivos=A06&atractivos=A07&atractivos=A13&atractivos=A15`;
    - el mismo con los 8 del caso 6 (`A05, A08, A04, A14, A06, A07, A12, A01`);
    - `/itinerario?partida=C01&atractivos=A01`;
    - `/resultados/r1` a `/resultados/r4`.
  - Lista de pasos (spec B9 y lo que no se puede automatizar):
    1. **Las tarjetas entran sin rebote.** En ruta, envolvente e itinerario con resultado, las tarjetas del resumen suben 8 px, aparecen escalonadas y se detienen sin pasarse. Para verlo, Chrome DevTools → Animations, al 10 %. Con movimiento reducido: solo un fundido corto, sin desplazamiento. Anotar si hay un parpadeo antes de la animación (DV-9).
    2. **El contador responde.** En `/itinerario`, al marcar y desmarcar fichas, «N elegidos (elige de 6 a 8)» cambia al instante: «✓ … listo para calcular» entre 6 y 8, y «! … falta / sobra …» fuera de ese rango. El botón nunca se deshabilita: con 5 se envía y el servidor responde con el error. Con «Atrás» después de calcular, el contador coincide con las casillas. Opcional: con VoiceOver (Cmd+F5), el cambio se anuncia.
    3. **El indicador del segmentado se desliza.** En Resultados, ir de R1 a R4 y de R4 a R2: el fondo del segmento activo se traslada (Chrome ≥ 126, Safari ≥ 18.2). Si no se anima, anotar «sin animación» y la versión. Con movimiento reducido no hay transición.
    4. **La barra translúcida es legible.** Desplazar la página para que el mapa, una tabla y las tarjetas pasen por debajo: el menú se lee siempre, y en lugar de una línea dura hay un desvanecido. Con «Reducir transparencia» y «Aumentar contraste», la barra queda sólida; anotar si un navegador no lo reconoce.
    5. **El contraste se cumple en los dos modos.** Revisar el texto secundario, los captions, el contador, los ids, el botón en modo oscuro y los contornos de los selects y de las casillas. El naranja solo aparece como línea, muestra o franja, nunca como texto. Opcional: el selector de contraste de Chrome DevTools.
    6. **M1.** El botón, las fichas y los segmentos se hunden un poco al presionarlos; con movimiento reducido, no.
    7. **Mapas.** Siguen claros en modo oscuro (aceptado en D2: anotarlo). Los colores de la leyenda coinciden con las líneas del mapa y con las franjas de la tabla (azul para Held-Karp, naranja para el voraz), y el polígono de la envolvente es verde.
    8. **375 px.** No hay desplazamiento horizontal en ninguna página. Las fichas van en 1 columna y la etiqueta encima del select. El segmentado se ve completo. Las tablas anchas se desplazan dentro de su caja.
    9. **Teclado.** Con Tab aparece «Saltar al contenido», que lleva a `main` sin dejarlo debajo de la barra. El foco se ve en fichas, segmentos, enlaces y botones. La sección actual se distingue, también la marca en el inicio (sugerencia 5 de la ronda 2).
    10. **Sin JavaScript** (en Chrome, Command Menu → «Disable JavaScript»): todo funciona, las tarjetas se ven y el contador muestra el valor del servidor.
  - Capturas para `evidencias/r5/` (documento técnico, sección 7.1), con nombres `r5-<pagina>-<modo>-<ancho>.png`. Como mínimo:
    - `r5-inicio-claro-1280.png`
    - `r5-ruta-claro-1280.png` (C01 → C12)
    - `r5-envolvente-claro-1280.png`
    - `r5-itinerario-oscuro-1280.png` (caso 5)
    - `r5-resultados-r2-oscuro-1280.png`
    - `r5-itinerario-claro-375.png`
  - Verificar: `review.md` registra fecha, quién lo hizo, navegadores con versión, modos, anchuras y el resultado de cada paso. Si algo obliga a cambiar el CSS, una plantilla o `app.js`, se corrige con su prueba y se vuelve a correr el comando de T45 antes de cerrar.
  - Opcional, en la misma sesión: los pasos de navegador pendientes de los casos 16 y 17 (T23).
  - anotar en `docs/anexo-ia.md` (si se usó IA para revisar las capturas o redactar `review.md`)

## Cobertura

| Caso / punto | Tarea |
|---|---|
| 1 Ruta real C01→C12 y asimetría | T11 |
| 2 `/ruta` real con «29,7» y Leaflet | T12, T19 |
| 3 Origen = destino (sintético y real) | T7, T14, T11, T19 |
| 4 Mismo nodo (T03/T05; A02/A06 sintético) | T7, T11 |
| 5 Itinerario que cabe | T9, T11 |
| 6 Itinerario que no cabe y regla de R4 | T9, T11, T19 |
| 7 Tramos = matriz | T9, T11 |
| 8 Validación → 400 sin Held-Karp | T8, T16 |
| 9 `/itinerario` real con «178,7», «190,4», «11,8» | T19 |
| 10 Envolvente (4 vértices sintética; 14 vértices y 1 631,5 km² real) | T12, T15, T19 |
| 11 Resultados (r2, r4 sin exactas, r1..r4 reales) | T10, T17 |
| 12 Archivos protegidos y `/resultados/r9` | T17 |
| 13 Datos faltantes y `main` → 1 sin traza | T5, T18 |
| 14 Carga única | T16 |
| 15 Coordenadas siguen la geometría | T6 |
| 16 Arranque con el README (manual) | T21, T23 |
| 17 Docker (opcional, manual) | T20, T23 |
| Bordes: id desconocido, incompleto, puerto ocupado, 6 caben / 8 no | T7, T14, T16, T18, T19 |
| Comportamiento 6 (base, menú, sin JS) y «no implementa algoritmos nuevos» | T2, T13 |
| R5.1 viñetas 1–4 | T6–T10, T12, T14–T17, T19 |
| R5 ejecución local con el README / Docker opcional | T18, T20, T21, T23 |
| Secciones 7 y 8 (aplicación que muestra resultados y funciona con el README) | T17, T19, T21, T23, T24 |
| Anexo de IA | T22 (y cada tarea con IA) |

### Cobertura del ajuste visual (B5)

| Punto / caso | Tarea |
|---|---|
| V0 paleta | T26 |
| V0 tipografía, curvas de nivel, movimiento | T27, T35 |
| V0 textos (botones con verbo concreto, inicio) | T28, T33 |
| V1 hoja propia sin CSS en línea | T26, T27 |
| V2 viewport, saltar, `aria-current`, foco, menú en 375 px | T27, T35 |
| V3 formularios | T28 |
| V4 tarjetas de resumen | T29, T30, T31 |
| V5 colores, leyenda, tabla y orden del itinerario | T26, T31 |
| V6 mensajes con `role` | T28 |
| V7 iframes con `title` y altura adaptable | T29, T30, T31, T35 |
| V8 tablas | T30, T32 |
| V9 resultados | T32 |
| V10 inicio | T33 |
| A1, A2, A3 | T27 (A3 en resultados también T32) |
| A4, A6 | T28 |
| A5 | T29, T30, T31 |
| A7 | T31 |
| A8 | T32 |
| A9 | T25, T26 |
| A10 (manual) | T35 |
| A11 | T26 |
| Pruebas actuales intactas («29,7», «178,7», «190,4», «11,8», «14 vértices», «1 631,5») | T25–T34 (regresión de cada tarea), T34 |
| Sin dependencias; `servicios.py` y R1–R4 sin tocar | T25, T34 |

### Cobertura del diseño v2 (B6)

| Punto / caso | Tarea | Prueba principal |
|---|---|---|
| D0 título, entradilla, resumen, detalle | T44 (T38 tipografía) | `test_d0_titulo_y_entradilla` |
| D1 tipografía | T38 | `test_b4_tipografia`, `test_v0_cifras_tabulares` (conservada) |
| D2 colores claro/oscuro, métodos, contraste, Folium claro | T38, T39 | `test_b4_variables_claro_y_oscuro`, `test_b4_contraste`, `test_b4_contorno_de_controles`, `test_b5_*`, `test_d3_superficies` |
| D3 materiales y profundidad | T39 | `test_b4_barra_translucida`, `test_b4_preferencias`, `test_d3_superficies` |
| D4 menú y control segmentado | T39, T43 | `test_d4_menu`, `test_a3_aria_current` (conservada), `test_b7_control_segmentado` |
| D5 lista agrupada, fichas, botón, errores | T40, T41 | `test_d5_*`, `test_a4_labels_y_botones` y `test_a6_alert_y_status` (conservadas) |
| D6 M1 | T38 | `test_b4_movimiento_m1` |
| D6 M2 | T42 | `test_b2_app_js_m2_m3`; B9 |
| D6 M3 | T41, T42 | `test_b6_contador_en_la_pagina`, `test_contador_*`, `test_b2_app_js_m2_m3`; B9 |
| D6 M4 | T43 | `test_b4_view_transition`; B9 |
| D6 movimiento reducido y rendimiento | T38, T42, T43 | `test_b4_movimiento_reducido`, `test_b2_app_js_limites`, `test_b4_view_transition`, `test_a11_sin_transition_all_ni_externos` |
| D7 inicio | T44 | `test_d7_inicio`, `test_v10_inicio_tarjetas` (conservada) |
| D8 lo que se quita de v1 | T37, T38 | `test_d8_sin_rastros_de_v1`; reescrituras de la tabla «Pruebas de v1» del plan |
| B1 | T36, T45 | `test_a1_estilos_servidos`, `test_a1_base_sin_style` (conservadas) |
| B2 | T37, T42 | `test_b2_*`; `tests/test_app_r5.py::test_sin_algoritmos_ni_js_propio`, `::test_inicio_y_menu` (reescritas) |
| B3 | T36 | `test_b3_motion_con_hash_y_licencia`, `test_b3_js_servidos` |
| B4 | T38, T39, T43 | `test_b4_*` |
| B5 | T38 | `test_b5_colores_de_metodos`, `test_b5_encabezados_de_metodo`, `test_a7_leyenda_con_colores` |
| B6 | T41 | `test_b6_contador_en_la_pagina` |
| B7 | T43 | `test_b7_control_segmentado` |
| B8 | T36–T45 (regresión), T45 | suite completa y `git diff` contra `BASE_B6` |
| B9 (manual) | T46 | `review.md` y `evidencias/r5/` |
| Sin tocar `servicios.py`, `datos.py`, `formato.py`, R1–R4, `requirements.txt`, `.gitignore`, `Dockerfile` | T36, T45 | `git status` / `git diff --stat` vacíos |

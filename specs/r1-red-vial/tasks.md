# Tareas — R1 Modelo de la red vial

Spec: `spec.md` · Plan: `plan.md`. Todas las órdenes se corren desde la raíz del repositorio (`/Users/santiagopolaniapinzon/proyecto-final-rutas-quindio`) con `.venv/bin/python`. Test primero en cada tarea: escribirlo, verlo fallar por la razón correcta, implementar, verlo pasar. Ninguna tarea hace `git add/commit/push`.

Cada tarea en la que se use IA termina con: **anotar en `docs/anexo-ia.md`** (fecha, herramienta, qué se generó, cómo se verificó).


> **Reglas del usuario para lo que falta:** (1) cada bloque termina con todas sus pruebas en verde y el trabajo se **detiene**: no se empieza el bloque siguiente hasta que el usuario haga su commit; (2) test primero **tarea por tarea**: escribir la prueba de una tarea, verla fallar por la razón correcta (módulo con `raise NotImplementedError` si hace falta, no un `ModuleNotFoundError` global) y solo entonces escribir su código; el reporte de cada bloque lo confirma.

> **Regla del usuario:** no modificar `.gitignore` sin preguntarle (debe conservar `docs/` y `.DS_Store`). `docs/` está ignorada: `docs/anexo-ia.md` se mantiene localmente; su versionado está pendiente de decisión del grupo. En T19, el README además debe avisar que si la descarga queda reintentando cada 55 s (504/429 de Overpass, reintento interno de OSMnx) se corta con Ctrl+C y se reintenta más tarde o se usa el Plan B.
## B1 · Base, memoria y catálogo (sin internet)

- [x] T1 · Base del proyecto: dependencias fijadas, configuración de pytest, paquete, constantes y `.gitignore`
  - Archivos: `requirements.txt` (osmnx==2.1.1, networkx==3.7, numpy==2.5.3, pandas==3.0.5, geopandas==1.2.0, pyproj==3.8.0, scipy==1.18.1, shapely==2.2.0, matplotlib==3.11.2, pytest==9.2.0, psutil==7.2.2, Flask==3.1.3, folium==0.20.0, requests==2.34.2), `pyproject.toml` (solo `[tool.pytest.ini_options]`: `pythonpath = ["."]`, `testpaths = ["tests"]`, `markers = ["red: usa la red real descargada y data/processed"]`), `rutas/__init__.py`, `rutas/r1/__init__.py`, `rutas/config.py` (incluye `UMBRAL_GZ_BYTES = 100_000_000`), `tests/conftest.py` (fábrica `grafo_sintetico(nodos, aristas)` con `crs = "epsg:4326"` y `x, y`; fixtures `grafo_procesado_real` y `red_radio_2km` que hacen `pytest.skip` si falta el archivo; `grafo_procesado_real` acepta `.graphml` o `.graphml.gz`), `.gitignore` (agregar `data/raw/`, `cache/`, `__pycache__/`, `.pytest_cache/`; conservar `estudio/`, `docs/` y `.DS_Store` como los dejó el grupo; **no** ignorar `data/processed/`), `docs/anexo-ia.md` (encabezado y tabla: fecha · integrante · herramienta · para qué · cómo se verificó)
  - Test primero: `tests/test_config.py::test_rutas_y_constantes` (existe `CATALOGO`; `EPSG_UTM == 32618`; `RADIOS_M == (2000, 5000, 10000, 20000)`; `UMBRAL_ALERTA_M == 500`; `UMBRAL_GZ_BYTES == 100_000_000`), `::test_fabrica_grafo_sintetico` (la fábrica produce un `MultiDiGraph` con `crs` y `x, y`), `::test_gitignore_excluye_data_raw` (`.gitignore` tiene la línea `data/raw/` y ninguna línea que ignore `data/processed`; sobre `docs/` no exige nada, su versionado está pendiente de decisión del grupo)
  - Verificar: `.venv/bin/python -m pytest tests/test_config.py && .venv/bin/pip check && git check-ignore data/raw/x.graphml && ! git check-ignore data/processed/x.graphml`

- [x] T2 · Estimación de memoria matriz vs listas para dos redes (punto 1; casos 1, 1b; Puerta 2)
  - Archivos: `rutas/r1/memoria.py` (`estimar_memoria`, `SUPUESTOS`, `filas_memoria(red, V, E)`)
  - Test primero: `tests/test_memoria.py::test_caso_1_v1000_e2500` (16 000 000 B / 16 MB; 68 000 B / 0,068 MB), `::test_caso_1b_v30000_e75000` (14 400 000 000 B / 14 400 MB; 2 040 000 B / 2,04 MB), `::test_bytes_son_enteros`, `::test_filas_memoria_dos_filas` (`filas_memoria("Red descargada", 1000, 2500)` → 2 dicts con claves exactas `red, V, E, representacion, supuesto, bytes, MB`, en orden Matriz de adyacencia y Listas de adyacencia; `red`, `V`, `E` repetidos en ambas; `bytes` = 16 000 000 y 68 000; `supuesto` no vacío)
  - Verificar: `.venv/bin/python -m pytest tests/test_memoria.py`

- [x] T3 · Carga y validación del catálogo (sección 4; caso 12 y bordes del catálogo)
  - Archivos: `rutas/r1/catalogo.py` (`CATEGORIAS`, `MINIMOS`, `RECUADRO`, `CatalogoInvalido`, `cargar_catalogo`, `validar_catalogo`)
  - Test primero: `tests/test_catalogo.py::test_caso_12_catalogo_real` (42 filas; conteos 12/15/9/6; ids únicos; 15 atractivos con duración > 0 y fuente "Criterio 1–4"; todas verificadas; Cocora lon −75,489 y PANACA −75,819 dentro), `::test_caso_12_id_repetido`, `::test_caso_12_categoria_invalida`, `::test_caso_12_latitud_fuera` (5,5), `::test_conteo_distinto`, `::test_atractivo_sin_duracion`, `::test_no_verificado`, `::test_mensaje_indica_fila_y_regla` (los sintéticos se arman copiando el catálogo real y alterando una celda, escritos a `tmp_path`)
  - Verificar: `.venv/bin/python -m pytest tests/test_catalogo.py`

## B2 · Pesos, componente y aristas paralelas (sin internet)

- [x] T4 · Velocidades y tiempos con la tabla del grupo (punto 2; casos 2, 3, 4, 4b y bordes de pesos)
  - Archivos: `rutas/r1/pesos.py` (`VELOCIDADES`, `maxspeed_original`, `agregar_pesos`, `verificar_velocidades`)
  - Test primero: `tests/test_pesos.py::test_caso_2_maxspeed_36_da_100s`, `::test_caso_3_maxspeed_30mph` (48,2802 km/h, ≈ 37,28 s ± 0,1), `::test_caso_4_tabla_por_tipo` (parametrizada: residential 120 s, primary 60 s, primary_link 60 s, track 180 s, grafo sin `maxspeed`), `::test_caso_4b_maxspeed_lista_y_none` (["30","50"] → 90 s; "none" + tertiary → 90 s), `::test_tabla_velocidades_completa` (16 claves, `*_link` = padre, road = 30), `::test_highway_lista_usa_primero`, `::test_longitud_cero_tiempo_cero`, `::test_tipo_fuera_de_tabla_se_imputa` (finito > 0), `::test_velocidad_invalida_lanza_error`, `::test_maxspeed_original` ("36" y ["30","50"] → True; "none", "signals", ausente → False), `::test_travel_time_formula_1e9` (`travel_time == length / (speed_kph / 3.6)` ± 1e-9)
  - Verificar: `.venv/bin/python -m pytest tests/test_pesos.py`
  - Nota: la tabla de la spec tiene 16 tipos, no 18 como decían el plan y estas tareas (error de conteo); la prueba verifica 16. Se agregaron `::test_marca_maxspeed_original_en_aristas` y `::test_resumen_highway_lista_usa_primero`.

- [x] T5 · Resumen de velocidades por tipo de vía (punto 2, porcentajes OSM/imputado)
  - Archivos: `rutas/r1/pesos.py` (`resumen_velocidades`)
  - Test primero: `tests/test_pesos.py::test_resumen_velocidades` (grafo sintético con 2 residential —una con `maxspeed`— y 1 primary sin él → residential 50 %/50 %, primary 0 %/100 %, Total 33,3 %/66,7 %; columnas `highway, aristas, con_maxspeed_osm, pct_osm, pct_imputado`)
  - Verificar: `.venv/bin/python -m pytest tests/test_pesos.py -k resumen`

- [x] T6 · Componente fuertemente conexa más grande (punto 3; casos 5, 6)
  - Archivos: `rutas/r1/componente.py` (`obtener_componente`, `contar`)
  - Test primero: `tests/test_componente.py::test_caso_5_componente_abc` (A→B, B→C, C→A, C→D, D→E → {A,B,C}, V = 3, E = 3, igual a `max(nx.strongly_connected_components(G), key=len)`), `::test_caso_6_ya_fuertemente_conexa` (ciclo → V = 3, E = 3), `::test_contar_incluye_paralelas`
  - Verificar: `.venv/bin/python -m pytest tests/test_componente.py`

- [x] T7 · `mejor_arista(G, u, v)` entre paralelas (precisión Puerta 1; caso 11b en memoria)
  - Archivos: `rutas/r1/aristas.py` (`AristaElegida`, `mejor_arista`)
  - Test primero: `tests/test_aristas.py::test_caso_11b_menor_tiempo` (clave 0: 50 s, 800 m; clave 1: 40 s, 900 m con `LineString` propia → clave 1, 40 s, 900 m y esa geometría), `::test_caso_11b_empate_menor_key`, `::test_caso_11b_sin_geometria_segmento_recto` (`LineString([(x_u, y_u), (x_v, y_v)])`), `::test_no_mezcla_atributos` (length, travel_time y geometry salen de la misma clave), `::test_sin_arista_lanza_keyerror`
  - Verificar: `.venv/bin/python -m pytest tests/test_aristas.py`

## B3 · UTM, ubicación de lugares y persistencia (sin internet)

- [x] T8 · Conversión a UTM 18N (punto 4; caso 10)
  - Archivos: `rutas/r1/utm.py` (`transformador`, `a_utm`, `a_latlon`, `agregar_utm_a_nodos`)
  - Test primero: `tests/test_utm.py::test_caso_10_catalogo_contra_pyproj` (C01, A03, A10 < 1 mm frente a `pyproj.Transformer` EPSG:4326 → EPSG:32618 creado en la prueba), `::test_caso_10_ida_y_vuelta` (< 1 m), `::test_caso_10_rango_recuadro` (esquinas del recuadro → x ∈ [389 000, 456 000], y ∈ [442 000, 542 000] aprox.; lon −75,6716, lat 4,5339 → (425 498, 501 177) ± 1 m), `::test_agregar_utm_a_nodos` (atributos `x_utm`, `y_utm` float)
  - Verificar: `.venv/bin/python -m pytest tests/test_utm.py`

- [x] T9 · Nodo más cercano por búsqueda lineal propia y asociación de lugares (punto 4; casos 7, 8, 9)
  - Archivos: `rutas/r1/ubicacion.py` (`nodo_mas_cercano`, `ubicar_lugares`)
  - Test primero: `tests/test_ubicacion.py::test_caso_7_vecino_mas_cercano` ((100,100); nodos 1 (103,104), 2 (200,100) → 1, 5,0 m, sin alerta), `::test_caso_8_alerta_y_frontera_500` (600 m → alerta; 500 m exactos → sin alerta), `::test_caso_9_empate_menor_id` (nodos 7 y 3 equidistantes → 3, probando ambos órdenes de la lista), `::test_lugar_sobre_nodo_distancia_cero`, `::test_ubicar_lugares_columnas_y_orden` (DataFrame `id_lugar, id_nodo, distancia_al_nodo_m, alerta_500m`, alertados conservados)
  - Verificar: `.venv/bin/python -m pytest tests/test_ubicacion.py`

- [x] T10 · Guardar y cargar el grafo procesado (`.graphml` o `.graphml.gz`) y las asociaciones sin redondear (punto 5; casos 4c, 11 sintético, 11b tras guardar/cargar; Puerta 2)
  - Archivos: `rutas/r1/persistencia.py` (`NOMBRE_GRAFO`, `guardar_grafo(G, carpeta, umbral_bytes=UMBRAL_GZ_BYTES)`, `cargar_grafo_procesado(carpeta)`, `guardar_procesado(..., umbral_bytes=...)`, `cargar_lugares_nodos`, `cargar_metadatos`)
  - Test primero: `tests/test_persistencia.py::test_caso_4c_paralelas_sobreviven` (A→B claves 0 y 1 con 50 s y 40 s, más B→A para que A y B formen la componente; tras `agregar_pesos` → `obtener_componente` → guardar/cargar siguen las 2 aristas A→B con sus tiempos; los tiempos de 4c se fijan con `length` y `maxspeed` que los producen), `::test_caso_11_guardar_cargar_sintetico` (mismos V, E; suma de `travel_time` ± 1e-6; `travel_time` y `length` arista por arista ± 1e-9; además igualdad exacta de `float`; `lugares_nodos.csv` idéntico tras cargar y volver a guardar), `::test_caso_11b_tras_guardar_cargar` (`mejor_arista` da lo mismo antes y después), `::test_tipos_al_cargar` (`x_utm`, `y_utm`, `length`, `speed_kph`, `travel_time` son `float`; `maxspeed_original` es `bool`; `id_nodo` es `int`), `::test_metadatos_ida_y_vuelta` (incluye `archivo_grafo` y `comprimido`), `::test_gz_y_sin_comprimir_dan_el_mismo_grafo` (el mismo grafo sintético con pesos se guarda en `tmp_path/a` con umbral por defecto → solo `.graphml`, y en `tmp_path/b` con `umbral_bytes=0` → solo `.graphml.gz`; cargar ambos con `cargar_grafo_procesado`: mismos nodos, mismas aristas `(u, v, key)`, `length`, `speed_kph`, `travel_time`, `x_utm`, `y_utm` ± 1e-9, mismos tipos), `::test_umbral_no_superado_no_comprime` (umbral mayor que el archivo → `.graphml`, sin `.gz`), `::test_nunca_quedan_las_dos_formas` (guardar comprimido y luego sin comprimir en la misma carpeta, y al revés → solo queda una forma), `::test_cargar_con_ambas_formas_es_error` (copiar a mano ambas formas → `ValueError`; carpeta vacía → `FileNotFoundError`), `::test_gz_reproducible` (guardar dos veces con `umbral_bytes=0` → `.gz` idénticos byte a byte, por `mtime=0`)
  - Verificar: `.venv/bin/python -m pytest tests/test_persistencia.py`

## B4 · Descarga real y pipeline de construcción

- [ ] T11 · Descargas con parámetros fijos, reintentos ante 502/504, comprobación del polígono y Plan B (sección 4, punto 1; casos 13 y 16; condición de la Puerta 2)
  - Archivos: `rutas/r1/descarga.py` (`LUGAR`, `PARAMETROS`, `centro_plaza_bolivar`, `comprobar_poligono_departamento`, `descargar_departamento`, `descargar_radio`, `cargar_red_cruda`, `con_reintentos(funcion, esperas=(30, 60, 120, 240), dormir=time.sleep)` y `codigo_http(error)`, que lee `e.response.status_code` o el código en el mensaje; reintenta solo 502/504, se rinde tras 4 reintentos con mensaje que sugiere el Plan B; toda llamada a OSMnx de descarga y geocodificación pasa por `con_reintentos`), `rutas/r1/descargar.py` (script: 5 descargas → `data/raw/*.graphml` + `data/raw/descarga.json` con fecha, versiones, parámetros, centro y polígono)
  - Test primero: `tests/test_descarga.py::test_caso_13_parametros_de_las_5_descargas` (`monkeypatch` de `osmnx.graph_from_place`, `osmnx.graph_from_point`, `osmnx.geocode_to_gdf` y `osmnx.save_graphml`; se ejecuta `descargar.main(carpeta=tmp_path)`; las 5 llamadas tienen `network_type="drive"` y `retain_all=True`; `dist` ∈ {2000, 5000, 10000, 20000}; `dist_type="bbox"`; centro = (lat, lon) de C01; falla si alguna usa los valores por defecto), `::test_poligono_municipio_falla` (`addresstype="city"` o área 120 km² → `ValueError`), `::test_poligono_departamento_ok`, `::test_cargar_graphml_docente` (un GraphML sintético guardado en `tmp_path` se carga con `cargar_red_cruda`), `::test_descarga_json_tiene_fecha_y_versiones`, `::test_caso_16a_502_dos_veces_luego_exito` (esperas [30, 60], 3 llamadas), `::test_caso_16b_502_siempre_se_rinde` (5 llamadas, esperas [30, 60, 120, 240], mensaje con "5 intentos" y "GraphML"), `::test_caso_16c_504_una_vez` (esperas [30]), `::test_caso_16d_otros_errores_no_se_reintentan` (400 y `ValueError` sin código → 1 llamada, sin esperas), `::test_caso_16e_script_reintenta_solo_la_red_que_fallo` (mock de `graph_from_point` con un 502 en `dist=5000` → 6 llamadas, 5 redes escritas). En todas, `dormir` es una función falsa que registra la espera: las pruebas no duermen
  - Verificar: `.venv/bin/python -m pytest tests/test_descarga.py`

- [ ] T12 · Pipeline `construir_red` y CSV de tamaños, memoria (dos redes) y velocidades (puntos 1, 2, 4, 5)
  - Archivos: `rutas/r1/construir_red.py` (`main(raw=..., graphml=None, catalogo=..., salida_processed=..., salida_results=..., umbral_gz=UMBRAL_GZ_BYTES)`: cargar red cruda o `--graphml`; `cargar_catalogo`; `agregar_pesos`; `contar` antes; `obtener_componente`; `contar` después; `agregar_utm_a_nodos`; `ubicar_lugares`; `guardar_procesado(..., umbral_bytes=umbral_gz)`; escribir `r1_tamanos.csv`, `r1_memoria.csv` = `filas_memoria("Red descargada", V_antes, E_antes) + filas_memoria("Componente fuertemente conexa", V_despues, E_despues)`, `r1_velocidades.csv`; imprimir lugares con alerta, ruta y tamaño del grafo guardado y si quedó comprimido)
  - Test primero: `tests/test_construir_red.py::test_pipeline_sintetico_escribe_salidas` (red cruda sintética con coordenadas en el Quindío, con una parte no fuertemente conexa, guardada en `tmp_path`; catálogo real; existen el grafo, `lugares_nodos.csv`, `metadatos.json` y los 3 CSV; columnas y nombres de fila del plan; `V_antes > V_despues`), `::test_memoria_cuatro_filas_dos_redes` (`r1_memoria.csv` con columnas exactas `red, V, E, representacion, supuesto, bytes, MB`; 4 filas en el orden del plan; `V, E` de "Red descargada" = `V_antes, E_antes` de `metadatos.json` y de "Componente fuertemente conexa" = `V_despues, E_despues`; `bytes` = `estimar_memoria` de cada par), `::test_pipeline_con_graphml` (`--graphml` → `metadatos["fuente"] == "GraphML del docente"`), `::test_alertas_se_conservan` (42 filas en `lugares_nodos.csv` aunque haya alertas), `::test_pipeline_comprime_si_supera_umbral` (`umbral_gz=0` → queda `grafo_componente.graphml.gz`, `metadatos["comprimido"] is True`, y `cargar_grafo_procesado` lo lee)
  - Verificar: `.venv/bin/python -m pytest tests/test_construir_red.py`

- [ ] T13 · Ejecutar la descarga y la construcción reales (requiere internet; punto 5)
  - Archivos: genera `data/raw/*` (ignorado por git) y `data/processed/*`, `results/r1/r1_tamanos.csv`, `r1_memoria.csv`, `r1_velocidades.csv` (no se edita código)
  - Test primero: no aplica (es la ejecución que alimenta T14); el criterio es T14
  - Verificar: `.venv/bin/python -m rutas.r1.descargar && .venv/bin/python -m rutas.r1.construir_red`; revisar en `data/processed/metadatos.json` la fecha de descarga, `addresstype = "state"`, V/E antes y después y `comprimido`; `ls -lh data/processed/` muestra **una sola** forma del grafo (`.graphml` < 100 MB, o `.graphml.gz`) y anotar su tamaño en el reporte; `git status --short data/` no lista nada bajo `data/raw/`; `r1_memoria.csv` tiene 4 filas. Solo si el `.gz` aun así pasa de 100 MB, reportarlo al usuario. Si la descarga falla: `--graphml <ruta del docente>` y copiar ese archivo a `data/raw/departamento.graphml`

- [ ] T14 · Pruebas con la red real (casos 11 real, 14, 15 y componente en radio 2 km)
  - Archivos: `tests/test_red_real.py` (todas con `@pytest.mark.red`)
  - Test primero: `tests/test_red_real.py::test_caso_14_velocidades_y_tiempos` (toda arista `speed_kph` finito > 0 y `travel_time == length / (speed_kph / 3.6)` ± 1e-6), `::test_caso_15_asociacion_contra_ckdtree` (42 lugares con nodo de la componente; distancia propia = `cKDTree.query` < 1e-6 m), `::test_componente_radio_2km_igual_a_networkx` (nodos de `obtener_componente` = mayor de `nx.strongly_connected_components` sobre `data/raw/radio_2km.graphml`), `::test_caso_11_guardar_cargar_real` (cargar el procesado con `cargar_grafo_procesado(DATA_PROCESSED)` —sirve con cualquiera de las dos formas—, guardarlo en `tmp_path` con el mismo umbral, volver a cargar: V, E, suma de `travel_time` ± 1e-6, arista por arista ± 1e-9; `lugares_nodos.csv` idéntico), `::test_metadatos_antes_despues` (V y E de `metadatos.json` = los del grafo cargado; `comprimido` coincide con la forma presente en disco), `::test_memoria_real_coincide_con_tamanos` (las `V, E` de `r1_memoria.csv` son las de `r1_tamanos.csv` para cada red)
  - Verificar: `.venv/bin/python -m pytest -m red`

## B5 · Medición y tablas (sección 6)

- [ ] T15 · Cronómetro modo (a), mismo proceso: mediana, una repetición si > 1 min, preparación fuera (sección 6; Puerta 2)
  - Archivos: `rutas/medicion.py` (`ResultadoMedicion`, `medir_en_proceso(funcion, preparar, repeticiones=5, umbral_una_s=60.0, limite_s=300.0)`, `info_maquina`)
  - Test primero: `tests/test_medicion.py::test_en_proceso_cinco_repeticiones_y_mediana` (`time.sleep`, `preparar=lambda: (0.02,)` → 5 repeticiones, `completada`, mediana entre 18 y 60 ms), `::test_en_proceso_una_sola_repeticion_si_supera_umbral` (`umbral_una_s=0.05`, sleep 0,1 s → `repeticiones == 1`), `::test_en_proceso_preparar_fuera_del_cronometro` (`preparar` que duerme 0,3 s y función trivial → mediana < 100 ms), `::test_en_proceso_preparar_en_cada_repeticion` (contador → `preparar` se llama 5 veces y la función recibe cada vez un objeto distinto), `::test_en_proceso_no_completada_si_supera_limite` (`limite_s=0.05`, `umbral_una_s=0.01`, sleep 0,1 s → `completada is False`, `tiempo_ms is None`, `repeticiones == 0`), `::test_info_maquina_tiene_campos` (`procesador, ram_gb, so, python`)
  - Verificar: `.venv/bin/python -m pytest tests/test_medicion.py -k "en_proceso or info_maquina"`

- [ ] T15b · Cronómetro modo (b), proceso hijo con límite de 5 min (sección 6; Puerta 2; lo usarán R2 lineal y R4)
  - Archivos: `rutas/medicion.py` (`_cronometrar_en_hijo(funcion, args, cola)` de nivel de módulo; `medir_en_hijo(funcion, args=(), repeticiones=5, umbral_una_s=60.0, limite_s=300.0)` con contexto `spawn`, `Queue`, `join(timeout=limite_s)`, `terminate()`; código corto y comentado: es material de sustentación)
  - Test primero: `tests/test_medicion.py::test_en_hijo_no_incluye_arranque_del_proceso` (`medir_en_hijo(time.sleep, (0.05,), repeticiones=1)` → `45 <= tiempo_ms <= 150`, aunque el tiempo de pared de la llamada medido por la prueba sea mayor), `::test_en_hijo_no_completada_si_supera_limite` (`time.sleep`, `(3,)`, `limite_s=0.5` → `completada is False`, `tiempo_ms is None`, `repeticiones == 0`, y la llamada vuelve en menos de 2,5 s: el hijo se terminó), `::test_en_hijo_cinco_repeticiones_y_mediana` (sleep 0,02 s → 5 repeticiones, mediana entre 18 y 60 ms), `::test_en_hijo_una_sola_repeticion_si_supera_umbral` (`umbral_una_s=0.05`, sleep 0,1 s → `repeticiones == 1`), `::test_en_hijo_error_en_el_hijo` (`math.sqrt`, `(-1,)` → `RuntimeError`, sin esperar al límite)
  - Verificar: `.venv/bin/python -m pytest tests/test_medicion.py -k en_hijo`

- [ ] T16 · Script de medición de `largest_component` en el mismo proceso (punto 3, sección 6)
  - Archivos: `rutas/r1/medir_componente.py` (`fila_tiempos(nombre, V, E, resultado) -> dict`; `preparar_copia(G)` → función sin argumentos que devuelve `(G.copy(),)`; `main(raw=..., salida=...)`: para cada red cruda la carga una vez y cuenta V y E fuera del cronómetro, llama `medir_en_proceso(obtener_componente, preparar_copia(G))`, escribe `r1_tiempos_componente.csv` y `maquina.json`)
  - Test primero: `tests/test_medir_componente.py::test_fila_tiempos_calcula_us_por_elemento` (`tiempo_por_elemento_us = tiempo_ms · 1000 / (V + E)`), `::test_fila_no_completada` (`tiempo_ms == "no completada"`, `repeticiones == 0`), `::test_preparar_copia_da_grafo_nuevo` (dos llamadas → objetos distintos, iguales en nodos y aristas al original; modificar la copia no toca el original), `::test_main_con_redes_sinteticas` (5 GraphML sintéticos pequeños en `tmp_path` con los nombres del plan → CSV con columnas `red, V, E, V_mas_E, tiempo_ms, tiempo_por_elemento_us, repeticiones`, 5 filas en orden Radio de 2 km … Departamento completo, `repeticiones == 5`, `maquina.json` presente), `::test_main_usa_modo_mismo_proceso` (`monkeypatch` de `medir_en_hijo` para que falle si se llama → `main` termina bien)
  - Verificar: `.venv/bin/python -m pytest tests/test_medir_componente.py`

- [ ] T17 · Tablas Markdown generadas desde los CSV
  - Archivos: `rutas/r1/tablas.py` (`a_markdown(df) -> str`; `main(results=..., processed=..., catalogo=...)` → `results/r1/tablas_r1.md` con: tamaños antes/después; tiempos (ms) y µs por elemento; memoria con columnas red, V, E, representación, supuesto, B y MB (4 filas, dos redes); velocidades (%); lugares con `alerta_500m` con nombre y distancia (m))
  - Test primero: `tests/test_tablas.py::test_tablas_salen_de_los_csv` (CSV pequeños escritos en `tmp_path` → cada valor aparece en el Markdown), `::test_unidades_en_encabezados` ("(ms)", "(µs)", "(MB)", "(m)"), `::test_memoria_muestra_ambas_redes` (la tabla de memoria tiene 4 filas con "Red descargada" y "Componente fuertemente conexa", cada una con matriz y listas, y sus V y E), `::test_tabla_alertas_solo_alertados`, `::test_no_completada_se_muestra`
  - Verificar: `.venv/bin/python -m pytest tests/test_tablas.py`

- [ ] T18 · Ejecutar la medición real y generar las tablas
  - Archivos: genera `results/r1/r1_tiempos_componente.csv`, `results/r1/maquina.json`, `results/r1/tablas_r1.md`
  - Test primero: no aplica (usa T15–T17 ya verificados)
  - Verificar: `.venv/bin/python -m rutas.r1.medir_componente && .venv/bin/python -m rutas.r1.tablas`; revisar que haya 5 filas, que `tiempo_por_elemento_us` sea del mismo orden entre filas y anotar en el reporte si alguna red ya era fuertemente conexa o fue "no completada". Correr con la máquina enchufada y sin otros procesos pesados

## Cierre

- [ ] T19 · Documentación de uso de IA y reproducción de R1
  - Archivos: `docs/anexo-ia.md` (entradas de R1: plan y tareas generados con Claude Code —agente planner—, código y pruebas generados con el implementer; cómo se verificó cada parte: casos a mano 1–9, `pyproj`, `cKDTree`, `nx.strongly_connected_components`, ida y vuelta de GraphML y `.gz`, pruebas sintéticas del cronómetro), `README.md` (sección "Reproducir R1": `pip install -r requirements.txt`, los 4 comandos y `pytest`; nota de que `data/raw/` no está en git y se regenera con `rutas.r1.descargar`, y de que el grafo puede estar como `.graphml.gz`)
  - Test primero: no aplica (documentación)
  - Verificar: `grep -n "R1" docs/anexo-ia.md && grep -n "rutas.r1.construir_red" README.md`
  - anotar en `docs/anexo-ia.md`

- [ ] T20 · Suite completa y regeneración de todos los resultados de R1
  - Archivos: ninguno nuevo (regenera `data/processed/*` y `results/r1/*` desde `data/raw/`)
  - Test primero: no aplica
  - Verificar: `.venv/bin/python -m rutas.r1.construir_red && .venv/bin/python -m rutas.r1.medir_componente && .venv/bin/python -m rutas.r1.tablas && .venv/bin/python -m pytest` (todas pasan, ninguna `red` saltada); comprobar que `results/r1/` tiene `r1_tamanos.csv`, `r1_tiempos_componente.csv`, `r1_memoria.csv` (4 filas), `r1_velocidades.csv`, `maquina.json`, `tablas_r1.md`, y que `data/processed/` tiene una sola forma del grafo

## Cobertura

| Caso / punto | Tarea |
|---|---|
| 1, 1b | T2 |
| Memoria con dos redes (Puerta 2) | T2, T12, T14, T17 |
| 2, 3, 4, 4b | T4 |
| 4c | T10 |
| 5, 6 | T6 |
| 7, 8, 9 | T9 |
| 10 | T8 |
| 11 | T10 (sintético, `.graphml` y `.gz`), T14 (real) |
| 11b | T7, T10 |
| 12 | T3 |
| 13 | T11 |
| 16 (reintentos 502/504, Puerta 2) | T11, T13 |
| 14, 15, componente radio 2 km | T14 |
| `data/raw/` fuera de git, `data/processed/` versionado (Puerta 2) | T1, T13 |
| R1 punto 1 (memoria y elección) | T2, T12, T17 |
| R1 punto 2 (pesos y velocidades) | T4, T5, T12, T14 |
| R1 punto 3 (componente y tiempos) | T6, T14, T16, T18 |
| R1 punto 4 (ubicación, alertas) | T8, T9, T12, T14, T17 |
| R1 punto 5 (grafo procesado, V/E antes y después) | T10, T12, T13, T14 |
| Sección 4 (catálogo, fecha de descarga) | T3, T11, T13 |
| Sección 6 (protocolo; cronómetro en dos modos) | T15, T15b, T16, T17, T18 |
| Anexo de IA | T19 (y cada tarea con IA) |

# Revisión — R5 Aplicación (Flask + Folium)

## Ronda 1: APROBADO

Fecha: 2026-11-12. Revisor: agente reviewer (Claude Code). Se revisó B1–B3 con commit (33f684f, 3e0973b, 75a3a02) y B4 en el árbol de trabajo sin commit (`Dockerfile`, `tests/test_dockerfile_r5.py`, `README.md`, `tasks.md`).

Pruebas: ✅ (las corrió el revisor)
- `.venv/bin/python -m pytest`: **536 pasan, 3 se saltan** (16,3 s).
- `-m "not red"`: **497 pasan, 1 se salta**, 41 deseleccionadas.
- `-m red -rs`: **39 pasan, 2 se saltan**: `test_red_real.py:79` (falta `data/raw/radio_2km.graphml`) y `test_red_real_r4.py:126` (falta `r4_exactas.csv`). Ninguna de las dos es de R5; las `red` de R5 corren todas.
- Solo R5 (`tests/test_*r5*.py` y `test_config.py`): 105 pasan.
- `git diff 623f807 -- rutas/r1 rutas/r2 rutas/r3 rutas/r4 requirements.txt .gitignore`: vacío, tanto contra el commit como en el árbol de trabajo. Fuera de `rutas/r5` solo cambian `rutas/config.py` (3 constantes al final), `tests/conftest.py` (fixture sintético al final) y `tests/test_config.py`.

| Caso / punto del enunciado | Cumplido | Test |
|---|---|---|
| 1 Ruta real C01→C12 = 1 783,39 s = `M.loc`, extremos, `detalle_ruta`, coordenada inicial, explorados; C12→C01 = 1 708,19 s | ✅ | `tests/test_red_real_r5.py::test_caso_1_ruta_real`, `::test_caso_1_asimetria` |
| 2 `/ruta?origen=C01&destino=C12` → 200, «29,7» y `leaflet` | ✅ | `tests/test_red_real_r5.py::test_caso_2_ruta_en_la_app` |
| 3 Origen = destino: tiempo 0, aviso, sin línea (sintético y real) | ✅ | `tests/test_servicios_r5.py::test_caso_3_mismo_lugar`, `tests/test_app_r5.py::test_caso_3_ruta_mismo_lugar`, `tests/test_mapas_r5.py::test_mapa_ruta_sin_linea`, `tests/test_red_real_r5.py::test_caso_3_*` |
| 4 Mismo nodo T03/T05 (y A02/A06 sintético) → 0 y aviso | ✅ | `tests/test_red_real_r5.py::test_caso_4_mismo_nodo`, `tests/test_servicios_r5.py::test_mismo_punto_sintetico` |
| 5 Itinerario que cabe (178,66 / 190,45 / 11,79 / 6,60 %, recorridos, 240 min, jornadas, sin regla) | ✅ | `tests/test_red_real_r5.py::test_caso_5_itinerario_cabe` |
| 6 Itinerario que no cabe: quita A01 y A12, 613,13 min = `r4_itinerario.json` | ✅ | `tests/test_red_real_r5.py::test_caso_6_itinerario_no_cabe`, `::test_itinerario_no_cabe_en_la_app` |
| 7 Tramos con Dijkstra = `M.loc[desde, hasta]` ± 1e-6 s; suma = desplazamiento (HK y voraz) | ✅ | `tests/test_red_real_r5.py::test_caso_7_tramos[held_karp|voraz]`, `tests/test_servicios_r5.py::test_tramos_igual_a_matriz_sintetico` |
| 8 Validación (5, 9, repetido, partida entre atractivos, `C02`, partida desconocida, 0) → 400 sin llamar a `resolver_por_ids` | ✅ | `tests/test_app_r5.py::test_caso_8_itinerario_400` (7 variantes, contador en 0), `tests/test_servicios_r5.py::test_caso_8_validacion` |
| 9 `/itinerario` real → «178,7», «190,4», «11,8» | ✅ | `tests/test_red_real_r5.py::test_caso_9_itinerario_en_la_app` |
| 10 Envolvente: sintética «4 vértices» con sus 4 coordenadas; real «14 vértices» y «1 631,5» | ✅ | `tests/test_app_r5.py::test_caso_10_envolvente`, `tests/test_mapas_r5.py::test_mapa_envolvente`, `tests/test_red_real_r5.py::test_caso_10_envolvente_real` |
| 11 Resultados: r2 con PNG y `r2_cociente.csv`; r4 sin exactas → aviso con `python -m rutas.r4.medir_exactas`; r1..r4 reales → 200 | ✅ | `tests/test_app_r5.py::test_caso_11_*`, `tests/test_servicios_r5.py::test_caso_11_resultados_sinteticos`, `::test_lista_fija_existe_en_results` |
| 12 Archivos protegidos: PNG 200 `image/png`; `..%2F..%2FCLAUDE.md`, `otro.png`, CSV, `r9` → 404 | ✅ | `tests/test_app_r5.py::test_caso_12_imagen_permitida`, `::test_caso_12_rechazos` |
| 13 `DatosFaltantes` con archivo y comando; `main` → 1 sin traza | ✅ | `tests/test_datos_r5.py::test_caso_13_carpeta_vacia`, `::test_cada_faltante_con_su_comando`, `tests/test_app_r5.py::test_caso_13_main_sin_datos` |
| 14 Carga única (contadores de `cargar_datos` y `cargar_grafo_procesado` en 0 tras 6 peticiones) | ✅ | `tests/test_app_r5.py::test_caso_14_carga_unica` |
| 15 Coordenadas siguen la geometría curva, en (lat, lon), sin duplicar uniones | ✅ | `tests/test_servicios_r5.py::test_caso_15_geometria_curva`, `::test_sin_duplicar_uniones`, `::test_segmento_recto_sin_geometria` |
| 16 Arranque siguiendo el README (manual) | ✅ con `curl` / ⏳ navegador | Comprobación manual (abajo) |
| 17 Docker (opcional, manual) | ✅ con `curl` / ⏳ navegador | `tests/test_dockerfile_r5.py::test_dockerfile` (estructura) y comprobación manual (abajo) |
| Borde: id desconocido → 400 «lugar desconocido: X» | ✅ | `tests/test_app_r5.py::test_ruta_lugar_desconocido`, `tests/test_servicios_r5.py::test_lugar_desconocido` |
| Borde: parámetros incompletos → solo el formulario | ✅ | `tests/test_app_r5.py::test_ruta_incompleta`, `::test_itinerario_sin_parametros` |
| Borde: 6 que caben sin bloque / no cabe con regla | ✅ | `tests/test_app_r5.py::test_itinerario_bloque_regla_*` |
| Borde: puerto ocupado → mensaje con `--puerto`, código 1 | ✅ | `tests/test_app_r5.py::test_puerto_ocupado` |
| Enunciado R5: ruta e itinerario calculados en el momento con Dijkstra con cola, Held-Karp y voraz | ✅ | `servicios.py:53` (`consultar(..., "cola_prioridad")`), `:98` (tramos), `:108` (`resolver_por_ids` con `held_karp` y `vecino_mas_cercano`). La matriz solo se usa como entrada del TSP, no para la ruta |
| Enunciado R5.1: elegir origen y destino y ver la ruta en un mapa con su tiempo | ✅ | casos 1–4 |
| Enunciado R5.1: envolvente sobre el mapa del departamento | ✅ | caso 10 |
| Enunciado R5.1: partida (por defecto Armenia = C01) y 6 a 8 atractivos; HK y voraz con tiempo total y diferencia | ✅ | casos 5–9, `test_itinerario_sin_parametros` (C01 seleccionado) |
| Enunciado R5.1: gráficas y tablas de R1 a R4 | ✅ | caso 11 |
| Enunciado R5 y secciones 7 y 8: ejecutable localmente con el README; Docker opcional | ✅ / ⏳ navegador | casos 16 y 17 |
| Sin algoritmos nuevos ni JavaScript propio | ✅ | `tests/test_app_r5.py::test_sin_algoritmos_ni_js_propio` y el `grep` del revisor (sin `heapq`, `networkx`, `scipy`, `shapely`, `itertools`, `osmnx` en `rutas/r5/*.py`; ningún `<script` en las plantillas) |

### Comprobaciones propias del revisor

**Seguridad de `/resultados/<r>/archivo/<nombre>`** (cliente de pruebas con los datos y `results/` reales). Dan 404:
- `../../CLAUDE.md`;
- `..%2F..%2FCLAUDE.md` y `%2e%2e%2f%2e%2e%2fCLAUDE.md`;
- `..%5c..%5cCLAUDE.md` y `%2Fetc%2Fpasswd`;
- `r2_tiempo_vs_explorados.png%00.txt` y la versión en mayúsculas;
- la PNG de r2 pedida bajo r1;
- las PNG faltantes de r1 y r4;
- `r2_cociente.csv`, `maquina.json`, `/resultados/__class__`, `/resultados/R2` y `/resultados/r9`.

`/resultados/..%2F/archivo/CLAUDE.md` da 308 (Werkzeug junta las barras) y al seguir la redirección da 404. Solo las dos PNG de la lista fija que existen dan 200 con `image/png`. La lista blanca (`app.py:81-83`) es la defensa real.

**Validación y escape.**
- `origen=<script>alert(1)</script>` → 400 «lugar desconocido: &lt;script&gt;…» (escapado por Jinja).
- Un atractivo `<b>x</b>` → 400 escapado.
- `partida=C01` sin casillas → 400 «elige entre 6 y 8 atractivos (llegaron 0)».
- Ids en minúscula (`c01`, `a05`) → 400 con el mensaje.
- `partida=` vacío → solo el formulario.
- Partida que es un atractivo no elegido (A01) y partida T03 con 8 atractivos → 200; en el segundo caso se aplica la regla y termina en 586,4 min.

Todos los mensajes están en español.

**Coma decimal.** Se ve en ruta, itinerario, envolvente y tablas de resultados (3 decimales). En `main` aparece como «Datos cargados en 0,4 s (8 791 nodos)».

**`main` falla limpio** (corrido como proceso real sobre una copia del repo en el scratchpad):
- Sin `matriz_tiempos.csv` ni `envolvente.geojson`: imprime dos líneas «falta …: .venv/bin/python -m rutas.r2.matriz» y «… rutas.r3.archivos» y sale con código 1, sin traza.
- Con el puerto ocupado por un socket en escucha: «el puerto N está ocupado; prueba con --puerto N+1» y sale con código 1, sin traza.

**Faltantes conocidos** (no son de R5), con su aviso:
- `/resultados/r1`: 4 tablas y el aviso de `r1_tiempos_componente.png` con `.venv/bin/python -m rutas.r1.tablas`.
- `/resultados/r4`: 3 tablas y los avisos de `r4_tiempo_vs_k.png` (`rutas.r4.tablas`) y de `r4_exactas.csv` (`rutas.r4.medir_exactas`).

Ninguno da error 500.

**Mutaciones** (13, sobre una copia del repo en el scratchpad; el árbol del usuario no se tocó). Todas las detectó la suite de R5:

| Mutación | Prueba que falla |
|---|---|
| M1: invertir origen y destino en `consultar` | `test_ruta_sintetica_app` |
| M2: no omitir el punto de unión | `test_sin_duplicar_uniones` |
| M3: el voraz usa `held_karp` | `test_itinerario_cabe_sintetico[voraz]` |
| M4: aceptar 5 atractivos | `test_caso_8_itinerario_400` |
| M5: quitar la lista blanca de imágenes | `test_caso_12_rechazos[r2_cociente.csv]` |
| M6: brecha con la base del voraz | `test_caso_5_itinerario_cabe` |
| M7: sin coma decimal | `test_caso_3_ruta_mismo_lugar` |
| M8: sin el aviso de mismo nodo | `test_mismo_punto_sintetico` |
| M9: no aplicar nunca la regla de las 11 h | `test_itinerario_bloque_regla_si_no_cabe` |
| M10: `main` devuelve 0 cuando faltan datos | `test_caso_13_main_sin_datos` |
| M11: no comprobar el puerto | `test_puerto_ocupado` |
| M12: permitir repetidos | `test_caso_8_itinerario_400[repetido]` |
| M13: `cabe` siempre falso | `test_itinerario_bloque_regla_no_aparece_si_cabe` |

**Caso 16, arranque con el README** (revisor, 2026-11-12, `.venv` existente, `curl`, sin navegador):
- `.venv/bin/python -m rutas.r5.app --puerto 5089` imprime «Datos cargados en 0,4 s (8 791 nodos)» y «Abre http://127.0.0.1:5089».
- `/resultados/r1` → 200.
- `/ruta?origen=C12&destino=C01` → «28,5 min».

Se usó otro puerto para no chocar con nada del usuario. El proceso se detuvo por PID: lanzado en segundo plano, no recibió el SIGINT, igual que anotó el implementer; con Ctrl+C en primer plano el comportamiento es el normal de Flask. Los pasos de T23 que registró el implementer coinciden con lo comprobado aquí con el cliente de pruebas.

**Caso 17, Docker** (revisor, imagen `rutas-quindio` ya construida, `docker run -d --rm -p 127.0.0.1:5088:5050`):
- Imprime «Datos cargados en 0,6 s (8 791 nodos)» y «Abre http://0.0.0.0:5050».
- `/` → 200.
- `/ruta?origen=C01&destino=C12` → 200 con «29,7».
- `/envolvente` → 200 con «14 vértices».
- `/itinerario` del caso 5 → 200 con «178,7», «190,4» y «11,8».
- `/resultados/r4` → 200 con el aviso `medir_exactas`.
- La PNG de r2 → 200; `..%2F..%2FDockerfile` → 404.

El contenedor se detuvo y se borró. No se tocaron los otros contenedores del usuario.

**Legibilidad.** El código es corto y está separado por capas (`datos`, `servicios`, `formato`, `mapas`, `app` y 6 plantillas de 10 a 49 líneas). Cada función tiene un docstring que explica el porqué, por ejemplo la omisión del punto de unión o la conversión de `numpy.int64` a `int`. Las plantillas usan solo `for`, `if` y el filtro `num`. Cualquier integrante puede explicarlas.

**Anexo de IA.** `docs/anexo-ia.md` (local, ignorado por `.gitignore`) tiene entradas para la spec, B1, B2, B3 y B4 y el resumen de R5, con herramienta, propósito y verificación.

### Bloqueantes
Ninguno.

### Sugerencias (no bloquean)
1. `rutas/r5/templates/ruta.html:19`: el resultado muestra solo «C01 → C12». La spec («Salidas en pantalla: … ids y nombres de origen y destino») pide también los nombres. Hoy el nombre solo aparece en la opción seleccionada del `<select>` y en el tooltip del mapa. Bastaría con pasar `nombre_de` a la plantilla, como hace `/itinerario`. Además, `tests/test_app_r5.py:66` comprueba «Atractivo Dos» en el HTML, pero ese texto ya sale de las `<option>` del formulario, así que la aserción no verifica el resultado. Conviene buscarlo dentro del `<h2>`.
2. `specs/r5-aplicacion/tasks.md`, T23, paso 6: dice «polígono con los lugares como marcadores», y el implementer ya advirtió que la página no dice «42 lugares». Hay que alinear el texto del paso con la spec del caso 10 (vértices y área) para que el usuario no lo marque como fallo al revisar en el navegador.
3. `README.md:187-188`: en *Itinerario* conviene decir «de 6 a 8 atractivos» y «por defecto Armenia (C01)», que son las palabras del enunciado. En el bloque de entorno conviene aclarar que `python3.13` debe estar instalado (la nota de Homebrew está en la línea 174, pero no dice cómo instalarlo).
4. `rutas/r5/mapas.py:25-28`: los marcadores usan la coordenada del catálogo y la línea empieza en el nodo de la red. Entre los dos puede haber hasta `distancia_al_nodo_m` (un hueco visible si se acerca mucho el mapa). No es un error, pero hay que saber explicarlo en la sustentación. Un `folium.PolyLine` corto del lugar al nodo, o una línea en el texto de la página, lo aclararía.
5. `specs/r5-aplicacion/spec.md:3`: el «Estado» sigue en ☐ pruebas · ☐ código · ☐ verificado. Lo actualiza el coordinator: ☑ pruebas y ☑ código; «verificado» cuando el usuario cierre lo del navegador.
6. Commit pendiente: B4 (`Dockerfile`, `tests/test_dockerfile_r5.py`, `README.md`, `tasks.md`) y este `review.md` están sin commit.

### Pendiente del usuario (navegador, no automatizable)
- Caso 16: en una terminal **nueva**, seguir solo la sección «Ejecutar la aplicación (R5)» del README y abrir `http://127.0.0.1:5050`. Comprobar:
  - el inicio con los 4 enlaces;
  - Ruta C01→C12, que la línea siga las vías y el tiempo sea 29,7 min; C12→C01 = 28,5 min; C01→C01 con el aviso;
  - Itinerario del caso 5, que el control de capas alterne Held-Karp y voraz y los marcadores numerados salgan en orden; el caso 6 con el bloque de la regla (A01, A12, 613,1 min); 5 casillas con el mensaje de error;
  - Envolvente: que el polígono y los lugares se vean;
  - Resultados r1..r4: que las imágenes y las tablas se vean bien, y los avisos de r1 y r4.
- Caso 17 en el navegador: `docker run --rm -p 5050:5050 rutas-quindio` y repetir Ruta y Envolvente.
- Anotar aquí la fecha, quién lo hizo, el navegador y el resultado de cada paso.

### Pendiente para el documento técnico
- Diagrama de arquitectura (sección 7.1): cómo pasan los datos de R1 (grafo, lugares), R2 (adyacencia, matriz), R3 (GeoJSON) y R4 (Held-Karp, voraz, regla) hasta `DatosApp` y las rutas de Flask.
- Capturas de las cuatro secciones (Ruta, Envolvente, Itinerario con las dos capas, Resultados).
- El comando de arranque (`.venv/bin/python -m rutas.r5.app`) y la alternativa con Docker.
- Una frase de complejidad que remita a R2 y R4 (la app no agrega algoritmos) y aclare que los `computo_ms` de la pantalla son informativos y no son la medición del protocolo.
- Pendientes de otros requerimientos que la app ya avisa: la medición real de R4 (`r4_exactas.csv`, `r4_tiempo_vs_k.png`, «Reproducir R4» en el README) y la gráfica de R1 (`r1_tiempos_componente.png`).

## Ronda 2: ajuste visual (B5): APROBADO

Fecha: 2026-11-12. Revisa el commit `1e27b50` (B5, T25 a T34) más el cambio sin commit de `tests/test_app_r5.py` (simulación de `puerto_libre`). El veredicto cubre lo automatizable. **A10 (T35, revisión manual en el navegador) queda pendiente del usuario** y no se da por hecha.

Pruebas: ✅ (corridas por el revisor, con la instancia del usuario escuchando en 5050)
- `.venv/bin/python -m pytest -m "not red"` → 541 pasan, 1 se salta, 41 deseleccionadas (8,6 s). `test_puerto_por_defecto` y `test_main_arranca` pasan aunque el 5050 esté ocupado.
- `.venv/bin/python -m pytest -m red -rs` → 39 pasan, 2 se saltan (los conocidos: `tests/test_red_real.py:79`, falta `radio_2km.graphml`; `tests/test_red_real_r4.py:126`, falta `r4_exactas.csv`). Las `red` de R5 corren todas.
- `tests/test_visual_r5.py` → 44 pasan.

**No-regresión.** `git diff dfe3b60 -- tests/test_app_r5.py tests/test_red_real_r5.py tests/test_mapas_r5.py` muestra solo las 2 líneas nuevas de `_main_con_run_falso` (`tests/test_app_r5.py:242-243`), que simulan `rutas.r5.app.puerto_libre` con `True`. Solo la usan `test_main_arranca` y `test_puerto_por_defecto`. `test_puerto_ocupado` (línea 227) no pasa por ahí y sigue ocupando un socket real, así que el caso «puerto ocupado → 1» sigue probado de verdad. `main` llama a `puerto_libre` por nombre global (`app.py:211`), por lo que la simulación sí tiene efecto. No se debilitó ninguna aserción: siguen «29,7», «178,7», «190,4», «11,8», «14 vértices» y «1 631,5».

**Archivos prohibidos.** `git diff --stat dfe3b60` sobre `rutas/r5/servicios.py`, `datos.py`, `formato.py`, `rutas/r1..r4`, `requirements.txt`, `.gitignore` y `Dockerfile` sale vacío. En `mapas.py` solo cambia la línea de `COLORES` (`mapas.py:8`).

| Caso / punto de la spec | Cumplido | Test |
|---|---|---|
| A1 hoja servida, sin `<style>` | ✅ | `tests/test_visual_r5.py::test_a1_estilos_servidos`, `::test_a1_base_sin_style` |
| A2 viewport, saltar, `id="contenido"` (12 URLs, incluidas las 400) | ✅ | `::test_a2_viewport_y_saltar` |
| A3 un solo `aria-current="page"` y en el enlace correcto | ✅ | `::test_a3_aria_current`, `::test_v9_navegacion_requerimientos` |
| A4 labels, fieldset, legend y botones | ✅ | `::test_a4_labels_y_botones` |
| A5 `title` en cada iframe | ✅ | `::test_a5_iframes_con_title` (3 páginas) |
| A6 `role="alert"` / `role="status"` | ✅ | `::test_a6_alert_y_status` |
| A7 leyenda con los hex de `COLORES` | ✅ | `::test_a7_leyenda_con_colores` |
| A8 imagen (alt, width, height, lazy) y título legible | ✅ | `::test_a8_imagen_y_titulo`, `::test_tamanos_de_imagenes` (IHDR real) |
| A9 sin JS propio | ✅ | `::test_a9_sin_js_propio`, `tests/test_app_r5.py::test_sin_algoritmos_ni_js_propio` |
| A10 revisión manual en el navegador | ⏳ usuario (T35) | — |
| A11 7 variables; sin `transition: all`, `@import` ni `url(http`; `COLORES` = Cocora/Cereza/Hoja | ✅ | `::test_a11_paleta_en_css`, `::test_a11_sin_transition_all_ni_externos`, `::test_a11_colores_de_mapas` |
| V0 paleta | ✅ | `::test_a11_paleta_en_css` |
| V0 tipografía, firma y movimiento | ✅ (texto del CSS) | `::test_v0_tipos_firma_y_movimiento`; el aspecto, en A10 |
| V0 textos (verbos concretos) | ✅ | `::test_a4_labels_y_botones`, `::test_v10_inicio_tarjetas` |
| V1 hoja propia | ✅ | `::test_a1_*` |
| V2 viewport, saltar, `aria-current`, foco | ✅ | `::test_a2_*`, `::test_a3_*`, `::test_v0_*` (`:focus-visible`); 375 px en A10 |
| V3 formularios | ✅ | `::test_a4_*`, `::test_v3_fieldset_y_cuadricula` |
| V4 tarjetas | ✅ (parcial: `tabular-nums` sin prueba, ver sugerencia 1) | `::test_v4_tarjetas_ruta`, `::test_v4_tarjetas_envolvente`, `::test_v4_tarjetas_itinerario` |
| V5 colores, leyenda, tabla y orden | ✅ (parcial: el color del encabezado sin prueba, ver sugerencia 2) | `::test_a7_*`, `::test_v5_tabla_comparacion`, `::test_v5_orden_de_la_pagina` |
| V6 mensajes con `role` | ✅ | `::test_a6_alert_y_status` |
| V7 iframes con `title` y altura adaptable | ✅ (la altura, en A10) | `::test_a5_*` |
| V8 tablas | ✅ | `::test_v8_tabla_envolvente`, `::test_tabla_con_titulo`, `::test_v8_tablas_de_resultados` |
| V9 resultados | ✅ | `::test_titulos_cubren_la_lista_fija`, `::test_tamanos_de_imagenes`, `::test_a8_*`, `::test_v9_*`, `::test_faltantes_con_titulo` |
| V10 inicio | ✅ | `::test_v10_inicio_tarjetas` |

### Comprobaciones propias del revisor

**Restricciones.** En el HTML servido no hay `<script` fuera del `srcdoc` de Folium ni `<style` (comprobado en las 11 URLs). `estilos.css` no tiene `@import`, `url(` ni fuentes externas. Las únicas URL externas están dentro del `srcdoc` de los mapas (Leaflet, CDN y mosaicos de OSM), igual que antes de B5; la spec las admite. El `style="background: …"` de la leyenda (`itinerario.html:32-33`) es un atributo, aprobado en la Puerta 2 (V-1 a V-11).

**`estilos.css` (148 líneas, 15 secciones comentadas).** Se lee de corrido, con un comentario por sección que dice para qué sirve, y usa solo variables de la paleta más `#fff`. Cualquier integrante lo puede explicar.
- Especificidad: no encontré reglas que se anulen. Las parejas que podrían chocar ganan en el orden correcto: `.menu a:hover` (0,2,1) sobre `.cabecera a` (0,1,1); `.cabecera [aria-current="page"]` (0,2,0) sobre `.menu a` (0,1,1); `thead .metodo-hk` (0,1,1) sobre `thead th` (0,0,2); `.tarjeta.metodo-hk` (0,2,0) sobre `.tarjeta`; `.casilla` sobre `label`. Selectores de uno o dos niveles, sin `!important`.
- Movimiento: no hay `transition: all`. El botón usa `transition: transform 160ms ease-out` y `:active { transform: scale(0.97) }`. Los cambios de color al pasar el mouse (150 ms) están solo dentro de `@media (hover: hover) and (pointer: fine)` (`estilos.css:131-135`). `prefers-reduced-motion: reduce` (`:136-139`) va después, con la misma especificidad, así que gana: quita la escala y deja solo las transiciones de color, como pide la skill emil-design-eng.
- Desviación menor del plan, no anotada en tasks: el plan ponía `.menu a:hover` en Niebla y `button:hover` en Guadua. Eso último no habría hecho nada, porque el botón ya es Guadua. El código usa Bahareque y Cocora (`estilos.css:133-134`). Es una mejora y el contraste sigue bien (ver tabla).

**Contraste WCAG 2.x** (luminancia relativa sRGB, calculada con un script; AA pide ≥ 4,5:1 para texto normal y ≥ 3:1 para texto grande y para contornos de controles):

| Par | Razón | AA texto |
|---|---|---|
| Tinta `#1D2521` sobre Niebla `#F3F6F4` | 14,42:1 | ✅ (AAA) |
| Tinta sobre blanco (tarjetas y tablas) | 15,69:1 | ✅ |
| Blanco sobre Guadua `#2F4A3A` (menú, botón, `thead`) | 9,72:1 | ✅ (AAA) |
| Blanco sobre la línea de las curvas (Hoja al 35 % sobre Guadua ≈ `#3F6148`) | 6,97:1 | ✅ (el peor caso del menú) |
| Cocora `#1F5F8B` sobre Niebla | 6,29:1 | ✅ |
| Cereza `#B8322A` sobre Niebla | 5,47:1 | ✅ |
| Cocora / Cereza sobre blanco | 6,84:1 / 5,95:1 | ✅ |
| Blanco sobre Cocora (`thead` de Held-Karp, botón al pasar el mouse) | 6,84:1 | ✅ |
| Blanco sobre Cereza (`thead` del voraz) | 5,95:1 | ✅ |
| Enlaces Guadua sobre Niebla / sobre blanco | 8,93:1 / 9,72:1 | ✅ (AAA) |
| Bahareque sobre Guadua (menú al pasar el mouse) | 7,01:1 | ✅ |
| Anillo de foco: Cocora sobre Niebla / Niebla sobre Guadua | 6,29:1 / 8,93:1 | ✅ (≥ 3:1) |
| Hoja `#5E8C61` sobre Niebla | 3,57:1 | No apta para texto; solo se usa en bordes (≥ 3:1 ✅). Ninguna regla usa `color: var(--hoja)` |
| Bahareque sobre blanco (borde del `<select>`) | 1,39:1 | ❌ como contorno de control (ver sugerencia 3) |

**Accesibilidad de las plantillas.** `<label for>` coincide con el `id` de los tres `<select>`; las casillas están en `<fieldset>` + `<legend>` y cada una va dentro de su `<label>`; `<nav aria-label>` en el menú y en R1–R4; `aria-current="page"` en el menú y `"true"` en R1–R4 (V-2); `role="alert"` y `role="status"`; `title` en los tres `<iframe>`; `<caption>`, `<thead>` y `th scope="col"`/`"row"` en la tabla de la envolvente, en la comparación, en la tabla de la regla y en las de pandas (`tabla_con_titulo`, que escapa con `markupsafe`); `<img>` con `alt` descriptivo, `width`, `height` y `loading="lazy"`; `lang="es"`.

**Fidelidad al V0.** Hay un solo elemento distintivo: la cabecera con `repeating-radial-gradient` (`estilos.css:45-52`). El resto es sobrio: tarjetas con borde superior, sin sombras, gradientes ni animaciones de entrada. Evita los tres clichés de la skill frontend-design. El fondo es gris verdoso (`#F3F6F4`), no crema `#F4F1EA`, y no hay acento terracota. No es negro con acento ácido. Tampoco es el estilo «periódico» de líneas finas y radio cero (usa radio de 4 px y tarjetas). La serifa del sistema queda en los títulos, con mesura.

**Mutaciones** (hechas por el revisor sobre el árbol de trabajo y restauradas desde una copia; `git status` al final es igual al del inicio):

| Mutación | Resultado |
|---|---|
| Quitar `title="Mapa de la ruta"` | ❌ 1 falla (`test_a5`) ✔ |
| `aria-current="page"` en la navegación R1–R4 | ❌ 2 fallan (`test_a3[r2]`, `test_v9`) ✔ |
| Sacar el `:hover` de `@media (hover: hover) and (pointer: fine)` | ❌ 1 falla (`test_v0`) ✔ |
| Quitar `role="alert"` del itinerario | ❌ 1 falla (`test_a6`) ✔ |
| Poner el mapa antes del resumen | ❌ 1 falla (`test_v5_orden`) ✔ |
| Quitar todo `font-variant-numeric: tabular-nums` | ✅ 541 pasan: **sobrevive** (sugerencia 1) |
| `thead .metodo-hk` con Cereza (encabezado de Held-Karp en rojo, distinto del mapa) | ✅ 541 pasan: **sobrevive** (sugerencia 2) |
| Borrar el bloque `prefers-reduced-motion` dejando la cadena en un comentario | ✅ sobrevive (sugerencia 4) |

**App real con `curl`** (puerto 5087, ya detenida; no se tocó el 5050). `/static/estilos.css` → 200 `text/css`. `/`, `/ruta?origen=C01&destino=C12`, `/ruta?origen=C01&destino=C01`, `/envolvente`, `/itinerario` con los 6 y con los 8 del caso 6, y `/resultados/r1..r4` → 200. `/itinerario?partida=C01&atractivos=A01` → 400 con `role="alert"` «elige entre 6 y 8 atractivos (llegaron 1)». Cada página tiene un solo `aria-current="page"` y en la sección correcta. Ruta: «29,7 min (1 783,4 s)», «24,00 km», «7 360» en tarjetas, y el `<h2>` en texto plano con los nombres. C01→C01: `role="status"` con el aviso. Envolvente: «14 vértices» y «1 631,5 km²». Leyenda con `#1F5F8B` y `#B8322A`. Caso 6: aparece el bloque de la regla con su `<caption>`. r2: títulos legibles, `<caption>` en las 3 tablas y `alt` descriptivo. r4: «Faltan» con título, archivo y comando.

### Bloqueantes
Ninguno.

### Sugerencias (no bloquean)
1. `tests/test_visual_r5.py:98-103`: la tabla «Verificación del ajuste» del plan dice que se comprueba `tabular-nums` en el CSS, pero `test_v0_tipos_firma_y_movimiento` no lo incluye. La mutación que lo quita de `estilos.css:71,86,108` sobrevive. Bastaría con agregar `"tabular-nums"` a la lista o, mejor, `re.search(r"\.tarjeta dd\s*\{[^}]*tabular-nums", css)` y lo mismo con `td`.
2. `tests/test_visual_r5.py:190-198`: V5 pide que el encabezado de cada método tenga el mismo color que el mapa. La prueba solo mira la clase `metodo-hk`/`metodo-voraz` en el `<th>`, no que `estilos.css:89-92` la asocie con `var(--cocora)`/`var(--cereza)`. Habría que agregar una aserción sobre el texto del CSS, por ejemplo `re.search(r"thead \.metodo-hk\s*\{[^}]*var\(--cocora\)", css)`.
3. `rutas/r5/static/estilos.css:66`: el borde del `<select>` en Bahareque sobre blanco tiene 1,39:1. WCAG 1.4.11 pide ≥ 3:1 para el contorno de un control. Usar `var(--hoja)` (3,89:1) o un gris más oscuro lo resuelve sin cambiar el estilo. Los bordes de tarjetas y tablas son decorativos y pueden quedar en Bahareque.
4. `tests/test_visual_r5.py:98-103`: la prueba busca cadenas sueltas en el CSS, que también se cumplen dentro de un comentario. Si se quiere más firmeza, comprobar `@media (prefers-reduced-motion: reduce)\s*\{` seguido de `transform: none`. Es una debilidad pequeña, porque hoy ningún comentario repite esas cadenas.
5. `rutas/r5/static/estilos.css:56`: `.cabecera [aria-current="page"]` solo cambia `border-bottom-color`. La marca (que lleva `aria-current` en `/`) no tiene borde, así que en el inicio no se ve qué sección está activa. Se podría dar a `.marca` el mismo `border-bottom: 3px solid transparent` que a `.menu a`, o aceptarlo así (el título de la página ya lo dice). Conviene revisarlo en T35.
6. `rutas/r5/app.py:80`: el tamaño de `r4_tiempo_vs_k.png` sigue aproximado (ya anotado en T32). Cuando exista la PNG, hay que corregirlo y agregarlo a `test_tamanos_de_imagenes`.
7. `docs/anexo-ia.md:24`: dice «las pruebas actuales siguen en verde sin cambios (`git diff` de ellas vacío)». Con el arreglo de `puerto_libre` ya no es cierto: conviene una línea que diga que se simuló `puerto_libre` en `_main_con_run_falso` y por qué.
8. `specs/r5-aplicacion/tasks.md` (T27/T34): anotar la desviación de los colores al pasar el mouse (Bahareque y Cocora en lugar de Niebla y Guadua, ver «Comprobaciones»), para que spec, plan y código digan lo mismo.
9. Commit pendiente: `tests/test_app_r5.py`, `specs/r5-aplicacion/tasks.md` y este `review.md`.

### Pendiente del usuario: T35 / A10 (navegador, no automatizable)
- Con la instancia del 5050 **reiniciada**, porque un servidor viejo sirve las plantillas anteriores: los 9 pasos de T35 a ≈ 1280 px y a ≈ 375 px. Lo más importante:
  - que las curvas de nivel no tapen el menú (la línea más clara da 6,97:1, pero hay que verlo);
  - que a 375 px no haya desplazamiento horizontal y que las tablas de pandas se desplacen dentro de `.tabla-ancha`;
  - que la casilla tenga 1 columna en móvil y 2 o 3 en escritorio;
  - que los colores de la leyenda coincidan con las líneas del mapa y con el encabezado de la tabla;
  - que el botón se hunda al presionar y no lo haga con `prefers-reduced-motion` emulado;
  - que el foco se vea con Tab y que «Saltar al contenido» funcione;
  - revisar de paso la sugerencia 5 (la marca en el inicio).
- Anotar aquí la fecha, quién, el navegador y su versión, las dos anchuras y el resultado de cada paso. Si algo obliga a cambiar el CSS, volver a correr el comando de T34.
- Siguen pendientes de la ronda 1 los casos 16 y 17 en el navegador.

### Pendiente para el documento técnico
- Capturas de las cuatro secciones a ancho de escritorio, y una a 375 px si se quiere, tomadas en T35.
- Si el documento menciona la interfaz, basta una línea: la hoja de estilos es propia, sin JavaScript ni recursos externos, y el diseño no cambia ningún resultado (sección 8: el diseño no se evalúa en R5).

## Ronda 3: diseño v2 apple-design (B6): APROBADO

Revisado el 2026-11-15 contra la línea base `b79167c`: spec «Diseño visual v2» (D0–D8, B1–B9), plan «Diseño visual v2 (bloque B6)» con la Puerta 2 (DV-1 a DV-16), `tasks.md` T36–T46 y `.claude/skills/apple-design/SKILL.md`. Durante la revisión el usuario hizo el commit `63a664a` («R5 bloque 6…»). El árbol quedó limpio e igual a lo revisado, y las suites se volvieron a correr sobre ese commit.

Pruebas: ✅
- `.venv/bin/python -m pytest -q -m "not red"` → **606 pasan, 1 se salta** (`test_envolvente.py:136`, prueba lenta con `--lento`), 41 deseleccionadas. Antes de B6 eran 545 y 1.
- `.venv/bin/python -m pytest -q -m red` → **39 pasan, 2 se saltan**. Son los saltos conocidos, ajenos a R5: falta `data/raw/radio_2km.graphml` y falta `results/r4/r4_exactas.csv`.
- `tests/test_visual_r5.py` + `tests/test_app_r5.py` → 142 pasan.

| Caso / punto | Cumplido | Test |
|---|---|---|
| B1 hoja servida `text/css`, `base.html` sin `<style>` | ✅ | `test_visual_r5.py::test_a1_estilos_servidos`, `::test_a1_base_sin_style` (conservadas) |
| B2 dos `<script defer>` solo en `base.html`, en `<head>` y en orden | ✅ | `::test_b2_scripts_solo_en_base`; `test_app_r5.py::test_sin_algoritmos_ni_js_propio`, `::test_inicio_y_menu` |
| B2 sin JS en línea, `on…=` ni `javascript:` | ✅ | `::test_b2_sin_js_en_linea` |
| B2 solo `app.js` y `vendor/motion.js` en `static/` | ✅ | `::test_b2_solo_dos_archivos_js` |
| B2 `app.js` ≤ 150 líneas (tiene 92), sin `fetch(`/`XMLHttpRequest`/`eval(`/`innerHTML`/`document.write`/`http`, con `prefers-reduced-motion` | ✅ | `::test_b2_app_js_limites` |
| B2 el HTML servido de las 12 URL tiene exactamente 2 `<script` | ✅ | `::test_b2_html_servido_solo_dos_scripts` |
| B3 SHA-256 de Motion y `LICENSE.md` MIT | ✅ (`shasum` propio: `521cfef8…2cae`) | `::test_b3_motion_con_hash_y_licencia`, `::test_b3_js_servidos` |
| B4 variables de D2 en claro y oscuro, `color-scheme` | ✅ | `::test_b4_variables_claro_y_oscuro`, `::test_b4_color_scheme` |
| B4 `prefers-reduced-motion`, `prefers-reduced-transparency`, `prefers-contrast`, `@view-transition` y `backdrop-filter` | ✅ | `::test_b4_movimiento_reducido`, `::test_b4_preferencias`, `::test_b4_view_transition`, `::test_b4_barra_translucida` |
| B4 sin `transition: all`, `@import` ni `url(http` | ✅ | `::test_a11_sin_transition_all_ni_externos` (conservada), `::test_b4_movimiento_m1` |
| D2 contraste 4,5:1 (texto) y 3:1 (controles) | ✅ | `::test_b4_contraste`, `::test_b4_contorno_de_controles` |
| B5 `COLORES` = `#007AFF`/`#FF9500`/`#34C759` = `--metodo-*` = leyenda | ✅ | `::test_b5_colores_de_metodos`, `::test_b5_encabezados_de_metodo`, `::test_a7_leyenda_con_colores` |
| B6 contador «0/1/6 elegidos» con `aria-live="polite"`, texto e ícono | ✅ | `::test_b6_contador_en_la_pagina` (4 casos, incluido el de ids repetidos), `::test_contador_elegidos`, `::test_contador_limites_iguales_a_servicios` |
| B7 segmentado con 4 enlaces y `aria-current="page"` en R2 (y en R3) | ✅ | `::test_b7_control_segmentado[r2,r3]` |
| B8 funcionales y estructura accesible de v1 en verde | ✅ | todo `-m "not red"` y `-m red`; `test_a2…a8`, `test_v3…v10` conservadas |
| D0 título y entradilla antes del control | ✅ | `::test_d0_titulo_y_entradilla` (5 páginas) |
| D1 tipografía | ✅ | `::test_b4_tipografia`, `::test_v0_cifras_tabulares` |
| D3 materiales y superficies | ✅ | `::test_b4_barra_translucida`, `::test_b4_preferencias`, `::test_d3_superficies` |
| D4 menú de 4 enlaces y segmentado | ✅ | `::test_d4_menu`, `::test_a3_aria_current`, `::test_b7_control_segmentado` |
| D5 lista agrupada, fichas, botón píldora, error con siguiente paso | ✅ | `::test_d5_lista_agrupada`, `::test_d5_fichas`, `::test_d5_boton_principal`, `::test_d5_error_con_siguiente_paso` |
| D6 M1 / M2 / M3 / M4 y movimiento reducido | ✅ (texto y CSS; el comportamiento real va en B9) | `::test_b4_movimiento_m1`, `::test_b2_app_js_m2_m3`, `::test_b4_view_transition`, `::test_b4_movimiento_reducido` |
| D7 inicio | ✅ | `::test_d7_inicio`, `::test_v10_inicio_tarjetas` |
| D8 sin rastros de v1 | ✅ | `::test_d8_sin_rastros_de_v1` |
| B9 revisión manual en Chrome y Safari | ⏳ del usuario (T46) | — |

### Comprobaciones propias del revisor

**Pruebas de v1 (comparación de funciones y cuerpos con AST, `b79167c` → actual):**
- Se borraron o reescribieron exactamente las 8 de la tabla del plan: `test_a9_sin_js_propio`, `test_a11_paleta_en_css` (con `PALETA`), `test_a11_colores_de_mapas`, `test_v0_tipos_firma_y_movimiento`, `test_v0_movimiento_reducido_quita_la_escala`, `test_v0_contorno_select`, `test_v5_colores_encabezado_metodos` y `test_v9_navegacion_requerimientos`.
- De las 24 conservadas, solo cambian dos, y las dos están en el plan:
  - `test_a3_aria_current` pierde el parámetro `("/resultados/r2", "Resultados")`;
  - `test_a4_labels_y_botones` cambia el fragmento de la leyenda a `<legend>Atractivos</legend>` (DV-2, opción A).
- También se borró el auxiliar `_variable`, que solo usaban las pruebas borradas. Está anotado en T38.
- Hay 33 pruebas nuevas, que coinciden una a una con la tabla «Pruebas nuevas de v2».
- En `test_app_r5.py` solo cambian las 2 aserciones previstas, y las sustitutas son más estrictas (cuentan exactamente 2 `<script` y comparan las etiquetas literales).
- No se debilitó ninguna otra prueba.

**Archivos protegidos:** `git diff b79167c --stat` está vacío para `rutas/r1..r4`, `servicios.py`, `datos.py`, `formato.py`, `requirements.txt`, `.gitignore`, `Dockerfile` y `CLAUDE.md`. En `mapas.py` solo cambian `COLORES` y el docstring (DV-15). No hay `package.json` ni `node_modules`, y `git check-ignore` no ignora ningún `.js`. No hay `networkx`, `scipy` ni `shapely` en `rutas/r5/*.py`.

**Motion contra el código del vendor (14.14.0, UMD):**
- El envoltorio asigna `globalThis.Motion={}` y exporta `t.animate=Mu` y `t.stagger`.
- `animate` resuelve los elementos con `Array.from(t)`, así que acepta el `NodeList` de `querySelectorAll`.
- Si `delay` es una función, la llama como `a.delay(e, r)` (índice y total), que es la firma de `stagger(0.04)`.
- Con `duration` y `bounce`, y sin `stiffness`/`damping`, el resorte se resuelve por duración. La razón de amortiguamiento es `Jt(bounce) = max(1 − bounce, 0,05)`, así que `bounce: 0` da 1,0: críticamente amortiguado, la rama sin oscilación. El valor por defecto sería `bounce = 0,3`; aquí se pasa 0 de forma explícita.
- `ease: "linear"` es válido.
- La API que usa `app.js` es la correcta para este build.

**`app.js`:**
- `node --check` da sintaxis correcta.
- Simulé el contador con un DOM falso para 0, 1, 5, 6, 8, 9 y 10 casillas. Da «! 0 elegidos · faltan 6 / fuera», …, «! 5 elegidos · falta 1», «✓ 6 elegidos · listo para calcular / en-rango», «! 9 elegidos · sobra 1» y «! 10 elegidos · sobran 2». Son los mismos textos que `contador_elegidos` en `app.py`.
- `escribir()` solo cambia `textContent` si el texto es distinto, así que la carga y el `pageshow` no generan anuncios repetidos.
- Solo anima `opacity` e `y` (`transform`). Con movimiento reducido hace un fundido de 0,2 s.
- Usa `textContent` y nunca HTML. Si no hay `window.Motion`, no hace nada.

**Mejora progresiva:**
- Ninguna regla de `estilos.css` oculta contenido (`opacity: 0`, `visibility` o `display: none`), salvo `.barra::after` en `prefers-contrast`.
- Las tarjetas se ven sin JS (DV-9).
- El contador sale del servidor, la validación sigue en el servidor y el botón nunca se deshabilita.

**`estilos.css`:**
- Hay variables en claro y en oscuro.
- `backdrop-filter` va con la versión `-webkit-` y con un respaldo `@supports not` que deja la barra sólida.
- Hay bloques `prefers-reduced-transparency` y `prefers-contrast: more`. `@view-transition` está solo dentro de `no-preference`.
- No hay `transition: all`, `!important` ni `@import`. La única `transition` es `transform 100ms ease-out` (M1). Fuera de M1–M4 no se anima nada.
- La especificidad es de uno o dos niveles. El único id es `#contenido`, y solo para `scroll-margin-top`.
- `.barra [aria-current]` (0,2,0) le gana a `.menu a` (0,1,1). La marca subrayada en `/` resuelve la sugerencia 5 de la ronda 2.
- Tipografía según el tamaño (skill §15):
  - `h1`: −0,02 em y 1,05 de interlineado;
  - `h2` y `.tarjeta dd`: −0,01 em;
  - `body` y `.entradilla`: 0;
  - texto chico (`.nota`, `caption`, `dt`, `.visita`): +0,01 em.

**Contraste** (WCAG 2.x, calculado por separado con la fórmula de luminancia relativa):

| Par | Claro | Oscuro |
|---|---|---|
| texto / fondo | 15,46 | 19,29 |
| texto / superficie | 16,83 | 15,63 |
| secundario / fondo (entradilla, contador) | 4,66 | 7,31 |
| secundario / superficie (`dt`, `.visita`, `.descripcion`) | 5,07 | 5,93 |
| botón: blanco / `#0071E3` (los dos modos, DV-4) | 4,70 | 4,70 |
| enlaces: van en `--texto` (DV-5) | 15,46–16,83 | 15,63–19,29 |
| acento / superficie (borde de la ficha elegida) | 4,70 | 5,64 |
| acento / fondo (anillo de foco, ≥ 3) | 4,31 | 6,96 |
| contorno del `select` `#8E8E93` / superficie | 3,26 | 5,22 |
| contorno del `select` / fondo (no se usa: el `select` va en `.grupo`) | 2,99 | 6,44 |
| texto / pista del segmentado | 13,48 | 17,70 |
| texto / barra translúcida, peor caso (contenido negro debajo en claro, blanco en oscuro) | 7,80 | 6,17 |
| naranja `#FF9500` / superficie y fondo | 2,20 / 2,02 | 7,74 / 9,55 |
| azul de método `#007AFF` / superficie | 4,02 | 4,24 |
| verde `#34C759` / superficie | 2,22 | 7,66 |

El naranja, el azul y el verde de método no se usan nunca como color de texto. Van en franjas `inset` (tarjetas, `thead`, `.error`), en la muestra con contorno de la leyenda y en el mapa. Todo el texto cumple 4,5:1 en los dos modos, y los contornos de los controles, 3:1. El borde de `.ficha` en `--separador` (1,25 en claro, 1,60 en oscuro) es decorativo: la casilla real sigue visible dentro.

**Accesibilidad.** Se conserva la de v1: etiquetas, `fieldset`/`legend`, `role="alert"`/`status`, `title` de los iframes, `caption`/`scope` y «Saltar al contenido», ahora con `scroll-margin-top`. Además se suman:
- el contador con texto e ícono `aria-hidden`;
- el `fieldset` con `aria-describedby="contador"`;
- en Resultados, un solo `aria-current="page"`, en el segmento, y `"true"` en «Resultados» del menú (DV-1);
- las fichas son `<label class="ficha">`, con la casilla dentro como área de clic.

**`curl`** (puerto 5077, ya detenido; el 5050 no se tocó):
- `/` → 200, con la entradilla y las 4 tarjetas.
- `/ruta?origen=C01&destino=A03` → 200, con la lista agrupada y las tarjetas «52,7 min», «35,42 km» y «8 568».
- `/envolvente` → 200, con «14 vértices» y «1 631,5 km²».
- `/itinerario` con A01–A06 → 200, con el contador «✓ 6 elegidos (elige de 6 a 8) · listo para calcular», `data-estado="en-rango"`, las fichas y el resumen.
- `/resultados/r2` → 200, con el segmentado (`aria-current="page"` en R2 y el indicador dentro) y «Resultados» del menú en `aria-current="true"`.
- Las respuestas 400 llevan su siguiente paso:
  - «lugar desconocido: X99. Elige el origen y el destino de la lista.»;
  - «elige entre 6 y 8 atractivos (llegaron 1). Ajusta la partida o los atractivos y vuelve a calcular.».
- `/static/estilos.css` → `text/css`; `app.js` y `motion.js` → `text/javascript`, 200.

**Mutaciones** (en una copia en el scratchpad, sin caché de bytecode, restauradas y verificadas con `diff`):

| Mutación | Resultado |
|---|---|
| `bounce: 0.2` en `app.js` | ❌ `test_b2_app_js_m2_m3` ✔ |
| `--texto-secundario: #8E8E93` | ❌ `test_b4_variables_claro_y_oscuro` ✔ |
| `@view-transition` fuera de `no-preference` | ❌ `test_b4_view_transition` ✔ |
| `aria-live="off"` en el contador | ❌ `test_b6_contador_en_la_pagina` ✔ |
| `transition: all 100ms` | ❌ `test_a11_sin_transition_all_ni_externos` ✔ |
| `innerHTML` en `escribir()` | ❌ `test_b2_app_js_limites` ✔ |
| `MINIMO = 5` en `app.js` | ❌ `test_b2_app_js_m2_m3` ✔ |
| `onclick=` en `ruta.html` | ❌ `test_b2_sin_js_en_linea` ✔ |
| `COLORES["voraz"] = "#FF9501"` | ❌ `test_b5_colores_de_metodos` ✔ |
| `aria-current="page"` en «Resultados» del menú | ❌ `test_b7_control_segmentado[r2,r3]` ✔ |
| quitar el `transform: none` de `prefers-reduced-motion` | ❌ `test_b4_movimiento_reducido` ✔ |
| quitar `defer` de `app.js` | ❌ 3 pruebas de B2 ✔ |
| `--relleno-boton: #2997FF` | ❌ `test_b4_contraste` ✔ |
| `x.js` extra en `static/` | ❌ `test_b2_solo_dos_archivos_js` ✔ |
| `class="cuenta"` → `class="conteo"` en la plantilla | ✅ **sobrevive** (sugerencia 2) |
| `.tarjeta { opacity: 0 }` en el CSS | ✅ **sobrevive** (sugerencia 3) |
| `.error { color: var(--metodo-voraz) }` (naranja como texto, 2,20:1) | ✅ **sobrevive** (sugerencia 1) |
| `a { color: var(--acento) }` (4,31:1 sobre el fondo claro, DV-5) | ✅ **sobrevive** (sugerencia 1) |
| `if (false && movimientoReducido.matches)` | ✅ sobrevive (sugerencia 5) |
| ícono sin `aria-hidden`; `dataset.estado` borrado del JS | ✅ sobreviven (menores, B9) |

### Bloqueantes
Ninguno.

### Sugerencias (no bloquean)
1. **Naranja y acento como texto, sin prueba.** D2 dice que el naranja nunca es color de texto, y DV-5 dice que el acento como texto va solo sobre una superficie. Hoy se cumple: `estilos.css` no tiene ningún `color: var(--acento)` ni `color: var(--metodo-*)`. Pero `test_b4_contraste` (`tests/test_visual_r5.py:443`) solo mira las variables, así que las mutaciones `.error { color: var(--metodo-voraz) }` (2,20:1) y `a { color: var(--acento) }` (4,31:1) pasan la suite. Se arregla con una aserción: ninguna declaración `color:` (sin contar `accent-color`) usa `var(--metodo-hk|voraz|envolvente)` ni `var(--acento)`.
2. **Selectores de `app.js` sin atar a la plantilla.**
   - `rutas/r5/static/app.js:67-69` busca `.cuenta`, `.estado` y `.icono` dentro de `#contador`.
   - Si se renombra una clase en `rutas/r5/templates/itinerario.html:17-18`, `querySelector` devuelve `null` y `escribir()` lanza `TypeError`: el contador deja de actualizarse sin que ninguna prueba falle (la mutación sobrevive).
   - Se arregla con una prueba que compruebe que cada selector que usa `app.js` (`#contador`, `.cuenta`, `.estado`, `.icono`, `.resumen .tarjeta`, `input[name="atractivos"]`) existe en el HTML servido, o con una guarda `if (elemento)` en `escribir()`.
3. **Regla «el CSS nunca oculta algo que solo el JS vuelve a mostrar» sin prueba.** Viene del plan, línea 798, y de DV-9. Hoy se cumple, pero la mutación `.tarjeta { opacity: 0 }` sobrevive. Se arregla con una prueba que impida `opacity: 0`, `visibility: hidden` y `display: none` en `.resumen`, `.tarjeta`, `.contador`, `.ficha` y `.casillas`.
4. **`aria-atomic="true"` en el contador** (`rutas/r5/templates/itinerario.html:16`). `app.js` cambia por separado `.cuenta` y `.estado`. Como `aria-atomic` vale `false` por defecto, el lector anuncia solo los fragmentos («7 elegidos», «listo para calcular») y no la regla «(elige de 6 a 8)». Con `aria-atomic="true"` se lee la frase completa. Conviene confirmarlo en B9 con VoiceOver.
5. **Rama de movimiento reducido en JS.** `test_b2_app_js_m2_m3` comprueba que `duration: 0.2` esté en el texto, pero no que la rama dependa de `movimientoReducido.matches`. La mutación `if (false && …)` sobrevive. El riesgo es bajo, porque B9 lo prueba con la emulación. Si se quiere una prueba más firme, `re.search(r"if \(movimientoReducido\.matches\)", js)`.
6. **`prefers-contrast: more` sin `.grupo`.** El plan (línea 1039) pone `.tarjeta, .grupo, .ficha, .tabla-ancha, .tarjeta-seccion, .segmentado`, pero `rutas/r5/static/estilos.css:193` omite `.grupo`. Los `select` conservan su contorno, así que no se pierde ningún control, pero el grupo queda sin borde definido (D3). Agregar `.grupo`, y de paso `.error, .aviso, .grafica, .faltantes`, alinea código y plan.
7. **Mensaje del commit `63a664a`.** El asunto quedó como `R5 bloque 6: diseño v2 con apple-design" -m "Tipografía…`: las comillas y el `-m` entraron en el texto. Como aún no se ha hecho push (`main` va 3 commits por delante de `origin/main`), el usuario puede corregirlo con `git commit --amend` si quiere.
8. **Doble anillo de foco en las fichas.** `estilos.css:63` pone el anillo en la casilla con `:focus-visible`, y `:125` pone otro en la ficha con `:has(input:focus-visible)`. Al tabular se ven dos anillos. Es cuestión de gusto: decidirlo en B9 y, si molesta, quitar el `outline` de `.ficha input:focus-visible`.

### Pendiente del usuario: B9 / T46 (navegador, no automatizable)
- **Antes de empezar:** reiniciar la instancia del 5050, que estaba corriendo durante la revisión (un servidor viejo puede servir plantillas cacheadas). Revisar en Chrome y en Safari, anotando la versión de cada uno, en claro y en oscuro, a ≈ 1280 px y a ≈ 375 px, y con el movimiento reducido emulado.
- **Movimiento:**
  - las tarjetas del resumen (`/ruta`, `/envolvente`, `/itinerario`) entran sin rebote y escalonadas;
  - con movimiento reducido, solo hay un fundido de opacidad;
  - el parpadeo previo a M2 (DV-9) es aceptable.
- **Contador:**
  - responde al marcar y desmarcar;
  - el ícono cambia entre «!» y «✓»;
  - al volver con «Atrás», queda sincronizado;
  - con VoiceOver, ver qué se anuncia (sugerencia 4).
- **Segmentado:**
  - el indicador se desliza entre R1 y R4 (Chrome 126+ y Safari 18.2+);
  - sin soporte, aparece directamente en el segmento nuevo;
  - con movimiento reducido, no hay transición.
- **Barra y contraste:**
  - la barra translúcida es legible con el mapa y las tablas pasando por debajo;
  - con `prefers-contrast: more` y con transparencia reducida, queda sólida;
  - el contraste se ve bien en los dos modos;
  - el mapa de Folium queda claro en modo oscuro (aceptado en D2).
- **Navegación y foco:**
  - Tab y «Saltar al contenido» no quedan tapados por la barra;
  - el foco se ve en las fichas (sugerencia 8), en el botón y en el segmentado;
  - M1: el botón, las fichas y los segmentos se hunden al presionar, y no lo hacen con movimiento reducido.
- **Pantalla angosta (375 px):**
  - sin desplazamiento horizontal;
  - las tablas se desplazan dentro de `.tabla-ancha`;
  - el menú se parte en dos líneas;
  - en cada fila, la etiqueta queda encima del `select`.
- **Al terminar:** anotar en esta ronda la fecha, quién lo hizo, los navegadores con su versión, los modos, las anchuras y el resultado de cada paso. Tomar las capturas para `evidencias/r5/`. Si algo obliga a cambiar el CSS, una plantilla o `app.js`, se corrige con su prueba y se vuelve a correr el comando de T45.

### Pendiente para el documento técnico
- Capturas de las cuatro secciones en claro, y una en oscuro y a 375 px si se quiere, tomadas en B9.
- Si el documento menciona la interfaz, basta una línea:
  - el diseño es propio, con la fuente del sistema y modo claro y oscuro;
  - el único JavaScript es una mejora progresiva (`app.js` con Motion 14.14.0, MIT): no implementa ningún algoritmo y la aplicación funciona sin él;
  - el diseño no se evalúa en R5 (sección 8) y no cambia ningún resultado.

## B9 (T46): revisión manual del diseño v2 por el usuario, 2026-11-15
- **Quién:** Juan Nicolás Castro, en su portátil (macOS), con la app local en `http://127.0.0.1:5050`.
- **Resultado:** el usuario abrió la app, revisó las secciones y aprobó el diseño v2 («ya me gustó»). No pidió cambios.
- **Sin registrar:** el usuario no anotó navegador y versión ni el detalle de cada paso (claro/oscuro, 375 px, movimiento reducido). Si el grupo quiere ese detalle para el documento técnico, se completa aquí.
- **Capturas:** las de las 4 secciones se generaron con Chrome sin interfaz (`--headless --screenshot`) y quedaron en `evidencias/r5/` (ver T46).
- **Sugerencias de la ronda 3:** las 8 quedan como mejoras opcionales; ninguna bloquea.

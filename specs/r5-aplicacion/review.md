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

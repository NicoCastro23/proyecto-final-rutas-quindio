# Aplicación — Requerimiento 5
Enunciado: sección 5, Requerimiento 5 (párrafo inicial, punto 1 con sus cuatro viñetas y la viñeta de ejecución local); sección 7 (entregable «Aplicación: ejecutable localmente siguiendo el README»); sección 8 («En R5 se evalúa que la aplicación muestre los resultados y funcione siguiendo el README»). Peso: 5 %.
Estado: ☑ spec (aprobada en Puertas 1 y 2, 2026-11-11) · ☑ pruebas (497 sin red; 14 de R5 con la red real) · ☑ código · ☑ verificado (review.md, ronda 1: APROBADO; pendiente la revisión en el navegador de los casos 16 y 17) · ☑ ajuste visual: spec aprobada (2026-11-12) · ☑ plan (Puerta 2, 2026-11-12) · ☑ código y verificado (review.md, ronda 2: APROBADO; pendiente T35 en el navegador)
Depende de:
- `r1-red-vial` (cerrado): `rutas.r1.persistencia` (`cargar_grafo_procesado`, `cargar_lugares_nodos`), `rutas.r1.aristas.mejor_arista` (geometría de cada tramo) y `data/catalogo.csv`.
- `r2-dijkstra` (cerrado): `rutas.r2.adyacencia.construir_adyacencia`, `rutas.r2.dijkstra.consultar` (versión `cola_prioridad`), `rutas.r2.ruta.detalle_ruta` y `rutas.r2.matriz.cargar_matriz`.
- `r3-envolvente-convexa` (cerrado): `data/processed/envolvente.geojson`.
- `r4-ruta-optima` (aprobado; falta su medición real): `rutas.r4.por_ids.resolver_por_ids` e `rutas.r4.itinerario.itinerario_dia`, `visitas_del_catalogo`.
- Los archivos de `results/r1..r4/`.

## Propósito
Una aplicación web local, demostrativa, que muestra los resultados del proyecto:
- la ruta entre dos lugares sobre el mapa, calculada en el momento con Dijkstra con cola de prioridad;
- la envolvente convexa ya calculada;
- el itinerario del día con Held-Karp y con el vecino más cercano, calculado en el momento;
- las tablas y gráficas de R1 a R4.

No implementa algoritmos nuevos: llama a las funciones verificadas de R2 y R4. Se evalúa que muestre los resultados y que arranque siguiendo el README, no el diseño.

## Datos reales (2026-11-11, para dimensionar)
- Cargar el grafo procesado (15 MB, 8 791 nodos) tarda ≈ 1,2 s y construir la adyacencia ≈ 0,01 s: se hace **una sola vez al arrancar**.
- Una consulta de Dijkstra con cola: ≈ 3 ms (C01 → C02: 2 200,2 s).
- `C01 → C12` (Armenia → Salento) = 1 783,39 s (29,7 min); `C12 → C01` = 1 708,19 s (28,5 min).
- `data/processed/` y `results/` están versionados, excepto `results/r4/r4_exactas.csv` y `r4_tiempo_vs_k.png` (pendientes de la medición de R4) y la gráfica de R1 (`r1_tiempos_componente.png` no está en `results/r1/`).

## Entradas y salidas
**Tecnología (decisión del grupo):** Flask 3.1.3 y Folium 0.20.0, ya fijadas en `requirements.txt`. Las plantillas son Jinja2, que viene con Flask. No se agregan dependencias. Las páginas son formularios HTML simples, sin JavaScript propio; el mapa lo genera Folium con Leaflet.

**Arranque:** `.venv/bin/python -m rutas.r5.app [--puerto 5050]`, que abre en `http://127.0.0.1:5050`. Se usa 5050 y no 5000 porque en macOS el 5000 lo ocupa AirPlay.

**Módulos** (`rutas/r5/`):
- `datos.py` → `cargar_datos(processed=DATA_PROCESSED, catalogo=CATALOGO) -> DatosApp`, que se llama una sola vez. `DatosApp` contiene:
  - `G`, `red` (adyacencia de R2) y `catalogo` (DataFrame);
  - `nodo_de` (`{id_lugar: id_nodo}`);
  - `matriz` (DataFrame de R2) y `envolvente` (GeoJSON como dict);
  - `atractivos` (ids cuya categoría es «Atractivo turístico»);
  - `visita_min` (`{id: minutos}`).

  Si falta un archivo, lanza `DatosFaltantes(mensaje)`. El mensaje nombra el archivo y el comando que lo genera (tabla de «Casos borde»).
- `servicios.py`: funciones puras sobre `DatosApp`, que devuelven dicts sin HTML y se prueban sin Flask:
  - `ruta_entre(datos, id_origen, id_destino)` → `{tiempo_s, tiempo_min, distancia_km, nodos_explorados, computo_ms, ids_nodos, coordenadas}`. `coordenadas` = lista de `(lat, lon)` siguiendo la geometría de `mejor_arista` en cada tramo.
  - `itinerario(datos, id_partida, ids_atractivos)` → `{held_karp: {...}, voraz: {...}, diferencia_min, brecha_pct, jornada: {...}}`. Para cada método trae `recorrido` (ids), `desplazamiento_min`, `visitas_min`, `jornada_min`, `cabe`, `computo_ms` y `tramos` (lista de `{desde, hasta, tiempo_min, coordenadas}`, uno por tramo, con Dijkstra con cola). En `jornada` va el resultado de `itinerario_dia` cuando Held-Karp no cabe: `{cabe_inicial, quitados: [{id, lugar, visita_min, desvio_min, ahorro_min}], jornada_final_min, recorrido_final}`.
  - `resultados(requerimiento)` → `{imagenes: [...], tablas: [(nombre, html)], faltantes: [(archivo, comando)]}`, leyendo `results/rX/`.
- `mapas.py`: arma los mapas con Folium y devuelve el HTML del mapa como texto.
  - `mapa_ruta(datos, ruta)`.
  - `mapa_envolvente(datos)`: el polígono y los 42 lugares como marcadores.
  - `mapa_itinerario(datos, it)`: una capa por método, con colores distintos, marcadores numerados según el orden de Held-Karp y un control de capas para alternar entre los dos.
- `app.py`: `crear_app(datos) -> Flask` (fábrica: las pruebas le pasan datos de prueba) y `main()` (lee `--puerto`, llama a `cargar_datos` y arranca). Las rutas son:

| Ruta | Método | Contenido |
|---|---|---|
| `/` | GET | Inicio con enlaces a las cuatro secciones |
| `/ruta` | GET | Formulario (origen y destino entre los 42 lugares, con id y nombre). Con `?origen=…&destino=…`, el mapa y los datos de la ruta |
| `/envolvente` | GET | Mapa con la envolvente y sus datos (vértices, área en km², de `envolvente.geojson`) |
| `/itinerario` | GET | Formulario: partida (cualquiera de los 42 lugares, por defecto C01) y casillas de los 15 atractivos. Con `?partida=…&atractivos=A05&atractivos=…`, el mapa, la tabla comparativa y la jornada |
| `/resultados/<r>` | GET | `r ∈ {r1, r2, r3, r4}`: imágenes, tablas y avisos de archivos faltantes |
| `/resultados/<r>/archivo/<nombre>` | GET | Sirve una imagen de `results/<r>/`, solo si `<nombre>` está en la lista de archivos de ese requerimiento (sin rutas arbitrarias) |

**Salidas en pantalla:**
- **Ruta.** Tiempo de viaje en min con 1 decimal (y en s), distancia en km, ids y nombres de origen y destino. Además, como extra para ilustrar R2: nodos explorados y tiempo de cómputo en ms.
- **Itinerario.** Una tabla con una columna por método. Las filas son:
  - el orden de visita (nombres);
  - el tiempo de desplazamiento (min), las visitas (min) y la jornada (h);
  - si cabe en 11 h;
  - el tiempo de cómputo (ms).

  Debajo, la diferencia voraz − Held-Karp en min y la brecha en %. Si Held-Karp no cabe en 11 h, se agrega el bloque de la regla de R4: qué atractivos quitaría, con visita, desvío y ahorro, y la jornada final. Ese bloque es solo informativo: el mapa sigue mostrando los atractivos que eligió el usuario.
- **Resultados.** Las imágenes PNG del requerimiento y sus CSV convertidos a tablas HTML con `pandas.DataFrame.to_html`, con los textos escapados. Cada tabla lleva el nombre del archivo, y la unidad cuando la columna la trae en el nombre (`tiempo_ms`, etc.).

**Archivos que muestra cada requerimiento** (lista fija en `servicios.py`; si falta alguno, se avisa con el comando):

| r | Imágenes | Tablas (CSV) | Comando si falta |
|---|---|---|---|
| r1 | `r1_tiempos_componente.png` | `r1_tamanos.csv`, `r1_tiempos_componente.csv`, `r1_memoria.csv`, `r1_velocidades.csv` | `python -m rutas.r1.tablas` / `rutas.r1.medir_componente` |
| r2 | `r2_tiempo_vs_explorados.png` | `r2_dijkstra.csv`, `r2_cociente.csv`, `r2_pares.csv` | `python -m rutas.r2.medir_dijkstra` y `rutas.r2.tablas` |
| r3 | `r3_envolvente.png` | `r3_envolvente.csv` | `python -m rutas.r3.medir_envolvente` y `rutas.r3.tablas` |
| r4 | `r4_tiempo_vs_k.png` | `r4_exactas.csv`, `r4_calidad.csv`, `r4_memoria.csv`, `r4_itinerario.csv` | `python -m rutas.r4.medir_exactas` y `rutas.r4.tablas` (calidad, memoria e itinerario con sus scripts) |

El plan confirma los nombres exactos contra `results/` y los README de cada requerimiento. Si el nombre de un archivo existente difiere de esta tabla, gana el archivo real y se anota en el plan. **Puerta 2:** los nombres coinciden. La columna de comandos es orientativa: la lista fija de `servicios.py` lleva **un comando por archivo**, tomado del código real (p. ej. `r1_tamanos.csv`, `r1_memoria.csv` y `r1_velocidades.csv` → `rutas.r1.construir_red`; `r4_calidad.csv` → `rutas.r4.calidad`; `r4_memoria.csv` → `rutas.r4.medir_memoria`; `r4_itinerario.csv` → `rutas.r4.itinerario`); ver `plan.md`, «Archivos de resultados».

## Comportamiento
1. **Carga única.** `main` llama a `cargar_datos` antes de arrancar Flask e imprime cuánto tardó. Ninguna petición vuelve a leer el grafo ni la matriz. Si falta un archivo, `main` imprime el mensaje de `DatosFaltantes` y termina con código 1, sin traza de Python.
2. **Ruta origen–destino.**
   - Cálculo: `consultar(datos.red, nodo_de[o], nodo_de[d], "cola_prioridad")`, en el momento, sin usar la matriz. `computo_ms` = `time.perf_counter` alrededor de esa llamada (es informativo, no es medición del protocolo).
   - Tiempo y distancia: salen de `detalle_ruta(G, ids_nodos)`.
   - Coordenadas: en cada tramo `(u, v)` se usan las coordenadas de `mejor_arista(G, u, v).geometry`, convertidas a `(lat, lon)` y sin repetir el punto de unión entre tramos.
   - Si origen = destino, el tiempo es 0, no se dibuja línea y se muestra el aviso «origen y destino son el mismo lugar». Si los dos lugares están en el mismo nodo (T03 y T05), también da 0, con el aviso «los dos lugares están en el mismo punto de la red».
3. **Envolvente.** Se dibuja el polígono de `envolvente.geojson` (14 vértices) sobre un mapa centrado en el Quindío, con los 42 lugares encima. El texto muestra el número de vértices y el área en km², leídos del GeoJSON.
4. **Itinerario.**
   - Validación: la partida debe ser cualquiera de los 42 lugares. Los atractivos son entre 6 y 8 ids distintos, todos de la categoría «Atractivo turístico» y distintos de la partida. Si algo no cumple, el formulario se vuelve a mostrar con el mensaje (HTTP 400) y no se calcula nada.
   - Held-Karp y voraz: con `resolver_por_ids(datos.matriz, partida, atractivos, "held_karp")` y `"vecino_mas_cercano"`. Cada `computo_ms` es informativo.
   - Tiempos:
     - `desplazamiento_min` = tiempo total / 60;
     - `visitas_min` = Σ `visita_min` de los atractivos, igual en los dos métodos;
     - `jornada_min` = desplazamiento + visitas;
     - `cabe` si la jornada es ≤ 660 min.
   - `diferencia_min` = desplazamiento voraz − desplazamiento Held-Karp, que es ≥ 0. `brecha_pct` = diferencia / desplazamiento HK × 100.
   - Tramos: para dibujar, cada tramo consecutivo del recorrido se calcula con `consultar` (cola de prioridad) y se obtienen sus coordenadas como en el punto 2. El tiempo de cada tramo debe coincidir con la matriz (±1e-6 s), porque R2 la calculó con la misma función.
   - Regla de las 11 h: si Held-Karp no cabe, se llama `itinerario_dia(T, ids, s, atractivos, visita_min)` (la regla de R4, sin cambios) y se muestra su resultado.
5. **Resultados.** Para cada requerimiento se muestran las imágenes y tablas de la lista fija que existan, y por cada una que falte, el aviso con su comando. Nunca hay error 500 por un archivo faltante. Las imágenes se sirven solo desde la lista fija: un nombre fuera de la lista da 404.
6. **Estilo.** Una plantilla base con un menú de 4 enlaces, un CSS mínimo en línea y textos en español. Se prefiere lo legible: cada integrante debe poder explicar cada ruta y cada plantilla en la sustentación.
7. **Extras aprobados por el grupo:**
   - nodos explorados y cómputo en ms en la ruta;
   - brecha % y cómputo en ms en el itinerario;
   - la regla de las 11 h de R4;
   - un `Dockerfile` opcional (enunciado: «Publicarla … en un contenedor Docker es opcional»): imagen `python:3.13-slim`, `pip install -r requirements.txt`, copia el repo con `data/processed` y `results`, y arranca en `0.0.0.0:5050`. Las órdenes `docker build` y `docker run` quedan en el README como alternativa; la vía principal sigue siendo `.venv`.

## Casos borde
- Origen = destino → tiempo 0 y aviso, sin línea (caso 3).
- Dos lugares en el mismo nodo (T03, T05) → tiempo 0 y aviso del mismo punto (caso 4).
- Id de lugar desconocido en `origen`/`destino` → formulario con el mensaje «lugar desconocido: X» y HTTP 400.
- Parámetros incompletos (solo origen) → solo el formulario, sin error.
- Itinerario:
  - con 5 o 9 atractivos, con un repetido, con la partida entre los atractivos o con un id que no es atractivo (p. ej. `C02`) → HTTP 400 con el mensaje;
  - con 8 atractivos que no caben → se muestra la regla de R4;
  - con 6 que caben → sin bloque de regla.
- Archivo procesado faltante → `DatosFaltantes` con el comando. Mapa de archivo → comando:
  - `grafo_componente.graphml`, `lugares_nodos.csv` → `python -m rutas.r1.construir_red`;
  - `matriz_tiempos.csv` → `python -m rutas.r2.matriz`;
  - `envolvente.geojson` → `python -m rutas.r3.archivos`;
  - `data/catalogo.csv` → «está en el repositorio: restaurarlo con git».
- Resultado faltante (p. ej. `r4_exactas.csv` hoy) → aviso con su comando, no error.
- `/resultados/r9` → 404. `/resultados/r1/archivo/../../CLAUDE.md` o un nombre fuera de la lista → 404.
- Puerto ocupado → mensaje que sugiere `--puerto`.

## Casos de prueba
Notación: `M.loc[i, j]` = tiempo de i a j (fila = origen, columna = destino). En pandas, `M[j][i]` lee la columna primero, así que se evita.

Las pruebas sin la marca `red` usan datos de prueba pequeños, construidos por la prueba: un grafo de pocos nodos con geometría, 8 lugares (2 cabeceras y 6 atractivos; corregido en la Puerta 2, porque con menos de 6 atractivos no se puede probar un itinerario válido), una matriz y una envolvente en un GeoJSON escrito en `tmp_path`. Usan el cliente de pruebas de Flask (`app.test_client()`). Las pruebas `red` usan los datos reales.

1. **Ruta real (`red`):** `ruta_entre(datos, "C01", "C12")`:
   - `tiempo_s` = `M.loc["C01", "C12"]` = 1 783,39 s ± 1e-6;
   - `ids_nodos[0]` = `nodo_de["C01"]` y `ids_nodos[-1]` = `nodo_de["C12"]`;
   - `detalle_ruta` da el mismo tiempo;
   - `coordenadas[0]` está a menos de 1e-6 grados del nodo de C01;
   - `nodos_explorados` > 0.

   Y `ruta_entre(datos, "C12", "C01")` = 1 708,19 s (asimetría visible en la app).
2. **Ruta en la app (`red`):** `GET /ruta?origen=C01&destino=C12` → 200, el HTML contiene «29,7» (min, con coma decimal) y el mapa de Folium (`leaflet`).
3. **Origen = destino:** `GET /ruta?origen=C01&destino=C01` → 200, tiempo 0 y el aviso. En datos de prueba también.
4. **Mismo nodo (`red`):** `ruta_entre(datos, "T03", "T05")` → `tiempo_s == 0` y el aviso del mismo punto.
5. **Itinerario que cabe (`red`):** partida C01 con `A05, A14, A06, A07, A13, A15` (calculado con `resolver_por_ids` el 2026-11-11):
   - Held-Karp: desplazamiento **178,66 min**, recorrido `C01, A15, A13, A07, A06, A14, A05, C01`;
   - voraz: **190,45 min**, `C01, A05, A14, A07, A06, A13, A15, C01`;
   - diferencia **11,79 min**, brecha **6,60 %**;
   - visitas 240 min;
   - jornada HK 418,66 min (cabe) y voraz 430,45 min (cabe);
   - sin bloque de regla.
6. **Itinerario que no cabe (`red`):** C01 con `A05, A08, A04, A14, A06, A07, A12, A01`:
   - Held-Karp: desplazamiento **145,22 min**, jornada 1 255,22 min, no cabe;
   - voraz: **155,39 min**;
   - diferencia 10,17 min, brecha 7,01 %;
   - la regla de R4 quita **A01 y luego A12** y termina en **613,13 min** (igual que `results/r4/r4_itinerario.json`).
7. **Tramos del itinerario (`red`):** en el caso 5, cada tramo calculado con Dijkstra = `M.loc[desde, hasta]` ± 1e-6 s, y la suma de tramos = desplazamiento de HK ± 1e-6 s × 60. Lo mismo para el voraz.
8. **Validación del itinerario:** 5 atractivos, 9 atractivos, un repetido, la partida entre los atractivos y `C02` como atractivo → cada uno HTTP 400 con su mensaje, sin llamar a Held-Karp (se comprueba con datos de prueba y un contador o monkeypatch).
9. **Itinerario en la app (`red`):** `GET /itinerario?partida=C01&atractivos=A05&…` (caso 5) → 200, el HTML contiene «178,7», «190,4» y «11,8».
10. **Envolvente:** `GET /envolvente` → 200. Con datos de prueba (un cuadrado de 4 vértices en el GeoJSON), el HTML contiene las 4 coordenadas del polígono y «4 vértices». Con datos reales (`red`): «14 vértices» y el área 1 631,5 km².
11. **Resultados:**
    - `GET /resultados/r2` → 200, con `r2_tiempo_vs_explorados.png` referenciado y la tabla de `r2_cociente.csv`.
    - `GET /resultados/r4` con `r4_exactas.csv` ausente (carpeta de prueba) → 200, con el aviso y el comando `python -m rutas.r4.medir_exactas`.
    - Las cuatro páginas `r1..r4` → 200 con los datos actuales del repo.
12. **Archivos protegidos:** `/resultados/r2/archivo/r2_tiempo_vs_explorados.png` → 200 con `image/png`; `/resultados/r2/archivo/..%2F..%2FCLAUDE.md` y `/resultados/r2/archivo/otro.png` → 404; `/resultados/r9` → 404.
13. **Datos faltantes:** `cargar_datos` con una carpeta `processed` vacía (`tmp_path`) → `DatosFaltantes`, cuyo mensaje contiene `grafo_componente.graphml` y `python -m rutas.r1.construir_red`. `main` con esa carpeta → código de salida 1, sin traza.
14. **Carga única:** con datos de prueba, varias peticiones a `/ruta` y `/itinerario` no vuelven a llamar a `cargar_datos` ni a `cargar_grafo_procesado` (monkeypatch que cuenta llamadas).
15. **Coordenadas siguen la geometría:** en el grafo de prueba, una arista con geometría curva de 3 puntos → `coordenadas` de la ruta tiene esos 3 puntos en orden `(lat, lon)`, sin duplicar los puntos de unión.
16. **Arranque con el README (manual, en la revisión):** en una terminal nueva, seguir solo el README (`.venv`, `pip install -r requirements.txt`, `python -m rutas.r5.app`), abrir `http://127.0.0.1:5050` y comprobar los casos 2, 9, 10 y 11 en el navegador. Lo comprueba el reviewer o el usuario y queda escrito en `review.md`.
17. **Docker (opcional, manual):** `docker build -t rutas-quindio .` y `docker run -p 5050:5050 rutas-quindio` → la app responde en `http://127.0.0.1:5050`. Si Docker no está disponible al revisar, se anota como no comprobado y no bloquea.

## Complejidad esperada
No hay algoritmos nuevos; el informe remite a R2 y R4.
- Arranque: cargar el GraphML es O(V + E) y construir la adyacencia también, ≈ 1,2 s en total.
- Ruta: una consulta de Dijkstra con cola, O((V + E) log V), ≈ 3 ms. Más la geometría, O(largo de la ruta).
- Itinerario con k ≤ 8: Held-Karp O(k²·2^k) ≤ 16 384 transiciones y voraz O(k²), menos de 1 ms. Más k + 1 consultas de Dijkstra por método para dibujar. La regla de las 11 h corre a lo sumo 8 + 7 + … Held-Karp con k ≤ 7. Todo junto queda por debajo de 0,1 s.

## Verificación
- Los casos 1, 5, 6 y 7 comparan con la matriz de R2 y con los resultados de R4 (mismas funciones verificadas, mismos datos).
- Los casos 3, 4, 8, 10 a 15 usan datos de prueba o los archivos del repo.
- El arranque con el README (caso 16) se revisa a mano y queda en `review.md`.

## Medición
No se mide en R5: no se aplica el protocolo de la sección 6. Los `computo_ms` de la pantalla son informativos y no se guardan.

## Pendientes para el documento técnico
- Diagrama de arquitectura (sección 7.1): cómo pasan los datos de R1 a R4 hasta la app.
- Capturas de las cuatro secciones.
- El comando de arranque.

Uso de IA en `docs/anexo-ia.md`.

## Ajuste visual (2026-11-12, aprobado en Puerta 1 del ajuste el 2026-11-12)
Origen: decisión del grupo de mejorar la parte visual con una auditoría y CSS propio (`specs/r5-aplicacion/auditoria-visual.md`, hecha con la skill `web-design-guidelines`). El enunciado no evalúa el diseño en R5. Esto ayuda en la sustentación y en las capturas del documento técnico, pero **no cambia lo que se calcula ni lo que se muestra**. Restricciones:
- sin JavaScript propio (la guardia sigue vigente);
- sin dependencias nuevas;
- sin tocar R1–R4 ni `servicios.py`;
- las pruebas actuales siguen en verde, incluidos los textos «29,7», «178,7», «190,4», «11,8», «14 vértices» y «1 631,5».

V0. **Dirección visual.** Sale de las skills `frontend-design` (anthropics/skills) y `emil-design-eng` (emilkowalski/skill), copiadas a `.claude/skills/` desde VerYganar-frontend el 2026-11-12.
- **Tema:** una herramienta académica sobre la red vial del Quindío. La ven el docente y el jurado en la sustentación. Su único trabajo es mostrar con claridad qué calculó cada algoritmo.
- **Paleta:** inspirada en el Paisaje Cultural Cafetero, evitando a propósito los dos clichés que señala la skill (fondo crema con acento terracota, y fondo negro con acento ácido). Hay 7 colores con nombre en variables CSS (5 base y 2 de método):
  - «Guadua» `#2F4A3A`: menú y títulos.
  - «Hoja» `#5E8C61`: acento y envolvente.
  - «Niebla» `#F3F6F4`: fondo.
  - «Bahareque» `#D5DDD7`: líneas y bordes.
  - «Tinta» `#1D2521`: texto.
  - Métodos: «Cocora» `#1F5F8B` para la ruta y Held-Karp, y «Cereza» `#B8322A` para el voraz.

  `COLORES` de `mapas.py` pasa a usar estos mismos valores.
- **Tipografía:** sin fuentes externas (la app debe funcionar sin internet aparte de los mosaicos del mapa).
  - Títulos: serifa del sistema, `"Iowan Old Style", "Palatino Linotype", Palatino, Georgia, serif`.
  - Texto: `system-ui, sans-serif`.
  - Ids de lugar: `ui-monospace`.
  - Escala de tipos con 4 tamaños.
- **Elemento distintivo (uno solo):** una franja de cabecera con curvas de nivel hechas solo con CSS (`repeating-radial-gradient` en tonos Guadua y Hoja), que evoca la cordillera. Lleva el título y el menú. El resto de la página es sobrio.
- **Movimiento mínimo** (emil-design-eng):
  - botones con `transform: scale(0.97)` en `:active` y `transition: transform 160ms ease-out`;
  - cambios de color al pasar el mouse en 150 ms, solo dentro de `@media (hover: hover) and (pointer: fine)`;
  - nunca `transition: all`;
  - con `prefers-reduced-motion: reduce` se quita la escala y se dejan solo los cambios de color.
- **Textos:** voz activa y verbos concretos. Los errores dicen qué pasó y cómo arreglarlo, sin disculparse.

V1. **Hoja de estilos propia** en `rutas/r5/static/estilos.css`, servida por Flask como estático. `base.html` la enlaza y deja de tener el CSS en línea. Debe ser corta y comentada por secciones, para que cada integrante pueda explicarla. Usa variables CSS para los colores, con la paleta de V0 (5 colores base y los 2 de método, usados también en V5).
V2. **Base:**
- `<meta name="viewport">` y enlace «Saltar al contenido» hacia `<main id="contenido">`;
- menú con `aria-current="page"` en la sección activa (la vista pasa el nombre de la sección) y estados `:hover` y `:focus-visible` en enlaces y botones;
- el menú se adapta (se parte en dos líneas) en pantallas de 375 px de ancho sin desbordarse.
V3. **Formularios:**
- cada `<select>` con `<label for>`;
- las casillas de atractivos en `<fieldset>` + `<legend>` («Atractivos (elige de 6 a 8)»), en una cuadrícula de 2 o 3 columnas, con la duración de visita alineada;
- botones con texto específico: «Calcular ruta» y «Calcular itinerario».
V4. **Resumen destacado:** los números clave van en «tarjetas», un bloque `<dl>` con estilo de tarjeta, con `tabular-nums`:
- en Ruta: tiempo (min), distancia (km) y nodos explorados;
- en Itinerario: Held-Karp, voraz, diferencia y brecha;
- en Envolvente: vértices y área.

El valor que hoy está en texto sigue apareciendo con el mismo formato.
V5. **Itinerario:**
- color fijo para Held-Karp y otro para el voraz, iguales en el mapa (`COLORES` de `mapas.py`), en el encabezado de la tabla y en una **leyenda en HTML** junto al mapa;
- la tabla de comparación con `<caption>`, `<thead>`, `th scope` y sin celda vacía en la esquina («Medida»);
- orden de la página: resumen → mapa → tabla de comparación → regla de las 11 h.
V6. **Mensajes:** el error con `role="alert"` y el aviso con `role="status"`.
V7. **Mapas:** cada `<iframe>` lleva un `title` descriptivo («Mapa de la ruta», «Mapa de la envolvente», «Mapa del itinerario») y una altura que se adapta a la pantalla.
V8. **Tablas:** `<caption>`, `<thead>`, `th scope`, filas alternadas, `tabular-nums` en los números y un contenedor con desplazamiento horizontal para las tablas anchas de pandas.
V9. **Resultados:**
- cada archivo con un **título legible** y una línea que dice de qué se trata (p. ej. `r2_cociente.csv` → «Cociente lineal / cola de prioridad (10 pares cercanos)»), definidos junto a `ARCHIVOS_RESULTADOS` en un diccionario nuevo de `app.py` o de un módulo de presentación, no en `servicios.py`;
- imágenes con `alt` descriptivo, `width`, `height` y `loading="lazy"`;
- navegación entre R1, R2, R3 y R4 dentro de la página.
V10. **Inicio:** cuatro tarjetas (Ruta, Envolvente, Itinerario y Resultados), cada una con una línea de qué hace y el algoritmo que usa. El enlace de Resultados lleva a la navegación de R1 a R4.

**Casos de prueba del ajuste** (cliente de pruebas de Flask, con datos sintéticos salvo que se diga otra cosa):
- A1. `GET /static/estilos.css` → 200 `text/css`. `base.html` lo enlaza y ya no contiene `<style>`.
- A2. Todas las páginas tienen `name="viewport"`, el enlace «Saltar al contenido» y `id="contenido"`.
- A3. `aria-current="page"` en el enlace correcto en `/ruta`, `/envolvente`, `/itinerario` y `/resultados/r2`, y en ningún otro enlace.
- A4. En `/ruta` aparecen `<label for="origen">` y `<label for="destino">`. En `/itinerario` aparecen `<label for="partida">`, `<fieldset>` y `<legend>`. Los botones dicen «Calcular ruta» y «Calcular itinerario».
- A5. Cada `<iframe>` tiene `title`.
- A6. Una entrada inválida en `/itinerario` produce `role="alert"`, y origen = destino produce `role="status"`.
- A7. La leyenda del itinerario usa los mismos colores hexadecimales que `COLORES` de `mapas.py`.
- A8. En `/resultados/r2`, la imagen tiene `alt` distinto del nombre del archivo, `width`, `height` y `loading="lazy"`, y el título de `r2_cociente.csv` es el legible.
- A11. `estilos.css` define las 7 variables de la paleta y no contiene `transition: all` ni `@import` ni `url(http`. `COLORES` de `mapas.py` coincide con «Cocora» y «Cereza».
- A9. La guardia «sin JavaScript propio» sigue en verde: ninguna plantilla ni `estilos.css` contiene `<script` ni `javascript:`.
- A10. Revisión manual del usuario en el navegador, a ancho de escritorio y a unos 375 px (herramientas de desarrollo), anotada en `review.md`. Las capturas para el documento técnico salen de aquí.

## Decisiones
Resueltas por el grupo (2026-11-11):
- Flask + Folium, ya en `requirements.txt`, sin dependencias nuevas.
- Rutas e itinerario dibujados por las vías reales (Dijkstra con cola y la geometría de `mejor_arista`).
- En el itinerario se muestra la jornada con las visitas, si cabe en 11 h, y la regla de R4 solo como información.
- Resultados = PNG más los CSV convertidos a tablas HTML con pandas.
- Alcance: lo pedido más extras útiles (nodos explorados, cómputo en ms, brecha % y Dockerfile opcional).

Puerta 2 (2026-11-11): se aprueban las decisiones 1–9 de `plan.md` (8 lugares sintéticos, comando por archivo, decimales y separador de miles, campos y parámetros extra, `--host` para Docker, comprobación previa del puerto, solo imágenes servidas, pruebas sobre `results/` sin `red`).

Puerta 1 (2026-11-11), aprobadas por el usuario junto con la spec:
- puerto 5050;
- datos de prueba sintéticos para las pruebas sin `red`;
- números con coma decimal en pantalla;
- partida del itinerario = cualquiera de los 42 lugares;
- R5 no modifica módulos de R1 a R4;
- no modificar `.gitignore`.

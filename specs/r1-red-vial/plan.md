# Plan — R1 Modelo de la red vial

Spec: `specs/r1-red-vial/spec.md` (aprobada en Puerta 1, 2026-11-10; decisiones de la Puerta 2 incorporadas). Enunciado: sección 4 (Datos), sección 5 Requerimiento 1 (puntos 1 a 5), sección 6 (protocolo experimental); formato de tablas en el Anexo, Requerimiento 1.

## Resumen

R1 produce los datos de los que dependen R2 a R5. El flujo tiene cuatro etapas, cada una con su propio comando:

1. **Descarga** (`python -m rutas.r1.descargar`): baja el departamento y las 4 redes por radio (`network_type="drive"`, `retain_all=True`) y las guarda crudas en `data/raw/` (fuera de git). Es la única etapa que usa internet.
2. **Construcción** (`python -m rutas.r1.construir_red`): lee la red cruda del departamento (o el GraphML del docente con `--graphml`), valida el catálogo, agrega pesos, extrae la componente, convierte a UTM, ubica los lugares y guarda `data/processed/` (versionado; el GraphML se comprime a `.graphml.gz` si pasa de 100 MB) y los CSV de tamaños, memoria y velocidades.
3. **Medición** (`python -m rutas.r1.medir_componente`): carga las 5 redes crudas desde disco y mide solo `ox.truncate.largest_component(G, strongly=True)`, **en el mismo proceso** (modo (a) de `rutas/medicion.py`).
4. **Tablas** (`python -m rutas.r1.tablas`): genera `results/r1/tablas_r1.md` a partir de los CSV.

En R1 el enunciado **no** pide implementación propia del algoritmo de componentes: pide usar `ox.truncate.largest_component` e investigar qué hace. Lo propio en R1 es la estimación de memoria, la asociación lugar → nodo (búsqueda lineal) y la validación del catálogo. NetworkX y SciPy aparecen solo en las pruebas (componente contra `nx.strongly_connected_components`, vecino más cercano contra `cKDTree`).

## Estado del repositorio que se reutiliza

- `data/catalogo.csv` (42 filas). Textos reales de `categoria`: `"Cabecera municipal"` (12), `"Atractivo turístico"` (15), `"Finca u hotel rural"` (9), `"Centro de acopio o trilladora"` (6). `pandas.read_csv` lee `verificado` como `bool` y `fuente_duracion` empieza siempre por `"Criterio 1:"` … `"Criterio 4:"`. Lat ∈ [4,2065; 4,6771], lon ∈ [−75,8188; −75,4890].
- `.venv` ya tiene todo lo necesario (verificado con `pip freeze`): osmnx 2.1.1, networkx 3.7, numpy 2.5.3, pandas 3.0.5, geopandas 1.2.0, pyproj 3.8.0, scipy 1.18.1, shapely 2.2.0, matplotlib 3.11.2, pytest 9.2.0, psutil 7.2.2, Flask 3.1.3, folium 0.20.0, requests 2.34.2. **No hace falta instalar nada**; solo fijarlas en `requirements.txt`.
- `.gitignore` existe (solo ignora `estudio/`); se le agregan líneas. No hay código, `requirements.txt` ni `docs/anexo-ia.md`.
- `ox.load_graphml` de OSMnx 2.1.1 acepta `graphml_str=` además de `filepath` (verificado en `osmnx/io.py`): así el `.graphml.gz` se lee descomprimiendo en memoria y pasando el texto, con los mismos `node_dtypes`/`edge_dtypes`, sin archivos temporales.
- Lo que consumen los siguientes requerimientos: R2 lee el grafo procesado, `lugares_nodos.csv` y usa `mejor_arista`; R3 lee `x_utm`, `y_utm` de los nodos; R5 usa el grafo, `mejor_arista` (geometría) y las tablas; R2 y R4 usan `rutas/medicion.py`. Por eso `cargar_grafo_procesado`, `cargar_lugares_nodos`, `mejor_arista`, `medir_en_proceso` y `medir_en_hijo` son API pública estable.

## Módulos y archivos

Paquete `rutas/` en la **raíz** del repositorio (no `src/`): así `python -m rutas.r1.<script>` funciona desde la raíz sin instalar el paquete y cualquier integrante lo corre igual. Módulos cortos, uno por idea.

| Ruta | Acción | Responsabilidad | Tipo |
|---|---|---|---|
| `requirements.txt` | crear | Versiones fijadas (lista arriba) | config |
| `pyproject.toml` | crear | Solo configuración de pytest: `pythonpath = ["."]`, `testpaths = ["tests"]`, marcador `red` registrado | config |
| `.gitignore` | modificar | Agregar `data/raw/` (Puerta 2), `cache/` (caché HTTP de OSMnx), `.pytest_cache/`, `__pycache__/`. `data/processed/` **no** se ignora | config |
| `docs/anexo-ia.md` | crear | Encabezado y tabla del registro de uso de IA | doc |
| `rutas/__init__.py` | crear | Vacío | — |
| `rutas/config.py` | crear | Rutas (`RAIZ`, `DATA_RAW`, `DATA_PROCESSED`, `RESULTS_R1`, `CATALOGO`), `EPSG_UTM = 32618`, `UMBRAL_ALERTA_M = 500`, `RADIOS_M = (2000, 5000, 10000, 20000)`, `UMBRAL_GZ_BYTES = 100_000_000`, nombres de archivos crudos | constantes |
| `rutas/medicion.py` | crear | Cronómetro en dos modos (mismo proceso / proceso hijo), mediana, `info_maquina()`. Compartido con R2–R4 | medición |
| `rutas/r1/__init__.py` | crear | Vacío | — |
| `rutas/r1/catalogo.py` | crear | Cargar y validar `catalogo.csv` | datos |
| `rutas/r1/memoria.py` | crear | `estimar_memoria(V, E)`, `filas_memoria(red, V, E)` | algoritmo puro |
| `rutas/r1/pesos.py` | crear | Tabla `VELOCIDADES`, `agregar_pesos`, `maxspeed_original`, verificación de velocidades, resumen por tipo de vía | modelo |
| `rutas/r1/componente.py` | crear | `obtener_componente(G)` (envuelve OSMnx) y `contar(G)` | algoritmo (librería) |
| `rutas/r1/aristas.py` | crear | `mejor_arista(G, u, v)` — usada por R2 y R5 | algoritmo puro |
| `rutas/r1/utm.py` | crear | Conversión EPSG:4326 ↔ EPSG:32618 y `x_utm`, `y_utm` en los nodos | datos |
| `rutas/r1/ubicacion.py` | crear | `nodo_mas_cercano` (búsqueda lineal propia) y `ubicar_lugares` | algoritmo puro |
| `rutas/r1/persistencia.py` | crear | Guardar (con compresión gzip si supera el umbral) y cargar grafo procesado (cualquiera de las dos formas), `lugares_nodos.csv`, `metadatos.json` | E/S |
| `rutas/r1/descarga.py` | crear | Descargas OSMnx con parámetros fijos, `con_reintentos` ante 502/504 (esperas 30, 60, 120, 240 s; Puerta 2), comprobación del polígono, lectura de red cruda / GraphML del docente | E/S |
| `rutas/r1/descargar.py` | crear | Script: descarga las 5 redes a `data/raw/` y escribe `data/raw/descarga.json` | script |
| `rutas/r1/construir_red.py` | crear | Script: pipeline de construcción (etapa 2) | script |
| `rutas/r1/medir_componente.py` | crear | Script: medición (etapa 3), escribe `r1_tiempos_componente.csv` y `maquina.json` | medición |
| `rutas/r1/tablas.py` | crear | Script: Markdown desde CSV (etapa 4) | tablas |
| `tests/conftest.py` | crear | Fábrica de grafos sintéticos y fixtures de datos reales (con `skip` si faltan) | pruebas |
| `tests/test_*.py` | crear | Una por módulo (ver Trazabilidad) | pruebas |
| `README.md` | modificar | Sección corta "Reproducir R1" con los 4 comandos | doc |

Separación exigida por la sección 6: lo medido (`componente.obtener_componente` → `largest_component`) no hace E/S; la carga del archivo, la copia del grafo, el conteo de V y E y la escritura del CSV quedan en `medir_componente.py` fuera del cronómetro; las tablas solo leen CSV.

## Estructuras de datos y firmas

Grafo: `networkx.MultiDiGraph` de OSMnx, que **es** una lista de adyacencia (diccionario de diccionarios: nodo → vecino → clave → atributos). Se usa tal cual porque (a) es la representación elegida en el punto 1, (b) conserva aristas paralelas con su `key` y (c) es lo que `largest_component`, `save_graphml` y R2 esperan. Ids de nodo: `int` (osmid).

```python
# rutas/r1/memoria.py
def estimar_memoria(V: int, E: int) -> dict:
    """{'matriz_bytes': 16*V*V, 'listas_bytes': 24*E + 8*V,
        'matriz_mb': .../1e6, 'listas_mb': .../1e6}  (enteros exactos en bytes)"""
SUPUESTOS: dict[str, str]   # texto del supuesto de cada representación, para el CSV
def filas_memoria(red: str, V: int, E: int) -> list[dict]
    # 2 filas con claves red, V, E, representacion, supuesto, bytes, MB:
    # "Matriz de adyacencia" y luego "Listas de adyacencia", valores de estimar_memoria(V, E).
```
`construir_red` llama a `filas_memoria("Red descargada", V_antes, E_antes) + filas_memoria("Componente fuertemente conexa", V_despues, E_despues)` → 4 filas (Puerta 2). Los nombres de red son los mismos de `r1_tamanos.csv`. "Red descargada" = red cruda del departamento (o el GraphML del docente con `--graphml`); `agregar_pesos` no cambia V ni E.

```python
# rutas/r1/catalogo.py
CATEGORIAS = {"Cabecera municipal": 12, "Atractivo turístico": 15,
              "Finca u hotel rural": 9, "Centro de acopio o trilladora": 6}
MINIMOS    = {... 12, 15, 8, 5}
RECUADRO   = {"lat": (4.0, 4.9), "lon": (-76.0, -75.4)}
class CatalogoInvalido(ValueError): ...
def cargar_catalogo(ruta=CATALOGO) -> pd.DataFrame        # lee y llama a validar_catalogo
def validar_catalogo(df: pd.DataFrame) -> None            # lanza CatalogoInvalido("fila N (id X): <regla>")
```
"Fila" = número de línea del CSV (encabezado = línea 1, primer lugar = línea 2). Reglas en este orden: columnas presentes; 42 filas; `id` únicos; categoría dentro de las 4; conteos exactos (12, 15, 9, 6) y mínimos; atractivo con `duracion_visita_min > 0` y `fuente_duracion` que empiece por `Criterio [1-4]`; `verificado` verdadero (acepta `True` booleano o texto `TRUE/true`); coordenadas en el recuadro. Las reglas globales (conteo de filas o por categoría) usan "fila —" en el mensaje.

```python
# rutas/r1/pesos.py
VELOCIDADES: dict[str, float]   # tabla de la spec, 17 claves (incluye *_link, road y ladder)
def maxspeed_original(valor) -> bool
    # True si OSMnx 2.1.1 obtendría una velocidad numérica de ese maxspeed.
    # Reutiliza ox.routing._collapse_multiple_maxspeed_values y _clean_maxspeed
    # (privadas, versión fijada) para que la marca coincida exactamente con lo que hace OSMnx.
def agregar_pesos(G) -> MultiDiGraph
    # 1) marca 'maxspeed_original' en cada arista (antes de imputar)
    # 2) ox.add_edge_speeds(G, hwy_speeds=VELOCIDADES); 3) ox.add_edge_travel_times(G)
    # 4) verificar_velocidades(G). Devuelve el mismo G.
def verificar_velocidades(G) -> None      # ValueError si algún speed_kph no es finito > 0 o travel_time NaN
def resumen_velocidades(G) -> pd.DataFrame
    # columnas: highway, aristas, con_maxspeed_osm, pct_osm, pct_imputado; fila final "Total".
    # highway lista -> primer elemento (igual que OSMnx).
```

```python
# rutas/r1/componente.py
def obtener_componente(G) -> MultiDiGraph   # return ox.truncate.largest_component(G, strongly=True)
def contar(G) -> tuple[int, int]            # (V, E) con E = G.number_of_edges() (paralelas incluidas)
```

```python
# rutas/r1/aristas.py
@dataclass(frozen=True)
class AristaElegida:
    u: int; v: int; key: int; length: float; travel_time: float; geometry: LineString
def mejor_arista(G, u, v) -> AristaElegida
    # Recorre G[u][v].items(); elige menor (travel_time, key). Sin 'geometry':
    # LineString([(x_u, y_u), (x_v, y_v)]) en lon/lat (mismo CRS que OSMnx).
    # Si no hay arista u->v: KeyError con mensaje claro. Costo: O(número de paralelas).
```
Shapely se usa solo como contenedor de la geometría que OSMnx ya trae (no resuelve ningún algoritmo).

```python
# rutas/r1/utm.py
def transformador(inverso=False) -> pyproj.Transformer   # EPSG:4326 -> EPSG:32618, always_xy=True
def a_utm(lons, lats) -> tuple[np.ndarray, np.ndarray]
def a_latlon(xs, ys) -> tuple[np.ndarray, np.ndarray]
def agregar_utm_a_nodos(G) -> MultiDiGraph               # atributos x_utm, y_utm (float sin redondear)
```

```python
# rutas/r1/ubicacion.py
def nodo_mas_cercano(x: float, y: float, nodos: list[tuple[int, float, float]]) -> tuple[int, float]
    # Búsqueda lineal propia: math.hypot; gana menor distancia y, a igual distancia, menor id.
def ubicar_lugares(catalogo: pd.DataFrame, G) -> pd.DataFrame
    # columnas id_lugar, id_nodo, distancia_al_nodo_m, alerta_500m (distancia > 500, estricto)
```
La lista `nodos` se arma una vez con `(id, x_utm, y_utm)` de la componente: es Θ(V) de memoria auxiliar para la entrada, y la búsqueda en sí es Θ(1) adicional, como dice la spec.

```python
# rutas/r1/persistencia.py
NOMBRE_GRAFO = "grafo_componente.graphml"          # forma comprimida: NOMBRE_GRAFO + ".gz"
def guardar_grafo(G, carpeta, umbral_bytes=UMBRAL_GZ_BYTES) -> Path
    # 1) ox.save_graphml(G, carpeta / NOMBRE_GRAFO)
    # 2) si el archivo pesa más de umbral_bytes: lo comprime a NOMBRE_GRAFO.gz
    #    (gzip.GzipFile(..., mtime=0) para que el .gz sea idéntico entre corridas iguales)
    #    y borra el .graphml; si no: borra un .gz viejo si existía.
    # Nunca quedan las dos formas. Devuelve la ruta del archivo que quedó.
def cargar_grafo_procesado(carpeta=DATA_PROCESSED) -> MultiDiGraph
    # Busca NOMBRE_GRAFO; si no está, NOMBRE_GRAFO.gz; si están ambos -> ValueError (ambiguo);
    # si no hay ninguno -> FileNotFoundError.
    # .graphml: ox.load_graphml(ruta, ...)
    # .gz:      ox.load_graphml(graphml_str=gzip.open(ruta, "rt", encoding="utf-8").read(), ...)
    # En ambos: node_dtypes={"x_utm": float, "y_utm": float},
    #           edge_dtypes={"maxspeed_original": _texto_a_bool}
def guardar_procesado(G, lugares: pd.DataFrame, metadatos: dict, carpeta=DATA_PROCESSED,
                      umbral_bytes=UMBRAL_GZ_BYTES) -> Path
    # guardar_grafo + lugares_nodos.csv + metadatos.json (agrega archivo_grafo y comprimido: bool)
def cargar_lugares_nodos(carpeta=DATA_PROCESSED) -> pd.DataFrame   # id_nodo int, distancia float, alerta bool
def cargar_metadatos(carpeta=DATA_PROCESSED) -> dict
```
Sin `round` ni `float_format`: `save_graphml` escribe `str(float)` (representación más corta que vuelve exacta) y `DataFrame.to_csv` sin `float_format` también. La compresión gzip no cambia el texto, así que las dos formas cargan el mismo grafo bit a bit; la prueba usa tolerancia 1e-9 como pide la decisión. El umbral es parámetro para poder forzar la compresión en pruebas (`umbral_bytes=0`).

```python
# rutas/r1/descarga.py
# con_reintentos(funcion, esperas=(30, 60, 120, 240), dormir=time.sleep) -> resultado de funcion()
#   reintenta solo si codigo_http(error) in {502, 504}; tras agotar esperas relanza con mensaje (n intentos, Plan B GraphML)
# codigo_http(error) -> int | None   (e.response.status_code o el número en el mensaje de ResponseStatusCodeError)
# Nota: OSMnx 2.1.1 ya reintenta 429/504 de Overpass cada 55 s sin límite; ver spec, casos borde.
LUGAR = "Quindío, Colombia"
PARAMETROS = {"network_type": "drive", "retain_all": True, "simplify": True}
def centro_plaza_bolivar(catalogo) -> tuple[float, float]       # (lat, lon) de C01
def comprobar_poligono_departamento(gdf) -> dict
    # exige addresstype == "state" y área en UTM entre 1 500 y 2 200 km² (Quindío ≈ 1 845 km²);
    # devuelve {display_name, addresstype, area_km2} para metadatos; si no, ValueError.
def descargar_departamento() -> MultiDiGraph     # ox.graph_from_place(LUGAR, **PARAMETROS)
def descargar_radio(centro, dist_m) -> MultiDiGraph
    # ox.graph_from_point(centro, dist=dist_m, dist_type="bbox", **PARAMETROS)
def cargar_red_cruda(ruta) -> MultiDiGraph        # ox.load_graphml; sirve también para el GraphML del docente
```

```python
# rutas/medicion.py  (compartido R1–R4; material de sustentación: corto y legible)
@dataclass
class ResultadoMedicion:
    tiempo_ms: float | None      # mediana; None si no completada
    repeticiones: int            # 5, 1 o 0
    completada: bool
    tiempos_ms: list[float]

# Modo (a): mismo proceso. R1, Dijkstra con cola (R2), envolvente (R3).
def medir_en_proceso(funcion, preparar, repeticiones=5, umbral_una_s=60.0,
                     limite_s=300.0) -> ResultadoMedicion

# Modo (b): proceso hijo. Solo Dijkstra lineal (R2) y fuerza bruta / Held-Karp (R4).
def medir_en_hijo(funcion, args=(), repeticiones=5, umbral_una_s=60.0,
                  limite_s=300.0) -> ResultadoMedicion

def info_maquina() -> dict       # procesador, ram_gb, so, python
```

Modo (a), en pseudocódigo (es todo el algoritmo):
```
para i en 0..repeticiones-1:
    args = preparar()                 # fuera del cronómetro (en R1: (G.copy(),))
    t0 = perf_counter_ns(); funcion(*args); t1 = perf_counter_ns()
    guardar (t1 - t0) / 1e6
    si i == 0 y la medida > umbral_una_s: parar (una sola repetición)
si la única/primera medida > limite_s: completada = False   # no se puede interrumpir en el mismo
                                                            # proceso; se reporta después
mediana con statistics.median
```

Modo (b): por cada repetición, `ctx = multiprocessing.get_context("spawn")`, `cola = ctx.Queue()`, `p = ctx.Process(target=_cronometrar_en_hijo, args=(funcion, args, cola))`, `p.start()`, `p.join(timeout=limite_s)`. Si `p.is_alive()` → `p.terminate(); p.join()` y se devuelve "no completada" (`tiempo_ms=None`, `repeticiones=0`). Si `p.exitcode != 0` → `RuntimeError` (el algoritmo falló en el hijo). Si no, `ns = cola.get()`. El hijo es una función de módulo de 3 líneas:
```python
def _cronometrar_en_hijo(funcion, args, cola):
    t0 = time.perf_counter_ns(); funcion(*args); t1 = time.perf_counter_ns()
    cola.put(t1 - t0)
```
Así el cronómetro queda **dentro** del hijo, alrededor de la llamada: arrancar el intérprete, importar módulos y deserializar `args` no cuentan. Cada hijo recibe su propia copia de `args` (se serializan al crearlo), así que no hace falta `preparar`. `funcion` y `args` deben ser serializables con `pickle` (funciones de módulo, no lambdas). Solo se envía un entero por la cola, así que `join` antes de `get` no se bloquea. Mismas reglas de repetición que el modo (a): 5, mediana, una sola si la primera pasa de `umbral_una_s`.

## Algoritmos, recurrencia y complejidad

| Algoritmo | Tiempo | Memoria adicional | Fuente a citar |
|---|---|---|---|
| `largest_component(G, strongly=True)`: `is_strongly_connected` + `strongly_connected_components` (Tarjan iterativo con mejoras Tarjan–Zwick) + `max` + `MultiDiGraph(G.subgraph(cc))` | Θ(V + E) | Θ(V) (preorden/`lowlink`, pila DFS, pila de componente) + Θ(V' + E') del subgrafo copiado | Tarjan 1972 (*SIAM J. Comput.* 1(2):146–160); Tarjan y Zwick 2024 (*Eur. J. Comb.* 119, doi:10.1016/j.ejc.2023.103815); código `networkx/algorithms/components/strongly_connected.py` (NX 3.7) y `osmnx/truncate.py` (OSMnx 2.1.1) |
| Pesos (`add_edge_speeds` + `add_edge_travel_times`) | Θ(E) (más el `groupby` por tipo de vía de pandas, O(E) con hash) | Θ(E) (GeoDataFrame de aristas) | `osmnx/routing.py` 2.1.1 |
| Conversión UTM | Θ(V + P) | Θ(V + P) | documentación de pyproj |
| Vecino más cercano lineal | Θ(P · V), P = 42 | Θ(1) por consulta | análisis propio (recorrido de V elementos por lugar) |
| `mejor_arista` | O(k), k = paralelas u→v (k ≤ 2 o 3 en la práctica) | Θ(1) | análisis propio |
| `estimar_memoria`, `filas_memoria` | Θ(1) | Θ(1) | — |
| Compresión gzip del GraphML (solo si > 100 MB) | Θ(tamaño del archivo) | Θ(1) en streaming al escribir; Θ(tamaño) al leer (texto completo en memoria para `graphml_str`) | documentación de `gzip` (DEFLATE, RFC 1951/1952) |

No hay algoritmo recursivo ni de programación dinámica en R1, así que no aplica recurrencia. La DFS de Tarjan en NetworkX 3.7 es iterativa (no hay límite de recursión de Python): mencionarlo en el informe.

## Datos y archivos

| Archivo | Lo escribe | En git | Formato |
|---|---|---|---|
| `data/raw/departamento.graphml`, `data/raw/radio_2km.graphml`, `radio_5km`, `radio_10km`, `radio_20km` | `descargar.py` | no (`.gitignore`) | GraphML de `ox.save_graphml`, red cruda (`retain_all=True`), sin pesos |
| `data/raw/descarga.json` | `descargar.py` | no | `fecha_descarga` (ISO 8601), `osmnx`, `networkx`, `lugar`, `centro` (lat, lon de C01), `radios_m`, `parametros`, `poligono` (display_name, addresstype, area_km2) |
| `data/processed/grafo_componente.graphml` **o** `grafo_componente.graphml.gz` (nunca ambos) | `construir_red.py` | sí | Spec: nodos `y, x, x_utm, y_utm`; aristas `length, speed_kph, travel_time, highway, maxspeed_original` + lo que trae OSMnx (`geometry`, `osmid`, `oneway`, `key`…). `.gz` si el `.graphml` pasa de 100 000 000 B |
| `data/processed/lugares_nodos.csv` | `construir_red.py` | sí | `id_lugar,id_nodo,distancia_al_nodo_m,alerta_500m`, orden del catálogo |
| `data/processed/metadatos.json` | `construir_red.py` | sí | contenido de `descarga.json` (o `"fuente": "GraphML del docente"` + ruta si se usó `--graphml`) + `V_antes, E_antes, V_despues, E_despues`, `ya_fuertemente_conexa`, `archivo_grafo`, `comprimido` |
| `results/r1/r1_tamanos.csv` | `construir_red.py` | sí | `red,nodos,aristas`; filas `Red descargada`, `Componente fuertemente conexa` |
| `results/r1/r1_memoria.csv` | `construir_red.py` | sí | `red,V,E,representacion,supuesto,bytes,MB`; 4 filas en este orden: (Red descargada, Matriz de adyacencia), (Red descargada, Listas de adyacencia), (Componente fuertemente conexa, Matriz…), (Componente fuertemente conexa, Listas…). `bytes` entero, `MB = bytes / 1e6` |
| `results/r1/r1_velocidades.csv` | `construir_red.py` | sí | `highway,velocidad_tabla_kmh,aristas,con_maxspeed_osm,pct_osm,pct_imputado` + fila `Total` (sobre la componente; porcentajes a 1 decimal) |
| `results/r1/r1_tiempos_componente.csv` | `medir_componente.py` | sí | `red,V,E,V_mas_E,tiempo_ms,tiempo_por_elemento_us,repeticiones`; filas `Radio de 2 km`, `Radio de 5 km`, `Radio de 10 km`, `Radio de 20 km`, `Departamento completo`; V y E de la **red cruda** medida; si no completada: `tiempo_ms = "no completada"`, `tiempo_por_elemento_us` vacío, `repeticiones = 0` |
| `results/r1/maquina.json` | `medir_componente.py` | sí | `procesador, ram_gb, so, python` |
| `results/r1/tablas_r1.md` | `tablas.py` | sí | Tablas Markdown: tamaños, tiempos (ms y µs/elemento), memoria (red, V, E, representación, B y MB), velocidades (%), lugares con `alerta_500m` (desde `lugares_nodos.csv` + nombre del catálogo) |

Sin datos aleatorios en R1: no hay semilla. La fecha de descarga queda en `descarga.json` y `metadatos.json` (este último sí está en git, así que la fecha de los datos procesados queda registrada aunque `data/raw/` no se versione).

## Verificación

| Qué | Contra qué | Datos |
|---|---|---|
| `estimar_memoria`, `filas_memoria` | cálculo a mano | casos 1 y 1b |
| Pesos | cálculo a mano (velocidad → tiempo) | grafos sintéticos: casos 2, 3, 4, 4b, longitud 0, `highway` lista, tipo fuera de tabla |
| Pesos en la red real | fórmula `length / (speed_kph / 3.6)` | grafo procesado, caso 14 |
| Componente | `max(nx.strongly_connected_components(G), key=len)` (mismo conjunto de nodos) y conteos a mano | casos 5, 6 y red cruda de radio 2 km |
| `mejor_arista` | caso a mano | caso 11b |
| UTM | `pyproj` directo, ida y vuelta, valor de referencia | caso 10 con C01, A03, A10 |
| Vecino más cercano | caso a mano; `scipy.spatial.cKDTree` (solo en la prueba) | casos 7–9; caso 15 con los 42 lugares reales |
| Persistencia | igualdad arista por arista tras guardar/cargar; `.graphml` vs `.graphml.gz` (umbral forzado a 0) | casos 4c, 11, 11b (sintético) y 11 (real) |
| Catálogo | reglas de la spec | caso 12 (real y mutaciones del real) |
| Parámetros de descarga | doble (mock) de `ox.graph_from_place` / `graph_from_point` | caso 13 |
| `medir_en_proceso`, `medir_en_hijo` | `time.sleep` con duraciones conocidas | pruebas propias de `medicion.py` |

Las pruebas sin internet usan grafos sintéticos construidos en `tests/conftest.py` (una fábrica `grafo_sintetico(nodos, aristas)` que pone `G.graph["crs"] = "epsg:4326"` y `x, y` en cada nodo, porque `add_edge_speeds` llama a `graph_to_gdfs`). Las pruebas con la red real llevan `@pytest.mark.red` y una fixture que hace `pytest.skip` si falta `data/processed/` o `data/raw/radio_2km.graphml`. Comandos: `.venv/bin/python -m pytest -m "not red"` (sin internet ni datos) y `.venv/bin/python -m pytest` (todo).

## Medición (sección 6)

- **Modo**: (a) mismo proceso, con `medir_en_proceso` (Puerta 2). R1 tarda milisegundos o segundos; el modo hijo no aporta nada aquí.
- **Qué**: solo `obtener_componente(G)` = `ox.truncate.largest_component(G, strongly=True)`, los tres pasos (comprobación, componentes, subgrafo).
- **Fuera del cronómetro**: descarga (etapa aparte), `ox.load_graphml` (una vez por red, antes de medir), la copia `G.copy()` en `preparar` de cada repetición, conteo de V y E, escritura de CSV.
- **Copia nueva por repetición**: `preparar = lambda: (G.copy(),)` (o `functools.partial`), así ninguna repetición recibe un grafo tocado por la anterior.
- **Repeticiones**: 5, mediana; si la primera pasa de 60 s, una sola; si pasa de 300 s → `"no completada"` (en el modo (a) se reporta después de terminar; no se espera que ocurra).
- **Unidad**: ms (`perf_counter_ns / 1e6`); `tiempo_por_elemento_us = tiempo_ms · 1000 / (V + E)`.
- **Máquina**: `maquina.json` con `platform`, `psutil.virtual_memory().total` y, en macOS, `sysctl -n machdep.cpu.brand_string` para el procesador.
- **Análisis** (en el informe, no en código): comparar `tiempo_por_elemento_us` entre filas; `metadatos`/la propia prueba indican si alguna red ya era fuertemente conexa.
- **Modo (b)** se implementa y prueba en R1 (T15b) porque `rutas/medicion.py` es compartido, pero R1 no lo usa; lo usarán R2 (Dijkstra lineal) y R4 (fuerza bruta, Held-Karp).

## Trazabilidad

| Caso de la spec | Tarea | Prueba |
|---|---|---|
| 1 | T2 | `tests/test_memoria.py::test_caso_1_v1000_e2500` |
| 1b | T2 | `tests/test_memoria.py::test_caso_1b_v30000_e75000` |
| Memoria con dos redes (Puerta 2) | T2, T12, T17 | `tests/test_memoria.py::test_filas_memoria_dos_filas`; `tests/test_construir_red.py::test_memoria_cuatro_filas_dos_redes`; `tests/test_tablas.py::test_memoria_muestra_ambas_redes` |
| 2 | T4 | `tests/test_pesos.py::test_caso_2_maxspeed_36_da_100s` |
| 3 | T4 | `tests/test_pesos.py::test_caso_3_maxspeed_30mph` |
| 4 | T4 | `tests/test_pesos.py::test_caso_4_tabla_por_tipo` (parametrizada: residential, primary, primary_link, track) |
| 4b | T4 | `tests/test_pesos.py::test_caso_4b_maxspeed_lista_y_none` |
| 4d | T4 | `tests/test_pesos.py::test_caso_4d_ladder_20_kmh`, `tests/test_red_real.py::test_caso_4d_ladder_real_20_kmh` |
| 4e | T5, T12 | `tests/test_construir_red.py::test_caso_4e_formato_de_velocidades_csv` |
| 4c | T10 | `tests/test_persistencia.py::test_caso_4c_paralelas_sobreviven` |
| 5 | T6 | `tests/test_componente.py::test_caso_5_componente_abc` |
| 6 | T6 | `tests/test_componente.py::test_caso_6_ya_fuertemente_conexa` |
| 7 | T9 | `tests/test_ubicacion.py::test_caso_7_vecino_mas_cercano` |
| 8 | T9 | `tests/test_ubicacion.py::test_caso_8_alerta_y_frontera_500` |
| 9 | T9 | `tests/test_ubicacion.py::test_caso_9_empate_menor_id` |
| 10 | T8 | `tests/test_utm.py::test_caso_10_catalogo_contra_pyproj`, `::test_caso_10_ida_y_vuelta`, `::test_caso_10_rango_recuadro` |
| 11 (sintético) | T10 | `tests/test_persistencia.py::test_caso_11_guardar_cargar_sintetico` |
| 11 con `.gz` (Puerta 2) | T10 | `tests/test_persistencia.py::test_gz_y_sin_comprimir_dan_el_mismo_grafo`, `::test_umbral_no_superado_no_comprime`, `::test_nunca_quedan_las_dos_formas`, `::test_cargar_con_ambas_formas_es_error` |
| 11 (real) | T14 | `tests/test_red_real.py::test_caso_11_guardar_cargar_real` |
| 11b | T7, T10 | `tests/test_aristas.py::test_caso_11b_menor_tiempo`, `::test_caso_11b_empate_menor_key`, `::test_caso_11b_sin_geometria_segmento_recto`; `tests/test_persistencia.py::test_caso_11b_tras_guardar_cargar` |
| 12 | T3 | `tests/test_catalogo.py::test_caso_12_catalogo_real`, `::test_caso_12_id_repetido`, `::test_caso_12_categoria_invalida`, `::test_caso_12_latitud_fuera` |
| 13 | T11 | `tests/test_descarga.py::test_caso_13_parametros_de_las_5_descargas` |
| 16 | T11 | `tests/test_descarga.py::test_caso_16a…16e_*` |
| 14 | T14 | `tests/test_red_real.py::test_caso_14_velocidades_y_tiempos` |
| 15 | T14 | `tests/test_red_real.py::test_caso_15_asociacion_contra_ckdtree` |
| Componente radio 2 km vs NetworkX | T14 | `tests/test_red_real.py::test_componente_radio_2km_igual_a_networkx` |
| Borde: velocidad finita > 0, tipo fuera de tabla | T4 | `tests/test_pesos.py::test_tipo_fuera_de_tabla_se_imputa`, `::test_velocidad_invalida_lanza_error` |
| Borde: `highway` lista | T4 | `tests/test_pesos.py::test_highway_lista_usa_primero` |
| Borde: longitud 0 | T4 | `tests/test_pesos.py::test_longitud_cero_tiempo_cero` |
| Borde: lugar sobre un nodo | T9 | `tests/test_ubicacion.py::test_lugar_sobre_nodo_distancia_cero` |
| Borde: descarga falla → GraphML docente | T11, T12 | `tests/test_descarga.py::test_cargar_graphml_docente`, `tests/test_construir_red.py::test_pipeline_con_graphml` |
| Borde: polígono no es el departamento | T11 | `tests/test_descarga.py::test_poligono_municipio_falla` |
| `data/raw/` fuera de git (Puerta 2) | T1 | `tests/test_config.py::test_gitignore_excluye_data_raw` |
| Punto 5: V, E antes y después, metadatos | T12 | `tests/test_construir_red.py::test_pipeline_sintetico_escribe_salidas` |
| Velocidades por tipo (CSV) | T5 | `tests/test_pesos.py::test_resumen_velocidades` |
| Medición modo (a), mismo proceso (Puerta 2) | T15 | `tests/test_medicion.py::test_en_proceso_*`, `::test_info_maquina_tiene_campos` |
| Medición modo (b), proceso hijo (Puerta 2) | T15b | `tests/test_medicion.py::test_en_hijo_*` |
| Medición de R1 (sección 6) | T16 | `tests/test_medir_componente.py::*` |
| Tablas desde CSV | T17 | `tests/test_tablas.py::*` |

Puntos del R1 → tareas: punto 1 (memoria) T2, T12, T17; punto 2 (pesos) T4, T5, T12, T14; punto 3 (componente y medición) T6, T14, T15, T16, T18; punto 4 (ubicación) T8, T9, T14; punto 5 (persistencia) T10, T12, T13; sección 4 (catálogo) T3; sección 6 T15, T15b, T16, T17, T18.

## Riesgos

- **Tamaño de `grafo_componente.graphml`**: resuelto por la Puerta 2 (gzip si pasa de 100 MB). El GraphML es texto XML muy repetitivo; gzip suele reducirlo de 5 a 10 veces, así que el `.gz` debería quedar muy por debajo de 100 MB. Si aun comprimido pasara de 100 MB, GitHub lo rechazaría: T13 lo comprueba y, solo en ese caso, se reporta al usuario.
- **Lectura del `.gz`**: `load_graphml(graphml_str=...)` carga el texto completo en memoria (decenas o cientos de MB en el peor caso); aceptable en un portátil, y solo pasa si el archivo es grande.
- **Diffs de git del `.gz`**: sin `mtime=0` el `.gz` cambiaría en cada corrida aunque el grafo fuera igual; por eso se fija.
- **Umbral 100 MB**: se usa 100 000 000 B (decimal, como el resto de MB del proyecto), un poco por debajo del límite real de GitHub (100 MiB = 104 857 600 B), así que es conservador.
- **Modo (a) no puede interrumpir**: si una repetición en el mismo proceso tardara más de 5 min, se espera a que termine y se marca "no completada". Para R1 no se espera (lineal, segundos); por eso los algoritmos que sí pueden acercarse al límite usan el modo (b).
- **Modo (b) y `spawn`**: `funcion` y `args` deben ser serializables (funciones de módulo). Las pruebas usan `time.sleep` y `math.sqrt` (built-ins), que lo son; en R2/R4 los algoritmos son funciones de módulo. En macOS el arranque de un hijo `spawn` cuesta del orden de 50–300 ms, que **no** entra en la medida (lo comprueba la prueba de 50 ms).
- **Funciones privadas de OSMnx** (`_clean_maxspeed`, `_collapse_multiple_maxspeed_values`) para `maxspeed_original`: estables con la versión fijada; una prueba (T4) fija su comportamiento, así que un cambio de versión se detecta.
- **`addresstype` de Nominatim**: si Nominatim no devolviera `"state"` para Quindío, la comprobación del polígono fallaría con un mensaje claro; se ajusta la regla (no se ignora) y se anota.
- **Caso 4c necesita una arista de vuelta** (aceptado): la prueba agrega B→A (clave 0) para que A y B queden en la componente; las dos paralelas A→B son lo que se comprueba.
- **Tiempos de la red completa**: `largest_component` en el departamento debería tardar segundos; no se espera tocar el límite. Si la descarga del departamento falla, se usa el GraphML del docente (`--graphml`) y para la medición se copia a `data/raw/departamento.graphml`.
- **Fechas distintas**: si se descarga otra vez, cambian V, E y las distancias de A03/A10/A11; por eso las pruebas reales comparan contra la propia salida, no contra números fijos.

## Decisiones

Aceptadas por el usuario (Puerta 2): 1) paquete `rutas/` en la raíz; 2) descarga en etapa aparte con redes crudas en `data/raw/`; 3) `maxspeed_original` reutilizando funciones privadas de OSMnx 2.1.1 con prueba que fija el comportamiento; 4) criterio del polígono (`addresstype == "state"`, área 1 500–2 200 km²); 5) "fila" = línea del CSV; 6) `r1_velocidades.csv` sobre la componente; 7) caso 4c con B→A. Además: memoria con 4 filas (dos redes), `data/raw/` en `.gitignore`, `data/processed/` versionado con `.gz` si pasa de 100 MB, y cronómetro en dos modos con R1 en el mismo proceso.

Tomadas en el plan, pendientes de confirmar (no bloquean):

- En `r1_tiempos_componente.csv`, V y E son los de la red **cruda** medida (la entrada de la función).
- Umbral de compresión = 100 000 000 B (decimal). Si ya existen ambas formas del grafo al cargar, error en lugar de elegir una.
- `cargar_grafo_procesado` y `cargar_lugares_nodos` reciben la **carpeta** (no la ruta del archivo), porque el nombre del grafo depende de si está comprimido.

## Bloqueos

Ninguno. La spec no contradice el enunciado (secciones 4, 5-R1 y 6 revisadas en el PDF).

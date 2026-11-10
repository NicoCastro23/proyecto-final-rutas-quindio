# Plan — R2 Caminos mínimos (Dijkstra y matriz de tiempos)

Spec: `specs/r2-dijkstra/spec.md` (aprobada en Puerta 1, 2026-11-10, con tres ajustes; decisiones de la Puerta 2 del 2026-11-10 incorporadas). Enunciado: sección 5, Requerimiento 2 (punto 1 con sus tres viñetas, matriz de tiempos y verificación); sección 6 (protocolo experimental); formatos en el Anexo, Requerimiento 2 (archivo de mediciones, gráfica, cociente y matriz).

## Resumen

R2 toma la componente de R1 y hace cuatro cosas, cada una con su comando:

1. **Algoritmos** (sin comando, solo funciones puras): representación **indexada** propia (`construir_adyacencia` → `Red(ids, indice, adyacencia)`), `dijkstra_lineal` y `dijkstra_cola` sobre índices (implementación propia; `heapq` es la estructura de apoyo permitida), `reconstruir_ruta`, el envoltorio `consultar` (ids ↔ índices) y `detalle_ruta`.
2. **Matriz** (`python -m rutas.r2.matriz`): 42 corridas de `dijkstra_cola` sin destino → `data/processed/matriz_tiempos.csv` (la usa R4) y `results/r2/r2_asimetria.json`. No es una medición de tiempo.
3. **Medición** (`python -m rutas.r2.medir_dijkstra`): elige los 20 pares con semilla 2026, mide la cola en los 20 (en el mismo proceso) y la lineal en los 10 cercanos (en proceso hijo), comprueba que las dos versiones coinciden y escribe `r2_pares.csv/json`, `r2_dijkstra.csv` y `maquina.json`. **La corre el usuario con el portátil enchufado.**
4. **Tablas** (`python -m rutas.r2.tablas`): desde los CSV/JSON genera `r2_cociente.csv`, la gráfica `r2_tiempo_vs_explorados.png` y `tablas_r2.md` (como `rutas/r1/tablas.py`).

No hay contradicción entre la spec y el enunciado (la spec elige los cercanos del mismo municipio, que el enunciado admite: «del mismo municipio o de municipios vecinos»). Sin bloqueos.

## Estado del repositorio que se reutiliza

- `rutas/config.py` (`RAIZ`, `DATA_PROCESSED`, `CATALOGO`, `RESULTS_R1`): se le agregan `RESULTS_R2` y `MATRIZ_TIEMPOS`.
- `rutas/medicion.py`: `medir_en_proceso(funcion, preparar, repeticiones=5, ...)`, `medir_en_hijo(funcion, args=(), repeticiones=5, ...)` (cronómetro dentro del hijo, `spawn`, límite 300 s → `NO_COMPLETADA`), `ResultadoMedicion`, `info_maquina()`. Se usan sin cambios.
- `rutas/r1/persistencia.py`: `cargar_grafo_procesado()` (MultiDiGraph, ids `int`, `travel_time`/`length` `float`), `cargar_lugares_nodos()` (`id_lugar, id_nodo, distancia_al_nodo_m, alerta_500m`, `round_trip`).
- `rutas/r1/catalogo.py`: `cargar_catalogo()` (columnas `id, nombre, municipio, categoria, ...`; 42 filas en el orden del catálogo).
- `rutas/r1/aristas.py`: `mejor_arista(G, u, v)` → `AristaElegida(u, v, key, length, travel_time, geometry)`.
- `rutas/r1/tablas.py`: `a_markdown(df, decimales)` se importa para las tablas de R2.
- `tests/conftest.py`: `grafo_sintetico(nodos, aristas)` (función, se importa con `from tests.conftest import ...`) y la fixture `grafo_procesado_real` (se salta si falta el grafo). Marcador `red` ya registrado en `pyproject.toml`.
- Datos reales comprobados: V = 8 791, E = 20 132 (`metadatos.json`); 12 municipios, todos con ≥ 2 lugares (Armenia 7, Calarcá 7, Quimbaya 5, Salento 4, Filandia/Montenegro/Pijao 3, Buenavista/Circasia/Córdoba/Génova/La Tebaida 2); el único nodo compartido es 2978288220 (T03 y T05, ambos de Armenia).
- `estudio/casos_prueba.json` (ignorado por git): secciones `red` (9 nodos, 24 aristas) y `R2` (`matriz_min`, `explorados_con_parada`, `cola_origen_2`, `arista_paralela`). Los casos 19–21 se comprobaron con una cola perezosa sobre la componente 1–7 (22 aristas): orden 1, 2, 3, 4, 5, 7, 6; 9 extracciones y 2 obsoletas desde 2; explorados con parada 2, 3, 4, 5, 7, 6.

## Módulos y archivos

Subpaquete `rutas/r2/`, un módulo por idea. Los algoritmos (`adyacencia.py`, `dijkstra.py`) no hacen E/S ni importan NetworkX; la medición y las gráficas están en módulos aparte porque solo se cronometra el algoritmo. (El módulo se llama `adyacencia.py` y no `red.py`/`construir_red` para no confundirlo con `rutas/r1/construir_red.py`.)

| Ruta | Acción | Responsabilidad | Tipo |
|---|---|---|---|
| `rutas/config.py` | modificar | Agregar `RESULTS_R2 = RAIZ / "results" / "r2"` y `MATRIZ_TIEMPOS = DATA_PROCESSED / "matriz_tiempos.csv"` | constantes |
| `rutas/r2/__init__.py` | crear | Vacío | — |
| `rutas/r2/adyacencia.py` | crear | `Red` (NamedTuple `ids, indice, adyacencia`) y `construir_adyacencia(G, peso="travel_time")` con la validación de pesos | preparación de datos (fuera del cronómetro) |
| `rutas/r2/dijkstra.py` | crear | `dijkstra_lineal`, `dijkstra_cola` (sobre índices), `reconstruir_ruta` y, al final y separado, el envoltorio `consultar(red, id_origen, id_destino, version)`. Las dos versiones una debajo de la otra, cortas, con la misma estructura | **algoritmo puro** + envoltorio |
| `rutas/r2/ruta.py` | crear | `detalle_ruta(G, ruta)` (ruta en ids) con `mejor_arista` (lo que dibuja R5) | apoyo (usa el grafo) |
| `rutas/r2/pares.py` | crear | `SEMILLA = 2026`, `seleccionar_pares(catalogo, lugares_nodos, semilla=SEMILLA)` | datos |
| `rutas/r2/matriz.py` | crear | `calcular_matriz`, `guardar_matriz`, `cargar_matriz`, `asimetria`, `main` (script) | datos + script |
| `rutas/r2/medir_dijkstra.py` | crear | `medir_pares`, `fila`, `main` (script de medición) | medición |
| `rutas/r2/tablas.py` | crear | `cociente`, `usar_escala_log`, `grafica_tiempo_vs_explorados`, `main` (tablas Markdown y PNG desde los CSV) | gráficas/tablas |
| `tests/conftest.py` | modificar | Agregar `red_desde_aristas(aristas, nodos=None)` y `cargar_red_clase()` (ver «Redes en las pruebas») | pruebas |
| `tests/datos/red_clase.json` | crear (se versiona) | Copia de las secciones `red` y `R2` de `estudio/casos_prueba.json` + clave `"_origen"` | datos de prueba |
| `tests/test_adyacencia.py`, `test_dijkstra.py`, `test_dijkstra_clase.py`, `test_dijkstra_propiedad.py`, `test_ruta.py`, `test_pares.py`, `test_matriz.py`, `test_medir_dijkstra.py`, `test_tablas_r2.py`, `test_red_real_r2.py` | crear | Pruebas (las `red` llevan `pytestmark = pytest.mark.red`) | pruebas |
| `tests/test_config.py` | modificar | `test_rutas_r2` | pruebas |
| `README.md` | modificar | Sección "Reproducir R2" | doc |
| `docs/anexo-ia.md` | modificar (local, ignorado por git) | Entradas de R2 | doc |

No se toca `.gitignore`, `pyproject.toml` ni `requirements.txt` (nada nuevo que instalar).

## Estructuras de datos y firmas

**Representación indexada (Puerta 2).** Los ids de OSM son enteros grandes y dispersos; se renumeran a índices 0..V−1 para que `dist`, `pred` y `visitado` sean **listas** de tamaño V (acceso O(1) por posición, sin hash) y las dos versiones tengan exactamente la misma inicialización.

- `ids`: `list[int]`, ids de nodo **ordenados de menor a mayor**; el índice i representa al nodo `ids[i]`.
- `indice`: `dict[int, int]`, id → i (solo lo usan el envoltorio y los scripts, nunca los algoritmos).
- `adyacencia`: `list[list[tuple[int, float]]]` de largo V; `adyacencia[i]` = lista de `(j, travel_time)` con **todas** las aristas `(u, v, key)` del MultiDiGraph (paralelas y autolazos); un nodo sin salidas tiene lista vacía.

Por qué lista de adyacencia: E ≈ 2,3 · V (red muy dispersa), así que ocupa O(V + E) y recorrer los vecinos de u cuesta su grado; una matriz V × V sería ≈ 7,7 · 10⁷ celdas. Como los índices siguen el orden de los ids, desempatar por menor índice = desempatar por menor id. Es una estructura propia: NetworkX no participa en los algoritmos.

```python
# rutas/r2/adyacencia.py
class Red(NamedTuple):
    ids: list[int]
    indice: dict[int, int]
    adyacencia: list[list[tuple[int, float]]]

def construir_adyacencia(G, peso="travel_time") -> Red:
    """ids = sorted(G.nodes); indice = {id: i}; adyacencia[indice[u]] recibe (indice[v], w) por cada
    arista (u, v, key). ValueError("arista (u, v, key) con travel_time=...: ...") si el peso es NaN,
    inf o negativo (mensaje con ids, no índices). Peso 0 permitido. O(V log V + E) (el sort de ids)."""
```

**Dijkstra** (sobre índices). Firma común; las dos devuelven lo mismo:

```python
# rutas/r2/dijkstra.py
def dijkstra_lineal(adyacencia, origen, destino=None): ...
def dijkstra_cola(adyacencia, origen, destino=None, estadisticas=None): ...
#   origen, destino: índices 0..V-1 (precondición; no se validan: un índice inválido da IndexError de Python)
#   con destino → (tiempo_s: float, ruta: list[int] de índices, nodos_explorados: int)
#                 tiempo_s = math.inf y ruta = [] si no es alcanzable
#   sin destino → (dist: list[float] de largo V, pred: list[int | None] de largo V, nodos_explorados: int)
#                 dist = inf y pred = None en los no alcanzados; pred[origen] = None
def reconstruir_ruta(pred, origen, destino) -> list[int]   # índices; [origen] si origen == destino; [] si destino sin predecesor
```

- **Inicialización igual en ambas** (spec, punto 0): `V = len(adyacencia)`, `dist = [inf] * V`, `pred = [None] * V`, `visitado = [False] * V`, `dist[origen] = 0.0`, `explorados = 0`. Es O(V) y forma parte de lo medido.
- Lo **único** distinto es cómo se elige el siguiente nodo:
  - **Lineal**: recorrer `i = 0 .. V−1` y quedarse con el no visitado de menor `dist[i]`, cambiando de candidato **solo si `dist[i] < mejor`** (estricto; `mejor` empieza en `inf`, así que los `inf` nunca se eligen y en un empate gana el menor índice). Si no hay candidato, termina.
  - **Cola**: `heapq` con entradas `(distancia, índice)` (la tupla da el desempate por menor índice). Inserción perezosa: al mejorar `v` se hace `heappush((nueva, v))`; al sacar un `u` ya visitado se descarta sin contarlo (entrada obsoleta). Se inserta solo si la distancia mejora estrictamente (regla que da los números del caso 20).
- Parada: `visitado[u] = True; explorados += 1` y **luego** `if u == destino: break` (parar al sacar, no al descubrir). Relajación estricta `dist[u] + w < dist[v]`.
- No modifican `adyacencia` (por eso la medición en proceso no necesita copiarla).
- **Contador del caso 20**: parámetro opcional `estadisticas=None` de `dijkstra_cola`. Dos enteros locales (`extracciones`, `obsoletas`); al terminar, si `estadisticas is not None`, se escriben `estadisticas["extracciones"]` y `estadisticas["obsoletas"]`. No cambia el valor devuelto ni la firma por defecto (decisión aceptada).
- Nota de redacción: la spec dice en el punto 3 «entradas `(distancia, id_nodo)`»; con la representación indexada la entrada es `(distancia, índice)`, que la misma spec declara equivalente (índices en el orden de los ids). No cambia ningún resultado.

Esqueleto (para que las dos versiones se lean lado a lado; el código final debe parecerse a esto):

```text
lineal                                         cola
V = len(adyacencia)                            V = len(adyacencia)
dist = [inf]*V; pred = [None]*V                dist = [inf]*V; pred = [None]*V
visitado = [False]*V; dist[origen] = 0         visitado = [False]*V; dist[origen] = 0
explorados = 0                                 explorados = 0; heap = [(0, origen)]
while True:                                    while heap:
  u = None; mejor = inf                          d, u = heappop(heap)
  for i in range(V):                             si visitado[u]: continue          # obsoleta
    si no visitado[i] y dist[i] < mejor:
      u = i; mejor = dist[i]
  si u is None: break
  visitado[u] = True; explorados += 1            visitado[u] = True; explorados += 1
  si u == destino: break                         si u == destino: break
  para (v, w) en adyacencia[u]:                  para (v, w) en adyacencia[u]:
    si dist[u] + w < dist[v]:                      si dist[u] + w < dist[v]:
      dist[v] = dist[u] + w; pred[v] = u             dist[v] = dist[u] + w; pred[v] = u
                                                     heappush(heap, (dist[v], v))
con destino: si dist[destino] == inf → (inf, [], explorados)
             si no → (dist[destino], reconstruir_ruta(pred, origen, destino), explorados)
sin destino: (dist, pred, explorados)
```

(En la cola, `dist[u]` es igual a `d` al sacar una entrada no obsoleta; usar `dist[u]` en ambas deja la relajación idéntica.)

**Envoltorio ids ↔ índices** (fuera de la medición; lo usan pares/matriz/medición fuera del cronómetro, las pruebas y R5):

```python
# rutas/r2/dijkstra.py (al final, separado de los algoritmos)
VERSIONES = {"lineal": dijkstra_lineal, "cola_prioridad": dijkstra_cola}   # mismos nombres que la columna version del CSV

def consultar(red, id_origen, id_destino, version="cola_prioridad") -> tuple[float, list[int], int]:
    """(tiempo_s, ruta en ids, nodos_explorados). KeyError(f"el nodo {x} no está en la red") si un id
    no está en red.indice; ValueError si version no es una clave de VERSIONES."""
```

El borde de la spec «origen o destino que no está en la adyacencia → `KeyError` con mensaje claro» lo cumple `consultar`; las funciones sobre índices tienen como precondición índices válidos.

**Ruta y detalle** (ids, porque usa el grafo):

```python
# rutas/r2/ruta.py
def detalle_ruta(G, ruta) -> tuple[float, float]:
    """(suma de travel_time, suma de length) de la ruta (lista de ids), tramo a tramo con mejor_arista(G, u, v).
    [origen] → (0.0, 0.0); ruta vacía → ValueError("ruta vacía: no hay camino")."""
```

**Redes en las pruebas** (`tests/conftest.py`):

```python
def red_desde_aristas(aristas, nodos=None) -> Red:
    """aristas: lista de (u, v, travel_time) con ids enteros pequeños (A=1 … F=6); nodos: ids extra sin
    aristas (p. ej. F aislado). Arma un nx.MultiDiGraph con travel_time y lo pasa por construir_adyacencia,
    así las pruebas usan el mismo camino que la red real (paralelas y autolazos incluidos)."""
def cargar_red_clase() -> tuple[Red, dict]:
    """Lee tests/datos/red_clase.json; red con las aristas cuyos dos extremos están en 1–7 (peso = campo
    en minutos del JSON, paralela 2→3 incluida) vía red_desde_aristas; devuelve (red, seccion_R2)."""
```

Con ids 1..n consecutivos, índice = id − 1; las pruebas de casos a mano usan `consultar` (ids) y las que miran listas de tamaño V (caso 7, 19, 20, 23, `test_sin_destino_listas_tamano_V`) llaman a `dijkstra_*` con `red.indice[id]` y leen `dist[red.indice[x]]`. Una prueba con ids no consecutivos y desordenados (30, 10, 20) comprueba la traducción.

**Pares** (`rutas/r2/pares.py`):

```python
SEMILLA = 2026
def seleccionar_pares(catalogo, lugares_nodos, semilla=SEMILLA) -> pandas.DataFrame
#   columnas: origen, destino, tipo ("cercano"|"lejano"), municipio_origen, municipio_destino, nodo_origen, nodo_destino
#   10 cercanos primero, luego 10 lejanos
```

Procedimiento exacto (aceptado; determinista en cualquier máquina):
1. `rng = random.Random(semilla)`; `municipios = sorted(set(catalogo.municipio))`; `rng.shuffle(municipios)`.
2. Lugares de cada municipio en el orden del catálogo. Un par es **válido** si los nodos son distintos y el par ordenado no está ya elegido. Un municipio sin ningún par válido se salta (hoy no hay ninguno).
3. Cercanos: vueltas sobre `municipios`; en cada municipio `o, d = rng.sample(lugares, 2)` repitiendo el sorteo hasta que sea válido; un par por municipio por vuelta; parar al llegar a 10.
4. Lejanos: `o, d = rng.sample(todos_los_ids, 2)` repitiendo hasta tener 10 válidos con municipios distintos.

**Matriz** (`rutas/r2/matriz.py`):

```python
def calcular_matriz(red, nodos) -> list[list[float]]
#   nodos: lista de id_nodo en el orden del catálogo; por fila: dist, _, _ = dijkstra_cola(red.adyacencia, red.indice[n])
#   y se leen dist[red.indice[m]] para cada m en nodos (traducción fuera del algoritmo);
#   KeyError si un nodo no está en la red; ValueError si algún destino queda en inf
def guardar_matriz(matriz, ids, ruta)        # csv con encabezado "id", ids...; cada celda repr(float); "\n"
def cargar_matriz(ruta) -> pandas.DataFrame  # index_col=0, float_precision="round_trip"; índice y columnas = ids
def asimetria(matriz, ids, tolerancia=1e-6) -> dict
#   {"pares_asimetricos": int (pares {i, j}, i < j), "par_max": [id_i, id_j],
#    "diferencia_max": float, "M_ij": float, "M_ji": float, "tolerancia": 1e-6}
def main(processed=DATA_PROCESSED, catalogo=CATALOGO, salida=RESULTS_R2)
```

**Medición** (`rutas/r2/medir_dijkstra.py`):

```python
COLUMNAS = ["origen", "destino", "version", "tiempo_viaje_s", "nodos_explorados", "tiempo_ms",
            "tipo", "distancia_m", "repeticiones"]       # las 6 del Anexo primero, luego las ampliadas
def fila(par, version, tiempo_s, explorados, resultado, distancia_m) -> dict
def medir_pares(G, red, pares, repeticiones=5,
                medir_cola=medir_en_proceso, medir_lineal=medir_en_hijo) -> list[dict]
def main(processed=DATA_PROCESSED, catalogo=CATALOGO, salida=RESULTS_R2, repeticiones=5)
```

`medir_pares`, por cada par en orden (todo lo que no es la llamada medida queda fuera del cronómetro):
1. `i_o, i_d = red.indice[nodo_origen], red.indice[nodo_destino]`.
2. `t, ruta, k = consultar(red, nodo_origen, nodo_destino, "cola_prioridad")`; `distancia_m = detalle_ruta(G, ruta)[1]`.
3. `medir_cola(dijkstra_cola, lambda: (red.adyacencia, i_o, i_d), repeticiones=...)` → fila `cola_prioridad`.
4. Si el par es cercano: `t_l, _, k_l = consultar(red, ..., "lineal")`; **comprobación** `|t_l − t| ≤ 1e-6` y `k_l == k` (si no, `AssertionError` con el par: no se escriben resultados de algo incorrecto; decisión aceptada); luego `medir_lineal(dijkstra_lineal, (red.adyacencia, i_o, i_d), repeticiones=...)` → fila `lineal`.

Los medidores se inyectan para probar sin cronometrar de verdad. Orden de filas: por par, primero `cola_prioridad` y luego `lineal` → 30 filas.

**Tablas** (`rutas/r2/tablas.py`):

```python
def cociente(df) -> dict   # {"mediana", "minimo", "maximo"} de tiempo_ms lineal / tiempo_ms cola, emparejando por (origen, destino); solo pares con ambas completadas
def usar_escala_log(df) -> bool   # max(tiempo_ms) / min(tiempo_ms) ≥ 100 entre las filas completadas
def grafica_tiempo_vs_explorados(results=RESULTS_R2) -> Path
def main(results=RESULTS_R2)   # escribe r2_cociente.csv, el PNG y tablas_r2.md
```

## Recurrencia y complejidad

Dijkstra no es recursivo; no hay recurrencia. Lo que va al informe:

| Algoritmo | Tiempo | Memoria adicional | Por qué |
|---|---|---|---|
| `construir_adyacencia` | O(V log V + E) | O(V + E) | ordenar los ids y una pasada por las aristas (fuera de la medición) |
| `dijkstra_lineal` | O(V²) | O(V) | O(V) de inicialización + ≤ V extracciones × recorrido de los V nodos + O(E) relajaciones |
| `dijkstra_cola` | O((V + E) log V) | O(V + E) | O(V) de inicialización + ≤ E + 1 inserciones y extracciones en `heapq`, O(log n) cada una; log E ≤ 2 log V + log 3 = O(log V) con ≤ 3 paralelas por par |
| Con parada temprana (k explorados) | lineal ≈ V + k · V; cola ≈ V + (k + aristas relajadas) · log | — | ambas pagan el mismo piso O(V) de inicialización (microsegundos); la lineal además un recorrido completo por extracción, que es su costo dominante |
| `consultar` | la de la versión + O(largo de la ruta) | O(largo de la ruta) | traducción ids ↔ índices (fuera de la medición) |
| `calcular_matriz` | O(42 · (V + E) log V) | O(V + E) por corrida + 42² | 42 corridas sin destino |
| `heapq.heappush`/`heappop` | O(log n) | lista de n | montículo binario sobre una lista; `Lib/heapq.py` con acelerador C `_heapq` |

Fuentes a citar (spec, ajuste 3): E. W. Dijkstra, «A note on two problems in connexion with graphs», *Numerische Mathematik* 1:269–271, 1959; documentación de Python 3.13, módulo `heapq` (complejidad y «Priority Queue Implementation Notes»); diapositivas de la clase de Dijkstra (red de los casos 19–23). Cormen et al. 24.3 solo si el grupo lo consulta. Los argumentos de correctitud (invariante, parada en el destino, pesos ≥ 0, comparación con R4) van al informe; la tabla de extracción del caso 19 sirve para ilustrarlos.

## Datos y archivos

| Archivo | Lo escribe | Formato |
|---|---|---|
| `tests/datos/red_clase.json` | T3 (una vez; se versiona) | `{"_origen": "...", "red": {...}, "R2": {...}}`, secciones copiadas sin cambios de `estudio/casos_prueba.json` |
| `data/processed/matriz_tiempos.csv` | `rutas.r2.matriz` | encabezado `id,C01,...` (42 ids en orden del catálogo); filas `id_i,M[i][0],...`; celdas `repr(float)` (s); `float_precision="round_trip"` al leer |
| `results/r2/r2_asimetria.json` | `rutas.r2.matriz` | ver `asimetria` |
| `results/r2/r2_pares.csv` | `rutas.r2.medir_dijkstra` | `origen, destino, tipo, municipio_origen, municipio_destino, nodo_origen, nodo_destino` |
| `results/r2/r2_pares.json` | `rutas.r2.medir_dijkstra` | `{"semilla": 2026, "generador": "random.Random", "cercanos": 10, "lejanos": 10, "regla": "<texto del procedimiento>"}` |
| `results/r2/r2_dijkstra.csv` | `rutas.r2.medir_dijkstra` | `COLUMNAS`; `version ∈ {lineal, cola_prioridad}`; `tiempo_viaje_s` y `distancia_m` sin redondear; `tiempo_ms` = mediana en ms o `"no completada"` |
| `results/r2/maquina.json` | `rutas.r2.medir_dijkstra` | `info_maquina()` |
| `results/r2/r2_cociente.csv` | `rutas.r2.tablas` | `mediana, minimo, maximo` (una fila) |
| `results/r2/r2_tiempo_vs_explorados.png` | `rutas.r2.tablas` | x = nodos explorados, y = tiempo (ms); `lineal` círculos azules, `cola_prioridad` triángulos naranjas; eje y logarítmico si `max(tiempo_ms) / min(tiempo_ms) ≥ 100` y entonces la etiqueta dice «Tiempo (ms, escala logarítmica)» |
| `results/r2/tablas_r2.md` | `rutas.r2.tablas` | mediciones (columnas del Anexo + tipo), cociente, pares y semilla, asimetría, máquina; unidad en los encabezados |

En todos los archivos los nodos van como **ids de OSM**, nunca como índices.

Semilla única: `2026` (pares, muestra de 20 pares de la prueba de la matriz y grafos aleatorios del caso 13), siempre con `random.Random(2026)`.

## Verificación

| Qué | Contra qué | Datos |
|---|---|---|
| `construir_adyacencia` | a mano: ids ordenados, índices, entradas | G1, multigrafo del caso 12, grafo con ids 30, 10, 20 |
| Ambas versiones | casos resueltos a mano (1–12) | G1, G2, multigrafo del caso 12 (ids A = 1 … F = 6, vía `red_desde_aristas`) |
| Ambas versiones | red de la clase (19–23) resuelta a mano y con NetworkX | `tests/datos/red_clase.json`, componente 1–7 |
| Lineal ↔ cola | otra implementación propia: mismo tiempo exacto y mismos explorados | casos 1–8, 11, 13; red real (14) y dentro de `medir_pares` antes de medir |
| Ambas | `networkx.single_source_dijkstra_path_length` (solo en pruebas) | 200 grafos aleatorios, semilla 2026 (13) |
| Cola en la red real | `nx.dijkstra_path_length(G, o, d, weight="travel_time")` ± 1e-6 | 20 pares (14) |
| Ruta | `detalle_ruta(ruta).travel_time` = tiempo ± 1e-6 | 20 pares (14), caso 12 |
| Matriz | `consultar(..., "cola_prioridad")` ± 1e-6 tras leer el CSV; reescritura byte a byte | 20 pares al azar + 20 medidos (16); matriz 7 × 7 de la clase (23) |
| Resultados medidos | `r2_dijkstra.csv`: lineal y cola con el mismo `tiempo_viaje_s` (± 1e-6) y `nodos_explorados` en los 10 cercanos | prueba `red` que se salta si no existe el CSV |

Cada prueba se escribe antes del código y se ve fallar por `NotImplementedError` del stub. Las pruebas que verifican código ya hecho (13, 14, 15, 16) se validan con una **mutación temporal** (p. ej. `<=` en lugar de `<` en la búsqueda del mínimo de la lineal, que rompe el desempate, o `<=` en la relajación) que debe hacerlas fallar, y luego se restaura.

## Medición (sección 6)

- **Qué se mide**: la llamada completa `dijkstra_*(adyacencia, i_origen, i_destino)`, **incluida la inicialización O(V) de `dist`/`pred`/`visitado`**, igual en las dos. Fuera del cronómetro: cargar el grafo y los CSV, `construir_adyacencia`, la traducción ids → índices, elegir pares, la corrida con `consultar` que da `tiempo_viaje_s`/`nodos_explorados`/ruta, `detalle_ruta`, la comprobación entre versiones y escribir archivos.
- **Cola**: `medir_en_proceso(dijkstra_cola, preparar)`, con `preparar = lambda: (red.adyacencia, i_o, i_d)` (no hace falta copiar: el algoritmo no modifica la adyacencia, lo prueba `test_no_modifica_adyacencia`).
- **Lineal**: `medir_en_hijo(dijkstra_lineal, (red.adyacencia, i_o, i_d))`; el cronómetro está dentro del hijo y el envío de la adyacencia por `pickle` no cuenta; > 300 s → `"no completada"`.
- 5 repeticiones, mediana en **ms**; una sola si la primera pasa de 60 s. `repeticiones` va al CSV.
- Misma máquina para todo R2, portátil enchufado, sin otros procesos pesados; `maquina.json`.
- **Cociente**: `tiempo_ms lineal / tiempo_ms cola` por par en los 10 cercanos; mediana, mínimo y máximo. Si alguna lineal fuera «no completada» se excluye y se avisa en `tablas_r2.md` (no se espera: la spec estima segundos por consulta).
- **Predicción a contrastar en el informe** (spec): ambas casi lineales en los explorados con un piso pequeño y común por la inicialización O(V); la lineal con pendiente ∝ V (un recorrido de V por extracción); la cola con pendiente ∝ grado · log; el cociente crece con los explorados.
- El script **lo corre el usuario**; las tareas de medición terminan entregándole el comando exacto.

## Trazabilidad

| Caso de la spec | Tarea | Prueba |
|---|---|---|
| Representación indexada (Entradas, Puerta 2) | T2 | `tests/test_adyacencia.py::test_g1_red_indexada`, `::test_ids_ordenados_e_indice` |
| 1, 2, 3 | T4, T5 | `tests/test_dijkstra.py::test_caso_1_a_b`, `::test_caso_2_a_d_entrada_obsoleta`, `::test_caso_3_a_e` (parametrizadas por versión, vía `consultar`) |
| 4 (origen = destino) | T4, T5 | `tests/test_dijkstra.py::test_caso_4_origen_igual_destino` |
| 5, 6 (inalcanzable) | T4, T5 | `tests/test_dijkstra.py::test_caso_5_a_f_inalcanzable`, `::test_caso_6_e_a_inalcanzable` |
| 7 (sin destino) | T4, T5 | `tests/test_dijkstra.py::test_caso_7_sin_destino`, `::test_sin_destino_listas_tamano_V` |
| 8 (peso 0) | T2, T4, T5 | `tests/test_adyacencia.py::test_peso_cero_permitido`; `tests/test_dijkstra.py::test_caso_8_peso_cero` |
| 9 (negativo, NaN, inf) | T2 | `tests/test_adyacencia.py::test_caso_9_peso_invalido` (parametrizada: −1, NaN, inf; mensaje con la arista en ids) |
| 10 (versiones iguales) | T5 | `tests/test_dijkstra.py::test_caso_10_versiones_coinciden` |
| 11 (desempate) | T4, T5 | `tests/test_dijkstra.py::test_caso_11_desempate_por_id` |
| 12 (paralelas y autolazo) | T2, T4, T5, T6 | `tests/test_adyacencia.py::test_paralelas_y_autolazo_se_conservan`; `tests/test_dijkstra.py::test_caso_12_paralelas_y_autolazo`; `tests/test_ruta.py::test_caso_12_detalle_usa_mejor_arista` |
| 13 (propiedad vs NetworkX) | T7 | `tests/test_dijkstra_propiedad.py::test_caso_13_sin_destino`, `::test_caso_13_con_destino` |
| 14 (red real) | T11 | `tests/test_red_real_r2.py::test_caso_14_lineal_igual_a_cola`, `::test_caso_14_ruta_y_networkx` |
| 15 (pesos reales) | T8 | `tests/test_red_real_r2.py::test_caso_15_adyacencia_real` |
| 16 (matriz real) | T11 | `tests/test_red_real_r2.py::test_caso_16_matriz_real` |
| 17 (pares) | T9 | `tests/test_pares.py::test_caso_17_catalogo_real`, `::test_misma_semilla_mismos_pares`, `::test_mismo_nodo_excluido_sintetico`, `::test_municipio_sin_pares_validos_se_salta` |
| 18 (cociente) | T13 | `tests/test_tablas_r2.py::test_caso_18_cociente` |
| 19 (orden de extracción) | T4, T5 | `tests/test_dijkstra_clase.py::test_caso_19_orden_de_extraccion` (parametrizada) |
| 20 (extracciones y obsoletas) | T5 | `tests/test_dijkstra_clase.py::test_caso_20_conteo_cola`, `::test_estadisticas_no_cambian_resultado` |
| 21 (explorados con parada) | T4, T5 | `tests/test_dijkstra_clase.py::test_caso_21_explorados_con_parada` |
| 22 (paralela 2→3) | T4, T5 | `tests/test_dijkstra_clase.py::test_caso_22_arista_paralela` |
| 23 (matriz 7 × 7 y asimetría) | T4, T5, T10 | `tests/test_dijkstra_clase.py::test_caso_23_matriz_clase`; `tests/test_matriz.py::test_caso_23_asimetria_clase` |
| Copia de la red de la clase | T3 | `tests/test_dijkstra_clase.py::test_red_clase_versionada` |
| Borde: `KeyError` origen/destino | T4 | `tests/test_dijkstra.py::test_consultar_id_inexistente_keyerror` |
| Envoltorio ids ↔ índices | T4 | `tests/test_dijkstra.py::test_consultar_traduce_ids`, `::test_consultar_version_desconocida` |
| Borde: no modifica la adyacencia | T4, T5 | `tests/test_dijkstra.py::test_no_modifica_adyacencia` |
| Borde: ruta de un nodo / vacía | T6 | `tests/test_ruta.py::test_ruta_de_un_nodo`, `::test_ruta_vacia_error` |
| Borde: mismo nodo en la matriz | T10 | `tests/test_matriz.py::test_mismo_nodo_da_cero`, `::test_inf_es_error` |
| Matriz CSV sin redondear | T10 | `tests/test_matriz.py::test_guardar_cargar_round_trip_byte_a_byte` |
| Medición y comprobación entre versiones | T12 | `tests/test_medir_dijkstra.py::*` |
| Gráfica y tablas desde CSV | T13 | `tests/test_tablas_r2.py::*` |
| Verificación en los resultados medidos | T14 | `tests/test_red_real_r2.py::test_resultados_medidos_versiones_coinciden` |

## Riesgos

- **Pruebas `red` lentas**: el caso 14 corre la lineal en 10 pares (≈ segundos cada uno) y el 16 hace 42 corridas: la suite `red` puede tardar ~1 min. Aceptable; `-m "not red"` sigue siendo rápida.
- **Confundir ids e índices**: con ids 1..n en las pruebas, índice = id − 1, y un error de traducción podría pasar inadvertido si se compara mal. Por eso los casos a mano van por `consultar` (ids) y hay una prueba con ids desordenados y no consecutivos (30, 10, 20). Los archivos de salida nunca llevan índices.
- **Índices inválidos**: `dijkstra_*` no valida (un índice negativo se interpretaría desde el final de la lista). Solo se llaman con índices salidos de `red.indice`; la validación con `KeyError` está en `consultar`.
- **Procesos hijo (`spawn`)**: `dijkstra_lineal` es función de módulo (se puede enviar con pickle); los scripts tienen `if __name__ == "__main__":`. Una prueba corre `medir_en_hijo` de verdad con una red diminuta y `repeticiones=1`.
- **Flotantes**: las dos versiones suman en el mismo orden (mismo árbol de predecesores por el desempate), así que deberían dar el mismo `float`; aun así se compara con 1e-6 como dice la spec.
- **Pares**: el procedimiento de sorteo fija detalles que la spec no fija (orden `sorted` antes de barajar, `rng.sample`, repetir hasta válido); si se cambia, cambian los pares.
- **Reproducibilidad de la matriz**: depende del grafo procesado de R1; si R1 se regenera, hay que regenerar la matriz (y R4).

## Decisiones

Tomadas por el usuario en la Puerta 2 (2026-11-10), ya en la spec:
1. Representación indexada con listas (`Red(ids, indice, adyacencia)`), inicialización O(V) igual en ambas versiones; solo cambia la búsqueda del mínimo. Envoltorio `consultar` fuera de la medición.
2. Se versiona `tests/datos/red_clase.json` (no hace falta tocar `.gitignore`).
3. El implementer calcula la matriz real en T11 (no es medición de tiempo); el usuario la regenera en T16.

Propuestas por el plan y aceptadas: contador `estadisticas=None` en `dijkstra_cola`; sorteo de pares (`sorted` antes de `shuffle`, `rng.sample`, saltar municipios sin pares válidos); eje log si `max/min ≥ 100`; esquina de la matriz `id`; `detalle_ruta` de un nodo → (0, 0) y ruta vacía → `ValueError`; `medir_dijkstra` se detiene sin escribir si las versiones difieren.

Nuevas y menores (no requieren puerta, se anotan): `construir_adyacencia` devuelve un `NamedTuple` `Red`; `consultar` usa como `version` los mismos nombres de la columna del CSV (`"lineal"`, `"cola_prioridad"`) y por defecto `"cola_prioridad"`; `dijkstra_*` no validan índices (lo hace `consultar`).

## Bloqueos

Ninguno.

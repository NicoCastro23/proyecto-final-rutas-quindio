# Plan — R4 Ruta óptima de recorrido (TSP asimétrico)

Spec: `specs/r4-ruta-optima/spec.md` (aprobada en Puerta 1, 2026-11-11, con sus «Decisiones»). Enunciado: sección 5, Requerimiento 4 (párrafo inicial y puntos 1 a 5); sección 6 (protocolo experimental, puntos 1 a 8); formatos en el Anexo, Requerimiento 4 (tabla `k | Tiempo fuerza bruta (ms) | Tiempo Held-Karp (ms)`, gráfica tiempo frente a k, tabla `k | Instancias | Brecha promedio (%) | Brecha máxima (%)`, itinerario `Orden | Lugar | Desplazamiento desde el anterior (min) | Visita (min) | Tiempo acumulado (h)` con fila «Regreso» y totales). Peso 25 %.

## Resumen

R4 toma la matriz 42 × 42 de R2 (`data/processed/matriz_tiempos.csv`, segundos, orden del catálogo) y las duraciones de visita del catálogo de R1, y hace seis cosas, cada una con su comando:

1. **Algoritmos** (sin comando, funciones puras en `rutas/r4/`): generador propio de permutaciones lexicográficas, **fuerza bruta**, **Held-Karp** (con la tabla expuesta en `tabla_held_karp` y un contador opcional de transiciones) y **vecino más cercano**. Sin E/S, sin `itertools`, sin NetworkX, sin NumPy. Más `costo_recorrido`, la validación común, los conteos teóricos y la memoria estimada.
2. **Instancias** (`python -m rutas.r4.instancias`): muestra anidada (semilla 2026) e instancias de calidad (semillas 2026..2035) → `results/r4/r4_instancias.json`. No mide nada; lo corre el implementer.
3. **Itinerario de un día** (`python -m rutas.r4.itinerario`): Held-Karp sobre los 8 atractivos por defecto desde C01, quitando atractivos hasta que quepa en 660 min → `r4_itinerario.csv` y `r4_itinerario.json`. No mide tiempos; lo corre el implementer.
4. **Calidad de la heurística** (`python -m rutas.r4.calidad`): 40 instancias (k = 5, 8, 10, 12 × 10 semillas), voraz frente a Held-Karp → `r4_calidad_detalle.csv` y `r4_calidad.csv`. No se cronometra; lo corre el implementer.
5. **Medición** (`python -m rutas.r4.medir_exactas`, larga, **la corre el usuario**): k = 5..12 sobre la muestra anidada, FB y HK con `medir_en_hijo`, verificación FB = HK antes de escribir → `r4_exactas.csv` y `maquina.json`. Aparte, `python -m rutas.r4.medir_memoria` (pico de `tracemalloc`, fuera de todo cronómetro, corto) → `r4_memoria.csv`.
6. **Tablas y gráfica** (`python -m rutas.r4.tablas`): `tablas_r4.md` y `r4_tiempo_vs_k.png` desde los CSV/JSON.

Contradicciones entre la spec y el enunciado: **ninguna**. La spec cubre los cinco puntos (k de 5 a 12 o hasta el límite, mayor k resuelto, gráfica, subestructura y recurrencia, recorrido de Held-Karp, memoria estimada, FB = HK; heurística propia justificada; 10 ≥ 5 instancias por k con k = 5, 8, 10, 12; itinerario con 6 a 8 atractivos, jornada de 11 h, quitar justificando; voraz frente a óptimo y Dijkstra), con partida Armenia y lugares al azar con semilla fija entre todas las categorías (la muestra sale de los 41 lugares distintos de C01). Sin bloqueos; hay una decisión de diseño que toca un módulo compartido (punto 1 de «Decisiones para el usuario»).

## Estado del repositorio que se reutiliza

- `rutas/config.py` (`RAIZ`, `DATA_PROCESSED`, `MATRIZ_TIEMPOS`, `CATALOGO`, `RESULTS_R1..R3`): se agrega `RESULTS_R4 = RAIZ / "results" / "r4"`.
- `rutas/medicion.py`: `medir_en_hijo(funcion, args=(), repeticiones=5, umbral_una_s=60.0, limite_s=300.0)`, `ResultadoMedicion(tiempo_ms, repeticiones, completada, tiempos_ms)`, `NO_COMPLETADA`, `info_maquina()`. **Hoy el hijo solo devuelve los nanosegundos**, no el valor de la función; el punto 10 de la spec necesita el `tiempo_total_s` de la FB medida en el hijo para k ≥ 10. Se agrega un parámetro opcional compatible (T17, ver «Decisiones para el usuario», 1).
- `rutas/r2/matriz.py`: `cargar_matriz(ruta)` → `DataFrame` con índice y columnas = ids (lee los `float` exactos con `round_trip`); `guardar_matriz(matriz, ids, ruta)` (lo usan las pruebas para escribir matrices sintéticas).
- `rutas/r1/catalogo.py`: `cargar_catalogo(ruta=CATALOGO)` valida los 42 lugares reales (los 15 atractivos con `categoria == "Atractivo turístico"` y `duracion_visita_min > 0`). Los scripts de R4 leen el catálogo con `pandas.read_csv(catalogo)`, igual que `rutas.r2.matriz.main` (el catálogo real ya lo valida R1), para que las pruebas puedan pasarles catálogos sintéticos pequeños. `cargar_catalogo` solo se usa en las pruebas con el catálogo real.
- `rutas/r1/tablas.py`: `a_markdown(df, decimales)`.
- `tests/conftest.py`: marcadores `red` y `lento` ya registrados en `pyproject.toml`; opción `--lento`. No hace falta agregar fixtures compartidas: las de R4 viven en sus archivos de prueba.
- Datos verificados por el planner (lectura, 2026-11-11): `data/catalogo.csv` tiene 42 lugares con C01 en el índice 0; `random.Random(2026).sample(otros, 12)` da `C09, A10, F07, T04, C08, A04, F01, F06, F03, A05, C02, A09`, igual que la spec. Visitas de los 8 atractivos por defecto: A05 60, A08 180, A04 180, A14 30, A06 30, A07 30, A12 180, A01 420 (1 110 min de visitas: no cabe ni sin desplazamientos).
- **Entorno**: hoy **no hay `.venv`** en el repo y `python3.13` **no está instalado** en esta máquina (`python3` es 3.14.6). El README pide `python3.13 -m venv .venv` y R1–R3 se midieron con 3.13.8. T1 lo comprueba y, si falta 3.13, se detiene y pregunta (ver «Decisiones para el usuario», 3). No se tocan `.gitignore`, `pyproject.toml` ni `requirements.txt`.

## Módulos y archivos

Subpaquete `rutas/r4/`, un módulo por idea. Los algoritmos (`permutaciones.py`, `fuerza_bruta.py`, `held_karp.py`, `vecino.py`, `recorrido.py`, `conteos.py`) no hacen E/S ni importan pandas; la traducción por ids, las instancias, el itinerario, la calidad, la medición y las tablas van aparte, porque solo se cronometra la llamada al algoritmo.

| Ruta | Acción | Responsabilidad | Tipo |
|---|---|---|---|
| `rutas/config.py` | modificar | `RESULTS_R4 = RAIZ / "results" / "r4"` | constantes |
| `rutas/medicion.py` | modificar | `medir_en_hijo(..., devolver_valor=False)`; campo `valor=None` al final de `ResultadoMedicion` (compatible con todo lo existente) | medición compartida |
| `rutas/r4/__init__.py` | crear | Vacío | — |
| `rutas/r4/permutaciones.py` | crear | `permutaciones_lexicograficas(elementos)` (algoritmo L de Knuth) | **algoritmo puro** |
| `rutas/r4/recorrido.py` | crear | `validar_entrada(T, s, lugares)`, `costo_recorrido(T, recorrido)` | **algoritmo puro** |
| `rutas/r4/fuerza_bruta.py` | crear | `fuerza_bruta(T, s, lugares)` | **algoritmo puro** |
| `rutas/r4/held_karp.py` | crear | `tabla_held_karp(T, s, lugares, contador=None)`, `held_karp(T, s, lugares, contador=None)` | **algoritmo puro** |
| `rutas/r4/vecino.py` | crear | `vecino_mas_cercano(T, s, lugares)` | **algoritmo puro** |
| `rutas/r4/conteos.py` | crear | `memoria_held_karp(k)`, `conteos_teoricos(k)` | teoría (puro) |
| `rutas/r4/por_ids.py` | crear | `METODOS`, `matriz_a_listas(matriz_df)`, `resolver_por_ids(matriz_df, id_partida, ids_lugares, metodo)` | traducción ids ↔ índices (para scripts y R5) |
| `rutas/r4/instancias.py` | crear | `SEMILLA`, `SEMILLAS_CALIDAD`, `PARTIDA`, `K_EXACTAS`, `K_CALIDAD`, `KMAX`, `otros_ids`, `muestra_anidada`, `instancias_calidad`, `main` (script → `r4_instancias.json`) | preparación (fuera del cronómetro) |
| `rutas/r4/itinerario.py` | crear | `JORNADA_MAX_MIN = 660`, `ATRACTIVOS_DIA`, `itinerario_dia(...)` (puro), `visitas_del_catalogo(catalogo_df, ids)`, `escribir_itinerario(...)`, `main` (script) | itinerario |
| `rutas/r4/calidad.py` | crear | `calidad_instancias(T, ids, instancias)`, `resumir_calidad(detalle_df)`, `main` (script) | experimento de calidad (sin cronómetro) |
| `rutas/r4/medir_exactas.py` | crear | `COLUMNAS`, `TOLERANCIA_S`, `K_VERIFICACION_PREVIA = 9`, `medir_exactas(...)`, `main` (script) | medición |
| `rutas/r4/medir_memoria.py` | crear | `pico_tracemalloc(T, s, lugares)`, `filas_memoria(...)`, `main` (script → `r4_memoria.csv`) | medición de memoria (sin cronómetro) |
| `rutas/r4/tablas.py` | crear | `grafica_tiempo_vs_k(results)`, `main(results)` (`tablas_r4.md` y `r4_tiempo_vs_k.png`) | gráficas/tablas |
| `tests/test_config.py` | modificar | `test_rutas_r4` | pruebas |
| `tests/test_medicion.py` | modificar | Pruebas de `devolver_valor` (las existentes no cambian) | pruebas |
| `tests/test_permutaciones.py`, `test_tsp_clase.py`, `test_held_karp.py`, `test_conteos_r4.py`, `test_tsp_propiedad.py`, `test_instancias_r4.py`, `test_por_ids.py`, `test_itinerario.py`, `test_calidad_r4.py`, `test_medir_exactas.py`, `test_medir_memoria_r4.py`, `test_tablas_r4.py`, `test_red_real_r4.py` | crear | Pruebas (`test_red_real_r4.py` con `pytestmark = pytest.mark.red`) | pruebas |
| `README.md` | modificar | Sección «Reproducir R4» | doc |
| `docs/anexo-ia.md` | modificar (local, ignorado) | Entradas de R4 | doc |

`itertools` solo aparece en `tests/` (casos 4b, 12, 13 y 16); una prueba lo comprueba leyendo el código fuente de `rutas/r4/*.py` (`test_sin_itertools_ni_networkx`, T2).

## Estructuras de datos y firmas

**Matriz `T`**: `list[list[float]]` de Python (no `DataFrame` ni arreglo NumPy). Acceso `T[i][j]` en O(1) con dos indexaciones de lista; los `float` de Python se suman sin la sobrecarga de los escalares de NumPy (que dentro de un ciclo de Python son varias veces más lentos). La conversión desde el `DataFrame` (`matriz_df.to_numpy().tolist()`, que ya da `float` de Python) se hace una vez, **fuera del cronómetro**. `math.inf` representa un arco imposible.

**Lugares**: `list[int]` de índices de `T`. **Recorrido**: `list[int]` `[s, p1, …, pk, s]`; con k = 0 es `[s]`.

**Tabla de Held-Karp**: dos listas de 2^k listas de k elementos, `costo[mascara][j]` (`float`, `math.inf` si no se usa) y `padre[mascara][j]` (`int` local 0..k−1 o `None`). La **máscara de bits** representa el subconjunto S ⊆ {0..k−1} en un solo `int` (bit j = lugar `L[j]`): quitar j es `mascara ^ (1 << j)`, la pertenencia es `mascara >> j & 1`, y recorrer las máscaras en orden creciente garantiza que `S∖{j}` (un número menor) ya está calculada. Indexar una lista por la máscara es O(1), sin hashing (un `dict` de `frozenset` sería más lento y gastaría más memoria). Las celdas con |S| = 0 o j ∉ S quedan sin usar: la tabla tiene k·2^k celdas y se usan k·2^(k−1); la spec fija las listas completas (decisión del grupo) porque así la estimación de memoria es exactamente k·2^k celdas.

**`L` = `sorted(lugares)`** en Held-Karp: así el desempate «menor i» y «menor j» es por menor índice de `T`, el resultado no depende del orden en que vengan los lugares y la tabla del caso 3 (lugares `[1, 2, 3]`) tiene bit 0 = lugar 1 (decisión del plan, 3).

```python
# rutas/r4/permutaciones.py  (algoritmo puro, sin itertools)
def permutaciones_lexicograficas(elementos):
    """Generador: todas las permutaciones de `elementos` (distintos) en orden lexicográfico,
    a partir de sorted(elementos), como tuplas. Algoritmo L (Knuth, TAOCP 4A, §7.2.1.2):
    1. a = sorted(elementos); yield tuple(a)
    2. i = mayor índice con a[i] < a[i+1]; si no hay, terminar
    3. j = mayor índice con a[i] < a[j]; intercambiar a[i], a[j]
    4. invertir a[i+1:]; yield tuple(a); volver a 2
    [] → una permutación (); [5] → (5,). No modifica `elementos` (trabaja sobre una copia)."""

# rutas/r4/recorrido.py
def validar_entrada(T, s, lugares) -> None:
    """ValueError si s o algún lugar no está en range(len(T)) (negativos incluidos), si hay
    lugares repetidos o si s está en lugares. O(k) con un set; no lee T."""
def costo_recorrido(T, recorrido) -> float:
    """float(suma de T[a][b] para cada par consecutivo). [s] → 0.0. Puede dar inf."""

# rutas/r4/fuerza_bruta.py
def fuerza_bruta(T, s, lugares) -> tuple[float, list[int]]:
    """validar_entrada; k = 0 → (0.0, [s]). Para cada p en permutaciones_lexicograficas(lugares):
    costo = T[s][p[0]] + Σ T[p[t]][p[t+1]] + T[p[-1]][s], sumado completo en un ciclo (sin poda,
    sin sumas incrementales); reemplaza al mejor solo si costo < mejor (estricto: en un empate
    gana la primera en orden lexicográfico). Si el mejor sigue en inf → ValueError("no hay
    recorrido finito"). Devuelve (float(mejor), [s, *mejor_p, s])."""

# rutas/r4/held_karp.py
def tabla_held_karp(T, s, lugares, contador=None) -> tuple[list[list[float]], list[list]]:
    """(costo, padre) de 2^k × k con L = sorted(lugares). Base: costo[1<<j][j] = T[s][L[j]],
    padre None. Para mascara = 1 .. 2^k − 1 con al menos 2 bits: bits = [j con el bit j];
    para cada j en bits, previa = mascara ^ (1 << j); para cada i en bits, i != j, en orden
    creciente: c = costo[previa][i] + T[L[i]][L[j]]; si c < mejor (estricto) → mejor, padre.
    Lee T[L[i]][L[j]] directamente una vez por transición (sin precalcular una submatriz).
    contador: None (por defecto, lo que usa la medición) o una lista [n] que se incrementa en
    k por la base y, una vez por máscara, en len(bits)·(len(bits) − 1)."""
def held_karp(T, s, lugares, contador=None) -> tuple[float, list[int]]:
    """validar_entrada; k = 0 → (0.0, [s]). costo, padre = tabla_held_karp(T, s, lugares, contador);
    cierre: j* = argmin_j costo[completa][j] + T[L[j]][s] (estricto: gana el menor j); contador
    += k. Si el óptimo es inf → ValueError("no hay recorrido finito"). Reconstrucción hacia atrás:
    mascara = completa, j = j*; mientras j no sea None: anotar L[j]; (mascara, j) =
    (mascara ^ (1 << j), padre[mascara][j]). Se invierte y se devuelve (float(opt), [s, …, s])."""

# rutas/r4/vecino.py
def vecino_mas_cercano(T, s, lugares) -> tuple[float, list[int]]:
    """validar_entrada; k = 0 → (0.0, [s]). orden = sorted(lugares) y visitado = [False] * k;
    desde actual = s, repetir k veces: se recorre `orden` saltando los visitados y se cambia de
    candidato solo si T[actual][j] < mejor (estricto: en empate gana el menor índice de T).
    Si ese mínimo es inf → ValueError. Al final se suma T[actual][s]; si el total es inf →
    ValueError("no hay recorrido finito"). O(k²)."""

# rutas/r4/conteos.py
def memoria_held_karp(k) -> dict:
    """{"k", "celdas": k·2^k, "bytes_estimados": 12·k·2^k, "mb_estimados": bytes / 1e6}."""
def conteos_teoricos(k) -> dict:
    """{"k", "transiciones_hk": k + k(k−1)·2^(k−2) + k (k ≥ 2; k = 1 → 2; k = 0 → 0),
       "permutaciones_fb": k!, "tramos_fb": (k+1)·k!}."""
```

Esqueleto de Held-Karp (el código final debe parecerse a esto, corto y fiel a la recurrencia):

```text
held_karp(T, s, lugares, contador=None):
  validar_entrada(T, s, lugares); si no hay lugares: return 0.0, [s]
  L = sorted(lugares); k = len(L); completa = (1 << k) − 1
  costo, padre = tabla_held_karp(T, s, lugares, contador)
  opt, j_fin = inf, None
  para j en 0..k−1:                                   # cierre
      c = costo[completa][j] + T[L[j]][s]
      si c < opt: opt, j_fin = c, j
  si contador no es None: contador[0] += k
  si opt == inf: ValueError("no hay recorrido finito")
  orden = []; mascara, j = completa, j_fin
  mientras j no sea None:
      orden.append(L[j]); mascara, j = mascara ^ (1 << j), padre[mascara][j]
  return float(opt), [s] + orden[::-1] + [s]
```

**Contador y medición.** El contador sirve solo para el caso 15. La medición llama `held_karp(T, s, lugares)` con los tres argumentos posicionales (`medir_en_hijo(held_karp, (T, s, lugares))`), así que `contador` es `None` y el único costo extra es **una comparación `contador is not None` por máscara** (2^k = 4 096 en k = 12) más una en la base y otra en el cierre, frente a ≈ 135 000 transiciones: < 0,1 % del trabajo. No hay ninguna comparación dentro del ciclo interno. Para que el contador no sea una fórmula disfrazada, una prueba (T9) lo contrasta con las **lecturas reales de `T`**: envuelve cada fila en una subclase de `list` que cuenta sus `__getitem__`, y el número de lecturas debe ser igual al contador (por eso `tabla_held_karp` lee `T[L[i]][L[j]]` una vez por transición).

**Traducción por ids** (`rutas/r4/por_ids.py`, fuera del cronómetro):

```python
METODOS = {"fuerza_bruta": fuerza_bruta, "held_karp": held_karp,
           "vecino_mas_cercano": vecino_mas_cercano}
def matriz_a_listas(matriz_df) -> tuple[list[list[float]], list[str]]:
    """(T, ids): T = matriz_df.to_numpy().tolist() (float de Python), ids = list(matriz_df.index).
    ValueError si las columnas no son iguales al índice."""
def resolver_por_ids(matriz_df, id_partida, ids_lugares, metodo) -> tuple[float, list[str]]:
    """Traduce ids → índices, llama METODOS[metodo](T, s, lugares) y traduce el recorrido a ids.
    ValueError si el método no existe o un id no está en la matriz."""
```

**Instancias** (`rutas/r4/instancias.py`):

```python
SEMILLA = 2026
SEMILLAS_CALIDAD = tuple(range(2026, 2036))    # 10 instancias por k
PARTIDA = "C01"
K_EXACTAS = tuple(range(5, 13))
K_CALIDAD = (5, 8, 10, 12)
KMAX = 12
def otros_ids(ids, partida=PARTIDA) -> list[str]        # los 41 ids distintos de la partida, en orden
def muestra_anidada(ids, partida=PARTIDA, semilla=SEMILLA, kmax=KMAX) -> list[str]
#   random.Random(semilla).sample(otros_ids(ids, partida), kmax); cada k usa los primeros k
def instancias_calidad(ids, partida=PARTIDA, ks=K_CALIDAD, semillas=SEMILLAS_CALIDAD) -> list[dict]
#   [{"k", "semilla", "ids": random.Random(semilla).sample(otros, k)}], k externo y semilla interna
def main(catalogo=CATALOGO, salida=RESULTS_R4)   # escribe r4_instancias.json (ids del catálogo)
```

Un `random.Random(semilla)` **nuevo** por instancia: cada una se reproduce sola, sin depender del orden de generación. Los scripts de medición, memoria y calidad recalculan las instancias con estas mismas funciones (deterministas), con los ids de la matriz (que están en el orden del catálogo), en lugar de leer el JSON, que es solo documentación.

**Itinerario** (`rutas/r4/itinerario.py`):

```python
JORNADA_MAX_MIN = 660
ATRACTIVOS_DIA = ["A05", "A08", "A04", "A14", "A06", "A07", "A12", "A01"]
def itinerario_dia(T, ids, s, atractivos, visita_min, jornada_max_min=JORNADA_MAX_MIN)
    -> tuple[list[dict], list[dict], dict]:
    """T en segundos; ids[i] = id del índice i; s y atractivos son índices de T; visita_min =
    {índice: minutos} de TODOS los atractivos del catálogo (un índice que no está ahí no es
    atractivo). ValueError si len(atractivos) no está en 6..8, si hay repetidos, si alguno no
    está en visita_min o si s está entre ellos.
    Jornada(A) = Σ visita_min[a] + held_karp(T, s, A)[0] / 60.
    Mientras jornada > jornada_max_min y queden ≥ 2 atractivos: para cada a en sorted(A),
    jornada(A ∖ {a}); se quita el de menor jornada (estricto: empate → menor índice) y se anota
    {"id", "jornada_antes_min", "jornada_despues_min", "ahorro_min"}.
    filas: una por atractivo del recorrido final {"orden": 1.., "id", "desplazamiento_min",
    "visita_min", "acumulado_h"} y la última {"orden": "Regreso", "id": ids[s], ...,
    "visita_min": None, "acumulado_h": jornada / 60}.
    totales: {"visitas_min", "desplazamientos_min", "jornada_min", "jornada_h", "cabe",
    "atractivos_finales"}. Sin redondear."""
def visitas_del_catalogo(catalogo_df, ids) -> dict[int, float]   # {índice: duracion_visita_min} de los atractivos
def escribir_itinerario(filas, quitados, totales, ids_iniciales, id_partida, nombres, salida)
#   r4_itinerario.csv (orden, id, lugar, desplazamiento_min, visita_min, acumulado_h; visita "—" en
#   Regreso) y r4_itinerario.json (partida, atractivos iniciales, quitados, totales, cabe)
def main(matriz=MATRIZ_TIEMPOS, catalogo=CATALOGO, salida=RESULTS_R4, partida=PARTIDA,
         atractivos=ATRACTIVOS_DIA)
```

El nombre del lugar (`lugar`) lo agrega `escribir_itinerario` desde el catálogo: `itinerario_dia` queda puro y R5 lo puede llamar con cualquier partida y atractivos.

**Calidad** (`rutas/r4/calidad.py`, sin cronómetro):

```python
COLUMNAS_DETALLE = ["k", "semilla", "optimo_s", "heuristica_s", "brecha_pct", "lugares"]
COLUMNAS = ["k", "instancias", "brecha_promedio_pct", "brecha_maxima_pct"]
def calidad_instancias(T, ids, instancias, partida=PARTIDA) -> list[dict]
#   por instancia: opt = held_karp, heur = vecino_mas_cercano; brecha = (heur − opt) / opt × 100;
#   si brecha < −1e-9 → ValueError (el voraz no puede ser mejor que el óptimo); lugares = "-".join(ids)
def resumir_calidad(detalle_df) -> DataFrame     # groupby k: count, mean, max
def main(matriz=MATRIZ_TIEMPOS, catalogo=CATALOGO, salida=RESULTS_R4)
```

**Medición** (`rutas/r4/medir_exactas.py`):

```python
COLUMNAS = ["k", "metodo", "tiempo_ms", "repeticiones", "estado", "tiempo_total_s", "recorrido"]
METODOS_EXACTOS = ("fuerza_bruta", "held_karp")       # orden de las filas dentro de cada k
TOLERANCIA_S = 1e-6
K_VERIFICACION_PREVIA = 9
def medir_exactas(T, ids, s, muestra, ks=K_EXACTAS, repeticiones=5, medir=medir_en_hijo) -> list[dict]
def main(matriz=MATRIZ_TIEMPOS, salida=RESULTS_R4, ks=K_EXACTAS, repeticiones=5)
```

`medir_exactas`, para cada k (en orden creciente), con `lugares` = índices de `muestra[:k]`:
1. Fuera del cronómetro, en el proceso principal: `ref = held_karp(T, s, lugares)` (≤ 1 s en k = 12). Si k ≤ 9: `fb = fuerza_bruta(T, s, lugares)` y, si `|fb[0] − ref[0]| > 1e-6`, `ValueError` con k y ambos valores (error explícito, no `assert`).
2. Para cada método en `METODOS_EXACTOS`: si ese método ya tuvo `no_completada` en un k menor → fila `no_ejecutada` (sin medir). Si no: `r = medir(funcion, (T, s, lugares), repeticiones=repeticiones, devolver_valor=True)`. Si `r.completada`: el valor del hijo `r.valor` se compara con `ref` (±1e-6; si difiere, `ValueError`) y la fila queda `ok` con `tiempo_ms`, `repeticiones`, `tiempo_total_s` y `recorrido` (ids unidos con `-`). Si no: fila `no_completada` con `tiempo_ms`, `tiempo_total_s` y `recorrido` vacíos y `repeticiones = 0`.
3. Imprime el avance de cada k (`flush=True`).

`main` carga la matriz, arma `T` e ids, calcula la muestra (`muestra_anidada(ids)`, partida `PARTIDA`), llama a `medir_exactas` y **solo al final** escribe `r4_exactas.csv` y `maquina.json`: si cualquier comprobación falla, el script termina con `ValueError` y no escribe nada. Las comprobaciones de los pasos 1 y 2 cumplen el punto 10 de la spec: en k ≤ 9 la FB se verifica antes de medir; en k ≥ 10 el valor que se compara es el que devolvió el hijo de la medición.

**Memoria** (`rutas/r4/medir_memoria.py`, sin cronómetro):

```python
COLUMNAS = ["k", "celdas", "bytes_estimados", "mb_estimados", "pico_tracemalloc_bytes", "pico_tracemalloc_mb"]
def pico_tracemalloc(T, s, lugares) -> int
#   gc.collect(); tracemalloc.start(); held_karp(T, s, lugares); _, pico = tracemalloc.get_traced_memory();
#   tracemalloc.stop(); return pico   (T ya existía antes de start: no se cuenta)
def filas_memoria(T, s, lugares_por_k) -> list[dict]   # memoria_held_karp(k) + pico, k = 5..12
def main(matriz=MATRIZ_TIEMPOS, salida=RESULTS_R4)
```

`tracemalloc` hace que Python registre cada asignación y vuelve el código varias veces más lento: por eso **nunca** se activa en `medir_exactas` y vive en su propio script.

**Tablas** (`rutas/r4/tablas.py`, `matplotlib.use("Agg")`):

```python
def grafica_tiempo_vs_k(results=RESULTS_R4) -> Path
#   lee r4_exactas.csv (keep_default_na=False); una curva por método solo con las filas ok;
#   ax.set_yscale("log"); etiquetas "k (lugares a visitar)" y "Tiempo (ms, escala logarítmica)";
#   leyenda "Fuerza bruta (no completada desde k = 12)" si aplica → r4_tiempo_vs_k.png
def main(results=RESULTS_R4)
#   tablas_r4.md: (1) tabla del Anexo pivoteada (k | Tiempo fuerza bruta (ms) | Tiempo Held-Karp (ms)),
#   "no completada" para no_completada y no_ejecutada, + repeticiones; (2) mayor k resuelto por método;
#   (3) cocientes medidos t(k+1)/t(k) frente a los predichos ((k+1)²/k para FB, 2((k+1)/k)² para HK);
#   (4) memoria estimada frente al pico (r4_memoria.csv); (5) conteos teóricos (conteos_teoricos);
#   (6) calidad (formato del Anexo, desde r4_calidad.csv); (7) itinerario (formato del Anexo, partida,
#   quitados con su ahorro y totales, desde r4_itinerario.csv/json); (8) semillas y muestra
#   (r4_instancias.json); (9) máquina. Unidades en los encabezados. Llama a grafica_tiempo_vs_k.
```

Cada sección se omite con una nota si su archivo no existe (p. ej. antes de que el usuario mida): así T21 puede regenerar las tablas parciales sin inventar datos.

**Cambio en `rutas/medicion.py`** (compatible):

```python
@dataclass
class ResultadoMedicion:
    tiempo_ms: float | None
    repeticiones: int
    completada: bool
    tiempos_ms: list[float] = field(default_factory=list)
    valor: object = None               # nuevo: lo que devolvió la función (solo con devolver_valor=True)

def _cronometrar_en_hijo(funcion, args, cola, devolver_valor=False):
    # cronómetro igual que hoy; después de `fin`, fuera del cronómetro:
    cola.put((fin - inicio, resultado) if devolver_valor else fin - inicio)

def medir_en_hijo(funcion, args=(), repeticiones=5, umbral_una_s=60.0, limite_s=300.0, devolver_valor=False)
#   con devolver_valor=True, ResultadoMedicion.valor = el valor de la primera repetición
```

El valor viaja por la misma cola después de detener el cronómetro. Es pequeño (un `float` y una lista de ≤ 14 enteros, unos cientos de bytes), muy por debajo del búfer del *pipe* (64 KB en macOS), así que `join()` antes de `get()` no se bloquea, igual que hoy con el entero. Con `devolver_valor=False` todo queda exactamente como está (R1–R3 no cambian).

## Recurrencia y complejidad

k = lugares a visitar (sin contar la partida).

| Algoritmo | Tiempo | Memoria adicional | Por qué |
|---|---|---|---|
| `permutaciones_lexicograficas` | O(1) amortizado por paso del algoritmo L + O(k) por la tupla entregada; Θ(k · k!) en total | O(k) | Knuth, *TAOCP* vol. 4A, §7.2.1.2, algoritmo L: el número medio de comparaciones e intercambios por permutación es constante. Copiar a tupla es O(k), igual que sumar el costo, así que no cambia el orden de la FB |
| `fuerza_bruta` | **Θ(k · k!)** | O(k) | k! permutaciones × (k+1) tramos sumados cada una; k = 12: 479 001 600 permutaciones y 6 227 020 800 tramos |
| `tabla_held_karp` + `held_karp` | **Θ(k² · 2^k)** | **Θ(k · 2^k)** | C({j}, j) = T[s][L[j]]; C(S, j) = min_{i ∈ S∖{j}} C(S∖{j}, i) + T[L[i]][L[j]]; óptimo = min_j C(L, j) + T[L[j]][s]. Σ_S \|S\|(\|S\|−1) = k(k−1)·2^(k−2) transiciones + k (base) + k (cierre); además O(k) por máscara para listar sus bits (O(k·2^k), menor). Tabla de 2^k × k celdas en `costo` y en `padre` |
| `vecino_mas_cercano` | **O(k²)** | O(k) | `sorted(lugares)` una vez (O(k log k)) y k pasos que recorren los k lugares ordenados saltando los visitados |
| `costo_recorrido`, `validar_entrada` | O(k) | O(k) | una pasada; el `set` de la validación es O(k) esperado |
| `itinerario_dia` | ≤ 1 + Σ_{m=2..8} m HK de ≤ 8 lugares | O(8 · 2^8) | por ronda, m Held-Karp de m−1 lugares (m ≤ 8): despreciable |
| `memoria_held_karp`, `conteos_teoricos` | O(1) / O(k) | O(1) | fórmulas |

Subestructura óptima (spec, Comportamiento 2): si P es óptimo sobre S terminando en j con penúltimo i, el tramo s→…→i es óptimo sobre S∖{j}; si no, se corta y se pega uno mejor más el arco i→j (solo se usan arcos en su sentido, así que la asimetría no importa). El informe la ilustra con la tabla del caso 3.

Memoria estimada (spec, Comportamiento 6): 12 B por celda (8 B del `float64` de `costo` + 4 B del predecesor), k · 2^k celdas, MB = 10⁶ B → k = 12: 589 824 B = 0,590 MB. El pico de `tracemalloc` será mayor porque en Python cada fila es un objeto `list` (≈ 56 B de cabecera + 8 B por puntero), cada `float` calculado es un objeto de 24 B y hay 2 × 2^k listas; orden de magnitud esperado en k = 12: 2 × 4 096 × (56 + 8 · 12) B ≈ 1,2 MB de listas + 24 576 floats × 24 B ≈ 0,6 MB → ≈ 2 MB (estimación del plan para contrastar en el informe; los `None` e `inf` iniciales son objetos compartidos y no suman).

Predicción de cocientes (spec): FB de k a k+1 ≈ (k+1)²/k (≈ 13,1 de 11 a 12); HK ≈ 2((k+1)/k)² (≈ 2,35 de 11 a 12).

Estimación de tiempos en esta máquina (para la Puerta 2, a confirmar con la corrida de humo de T18): FB ≈ 2–3 µs por permutación en Python → k = 10 ≈ 10 s, k = 11 ≈ 1,5–2,5 min (una sola repetición si pasa de 60 s), k = 12 ≈ 20–30 min → **no completada** a los 5 min. HK en k = 12 ≈ 0,2–0,5 s. Corrida completa de `medir_exactas`: ≈ 10–15 min.

Fuentes (spec): Held y Karp (1962), *J. SIAM* 10(1); Bellman (1962), *J. ACM* 9(1); Knuth, *TAOCP* vol. 4A, §7.2.1.2; Rosenkrantz, Stearns y Lewis (1977), *SIAM J. Comput.* 6(3) (cota del vecino más cercano solo en el caso métrico simétrico); Cormen et al., 3.ª ed., §34.5.4 (TSP NP-difícil); documentación de Python 3.13 (`tracemalloc`, `random.Random.sample`, `list.sort`).

## Datos y archivos

| Archivo | Lo escribe | Formato |
|---|---|---|
| `results/r4/r4_instancias.json` | `rutas.r4.instancias` | `{"semilla": 2026, "generador": "random.Random(semilla).sample(otros, k)", "partida": "C01", "otros": "los 41 ids distintos de C01, en orden del catálogo", "k_exactas": [5, …, 12], "muestra_anidada": [12 ids], "regla_anidada": "cada k usa los primeros k", "semillas_calidad": [2026, …, 2035], "calidad": [{"k": 5, "semilla": 2026, "ids": [...]}, … 40 entradas]}` |
| `results/r4/r4_exactas.csv` | `rutas.r4.medir_exactas` | `COLUMNAS`; 16 filas (k = 5..12 × `fuerza_bruta`, `held_karp`, en ese orden); `tiempo_ms` = mediana en ms sin redondear o vacío; `estado` ∈ {`ok`, `no_completada`, `no_ejecutada`}; `tiempo_total_s` en segundos sin redondear o vacío; `recorrido` = ids con `-` (`C01-…-C01`) o vacío |
| `results/r4/maquina.json` | `rutas.r4.medir_exactas` | `info_maquina()` |
| `results/r4/r4_memoria.csv` | `rutas.r4.medir_memoria` | `k, celdas, bytes_estimados, mb_estimados, pico_tracemalloc_bytes, pico_tracemalloc_mb` (k = 5..12, muestra anidada) |
| `results/r4/r4_calidad_detalle.csv` | `rutas.r4.calidad` | `k, semilla, optimo_s, heuristica_s, brecha_pct, lugares` (40 filas; `lugares` = ids con `-`) |
| `results/r4/r4_calidad.csv` | `rutas.r4.calidad` | `k, instancias, brecha_promedio_pct, brecha_maxima_pct` (4 filas, desde el detalle) |
| `results/r4/r4_itinerario.csv` | `rutas.r4.itinerario` | `orden, id, lugar, desplazamiento_min, visita_min, acumulado_h`; `orden` 1..m y la última `Regreso` (lugar de partida, `visita_min` = `—`); valores sin redondear |
| `results/r4/r4_itinerario.json` | `rutas.r4.itinerario` | `{"partida": {"id", "lugar"}, "atractivos_iniciales": [ids], "quitados": [{"id", "lugar", "jornada_antes_min", "jornada_despues_min", "ahorro_min"}], "atractivos_finales": [ids en orden de visita], "totales": {"visitas_min", "desplazamientos_min", "jornada_min", "jornada_h"}, "jornada_max_min": 660, "cabe": true}` |
| `results/r4/tablas_r4.md` | `rutas.r4.tablas` | ver `main` de tablas; tiempos con 3 decimales, brechas con 2, minutos con 1, horas con 2 |
| `results/r4/r4_tiempo_vs_k.png` | `rutas.r4.tablas` | k en x, ms (log) en y, una curva por método |

Semillas: **2026** para la muestra anidada y la propiedad (casos 11 y 12); **2026..2035** para la calidad. Se documentan en `r4_instancias.json` y en `tablas_r4.md`.

## Verificación

| Qué | Contra qué | Datos |
|---|---|---|
| `permutaciones_lexicograficas` | `list(itertools.permutations(...))` (solo en la prueba) | caso 13 ([0..3], [5], []), no modifica la entrada |
| `costo_recorrido` | a mano | matriz de clase: los 6 recorridos del caso 1; inverso del caso 5 (40) |
| `fuerza_bruta` | a mano; `itertools.permutations` | casos 1, 2, 4b, 6–10, 17; propiedad (caso 12) |
| `tabla_held_karp` | tabla calculada a mano en la spec | caso 3 (12 celdas usadas, `inf`/`None` en las demás) |
| `held_karp` | a mano; FB | casos 2, 5–10, 17; propiedad FB = HK (caso 11); red real k = 5..8 (19a) |
| Recorrido de HK | permutación válida y `costo_recorrido` = valor reportado (±1e-6) | casos 11, 17, 19b |
| Contador | fórmula k + k(k−1)2^(k−2) + k **y** lecturas reales de `T` | caso 15 (k = 3, 5, 8, 10, 12) |
| `vecino_mas_cercano` | a mano | casos 4 (39, 11,43 %), 4b (16 frente a 14), 6–10; brecha ≥ 0 (caso 11) |
| `memoria_held_karp`, `conteos_teoricos` | valores de la spec | casos 14 y 15 |
| `resolver_por_ids` | a mano | caso 18 |
| `itinerario_dia` | matriz construida para la frontera; enumeración con `itertools` en la prueba | caso 16 (660 cabe; 661 quita exactamente uno, el único que más ahorra) |
| Itinerario real | enumeración independiente del coordinador | caso 19c (quita A01 y luego A12; 613,1 ± 0,1 min) |
| Instancias | lista de la spec | caso 19d |
| Script de medición | FB = HK antes de escribir (k ≤ 9 en el proceso principal; k ≥ 10 con el valor del hijo) → `ValueError` y no escribe | T18 con medidor falso que devuelve un valor alterado |
| Calidad | brecha ≥ 0 (si no, `ValueError`); resumen = promedio y máximo del detalle | caso 20, T20 |
| Tablas y gráfica | CSV de ejemplo escritos por la prueba | caso 20 |

Construcción de la matriz del caso 16 (propuesta; la prueba la comprueba por enumeración antes de usarla, para no depender de que el razonamiento esté bien): partida 0; atractivos 1..5 en un mismo punto P (arcos 0 entre ellos, como T03↔T05) y el atractivo 6 en un punto Q; en minutos, 0↔P = 60 en ambos sentidos, P↔Q = 90, 0→Q = Q→0 = 150. Todo recorrido óptimo cuesta 60 + 90 + 150 = **300 min** → con 6 visitas de 60 min la jornada es 660 y **cabe**. Variante 301: 0→Q = Q→0 = 151 → 661, no cabe; quitar el 6 deja 0→P→0 = 120 min (jornada 420, ahorro 241), y quitar cualquiera de 1..5 deja 301 min (jornada 601, ahorro 60): se quita **exactamente uno, el 6**, que es único. La matriz se escribe en segundos (× 60).

**Corrección (B3, 2026-11-11):** la propuesta anterior es incorrecta. El recorrido 0→P→Q→P→0 cuesta 60 + 90 + 90 + 60 = 300 min sin importar cuánto valga 0↔Q, así que la variante no llega a 301. La prueba usa una línea S–P–Q asimétrica: Q→P = 91 y Q→S = 151, el resto igual. Por enumeración da 300 en el caso base, 301 en la variante, 120 sin el 6 y 301 sin cualquiera de 1..5. El resultado del caso 16 de la spec no cambia: se quita X6, con un ahorro de 241 min.

Cada prueba se escribe antes del código y se ve fallar con el `NotImplementedError` del stub. Las que verifican código ya hecho (propiedad, red real) se validan con una **mutación temporal** que debe hacerlas fallar y luego se restaura (p. ej. en HK sumar `T[L[j]][L[i]]` en lugar de `T[L[i]][L[j]]`, que rompe la asimetría; en el itinerario quitar el de menor ahorro).

## Medición (sección 6)

- **Qué se mide**: solo `fuerza_bruta(T, s, lugares)` y `held_karp(T, s, lugares)`, con `T` como lista de listas de `float` ya construida y `lugares` como índices. Fuera del cronómetro: leer la matriz, convertirla, sortear la muestra, traducir ids, la verificación FB = HK en el proceso principal, comparar el valor del hijo, `tracemalloc`, el contador (desactivado: `None`), la calidad, el itinerario y escribir archivos.
- **Cómo**: `medir_en_hijo` para los dos métodos (mismo modo para que sean comparables y para poder interrumpir la FB a los 5 min); 5 repeticiones y mediana; si la primera pasa de 60 s, una sola; si pasa de 300 s, `no_completada` y los k mayores de ese método quedan `no_ejecutada`. El cronómetro (`perf_counter_ns`) está dentro del hijo y rodea solo la llamada; arrancar el intérprete, importar y recibir `T` por *pickle* no cuentan. Unidad: **ms**.
- **Misma máquina** (`maquina.json`), portátil enchufado y sin otros procesos pesados. **La corrida real la lanza el usuario** (≈ 10–15 min); el implementer solo hace humo con `ks=(5, 6, 7, 8)`, `repeticiones=1` y salida en una carpeta temporal.
- **Memoria**: `rutas.r4.medir_memoria` aparte, sin cronómetro. Lo corre el implementer (unos segundos).
- **Calidad e itinerario**: no se cronometran (spec). Los corre el implementer.
- **Informe**: tabla del Anexo, gráfica en escala logarítmica, cocientes medidos frente a predichos, mayor k de cada método, memoria estimada frente a medida.

## Trazabilidad

### Casos de prueba de la spec → tarea → prueba

| Caso | Tarea | Prueba |
|---|---|---|
| 1 Los 6 recorridos de la matriz de clase (óptimo 35) | T4, T5 | `tests/test_tsp_clase.py::test_caso_1_seis_recorridos`, `::test_caso_1_2_fuerza_bruta` |
| 2 FB y HK → (35, [0, 1, 3, 2, 0]) | T5, T8 | `tests/test_tsp_clase.py::test_caso_1_2_fuerza_bruta`, `::test_caso_2_held_karp` |
| 3 Tabla de Held-Karp (12 celdas) | T7 | `tests/test_held_karp.py::test_caso_3_tabla` |
| 4 Voraz no óptimo (39, 11,43 %) | T6 | `tests/test_tsp_clase.py::test_caso_4_voraz_no_optimo` |
| 4b Ejemplo simétrico en una vía (16 frente a 14) | T5, T6, T8 | `tests/test_tsp_clase.py::test_caso_4b_via` (enumera con `itertools`: 4 de 14 y 2 de 16) |
| 5 Asimetría: inverso cuesta 40 | T4, T8 | `tests/test_tsp_clase.py::test_caso_5_asimetria` |
| 6 k = 1 | T5, T6, T8 | `tests/test_tsp_clase.py::test_caso_6_k1` (parametrizada por método) |
| 7 k = 2 | T5, T6, T8 | `tests/test_tsp_clase.py::test_caso_7_k2` (parametrizada) |
| 8 k = 0 | T5, T6, T8 | `tests/test_tsp_clase.py::test_caso_8_k0` (parametrizada) |
| 9 Arco imposible y todo `inf` | T5, T6, T8 | `tests/test_tsp_clase.py::test_caso_9_arco_inf`, `::test_caso_9_sin_recorrido_finito` (parametrizadas) |
| 10 Errores de entrada | T4, T5, T6, T8 | `tests/test_tsp_clase.py::test_validar_entrada`, `::test_caso_10_errores` (parametrizada: método × entrada) |
| 11 Propiedad FB = HK, recorrido válido, brecha ≥ 0 | T11 | `tests/test_tsp_propiedad.py::test_caso_11_fb_igual_hk_y_voraz` |
| 12 FB = mínimo con `itertools.permutations` | T11 | `tests/test_tsp_propiedad.py::test_caso_12_fb_contra_itertools` |
| 13 Generador propio | T3 | `tests/test_permutaciones.py::test_caso_13_orden_lexicografico`, `::test_uno_y_vacio`, `::test_no_modifica_entrada`, `::test_entrada_desordenada` |
| 14 Memoria estimada | T10 | `tests/test_conteos_r4.py::test_caso_14_memoria` |
| 15 Conteos (HK con contador; FB teórico) | T9, T10 | `tests/test_held_karp.py::test_caso_15_contador`, `::test_contador_igual_a_lecturas_de_T`, `::test_sin_contador_por_defecto`; `tests/test_conteos_r4.py::test_caso_15_conteos_teoricos` |
| 16 Itinerario en la frontera (660 / 661) | T14 | `tests/test_itinerario.py::test_caso_16_cabe_justo`, `::test_caso_16_quita_uno` |
| 17 Desempate lexicográfico de FB | T5, T8 | `tests/test_tsp_clase.py::test_caso_17_desempate` |
| 18 Envoltorio por ids | T13 | `tests/test_por_ids.py::test_caso_18_por_ids` |
| 19a FB = HK en la red real, k = 5..8 | T16 | `tests/test_red_real_r4.py::test_caso_19a_fb_igual_hk` |
| 19b HK k = 12 en la red real | T16 | `tests/test_red_real_r4.py::test_caso_19b_hk_k12` |
| 19c Itinerario por defecto (A01, A12; 613,1 min) | T16 | `tests/test_red_real_r4.py::test_caso_19c_itinerario` |
| 19d Muestra anidada con semilla 2026 | T12 | `tests/test_instancias_r4.py::test_caso_19d_muestra_anidada` |
| 20 Tablas y gráfica desde CSV de ejemplo; calidad = promedio y máximo | T20, T21 | `tests/test_calidad_r4.py::test_caso_20_resumen`; `tests/test_tablas_r4.py::test_caso_20_tabla_exactas`, `::test_caso_20_grafica`, `::test_caso_20_calidad_e_itinerario` |
| Bordes: T03/T05 (costo 0), matriz simétrica | T11 | `tests/test_tsp_propiedad.py::test_costo_cero_entre_lugares`, `::test_matriz_simetrica` |
| Bordes del itinerario (6..8, no atractivo, partida entre ellos, cabe de entrada) | T14 | `tests/test_itinerario.py::test_errores`, `::test_cabe_de_entrada_no_quita` |
| Bordes de medición (> 1 min una vez; > 5 min `no_completada`, fila no omitida) | T17, T18 | `tests/test_medicion.py::test_en_hijo_devuelve_valor`, `::test_en_hijo_valor_no_completada`; `tests/test_medir_exactas.py::test_no_completada_y_no_ejecutada` |

### Puntos del enunciado → tarea

| Punto | Tarea |
|---|---|
| R4, párrafo inicial: partida Armenia, k lugares al azar con semilla fija entre todas las categorías, matriz asimétrica de R2 | T12, T13, T18 |
| R4.1 Fuerza bruta propia | T3, T5 |
| R4.1 Held-Karp propio, subestructura y recurrencia (tabla del caso 3 para el informe), devuelve el recorrido | T7, T8 |
| R4.1 k de 5 a 12 o hasta el límite; mayor k resuelto; gráfica | T18, T21, T22 |
| R4.1 Memoria según el tamaño de la tabla | T10, T19, T21 |
| R4.1 FB = HK en los k que FB resuelve | T11, T16, T18 |
| R4.2 Heurística voraz propia (vecino más cercano) y su justificación | T6 (justificación en el informe) |
| R4.3 Calidad: k = 5, 8, 10, 12, ≥ 5 instancias, promedio y máximo | T12, T20, T21 |
| R4.4 Itinerario de un día: 6 a 8 atractivos, Held-Karp, 11 h, quitar justificando, duración final | T14, T15, T16, T21 |
| R4.5 Voraz frente a óptimo y Dijkstra | T6 (casos 4 y 4b; texto del informe) |
| R5 (consumidor): Held-Karp y voraz en vivo por ids, itinerario con otra partida | T13, T14 |
| 6.1 Misma máquina; procesador, RAM, SO, versión | T1, T18, T21 |
| 6.2 Solo el algoritmo | T9, T17, T18, T19 |
| 6.3 5 repeticiones, mediana; una si > 1 min | T17, T18 |
| 6.4 Unidad ms | T18, T21 |
| 6.5 Semilla fija documentada | T12, T21 |
| 6.6 Verificación antes de medir | T3–T11, T16, T18, T20 |
| 6.7 Límite de 5 min → «no completada» | T18, T21 |
| 6.8 Tablas y gráficas desde CSV/JSON, con unidad | T21 |
| Anexo, Requerimiento 4 (las tres tablas, la gráfica, totales del itinerario) | T15, T20, T21 |
| Anexo de IA | T23 (y cada tarea con IA) |

## Riesgos

- **Duración de la medición real**: ≈ 10–15 min, dominada por la FB en k = 11 (1–5 repeticiones según pase o no de 60 s) y k = 12 (5 min hasta `no_completada`). Si la FB k = 11 tarda justo menos de 60 s, se hacen 5 repeticiones (≈ 5 min); es lo que pide el protocolo. Si el script falla al final (FB ≠ HK), no escribe nada y se pierde la corrida: es lo que pide la spec; el implementer lo cubre con pruebas y con la corrida de humo.
- **Valor desde el hijo**: el cambio en `medir_en_hijo` es opcional y compatible; las pruebas existentes de `test_medicion.py` y las de R1–R3 deben seguir verdes sin cambios (lo comprueba T17 con la suite completa sin `red`).
- **`tracemalloc`**: mide lo que asigna Python durante la llamada, no el tamaño de `T` (ya existía). El pico depende de la versión de Python; se anota en `tablas_r4.md` junto a la máquina.
- **Precisión**: los costos son sumas de `float`; FB y HK suman en distinto orden, por eso la comparación usa ±1e-6 s y nunca igualdad exacta. Las pruebas con matrices de enteros (casos 1–17) sí comparan exacto.
- **Desempate HK frente a FB**: con empates de costo pueden devolver recorridos distintos; las pruebas comparan tiempos y validez del recorrido (spec), salvo el caso 17 para la FB.
- **Python 3.13 ausente**: ver «Decisiones para el usuario», 3.
- **R5** usa `resolver_por_ids` e `itinerario_dia`: sus firmas quedan fijadas aquí; cambiarlas después obliga a revisar la spec de R5.

## Decisiones

Tomadas en la spec (Puerta 1, 2026-11-11): vecino más cercano con desempate por menor índice; FB con generador lexicográfico propio, sin poda; muestra anidada con semilla 2026; quitar del itinerario el atractivo que más reduce la jornada recalculando con HK; itinerario por defecto C01 + A05, A08, A04, A14, A06, A07, A12, A01; memoria = 12 B por celda + `tracemalloc` aparte; 10 instancias por k (2026..2035); tabla 2^k × k; resultados en `results/r4/`; FB y HK con `medir_en_hijo`; tolerancia 1e-6 s; `no_ejecutada` tras un `no_completada`; eje y logarítmico; no tocar `.gitignore`.

Tomadas por el plan (menores; el usuario puede cambiarlas en la Puerta 2):
1. Un módulo por algoritmo en `rutas/r4/` (`fuerza_bruta.py`, `held_karp.py`, `vecino.py`, `permutaciones.py`, `recorrido.py`) y scripts separados por experimento (`instancias`, `itinerario`, `calidad`, `medir_exactas`, `medir_memoria`, `tablas`).
2. El generador entrega **tuplas** (copia O(k) por permutación, igual de cara que sumar el costo): así el consumidor puede guardar la mejor sin copiarla y la prueba del caso 13 compara directo con `itertools`.
3. Held-Karp trabaja con `L = sorted(lugares)`; `padre` guarda el índice local (0..k−1).
4. Contador: lista `[n]` opcional, incrementada una vez por máscara (no dentro del ciclo interno) y contrastada con las lecturas reales de `T`.
5. En `medir_exactas`, HK se calcula en el proceso principal para **todo** k como referencia (≤ 1 s) y con ella se comparan los valores de los hijos de FB y HK; la FB del proceso principal solo para k ≤ 9.
6. `itinerario_dia` recibe índices y `visita_min = {índice: minutos}` de todos los atractivos del catálogo; devuelve `(filas, quitados, totales)` sin redondear; el nombre del lugar lo agrega el script.
7. `instancias`, `itinerario`, `calidad` y `medir_memoria` los corre el implementer (deterministas, cortos, sin cronómetro); solo `medir_exactas` la corre el usuario.
8. El caso 19d se prueba **sin** el marcador `red` (`tests/test_instancias_r4.py`): solo necesita `data/catalogo.csv`, que está versionado. Así corre siempre.
9. `tablas_r4.md` incluye una tabla de cocientes medidos frente a predichos entre k consecutivos (sale del CSV; sostiene el párrafo de la sección 6.8 que pide la spec en «Medición»).
10. `resolver_por_ids` con un id desconocido o un método desconocido → `ValueError`. En el vecino, un regreso `inf` también da `ValueError("no hay recorrido finito")`, igual que en FB y HK.
11. El vecino recorre `sorted(lugares)` una vez con una lista de visitados (O(k²) exacto), en lugar de ordenar los pendientes en cada paso.
12. Los scripts de R4 leen el catálogo con `pandas.read_csv` (como R2), no con `cargar_catalogo`, para poder probarlos con catálogos sintéticos pequeños.

## Decisiones para el usuario (Puerta 2)

1. **Modificar `rutas/medicion.py` (módulo compartido)**: agregar `devolver_valor=False` a `medir_en_hijo` y el campo `valor=None` al final de `ResultadoMedicion`. Hace falta para cumplir el punto 10 de la spec (en k ≥ 10 la FB solo se ejecuta en el hijo de la medición, que hoy no devuelve su resultado). Es compatible: con el valor por defecto nada cambia en R1–R3. Alternativa sin tocarlo: correr la FB otra vez en un hijo aparte solo para verificar, lo que duplica el tiempo de k = 10 y 11 (≈ +3 min) y contradice la redacción de la spec.
2. Confirmar las decisiones menores 2–12 de arriba (en especial la 6, porque fija la firma que usará R5, y la 8).
3. **Python 3.13**: no está instalado (`python3` = 3.14.6) y no hay `.venv`. Opciones: (a) instalar 3.13 (p. ej. `brew install python@3.13`) y crear `.venv` como dice el README — recomendada, mantiene la misma versión que R1–R3; (b) crear `.venv` con 3.14 si todas las versiones de `requirements.txt` instalan, anotando la versión en `maquina.json` y en el README. T1 se detiene hasta que el usuario elija.

## Bloqueos

Ninguno.

## Puerta 2 (2026-11-11), resuelta por el usuario
1. Se aprueba modificar `rutas/medicion.py`: `medir_en_hijo(..., devolver_valor=False)` y campo `ResultadoMedicion.valor=None` al final. Compatible con R1–R3, cuya suite debe seguir en verde.
2. Se aprueban las decisiones menores 1–12 del plan, incluida la firma de `itinerario_dia` (índices; devuelve `(filas, quitados, totales)` sin redondear) y el caso 19d sin la marca `red`.
3. Python: se instaló Python 3.13.18 con Homebrew (`/opt/homebrew/bin/python3.13`) y se creó `.venv` con `requirements.txt` (la suite sin `red` pasa: 279 pasan y 1 se salta). R1–R3 usaron 3.13.8: misma versión menor y otro parche. `maquina.json` de R4 registra 3.13.18, y el README lo aclara en T23. T1 queda resuelta: solo verifica `.venv/bin/python --version` y la suite.

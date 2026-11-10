# Plan — R3 Envolvente convexa de la red vial (QuickHull)

Spec: `specs/r3-envolvente-convexa/spec.md` (aprobada en Puerta 1, 2026-11-10, con sus «Decisiones»). Enunciado: sección 5, Requerimiento 3 (párrafo «Coordenadas», punto 1 Algoritmo, punto 2 Experimento); sección 6 (protocolo experimental); formato en el Anexo, Requerimiento 3 (tabla `Conjunto de puntos | n | Vértices de la envolvente | Tiempo propio (ms) | Tiempo SciPy (ms) | Cociente`). Peso 20 %.

## Resumen

R3 toma los nodos de la componente de R1 (atributos `x_utm`, `y_utm`, EPSG:32618) y hace cuatro cosas, cada una con su comando:

1. **Algoritmo** (sin comando, funciones puras en `rutas/r3/envolvente.py`): predicado `cruz`, **QuickHull recursivo** propio (`envolvente` + `_lado`), `area` (fórmula del zapato con enteros) y `normalizar`. Sin E/S, sin NumPy, sin SciPy.
2. **Archivos de la envolvente** (`python -m rutas.r3.archivos`): envolvente de la red real → `data/processed/envolvente.csv` y `data/processed/envolvente.geojson` (los usa R5). No es una medición; lo corre el implementer (como la matriz en R2).
3. **Medición** (`python -m rutas.r3.medir_envolvente`): nodos de la red y cuadrados de 1 000 / 10 000 / 50 000 puntos con semilla 2026; comprueba antes que propia y SciPy dan los mismos vértices (si no, `ValueError` y no escribe nada); mide ambas con `medir_en_proceso`; escribe `r3_envolvente.csv`, `r3_puntos.json`, `maquina.json`. **La corre el usuario con el portátil enchufado.**
4. **Tablas y gráfica** (`python -m rutas.r3.tablas`): `tablas_r3.md` y `r3_envolvente.png` desde los CSV/JSON/GraphML.

Además, en el primer bloque, la **tarea pequeña de R2** aprobada en Puerta 1: unidad de la pendiente del ajuste por versión en `tablas_r2.md` (cola en µs/nodo, lineal en ms/nodo), regenerando solo el Markdown desde los CSV ya medidos.

No hay contradicción entre la spec y el enunciado: la spec redondea a enteros, quita repetidos, no cuenta alineados, implementa un divide y vencerás propio (QuickHull), compara con `scipy.spatial.ConvexHull` en todas las pruebas no degeneradas y mide los cuatro conjuntos del Anexo con semilla fija. Sin bloqueos.

## Estado del repositorio que se reutiliza

- `rutas/config.py` (`RAIZ`, `DATA_PROCESSED`, `RESULTS_R1`, `RESULTS_R2`, `EPSG_UTM = 32618`): se agregan `RESULTS_R3`, `ENVOLVENTE_CSV`, `ENVOLVENTE_GEOJSON`.
- `rutas/medicion.py`: `medir_en_proceso(funcion, preparar, repeticiones=5, umbral_una_s=60, limite_s=300)`, `ResultadoMedicion(tiempo_ms, repeticiones, completada, tiempos_ms)`, `NO_COMPLETADA`, `info_maquina()`. Sin cambios.
- `rutas/r1/persistencia.py`: `cargar_grafo_procesado(carpeta)` (lee `x_utm`, `y_utm` como `float`), `guardar_grafo(G, carpeta)` (para las carpetas sintéticas de las pruebas).
- `rutas/r1/utm.py`: `a_latlon(xs, ys)` y `a_utm(lons, lats)` (pyproj, `always_xy=True`), `agregar_utm_a_nodos(G)`.
- `rutas/r1/tablas.py`: `a_markdown(df, decimales)`.
- `rutas/r2/tablas.py`: `_tabla_ajuste(ajuste)` y `main(results)` (tarea pequeña de R2).
- `tests/conftest.py`: `grafo_sintetico`, fixture `grafo_procesado_real` (se salta si falta el grafo), `cargar_red_clase()`. Marcador `red` ya registrado en `pyproject.toml`.
- `tests/datos/red_clase.json`: claves `_origen`, `red` (9 nodos con `x`, `y` en metros; 24 aristas), `R2`. **Ojo:** `tests/test_dijkstra_clase.py::test_red_clase_versionada` exige hoy `set(datos) == {"_origen", "red", "R2"}`; al agregar `R3` esa aserción se actualiza en la misma tarea (T2).
- `estudio/casos_prueba.json` (ignorado por git): sección `R3` con `nodos_red` (vértices 9, 7, 8, 3, 2; 4 y 6 sobre lados; área 585 000 m²), `empate`, `rectangulo` y `scipy_falla` (`colineales`, `dos_puntos`).
- `data/processed/` está versionado archivo por archivo (`grafo_componente.graphml`, `matriz_tiempos.csv`, …): `envolvente.csv` y `.geojson` se versionan igual (commit del usuario). `results/r3/` se crea nuevo.
- Entorno: Python 3.13.8, SciPy 1.18.1, NumPy, pyproj, matplotlib 3.11.2 en `.venv`. No se instala nada; no se tocan `.gitignore`, `pyproject.toml` ni `requirements.txt`.

## Módulos y archivos

Subpaquete `rutas/r3/`, un módulo por idea. El algoritmo (`envolvente.py`) no hace E/S ni importa NumPy/SciPy; la preparación de puntos, la referencia SciPy, los archivos, la medición y las tablas van aparte porque solo se cronometra el algoritmo.

| Ruta | Acción | Responsabilidad | Tipo |
|---|---|---|---|
| `rutas/config.py` | modificar | `RESULTS_R3 = RAIZ / "results" / "r3"`, `ENVOLVENTE_CSV = DATA_PROCESSED / "envolvente.csv"`, `ENVOLVENTE_GEOJSON = DATA_PROCESSED / "envolvente.geojson"` | constantes |
| `rutas/r3/__init__.py` | crear | Vacío | — |
| `rutas/r3/envolvente.py` | crear | `cruz`, `envolvente`, `_lado`, `area`, `normalizar`; `sys.setrecursionlimit(20_000)` con su comentario | **algoritmo puro** |
| `rutas/r3/puntos.py` | crear | `redondear`, `preparar_puntos`, `puntos_de_grafo`, `puntos_cuadrado` (`SEMILLA = 2026`, `LADO = 10**6`) | preparación (fuera del cronómetro) |
| `rutas/r3/referencia.py` | crear | `vertices_scipy(puntos)` (solo verificar y medir; importa SciPy) | verificación |
| `rutas/r3/archivos.py` | crear | `escribir_envolvente(vertices, carpeta)`, `main(processed)` (script) | datos para R5 |
| `rutas/r3/medir_envolvente.py` | crear | `COLUMNAS`, `TAMANOS`, `conjuntos`, `comprobar_iguales`, `medir_conjunto`, `main` (script) | medición |
| `rutas/r3/tablas.py` | crear | `grafica_envolvente`, `main` (`tablas_r3.md` y `r3_envolvente.png`) | gráficas/tablas |
| `rutas/r2/tablas.py` | modificar | `_tabla_ajuste`: unidad de la pendiente por versión (tarea pequeña de R2) | tablas |
| `tests/datos/red_clase.json` | modificar | Agregar la sección `R3` (copiada sin cambios) y actualizar `_origen` | datos de prueba |
| `tests/conftest.py` | modificar | `cargar_casos_r3()` y `comprobar_envolvente(vertices, puntos)` (invariantes del caso 13) | pruebas |
| `tests/test_config.py` | modificar | `test_rutas_r3` | pruebas |
| `tests/test_dijkstra_clase.py` | modificar | `test_red_clase_versionada`: claves `{"_origen", "red", "R2", "R3"}` | pruebas |
| `tests/test_tablas_r2.py` | modificar | Unidades de la pendiente | pruebas |
| `tests/test_envolvente.py`, `test_puntos_r3.py`, `test_envolvente_clase.py`, `test_envolvente_propiedad.py`, `test_archivos_r3.py`, `test_medir_envolvente.py`, `test_tablas_r3.py`, `test_red_real_r3.py` | crear | Pruebas (`test_red_real_r3.py` con `pytestmark = pytest.mark.red`) | pruebas |
| `README.md` | modificar | Sección «Reproducir R3» | doc |
| `docs/anexo-ia.md` | modificar (local, ignorado) | Entradas de R3 | doc |

## Estructuras de datos y firmas

**Punto**: `tuple[int, int]` `(x, y)` en metros UTM, con `int` de Python. Las tuplas se comparan lexicográficamente de forma nativa (x, luego y), que es justo el orden que usan el mínimo/máximo iniciales y el desempate. Los `int` de Python son de precisión arbitraria, así que `cruz` no desborda nunca (en el caso 8 vale 9·10¹⁸, que además cabe en 64 bits): equivale a lo que el enunciado pide con enteros de 64 bits, sin flotantes en ninguna comparación geométrica.

**Conjunto de puntos**: `list[tuple[int, int]]` (lista de Python; QuickHull la recorre una vez por nivel para repartirla). No se usan arreglos de NumPy en el algoritmo: así el código propio es Python puro y la comparación con SciPy (C) muestra el efecto del lenguaje, que es lo que pide explicar el punto 2.

**Polígono**: `list[tuple[int, int]]` de vértices en sentido **antihorario**, empezando por el de menor `y` y, en empate, menor `x`; sin repetir el primero al final (el cierre se agrega solo al escribir el GeoJSON y al dibujar).

```python
# rutas/r3/envolvente.py  (algoritmo puro, sin E/S)
import sys
# QuickHull es recursivo porque sigue la recurrencia del informe. Con particiones parejas la
# profundidad es O(log n), pero en el peor caso llega a O(n) y el límite por defecto de Python
# (~1 000 llamadas) cortaría la ejecución con RecursionError. 20 000 cubre los 8 791 nodos de la
# red y los 5 000 puntos de la parábola (casos 15 y 16).
sys.setrecursionlimit(max(sys.getrecursionlimit(), 20_000))

def cruz(o, a, b) -> int:
    """(a.x − o.x)(b.y − o.y) − (a.y − o.y)(b.x − o.x): > 0 si b está a la izquierda de o→a,
    0 si están alineados, < 0 si está a la derecha. Enteros, sin flotantes."""

def envolvente(puntos) -> list[tuple[int, int]]:
    """Vértices de la envolvente convexa (QuickHull), antihorario desde el de menor (y, x).
    [] si no hay puntos; [p] si hay un solo punto distinto; [extremo1, extremo2] si todos están
    alineados. Tolera repetidos. No modifica `puntos`."""

def _lado(puntos, a, b) -> list[tuple[int, int]]:
    """Recursiva. `puntos` están todos estrictamente a la izquierda de a→b. Devuelve los vértices
    de la envolvente que hay entre a y b (sin incluirlos), en el orden en que se recorren de a a b."""

def area(vertices) -> float:
    """Área del polígono con la fórmula del zapato: el doble del área se calcula con enteros (exacto)
    y se divide entre 2 al final (abs). 0 con menos de 3 vértices."""

def normalizar(vertices) -> list[tuple[int, int]]:
    """Mismo polígono en sentido antihorario (si el área con signo es negativa se invierte) y rotado
    para empezar en el vértice de menor (y, x). Sirve para comparar con SciPy."""
```

Esqueleto de QuickHull (el código final debe parecerse a esto; corto y fiel a la recurrencia):

```text
envolvente(puntos):
  si no hay puntos: return []
  A = min(puntos); B = max(puntos)                 # lexicográfico (x, luego y): O(n), sin ordenar
  si A == B: return [A]                            # un solo punto distinto (con o sin repetidos)
  izq_AB = [p para p en puntos si cruz(A, B, p) > 0]   # estrictamente; los alineados se descartan
  izq_BA = [p para p en puntos si cruz(B, A, p) > 0]
  ciclo = [A] + _lado(izq_AB, A, B) + [B] + _lado(izq_BA, B, A)   # sentido horario
  ciclo.reverse()                                  # antihorario
  k = índice del mínimo de ciclo por (y, x); return ciclo[k:] + ciclo[:k]

_lado(puntos, a, b):
  si no hay puntos: return []
  c = el de mayor cruz(a, b, c); en empate, el menor lexicográfico   # más lejano de la recta ab
  izq_ac = [p para p en puntos si cruz(a, c, p) > 0]
  izq_cb = [p para p en puntos si cruz(c, b, p) > 0]
  # los demás (dentro del triángulo a, c, b o sobre sus lados) se descartan
  return _lado(izq_ac, a, c) + [c] + _lado(izq_cb, c, b)
```

Por qué así: los puntos a la izquierda de a→b están «por fuera» del lado ab visto desde el polígono que se recorre en sentido horario (A → arriba → B → abajo), y a→c→b sigue ese mismo sentido; por eso se ensambla en horario y se invierte una sola vez al final. Comprobado a mano con el caso 1 (A = (0,0), B = (4,4): ciclo horario (0,0), (0,4), (4,4), (4,0) → antihorario desde (0,0): (0,0), (4,0), (4,4), (0,4)) y con el caso 2 (empate en `cruz` = 50 entre (2,5), (5,5), (8,5): se elige (2,5); luego (8,5) sale en la recursión de c→B y (5,5) queda alineado con `cruz` = 0 y se descarta). Con todos los puntos alineados `izq_AB` e `izq_BA` quedan vacías y el resultado es `[A, B]` rotado al de menor (y, x). Los repetidos de A, B o c tienen `cruz` = 0 y se descartan solos, sin necesidad de un conjunto.

**Preparación** (fuera del cronómetro):

```python
# rutas/r3/puntos.py
SEMILLA = 2026
LADO = 10**6                                  # cuadrado [0, 10^6) × [0, 10^6), en metros

def redondear(x) -> int:                      # math.floor(x + 0.5): empates .5 hacia +inf
def preparar_puntos(xs, ys) -> list[tuple[int, int]]:
    """Redondea cada coordenada con `redondear`, quita repetidos (set) y devuelve sorted(...).
    zip(xs, ys, strict=True): largos distintos → ValueError."""
def puntos_de_grafo(G) -> list[tuple[int, int]]:
    """preparar_puntos de x_utm, y_utm de los nodos de G, recorridos en sorted(G.nodes)."""
def puntos_cuadrado(n, semilla=SEMILLA, lado=LADO) -> list[tuple[int, int]]:
    """rng = random.Random(semilla); n veces (rng.randrange(lado), rng.randrange(lado)) (x y luego y);
    se quitan repetidos y se ordena. Devuelve n_obtenido ≤ n puntos."""
```

Cada cuadrado usa un `random.Random(2026)` **nuevo** (así cada conjunto se reproduce solo, sin depender del orden en que se generan; el de 1 000 resulta ser un prefijo del de 10 000, lo que no afecta la medición y se documenta en `r3_puntos.json`).

**Referencia SciPy** (solo verificación y medición):

```python
# rutas/r3/referencia.py
def vertices_scipy(puntos) -> list[tuple[int, int]]:
    """ConvexHull(numpy.array(puntos, dtype=numpy.float64)); vértices hull.vertices (en 2-D vienen en
    sentido antihorario) traducidos a tuplas de int de Python y pasados por normalizar.
    Deja pasar scipy.spatial.QhullError (todos alineados, menos de 3 puntos)."""
```

**Archivos** (`rutas/r3/archivos.py`):

```python
def escribir_envolvente(vertices, carpeta=DATA_PROCESSED) -> tuple[Path, Path]
#   envolvente.csv con el módulo csv: encabezado orden,x_utm,y_utm,lat,lon; orden = 1..h en sentido
#   antihorario; x_utm, y_utm enteros; lat, lon = a_latlon(...) con repr(float)
#   envolvente.geojson: FeatureCollection con un Feature Polygon en [lon, lat] (EPSG:4326), anillo
#   cerrado (primer punto repetido al final), antihorario (RFC 7946); properties
#   {"vertices": h, "area_km2": area(vertices) / 1e6}
def main(processed=DATA_PROCESSED)
#   G = cargar_grafo_procesado(processed); puntos = puntos_de_grafo(G); v = envolvente(puntos);
#   si set(v) != set(vertices_scipy(puntos)) o normalizar(v) != vertices_scipy(puntos): ValueError
#   (no escribe nada); si no, escribe los dos archivos e imprime h y el área en km²
```

**Medición** (`rutas/r3/medir_envolvente.py`):

```python
TAMANOS = (1_000, 10_000, 50_000)
COLUMNAS = ["conjunto", "n", "vertices", "tiempo_propio_ms", "tiempo_scipy_ms", "cociente",
            "repeticiones"]                       # las 6 del Anexo primero, luego la ampliada
NOMBRE_RED = "Nodos de la red"
def nombre_cuadrado(n) -> str                     # "Cuadrado, 1 000 puntos" (separador de miles: espacio)
def conjuntos(puntos_red, semilla=SEMILLA, tamanos=TAMANOS) -> list[tuple[str, int, list]]
#   [(nombre, n_pedido, puntos)] en el orden del Anexo; para la red n_pedido = len(puntos_red)
def comprobar_iguales(lista) -> None
#   para cada conjunto: envolvente(puntos) vs vertices_scipy(puntos), por conjunto de vértices y
#   normalizados; si difieren → ValueError(f"{nombre}: propia {h1} vértices, SciPy {h2} ...")
#   (error explícito, no assert)
def medir_conjunto(nombre, puntos, repeticiones=5, medir=medir_en_proceso) -> dict
#   arreglo = numpy.array(puntos, dtype=numpy.float64)          # fuera del cronómetro
#   propio = medir(envolvente, lambda: (puntos,), repeticiones=repeticiones)
#   scipy  = medir(ConvexHull, lambda: (arreglo,), repeticiones=repeticiones)
#   fila: n = len(puntos); vertices = len(envolvente(puntos)) (corrida fuera del cronómetro);
#   tiempos = mediana en ms o "no completada"; cociente = propio / scipy o "no completada";
#   repeticiones = min(propio.repeticiones, scipy.repeticiones)
def main(processed=DATA_PROCESSED, salida=RESULTS_R3, repeticiones=5)
#   carga el grafo → puntos_de_grafo → conjuntos → comprobar_iguales (antes de medir nada) →
#   medir_conjunto × 4 → escribe r3_envolvente.csv, r3_puntos.json, maquina.json
```

Las `lambda` se crean dentro de `medir_conjunto` (una llamada por conjunto), no dentro de un ciclo, para no repetir el error de captura que se encontró en R2 (T12). `envolvente` no modifica la lista (prueba `test_no_modifica_entrada`), así que `preparar` puede devolver siempre la misma.

**Tablas** (`rutas/r3/tablas.py`, `matplotlib.use("Agg")`):

```python
def grafica_envolvente(processed=DATA_PROCESSED, salida=RESULTS_R3) -> Path
#   puntos = puntos_de_grafo(cargar_grafo_procesado(processed)); vértices leídos de envolvente.csv;
#   nodos como puntos grises pequeños, polígono cerrado en rojo con marcadores en los vértices,
#   ejes x_utm / y_utm (m), aspecto igual, título con n y número de vértices → r3_envolvente.png
def main(results=RESULTS_R3, processed=DATA_PROCESSED)
#   tablas_r3.md: tabla del Anexo (+ Repeticiones), vértices frente a (8/3) ln n en los cuadrados,
#   semilla y n pedidos/obtenidos (r3_puntos.json), envolvente de la red (vértices y área en km² del
#   GeoJSON), máquina; unidad "ms" en los encabezados. Llama a grafica_envolvente.
```

**Tarea pequeña de R2** (`rutas/r2/tablas.py`): `ajuste_tiempo_explorados` no cambia (sigue en ms/nodo, su prueba sigue igual). Solo cambia `_tabla_ajuste`, con una constante

```python
UNIDAD_PENDIENTE = {"lineal": ("ms/nodo", 1), "cola_prioridad": ("µs/nodo", 1000)}
```

y columnas `Versión | Pendiente | Unidad de la pendiente | Ordenada (ms)` (una fila por versión con su unidad; la pendiente de la cola se multiplica por 1 000). Con los datos reales la cola pasa de «0.0003 ms/nodo» a ≈ «0.33 µs/nodo», que sí se puede leer.

**Pruebas** (`tests/conftest.py`):

```python
def cargar_casos_r3() -> tuple[dict, dict]:
    """(nodos de la red de la clase {id: (x, y)} como int, sección R3) desde tests/datos/red_clase.json."""
def comprobar_envolvente(vertices, puntos) -> None:
    """Invariantes del caso 13 (independientes de SciPy), con assert:
    - vértices sin repetir y todos en `puntos`;
    - con ≥ 3 vértices: cada tres consecutivos (cíclicamente) cumplen cruz > 0 (convexidad estricta,
      antihorario, sin alineados);
    - todo punto p cumple cruz(v_i, v_{i+1}, p) ≥ 0 para cada lado (dentro o sobre el borde); se
      omite si set(vertices) == set(puntos) (círculo, parábola: evita O(n·h) = 25·10⁶ operaciones);
    - con 2 vértices: todos los puntos alineados con ellos y entre ambos (cruz = 0);
    - el primero es el de menor (y, x)."""
```

## Recurrencia y complejidad

n = puntos del subproblema; h = vértices de la envolvente.

| Algoritmo | Tiempo | Memoria adicional | Por qué |
|---|---|---|---|
| `cruz` | O(1) | O(1) | 2 productos y 1 resta de enteros (Python: coste ligeramente mayor con enteros grandes, despreciable con coordenadas < 10⁷) |
| QuickHull (`envolvente`) | O(n log n) con particiones parejas; O(n²) en el peor caso | O(n) en listas por nivel + pila O(log n) parejo / O(n) peor caso | T(n) = T(n₁) + T(n₂) + O(n) con n₁ + n₂ ≤ n − 1 (la pasada que busca c y reparte); parejo: T(n) = 2T(n/2) + O(n) = O(n log n) por el teorema maestro (caso 2); peor caso T(n) = T(n − 1) + O(n) = O(n²) |
| Con pocos vértices (red real: 14 de 8 791) | cercano a O(n log h) en la práctica | — | cada nivel descarta los puntos del triángulo a, c, b; la recursión solo profundiza mientras quedan puntos por fuera (Barber et al. reportan O(n log r) empíricamente) |
| `area`, `normalizar` | O(h) | O(h) | una pasada |
| `preparar_puntos` | O(n log n) | O(n) | redondeo O(n), `set` O(n) esperado (tabla hash), `sorted` (Timsort) O(n log n) en el peor caso — documentación de Python, `list.sort`. Fuera de la medición |
| `puntos_cuadrado` | O(n log n) | O(n) | generación O(n) + `set` + `sorted`. Fuera de la medición |
| `ConvexHull` (SciPy) | O(n log r) empírico (Qhull, r = vértices procesados); O(n log n) | O(n) | Qhull en C, envoltorio Cython `scipy/spatial/_qhull.pyx` |

Nota para el informe sobre los casos 15 y 16: el círculo y la parábola tienen **todos** los puntos como vértices, pero QuickHull elige siempre el punto más lejano de la cuerda, que en ambas curvas es el del «medio», así que las particiones salen parejas y la profundidad es O(log n); el trabajo es Θ(n log n) porque no se descarta nada. El peor caso O(n²) con profundidad O(n) exige distribuciones donde el más lejano deja a casi todos de un lado (p. ej. puntos sobre una curva convexa con espaciado que crece geométricamente); el límite de recursión de 20 000 cubre ese caso para los tamaños del proyecto.

Fuentes (spec): Eddy 1977 (*ACM TOMS* 3(4):398–403, QuickHull en el plano); Barber, Dobkin y Huhdanpaa 1996 (*ACM TOMS* 22(4):469–483, Qhull, O(n log r) empírico); Rényi y Sulanke 1963 (*Z. Wahrscheinlichkeitstheorie* 2:75–84, número esperado de vértices ≈ (8/3) ln n en un cuadrado); documentación de Python 3.13 (`list.sort`, `sys.setrecursionlimit`); documentación y código de SciPy 1.18.1 (`scipy.spatial.ConvexHull`, `_qhull.pyx`) y de Qhull. Cormen et al. queda pendiente, como en R2.

## Datos y archivos

| Archivo | Lo escribe | Formato |
|---|---|---|
| `tests/datos/red_clase.json` | T2 (una vez; se versiona) | `{"_origen": "...", "red": {...}, "R2": {...}, "R3": {...}}`; `R3` copiada sin cambios de `estudio/casos_prueba.json`; `red` y `R2` intactas |
| `data/processed/envolvente.csv` | `rutas.r3.archivos` | `orden,x_utm,y_utm,lat,lon`; `orden` 1..h antihorario desde el de menor (y, x); `x_utm`, `y_utm` enteros (m, EPSG:32618); `lat`, `lon` en grados (EPSG:4326, `repr(float)`) |
| `data/processed/envolvente.geojson` | `rutas.r3.archivos` | `{"type": "FeatureCollection", "features": [{"type": "Feature", "properties": {"vertices": h, "area_km2": …}, "geometry": {"type": "Polygon", "coordinates": [[[lon, lat], …, [lon₁, lat₁]]]}}]}` |
| `results/r3/r3_envolvente.csv` | `rutas.r3.medir_envolvente` | `COLUMNAS`; 4 filas en el orden del Anexo: «Nodos de la red», «Cuadrado, 1 000 puntos», «Cuadrado, 10 000 puntos», «Cuadrado, 50 000 puntos»; `n` = puntos tras quitar repetidos; tiempos = mediana en ms o `"no completada"`; `cociente` = propio / SciPy sin redondear |
| `results/r3/r3_puntos.json` | `rutas.r3.medir_envolvente` | `{"semilla": 2026, "generador": "random.Random (uno nuevo por cuadrado)", "cuadrado": "[0, 1000000) x [0, 1000000), enteros, metros", "redondeo": "math.floor(x + 0.5)", "conjuntos": [{"conjunto": ..., "n_pedido": ..., "n_obtenido": ...}, ...]}` (incluye la red con `n_pedido` = nodos del grafo) |
| `results/r3/maquina.json` | `rutas.r3.medir_envolvente` | `info_maquina()` |
| `results/r3/tablas_r3.md` | `rutas.r3.tablas` | ver `main` de tablas |
| `results/r3/r3_envolvente.png` | `rutas.r3.tablas` (`grafica_envolvente`) | nodos y polígono en metros UTM |

Semilla única: **2026** (`random.Random(2026)`): cuadrados del experimento, 100 conjuntos del caso 11.

## Verificación

| Qué | Contra qué | Datos |
|---|---|---|
| `cruz`, `area`, `normalizar` | a mano | triángulos y cuadrados pequeños; caso 8 (9·10¹⁸) |
| `preparar_puntos` | a mano | caso 9 (2,5 → 3; −0,5 → 0; 2,4999 → 2; fusión de repetidos) |
| `envolvente` | casos resueltos a mano | casos 1–8 y bordes (0, 1, 2 puntos, alineados, repetidos) |
| `envolvente` | `scipy.spatial.ConvexHull` (normalizado y por conjunto) | casos 1–4, 8, 10; propiedad (11, 100 conjuntos); cuadrados (12); red real (14); círculo (15). En 6 y 7 se comprueba que SciPy lanza `QhullError` |
| `envolvente` | red de la clase (resuelta a mano y con SciPy) | caso 10: nodos 9, 7, 8, 3, 2; área 585 000 m² |
| Toda salida | invariantes geométricos (sin SciPy) | caso 13 con `comprobar_envolvente` en todas las pruebas |
| `area` en la red | `ConvexHull(...).volume` (en 2-D es el área) ± 1 m² | caso 14 |
| Archivos | ida y vuelta UTM → lat/lon → UTM < 1 m; polígono cerrado | caso 17 (sintético y real) |
| Medición | `comprobar_iguales` antes de medir (`ValueError`, no escribe) | los 4 conjuntos |
| Resultados medidos | `r3_envolvente.csv`: 4 filas en orden, `vertices` = 14 en la red, `n` = `n_obtenido` de `r3_puntos.json`, cociente = propio / SciPy | prueba `red` que se salta si no existe |

Cada prueba se escribe antes del código y se ve fallar con el `NotImplementedError` del stub. Las que verifican código ya hecho (11, 12, 14, 15, 16) se validan con una **mutación temporal** que debe hacerlas fallar y luego se restaura, p. ej. en `_lado` usar `>= 0` en lugar de `> 0` al repartir (los alineados se vuelven vértices) o desempatar por el **mayor** lexicográfico.

## Medición (sección 6)

- **Qué se mide**: la llamada `envolvente(puntos)` con la lista ya preparada y `ConvexHull(arreglo)` con el `numpy.array` de `float64` ya construido (decisión del grupo). Fuera del cronómetro: cargar el grafo, `puntos_de_grafo`, `puntos_cuadrado`, la conversión a NumPy, la comprobación previa, contar vértices y escribir archivos.
- Ambas con `medir_en_proceso`, 5 repeticiones, mediana en **ms**; una sola si la primera pasa de 60 s; «no completada» si pasa de 300 s (en el mismo proceso no se puede interrumpir: se reporta al terminar; no se espera, la estimación es de décimas de segundo para 50 000 puntos en Python).
- Misma máquina, portátil enchufado, sin otros procesos pesados; `maquina.json`.
- **Cociente** = tiempo propio / tiempo SciPy por conjunto.
- **Predicción a contrastar en el informe**: SciPy uno o dos órdenes de magnitud más rápido (C frente a Python interpretado, mismo tipo de algoritmo); el tiempo propio crece como n log n o menos en los cuadrados (h ≈ 18, 25, 29 vértices); la red (8 791 puntos, 14 vértices) debería costar menos que el cuadrado de 10 000 por tener menos puntos y menos vértices.
- El script **lo corre el usuario**; la tarea de medición termina entregándole el comando exacto.

## Trazabilidad

| Caso de la spec | Tarea | Prueba |
|---|---|---|
| Copia de la sección R3 | T2 | `tests/test_envolvente_clase.py::test_r3_versionada`; `tests/test_dijkstra_clase.py::test_red_clase_versionada` (claves actualizadas) |
| Tarea pequeña de R2 (unidades) | T3 | `tests/test_tablas_r2.py::test_tabla_ajuste_unidad_por_version`, `::test_tablas_md_incluye_cociente_por_par_y_ajuste` (actualizada) |
| Predicado de giro (Comportamiento 1) | T4 | `tests/test_envolvente.py::test_cruz_signos` |
| 1 cuadrado con extras | T6, T7 | `tests/test_envolvente.py::test_caso_1_cuadrado_con_extras`; `tests/test_envolvente_clase.py::test_casos_a_mano_contra_scipy` |
| 2 desempate | T6, T7, T8 | `tests/test_envolvente.py::test_caso_2_desempate`; `tests/test_envolvente_clase.py::test_caso_2_empate_json` |
| 3 rectángulo con puntos en los lados | T6, T8 | `tests/test_envolvente.py::test_caso_3_rectangulo_lados`; `tests/test_envolvente_clase.py::test_caso_3_rectangulo_json` |
| 4 pentágono | T6, T7 | `tests/test_envolvente.py::test_caso_4_pentagono` |
| 5 duplicados | T5, T6 | `tests/test_envolvente.py::test_caso_5_duplicados`; `tests/test_puntos_r3.py::test_preparar_quita_repetidos` |
| 6 alineados (+ QhullError) | T6, T7 | `tests/test_envolvente.py::test_caso_6_alineados`; `tests/test_envolvente_clase.py::test_scipy_falla_en_degenerados` |
| 7 un punto, vacío, dos puntos (+ QhullError) | T6, T7 | `tests/test_envolvente.py::test_caso_7_bordes_pequenos`; `tests/test_envolvente_clase.py::test_scipy_falla_en_degenerados` |
| 8 coordenadas grandes | T4, T6, T7 | `tests/test_envolvente.py::test_cruz_grande`, `::test_caso_8_coordenadas_grandes` |
| 9 redondeo | T5 | `tests/test_puntos_r3.py::test_caso_9_redondeo`, `::test_preparar_quita_repetidos` |
| 10 red de la clase | T8 | `tests/test_envolvente_clase.py::test_caso_10_red_clase` |
| 11 propiedad vs SciPy | T9 | `tests/test_envolvente_propiedad.py::test_caso_11_aleatorios_vs_scipy` |
| 12 cuadrados vs SciPy y (8/3) ln n | T5, T9 | `tests/test_envolvente_propiedad.py::test_caso_12_cuadrados`; `tests/test_puntos_r3.py::test_puntos_cuadrado_semilla` |
| 13 invariantes | T6–T11 | `comprobar_envolvente` (en `tests/conftest.py`), llamada en todas las pruebas de salida; `tests/test_envolvente.py::test_invariantes_detectan_errores` |
| 14 red real | T11 | `tests/test_red_real_r3.py::test_caso_14_red_real` |
| 15 círculo | T10 | `tests/test_envolvente_propiedad.py::test_caso_15_circulo` |
| 16 parábola | T10 | `tests/test_envolvente_propiedad.py::test_caso_16_parabola`, `tests/test_envolvente.py::test_limite_de_recursion` |
| 17 archivos | T12 | `tests/test_archivos_r3.py::test_caso_17_sintetico`; `tests/test_red_real_r3.py::test_caso_17_archivos_reales` |
| Borde: no modifica la entrada | T6 | `tests/test_envolvente.py::test_no_modifica_entrada` |
| Borde: coordenadas negativas | T6 | `tests/test_envolvente.py::test_coordenadas_negativas` |
| Comprobación previa y medición | T14 | `tests/test_medir_envolvente.py::*` |
| Tablas y gráfica desde los archivos | T13, T15 | `tests/test_tablas_r3.py::*` |
| Resultados medidos | T16 | `tests/test_red_real_r3.py::test_resultados_medidos` |

## Riesgos

- **Recursión**: con `setrecursionlimit(20_000)` en la importación del módulo se cambia un ajuste global del intérprete (se documenta; nunca se baja si ya era mayor). En Python 3.13 las llamadas entre funciones Python no consumen pila de C, así que 20 000 niveles no desbordan.
- **Desempate**: si se cambia la regla (menor lexicográfico) la salida no cambia en vértices, pero sí podría hacer pasar por alto un error de alineados; la mutación de T9 lo vigila.
- **SciPy y alineados**: `ConvexHull` sin la opción `Qc` no reporta puntos alineados como vértices (spec); si alguna prueba aleatoria mostrara lo contrario, se reporta en lugar de ajustar la prueba.
- **SciPy y `float64` (resuelto en la Puerta 2)**: el arreglo se construye en `float64` fuera del cronómetro, así `ConvexHull` no copia dentro de la llamada medida; los enteros < 2⁵³ se representan exactamente. Medido antes de decidir: 2,43 ms (`int64`) frente a 2,42 ms (`float64`) con 50 000 puntos.
- **Prueba lenta**: el caso 12 corre QuickHull en Python con 50 000 puntos (≈ décimas de segundo) y el invariante de contención O(n·h) (≈ 1,5·10⁶ productos); aceptable en `-m "not red"`.
- **Reproducibilidad**: `envolvente.csv/.geojson` dependen del grafo procesado de R1; si R1 se regenera hay que correr de nuevo `rutas.r3.archivos`.
- **Regenerar `tablas_r2.md`**: `rutas.r2.tablas.main` también reescribe `r2_cociente.csv` y la PNG. Ambos se generan de forma determinista desde los mismos CSV (pandas escribe los mismos `float`; matplotlib con Agg no guarda fecha en el PNG), así que se espera que solo cambie `tablas_r2.md`. Se comprueba con `git status --porcelain results/r2`; si otro archivo cambia, el implementer **lo reporta** y no lo arregla (el usuario decide si lo restaura con `git restore`). Es la opción más simple: no agrega un parámetro nuevo a `main`.

## Decisiones

Tomadas en la spec (Puerta 1, 2026-11-10): QuickHull recursivo con `sys.setrecursionlimit(20_000)` documentado; casos del círculo y la parábola; cuadrado de 10⁶ × 10⁶ con semilla 2026; en SciPy solo se mide `ConvexHull(arreglo)`; redondeo `floor(x + 0.5)`; resultados en `results/r3/`; la medición real la corre el usuario; copia de la sección `R3` en `tests/datos/red_clase.json`; tarea pequeña de R2 en el primer bloque; no tocar `.gitignore`.

Tomadas por el plan (menores; se anotan, el usuario puede cambiarlas en la Puerta 2):
1. `area(vertices) -> float`: doble del área entero (exacto) dividido entre 2 al final.
2. Un `random.Random(2026)` nuevo por cuadrado (cada conjunto reproducible por sí solo).
3. Columna `repeticiones` del CSV = mínimo de las repeticiones de propio y SciPy (serán 5 y 5).
4. `envolvente.csv` con `orden` desde 1; GeoJSON como `FeatureCollection` de un `Feature` (lo leen Folium/Leaflet directamente).
5. Nombres de los conjuntos con espacio normal como separador de miles («Cuadrado, 1 000 puntos»), como en la spec.
6. Caso 12: «del mismo orden que (8/3) ln n» se prueba como `0,5·e ≤ h ≤ 2·e` con e = (8/3) ln n.
7. `tablas_r3.md` incluye una tabla corta «Vértices frente a (8/3) ln n» de los cuadrados (sale del CSV; sirve al párrafo «coincide con lo esperado» de la sección 6.8).
8. Tabla del ajuste de R2: columnas `Pendiente` y `Unidad de la pendiente` (una fila por versión con su unidad), sin cambiar `ajuste_tiempo_explorados`.
9. La PNG de la envolvente la genera la función `grafica_envolvente` ya en B3 (solo necesita `data/processed`), y `rutas.r3.tablas` la regenera en B4.

Para confirmar por el usuario:
1. **Tipo del arreglo de SciPy**: resuelto en la Puerta 2 → `float64` construido fuera del cronómetro (spec, punto 5).

## Bloqueos

Ninguno.

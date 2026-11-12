# Plan — R5 Aplicación (Flask + Folium)

Spec: `specs/r5-aplicacion/spec.md` (aprobada en Puerta 1, 2026-11-11, con todas las propuestas de «Decisiones»). Enunciado: sección 5, Requerimiento 5 (párrafo inicial, punto 1 con sus cuatro viñetas y la viñeta «Debe poder ejecutarse localmente siguiendo el README. Publicarla en una URL o en un contenedor Docker es opcional»); sección 7 (entregable «Aplicación: ejecutable localmente siguiendo el README»); sección 8 («En R5 se evalúa que la aplicación muestre los resultados y funcione siguiendo el README»). El Anexo no trae formato para R5. Peso 5 %.

## Resumen

R5 es una aplicación web local, demostrativa, que **no implementa algoritmos nuevos**: carga una sola vez los datos procesados de R1–R3 y llama a las funciones ya verificadas de R2 (Dijkstra con cola de prioridad) y de R4 (Held-Karp, vecino más cercano y la regla de las 11 h). Tiene cuatro secciones:

1. **Ruta** origen–destino entre los 42 lugares, calculada en el momento con `consultar(..., "cola_prioridad")` y dibujada por las vías reales (geometría de `mejor_arista`).
2. **Envolvente** convexa ya calculada en R3 (`envolvente.geojson`), con los 42 lugares encima.
3. **Itinerario** del día: partida (por defecto C01, Armenia) y de 6 a 8 atractivos; Held-Karp y voraz en el momento, tabla comparativa, diferencia y brecha, y la regla de R4 cuando Held-Karp no cabe en 11 h.
4. **Resultados** de R1 a R4: las PNG y los CSV de `results/rX/` como tablas HTML, con un aviso y el comando cuando falta un archivo.

Capas, separadas para que cada una se pruebe sola:
- `datos.py`: carga única y `DatosFaltantes` (E/S, sin Flask).
- `servicios.py`: lógica pura sobre `DatosApp` → dicts sin HTML (sin Flask; se prueba con datos sintéticos y con la red real).
- `formato.py`: números con coma decimal (sin Flask).
- `mapas.py`: HTML de Folium (sin Flask).
- `app.py` + `templates/`: rutas HTTP, validación → HTTP 400, plantillas Jinja. Sin JavaScript propio.

No se mide nada (spec, «Medición»): los `computo_ms` son informativos y no se guardan. No hay protocolo de la sección 6 en R5.

## Estado del repositorio que se reutiliza (sin modificarlo)

Firmas leídas en el código el 2026-11-11:

| Función | Firma real | Uso en R5 |
|---|---|---|
| `rutas.r1.persistencia.cargar_grafo_procesado(carpeta=DATA_PROCESSED)` | `MultiDiGraph` desde `.graphml` o `.graphml.gz`; `FileNotFoundError` si no hay ninguno | `cargar_datos` (antes se comprueba la existencia para dar `DatosFaltantes`) |
| `rutas.r1.persistencia.cargar_lugares_nodos(carpeta)` | `DataFrame` `id_lugar, id_nodo (int64), distancia_al_nodo_m, alerta_500m` | `nodo_de`; **`id_nodo` llega como `numpy.int64`**: se convierte con `int()` (como hace `rutas.r2.matriz.main`) |
| `rutas.r1.aristas.mejor_arista(G, u, v)` | `AristaElegida(u, v, key, length, travel_time, geometry)`; `geometry` es un `LineString` de Shapely en (lon, lat); si la arista no trae geometría, el segmento recto u→v | `coordenadas_de` |
| `rutas.r2.adyacencia.construir_adyacencia(G)` | `Red(ids, indice, adyacencia)` | `DatosApp.red` |
| `rutas.r2.dijkstra.consultar(red, id_origen, id_destino, version="cola_prioridad")` | `(tiempo_s, ruta_ids, explorados)`; `KeyError` si un nodo no está; mismo nodo → `(0.0, [n], 1)` | ruta y tramos |
| `rutas.r2.ruta.detalle_ruta(G, ruta)` | `(tiempo_s, distancia_m)`; un solo nodo → `(0, 0)` (enteros); ruta vacía → `ValueError` | tiempo y distancia de la ruta (`distancia_km = distancia_m / 1000`) |
| `rutas.r2.matriz.cargar_matriz(ruta)` / `calcular_matriz(red, nodos)` / `guardar_matriz(matriz, ids, ruta)` | `DataFrame` ids × ids en s / lista de listas / CSV | `DatosApp.matriz`; las dos últimas solo en el fixture sintético |
| `rutas.r4.por_ids.resolver_por_ids(matriz_df, id_partida, ids_lugares, metodo)` | `(tiempo_s, recorrido_ids)`; `ValueError` si un id no está | Held-Karp (`"held_karp"`) y voraz (`"vecino_mas_cercano"`) |
| `rutas.r4.por_ids.matriz_a_listas(matriz_df)` | `(T, ids)` | entrada de `itinerario_dia` |
| `rutas.r4.itinerario.itinerario_dia(T, ids, s, atractivos, visita_min, jornada_max_min=660)` | **`s` y `atractivos` son índices de `T`; `visita_min` es `{índice: min}`**; valida 6..8 y lanza `ValueError`; devuelve `(filas, quitados, totales)`; cada quitado: `id, jornada_antes_min, jornada_despues_min, ahorro_min, visita_min, desvio_min` (sin `lugar`) | regla de las 11 h |
| `rutas.r4.itinerario.visitas_del_catalogo(catalogo_df, ids)` | `{índice: duracion_visita_min}` de los atractivos | `visita_min` por índice para `itinerario_dia` |
| `rutas.r4.itinerario.JORNADA_MAX_MIN` | `660` | `cabe` |
| `tests/conftest.py` | `grafo_sintetico(nodos, aristas)`; `rutas.r1.utm.agregar_utm_a_nodos`; `rutas.r1.persistencia.guardar_grafo` | fixture sintético de R5 |

Comprobado con los datos reales (lectura, 2026-11-11):
- `consultar` C01→C12 = 1 783,3905017473564 s, **igual bit a bit** a `M.loc["C01", "C12"]`; C12→C01 = 1 708,1902205666652 s; T03→T05 = 0,0 (mismo nodo, ruta de 1 nodo, 1 explorado). `detalle_ruta` da el mismo tiempo; la distancia C01→C12 es 24,00 km.
- Las 11 509 aristas del grafo con `geometry` empiezan exactamente en las coordenadas de `u` y terminan en las de `v`: unir tramos quitando el primer punto de cada tramo después del primero no deja huecos ni duplicados.
- Caso 5: HK 178,6557 min `C01, A15, A13, A07, A06, A14, A05, C01`; voraz 190,4473 min; diferencia 11,7916; brecha 6,6002 %. Cada tramo con `consultar` = `M.loc[desde, hasta]` y la suma = desplazamiento HK. Caso 6: HK 145,2168, voraz 155,3897, diferencia 10,1730, brecha 7,0054 %. Coinciden con la spec.
- El catálogo tiene 15 atractivos (`categoria == "Atractivo turístico"`, A01..A15) con `duracion_visita_min`.
- `data/processed/envolvente.geojson`: un `Feature` con `properties = {"vertices": 14, "area_km2": 1631.4960175}` y un anillo de 15 puntos `[lon, lat]` (el primero repetido al final).
- `.venv` con Python 3.13.18; Flask 3.1.3, Folium 0.20.0 y Jinja2 3.1.6 instalados.

### Archivos de resultados: tabla de la spec frente a `results/` y a los módulos

Todos los nombres de la tabla de la spec existen con ese nombre exacto, salvo los tres que la spec ya da como ausentes (`r1_tiempos_componente.png`, `r4_exactas.csv`, `r4_tiempo_vs_k.png`). **Diferencias en los comandos** (gana el código real; se usa un comando por archivo):

| r | Archivo | Comando real que lo escribe | Diferencia con la spec |
|---|---|---|---|
| r1 | `r1_tamanos.csv`, `r1_memoria.csv`, `r1_velocidades.csv` | `.venv/bin/python -m rutas.r1.construir_red` | La spec decía `rutas.r1.tablas` / `medir_componente`; los escribe `construir_red` (`rutas/r1/construir_red.py:82-89`) |
| r1 | `r1_tiempos_componente.csv` | `.venv/bin/python -m rutas.r1.medir_componente` | — |
| r1 | `r1_tiempos_componente.png` | `.venv/bin/python -m rutas.r1.tablas` | Hoy falta: se mostrará el aviso |
| r2 | `r2_dijkstra.csv`, `r2_pares.csv` | `.venv/bin/python -m rutas.r2.medir_dijkstra` | Precisión: la spec juntaba los dos comandos |
| r2 | `r2_cociente.csv`, `r2_tiempo_vs_explorados.png` | `.venv/bin/python -m rutas.r2.tablas` | Ídem |
| r3 | `r3_envolvente.csv` | `.venv/bin/python -m rutas.r3.medir_envolvente` | Ídem |
| r3 | `r3_envolvente.png` | `.venv/bin/python -m rutas.r3.tablas` | Ídem |
| r4 | `r4_exactas.csv` | `.venv/bin/python -m rutas.r4.medir_exactas` | Hoy falta |
| r4 | `r4_tiempo_vs_k.png` | `.venv/bin/python -m rutas.r4.tablas` (después de `medir_exactas`; sin `r4_exactas.csv` no escribe la PNG) | Hoy falta |
| r4 | `r4_calidad.csv` | `.venv/bin/python -m rutas.r4.calidad` | La spec decía «con sus scripts» |
| r4 | `r4_memoria.csv` | `.venv/bin/python -m rutas.r4.medir_memoria` | Ídem |
| r4 | `r4_itinerario.csv` | `.venv/bin/python -m rutas.r4.itinerario` | Ídem |

Los comandos se escriben con `.venv/bin/python -m …`, como en el README; contienen el texto `python -m rutas.…` que piden los casos 11 y 13. Hay archivos en `results/` que la lista fija no muestra (spec: lista fija): `maquina.json` y `tablas_rX.md` de cada requerimiento, `r2_asimetria.json`, `r2_pares.json`, `r3_puntos.json`, `r4_calidad_detalle.csv`, `r4_instancias.json`, `r4_itinerario.json`. Otra diferencia: el README todavía **no tiene** «Reproducir R4» (es la T23 pendiente de R4); la sección de R5 no depende de ella.

## Módulos y archivos

| Ruta | Acción | Responsabilidad | Tipo |
|---|---|---|---|
| `rutas/config.py` | modificar (agregar al final; no tocar lo demás) | `RESULTS = RAIZ / "results"`, `HOST_R5 = "127.0.0.1"`, `PUERTO_R5 = 5050` | constantes |
| `rutas/r5/__init__.py` | crear | Vacío | — |
| `rutas/r5/formato.py` | crear | `numero(valor, decimales=1)`: coma decimal y espacio de miles | presentación (puro) |
| `rutas/r5/datos.py` | crear | `DatosFaltantes`, `DatosApp`, `COMANDOS_DATOS`, `archivos_faltantes(processed, catalogo)`, `cargar_datos(processed=DATA_PROCESSED, catalogo=CATALOGO)` | carga (E/S, una vez) |
| `rutas/r5/servicios.py` | crear | `ErrorEntrada`, `ARCHIVOS_RESULTADOS`, `validar_lugar`, `coordenadas_de`, `ruta_entre`, `validar_itinerario`, `itinerario`, `resultados` | lógica pura (sin Flask ni HTML) |
| `rutas/r5/mapas.py` | crear | `COLORES`, `centro(datos)`, `mapa_ruta`, `mapa_envolvente`, `mapa_itinerario` → texto HTML de Folium | mapas (sin Flask) |
| `rutas/r5/app.py` | crear | `crear_app(datos, results=RESULTS) -> Flask`, `puerto_libre(host, puerto)`, `main(argv=None, processed=DATA_PROCESSED, catalogo=CATALOGO)` | web |
| `rutas/r5/templates/base.html` | crear | Menú de 4 enlaces, CSS mínimo en línea, `{% block contenido %}` | plantilla |
| `rutas/r5/templates/inicio.html`, `ruta.html`, `envolvente.html`, `itinerario.html`, `resultados.html` | crear | Una por sección | plantillas |
| `Dockerfile` | crear | Imagen opcional `python:3.13-slim` | despliegue |
| `README.md` | modificar | Sección «Ejecutar la aplicación (R5)» al final | doc |
| `tests/conftest.py` | modificar (agregar al final) | `carpeta_app_sintetica(tmp_path, visitas=None)` y fixtures `datos_app`, `cliente_app` | pruebas |
| `tests/test_config.py` | modificar | `test_rutas_r5` | pruebas |
| `tests/test_formato_r5.py`, `test_datos_r5.py`, `test_servicios_r5.py`, `test_mapas_r5.py`, `test_app_r5.py`, `test_dockerfile_r5.py`, `test_red_real_r5.py` | crear | Pruebas (`test_red_real_r5.py` con `pytestmark = pytest.mark.red`) | pruebas |
| `docs/anexo-ia.md` | modificar (local, ignorado) | Entradas de R5 | doc |

No se tocan `rutas/r1..r4/`, `.gitignore`, `pyproject.toml` ni `requirements.txt` (Flask y Folium ya están). No se crea `.dockerignore`: el Dockerfile copia solo lo necesario con `COPY` explícitos (ver «Decisiones», 9).

## Estructuras de datos y firmas

```python
# rutas/config.py (agregado)
RESULTS = RAIZ / "results"      # RESULTS_R1..R4 == RESULTS / "r1".."r4"
HOST_R5 = "127.0.0.1"
PUERTO_R5 = 5050                # 5000 lo ocupa AirPlay en macOS
```

```python
# rutas/r5/formato.py
def numero(valor, decimales=1):
    """Texto con coma decimal y espacio como separador de miles: 1631.496 → "1 631,5",
    29.72 → "29,7", 0 → "0,0". f"{valor:,.{decimales}f}" y luego "," → " " y "." → ","."""
```
Decimales usados en las plantillas (decisión del plan, 2): minutos y segundos 1; km 2; horas 2; % 2; ms 3; km² 1; coordenadas 6. Se registra en Flask como filtro Jinja `num` (`{{ x|num(1) }}`).

```python
# rutas/r5/datos.py
class DatosFaltantes(Exception):
    """El mensaje nombra cada archivo faltante y el comando que lo genera."""

@dataclass(frozen=True)
class DatosApp:
    G: object            # MultiDiGraph de R1 (para detalle_ruta y mejor_arista)
    red: object          # Red de R2 (adyacencia indexada)
    catalogo: object     # DataFrame de data/catalogo.csv (orden del catálogo)
    nodo_de: dict        # {id_lugar: id_nodo int}
    nombre_de: dict      # {id_lugar: nombre}  (agregado por el plan: lo usan plantillas y la regla)
    matriz: object       # DataFrame ids × ids en segundos (R2)
    envolvente: dict     # GeoJSON leído con json
    atractivos: list     # ids con categoria == "Atractivo turístico", en orden del catálogo
    visita_min: dict     # {id_atractivo: minutos (float)}

COMANDOS_DATOS = {       # archivo → comando (tabla «Casos borde» de la spec)
    "grafo_componente.graphml": ".venv/bin/python -m rutas.r1.construir_red",
    "lugares_nodos.csv": ".venv/bin/python -m rutas.r1.construir_red",
    "matriz_tiempos.csv": ".venv/bin/python -m rutas.r2.matriz",
    "envolvente.geojson": ".venv/bin/python -m rutas.r3.archivos",
    "catalogo.csv": "está en el repositorio: restaurarlo con git",
}

def archivos_faltantes(processed, catalogo):
    """[(nombre, comando)] en el orden de COMANDOS_DATOS. El grafo cuenta como presente
    si existe grafo_componente.graphml o grafo_componente.graphml.gz."""

def cargar_datos(processed=DATA_PROCESSED, catalogo=CATALOGO) -> DatosApp:
    """Una sola vez al arrancar. Si archivos_faltantes no está vacía → DatosFaltantes con
    una línea por archivo: "falta <ruta>: <comando>". Si no:
    G = cargar_grafo_procesado(processed); red = construir_adyacencia(G);
    lugares = cargar_lugares_nodos(processed); nodo_de = {id: int(n)};
    catalogo_df = pd.read_csv(catalogo); matriz = cargar_matriz(processed / MATRIZ_TIEMPOS.name);
    envolvente = json.loads((processed / ENVOLVENTE_GEOJSON.name).read_text("utf-8"))."""
```
`pd.read_csv` y no `cargar_catalogo` (igual que R2 y R4) para poder pasarle el catálogo sintético de 8 lugares. `DatosApp` es inmutable (`frozen=True`): ninguna petición la cambia, así no hay estado compartido entre peticiones.

```python
# rutas/r5/servicios.py
class ErrorEntrada(ValueError):
    """Entrada inválida del usuario; la app la convierte en HTTP 400 con el mensaje."""

def validar_lugar(datos, id_lugar):
    """ErrorEntrada("lugar desconocido: X") si X no está en datos.nodo_de."""

def coordenadas_de(G, ids_nodos):
    """[(lat, lon)] siguiendo mejor_arista(G, u, v).geometry en cada tramo; del segundo tramo
    en adelante se omite el primer punto (es el último del tramo anterior). Con menos de 2
    nodos → []. Las coordenadas de Shapely vienen (lon, lat) y se invierten."""

def ruta_entre(datos, id_origen, id_destino):
    """Valida los dos ids; t0 = perf_counter(); tiempo_s, ids_nodos, explorados =
    consultar(datos.red, nodo_de[o], nodo_de[d], "cola_prioridad"); computo_ms = (perf_counter() − t0) × 1000;
    tiempo_s, distancia_m = detalle_ruta(datos.G, ids_nodos)  (el tiempo que se muestra es el de
    detalle_ruta; la prueba exige que coincida con el de consultar ±1e-6).
    Devuelve {"origen", "destino", "tiempo_s", "tiempo_min", "distancia_km", "nodos_explorados",
              "computo_ms", "ids_nodos", "coordenadas", "aviso"}.
    aviso: "origen y destino son el mismo lugar" si o == d; "los dos lugares están en el mismo
    punto de la red" si o ≠ d y nodo_de[o] == nodo_de[d]; None en otro caso."""

def validar_itinerario(datos, id_partida, ids_atractivos):
    """ErrorEntrada, en este orden: "lugar desconocido: X" (partida); "elige entre 6 y 8
    atractivos (llegaron N)"; "atractivo repetido: X"; "la partida X no puede estar entre los
    atractivos"; "X no es un atractivo turístico" (también si X no existe). No calcula nada."""

def itinerario(datos, id_partida, ids_atractivos):
    """validar_itinerario; luego, para m en ("held_karp", "vecino_mas_cercano"):
    t0; tiempo_s, recorrido = resolver_por_ids(datos.matriz, partida, atractivos, m); computo_ms.
    Por método: {"recorrido", "desplazamiento_min" = tiempo_s / 60, "visitas_min" = Σ visita_min,
    "jornada_min", "cabe" = jornada_min <= JORNADA_MAX_MIN, "computo_ms", "tramos"}; cada tramo
    {"desde", "hasta", "tiempo_min", "coordenadas"} con consultar + coordenadas_de.
    Devuelve {"partida", "atractivos", "held_karp", "voraz", "diferencia_min", "brecha_pct", "jornada"}.
    jornada = None si Held-Karp cabe; si no, se llama itinerario_dia con índices (ver abajo)."""

ARCHIVOS_RESULTADOS = {  # r → {"imagenes": [(archivo, comando)], "tablas": [(archivo, comando)]}
    "r1": {"imagenes": [("r1_tiempos_componente.png", ".venv/bin/python -m rutas.r1.tablas")],
           "tablas": [("r1_tamanos.csv", ".venv/bin/python -m rutas.r1.construir_red"),
                      ("r1_tiempos_componente.csv", ".venv/bin/python -m rutas.r1.medir_componente"),
                      ("r1_memoria.csv", ".venv/bin/python -m rutas.r1.construir_red"),
                      ("r1_velocidades.csv", ".venv/bin/python -m rutas.r1.construir_red")]},
    "r2": ...,  "r3": ...,  "r4": ...   # según la tabla de diferencias de arriba
}

def resultados(requerimiento, results=RESULTS):
    """KeyError si requerimiento no está en ARCHIVOS_RESULTADOS. Para cada archivo de la lista
    fija que exista en results/<r>/: imagen → su nombre en "imagenes"; CSV → (nombre, html) con
    pd.read_csv(ruta, keep_default_na=False).to_html(index=False, escape=True, border=0,
    float_format=lambda x: numero(x, 3), classes="tabla"). Cada faltante → (archivo, comando).
    Devuelve {"imagenes": [...], "tablas": [(nombre, html)], "faltantes": [(archivo, comando)]}."""
```

Adaptación a `itinerario_dia` (sin cambiar R4): `T, ids = matriz_a_listas(datos.matriz)`; `s = ids.index(partida)`; `indices = [ids.index(a) for a in atractivos]`; `visita_idx = visitas_del_catalogo(datos.catalogo, ids)`; `filas, quitados, totales = itinerario_dia(T, ids, s, indices, visita_idx)`. Se arma:
```python
jornada = {"cabe_inicial": False,
           "quitados": [{"id": q["id"], "lugar": datos.nombre_de[q["id"]], "visita_min": q["visita_min"],
                         "desvio_min": q["desvio_min"], "ahorro_min": q["ahorro_min"]} for q in quitados],
           "jornada_final_min": totales["jornada_min"],
           "recorrido_final": [partida] + [f["id"] for f in filas if f["orden"] != "Regreso"] + [partida],
           "cabe_final": totales["cabe"]}
```
`cabe_final` se agrega al dict de la spec (si con un solo atractivo todavía no cabe, la pantalla lo dice; con los datos reales no pasa).

`diferencia_min = voraz.desplazamiento_min − held_karp.desplazamiento_min`; si es menor que −1e-9 → `RuntimeError` (no puede pasar: el voraz nunca es mejor que el óptimo; sería un error de datos). `brecha_pct = diferencia_min / held_karp.desplazamiento_min × 100`, y 0 si el desplazamiento de HK es 0 (todos en el mismo nodo: posible en datos sintéticos).

```python
# rutas/r5/mapas.py  — cada función devuelve mapa.get_root().render(): un documento HTML
# completo que la plantilla inserta como <iframe srcdoc="{{ mapa }}"> (Jinja lo escapa solo)
COLORES = {"ruta": "#1f77b4", "held_karp": "#1f77b4", "voraz": "#ff7f0e", "envolvente": "#2ca02c"}

def centro(datos):                       # (lat, lon) promedio de los lugares del catálogo
def mapa_ruta(datos, ruta):              # PolyLine de ruta["coordenadas"] (si hay ≥ 2 puntos),
                                         # marcadores de origen y destino; fit_bounds a la ruta
def mapa_envolvente(datos):              # folium.Polygon con el anillo en (lat, lon) +
                                         # un CircleMarker con tooltip "id · nombre" por lugar
def mapa_itinerario(datos, it):          # FeatureGroup "Held-Karp" y "Vecino más cercano", cada
                                         # uno con la PolyLine de sus tramos en su color;
                                         # marcadores numerados (DivIcon) según el orden de HK, en la latitud/longitud
                                         # del catálogo de cada atractivo;
                                         # marcador de la partida; folium.LayerControl(collapsed=False)
```
`get_root().render()` y no `_repr_html_()`, porque esta última está pensada para Jupyter. El `<iframe srcdoc>` no es JavaScript propio: el JS es el que genera Folium (Leaflet).

```python
# rutas/r5/app.py
def crear_app(datos, results=RESULTS) -> Flask:
    """Fábrica: registra el filtro `num`, guarda datos y results en app.config y define las rutas
    de la spec. ErrorEntrada → render_template(..., error=mensaje), 400."""

def puerto_libre(host, puerto) -> bool:
    """Intenta socket.bind((host, puerto)) y lo cierra; False si da OSError."""

def main(argv=None, processed=DATA_PROCESSED, catalogo=CATALOGO) -> int:
    """argparse: --puerto (int, por defecto PUERTO_R5) y --host (por defecto HOST_R5).
    t0; datos = cargar_datos(processed, catalogo) → si DatosFaltantes: print(mensaje, file=sys.stderr), return 1.
    print(f"Datos cargados en {numero(s, 1)} s ({numero(V, 0)} nodos)").
    Si not puerto_libre: print("el puerto N está ocupado; prueba con --puerto 5051"), return 1.
    print("Abre http://<host>:<puerto>"); crear_app(datos).run(host, puerto, debug=False); return 0."""

if __name__ == "__main__":
    sys.exit(main())
```

Rutas (`app.py`):

| Ruta | Lógica |
|---|---|
| `GET /` | `inicio.html` con los 4 enlaces |
| `GET /ruta` | Si `origen` y `destino` llegan los dos y no vacíos: `ruta_entre` y `mapa_ruta`; `ErrorEntrada` → 400 con el formulario. Si falta alguno: solo el formulario (200) |
| `GET /envolvente` | `mapa_envolvente`; vértices = `properties["vertices"]`, área = `properties["area_km2"]`; tabla de vértices (lat, lon) desde el anillo sin el punto repetido |
| `GET /itinerario` | Si llega `partida`: `request.args.getlist("atractivos")` → `itinerario` y `mapa_itinerario`; `ErrorEntrada` → 400 con el formulario y las casillas marcadas. Si no llega `partida`: formulario con C01 elegido (o el primer lugar si no hay C01) |
| `GET /resultados/<r>` | `r not in ARCHIVOS_RESULTADOS` → `abort(404)`; si no, `resultados(r, results)` |
| `GET /resultados/<r>/archivo/<nombre>` | 404 si `r` no está o `nombre` no está en `ARCHIVOS_RESULTADOS[r]["imagenes"]` o el archivo no existe; si no, `send_from_directory(results / r, nombre, mimetype="image/png")`. El conversor por defecto de Flask no acepta `/` en `<nombre>`, así que `..%2F..%2FCLAUDE.md` ni siquiera llega a la vista; la lista blanca cubre el resto |

Plantillas: `base.html` con `<nav>` (Inicio, Ruta, Envolvente, Itinerario, Resultados r1..r4), `<style>` en línea, `lang="es"`; los formularios usan `method="get"` y `<select>`/`<input type="checkbox">`; ningún `<script>`. Las tablas de pandas y el mapa se insertan con `|safe` (las de pandas ya vienen escapadas) y el mapa con `srcdoc="{{ mapa }}"` (autoescape).

Pantallas (spec, «Salidas en pantalla»):
- **Ruta**: «Tiempo de viaje: 29,7 min (1 783,4 s)», «Distancia: 24,00 km», origen y destino con id y nombre, «Nodos explorados: 7 360», «Cómputo: X,XXX ms», el aviso si lo hay y el mapa.
- **Itinerario**: tabla con columnas «Held-Karp (óptimo)» y «Vecino más cercano (voraz)» y filas: orden de visita (nombres, separados por « → »), desplazamiento (min), visitas (min), jornada (h), cabe en 11 h (Sí/No), cómputo (ms). Debajo: «Diferencia voraz − Held-Karp: 11,8 min (brecha 6,60 %)». Si `jornada` no es `None`: el bloque «Regla de las 11 h (R4, informativo)» con una fila por quitado (lugar, visita, desvío, ahorro en min) y la jornada final; el mapa sigue con los atractivos elegidos.
- **Envolvente**: «14 vértices», «Área: 1 631,5 km²», tabla de vértices y mapa.
- **Resultados**: un `<h2>` por archivo (nombre), las `<img src="/resultados/r2/archivo/…">`, las tablas y una lista «Faltan» con `archivo: comando`.

## Recurrencia y complejidad

No hay algoritmos nuevos; el informe remite a R2 (Dijkstra con cola, O((V + E) log V)) y a R4 (Held-Karp O(k²·2^k) tiempo y O(k·2^k) memoria; voraz O(k²)). Costo de la app:

| Operación | Tiempo | Memoria |
|---|---|---|
| Arranque: `cargar_grafo_procesado` + `construir_adyacencia` + matriz + catálogo | O(V + E) lectura + O(V log V + E) adyacencia, ≈ 1,2 s medido | O(V + E) (grafo y adyacencia), O(n²) matriz con n = 42 |
| `ruta_entre` | O((V + E) log V) Dijkstra (≈ 3 ms) + O(Σ puntos de geometría de la ruta) | O(V) de Dijkstra + O(puntos) |
| `itinerario` (k ≤ 8) | HK ≤ 8²·2⁸ = 16 384 pasos y voraz O(k²), < 1 ms; 2(k + 1) Dijkstra para dibujar ≈ 2·9·3 ms ≈ 54 ms; `matriz_a_listas` O(n²); regla de las 11 h a lo sumo 1 + 8 + 7 + … HK con k ≤ 8 | O(k·2^k) de HK + O(V) por Dijkstra |
| `resultados` | O(tamaño de los CSV) | ídem |
| Mapas de Folium | O(puntos dibujados) | ídem |

Fuentes: las mismas de R2 (Dijkstra con montículo binario) y R4 (Held & Karp, 1962); R5 no agrega ninguna.

## Datos y archivos

R5 no escribe archivos: solo lee.

| Archivo | Formato | Lo lee |
|---|---|---|
| `data/processed/grafo_componente.graphml[.gz]` | GraphML de OSMnx (nodos con `x`, `y` en lon/lat; aristas con `travel_time`, `length`, `geometry` opcional) | `cargar_datos` |
| `data/processed/lugares_nodos.csv` | `id_lugar, id_nodo, distancia_al_nodo_m, alerta_500m` | `cargar_datos` |
| `data/processed/matriz_tiempos.csv` | esquina `id`, ids del catálogo en fila y columna, segundos | `cargar_datos` |
| `data/processed/envolvente.geojson` | `FeatureCollection` con un `Feature`: `properties {vertices, area_km2}`, `Polygon` `[lon, lat]` cerrado | `cargar_datos` |
| `data/catalogo.csv` | `id, nombre, municipio, categoria, latitud, longitud, duracion_visita_min, …` | `cargar_datos` |
| `results/rX/*` | lista fija de `ARCHIVOS_RESULTADOS` | `resultados` y la ruta de imágenes |

**Datos sintéticos de prueba** (`tests/conftest.py::carpeta_app_sintetica(tmp_path, visitas=None)`, escribe todo en `tmp_path` y devuelve `(processed, catalogo, results)`):
- Grafo de 6 nodos cerca de Armenia, con `grafo_sintetico` + `agregar_utm_a_nodos` + `guardar_grafo`: nodos 1 (−75.70, 4.50), 2 (−75.68, 4.50), 3 (−75.66, 4.50), 4 (−75.66, 4.52), 5 (−75.68, 4.52), 6 (−75.70, 4.52); anillo 1→2→3→4→5→6→1 y su inverso, `travel_time` 60 s y `length` 500 m, salvo 2→1 = 90 s (asimetría). La arista 1→2 lleva `geometry = LineString([(-75.70, 4.50), (-75.69, 4.505), (-75.68, 4.50)])` (curva de 3 puntos, caso 15).
- **8 lugares** (ver «Decisiones para el usuario», 1): C01→1, C02→4 (cabeceras), A01→2, A02→3, A03→5, A04→6, A05→4, A06→3 (atractivos; A05 comparte nodo con C02 y A06 con A02, para el aviso del mismo punto). Visitas por defecto 30, 60, 30, 60, 30, 60 min (270 min: cabe); con `visitas=[120] * 6` (720 min) no cabe y se dispara la regla.
- `lugares_nodos.csv` escrito con pandas; `matriz_tiempos.csv` con `calcular_matriz(construir_adyacencia(G), nodos)` + `guardar_matriz` de R2 (así los tramos coinciden con la matriz como en la red real).
- `envolvente.geojson`: cuadrado de 4 vértices `[-75.71, 4.49], [-75.65, 4.49], [-75.65, 4.53], [-75.71, 4.53]` (+ el primero al final), `properties {"vertices": 4, "area_km2": 29.6}`.
- `results/`: `r2/` con `r2_tiempo_vs_explorados.png` (8 bytes de cabecera PNG), `r2_cociente.csv` y `r2_dijkstra.csv`, `r2_pares.csv` pequeños; `r4/` con todo menos `r4_exactas.csv` y `r4_tiempo_vs_k.png`. Las pruebas que piden «los datos actuales del repo» usan `RESULTS` real (versionado), sin la marca `red`.
- Fixtures: `datos_app` (`cargar_datos` sobre la carpeta sintética) y `cliente_app` (`crear_app(datos_app, results).test_client()`).

Sin aleatoriedad: no hay semillas en R5.

## Verificación

| Qué | Contra qué | Datos |
|---|---|---|
| `numero` | valores escritos a mano | 29.72 → «29,7», 1631.496 → «1 631,5», 0 → «0,0», 6.6002 con 2 → «6,60» |
| `cargar_datos` / `DatosFaltantes` | contenido conocido de la carpeta / mensajes de la spec | sintéticos; carpeta vacía (caso 13); cada archivo faltante por separado |
| `coordenadas_de` | los 3 puntos de la geometría curva, en (lat, lon), sin duplicar uniones; segmento recto si no hay geometría | sintéticos (caso 15) |
| `ruta_entre` | matriz de R2 (±1e-6 s), `detalle_ruta`, nodo de C01 (< 1e-6°) | real (casos 1 y 4); sintéticos (caso 3, mismo punto, id desconocido) |
| `validar_itinerario` | mensajes de la spec y un contador de `resolver_por_ids` (monkeypatch) que queda en 0 | sintéticos (caso 8) |
| `itinerario` | resultados de `resolver_por_ids` calculados el 2026-11-11 y `results/r4/r4_itinerario.json`; tramos = matriz | real (casos 5, 6, 7); sintéticos (cabe / no cabe, tramos = matriz) |
| `resultados` | presencia real de archivos | carpeta sintética (caso 11, r4 sin exactas); `results/` real |
| Mapas | texto del HTML de Folium (`leaflet`, `L.polyline`, `L.polygon`, nombres de capas, `L.control.layers`) | sintéticos |
| Rutas HTTP | códigos y textos en `response.get_data(as_text=True)` | cliente de pruebas de Flask, sintéticos y real |
| Carga única | monkeypatch que cuenta llamadas a `cargar_datos` y a `cargar_grafo_procesado` | sintéticos (caso 14) |
| Sin algoritmos ni JS propios | guardia que lee el texto de `rutas/r5/*.py` (no importa `heapq`, `networkx`, `scipy`, `itertools`) y de `templates/*.html` (no contiene `<script`) | código fuente |
| R1–R4 sin cambios | `git diff --stat -- rutas/r1 rutas/r2 rutas/r3 rutas/r4` vacío | repo |
| Arranque con el README y Docker | a mano (casos 16 y 17), escrito en `review.md` | real |

Cada prueba se escribe antes del código y se ve fallar con el `NotImplementedError` de los stubs. Las que prueban código que solo envuelve funciones ya verificadas (red real) se validan con una **mutación temporal** que debe hacerlas fallar y se restaura: p. ej. en `ruta_entre` invertir origen y destino (rompe el caso 1 por la asimetría), en `coordenadas_de` no omitir el punto de unión (rompe el caso 15) y en `itinerario` tomar el recorrido del voraz para los dos métodos (rompe el caso 5).

## Medición

No aplica (spec, «Medición»): R5 no sigue el protocolo de la sección 6 y no guarda tiempos. `computo_ms` = `time.perf_counter()` alrededor de `consultar` y de cada `resolver_por_ids` (incluye la conversión de la matriz a listas dentro de `resolver_por_ids`); se muestra con 3 decimales como dato informativo y se aclara en la pantalla («informativo, no es la medición de R2/R4»). El tiempo de carga que imprime `main` también es informativo.

## Trazabilidad

### Casos de prueba de la spec → tarea → prueba

| Caso | Tarea | Prueba |
|---|---|---|
| 1 Ruta real C01→C12 (1 783,39 s, extremos, `detalle_ruta`, coordenada inicial, explorados) y C12→C01 (1 708,19 s) | T11 | `tests/test_red_real_r5.py::test_caso_1_ruta_real`, `::test_caso_1_asimetria` |
| 2 `GET /ruta?origen=C01&destino=C12` → «29,7» y `leaflet` | T19 | `tests/test_red_real_r5.py::test_caso_2_ruta_en_la_app` |
| 3 Origen = destino (sintéticos y real) | T7, T11, T14, T19 | `tests/test_servicios_r5.py::test_caso_3_mismo_lugar`; `tests/test_app_r5.py::test_caso_3_ruta_mismo_lugar`; `tests/test_red_real_r5.py::test_caso_3_mismo_lugar_real` (T11), `::test_caso_3_ruta_mismo_lugar_real` (T19) |
| 4 Mismo nodo T03/T05 (real) y A02/A06 (sintético) | T7, T11 | `tests/test_servicios_r5.py::test_mismo_punto_sintetico`; `tests/test_red_real_r5.py::test_caso_4_mismo_nodo` |
| 5 Itinerario que cabe (178,66 / 190,45 / 11,79 / 6,60 %) | T9, T11 | `tests/test_servicios_r5.py::test_itinerario_cabe_sintetico`; `tests/test_red_real_r5.py::test_caso_5_itinerario_cabe` |
| 6 Itinerario que no cabe: regla quita A01 y A12, 613,13 min | T9, T11, T19 | `tests/test_servicios_r5.py::test_itinerario_no_cabe_sintetico`; `tests/test_red_real_r5.py::test_caso_6_itinerario_no_cabe`, `::test_itinerario_no_cabe_en_la_app` |
| 7 Tramos = matriz ± 1e-6 s; suma = desplazamiento | T9, T11 | `tests/test_servicios_r5.py::test_tramos_igual_a_matriz_sintetico`; `tests/test_red_real_r5.py::test_caso_7_tramos` |
| 8 Validación del itinerario → 400 sin llamar a Held-Karp | T8, T16 | `tests/test_servicios_r5.py::test_caso_8_validacion` (parametrizada); `tests/test_app_r5.py::test_caso_8_itinerario_400` (parametrizada, contador en 0) |
| 9 `GET /itinerario` real → «178,7», «190,4», «11,8» | T19 | `tests/test_red_real_r5.py::test_caso_9_itinerario_en_la_app` |
| 10 Envolvente: sintética «4 vértices» y sus 4 coordenadas; real «14 vértices» y «1 631,5» | T12, T15, T19 | `tests/test_mapas_r5.py::test_mapa_envolvente`; `tests/test_app_r5.py::test_caso_10_envolvente`; `tests/test_red_real_r5.py::test_caso_10_envolvente_real`, `::test_formulario_42_lugares_15_atractivos` |
| 11 Resultados: r2 con PNG y `r2_cociente.csv`; r4 sin exactas → aviso con `python -m rutas.r4.medir_exactas`; r1..r4 reales → 200 | T10, T17 | `tests/test_servicios_r5.py::test_caso_11_resultados_sinteticos`, `::test_lista_fija_existe_en_results`; `tests/test_app_r5.py::test_caso_11_resultados_r2`, `::test_caso_11_r4_sin_exactas`, `::test_caso_11_cuatro_paginas_reales` |
| 12 Archivos protegidos (200 `image/png`; `..%2F..%2FCLAUDE.md`, `otro.png`, `/resultados/r9` → 404) | T17 | `tests/test_app_r5.py::test_caso_12_imagen_permitida`, `::test_caso_12_rechazos` (parametrizada) |
| 13 Datos faltantes: `DatosFaltantes` con `grafo_componente.graphml` y `python -m rutas.r1.construir_red`; `main` → 1 sin traza | T5, T18 | `tests/test_datos_r5.py::test_caso_13_carpeta_vacia`, `::test_cada_faltante_con_su_comando`; `tests/test_app_r5.py::test_caso_13_main_sin_datos` |
| 14 Carga única | T16 | `tests/test_app_r5.py::test_caso_14_carga_unica` |
| 15 Coordenadas siguen la geometría curva | T6 | `tests/test_servicios_r5.py::test_caso_15_geometria_curva`, `::test_sin_duplicar_uniones`, `::test_segmento_recto_sin_geometria` |
| 16 Arranque siguiendo el README (manual) | T21, T23 | lista manual de T23 → `review.md` |
| 17 Docker (opcional, manual) | T20, T23 | `tests/test_dockerfile_r5.py::test_dockerfile` (estructura) + lista manual de T23 |
| Borde: id desconocido en `/ruta` → 400 «lugar desconocido: X» | T7, T14 | `tests/test_servicios_r5.py::test_lugar_desconocido`; `tests/test_app_r5.py::test_ruta_lugar_desconocido` |
| Borde: parámetros incompletos → solo el formulario | T14, T16 | `tests/test_app_r5.py::test_ruta_incompleta`, `::test_itinerario_sin_parametros` |
| Borde: 8 que no caben → regla; 6 que caben → sin bloque | T9, T16, T19 | `tests/test_app_r5.py::test_itinerario_bloque_regla` (parametrizada); casos 5 y 6 reales |
| Borde: puerto ocupado → mensaje con `--puerto` | T18 | `tests/test_app_r5.py::test_puerto_ocupado` |
| Comportamiento 1: `main` imprime el tiempo de carga y arranca en el host y puerto | T18 | `tests/test_app_r5.py::test_main_arranca` (con `Flask.run` reemplazado) |
| Comportamiento 6 y 7: sin JS propio, sin algoritmos nuevos, menú de 4 enlaces | T2, T13 | `tests/test_app_r5.py::test_sin_algoritmos_ni_js_propio`, `::test_inicio_y_menu` |

### Viñetas del enunciado (R5, sección 7 y sección 8) → tarea

| Punto del enunciado | Tarea |
|---|---|
| R5, párrafo: demostrativa; puede usar la envolvente ya calculada | T5, T12, T15 |
| R5, párrafo: rutas e itinerario calculados en el momento con Dijkstra con cola, Held-Karp y voraz | T7, T9, T11 |
| R5.1 viñeta 1: elegir origen y destino y ver la ruta en un mapa con su tiempo de viaje | T6, T7, T12, T14, T19 |
| R5.1 viñeta 2: envolvente convexa sobre el mapa del departamento | T5, T12, T15, T19 |
| R5.1 viñeta 3: partida (por defecto Armenia) y de 6 a 8 atractivos; recorrido con HK y voraz, tiempo total de cada uno y diferencia | T8, T9, T12, T16, T19 |
| R5.1 viñeta 4: gráficas y tablas de R1 a R4 | T10, T17 |
| R5, viñeta: ejecutable localmente siguiendo el README | T18, T21, T23 (caso 16) |
| R5, viñeta: Docker opcional | T20, T23 (caso 17) |
| Sección 7: entregable «Aplicación: ejecutable localmente siguiendo el README» | T21, T23, T24 |
| Sección 8: «muestre los resultados y funcione siguiendo el README» | T10, T17, T19, T23, T24 |
| Sección 7.1 (pendiente del documento técnico): diagrama de arquitectura y capturas | fuera de las tareas de código; se anota en «Pendientes» del cierre (T24) |
| Anexo de IA | T22 (y cada tarea con IA) |

## Riesgos

- **Leaflet y teselas por internet**: Folium enlaza Leaflet, Bootstrap y las teselas de OpenStreetMap desde CDN; sin internet el navegador muestra la página y las tablas pero el mapa queda en blanco. Las pruebas no dependen de la red (solo buscan texto). Se advierte en el README.
- **`numpy.int64` en `nodo_de`**: funciona como clave (mismo hash que `int`), pero se convierte a `int` para no arrastrar tipos de NumPy a la plantilla ni a `send`/`json`.
- **Coma decimal y separador de miles**: se usa el espacio ASCII (U+0020), como en la spec («1 631,5»). Si el grupo prefiere un espacio fino o no separable (U+202F / U+00A0), cambian el formato y las cadenas de las pruebas.
- **Tamaño del HTML del itinerario**: 2 métodos × hasta 9 tramos con geometría completa (≈ 1 000–3 000 puntos); el documento de Folium crece a unos cientos de kB. Aceptable en local.
- **`brecha_pct` con desplazamiento 0**: solo en datos sintéticos con todos los lugares en un nodo; se define 0 para evitar la división por cero.
- **Docker**: las ruedas de `osmnx`/`geopandas`/`pyproj`/`shapely` para Linux deberían instalarse sin compilar en `python:3.13-slim`; si falta alguna biblioteca del sistema, el caso 17 se anota como no comprobado (no bloquea, spec).
- **Werkzeug y el puerto ocupado**: `app.run` ya sale con un mensaje en inglés y `sys.exit(1)`; por eso `main` comprueba antes con `puerto_libre` para dar el mensaje en español con `--puerto`. Queda una carrera mínima entre la comprobación y el `bind`, sin consecuencia.
- **`r4_exactas.csv` y `r4_tiempo_vs_k.png`**: hasta que el usuario corra la medición de R4, `/resultados/r4` muestra el aviso; es el comportamiento pedido.

## Decisiones

Tomadas en la spec (Puerta 1, 2026-11-11): Flask 3.1.3 + Folium 0.20.0 sin dependencias nuevas; plantillas Jinja en `rutas/r5/templates/`; sin JS propio; puerto 5050; carga única; rutas e itinerario dibujados con Dijkstra con cola y `mejor_arista`; regla de R4 solo informativa; resultados = PNG + CSV con `to_html`; coma decimal; partida = cualquiera de los 42 lugares; datos sintéticos para las pruebas sin `red`; R5 no modifica R1–R4; no tocar `.gitignore`; Dockerfile opcional.

Tomadas por el plan (menores; el usuario las confirma o cambia en la Puerta 2):
1. **Datos sintéticos con 8 lugares** (2 cabeceras y 6 atractivos), no «4 o 5»: con menos de 6 atractivos no se puede probar sin `red` un itinerario válido (casos 8 y 14, bloque de la regla).
2. Módulo extra `rutas/r5/formato.py` con `numero(valor, decimales)` y los decimales de cada magnitud (min y s 1; km 2; h 2; % 2; ms 3; km² 1; coordenadas 6). Separador de miles = espacio ASCII.
3. `DatosApp` agrega `nombre_de` (`{id: nombre}`) a los campos de la spec; es `@dataclass(frozen=True)`.
4. `ruta_entre` agrega las claves `origen`, `destino` y `aviso` (el caso 4 pide que el aviso salga de la función); `itinerario` agrega `partida`, `atractivos` y `jornada["cabe_final"]`.
5. `resultados(requerimiento, results=RESULTS)` y `crear_app(datos, results=RESULTS)`: parámetro opcional para la carpeta de resultados (lo necesita el caso 11 con una carpeta de prueba). Se agrega `RESULTS = RAIZ / "results"` a `config.py`, más `HOST_R5` y `PUERTO_R5`.
6. Un comando **por archivo** en `ARCHIVOS_RESULTADOS` (los reales del código, ver la tabla de diferencias), con el prefijo `.venv/bin/python -m`.
7. `/itinerario` calcula cuando llega `partida` (el formulario siempre la envía); sin casillas marcadas da 400 «elige entre 6 y 8 atractivos (llegaron 0)». Sin `partida`, solo el formulario. `/ruta` calcula solo si llegan `origen` y `destino` no vacíos.
8. Orden de los mensajes de validación del itinerario: partida desconocida → cantidad → repetido → partida entre los atractivos → no es atractivo. Un solo mensaje (el primero que falla).
9. **Dockerfile con `COPY` explícitos** (`requirements.txt`, `rutas/`, `data/catalogo.csv`, `data/processed/`, `results/`), sin `.dockerignore`: así no entran `.venv/`, `data/raw/`, `cache/`, `docs/` ni `estudio/`. `main` acepta `--host` (por defecto `127.0.0.1`) porque el contenedor debe escuchar en `0.0.0.0`; el `CMD` usa `--host 0.0.0.0 --puerto 5050`.
10. Los mapas se devuelven como documento HTML completo (`get_root().render()`) y se insertan con `<iframe srcdoc="…">` escapado por Jinja.
11. Las CSV se leen con `keep_default_na=False` (celdas vacías como en `r4_exactas.csv`) y los `float` se muestran con 3 decimales y coma.
12. Solo se sirven las **imágenes** de la lista fija por `/resultados/<r>/archivo/<nombre>`; las CSV se ven como tablas, no se descargan.
13. `main(argv=None, processed=..., catalogo=...)` devuelve el código de salida (0 o 1) y el bloque `__main__` hace `sys.exit(main())`; así el caso 13 se prueba sin subproceso.
14. Las pruebas de `/resultados` con «los datos actuales del repo» y la de la lista fija contra `results/` van **sin** la marca `red`: `results/` está versionado (como el caso 19d de R4).

## Decisiones para el usuario (Puerta 2)

1. Confirmar la **decisión 1** (8 lugares sintéticos en vez de «4 o 5»): corrige una inconsistencia interna de la spec, no del enunciado.
2. Confirmar la **tabla de comandos por archivo** (decisión 6), que reemplaza los comandos agrupados de la spec (en especial r1: `construir_red` en lugar de `tablas`).
3. Confirmar las decisiones menores 2–5 y 7–14, en especial la 9 (`--host` y `COPY` explícitos en el Dockerfile) y el separador de miles con espacio ASCII (decisión 2).

## Bloqueos

Ninguno. La spec no contradice el enunciado y todo encaja con las firmas reales de R1–R4 mediante adaptadores en `servicios.py` (índices y `visita_min` por índice para `itinerario_dia`; `lugar` de cada quitado desde el catálogo; `distancia_m` → km; `numpy.int64` → `int`). No hace falta cambiar ningún módulo de R1–R4.

## Puerta 2 (2026-11-11), resuelta por el usuario
Se aprueban todas las decisiones de «Decisiones para el usuario (Puerta 2)» tal como están propuestas. La spec se corrigió: datos sintéticos con 8 lugares y un comando por archivo en la lista de resultados.

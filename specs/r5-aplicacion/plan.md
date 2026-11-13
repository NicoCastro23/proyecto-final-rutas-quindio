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

## Ajuste visual (bloque B5, plan del 2026-11-12)

Spec: `spec.md`, sección «Ajuste visual» (V0–V10 y casos A1–A11), aprobada por el usuario el 2026-11-12. Hallazgos por archivo:línea: `auditoria-visual.md`. Dirección visual: skills `.claude/skills/frontend-design/SKILL.md` y `.claude/skills/emil-design-eng/SKILL.md`. Enunciado: sección 8 («En R5 se evalúa que la aplicación muestre los resultados y funcione siguiendo el README»): el diseño no se evalúa; el ajuste sirve para la sustentación y para las capturas del documento técnico (sección 7.1).

R5 ya está implementado y aprobado (T1–T24 y la ronda 1). El ajuste **cambia cómo se ve, no qué se calcula ni qué datos se muestran**. Restricciones (spec):
- sin JavaScript propio: la guardia `test_sin_algoritmos_ni_js_propio` sigue y se amplía con A9 a `estilos.css` y a `javascript:`;
- sin dependencias nuevas: `requirements.txt` no cambia. `markupsafe` (para escapar el `<caption>` de las tablas de pandas) ya viene con Flask; no se agregan fuentes externas ni `@import`;
- no se tocan `rutas/r1..r4/`, `rutas/r5/servicios.py`, `rutas/r5/datos.py`, `rutas/r5/formato.py`, `requirements.txt`, `.gitignore` ni el `Dockerfile` (ya copia `rutas/` completo, así que `rutas/r5/static/` entra en la imagen sin cambios);
- todas las pruebas actuales siguen en verde **sin modificarlas**, incluidos «29,7», «178,7», «190,4», «11,8», «14 vértices» y «1 631,5» (ver «Pruebas actuales que dependen del HTML»).

### Archivos a crear o modificar

| Ruta | Acción | Qué cambia | Puntos |
|---|---|---|---|
| `rutas/r5/static/estilos.css` | crear | Hoja de estilos propia, por secciones comentadas (ver abajo). Flask la sirve en `/static/estilos.css` sin configurar nada: `Flask(__name__)` en `rutas.r5.app` toma `rutas/r5/` como raíz, igual que con `templates/` | V0, V1, A1, A11 |
| `rutas/r5/templates/base.html` | modificar | Quita el `<style>`; agrega `<meta name="viewport">`, `<link>` a la hoja, el enlace «Saltar al contenido», la cabecera con curvas de nivel y el menú (marca + 4 enlaces) con `aria-current="page"` según `seccion`; `<main id="contenido">` | V1, V2, A1–A3 |
| `rutas/r5/templates/inicio.html` | modificar | Cuatro tarjetas (Ruta, Envolvente, Itinerario, Resultados): qué hace y qué algoritmo usa | V10 |
| `rutas/r5/templates/ruta.html` | modificar | `<label for>` + `id` en los dos `<select>`; botón «Calcular ruta»; error con `role="alert"`; tarjetas de resumen; aviso con `role="status"`; `<iframe title="Mapa de la ruta">` | V3, V4, V6, V7 |
| `rutas/r5/templates/envolvente.html` | modificar | Tarjetas (vértices y área); tabla con `<caption>`, `<thead>`, `th scope`; `<iframe title="Mapa de la envolvente">` | V4, V7, V8 |
| `rutas/r5/templates/itinerario.html` | modificar | `<label for="partida">`; casillas en `<fieldset>` + `<legend>` en cuadrícula; botón «Calcular itinerario»; error con `role="alert"`; orden resumen → mapa (con leyenda) → tabla → regla; tabla con `<caption>`, «Medida», `th scope`; `<iframe title="Mapa del itinerario">` | V3–V7 |
| `rutas/r5/templates/resultados.html` | modificar | Navegación R1–R4; título legible y descripción por archivo; `<img>` con `alt`, `width`, `height`, `loading="lazy"`; cada tabla en un contenedor con desplazamiento; faltantes con su título | V8, V9 |
| `rutas/r5/mapas.py` | modificar **solo** `COLORES` | `{"ruta": "#1F5F8B", "held_karp": "#1F5F8B", "voraz": "#B8322A", "envolvente": "#5E8C61"}` (Cocora, Cocora, Cereza, Hoja). El resto del archivo no cambia | V0, V5, A7, A11 |
| `rutas/r5/app.py` | modificar | Cada `render_template` pasa `seccion`; la vista de itinerario pasa `colores=COLORES`; nuevos `TITULOS_RESULTADOS`, `TAMANOS_IMAGENES`, `tabla_con_titulo(html, descripcion, archivo)` y `presentar_resultados(crudo)`; la vista de resultados pasa también `requerimientos` | V2, V5, V8, V9 |
| `tests/test_visual_r5.py` | crear | Pruebas A1–A9, A11 y las de V3, V4, V5, V8, V9, V10 (cliente de Flask con datos sintéticos; sin marca `red`) | — |
| `docs/anexo-ia.md` | modificar (local, ignorado) | Entradas del ajuste visual | — |

No se crean módulos nuevos de Python: el diccionario de títulos va en `app.py` (la spec admite `app.py` o un módulo de presentación; ver «Decisiones», V-4).

### Dirección visual (V0) traducida a tokens

Sale de las dos skills: un tema concreto (herramienta académica sobre la red vial del Quindío, para docente y jurado; su único trabajo es mostrar qué calculó cada algoritmo), una paleta con nombre que evita los dos clichés que señala `frontend-design` (crema + terracota, negro + acento ácido), **un solo** elemento distintivo y el resto sobrio; movimiento mínimo según `emil-design-eng` (escala 0,97 al presionar, 160 ms `ease-out`, nunca `transition: all`, respeto de `prefers-reduced-motion`).

| Variable CSS | Nombre | Valor | Uso |
|---|---|---|---|
| `--guadua` | Guadua | `#2F4A3A` | Cabecera, menú, títulos, enlaces |
| `--hoja` | Hoja | `#5E8C61` | Acento (bordes de tarjetas, líneas de la cabecera), envolvente |
| `--niebla` | Niebla | `#F3F6F4` | Fondo de la página |
| `--bahareque` | Bahareque | `#D5DDD7` | Líneas, bordes, filas alternadas |
| `--tinta` | Tinta | `#1D2521` | Texto |
| `--cocora` | Cocora | `#1F5F8B` | Ruta y Held-Karp; anillo de foco |
| `--cereza` | Cereza | `#B8322A` | Voraz; borde del mensaje de error |

Contraste (comprobación a mano en A10): blanco sobre Guadua ≈ 9,6:1; Tinta sobre Niebla > 14:1; Cocora y Cereza sobre blanco > 4,5:1. **Hoja sobre Niebla no llega a 4,5:1**: Hoja no se usa para texto, solo para bordes y líneas; los enlaces del contenido van en Guadua y subrayados.

Tipografía (sin fuentes externas: la app solo usa internet para los mosaicos del mapa):
- `--fuente-titulos: "Iowan Old Style", "Palatino Linotype", Palatino, Georgia, serif;`
- `--fuente-texto: system-ui, sans-serif;`
- `--fuente-ids: ui-monospace, "SF Mono", Menlo, Consolas, monospace;` (ids de lugar con `class="id"`).
- Escala de 4 tamaños: `--t-pequeno: 0.875rem` (notas, captions), `--t-base: 1rem` (texto), `--t-medio: 1.25rem` (h2, valores de tarjetas), `--t-grande: 1.75rem` (h1, marca).

Elemento distintivo: la franja de cabecera con **curvas de nivel** hechas solo con CSS, que evoca la cordillera:
```css
.cabecera {
  background-color: var(--guadua);
  background-image: repeating-radial-gradient(ellipse at 85% 140%,
      transparent 0 22px, rgb(94 140 97 / 0.35) 22px 24px);   /* Hoja con transparencia */
}
```
Líneas finas y semitransparentes para que el texto blanco del menú mantenga el contraste; el resto de la página no lleva decoración.

Esquema de las páginas con resultado (ancho de escritorio; a 375 px todo queda en una columna):
```
┌ cabecera (curvas de nivel) ─────────────────────────────────────────┐
│ Rutas del Paisaje Cultural Cafetero   Ruta  Envolvente  Itinerario  Resultados │
└─────────────────────────────────────────────────────────────────────┘
 h1 · formulario (labels, cuadrícula de casillas, botón «Calcular …»)
 [mensaje role=alert / role=status]
 ┌tarjeta┐ ┌tarjeta┐ ┌tarjeta┐ ┌tarjeta┐     ← <dl class="resumen">
 leyenda (solo itinerario) + iframe del mapa
 tabla con caption (comparación / vértices)
 regla de las 11 h (solo si Held-Karp no cabe)
```

### Estructura de `estilos.css` (secciones comentadas)

Objetivo: unas 200 líneas, una sección por bloque de la página, cada una con un comentario de una línea que diga para qué sirve. Selectores de clase de un solo nivel (más el elemento cuando hace falta) para no pelear especificidades (advertencia de `frontend-design`).

```
/* 1. Paleta y escala ........ :root con las 7 variables de color, las 3 familias y los 4 tamaños */
/* 2. Base ................... box-sizing, body (Niebla, Tinta, fuente de texto), h1–h2 con la serifa,
                               enlaces en Guadua subrayados, .id en monoespaciada, img { max-width:100%; height:auto } */
/* 3. Foco visible ........... :focus-visible con outline de 3 px en Cocora (Niebla dentro de la cabecera) */
/* 4. Saltar al contenido .... .saltar fuera de pantalla hasta que recibe foco */
/* 5. Cabecera y menú ........ .cabecera con las curvas de nivel; .marca; .menu con flex-wrap (en 375 px se
                               parte en dos líneas); [aria-current="page"] con subrayado grueso */
/* 6. Contenido .............. main con ancho máximo (~70rem) y márgenes */
/* 7. Formularios ............ label encima del select; fieldset sin borde pesado; .casillas en cuadrícula
                               repeat(auto-fill, minmax(17rem, 1fr)); .visita alineada a la derecha; button */
/* 8. Mensajes ............... .error (borde Cereza) y .aviso (borde Hoja), con fondo claro */
/* 9. Tarjetas de resumen .... dl.resumen en cuadrícula; .tarjeta con borde superior; dd con --t-medio y
                               tabular-nums; .metodo-hk / .metodo-voraz cambian el color del borde */
/* 10. Mapas y leyenda ....... iframe.mapa: width 100 %, height clamp(320px, 60vh, 560px); .leyenda y .muestra */
/* 11. Tablas ................ caption, th, td, thead; filas alternadas (Bahareque claro); td numéricos con
                               tabular-nums; .tabla-ancha { overflow-x: auto } */
/* 12. Resultados ............ nav.requerimientos; figure.grafica; .descripcion; .faltantes */
/* 13. Inicio ................ .secciones en cuadrícula de tarjetas */
/* 14. Movimiento ............ button: transition transform 160ms ease-out; :active scale(0.97);
                               @media (hover: hover) and (pointer: fine) { color/background 150ms en a y button };
                               @media (prefers-reduced-motion: reduce) { sin scale, solo los cambios de color } */
/* 15. Pantallas angostas .... @media (max-width: 40rem): márgenes y tamaños menores */
```
Movimiento (secciones 14), escrito para que nunca aparezca `transition: all`:
```css
button { transition: transform 160ms ease-out; }
button:active { transform: scale(0.97); }
@media (hover: hover) and (pointer: fine) {
  a, button { transition: color 150ms ease-out, background-color 150ms ease-out, transform 160ms ease-out; }
  .menu a:hover { color: var(--niebla); }
  button:hover { background-color: var(--guadua); }
}
@media (prefers-reduced-motion: reduce) {
  button, a { transition: color 150ms ease-out, background-color 150ms ease-out; }
  button:active { transform: none; }
}
```
`font-variant-numeric: tabular-nums` va en `dl.resumen dd`, en los `td` de las tablas y en los números de la leyenda.

### Sección activa (`aria-current`) en `base.html`

Cada vista pasa la sección en el contexto: `seccion="inicio" | "ruta" | "envolvente" | "itinerario" | "resultados"`. En `/ruta` y `/itinerario` se agrega la clave `"seccion"` al diccionario `contexto` que ya existe (así también la llevan las respuestas 400); en `/`, `/envolvente` y `/resultados/<r>` se pasa como argumento de `render_template`. No se usa `request.endpoint`: la spec pide que la vista pase el nombre, y así cada integrante ve en la vista qué sección marca.

`base.html` (menú de la marca + 4 enlaces, como pide el Comportamiento 6 de la spec):
```jinja
<a class="saltar" href="#contenido">Saltar al contenido</a>
<header class="cabecera">
  <a class="marca" href="/"{% if seccion == "inicio" %} aria-current="page"{% endif %}>Rutas del Paisaje Cultural Cafetero</a>
  <nav class="menu" aria-label="Secciones">
    {% for clave, enlace, texto in [("ruta", "/ruta", "Ruta"), ("envolvente", "/envolvente", "Envolvente"),
                                    ("itinerario", "/itinerario", "Itinerario"), ("resultados", "/resultados/r1", "Resultados")] %}
    <a href="{{ enlace }}"{% if seccion == clave %} aria-current="page"{% endif %}>{{ texto }}</a>
    {% endfor %}
  </nav>
</header>
<main id="contenido">{% block contenido %}{% endblock %}</main>
```
Los enlaces «R2», «R3», «R4» salen del menú y pasan a la navegación dentro de `/resultados/<r>` (V9). Esa navegación marca el requerimiento actual con `aria-current="true"` (no `"page"`), para que en `/resultados/r2` haya **un solo** `aria-current="page"`, en «Resultados» (A3). Si `seccion` no llega (no debería pasar), ningún enlace queda marcado y la página no falla.

### Títulos y descripciones de los archivos de resultados (V9)

En `app.py`, junto a la importación de `ARCHIVOS_RESULTADOS` (que no cambia). Una entrada por cada uno de los **15 archivos** de la lista fija: `archivo: (título, descripción)`. La descripción es una línea, termina en punto y sirve también como `alt` de las imágenes y como `<caption>` de las tablas. Ningún texto contiene «Faltan» ni «Regla de las 11 h» (ver invariantes).

```python
TITULOS_RESULTADOS = {
    # R1 · red vial
    "r1_tiempos_componente.png": (
        "Tiempo de la componente fuertemente conexa frente a V + E",
        "Gráfica de la mediana de 5 repeticiones, en ms, del cálculo de la componente fuertemente conexa en redes de 2, 5, 10 y 20 km de radio y en el departamento completo."),
    "r1_tamanos.csv": (
        "Tamaño de la red vial",
        "Nodos y aristas de la red descargada y de su componente fuertemente conexa, que es la red que usan R2 a R5."),
    "r1_tiempos_componente.csv": (
        "Tiempo de la componente fuertemente conexa por red",
        "Cinco redes de tamaño creciente: V, E, V + E, mediana en ms, microsegundos por elemento y repeticiones."),
    "r1_memoria.csv": (
        "Memoria: matriz frente a listas de adyacencia",
        "Bytes estimados de cada representación para la red descargada y para la componente, con el supuesto de cada cálculo."),
    "r1_velocidades.csv": (
        "Velocidades por tipo de vía",
        "Velocidad asignada a cada tipo de vía (highway) y porcentaje de tramos con velocidad de OpenStreetMap o imputada."),
    # R2 · Dijkstra
    "r2_tiempo_vs_explorados.png": (
        "Tiempo de Dijkstra frente a nodos explorados",
        "Gráfica de la versión lineal y la versión con cola de prioridad: cada punto es un par origen–destino, con la mediana de sus repeticiones en ms."),
    "r2_dijkstra.csv": (
        "Mediciones de Dijkstra por par",
        "10 pares cercanos y 10 lejanos: tiempo de viaje, nodos explorados y mediana en ms; la versión lineal se mide solo en los cercanos."),
    "r2_cociente.csv": (
        "Cociente lineal / cola de prioridad (10 pares cercanos)",
        "Mediana, mínimo y máximo de cuántas veces más tarda la versión lineal que la de cola de prioridad."),
    "r2_pares.csv": (
        "Pares origen–destino medidos",
        "Los 20 pares de lugares (10 cercanos y 10 lejanos), con su municipio y su nodo en la red."),
    # R3 · envolvente convexa
    "r3_envolvente.png": (
        "Envolvente convexa de los nodos de la red",
        "Gráfica de los nodos de la componente en coordenadas UTM (m) y del polígono que calcula QuickHull."),
    "r3_envolvente.csv": (
        "QuickHull propio frente a SciPy",
        "Nodos de la red y cuadrados de 1 000, 10 000 y 50 000 puntos: vértices, mediana en ms de cada implementación y cociente propio / SciPy."),
    # R4 · ruta óptima
    "r4_tiempo_vs_k.png": (
        "Tiempo de fuerza bruta y Held-Karp frente a k",
        "Gráfica de la mediana en ms para k = 5 a 12 lugares, con el eje y en escala logarítmica."),
    "r4_exactas.csv": (
        "Fuerza bruta y Held-Karp por número de lugares",
        "Para k = 5 a 12: mediana en ms de cada método, estado (completada o no en 5 min), tiempo del recorrido óptimo y el recorrido."),
    "r4_calidad.csv": (
        "Brecha del vecino más cercano frente al óptimo",
        "10 instancias por cada k (5, 8, 10 y 12): brecha promedio y máxima, en %, frente a Held-Karp."),
    "r4_memoria.csv": (
        "Memoria de la tabla de Held-Karp",
        "Para k = 5 a 12: celdas y bytes estimados de la tabla frente al pico medido con tracemalloc."),
    "r4_itinerario.csv": (
        "Itinerario del día desde Armenia",
        "Recorrido que queda después de quitar atractivos hasta caber en 11 h: desplazamiento y visita de cada parada y horas acumuladas."),
}

TAMANOS_IMAGENES = {   # (ancho, alto) en px para width/height de <img>; el CSS escala con height: auto
    "r1_tiempos_componente.png": (1050, 675),   # figsize 7 × 4,5 in a 150 ppp, sin recorte (rutas/r1/tablas.py)
    "r2_tiempo_vs_explorados.png": (1050, 675), # leído del archivo actual (igual a 7 × 4,5 in a 150 ppp)
    "r3_envolvente.png": (914, 1126),           # leído del archivo actual (bbox_inches="tight")
    "r4_tiempo_vs_k.png": (1200, 750),          # aproximado: 8 × 5 in a 150 ppp con bbox_inches="tight"
}
```
Fuentes de cada texto: columnas reales de los CSV de `results/`, los títulos y ejes de las gráficas en `rutas/rX/tablas.py`, la tabla de órdenes del README y las specs de R1–R4 (R1: componente con `largest_component` en 5 redes; R2: 10 pares cercanos con las dos versiones y 10 lejanos solo con cola; R3: QuickHull frente a `scipy.spatial.ConvexHull`; R4: k = 5..12, calidad con k = 5, 8, 10, 12 y 10 instancias, itinerario final del caso 6 tras la regla).

Funciones nuevas de `app.py` (puras, sin E/S, probadas directamente):
```python
def tabla_con_titulo(html, descripcion, archivo):
    """Inserta <caption>descripción <code>archivo</code></caption> justo después de la etiqueta
    <table …> que genera pandas y agrega scope="col" a cada <th> (con index=False todos los <th>
    son encabezados de columna). Escapa la descripción y el archivo con markupsafe.escape.
    Devuelve Markup. No cambia ninguna celda."""

def presentar_resultados(crudo):
    """Recibe lo que devuelve servicios.resultados(r, results) y lo devuelve con los textos:
    {"imagenes": [{"archivo", "titulo", "descripcion", "ancho", "alto"}],
     "tablas": [{"archivo", "titulo", "descripcion", "html"}],        # html = tabla_con_titulo(...)
     "faltantes": [{"archivo", "titulo", "comando"}]}
    KeyError si un archivo no tiene título (lo evita la prueba de cobertura del diccionario)."""
```
La vista queda: `render_template("resultados.html", r=r, seccion="resultados", requerimientos=list(ARCHIVOS_RESULTADOS), **presentar_resultados(resultados(r, results)))`. `servicios.resultados` sigue igual (spec: no se toca `servicios.py`).

`resultados.html`: `<h1>Resultados de R2</h1>`, `<nav class="requerimientos" aria-label="Resultados por requerimiento">` con R1–R4; por imagen un `<figure class="grafica">` con `<h2>` (título), `<p class="descripcion">` con la descripción y `<code>archivo</code>`, y `<img src="…" alt="{{ descripcion }}" width="…" height="…" loading="lazy">`; por tabla un `<section>` con `<h2>` (título) y `<div class="tabla-ancha">{{ tabla.html }}</div>` (el `<caption>` lleva la descripción y el nombre del archivo); al final, solo si hay faltantes, `<section class="faltantes"><h2>Faltan</h2>` con «título (`archivo`): `comando`».

### Cambios por plantilla, con lo que no debe cambiar

- **`ruta.html`**: `<label for="origen">Origen</label> <select id="origen" name="origen">` (ídem destino); `<button type="submit">Calcular ruta</button>`; `<p class="error" role="alert">`. El resultado sigue dentro de `<div id="resultado-ruta">` y su `<h2>` sigue siendo **texto plano en una línea**: `{{ ruta.origen }} {{ nombre_de[ruta.origen] }} → {{ ruta.destino }} {{ nombre_de[ruta.destino] }}` (sin `<span class="id">`, ver «Decisiones», V-3). Debajo, `<dl class="resumen">` con tres tarjetas: «Tiempo de viaje» → `29,7 min` y en `<small>` `(1 783,4 s)`; «Distancia» → `24,00 km`; «Nodos explorados» → `7 360`. El cómputo en ms queda como nota (`<p class="nota">`). Aviso: `<p class="aviso" role="status">`. Mapa: `<iframe class="mapa" title="Mapa de la ruta" srcdoc="{{ mapa }}">`.
- **`envolvente.html`**: `<dl class="resumen">` con «Polígono» → `{{ n_vertices }} vértices` y «Área» → `{{ area_km2|num(1) }} km²` (el número y la unidad en el mismo texto, en una línea); iframe con `title="Mapa de la envolvente"`; tabla con `<caption>Vértices de la envolvente (grados)</caption>`, `<thead>` con `th scope="col"` (Vértice, Latitud, Longitud) y en cada fila el número como `<th scope="row">`.
- **`itinerario.html`**: `<label for="partida">Partida</label> <select id="partida" name="partida">`; `<fieldset><legend>Atractivos (elige de 6 a 8)</legend><div class="casillas">` y por atractivo `<label class="casilla"><input type="checkbox" name="atractivos" value="{{ id }}"{% if id in elegidos %} checked{% endif %}> <span class="id">{{ id }}</span> {{ nombre }} <span class="visita">{{ min }} min</span></label>`; `<button type="submit">Calcular itinerario</button>`; error con `role="alert"`. Con resultado, en este orden:
  1. `<dl class="resumen">`: «Held-Karp (óptimo)» → `178,7 min` (tarjeta `metodo-hk`), «Vecino más cercano (voraz)» → `190,4 min` (`metodo-voraz`), «Diferencia» → `11,8 min`, «Brecha» → `6,60 %`;
  2. `<ul class="leyenda">` con una `<span class="muestra" style="background: {{ colores.held_karp }}">` y otra con `colores.voraz` (los valores salen de `COLORES`, una sola fuente para el mapa y la leyenda), y el iframe con `title="Mapa del itinerario"`;
  3. `<table class="comparacion">` con `<caption>Held-Karp frente al vecino más cercano</caption>`, `<thead><tr><th scope="col">Medida</th><th scope="col" class="metodo-hk">Held-Karp (óptimo)</th><th scope="col" class="metodo-voraz">Vecino más cercano (voraz)</th></tr></thead>` y cada fila con `<th scope="row">` (orden de visita, desplazamiento, visitas, jornada, cabe en 11 h, cómputo);
  4. si `it.jornada`: `<section class="regla">` con el `<h2>Regla de las 11 h (R4, informativo)</h2>`, su texto, la tabla con `<caption>` y la jornada final.
- **`inicio.html`**: `<ul class="secciones">` con cuatro `<li class="tarjeta-seccion">`, cada una con `<h2><a href="…">Sección</a></h2>`, una línea de qué hace y una de qué algoritmo usa:
  - Ruta (`/ruta`): «Elige dos de los 42 lugares y mira el camino más rápido por las vías.» · «Dijkstra con cola de prioridad (R2), calculado en el momento.»
  - Envolvente (`/envolvente`): «Mira el polígono convexo que encierra todos los nodos de la red vial del Quindío.» · «QuickHull, divide y vencerás (R3), ya calculado.»
  - Itinerario (`/itinerario`): «Elige la partida y de 6 a 8 atractivos y compara los dos recorridos del día.» · «Held-Karp (óptimo) y vecino más cercano (voraz) (R4), calculados en el momento.»
  - Resultados (`/resultados/r1`): «Revisa las tablas y gráficas de cada requerimiento, de R1 a R4.» · «Mediciones del protocolo de la sección 6.»

  Corrige un error del texto actual: hoy dice «envolvente convexa de los 42 lugares», pero la envolvente de R3 es la de los **8 791 nodos** de la red (spec de R3, «Propósito»).
- **`resultados.html`**: ver la sección anterior.

### Pruebas actuales que dependen del HTML

Revisadas una por una (`tests/test_app_r5.py`, `tests/test_red_real_r5.py`, `tests/test_mapas_r5.py`). **Ninguna depende del texto «Calcular» ni del orden de la página**, así que no hay que cambiar ninguna. Sí dependen de fragmentos exactos que el HTML nuevo debe conservar (invariantes; cada tarea de B5 corre estas pruebas en su verificación):

| Prueba actual | Fragmento del que depende | Cómo se conserva |
|---|---|---|
| `test_app_r5.py::test_ruta_sintetica_app`, `test_red_real_r5.py::test_caso_2_ruta_en_la_app` | Corta en `id="resultado-ruta"` y busca «C01 Cabecera Uno → A02 Atractivo Dos» / «C01 Plaza de Bolívar de Armenia → C12 Plaza de Bolívar de Salento» como texto seguido | El `<div id="resultado-ruta">` sigue envolviendo el resultado y el `<h2>` queda en texto plano y en una línea (sin `<span>` en los ids) |
| `test_app_r5.py::test_ruta_incompleta` | Sin resultado no aparecen «Tiempo de viaje» ni «desconocido» | La etiqueta «Tiempo de viaje» de la tarjeta está dentro de `{% if ruta %}`; ningún texto de ayuda dice «desconocido» |
| `test_app_r5.py::test_ruta_formulario`, `test_red_real_r5.py::test_formulario_42_lugares_15_atractivos` | `html.count("<option") == 16` / `== 42`; `count('name="atractivos"') == 15` | No se agregan `<option>` ni otros elementos con `name="atractivos"` (la navegación y la leyenda no usan formularios) |
| `test_app_r5.py::test_itinerario_sin_parametros` | 6 `name="atractivos"` y `<option value="C01"[^>]*selected` | Igual que arriba; el `<option>` no cambia |
| `test_app_r5.py::test_caso_8_itinerario_400` | `value="A01" checked` seguidos | En la casilla, `checked` va inmediatamente después de `value="…"`; si se agrega un `id`, va antes de `value` |
| `test_app_r5.py::test_caso_10_envolvente`, `test_red_real_r5.py::test_caso_10_envolvente_real` | «4 vértices», «29,6 km²» / «14 vértices», «1 631,5» y las coordenadas con 6 decimales | La tarjeta muestra `{{ n }} vértices` y `{{ área }} km²` en un mismo texto; la tabla sigue con `num(6)` |
| `test_red_real_r5.py::test_caso_9_itinerario_en_la_app`, `test_app_r5.py::test_itinerario_sintetico_app` | «178,7», «190,4», «11,8»; los nombres del recorrido; «Held-Karp», «Vecino más cercano» | Aparecen en las tarjetas y en la tabla con el mismo `num(1)` |
| `test_app_r5.py::test_itinerario_bloque_regla_no_aparece_si_cabe`, `test_caso_9` (`not in`) | «Regla de las 11 h» **no** aparece si Held-Karp cabe | Ese texto solo está en el `<h2>` del bloque condicional; la leyenda, el formulario y las tarjetas no lo usan |
| `test_app_r5.py::test_caso_11_resultados_r2` | `src="…r2_tiempo_vs_explorados.png"`, «r2_cociente.csv», `<table`, «mediana» | El nombre del archivo sigue visible en `<code>` (en la descripción y en el `<caption>`) |
| `test_app_r5.py::test_caso_11_cuatro_paginas_reales` | «Faltan» **no** aparece en r2 y r3 | «Faltan» solo es el `<h2>` del bloque condicional; ninguna descripción ni la navegación lo contiene |
| `test_app_r5.py::test_caso_11_r4_sin_exactas` | «r4_exactas.csv» y «python -m rutas.r4.medir_exactas» | Los faltantes muestran título, archivo y comando |
| `test_app_r5.py::test_inicio_y_menu` | `href="/ruta"`, `href="/envolvente"`, `href="/itinerario"`, `href="/resultados/r1"` en `/` | Están en el menú y en las tarjetas del inicio |
| `test_mapas_r5.py::test_mapa_itinerario` | `COLORES["held_karp"]` y `COLORES["voraz"]` dentro del HTML de Folium | Folium copia el texto del color tal cual; la prueba lee `COLORES`, así que sigue valiendo con los valores nuevos |
| `test_app_r5.py::test_sin_algoritmos_ni_js_propio` | Ninguna plantilla contiene `<script` | No cambia; A9 agrega una prueba nueva para `estilos.css` y `javascript:` (refuerza, no reemplaza) |

Si durante la implementación alguna de estas pruebas falla, **se corrige la plantilla, no la prueba**. Si el grupo decide de todos modos poner los ids del `<h2>` de la ruta en monoespaciada (decisión V-3), la única prueba que habría que ajustar es la del texto de `#resultado-ruta`, y el ajuste propuesto no la debilita: comparar el texto del bloque sin etiquetas (`re.sub(r"<[^>]+>", "", resultado)`) contra la misma cadena exacta.

### Verificación del ajuste

| Qué | Contra qué | Datos |
|---|---|---|
| Hoja servida y enlazada (A1) | `GET /static/estilos.css` → 200 `text/css`; `base.html` contiene el `<link>` y no `<style` | cliente sintético, texto de la plantilla |
| Paleta y movimiento (A11, V0) | texto de `estilos.css`: las 7 variables con su hex (sin distinguir mayúsculas); no `transition: all` (regex `transition\s*:\s*all`), `@import` ni `url(http`; sí `scale(0.97)`, `160ms ease-out`, `(hover: hover) and (pointer: fine)`, `prefers-reduced-motion`, `repeating-radial-gradient`, `:focus-visible`, `tabular-nums` | archivo |
| `COLORES` (A11, A7) | `COLORES` == Cocora / Cereza / Hoja de `estilos.css`; la leyenda del itinerario contiene los mismos hex | archivo y cliente sintético |
| Base y menú (A2, A3) | `name="viewport"`, «Saltar al contenido», `id="contenido"` en todas las páginas (200 y 400); un solo `aria-current="page"` y en el enlace correcto | cliente sintético |
| Formularios y mensajes (A4, A6, V3) | `<label for>` + `id` coincidentes, `<fieldset>`/`<legend>`, botones; `role="alert"` con el mensaje y `role="status"` con el aviso; sin `role="alert"` si no hay error | cliente sintético |
| Mapas (A5, V7) | cada `<iframe` tiene `title="Mapa de …"` | cliente sintético |
| Tarjetas, orden y tabla del itinerario (V4, V5) | `<dl class="resumen">` con los valores formateados con `numero`; posición de resumen < iframe < tabla < regla en el HTML; «Medida», `<caption>`, `scope`, sin `<th></th>` | cliente sintético (cabe y no cabe) |
| Resultados (A8, V8, V9) | diccionario con los 15 archivos de `ARCHIVOS_RESULTADOS`; `alt` ≠ nombre; `width`/`height` = `TAMANOS_IMAGENES` (y = tamaño real de las PNG de r2 y r3); `loading="lazy"`; cada `<table` con `<caption>` dentro de `.tabla-ancha`; navegación R1–R4 | cliente sintético y `results/` real (sin `red`) |
| Sin JS, sin dependencias, sin tocar lo prohibido (A9) | prueba de texto + `git diff --stat` vacío de `rutas/r1..r4`, `servicios.py`, `datos.py`, `formato.py`, `requirements.txt`, `.gitignore`, `Dockerfile` | repo |
| Aspecto real (A10) | revisión manual en el navegador a ancho de escritorio y a ~375 px | `review.md` |

Cada prueba nueva se escribe antes del cambio y se ve fallar contra el HTML actual (el rojo es «por la razón correcta»: falta el atributo, el texto o el archivo). No hay algoritmo ni medición nuevos.

### Trazabilidad del ajuste: V0–V10 y A1–A11 → tarea → prueba

Todas las pruebas son de `tests/test_visual_r5.py` salvo que se diga otra cosa.

| Punto / caso | Tarea | Prueba |
|---|---|---|
| V0 dirección visual: paleta | T26 | `::test_a11_paleta_en_css`, `::test_a11_colores_de_mapas` |
| V0 tipografía, firma (curvas de nivel) y movimiento | T27 | `::test_v0_tipos_firma_y_movimiento`; A10 (T35) para el aspecto |
| V0 textos (voz activa, errores con el paso siguiente) | T28, T33 | `::test_a4_labels_y_botones` (botones «Calcular ruta» / «Calcular itinerario»), `::test_v10_inicio_tarjetas`; los mensajes de error no cambian (vienen de `servicios.py`) |
| V1 hoja propia, sin CSS en línea | T26, T27 | `::test_a1_estilos_servidos`, `::test_a1_base_sin_style` |
| V2 viewport, saltar al contenido, `aria-current`, foco, menú en 375 px | T27, T35 | `::test_a2_viewport_y_saltar`, `::test_a3_aria_current`, `::test_v0_tipos_firma_y_movimiento` (`:focus-visible`); 375 px en A10 |
| V3 formularios | T28 | `::test_a4_labels_y_botones`, `::test_v3_fieldset_y_cuadricula` |
| V4 tarjetas de resumen | T29, T30, T31 | `::test_v4_tarjetas_ruta`, `::test_v4_tarjetas_envolvente`, `::test_v4_tarjetas_itinerario` |
| V5 colores, leyenda, tabla y orden del itinerario | T26, T31 | `::test_a7_leyenda_con_colores`, `::test_v5_tabla_comparacion`, `::test_v5_orden_de_la_pagina` |
| V6 mensajes con `role` | T28 | `::test_a6_alert_y_status` |
| V7 iframes con `title` y altura adaptable | T29, T30, T31, T35 | `::test_a5_iframes_con_title` (parametrizada por página); la altura, en A10 |
| V8 tablas | T30, T32 | `::test_v8_tabla_envolvente`, `::test_tabla_con_titulo`, `::test_v8_tablas_de_resultados` |
| V9 resultados: títulos, imágenes, navegación | T32 | `::test_titulos_cubren_la_lista_fija`, `::test_tamanos_de_imagenes`, `::test_a8_imagen_y_titulo`, `::test_v9_navegacion_requerimientos`, `::test_faltantes_con_titulo` |
| V10 inicio con cuatro tarjetas | T33 | `::test_v10_inicio_tarjetas` |
| A1 | T27 | `::test_a1_estilos_servidos`, `::test_a1_base_sin_style` |
| A2 | T27 | `::test_a2_viewport_y_saltar` (parametrizada: `/`, `/ruta`, `/ruta` con resultado, `/ruta` 400, `/envolvente`, `/itinerario`, `/itinerario` con resultado, `/itinerario` 400, `/resultados/r1..r4`) |
| A3 | T27, T32 | `::test_a3_aria_current` (parametrizada: `/ruta`, `/envolvente`, `/itinerario`, `/resultados/r2`) |
| A4 | T28 | `::test_a4_labels_y_botones` |
| A5 | T29, T30, T31 | `::test_a5_iframes_con_title` |
| A6 | T28 | `::test_a6_alert_y_status` |
| A7 | T31 | `::test_a7_leyenda_con_colores` |
| A8 | T32 | `::test_a8_imagen_y_titulo` |
| A9 | T25 (rojo), T26 (verde) | `::test_a9_sin_js_propio`; se mantiene `tests/test_app_r5.py::test_sin_algoritmos_ni_js_propio` |
| A10 | T35 | revisión manual → `review.md` |
| A11 | T26 | `::test_a11_paleta_en_css`, `::test_a11_sin_transition_all_ni_externos`, `::test_a11_colores_de_mapas` |
| Restricciones: pruebas actuales («29,7», «178,7», «190,4», «11,8», «14 vértices», «1 631,5») | T25–T34 | `tests/test_app_r5.py`, `tests/test_red_real_r5.py`, `tests/test_mapas_r5.py` sin cambios, en la verificación de cada tarea y en T34 |
| Restricciones: sin dependencias; `servicios.py` y R1–R4 sin tocar | T25, T34 | `git diff --stat` vacío (T34) |

### Riesgos del ajuste

- **Una plantilla nueva rompe un fragmento del que depende una prueba actual** (tabla de invariantes). Mitigación: cada tarea corre `tests/test_app_r5.py` y, cuando toca ruta, envolvente o itinerario, las pruebas `red` correspondientes.
- **Contraste sobre la franja de curvas de nivel**: si las líneas son muy claras, el texto blanco del menú pierde contraste. Líneas de 2 px con Hoja al 35 % sobre Guadua; se comprueba a ojo y con las herramientas del navegador en A10.
- **`width`/`height` de `r4_tiempo_vs_k.png` es aproximado** (la figura se guarda con `bbox_inches="tight"` y aún no existe). Con `height: auto` el navegador usa la proporción real al cargar, así que solo afecta la reserva de espacio antes de la carga. Cuando exista la PNG, se corrige el valor (anotado en T32).
- **Leyenda con `style` en línea**: es un atributo de estilo, no JavaScript ni una etiqueta `<style>`; pasa A1 (busca `<style`) y A9. Se usa para que la leyenda lea el color de `COLORES` y no haya dos fuentes.
- **El mapa sigue dependiendo de internet** (Leaflet y mosaicos); la hoja propia no, porque no usa fuentes ni recursos externos (A11).
- **La spec dice en V1 «con la paleta café del menú actual»**, pero V0 (más reciente y detallado) define la paleta Guadua/Hoja/…, que reemplaza al café `#3b2a1a`. El plan sigue V0 (decisión V-7).

### Decisiones del ajuste para el usuario

- **V-1. Menú con la marca y 4 enlaces** (Ruta, Envolvente, Itinerario, Resultados → `/resultados/r1`), en lugar de los 8 actuales; R1–R4 pasan a la navegación de la página de resultados. Cumple «menú de 4 enlaces» (Comportamiento 6), cabe en 375 px y es lo que pide V10 («el enlace de Resultados lleva a la navegación de R1 a R4»). La marca lleva `aria-current="page"` en `/`.
- **V-2. `aria-current="true"`** en la navegación R1–R4 de resultados, para que en `/resultados/r2` haya un único `aria-current="page"` (A3, «en ningún otro enlace»).
- **V-3. Ids en monoespaciada en todas partes salvo en el `<h2>` de la ruta**, que queda en texto plano para no tocar la prueba actual de `#resultado-ruta`. Alternativa: ponerlo también en monoespaciada y ajustar esa prueba comparando el texto sin etiquetas (misma cadena; no la debilita).
- **V-4. `TITULOS_RESULTADOS` y `TAMANOS_IMAGENES` en `app.py`**, no en un módulo nuevo (la spec admite los dos). Los textos de los 15 archivos están arriba; el grupo puede corregir la redacción sin cambiar las pruebas (las pruebas exigen cobertura, no un texto exacto, salvo el de `r2_cociente.csv`, que fija la spec).
- **V-5. `<caption>` de las tablas de pandas insertado en `app.py`** (`tabla_con_titulo`, manipulación de texto sobre el HTML de `to_html`), para no tocar `servicios.py`. El `<caption>` lleva la descripción y el nombre del archivo; el `<h2>`, el título legible.
- **V-6. Tamaño de las imágenes fijo en un diccionario** (no se lee la cabecera PNG en cada petición; la PNG sintética de las pruebas solo tiene 8 bytes). r4 queda aproximado hasta que exista.
- **V-7. Paleta de V0** en lugar de «la paleta café del menú actual» que menciona V1.
- **V-8. Solo cambian los 4 valores de `COLORES`**; los grises fijos de `mapas.py` (marcadores de la envolvente `#444` y borde de los números `#333`) y el marcador verde de la partida no cambian, porque la spec solo nombra `COLORES`. Si el grupo quiere, se pasan a Tinta en una tarea aparte.
- **V-9. La cuadrícula de casillas usa `repeat(auto-fill, minmax(17rem, 1fr))`**: 2 o 3 columnas en escritorio (lo que pide V3) y 1 columna a 375 px.
- **V-10. Corrección de texto en el inicio**: la envolvente es la de los nodos de la red, no «de los 42 lugares» como dice hoy `inicio.html`.
- **V-11. B5 es un solo bloque** (T25–T35) que termina con la suite en verde y se detiene para el commit del usuario; la revisión manual (T35) va al final y, si obliga a cambiar CSS, se vuelve a correr el comando de T34.

### Bloqueos del ajuste

Ninguno. El ajuste no contradice el enunciado (el diseño no se evalúa en R5 y no se cambia ningún resultado) y cabe en los archivos permitidos por la spec sin tocar `servicios.py` ni R1–R4. La única inconsistencia interna de la spec (V1 «paleta café» frente a V0) se resuelve a favor de V0 y queda en V-7 para confirmar.

### Puerta 2 del ajuste visual (2026-11-12), resuelta por el usuario
Se aprueban las decisiones V-1 a V-11 tal como están propuestas: menú de 4 enlaces, ids en monoespaciada salvo el `<h2>` de la ruta, títulos y tamaños de imagen en `app.py`, tamaño provisional de `r4_tiempo_vs_k.png`, solo cambian los 4 valores de `COLORES`, cuadrícula de 2–3 columnas o 1 en móvil, corrección del texto de la envolvente en el inicio y leyenda con `style` en línea. La spec se corrigió en V1 («paleta de V0»).

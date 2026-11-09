# Aplicación — Requerimiento 5
Enunciado: sección 5, Requerimiento 5. Peso: 5 %.
Estado: ☐ spec (borrador, pendiente de aprobación del grupo) · ☐ pruebas · ☐ código · ☐ verificado
Depende de: R1 (grafo y catálogo), R2 (Dijkstra con cola), R3 (envolvente ya calculada), R4 (Held-Karp y voraz). Se implementa al final.

## Propósito
Aplicación demostrativa (web o de escritorio) que muestra los resultados del proyecto. Se evalúa que muestre los resultados y que funcione siguiendo el README, no su diseño visual.

## Entradas y salidas
**Entradas:** grafo procesado y catálogo (R1), matriz de tiempos (R2), envolvente (R3), CSV/JSON/PNG de resultados (R1 a R4). Selecciones del usuario en la interfaz.

**Salidas en pantalla:** mapas (ruta, envolvente, itinerario), tiempos, tablas y gráficas.

## Comportamiento
La aplicación permite:
1. **Ruta origen–destino:** elegir dos lugares del catálogo y ver en un mapa la ruta calculada **en el momento** con Dijkstra con cola de prioridad (R2), junto con su tiempo de viaje (min). Origen = destino → mensaje "origen y destino iguales" con tiempo 0.
2. **Envolvente convexa:** mostrar el polígono precalculado (R3) sobre el mapa del departamento.
3. **Itinerario del día:** elegir lugar de partida (por defecto Armenia) y entre 6 y 8 atractivos; calcular en el momento con **Held-Karp** y con la **heurística voraz**; mostrar ambos recorridos en el mapa con el tiempo total de cada uno y la diferencia entre ellos. Fuera del rango 6 a 8 → mensaje de validación, sin calcular. Indicar si cabe en 11 h.
4. **Resultados:** ver tablas y gráficas de R1 a R4 (pueden ser las imágenes del documento técnico).
5. **Ejecución local:** se arranca con los comandos del README, sin descargar la red (usa los datos procesados). Docker o URL pública son opcionales.

## Casos borde
- Origen o destino sin ruta → mensaje claro (no debería ocurrir dentro de la componente).
- Atractivo repetido o partida incluida en la selección → se rechaza.
- Datos procesados ausentes → mensaje que indica qué script de R1 a R4 correr.
- Selección de 6 atractivos con Held-Karp: responde en tiempo interactivo (k = 6 trivial; con 8 sigue siendo inmediato).
- El README funciona en una máquina limpia (entorno nuevo).

## Casos de prueba
1. Armenia → Salento: devuelve la ruta y el tiempo igual al de `M[Armenia][Salento]` de la matriz de R2 (diferencia < 1 s) y la ruta empieza y termina en los nodos de esos lugares.
2. Origen = destino → tiempo 0 y mensaje.
3. Itinerario con 6 atractivos desde Armenia: el tiempo de Held-Karp ≤ el de la heurística; la diferencia mostrada = heurística − Held-Karp.
4. Itinerario con 5 o 9 atractivos → error de validación.
5. La envolvente mostrada tiene los mismos vértices que `data/processed/envolvente.csv`.
6. Todas las tablas y gráficas de R1 a R4 listadas en el índice de resultados se abren sin error.
7. Arranque en entorno limpio siguiendo solo el README → la aplicación abre y responde a la consulta del caso 1.

## Complejidad esperada
Sin análisis propio: reutiliza R2 (consulta Dijkstra) y R4 (Held-Karp con k ≤ 8: O(k² 2^k) ≈ 16 384 operaciones). La documentación solo remite a esas secciones.

## Verificación
- Casos 1 y 3 contra los resultados de R2 y R4 (misma función, mismos datos).
- Revisión manual del arranque desde cero con el README.

## Medición
No se mide en R5. Opcional: tiempo de respuesta percibido de la ruta y del itinerario, sin entrar al protocolo de la sección 6.

## Decisiones
El lenguaje es **Python**, así que la aplicación también (web con Flask/FastAPI + Folium/Leaflet, o escritorio).

Abiertas:
- Web o escritorio, y la librería concreta.
- Comando de ejecución y capturas para el README.
- Si se publica en URL o contenedor Docker (opcional).

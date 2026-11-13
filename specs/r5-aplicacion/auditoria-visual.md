# Auditoría visual de R5 (2026-11-12)

Hecha por el coordinador con las guías de la skill `web-design-guidelines` (Vercel, `web-interface-guidelines/command.md`, descargadas el 2026-11-12). Se revisaron `rutas/r5/templates/*.html` y `rutas/r5/mapas.py`. Se omiten las reglas propias de React/JS (hidratación, `onKeyDown`, virtualización), porque la app no tiene JavaScript propio.

## rutas/r5/templates/base.html

- base.html:3: falta `<meta name="viewport" content="width=device-width, initial-scale=1">`, así que en el celular se ve a escala de escritorio.
- base.html:6-17: CSS en línea mínimo: sin estados `:hover` ni `:focus-visible` en enlaces y botones, y sin `font-variant-numeric: tabular-nums` en las columnas de números.
- base.html:20-29: el menú no marca la página actual (`aria-current="page"`) y no hay enlace «Saltar al contenido».
- base.html:12: `th` sin `scope`, y las tablas no tienen contenedor con desplazamiento horizontal (las de pandas son anchas).

## rutas/r5/templates/inicio.html

- inicio.html:4-9: lista simple. Podrían ser tarjetas con una línea por sección. «Resultados» solo enlaza a R1.

## rutas/r5/templates/ruta.html

- ruta.html:5,9: los `<select>` no tienen `<label>` asociado: «Origen» y «Destino» son texto suelto.
- ruta.html:13: botón genérico «Calcular» → «Calcular ruta».
- ruta.html:16: el error no tiene `role="alert"`.
- ruta.html:21-24: los números clave (tiempo, distancia, explorados) van en párrafos. Mejor como resumen destacado y con `tabular-nums`.
- ruta.html:25: el aviso no tiene `role="status"`.
- ruta.html:26: `<iframe>` sin `title`.

## rutas/r5/templates/envolvente.html

- envolvente.html:5: `<iframe>` sin `title`.
- envolvente.html:6-11: tabla sin `<caption>` ni `<thead>`, `th` sin `scope`, y latitud y longitud sin `tabular-nums`.

## rutas/r5/templates/itinerario.html

- itinerario.html:5: el `<select>` de partida no tiene `<label>`.
- itinerario.html:9-12: las casillas van con `<p>` + `<br>`. Deberían ser `<fieldset>` + `<legend>` en una cuadrícula.
- itinerario.html:13: botón genérico «Calcular» → «Calcular itinerario».
- itinerario.html:16: el error no tiene `role="alert"`.
- itinerario.html:22: celda de esquina `<th></th>` vacía, sin `<caption>` y con `th` sin `scope`. Los colores de Held-Karp y del voraz en el mapa no se relacionan con la tabla: falta una leyenda.
- itinerario.html:32: el resultado principal (diferencia y brecha) queda en una línea suelta debajo de la tabla.
- itinerario.html:47: `<iframe>` sin `title`. El mapa queda al final, después de las tablas.

## rutas/r5/templates/resultados.html

- resultados.html:5,9: los títulos son nombres de archivo (`r2_cociente.csv`) en vez de títulos legibles.
- resultados.html:6: `<img>` sin `width`/`height` ni `loading="lazy"`, y su `alt` es el nombre del archivo, que no describe la gráfica.
- resultados.html:10: las tablas de pandas no tienen `<caption>` ni contenedor con desplazamiento.
- resultados.html:13: «Faltan» ✓ trae el comando para resolverlo (cumple «el error incluye el siguiente paso»).

## rutas/r5/mapas.py

- mapas.py:39,72: el color de la ruta y el de cada método no tienen leyenda en la página. El control de capas solo muestra el nombre.
- ✓ tooltips con id y nombre, y marcadores numerados por orden de visita.

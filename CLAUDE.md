# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Proyecto
Proyecto final de Análisis de Algoritmos (Universidad del Quindío): "Rutas del Paisaje Cultural Cafetero". Enunciado y rúbrica: `/Users/nicolascastro/Desktop/Documentos-Analisis de algoritmos/Proyecto final 2026-2.pdf` y `Anexo proyecto.pdf`. Agentes en `.claude/agents/` (`coordinator`, `planner`, `implementer`, `reviewer`); arranca con `claude --agent coordinator`.

## Metodología: Spec-Driven Development (SDD)
Decidido por el grupo (el enunciado lo promueve): **ninguna función de un requerimiento se programa antes de tener su spec**.
1. Escribe la spec en `specs/<id>-<slug>/spec.md` (una carpeta por requerimiento o algoritmo, plantilla en `specs/README.md`): comportamiento esperado, entradas/salidas, casos borde y casos de prueba concretos.
2. Escribe las pruebas a partir de la spec; luego el código hasta que pasen.
3. La spec es el contexto que se le da a la IA y contra la que se verifica su salida. Si el código y la spec difieren, se corrige uno de los dos de forma explícita y se hace commit del cambio.
4. Cada spec enlaza la sección del enunciado que cubre. La verificación pedida por el protocolo (sección 6) sale de sus casos de prueba.

## Reglas del proyecto
- Lenguaje: **Python** (todos los algoritmos, la descarga con OSMnx y la aplicación). Fijar versiones en `requirements.txt` (NetworkX, OSMnx, SciPy). Todos los algoritmos en un solo lenguaje; implementación propia donde el enunciado lo exige (NetworkX/SciPy/Shapely solo para verificar).
- Todo uso de IA se anota en `docs/anexo-ia.md` para el anexo de IA (herramienta, para qué, cómo se verificó). Cada integrante debe poder explicar y modificar cualquier parte del código.
- Commits pequeños y frecuentes de cada integrante.

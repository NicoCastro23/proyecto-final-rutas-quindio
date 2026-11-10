"""Componente fuertemente conexa más grande.

En R1 el enunciado pide usar la función de OSMnx (no una implementación propia):
internamente comprueba si el grafo ya es fuertemente conexo y, si no, toma la mayor
de las componentes que calcula NetworkX (Tarjan iterativo) y copia ese subgrafo.
Eso es lo que se mide en medir_componente.py.
"""
import osmnx as ox


def obtener_componente(G):
    """Devuelve el MultiDiGraph de la mayor componente fuertemente conexa."""
    return ox.truncate.largest_component(G, strongly=True)


def contar(G):
    """(V, E) con E = aristas del MultiDiGraph, paralelas incluidas."""
    return G.number_of_nodes(), G.number_of_edges()

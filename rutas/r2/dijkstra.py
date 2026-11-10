"""Dijkstra propio, en dos versiones, sobre la representación indexada (rutas.r2.adyacencia).

Los algoritmos trabajan con índices 0..V-1 (listas de tamaño V). La traducción ids <-> índices
vive solo en `consultar`. Las dos versiones tienen la misma inicialización y la misma relajación;
lo único que cambia es cómo se busca el siguiente nodo a extraer.
"""
import heapq
import math


def reconstruir_ruta(pred, origen, destino):
    """Sigue los predecesores desde el destino hasta el origen y devuelve la ruta origen -> destino.

    Devuelve [] si el destino no tiene predecesor (y no es el origen): no hay camino.
    """
    if destino != origen and pred[destino] is None:
        return []
    ruta = [destino]
    while ruta[-1] != origen:
        ruta.append(pred[ruta[-1]])
    ruta.reverse()
    return ruta


def dijkstra_lineal(adyacencia, origen, destino=None):
    """Dijkstra buscando el mínimo recorriendo todos los nodos: O(V^2)."""
    V = len(adyacencia)
    dist = [math.inf] * V
    pred = [None] * V
    visitado = [False] * V
    dist[origen] = 0.0
    explorados = 0
    while True:
        # Búsqueda lineal del no visitado de menor distancia. Se cambia de candidato solo si es
        # estrictamente menor: en un empate gana el menor índice (= menor id).
        u = None
        mejor = math.inf
        for i in range(V):
            if not visitado[i] and dist[i] < mejor:
                u = i
                mejor = dist[i]
        if u is None:  # no queda ningún nodo alcanzable sin extraer
            break
        visitado[u] = True
        explorados += 1
        if u == destino:  # parar al sacar el destino: su distancia ya es final
            break
        for v, w in adyacencia[u]:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                pred[v] = u
    return _resultado(dist, pred, explorados, origen, destino)


def dijkstra_cola(adyacencia, origen, destino=None, estadisticas=None):
    """Dijkstra con montículo binario (heapq): O((V + E) log V).

    heapq no permite bajar la prioridad de una entrada: cuando un nodo mejora se inserta otra
    entrada y la vieja queda obsoleta; al sacarla (el nodo ya está visitado) se descarta sin
    contarla. Las entradas son (distancia, índice), así que el empate lo gana el menor índice.
    Si `estadisticas` es un dict, se llena con "extracciones" y "obsoletas" (solo para pruebas).
    """
    V = len(adyacencia)
    dist = [math.inf] * V
    pred = [None] * V
    visitado = [False] * V
    dist[origen] = 0.0
    explorados = 0
    extracciones = 0
    obsoletas = 0
    cola = [(0.0, origen)]
    while cola:
        _, u = heapq.heappop(cola)
        extracciones += 1
        if visitado[u]:  # entrada obsoleta: u ya salió con una distancia menor o igual
            obsoletas += 1
            continue
        visitado[u] = True
        explorados += 1
        if u == destino:  # parar al sacar el destino: su distancia ya es final
            break
        for v, w in adyacencia[u]:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                pred[v] = u
                heapq.heappush(cola, (dist[v], v))
    if estadisticas is not None:
        estadisticas["extracciones"] = extracciones
        estadisticas["obsoletas"] = obsoletas
    return _resultado(dist, pred, explorados, origen, destino)


def _resultado(dist, pred, explorados, origen, destino):
    """Sin destino: (dist, pred, explorados). Con destino: (tiempo, ruta, explorados)."""
    if destino is None:
        return dist, pred, explorados
    if dist[destino] == math.inf:
        return math.inf, [], explorados
    return dist[destino], reconstruir_ruta(pred, origen, destino), explorados


VERSIONES = {"lineal": dijkstra_lineal, "cola_prioridad": dijkstra_cola}


def consultar(red, id_origen, id_destino, version="cola_prioridad"):
    """Envoltorio con ids: (tiempo_s, ruta en ids, nodos_explorados). Fuera de la medición."""
    if version not in VERSIONES:
        raise ValueError(f"versión desconocida: {version!r}; usa {list(VERSIONES)}")
    for id_nodo in (id_origen, id_destino):
        if id_nodo not in red.indice:
            raise KeyError(f"el nodo {id_nodo} no está en la red")
    tiempo, ruta, explorados = VERSIONES[version](
        red.adyacencia, red.indice[id_origen], red.indice[id_destino])
    return tiempo, [red.ids[i] for i in ruta], explorados

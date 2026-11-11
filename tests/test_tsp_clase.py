"""Casos de la matriz de clase y de la vía (spec R4, casos 1 a 10, 17)."""
import copy
import itertools
import math

import pytest

from rutas.r4.fuerza_bruta import fuerza_bruta
from rutas.r4.held_karp import held_karp
from rutas.r4.recorrido import costo_recorrido, validar_entrada
from rutas.r4.vecino import vecino_mas_cercano

# Matriz de clase (segundos, partida 0, lugares [1, 2, 3]); la reutilizan otros archivos.
T_CLASE = [[0, 10, 15, 20], [5, 0, 9, 10], [6, 13, 0, 12], [8, 8, 9, 0]]

# Métodos que deben cumplir los casos 6 a 10; crece con los bloques (T6: vecino, T8: Held-Karp).
METODOS_CLASE = [fuerza_bruta, vecino_mas_cercano, held_karp]

# Matriz de la vía (caso 4b): posiciones A = 0, B = 1, C = -2, D = 5; T[i][j] = |pos_i - pos_j|.
POSICIONES_VIA = [0, 1, -2, 5]
T_VIA = [[abs(a - b) for b in POSICIONES_VIA] for a in POSICIONES_VIA]


def test_caso_1_seis_recorridos():
    esperados = {(1, 2, 3): 39, (1, 3, 2): 35, (2, 1, 3): 46,
                 (2, 3, 1): 40, (3, 1, 2): 43, (3, 2, 1): 47}
    for orden, costo in esperados.items():
        assert costo_recorrido(T_CLASE, [0, *orden, 0]) == costo


def test_caso_5_asimetria():
    assert costo_recorrido(T_CLASE, [0, 2, 3, 1, 0]) == 40
    assert costo_recorrido(T_CLASE, [0, 2, 3, 1, 0]) != 35
    # El recorrido óptimo de Held-Karp no es el inverso del otro sentido.
    assert held_karp(T_CLASE, 0, [1, 2, 3])[1] != [0, 2, 3, 1, 0]


def test_costo_recorrido_bordes():
    costo = costo_recorrido(T_CLASE, [0])
    assert costo == 0.0 and isinstance(costo, float)
    T = copy.deepcopy(T_CLASE)
    T[1][3] = math.inf
    assert costo_recorrido(T, [0, 1, 3, 2, 0]) == math.inf


@pytest.mark.parametrize("s, lugares", [(0, [1, 1]), (0, [0, 1]), (0, [7]),
                                        (0, [-1]), (9, [1, 2])])
def test_validar_entrada_errores(s, lugares):
    with pytest.raises(ValueError):
        validar_entrada(T_CLASE, s, lugares)


def test_validar_entrada_correcta():
    validar_entrada(T_CLASE, 0, [1, 2, 3])


def test_caso_1_2_fuerza_bruta():
    assert fuerza_bruta(T_CLASE, 0, [1, 2, 3]) == (35, [0, 1, 3, 2, 0])


def test_caso_2_held_karp():
    assert held_karp(T_CLASE, 0, [1, 2, 3]) == (35, [0, 1, 3, 2, 0])


def test_caso_4b_via():
    costos = sorted(costo_recorrido(T_VIA, [0, *p, 0])
                    for p in itertools.permutations([1, 2, 3]))
    assert costos == [14, 14, 14, 14, 16, 16]
    assert fuerza_bruta(T_VIA, 0, [1, 2, 3]) == (14, [0, 1, 3, 2, 0])
    # Held-Karp: costo 14 y un recorrido válido cuyo costo, recalculado desde T, es 14.
    tiempo_hk, recorrido_hk = held_karp(T_VIA, 0, [1, 2, 3])
    assert tiempo_hk == 14
    assert recorrido_hk[0] == recorrido_hk[-1] == 0 and sorted(recorrido_hk[1:-1]) == [1, 2, 3]
    assert costo_recorrido(T_VIA, recorrido_hk) == 14
    # El voraz cae en 16 y su brecha es 14,29 %.
    tiempo, recorrido = vecino_mas_cercano(T_VIA, 0, [1, 2, 3])
    assert (tiempo, recorrido) == (16, [0, 1, 2, 3, 0])
    assert (tiempo - 14) / 14 * 100 == pytest.approx(14.2857, abs=1e-3)


@pytest.mark.parametrize("metodo", METODOS_CLASE)
def test_caso_6_k1(metodo):
    assert metodo(T_CLASE, 0, [1]) == (15, [0, 1, 0])


@pytest.mark.parametrize("metodo", METODOS_CLASE)
def test_caso_7_k2(metodo):
    assert metodo(T_CLASE, 0, [1, 2]) == (25, [0, 1, 2, 0])


@pytest.mark.parametrize("metodo", METODOS_CLASE)
def test_caso_8_k0(metodo):
    tiempo, recorrido = metodo(T_CLASE, 0, [])
    assert (tiempo, recorrido) == (0.0, [0])
    assert isinstance(tiempo, float)


@pytest.mark.parametrize("metodo", METODOS_CLASE)
def test_caso_9_arco_inf(metodo):
    T = copy.deepcopy(T_CLASE)
    T[1][3] = math.inf
    assert metodo(T, 0, [1, 2, 3]) == (39, [0, 1, 2, 3, 0])


@pytest.mark.parametrize("metodo", METODOS_CLASE)
def test_caso_9_sin_recorrido_finito(metodo):
    T = copy.deepcopy(T_CLASE)
    for j in (1, 2, 3):
        T[0][j] = math.inf
    with pytest.raises(ValueError):
        metodo(T, 0, [1, 2, 3])


@pytest.mark.parametrize("metodo", METODOS_CLASE)
@pytest.mark.parametrize("lugares", [[1, 1], [0, 1], [7]])
def test_caso_10_errores(metodo, lugares):
    with pytest.raises(ValueError):
        metodo(T_CLASE, 0, lugares)


def test_caso_17_desempate():
    T = [[0 if i == j else 1 for j in range(4)] for i in range(4)]
    assert fuerza_bruta(T, 0, [1, 2, 3]) == (4, [0, 1, 2, 3, 0])
    tiempo_hk, recorrido_hk = held_karp(T, 0, [1, 2, 3])
    assert tiempo_hk == 4
    assert recorrido_hk[0] == recorrido_hk[-1] == 0 and sorted(recorrido_hk[1:-1]) == [1, 2, 3]
    assert costo_recorrido(T, recorrido_hk) == 4


@pytest.mark.parametrize("metodo", METODOS_CLASE)
def test_no_modifica_entradas(metodo):
    T, lugares = copy.deepcopy(T_CLASE), [3, 1, 2]
    metodo(T, 0, lugares)
    assert T == T_CLASE and lugares == [3, 1, 2]


def test_caso_4_voraz_no_optimo():
    tiempo, recorrido = vecino_mas_cercano(T_CLASE, 0, [1, 2, 3])
    assert (tiempo, recorrido) == (39, [0, 1, 2, 3, 0])
    optimo = fuerza_bruta(T_CLASE, 0, [1, 2, 3])[0]
    assert (tiempo - optimo) / optimo * 100 == pytest.approx(11.428571, abs=1e-4)


def test_vecino_desempate_menor_indice():
    # Desde la partida, los lugares 1 y 2 están a la misma distancia (5): gana el índice 1,
    # aunque los lugares lleguen desordenados.
    T = [[0, 5, 5, 9], [5, 0, 3, 3], [5, 3, 0, 3], [9, 3, 3, 0]]
    tiempo, recorrido = vecino_mas_cercano(T, 0, [3, 2, 1])
    assert recorrido == [0, 1, 2, 3, 0]


def test_vecino_regreso_inf():
    T = copy.deepcopy(T_CLASE)
    for i in (1, 2, 3):
        T[i][0] = math.inf
    with pytest.raises(ValueError):
        vecino_mas_cercano(T, 0, [1, 2, 3])

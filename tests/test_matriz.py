"""Matriz de tiempos: cálculo, guardado sin redondear, lectura y asimetría (R2)."""
import math

import pytest

from rutas.r2.matriz import asimetria, calcular_matriz, cargar_matriz, guardar_matriz
from tests.conftest import cargar_red_clase, red_desde_aristas

# Grafo G1 de la spec con A=1 ... F=6 (F aislado)
G1 = [(1, 2, 4), (1, 3, 1), (3, 2, 2), (2, 4, 1), (3, 4, 5), (4, 5, 3)]


def test_caso_23_asimetria_clase():
    red, r2 = cargar_red_clase()
    orden = r2["matriz_min"]["orden"]
    matriz = calcular_matriz(red, orden)
    assert matriz == [[float(x) for x in fila] for fila in r2["matriz_min"]["filas"]]

    resultado = asimetria(matriz, orden)
    assert resultado["pares_asimetricos"] == 9
    assert resultado["par_max"] == [4, 7]          # normalizado a i < j por el orden de ids
    assert resultado["diferencia_max"] == 10
    assert resultado["M_ij"] == 4 and resultado["M_ji"] == 14


def test_asimetria_matriz_simetrica_y_tolerancia():
    simetrica = [[0.0, 2.0], [2.0, 0.0]]
    assert asimetria(simetrica, ["a", "b"])["pares_asimetricos"] == 0
    casi = [[0.0, 2.0], [2.0 + 1e-7, 0.0]]          # por debajo de la tolerancia 1e-6
    assert asimetria(casi, ["a", "b"])["pares_asimetricos"] == 0


def test_mismo_nodo_da_cero():
    # Red fuertemente conexa 1 -> 2 -> 3 y de vuelta; los lugares 0 y 2 comparten el nodo 1
    red = red_desde_aristas([(1, 2, 3), (2, 1, 5), (2, 3, 1), (3, 2, 1)])
    matriz = calcular_matriz(red, [1, 3, 1])
    assert matriz[0][2] == 0 and matriz[2][0] == 0
    assert all(matriz[i][i] == 0 for i in range(3))
    assert matriz[0][1] == 4 and matriz[1][0] == 6      # asimétrica: 1->3 = 4, 3->1 = 6


def test_inf_es_error():
    red = red_desde_aristas(G1, nodos=[6])
    with pytest.raises(ValueError, match="inalcanzable"):
        calcular_matriz(red, [1, 6])


def test_nodo_ausente_keyerror():
    red = red_desde_aristas(G1)
    with pytest.raises(KeyError, match="99"):
        calcular_matriz(red, [1, 99])


def test_guardar_cargar_round_trip_byte_a_byte(tmp_path):
    ids = ["C01", "C02", "C03"]
    matriz = [[0.0, 0.1 + 0.2, 1 / 3], [123.456789012345678, 0.0, 2.0], [1e-9, 7.0, 0.0]]
    primero, segundo = tmp_path / "a.csv", tmp_path / "b.csv"
    guardar_matriz(matriz, ids, primero)

    texto = primero.read_text(encoding="utf-8")
    assert texto.splitlines()[0] == "id,C01,C02,C03"
    assert texto.splitlines()[1].startswith("C01,0.0,0.30000000000000004,")

    leida = cargar_matriz(primero)
    assert list(leida.index) == ids and list(leida.columns) == ids
    assert leida.values.tolist() == matriz           # igualdad exacta, sin tolerancia

    guardar_matriz(leida.values.tolist(), list(leida.index), segundo)
    assert primero.read_bytes() == segundo.read_bytes()


def test_main_sintetico(tmp_path):
    """Carpeta processed sintética: grafo fuertemente conexo de 3 nodos y 3 lugares."""
    import json

    import pandas as pd

    from rutas.r1.persistencia import guardar_procesado
    from rutas.r2.matriz import main
    from tests.conftest import grafo_sintetico

    nodos = {10: (-75.6, 4.5), 20: (-75.7, 4.6), 30: (-75.8, 4.7)}
    aristas = [(10, 20, {"travel_time": 60.0, "length": 500.0}),
               (20, 30, {"travel_time": 30.5, "length": 300.0}),
               (30, 10, {"travel_time": 90.25, "length": 900.0}),
               (20, 10, {"travel_time": 70.0, "length": 500.0})]
    G = grafo_sintetico(nodos, aristas)
    lugares = pd.DataFrame({"id_lugar": ["L1", "L2", "L3"], "id_nodo": [10, 20, 30],
                            "distancia_al_nodo_m": [1.0, 2.0, 3.0],
                            "alerta_500m": [False, False, False]})
    processed, salida = tmp_path / "processed", tmp_path / "r2"
    guardar_procesado(G, lugares, {}, carpeta=processed)
    catalogo = tmp_path / "catalogo.csv"
    pd.DataFrame({"id": ["L1", "L2", "L3"], "municipio": ["A", "A", "B"]}).to_csv(catalogo, index=False)

    main(processed=processed, catalogo=catalogo, salida=salida)

    matriz = cargar_matriz(processed / "matriz_tiempos.csv")
    assert list(matriz.index) == ["L1", "L2", "L3"] and matriz.shape == (3, 3)
    assert matriz.loc["L1", "L3"] == 60.0 + 30.5 and matriz.loc["L3", "L1"] == 90.25
    resultado = json.loads((salida / "r2_asimetria.json").read_text(encoding="utf-8"))
    assert set(resultado) == {"pares_asimetricos", "par_max", "diferencia_max", "M_ij", "M_ji",
                              "tolerancia"}
    assert resultado["pares_asimetricos"] == 3

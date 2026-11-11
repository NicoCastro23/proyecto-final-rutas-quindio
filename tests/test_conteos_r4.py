"""Memoria estimada de Held-Karp y conteos teóricos (spec R4, casos 14 y 15)."""
import pytest

from rutas.r4.conteos import conteos_teoricos, memoria_held_karp


@pytest.mark.parametrize("k, celdas, bytes_", [(5, 160, 1920), (8, 2048, 24576),
                                               (10, 10240, 122880), (12, 49152, 589824)])
def test_caso_14_memoria(k, celdas, bytes_):
    m = memoria_held_karp(k)
    assert m["k"] == k
    assert m["celdas"] == celdas
    assert m["bytes_estimados"] == bytes_
    assert m["mb_estimados"] == pytest.approx(bytes_ / 1e6)


def test_caso_14_memoria_k12_en_mb():
    assert memoria_held_karp(12)["mb_estimados"] == pytest.approx(0.589824)


@pytest.mark.parametrize("k, transiciones", [(3, 18), (5, 170), (8, 3600),
                                             (10, 23060), (12, 135192)])
def test_caso_15_conteos_teoricos(k, transiciones):
    assert conteos_teoricos(k)["transiciones_hk"] == transiciones


def test_caso_15_fuerza_bruta_k12():
    c = conteos_teoricos(12)
    assert c["permutaciones_fb"] == 479_001_600
    assert c["tramos_fb"] == 6_227_020_800


def test_conteos_bordes():
    assert conteos_teoricos(0)["transiciones_hk"] == 0
    assert conteos_teoricos(1)["transiciones_hk"] == 2

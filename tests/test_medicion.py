"""Pruebas de rutas/medicion.py con time.sleep de duración conocida (sección 6)."""
import math
import time

import pytest

from rutas.medicion import info_maquina, medir_en_hijo, medir_en_proceso


# ---------- modo (a): mismo proceso ----------

def test_en_proceso_cinco_repeticiones_y_mediana():
    r = medir_en_proceso(time.sleep, preparar=lambda: (0.02,))
    assert r.completada and r.repeticiones == 5 and len(r.tiempos_ms) == 5
    assert 18 <= r.tiempo_ms <= 60


def test_en_proceso_una_sola_repeticion_si_supera_umbral():
    r = medir_en_proceso(time.sleep, preparar=lambda: (0.1,), umbral_una_s=0.05)
    assert r.repeticiones == 1 and r.completada


def test_en_proceso_preparar_fuera_del_cronometro():
    def preparar():
        time.sleep(0.3)
        return ()

    r = medir_en_proceso(lambda: None, preparar=preparar, repeticiones=2)
    assert r.tiempo_ms < 100


def test_en_proceso_preparar_en_cada_repeticion():
    llamadas, recibidos = [], []

    def preparar():
        llamadas.append(1)
        return (object(),)

    medir_en_proceso(lambda objeto: recibidos.append(objeto), preparar=preparar)
    assert len(llamadas) == 5
    assert len({id(o) for o in recibidos}) == 5


def test_en_proceso_no_completada_si_supera_limite():
    r = medir_en_proceso(time.sleep, preparar=lambda: (0.1,), limite_s=0.05, umbral_una_s=0.01)
    assert r.completada is False and r.tiempo_ms is None and r.repeticiones == 0


def test_info_maquina_tiene_campos():
    info = info_maquina()
    assert set(info) == {"procesador", "ram_gb", "so", "python"}
    assert info["procesador"] and info["so"] and info["python"] and info["ram_gb"] > 0


# ---------- modo (b): proceso hijo ----------

def test_en_hijo_no_incluye_arranque_del_proceso():
    inicio = time.perf_counter()
    r = medir_en_hijo(time.sleep, (0.05,), repeticiones=1)
    pared_ms = (time.perf_counter() - inicio) * 1000
    assert 45 <= r.tiempo_ms <= 150
    assert pared_ms > r.tiempo_ms          # arrancar el hijo (spawn) cuesta más y no se cuenta


def test_en_hijo_no_completada_si_supera_limite():
    inicio = time.perf_counter()
    r = medir_en_hijo(time.sleep, (3,), limite_s=0.5)
    assert time.perf_counter() - inicio < 2.5      # el hijo se terminó, no se esperó a que acabe
    assert r.completada is False and r.tiempo_ms is None and r.repeticiones == 0


def test_en_hijo_cinco_repeticiones_y_mediana():
    r = medir_en_hijo(time.sleep, (0.02,))
    assert r.completada and r.repeticiones == 5
    assert 18 <= r.tiempo_ms <= 60


def test_en_hijo_una_sola_repeticion_si_supera_umbral():
    r = medir_en_hijo(time.sleep, (0.1,), umbral_una_s=0.05)
    assert r.repeticiones == 1


def test_en_hijo_error_en_el_hijo():
    inicio = time.perf_counter()
    with pytest.raises(RuntimeError, match="hijo"):
        medir_en_hijo(math.sqrt, (-1,))
    assert time.perf_counter() - inicio < 30       # falla ya, no espera el límite de 300 s


# ---------- devolver_valor (R4, T17): el valor viaja después de parar el cronómetro ----------

def test_en_hijo_devuelve_valor():
    r = medir_en_hijo(math.sqrt, (16.0,), repeticiones=2, devolver_valor=True)
    assert r.completada and r.valor == 4.0


def test_en_hijo_sin_valor_por_defecto():
    r = medir_en_hijo(math.sqrt, (16.0,), repeticiones=2)
    assert r.completada and r.valor is None


def test_en_hijo_valor_no_completada():
    r = medir_en_hijo(time.sleep, (3,), limite_s=0.5, devolver_valor=True)
    assert r.completada is False and r.valor is None


def test_en_hijo_devuelve_tupla_con_lista():
    from rutas.r4.held_karp import held_karp
    from tests.test_tsp_clase import T_CLASE
    r = medir_en_hijo(held_karp, (T_CLASE, 0, [1, 2, 3]), repeticiones=1, devolver_valor=True)
    assert r.valor == (35.0, [0, 1, 3, 2, 0])

"""Servicios de R5 con la red real (casos 1, 3, 4, 5, 6 y 7). Marcador `red`."""
import json

import pytest

from rutas.config import DATA_PROCESSED, RESULTS_R4
from rutas.r2.ruta import detalle_ruta
from rutas.r5.app import crear_app
from rutas.r5.datos import cargar_datos
from rutas.r5.servicios import itinerario, ruta_entre

pytestmark = pytest.mark.red

CASO_5 = ["A05", "A14", "A06", "A07", "A13", "A15"]
CASO_6 = ["A05", "A08", "A04", "A14", "A06", "A07", "A12", "A01"]


@pytest.fixture(scope="module")
def datos_reales():
    if not any((DATA_PROCESSED / n).exists()
               for n in ("grafo_componente.graphml", "grafo_componente.graphml.gz")):
        pytest.skip("falta data/processed/grafo_componente.graphml[.gz]")
    return cargar_datos()          # una sola vez para todo el módulo


def test_caso_1_ruta_real(datos_reales):
    d = datos_reales
    r = ruta_entre(d, "C01", "C12")
    assert r["tiempo_s"] == pytest.approx(d.matriz.loc["C01", "C12"], abs=1e-6)
    assert r["tiempo_s"] == pytest.approx(1783.39, abs=0.01)
    assert r["ids_nodos"][0] == d.nodo_de["C01"]
    assert r["ids_nodos"][-1] == d.nodo_de["C12"]
    assert detalle_ruta(d.G, r["ids_nodos"])[0] == pytest.approx(r["tiempo_s"], abs=1e-6)
    nodo = d.G.nodes[d.nodo_de["C01"]]
    lat, lon = r["coordenadas"][0]
    assert abs(lat - nodo["y"]) < 1e-6 and abs(lon - nodo["x"]) < 1e-6
    assert r["nodos_explorados"] > 0


def test_caso_1_asimetria(datos_reales):
    r = ruta_entre(datos_reales, "C12", "C01")
    assert r["tiempo_s"] == pytest.approx(1708.19, abs=0.01)
    assert r["tiempo_s"] == pytest.approx(datos_reales.matriz.loc["C12", "C01"], abs=1e-6)


def test_caso_3_mismo_lugar_real(datos_reales):
    r = ruta_entre(datos_reales, "C01", "C01")
    assert r["tiempo_s"] == 0
    assert r["aviso"] == "origen y destino son el mismo lugar"


def test_caso_4_mismo_nodo(datos_reales):
    r = ruta_entre(datos_reales, "T03", "T05")
    assert r["tiempo_s"] == 0
    assert r["aviso"] == "los dos lugares están en el mismo punto de la red"


def test_caso_5_itinerario_cabe(datos_reales):
    it = itinerario(datos_reales, "C01", CASO_5)
    hk, voraz = it["held_karp"], it["voraz"]
    assert hk["desplazamiento_min"] == pytest.approx(178.66, abs=0.01)
    assert hk["recorrido"] == ["C01", "A15", "A13", "A07", "A06", "A14", "A05", "C01"]
    assert voraz["desplazamiento_min"] == pytest.approx(190.45, abs=0.01)
    assert voraz["recorrido"] == ["C01", "A05", "A14", "A07", "A06", "A13", "A15", "C01"]
    assert it["diferencia_min"] == pytest.approx(11.79, abs=0.01)
    assert it["brecha_pct"] == pytest.approx(6.60, abs=0.01)
    assert hk["visitas_min"] == voraz["visitas_min"] == 240
    assert hk["jornada_min"] == pytest.approx(418.66, abs=0.01)
    assert voraz["jornada_min"] == pytest.approx(430.45, abs=0.01)
    assert hk["cabe"] and voraz["cabe"]
    assert it["jornada"] is None


def test_caso_6_itinerario_no_cabe(datos_reales):
    it = itinerario(datos_reales, "C01", CASO_6)
    hk = it["held_karp"]
    assert hk["desplazamiento_min"] == pytest.approx(145.22, abs=0.01)
    assert hk["jornada_min"] == pytest.approx(1255.22, abs=0.01)
    assert not hk["cabe"]
    assert it["voraz"]["desplazamiento_min"] == pytest.approx(155.39, abs=0.01)
    assert it["diferencia_min"] == pytest.approx(10.17, abs=0.01)
    assert it["brecha_pct"] == pytest.approx(7.01, abs=0.01)
    jornada = it["jornada"]
    assert [q["id"] for q in jornada["quitados"]] == ["A01", "A12"]
    esperado = json.loads((RESULTS_R4 / "r4_itinerario.json").read_text(encoding="utf-8"))
    assert jornada["jornada_final_min"] == pytest.approx(esperado["totales"]["jornada_min"], abs=1e-6)
    assert jornada["jornada_final_min"] == pytest.approx(613.13, abs=0.01)


@pytest.mark.parametrize("clave", ["held_karp", "voraz"])
def test_caso_7_tramos(datos_reales, clave):
    r = itinerario(datos_reales, "C01", CASO_5)[clave]
    for tramo in r["tramos"]:
        esperado = datos_reales.matriz.loc[tramo["desde"], tramo["hasta"]]
        assert tramo["tiempo_min"] * 60 == pytest.approx(esperado, abs=1e-6)
    assert sum(t["tiempo_min"] for t in r["tramos"]) * 60 == pytest.approx(
        r["desplazamiento_min"] * 60, abs=1e-6)


# ---- La app con la red real (casos 2, 3, 9 y 10) ----
@pytest.fixture(scope="module")
def cliente_real(datos_reales):
    return crear_app(datos_reales).test_client()


def _consulta(partida, atractivos):
    return f"/itinerario?partida={partida}&" + "&".join(f"atractivos={a}" for a in atractivos)


def test_caso_2_ruta_en_la_app(cliente_real):
    r = cliente_real.get("/ruta?origen=C01&destino=C12")
    html = r.get_data(as_text=True)
    assert r.status_code == 200 and "29,7" in html and "leaflet" in html


def test_caso_3_ruta_mismo_lugar_real(cliente_real):
    r = cliente_real.get("/ruta?origen=C01&destino=C01")
    assert r.status_code == 200
    assert "origen y destino son el mismo lugar" in r.get_data(as_text=True)


def test_caso_9_itinerario_en_la_app(cliente_real):
    r = cliente_real.get(_consulta("C01", CASO_5))
    html = r.get_data(as_text=True)
    assert r.status_code == 200
    assert "178,7" in html and "190,4" in html and "11,8" in html
    assert "Regla de las 11 h" not in html


def test_itinerario_no_cabe_en_la_app(cliente_real):
    r = cliente_real.get(_consulta("C01", CASO_6))
    html = r.get_data(as_text=True)
    assert r.status_code == 200
    assert "Regla de las 11 h" in html and "Parque Nacional del Café" in html and "613,1" in html


def test_caso_10_envolvente_real(cliente_real):
    r = cliente_real.get("/envolvente")
    html = r.get_data(as_text=True)
    assert r.status_code == 200 and "14 vértices" in html and "1 631,5" in html


def test_formulario_42_lugares_15_atractivos(cliente_real):
    html = cliente_real.get("/itinerario").get_data(as_text=True)
    assert html.count("<option") == 42
    assert html.count('name="atractivos"') == 15

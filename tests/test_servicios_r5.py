"""Pruebas de los servicios de R5 (sin Flask) con los datos sintéticos de conftest."""
import pytest

from rutas.r5.servicios import ErrorEntrada, coordenadas_de, ruta_entre, validar_itinerario, itinerario
from rutas.r5.servicios import ARCHIVOS_RESULTADOS, resultados
from rutas.config import RESULTS
from rutas.r4.por_ids import resolver_por_ids
from rutas.r5.datos import cargar_datos
from tests.conftest import carpeta_app_sintetica


# --- T6: coordenadas que siguen la geometría (caso 15) ---------------------------------------
def test_caso_15_geometria_curva(datos_app):
    # la arista 1->2 trae una curva de 3 puntos en (lon, lat); se devuelven como (lat, lon)
    assert coordenadas_de(datos_app.G, [1, 2]) == [(4.50, -75.70), (4.505, -75.69), (4.50, -75.68)]


def test_sin_duplicar_uniones(datos_app):
    puntos = coordenadas_de(datos_app.G, [1, 2, 3])
    assert len(puntos) == 4
    assert puntos[-1] == (4.50, -75.66)
    assert all(a != b for a, b in zip(puntos, puntos[1:]))


def test_segmento_recto_sin_geometria(datos_app):
    assert coordenadas_de(datos_app.G, [2, 3]) == [(4.50, -75.68), (4.50, -75.66)]


def test_un_nodo_sin_linea(datos_app):
    assert coordenadas_de(datos_app.G, [1]) == []


# --- T7: ruta_entre y validar_lugar (casos 3 y 4 sintéticos) ---------------------------------
def test_ruta_sintetica(datos_app):
    r = ruta_entre(datos_app, "C01", "A02")
    assert r["tiempo_s"] == pytest.approx(datos_app.matriz.loc["C01", "A02"], abs=1e-6)
    assert r["ids_nodos"] == [1, 2, 3]
    assert r["distancia_km"] == pytest.approx(1.0)
    assert r["tiempo_min"] == pytest.approx(r["tiempo_s"] / 60)
    assert r["nodos_explorados"] > 0
    assert r["computo_ms"] >= 0
    assert len(r["coordenadas"]) == 4
    assert r["aviso"] is None


def test_caso_3_mismo_lugar(datos_app):
    r = ruta_entre(datos_app, "C01", "C01")
    assert r["tiempo_s"] == 0
    assert r["coordenadas"] == []
    assert r["aviso"] == "origen y destino son el mismo lugar"


def test_mismo_punto_sintetico(datos_app):
    r = ruta_entre(datos_app, "A02", "A06")
    assert r["tiempo_s"] == 0
    assert r["aviso"] == "los dos lugares están en el mismo punto de la red"


def test_lugar_desconocido(datos_app):
    with pytest.raises(ErrorEntrada, match="lugar desconocido: X99"):
        ruta_entre(datos_app, "X99", "C01")
    with pytest.raises(ErrorEntrada, match="lugar desconocido: X99"):
        ruta_entre(datos_app, "C01", "X99")


def test_asimetria_sintetica(datos_app):
    assert ruta_entre(datos_app, "A01", "C01")["tiempo_s"] == pytest.approx(90)
    assert ruta_entre(datos_app, "C01", "A01")["tiempo_s"] == pytest.approx(60)


# --- T8: validación del itinerario (caso 8 a nivel de servicio) ------------------------------
SEIS = ["A01", "A02", "A03", "A04", "A05", "A06"]


@pytest.mark.parametrize("partida, lista, fragmento", [
    ("C01", SEIS[:5], "entre 6 y 8"),
    ("C01", SEIS + ["A01", "A02", "A03"], "entre 6 y 8"),
    ("C01", [], "(llegaron 0)"),
    ("C01", ["A01", "A01", "A02", "A03", "A04", "A05"], "repetido: A01"),
    ("A01", SEIS, "la partida A01"),
    ("C01", SEIS[:5] + ["C02"], "C02 no es un atractivo turístico"),
    ("X99", SEIS, "lugar desconocido: X99"),
])
def test_caso_8_validacion(datos_app, partida, lista, fragmento):
    with pytest.raises(ErrorEntrada, match=fragmento.replace("(", r"\(").replace(")", r"\)")):
        validar_itinerario(datos_app, partida, lista)


def test_validacion_correcta(datos_app):
    validar_itinerario(datos_app, "C01", SEIS)
    validar_itinerario(datos_app, "C02", SEIS)      # la partida puede ser cualquier lugar


# --- T9: itinerario (casos 5, 6 y 7 en sintéticos) --------------------------------------------
METODOS = [("held_karp", "held_karp"), ("voraz", "vecino_mas_cercano")]


@pytest.mark.parametrize("clave, metodo", METODOS)
def test_itinerario_cabe_sintetico(datos_app, clave, metodo):
    it = itinerario(datos_app, "C01", SEIS)
    tiempo_s, recorrido = resolver_por_ids(datos_app.matriz, "C01", SEIS, metodo)
    r = it[clave]
    assert r["desplazamiento_min"] * 60 == pytest.approx(tiempo_s, abs=1e-6)
    assert r["recorrido"] == recorrido
    assert r["visitas_min"] == 270
    assert r["jornada_min"] == pytest.approx(r["desplazamiento_min"] + 270)
    assert r["cabe"] is True
    assert r["computo_ms"] >= 0
    assert it["diferencia_min"] >= 0
    assert it["partida"] == "C01" and it["atractivos"] == SEIS
    assert it["jornada"] is None


@pytest.mark.parametrize("clave", ["held_karp", "voraz"])
def test_tramos_igual_a_matriz_sintetico(datos_app, clave):
    r = itinerario(datos_app, "C01", SEIS)[clave]
    pares = list(zip(r["recorrido"], r["recorrido"][1:]))
    assert len(r["tramos"]) == len(pares)
    for tramo, (desde, hasta) in zip(r["tramos"], pares):
        assert (tramo["desde"], tramo["hasta"]) == (desde, hasta)
        assert tramo["tiempo_min"] * 60 == pytest.approx(datos_app.matriz.loc[desde, hasta], abs=1e-6)
    assert sum(t["tiempo_min"] for t in r["tramos"]) == pytest.approx(r["desplazamiento_min"], abs=1e-6 / 60)


def test_itinerario_no_cabe_sintetico(tmp_path):
    processed, catalogo, _ = carpeta_app_sintetica(tmp_path, visitas=[120] * 6)
    datos = cargar_datos(processed, catalogo)
    it = itinerario(datos, "C01", SEIS)
    assert it["held_karp"]["cabe"] is False
    jornada = it["jornada"]
    assert jornada["quitados"]
    for q in jornada["quitados"]:
        assert q["lugar"] == datos.nombre_de[q["id"]]
        assert q["visita_min"] == 120
        assert {"desvio_min", "ahorro_min"} <= set(q)
    assert jornada["jornada_final_min"] <= 660
    final = jornada["recorrido_final"]
    assert final[0] == final[-1] == "C01"
    assert not {q["id"] for q in jornada["quitados"]} & set(final)
    # el mapa sigue mostrando los 6 elegidos: recorrido y tramos de HK no cambian
    assert sorted(it["held_karp"]["recorrido"][1:-1]) == SEIS
    assert len(it["held_karp"]["tramos"]) == 7


def test_no_llama_resolver_si_invalido(datos_app, monkeypatch):
    llamadas = []
    monkeypatch.setattr("rutas.r5.servicios.resolver_por_ids",
                        lambda *a, **k: llamadas.append(a))
    with pytest.raises(ErrorEntrada):
        itinerario(datos_app, "C01", SEIS[:5])
    assert llamadas == []


# --- T10: resultados con la lista fija (caso 11 a nivel de servicio) --------------------------
def test_caso_11_resultados_sinteticos(tmp_path):
    _, _, results = carpeta_app_sintetica(tmp_path)
    r2 = resultados("r2", results)
    assert r2["imagenes"] == ["r2_tiempo_vs_explorados.png"]
    tablas = dict(r2["tablas"])
    assert "<table" in tablas["r2_cociente.csv"] and "mediana" in tablas["r2_cociente.csv"]
    assert "1,500" in tablas["r2_cociente.csv"]            # coma decimal, 3 decimales
    assert r2["faltantes"] == []
    r4 = resultados("r4", results)
    assert ("r4_exactas.csv", ".venv/bin/python -m rutas.r4.medir_exactas") in r4["faltantes"]
    assert ("r4_tiempo_vs_k.png", ".venv/bin/python -m rutas.r4.tablas") in r4["faltantes"]


def test_texto_escapado(tmp_path):
    (tmp_path / "r2").mkdir()
    (tmp_path / "r2" / "r2_pares.csv").write_text("nombre\n<b>x</b>\n", encoding="utf-8")
    html = dict(resultados("r2", tmp_path)["tablas"])["r2_pares.csv"]
    assert "&lt;b&gt;" in html and "<b>x</b>" not in html


def test_celdas_vacias(tmp_path):
    (tmp_path / "r4").mkdir()
    (tmp_path / "r4" / "r4_calidad.csv").write_text("k,nota\n6,\n7,algo\n", encoding="utf-8")
    html = dict(resultados("r4", tmp_path)["tablas"])["r4_calidad.csv"]
    assert "nan" not in html.lower()


def test_requerimiento_desconocido(tmp_path):
    with pytest.raises(KeyError):
        resultados("r9", tmp_path)


def test_lista_fija_existe_en_results():
    """Contra results/ real: solo pueden faltar los tres archivos que aún no se generan."""
    faltan = set()
    for r, grupos in ARCHIVOS_RESULTADOS.items():
        for archivo, _ in grupos["imagenes"] + grupos["tablas"]:
            if not (RESULTS / r / archivo).exists():
                faltan.add(archivo)
    assert faltan <= {"r1_tiempos_componente.png", "r4_exactas.csv", "r4_tiempo_vs_k.png"}

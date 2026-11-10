import pandas as pd
import pytest

from rutas.config import CATALOGO
from rutas.r1.catalogo import RECUADRO, CatalogoInvalido, cargar_catalogo


def _con_celda_alterada(tmp_path, fila, columna, valor):
    """Copia el catálogo real, cambia una celda y lo escribe en tmp_path."""
    df = pd.read_csv(CATALOGO)
    df.loc[fila, columna] = valor
    ruta = tmp_path / "catalogo.csv"
    df.to_csv(ruta, index=False)
    return ruta


def test_caso_12_catalogo_real():
    df = cargar_catalogo()
    assert len(df) == 42
    assert df["categoria"].value_counts().to_dict() == {
        "Cabecera municipal": 12, "Atractivo turístico": 15,
        "Finca u hotel rural": 9, "Centro de acopio o trilladora": 6}
    assert df["id"].is_unique
    atractivos = df[df["categoria"] == "Atractivo turístico"]
    assert (atractivos["duracion_visita_min"] > 0).all()
    assert atractivos["fuente_duracion"].str.match(r"Criterio [1-4]").all()
    assert df["verificado"].all()
    # Recuadro de la spec: lat 4,0 a 4,9 y lon -76,0 a -75,4. Cocora (lon -75,489) y PANACA
    # (lon -75,819) deben quedar dentro; un recuadro que termine en -75,5 dejaría fuera a Cocora.
    for nombre in ("Valle de Cocora", "PANACA"):
        lugar = df[df["nombre"] == nombre]
        assert len(lugar) == 1, nombre
        fila = lugar.iloc[0]
        assert 4.0 <= fila["latitud"] <= 4.9, nombre
        assert -76.0 <= fila["longitud"] <= -75.4, nombre
    assert RECUADRO == {"lat": (4.0, 4.9), "lon": (-76.0, -75.4)}
    cocora = df[df["nombre"] == "Valle de Cocora"].iloc[0]
    assert df[df["id"] == "A03"].iloc[0]["nombre"] == "Valle de Cocora"
    assert not (-76.0 <= cocora["longitud"] <= -75.5)    # un recuadro hasta -75,5 la excluiría


def test_caso_12_id_repetido(tmp_path):
    ruta = _con_celda_alterada(tmp_path, 1, "id", "C01")
    with pytest.raises(CatalogoInvalido, match="id"):
        cargar_catalogo(ruta)


def test_caso_12_categoria_invalida(tmp_path):
    ruta = _con_celda_alterada(tmp_path, 3, "categoria", "Museo")
    with pytest.raises(CatalogoInvalido, match="categor"):
        cargar_catalogo(ruta)


def test_caso_12_latitud_fuera(tmp_path):
    ruta = _con_celda_alterada(tmp_path, 4, "latitud", 5.5)
    with pytest.raises(CatalogoInvalido, match="latitud"):
        cargar_catalogo(ruta)


def test_conteo_distinto(tmp_path):
    df = pd.read_csv(CATALOGO).iloc[:-1]
    ruta = tmp_path / "catalogo.csv"
    df.to_csv(ruta, index=False)
    with pytest.raises(CatalogoInvalido, match="42"):
        cargar_catalogo(ruta)


def test_atractivo_sin_duracion(tmp_path):
    df = pd.read_csv(CATALOGO)
    fila = df.index[df["categoria"] == "Atractivo turístico"][0]
    ruta = _con_celda_alterada(tmp_path, fila, "duracion_visita_min", float("nan"))
    with pytest.raises(CatalogoInvalido, match="duracion"):
        cargar_catalogo(ruta)


def test_no_verificado(tmp_path):
    ruta = _con_celda_alterada(tmp_path, 2, "verificado", False)
    with pytest.raises(CatalogoInvalido, match="verificado"):
        cargar_catalogo(ruta)


def test_mensaje_indica_fila_y_regla(tmp_path):
    # La fila 4 del DataFrame (índice 3) es la línea 5 del CSV (encabezado = línea 1)
    ruta = _con_celda_alterada(tmp_path, 3, "categoria", "Museo")
    with pytest.raises(CatalogoInvalido) as e:
        cargar_catalogo(ruta)
    mensaje = str(e.value)
    assert "fila 5" in mensaje
    assert df_id(3) in mensaje
    assert "categor" in mensaje


def df_id(indice):
    return pd.read_csv(CATALOGO).loc[indice, "id"]

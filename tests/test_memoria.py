from rutas.r1.memoria import estimar_memoria, filas_memoria


def test_caso_1_v1000_e2500():
    r = estimar_memoria(1000, 2500)
    assert r["matriz_bytes"] == 16_000_000
    assert r["matriz_mb"] == 16.0
    assert r["listas_bytes"] == 68_000
    assert r["listas_mb"] == 0.068


def test_caso_1b_v30000_e75000():
    r = estimar_memoria(30_000, 75_000)
    assert r["matriz_bytes"] == 14_400_000_000
    assert r["matriz_mb"] == 14_400.0
    assert r["listas_bytes"] == 2_040_000
    assert r["listas_mb"] == 2.04


def test_bytes_son_enteros():
    r = estimar_memoria(123_457, 300_001)
    assert isinstance(r["matriz_bytes"], int)
    assert isinstance(r["listas_bytes"], int)


def test_filas_memoria_dos_filas():
    filas = filas_memoria("Red descargada", 1000, 2500)
    assert len(filas) == 2
    for f in filas:
        assert list(f) == ["red", "V", "E", "representacion", "supuesto", "bytes", "MB"]
        assert (f["red"], f["V"], f["E"]) == ("Red descargada", 1000, 2500)
        assert f["supuesto"]
    assert filas[0]["representacion"] == "Matriz de adyacencia"
    assert filas[1]["representacion"] == "Listas de adyacencia"
    assert filas[0]["bytes"] == 16_000_000
    assert filas[1]["bytes"] == 68_000

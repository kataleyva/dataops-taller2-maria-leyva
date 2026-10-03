# Pruebas unitarias del test de datos y del modelo.

from generar_datos import generar_ventas
from train_model import entrenar
from validar_datos import validar
from validate_model import es_valido

COLUMNAS = ["semana", "precio_promedio", "promocion", "id_tienda", "ventas"]


def test_datos_limpios_pasan_la_validacion():
    assert not validar(generar_ventas(), COLUMNAS, 0.10)


def test_mas_de_10_por_ciento_de_nulos_falla():
    errores = validar(generar_ventas(porcentaje_nulos=0.15), COLUMNAS, 0.10)
    assert any("nulos" in error for error in errores)


def test_columna_faltante_falla():
    datos = generar_ventas().drop(columns=["promocion"])
    assert validar(datos, COLUMNAS, 0.10)


def test_modelo_con_datos_sinteticos_supera_el_umbral():
    _, mape = entrenar(generar_ventas(), "ventas")
    assert mape <= 15.0


def test_modelo_peor_que_produccion_no_se_promueve():
    assert not es_valido(18.2, 12.1, 15.0)
    assert es_valido(10.0, 12.1, 15.0)

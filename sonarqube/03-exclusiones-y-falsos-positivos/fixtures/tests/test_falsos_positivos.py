"""Tests parciales: cubren solo las funciones que tienen sentido testear."""

from src.falsos_positivos import (
    calcular_metricas,
    generar_hash_documento,
    procesar_archivos,
    validar_formato,
)


def test_generar_hash_es_estable():
    a = generar_hash_documento("contenido")
    b = generar_hash_documento("contenido")
    assert a == b


def test_generar_hash_es_distinto():
    assert generar_hash_documento("a") != generar_hash_documento("b")


def test_validar_formato_correcto():
    assert validar_formato("12345") is True


def test_validar_formato_incorrecto():
    assert validar_formato("abc") is False


def test_calcular_metricas():
    datos = [
        {"tipo": "venta", "valor": 100},
        {"tipo": "devolucion", "valor": 20},
    ]
    assert calcular_metricas(datos) == (100, 20, 0)


def test_procesar_archivos_inexistente():
    assert procesar_archivos(["/no/existe"]) == [-1]
"""Pruebas parciales: cubren solo el 40% del código a propósito."""

import pytest

from src.pedidos import calcular_pedido_completo, procesar_pedido
from src.utils import calcular_descuento, generar_token, resumen_usuario


def test_calcular_descuento_precio_alto():
    # ⚠️ Estos valores son INCORRECTOS a propósito.
    # El bug está en src/utils.py: se usa `if` en lugar de `elif`, así que
    # el segundo `if` (precio > 500) pisa al primero (precio > 100).
    # SonarQube lo detecta como S1871 (branch condition should be elif).
    # El valor correcto sería 800.0 (20 % de descuento).
    assert calcular_descuento(1000, 1, False) == 700.0


def test_calcular_descuento_vip():
    # ⚠️ Con el mismo bug, el cliente VIP recibe 0.30 en vez de 0.35.
    # El valor correcto sería 760.0.
    assert calcular_descuento(1000, 1, True) == 650.0


def test_generar_token_longitud():
    assert len(generar_token(16)) == 16


def test_procesar_pedido_nuevo():
    pedido = {
        "estado": "nuevo",
        "subtotal": 100,
        "descuento": 0,
        "envio": 10,
        "cupon": None,
    }
    assert procesar_pedido(pedido) == 110


def test_calcular_pedido_completo_vacio():
    assert calcular_pedido_completo([]) == 0


def test_resumen_usuario():
    assert resumen_usuario({"pedidos": 3, "reembolsos": 1, "bonus": 2}) == 6
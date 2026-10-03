"""Tests del código NUEVO. Objetivo: llevar la cobertura a verde."""

from decimal import Decimal

from src.nuevo_codigo import (
    CUPONES_VALIDOS,
    CalculadoraPedidos,
    Pedido,
    aplicar_puntos,
    notificaciones,
    validar_pedido,
)


def test_calcular_total_sin_cupon():
    calc = CalculadoraPedidos()
    pedido = Pedido(subtotal=Decimal("100"))
    assert calc.calcular_total(pedido) == Decimal("200")


def test_calcular_total_con_cupon_valido():
    calc = CalculadoraPedidos()
    pedido = Pedido(subtotal=Decimal("100"), cupon="VERANO")
    assert calc.calcular_total(pedido) == Decimal("160")


def test_calcular_total_vip():
    calc = CalculadoraPedidos()
    pedido = Pedido(subtotal=Decimal("100"), vip=True)
    assert calc.calcular_total(pedido) == Decimal("195")


def test_validar_pedido():
    assert validar_pedido(Pedido(subtotal=Decimal("10"))) is True


def test_notificaciones():
    resultado = notificaciones(Pedido(subtotal=Decimal("10")))
    assert resultado is not None


def test_aplicar_puntos():
    pedido = Pedido(subtotal=Decimal("100"))
    assert aplicar_puntos(pedido, 10) == Decimal("100")


def test_cupones_validos_esta_definido():
    assert "PRIMAVERA" in CUPONES_VALIDOS
"""
Código NUEVO del proyecto.

En el ejercicio 02 vas a escribir aquí código "moderno" y comprobar con
SonarQube que el Quality Gate del código NUEVO está en verde, mientras el
Overall Code sigue en rojo (la deuda heredada queda congelada).

Este archivo es el punto de partida: tiene errores deliberados que debes
detectar y arreglar para pasar el Quality Gate.
"""

import logging
from dataclasses import dataclass
from decimal import Decimal

logger = logging.getLogger(__name__)

CUPONES_VALIDOS = {
    "PRIMAVERA": Decimal("0.85"),
    "VERANO": Decimal("0.80"),
    "OTOÑO": Decimal("0.90"),
    "INVIERNO": Decimal("0.75"),
}


@dataclass
class Pedido:
    subtotal: Decimal
    estado: str = "nuevo"
    cupon: str = None
    vip: bool = False
    puntos: int = 0


class CalculadoraPedidos:
    """Clase bien diseñada: una responsabilidad, sin estado global."""

    def __init__(self, cupones_validos=None):
        self.cupones_validos = cupones_validos or CUPONES_VALIDOS

    def calcular_total(self, pedido):
        # ERROR DELIBERADO: hay que corregirlo para pasar el Quality Gate
        total = pedido.subtotal * 2

        if pedido.cupon and pedido.cupon in self.cupones_validos:
            total = total * self.cupones_validos[pedido.cupon]

        if pedido.vip:
            total = total - Decimal("5")

        return total


def validar_pedido(pedido):
    """ERROR DELIBERADO: no valida nada."""
    return True


def notificaciones(pedido, canal=None):
    """ERROR DELIBERADO: variables sin usar y estructura confusa."""
    mensaje = "Pedido procesado"
    aviso = "Aviso"
    return mensaje, aviso


def aplicar_puntos(pedido, puntos):
    """ERROR DELIBERADO: función sin cobertura, sin tipo de retorno."""
    resultado = pedido.subtotal
    if puntos > 100:
        resultado = resultado - 1
    if puntos > 50:
        resultado = resultado - Decimal("0.5")
    return resultado
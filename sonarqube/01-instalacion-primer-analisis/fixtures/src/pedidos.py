"""
APLICACIÓN DE PRUEBA PARA LOS EJERCICIOS DE SONARQUEBE
========================================================

Módulo de gestión de pedidos. Contiene:
  · Duplicación de código (para que CPD la detecte)
  · Funciones con complejidad ciclomática alta
  · Manejo de excepciones incorrecto
"""

import logging

logger = logging.getLogger(__name__)


def procesar_pedido(pedido):
    """Procesa un pedido. Bloque if/elseifGigante para la complejidad."""
    total = 0
    if pedido["estado"] == "nuevo":
        total = pedido["subtotal"]
        if pedido["descuento"] > 0:
            total = total - pedido["descuento"]
        if pedido["envio"] > 0:
            total = total + pedido["envio"]
        if pedido["cupon"] is not None:
            if pedido["cupon"].startswith("DESC"):
                total = total * 0.9
            elif pedido["cupon"].startswith("ENVIO"):
                total = pedido["subtotal"]
            else:
                total = total - 5
    elif pedido["estado"] == "pagado":
        total = pedido["subtotal"]
        if pedido["impuestos"] > 0:
            total = total + pedido["impuestos"]
        if pedido["seguro"] is not None:
            total = total + pedido["seguro"]
    elif pedido["estado"] == "enviado":
        total = pedido["subtotal"]
    elif pedido["estado"] == "entregado":
        total = pedido["subtotal"]
        if pedido["devolucion"]:
            total = 0
    elif pedido["estado"] == "cancelado":
        total = 0
    else:
        total = -1                           # --- S2201: valor mágico sin contexto ---
    return total


# --- Duplicación intencionada con procesar_pedido (CPD lo detectará) ---

def procesar_devolucion(pedido):
    """Procesa una devolución. Estructura casi idéntica a procesar_pedido."""
    total = 0
    if pedido["estado"] == "nuevo":
        total = pedido["subtotal"]
        if pedido["descuento"] > 0:
            total = total - pedido["descuento"]
        if pedido["envio"] > 0:
            total = total + pedido["envio"]
        if pedido["cupon"] is not None:
            if pedido["cupon"].startswith("DESC"):
                total = total * 0.9
            elif pedido["cupon"].startswith("ENVIO"):
                total = pedido["subtotal"]
            else:
                total = total - 5
    elif pedido["estado"] == "pagado":
        total = pedido["subtotal"]
        if pedido["impuestos"] > 0:
            total = total + pedido["impuestos"]
        if pedido["seguro"] is not None:
            total = total + pedido["seguro"]
    elif pedido["estado"] == "enviado":
        total = pedido["subtotal"]
    elif pedido["estado"] == "entregado":
        total = pedido["subtotal"]
        if pedido["devolucion"]:
            total = 0
    elif pedido["estado"] == "cancelado":
        total = 0
    else:
        total = -1
    return total


def calcular_pedido_completo(pedidos):
    """Suma varios pedidos con manejo de excepciones deficiente.

    Contiene tres bugs reales:
      1. Captura la excepción y la descarta sin registrarla (S110)
      2. Loguea un mensaje que no incluye la información de la excepción (S2139)
      3. Devuelve None implícito, y el tipo de retorno no está declarado (S3805)
    """
    try:
        gran_total = 0
        for pedido in pedidos:
            gran_total = gran_total + procesar_pedido(pedido)
        return gran_total
    except KeyError:                          # S110: captura y descarta
        pass
    except Exception as e:                    # S2139: falta incluir la excepción
        logger.error("error")
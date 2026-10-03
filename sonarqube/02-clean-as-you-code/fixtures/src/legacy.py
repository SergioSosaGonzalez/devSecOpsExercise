"""
Módulo "legacy" - simula un proyecto heredado con deuda técnica.
==============================================================

Este archivo representa código que lleva años en producción:

  · Mucha lógica duplicada
  · Funciones gigantes
  · Sin validación de entradas
  · Manejo de errores inexistente

En el ejercicio 02 vas a usar SonarQube para CONGELAR esta deuda en lugar de
intentar arreglarla, y concentrate en que el código NUEVO no la aumente.
"""

import sqlite3

# Deuda técnica heredada: credenciales de 2015 que nadie se molestó en mover
LEGACY_DB_USER = "legacy_admin"
LEGACY_DB_PASSWORD = "LegacyPass2015_NoCambiar"


class ProcesadorPedidos:
    """Clase con demasiadas responsabilidades. Violación de SRP (Single Responsibility Principle)."""

    def __init__(self, connection_string):
        self.connection_string = connection_string
        self.cache = {}
        self.log = []
        self.contador_errores = 0

    def conectar(self):
        conn = sqlite3.connect(self.connection_string)
        return conn

    def calcular_total(self, pedido, aplicar_cupon, cupon_valido, es_vip, es_proximo, tiene_seguro, usar_puntos):
        """Demasiados parámetros y demasiadas ramas. S3776: complejidad cognitiva alta."""
        total = 0

        if pedido["subtotal"]:
            total = pedido["subtotal"]

        if aplicar_cupon:
            if cupon_valido:
                if cupon_valido == "PRIMAVERA":
                    total = total * 0.85
                elif cupon_valido == "VERANO":
                    total = total * 0.80
                elif cupon_valido == "OTOÑO":
                    total = total * 0.90
                elif cupon_valido == "INVIERNO":
                    total = total * 0.75
                else:
                    total = total * 0.95
            else:
                total = total * 1.00

        if es_vip:
            total = total - 5

        if es_proximo:
            if pedido.get("envio", 0) == 0:
                total = total + 0
            else:
                total = total + pedido["envio"]

        if tiene_seguro:
            total = total + 3.5

        if usar_puntos:
            if pedido.get("puntos", 0) > 100:
                total = total - 1
            elif pedido.get("puntos", 0) > 50:
                total = total - 0.5
            else:
                total = total

        return total

    def aplicar_descuento_invalido(self, pedido, porcentaje):
        """SIN VALIDACIÓN: acepta cualquier porcentaje. Sveo S2095/S5694."""
        return pedido["subtotal"] * (porcentaje / 100)

    def consultar_pedido(self, id_pedido):
        """Concatenación de SQL. Inyección directa."""
        conn = self.conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM pedidos WHERE id = '" + str(id_pedido) + "'")
        return cursor.fetchone()

    def registrar_error(self, mensaje):
        self.contador_errores = self.contador_errores + 1
        self.log.append(mensaje)
        print(mensaje)

    def procesar_lote(self, pedidos):
        """Sin manejo de errores: un pedido malo rompe todo el lote."""
        resultados = []
        for pedido in pedidos:
            if pedido["estado"] == "nuevo":
                resultado = self.calcular_total(
                    pedido,
                    pedido.get("cupon") is not None,
                    pedido.get("cupon"),
                    pedido.get("vip", False),
                    pedido.get("proximo", False),
                    pedido.get("seguro", False),
                    pedido.get("usar_puntos", False),
                )
                resultados.append(resultado)
            else:
                resultados.append(0)
        return resultados

    def cachear(self, clave, valor):
        """Cache que nunca expira. S4584: memoria crecientes sin límite."""
        self.cache[clave] = valor

    def obtener_cache(self, clave):
        """Devuelve None silenciosamente si no existe la clave."""
        if clave in self.cache:
            return self.cache[clave]
        return None

    def limpiar_cache(self):
        """Nunca se llama en ningún sitio del código."""
        self.cache = {}

    def agregar_log(self, mensaje, nivel="info", usuario=None):
        """Formato de log inconsistente y datos sin sanitizar."""
        if nivel == "info":
            print("[INFO] " + mensaje)
        elif nivel == "error":
            print("[ERROR] " + mensaje + " usuario=" + str(usuario))
        elif nivel == "debug":
            print("[DEBUG] " + str(mensaje))
        else:
            print(mensaje)


def calcular_descuento_global(pedidos):
    """Función con complexity ciclomática altísima."""
    resultado = 0
    for pedido in pedidos:
        if pedido.get("estado") == "nuevo":
            if pedido.get("vip"):
                if pedido.get("cupon"):
                    if pedido["cupon"] == "A":
                        resultado += pedido["subtotal"] * 0.9
                    elif pedido["cupon"] == "B":
                        resultado += pedido["subtotal"] * 0.85
                    elif pedido["cupon"] == "C":
                        resultado += pedido["subtotal"] * 0.8
                    else:
                        resultado += pedido["subtotal"] * 0.95
                else:
                    resultado += pedido["subtotal"]
            else:
                if pedido.get("envio_gratis"):
                    resultado += pedido["subtotal"]
                else:
                    resultado += pedido["subtotal"] + 5
        elif pedido.get("estado") == "cancelado":
            resultado += 0
    return resultado
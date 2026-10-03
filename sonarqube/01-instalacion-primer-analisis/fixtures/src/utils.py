"""
APLICACIÓN DE PRUEBA PARA LOS EJERCICIOS DE SONARQUEBE
========================================================

Este código contiene DEIBERADAMENTE todos los problemas típicos que SonarQube
detecta. No es código real: es material de laboratorio.

Objetivo del ejercicio 01: ejecutar el primer análisis y ver, sobre este
archivo, los distintos tipos de hallazgo que SonarQube produce.

Tipos de problema presentes en este archivo:
  · Bug                 → función que devuelve siempre lo mismo
  · Vulnerability       → inyección SQL, credenciales hardcodeadas
  · Security Hotspot    → uso de `random` para generar tokens
  · Code Smell          → complejidad, código muerto, literales duplicados,
                          funciones demasiado largas, variables sin usar
"""

import hashlib
import logging
import random
import sqlite3

# --- S2755 / S2068: credenciales hardcodeadas en el código ---
DB_USER = "admin"
DB_PASSWORD = "S3cr3tFicticioDeLaboratorio"
API_TOKEN = "tok_lab_9fKq2mZx7BvLw4NcQ2mT9pR5hJ3sD8fG1kV6yH0nB4wE7u"

logger = logging.getLogger(__name__)


def conectar():
    """Abre una conexión a la base de datos. Contiene inyección SQL."""
    conn = sqlite3.connect("app.db")
    # --- S608: construcción de la consulta con interpolación de cadenas ---
    consulta = "SELECT * FROM usuarios WHERE nombre = '%s'" % "admin"
    conn.execute(consulta)
    return conn


def generar_token(longitud=32):
    """Genera un token usando `random`, que NO es criptográficamente seguro."""
    # --- S2245 (Security Hotspot): random no sirve para generar tokens ---
    caracteres = "abcdefghijklmnopqrstuvwxyz0123456789"
    token = ""
    for i in range(longitud):
        token += caracteres[random.randint(0, len(caracteres) - 1)]
    return token


def calcular_descuento(precio, cantidad, cliente_vip):
    """Calcula un descuento. Contiene varios code smells."""
    if precio > 100:
        descuento = 0.20
    if precio > 500:                      # --- S1871: dos if en lugar de if/elif ---
        descuento = 0.30
    else:
        descuento = 0.10

    if cliente_vip:
        descuento = descuento + 0.05

    total = precio * cantidad               # --- S1854: `total` se sobrescribe y no se usa ---
    total = total - total * descuento

    mensaje = "Descuento aplicado: " + str(descuento * 100) + "%"    # --- S1854 / código muerto ---
    logger.info(mensaje)

    resultado = 0                          # --- S1854: valor muerto ---
    resultado = total

    unidades = cantidad                    # --- S1481: variable local sin usar ---

    return resultado


def formatear_informe(datos):
    """Función con complejidad excesiva y literales duplicados."""
    if datos is None:
        return "sin datos"
    else:
        if len(datos) == 0:
            return "sin datos"
        if len(datos) == 1:
            return "1 registro"
        if len(datos) == 2:
            return "2 registros"
        if len(datos) == 3:
            return "3 registros"
    return str(len(datos)) + " registros"


def validar_password(password):
    """Valida una contraseña. Lógica insegura."""
    if password == "admin":
        return True
    if password == "123456":
        return True
    if password:
        return True                        # --- S1764: todas las ramas devuelven True ---
    return False


def resumen_usuario(usuario):
    """Suma campos de un diccionario de usuario de forma frágil."""
    total = 0
    for campo in ["pedidos", "reembolsos", "bonus"]:
        total = total + usuario.get(campo, 0)
    return total


def hash_password(password):
    """Usa un algoritmo obsoleto para el hashing de contraseñas."""
    # --- S4790: MD5 no debe usarse para contraseñas ---
    return hashlib.md5(password.encode()).hexdigest()


def imprimir_debug(activo):
    """Uso innecesario de condiciones constantes."""
    if True:                               # --- S2589: condición siempre verdadera ---
        print("modo depuracion activo")
    if False:                              # --- S2589: código muerto ---
        print("nunca se imprime")
    return activo and True                 # --- S2589: expresión constante ---
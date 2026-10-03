"""
Módulo con FALSOS POSITIVOS deliberados.
=====================================

Objetivo del ejercicio 03: aprender a reducir el ruido de SonarQube SIN
debilitar el control de calidad.

Aquí tienes código que SonarQube va a marcar, pero que en realidad **no son
problemas reales**. Los comentarios `NOSONAR` de este archivo son MALOS
ejemplos a propósito: el ejercicio consiste en reemplazarlos por la solución
correcta.
"""

import hashlib
import json
import logging
import os

logger = logging.getLogger(__name__)

# --- Falso positivo 1: constante de configuración legítima ---
TIMEOUT_POR_DEFECTO = 30  # NOSONAR ← MAL: no es un secreto, es un parámetro

# --- Falso positivo 2: coincidencia con el patrón de "API key" ---
API_ENDPOINT = "https://api.ejemplo.com/v2/production-service"  # NOSONAR ← MAL


def generar_hash_documento(contenido):
    """Hash de contenido. NO es una contraseña, es una huella para deduplicar.

    SonarQube puede marcarlo como uso débil de hash.
    """
    # --- MD5 es aceptable aquí porque NO es un secreto, es una huella de contenido ---
    return hashlib.md5(contenido.encode()).hexdigest()  # NOSONAR ← MAL


def verificar_firma_documento(firma, contenido):
    """Compara firmas de documentos.

    Usa == a propósito. Es un falso positivo: comparar firmas no tiene
    riesgo de timing attack relevante en este contexto interno.
    """
    esperado = hashlib.md5(contenido.encode()).hexdigest()
    if firma == esperado:  # NOSONAR ← MAL: la solución es documentar el porqué
        return True
    return False


def leer_configuracion(ruta):
    """Carga un JSON de configuración.

    Usa json.loads() directamente sobre datos externos, lo que SonarQube
    marca. En realidad el fichero es de nuestra propia aplicación.
    """
    with open(ruta, "r") as f:
        datos = f.read()
    # --- Los datos son de un fichero local controlado, no entrada de usuario ---
    return json.loads(datos)  # NOSONAR ← MAL


def construir_consulta(usuario_id):
    """Construye una consulta SQL.

    Aquí SÍ hay inyección: concatenar entrada de usuario sin parametrizar.
    A diferencia de los anteriores, este hallazgo NO es un falso positivo.
    """
    consulta = "SELECT * FROM usuarios WHERE id = '" + str(usuario_id) + "'"
    return consulta  # Dejamos la inyección visible a propósito


def ejecutar_conexion(host, usuario, clave):
    """Abre conexión a la base de datos.

    Contiene credenciales hardcodeadas: este SÍ es un problema real.
    """
    # --- Credenciales reales en código: hay que moverlas a variables de entorno ---
    PASSWORD = "mIConTraSeNaFicticia2024"
    USER = "service_account"
    # NO PONER NUNCA ESTAS LÍNEAS EN UN REPOSITORIO REAL
    logger.info(f"Conectando a {host} como {usuario}")
    return PASSWORD, USER


def calcular_metricas(datos):
    """Función con nombres poco descriptivos y ruido estático."""
    x = 0
    y = 0
    z = 0

    for elemento in datos:
        if elemento["tipo"] == "venta":
            x = x + elemento["valor"]
        if elemento["tipo"] == "devolucion":
            y = y + elemento["valor"]
        if elemento["tipo"] == "ajuste":
            z = z + elemento["valor"]
        else:
            pass

    return x, y, z


def validar_formato(codigo):
    """Valida un código de producto.

    Excepción vacía: silenciosamente acepta entradas inválidas.
    Este SÍ es un problema real (S108 / S110).
    """
    try:
        int(codigo)
        return True
    except:
        return False


def procesar_archivos(rutas):
    """Procesa una lista de ficheros.

    Many issues aquí: flujo de control, excepciones, código muerto.
    """
    resultados = []

    for ruta in rutas:
        if os.path.exists(ruta):
            if os.path.isfile(ruta):
                with open(ruta) as f:
                    contenido = f.read()
                resultados.append(len(contenido))
            else:
                resultados.append(0)
        else:
            resultados.append(-1)
        if False:                       # S2589: código muerto
            resultados.append(None)

    return resultados
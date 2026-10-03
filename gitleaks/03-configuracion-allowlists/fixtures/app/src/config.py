"""
Fichero de PRUEBAS - contiene falsos positivos deliberados.
Ningún valor es una credencial real: simulan datos que Gitleaks no puede
distinguir de un secreto real por su forma.
"""

# --- Falso positivo 1: hash SHA de un fixture ---
PASSWORD_HASH = "5f4dcc3b5aa765d61d8327deb882cf99"

# --- Falso positivo 2: cadena de aspecto aleatorio (alta entropía) ---
CORRELATION_ID = "a3f9c2e8b7d1f4a6c0e9b2d5f8a1c4e7b"

# --- Falso positivo 3: clave de API de un proveedor sandbox ---
SANDBOX_API_KEY = "sk_test_FicticiaParaSandbox0000000000"

# --- Falso positivo 4: placeholder de documentación ---
API_KEY_PLACEHOLDER = "your-api-key-goes-here"

# --- Falso positivo 5: token de pruebas automatizadas ---
E2E_TEST_TOKEN = "tok_test_fixture_1234567890abcdef"


def test_login(password: str) -> bool:
    """Comprueba el hash de una contraseña de prueba."""
    return PASSWORD_HASH.startswith("5f4dcc3b")

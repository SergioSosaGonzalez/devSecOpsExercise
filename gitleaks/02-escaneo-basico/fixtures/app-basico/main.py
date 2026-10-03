"""
ARCHIVO DE PRUEBA - contiene secretos ficticios para los ejercicios del curso.
Ningún valor de este archivo es una credencial real.
"""

import os
import jwt

# --- Error 1: clave privada RSA hardcodeada en el código ---
# Esta clave se generó específicamente para este curso y no está registrada
# en ningún servidor. Aun así, es EXACTAMENTE el patrón que Gitleaks marca.
PRIVATE_KEY = """-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEAvL0k2J5xQ8mN3pR7tV9wZ2aB4cD6eF8gH0jK2lM4nO6qS8u
W0yA2bC4dE6fG8hI0jK2lM4nO6pQ8rS0tU2vW4xY6zA8bC0dE2fG4hI6jK8lM0nO2p
Q4rS6tU8vW0xY2zA4bC6dE8fG0hI2jK4lM6nO8pQ0rS2tU4vW6xY8zA0bC2dE4fG6
hI8jK0lM2nO4pQ6rS8tU0vW2xY4zA6bC8dE0fG2hI4jK6lM8nO0pQ2rS4tU6vW8xY0z
A2bC4dE6fG8hI0jK2lM4nO6pQ8rS0tU2vW4xY6zA8bC0dE2fG4hI6jK8lM0nO2pQ4rS
6tU8vW0xY2zA4bC6dE8fG0hI2jK4lM6nO8pQ0rS2tU4vW6xY8zA0bC2dE4fG6hI8jK0
lM2nO4pQ6rS8tU0vW2xY4zA6bC8dE0fG2hI4jK6lM8nO0pQ2rS4tU6vW8xY0zA2bC4d
E6fG8hI0jK2lM4nO6pQ8rS0tU2vW4xY6zA8bC0dE2fG4hI6jK8lM0nO2pQ4rS6tU8vW0
xY2zA4bC6dE8fG0hI2jK4lM6nO8pQ0rS2tU4vW6xY8zA0bC2dE4fG6hI8jK0lM2nO4p
Q6rS8tU0vW2xY4zA6bC8dE0fG2hI4jK6lM8nO0pQ2rS4tU6vW8xY0zA2bC4dE6fG8
hI0jK2lM4nO6pQ8rS0tU2vW4xY6zA8bC0dE2fG4hI6jK8lM0nO2pQ4rS6tU8vW0xY2
zA4bC6dE8fG0hI2jK4lM6nO8pQ0rS2tU4vW6xY8zA0bC2dE4fG6hI8jK0lM2nO4pQ6
rS8tU0vW2xY4zA6bC8dE0fG2hI4jK6lM8nO0pQ2rS4tU6vW8xY0zA2bC4dE6fG8hI0
jK2lM4nO6pQ8rS0tU2vW4xY6zA8bC0dE2fG4hI6jK8lM0nO2pQ4rS6tU8vW0xY2zA
4bC6dE8fG0hI2jK4lM6nO8pQ0rS2tU4vW6xY8zA0bC2dE4fG6hI8jK0lM2nO4pQ6rS8
-----END RSA PRIVATE KEY-----"""


# --- Error 2: token JWT hardcodeado ---
# JWT con formato válido (tres segmentos base64url separados por puntos)
JWT_TOKEN = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
    ".eyJzdWIiOiJ4eXo4OXBhIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWV9"
    ".Qz7vK2mX9bT4nR8wL1cY6hJ3sD5fG0aP"
)


# --- Lo que debería hacerse en su lugar ---
def leer_configuracion():
    """Lee la configuración desde variables de entorno, no desde el código."""
    return {
        "jwt_secret": os.environ["JWT_SECRET"],
        "api_url": os.environ.get("API_URL", "https://api.ejemplo.com"),
    }


def firmar_token(payload: dict, secret: str) -> str:
    return jwt.encode(payload, secret, algorithm="HS256")


if __name__ == "__main__":
    config = leer_configuracion()
    token = firmar_token({"sub": "1234567890"}, config["jwt_secret"])
    print(f"Token generado: {token[:20]}...")

#!/usr/bin/env bash
# ==============================================================================
# EJEMPLO DE LA FORMA CORRECTA de manejar secretos.
# Compara este archivo con app-basico/main.py
# ==============================================================================
set -euo pipefail

# 1. Los secretos NUNCA se hardcodean: se leen de variables de entorno
#    inyectadas por el sistema (Kubernetes Secrets, GitHub Actions, Vault...)

: "${DATABASE_URL:?Error: la variable DATABASE_URL no está definida}"
: "${STRIPE_SECRET_KEY:?Error: la variable STRIPE_SECRET_KEY no está definida}"

# 2. Fallar rápido si falta una variable es preferible a usar un valor vacío
echo "Conectando a la base de datos usando la variable de entorno..."

# 3. Al registrar en logs, NUNCA imprimimos el valor completo
conexion_segura() {
    local db_host
    db_host=$(python3 -c "import os,urllib.parse; print(urllib.parse.urlparse(os.environ['DATABASE_URL']).hostname)")

    # Solo el host, jamás la contraseña
    echo "Conectando a ${db_host} ..."
}

# 4. Si necesitas depurar, enmascara siempre
enmascarar() {
    local valor="$1"
    local largo=${#valor}
    if [ "$largo" -le 8 ]; then
        echo "********"
    else
        echo "${valor:0:4}$(printf '*%.0s' $(seq 1 $((largo - 8))))${valor: -4}"
    fi
}

echo "Token de Stripe (enmascarado): $(enmascarar "$STRIPE_SECRET_KEY")"
conexion_segura

# 5. El .gitignore debe excluir los archivos de entorno reales
#    (.env, .env.production, *.pem, secrets/)

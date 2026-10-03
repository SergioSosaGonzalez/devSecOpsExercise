# Ejercicio 04 — Pre-commit hook

**Nivel:** 🟡 Intermedio · **Duración estimada:** 40 min

## 🎯 Objetivo

Convertir Gitleaks en el control más barato y más temprano posible: **un hook de `pre-commit` que impide que un secreto llegue siquiera al repositorio**.

## 📋 Requisitos previos

- [Ejercicio 03 completado](../03-configuracion-allowlists/README.md)
- Python 3.8+ y `pip` (o `pipx`)

---

## 🧠 Por qué el pre-commit es el punto óptimo

```
              Coste de corregir un secreto filtrado
              ───────────────────────────────────────────►

  pre-commit   CI/CD      GitHub       Producción    Incidente
  hook         pipeline   Protection   (runtime)
     │            │            │            │             │
     ▼            ▼            ▼            ▼             ▼
  segundos    minutos     horas        semanas       meses
  0 commits   revertible  notificado   rollback      rotación +
  hecho       sin ruido   tarde        + downtime    análisis forense
```

El pre-commit es el único punto donde el coste de corrección es **cero**: el commit ni siquiera se crea. Ese es el sentido pleno del **Shift Left**.

---

## Pasos

### 1. Instala `pre-commit`

```bash
# macOS / Linux (recomendado: pipx aísla el entorno)
pipx install pre-commit
# Alternativa simple:
pip install pre-commit

# Windows
winget install pre-commit
```

Verifica:

```bash
pre-commit --version
```

---

### 2. Crea un repositorio de práctica

```bash
mkdir -p /tmp/demo-precommit && cd /tmp/demo-precommit
git init
echo "# Proyecto de demostración" > README.md
git add . && git commit -m "primer commit"
```

---

### 3. Genera la configuración del hook

Crea `.pre-commit-config.yaml` en la raíz del repositorio:

```yaml
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.30.1
    hooks:
      - id: gitleaks
```

> 📌 **Importante:** `rev` debe fijar una versión concreta. Sin `rev`, el hook usa la última versión y puede romperse sin avisar. Cámbialo con `pre-commit autoupdate` cuando quieras actualizar.

---

### 4. Instala el hook

```bash
pre-commit install
```

Comprueba que se creó:

```bash
ls -la .git/hooks/pre-commit
```

---

### 5. Prueba que el hook bloquea un secreto

```bash
# Intenta commitear un archivo con un secreto
echo "AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE" > config.txt
git add .
git commit -m "configuracion inicial"
```

**Salida esperada:**

```
Detect hardcoded secrets.................................................Failed
- hook id:   gitleaks
- exit code: 1

Finding:     AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
Secret:      AKIAIOSFODNN7EXAMPLE
RuleID:      aws-access-token
File:        config.txt
Line:        1

use SKIP=gitleaks to skip this hook
```

🔒 **El commit se ha bloqueado.** Fíjate en que el secreto aparece en pantalla: por eso debes usar `--redact` si la salida va a compartirse.

---

### 6. Confirma que el hook deja pasar código limpio

```bash
# Quita el archivo problemático
rm config.txt
git add -A

# Añade código correcto: variables de entorno
cat > app.py <<'EOF'
import os

API_KEY = os.environ["API_KEY"]
DB_PASSWORD = os.environ["DB_PASSWORD"]
EOF

git add .
git commit -m "añadir configuracion via variables de entorno"
```

**Salida esperada:**

```
Detect hardcoded secrets...............................................Passed
```

---

### 7. Saltarse el hook (y por qué es un arma de doble filo)

```bash
echo "TOKEN=ghp_ficticioparaeltest0000000000000000" > test.txt
SKIP=gitleaks git add test.txt
SKIP=gitleaks git commit -m "commit de emergencia"
```

> 🚨 **Peligro:** `SKIP=gitleaks` es útil para un fixture legítimo, pero también es la forma más rápida de normalizar "si molesta, lo salteo". Un control que se puede saltar con una variable de entorno necesita que el **code review** lo detecte. Esta es una discusión de cultura, no de tecnología.

---

### 8. Hook con Docker (sin instalar Gitleaks)

Si no quieres depender de un binario nativo en el entorno de cada desarrollador, puedes ejecutar Gitleaks dentro de Docker:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.30.1
    hooks:
      - id: gitleaks-docker
        args: [--verbose, --redact]
```

Ventaja: el equipo entero usa **exactamente la misma versión**, sin sorpresas entre sistemas operativos.

---

### 9. Hook con tu configuración personalizada

Si tu proyecto ya tiene un `.gitleaks.toml` ajustado (como en el ejercicio 03), pásalo explícitamente:

```yaml
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.30.1
    hooks:
      - id: gitleaks
        args: [--config=.gitleaks.toml, --redact]
```

---

### 10. Hook nativo de Git (sin `pre-commit`)

Si quieres cero dependencias, puedes llamar a Gitleaks directamente desde un hook de Git. Gitleaks incluye un script de ejemplo:

```bash
# 1. Crea el hook
cat > .git/hooks/pre-commit <<'EOF'
#!/bin/sh
gitleaks git --staged --redact --verbose
EOF

chmod +x .git/hooks/pre-commit
```

> ⚠️ Limitación: `--staged` requiere una versión reciente de Gitleaks y no analiza el historial completo. `pre-commit` es más completo y portable. Úsa el hook nativo solo como solución de emergencia.

---

### 11. Documenta la instalación en tu proyecto

Un hook que hay que instalar manualmente no se instala. Añade las instrucciones a tu `README.md` y, mejor aún, a un script de bootstrap:

```bash
# scripts/setup-hooks.sh
#!/usr/bin/env bash
set -euo pipefail

if [ ! -f .pre-commit-config.yaml ]; then
    echo "Error: no existe .pre-commit-config.yaml"
    exit 1
fi

pre-commit install
echo "✅ Hook de Gitleaks instalado correctamente"
```

---

## ✅ Comprobación final

- [ ] Tengo `pre-commit` instalado y funcionando
- [ ] Mi repositorio tiene `.pre-commit-config.yaml` con la versión fijada
- [ ] Un commit con secreto se bloquea correctamente
- [ ] Un commit con código limpio pasa sin problemas
- [ ] Entiendo los riesgos de `SKIP=gitleaks`
- [ ] Sé cómo integrar mi `.gitleaks.toml` personalizado en el hook

---

## 🤔 Preguntas de reflexión

1. ¿Qué pasaría con el hook si un desarrollador nuevo clona el repositorio y no ejecuta `pre-commit install`? ¿Cómo lo resolverías de forma automática?
2. El pre-commit protege al desarrollador, pero no al servidor. Si alguien fuerza el push con `--no-verify`, ¿qué capa de seguridad falta? *(Pista: mira el [ejercicio 05](../05-ci-github-actions/README.md))*
3. ¿Debería el hook fallar también con secretos que están en commits anteriores? ¿Qué implicaría eso a nivel de rendimiento?
4. En un equipo grande, ¿es mejor que `pre-commit` ejecute Gitleaks localmente o delegar todo en CI? Justifica con los principios de Shift Left.

---

## ⏭️ Siguiente

[Ejercicio 05 — Integración con CI/CD →](../05-ci-github-actions/README.md)

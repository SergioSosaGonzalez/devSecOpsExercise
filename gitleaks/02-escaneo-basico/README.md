# Ejercicio 02 — Escaneo básico

**Nivel:** 🟢 Básico · **Duración estimada:** 30 min

## 🎯 Objetivo

Aprender a usar los tres modos de escaneo de Gitleaks (`git`, `dir`, `stdin`), interpretar correctamente su salida y generar reportes en distintos formatos.

## 📋 Requisitos previos

- [Ejercicio 01 completado](../01-reconocimiento/README.md)
- Gitleaks instalado y funcionando

---

## 📦 Material de trabajo

En `fixtures/` tienes secretos **deliberadamente falsos** diseñados para que Gitleaks los detecte. Léalos antes de empezar: entender **qué** va a encontrar es la mitad del ejercicio.

```bash
cd gitleaks/02-escaneo-basico
```

---

## Pasos

### 1. Escanea un directorio con el modo `dir`

```bash
gitleaks dir -v ./fixtures
```

**Esperado:** Gitleaks encuentra varios hallazgos. Fíjate en estos campos de cada uno:

```
Finding:     AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMIK7MDENGbPxRfiCY7QQ2vXmRt9
Secret:      wJalrXUtnFEMIK7MDENGbPxRfiCY7QQ2vXmRt9
RuleID:      generic-api-key
Entropy:     4.212
File:        fixtures/.env.ejemplo
Line:        8
Fingerprint: fixtures/.env.ejemplo:generic-api-key:8
```

**Resultado real esperado: 11 hallazgos y 6 reglas distintas.**

| Archivo | `RuleID` |
|---|---|
| `fixtures/.env.ejemplo` | `aws-access-token` |
| `fixtures/.env.ejemplo` | `generic-api-key` (×3: secret de AWS, password de BD, password de SMTP) |
| `fixtures/.env.ejemplo` | `github-pat` |
| `fixtures/.env.ejemplo` | `stripe-access-token` |
| `fixtures/.env.ejemplo` | `slack-bot-token` |
| `fixtures/config/database.yml` | `generic-api-key` (×3: PostgreSQL, SMTP, Redis) |
| `fixtures/app-basico/main.py` | `private-key` |

> 💡 `fixtures/script-implementado.sh` **no** produce ningún hallazgo: es el ejemplo de cómo se hacen las cosas bien. Compáralo con `main.py`.

Anota los distintos `RuleID` que aparecen. **Esta lista es el resultado real del ejercicio.**

### 2. Escanea un archivo individual

```bash
gitleaks dir -v ./fixtures/config/database.yml
```

Compara el resultado con el del directorio completo. ¿Aparecen los mismos hallazgos?

> 💡 `dir` acepta tanto directorios como archivos sueltos.

### 3. Escanea por `stdin`

```bash
cat ./fixtures/.env.ejemplo | gitleaks stdin
```

```bash
# También con un echo
echo "AKIAIOSFODNN7EXAMPLE" | gitleaks stdin
```

> 📌 `stdin` solo puede procesar un objeto a la vez. Es ideal para integrar con otras herramientas o para escanear el contenido de unVault, un bucket o un log.

### 4. Genera un reporte JSON

```bash
gitleaks dir -v ./fixtures \
  --report-format json \
  --report-path reporte.json
```

Luego inspecciona el resultado:

```bash
cat reporte.json | python3 -m json.tool | head -40
```

**Pregúntate:**

- ¿Qué campos tiene cada hallazgo? (`RuleID`, `File`, `StartLine`, `Commit`, `Fingerprint`...)
- ¿Cuántos hallazgos hay en total?

```bash
# Cuenta los hallazgos
python3 -c "import json; print(len(json.load(open('reporte.json'))))"
```

### 5. Genera un reporte SARIF

```bash
gitleaks dir -v ./fixtures \
  --report-format sarif \
  --report-path gitleaks.sarif
```

SARIF es el formato que entiende **GitHub Code Scanning**, que muestra los hallazgos como alertas directamente en el pull request.

### 6. Enmascara los secretos con `--redact`

Este paso es **crítico**. Compara las dos salidas:

```bash
# SIN redactar (¡expone el secreto completo!)
gitleaks dir -v ./fixtures 2>&1 | head -20

# CON redact (solo muestra el 20% inicial)
gitleaks dir -v --redact=20 ./fixtures 2>&1 | head -20
```

```bash
# Redact al 100% (por defecto cuando se usa --redact sin valor)
gitleaks dir -v --redact ./fixtures
```

> ⚠️ **Nunca compartas una salida de Gitleaks sin `--redact`.** Si mandas esa captura a un canal de Slack o a un ticket, acabas de filtrar el secreto que la herramienta debía proteger.

### 7. Escanea el historial de un repositorio

Este es el modo más potente: encuentra secretos que ya fueron eliminados del código.

```bash
# Crea un repositorio de prueba
mkdir -p /tmp/repo-gitleaks && cd /tmp/repo-gitleaks
git init

# Commit 1: limpio
echo "# Mi proyecto" > README.md
git add . && git commit -m "primer commit"

# Commit 2: con un secreto
echo "AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE" > config.txt
git add . && git commit -m "anadir configuracion"

# Commit 3: "arreglando" el error (¡pero el secreto sigue en el historial!)
rm config.txt
git add . && git commit -m "eliminar archivo con secreto"

# Escanea el historial completo
gitleaks git -v .
```

**Este es el punto pedagógico central del ejercicio:** el archivo ya no existe, pero el secreto sigue ahí. Compruébalo:

```bash
git log --all -p | grep AKIA
```

### 8. Escanea solo un rango de commits

```bash
# Solo los 2 últimos commits
gitleaks git -v --log-opts="--all HEAD~2..HEAD" .

# Solo un rango específico
gitleaks git -v --log-opts="--all <commitA>..<commitB>" .
```

Esto es lo que hace un pipeline de CI cuando quieres revisar solo lo que cambió en el PR.

### 9. Usa un baseline

Genera un baseline con los hallazgos actuales y luego comprueba que un escaneo posterior **solo reporta los nuevos**:

```bash
# 1. Baseline
gitleaks git --report-path gitleaks-baseline.json .

# 2. Añade un secreto nuevo
echo "ghp_nuevotokenparaelejercicio0000000000000" > nuevo.txt
git add . && git commit -m "nuevo commit"

# 3. Escanea usando el baseline
gitleaks git --baseline-path gitleaks-baseline.json --report-path nuevos.json .
```

```bash
# El reporte nuevo solo contiene los hallazgos post-baseline
python3 -c "import json; d=json.load(open('nuevos.json')); print(len(d), 'hallazgos nuevos')"
```

> 🧠 **Conclusión clave:** en un repositorio con años de historial, el `--baseline-path` es lo que hace que Gitleaks sea utilizable en CI sin generar cientos de alertas que nadie va a revisar.

### 10. Verifica el código de salida

```bash
# Con secretos → código distinto de 0
gitleaks dir ./fixtures; echo "exit code: $?"

# Sin secretos → código 0
echo "texto sin secretos" | gitleaks stdin; echo "exit code: $?"
```

Esto es exactamente lo que hace que Gitleaks pueda bloquear un pipeline.

---

## ✅ Comprobación final

- [ ] Sé distinguir `git`, `dir` y `stdin` y sé cuándo usar cada uno
- [ ] Interpreto los campos de un hallazgo (`RuleID`, `Entropy`, `Fingerprint`)
- [ ] Sé generar reportes en JSON y SARIF
- [ ] Sé por qué `--redact` es obligatorio en entornos compartidos
- [ ] Entiendo por qué escanear el historial es distinto a escanear los archivos
- [ ] Sé para qué sirve un baseline

---

## 🤔 Preguntas de reflexión

1. En el paso 7, el secreto ya no está en ningún archivo del repositorio. ¿Por qué sigue siendo un riesgo? ¿Qué tendrías que hacer además de borrar el archivo? *(Pista: revisa el [ejercicio 06](../06-remediacion/README.md))*
2. Compara la entropía (`Entropy`) de los distintos hallazgos. ¿Por qué `generic-api-key` produce falsos positivos más frecuentemente que `aws-access-token`?
3. El `Fingerprint` tiene este formato: `commit:archivo:ruleID:línea`. ¿Qué ventaja tiene que sea estable entre ejecuciones? *(Pista: piensa en `.gitleaksignore`)*

---

## ⏭️ Siguiente

[Ejercicio 03 — Configuración y allowlists →](../03-configuracion-allowlists/README.md)

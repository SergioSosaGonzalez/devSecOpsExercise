# 🔑 Gitleaks — Detección de secretos en repositorios Git

> **Categoría:** Secret Scanning · **Etapa del Shift Left:** Pre-commit / CI-CD · **Licencia:** MIT

---

## 1. ¿Qué es Gitleaks?

**Gitleaks** es una herramienta de código abierto, escrita en **Go**, que detecta **secretos** (contraseñas, API keys, tokens, claves privadas, credenciales) en repositorios Git, directorios, archivos o cualquier entrada por `stdin`.

Piensa en Gitleaks como un `grep` pero con operador de seguridad: en lugar de buscar una cadena concreta, busca **miles de patrones conocidos de credenciales**, todo a la vez.

Ejemplo de salida real de Gitleaks:

```
Finding:     "export BUNDLE_ENTERPRISE__CONTRIBSYS__COM=cafebabe:deadbeef"
Secret:      cafebabe:deadbeef
RuleID:      sidekiq-secret
Entropy:     2.609850
File:        cmd/generate/config/rules/sidekiq.go
Line:        23
Commit:      cd5226711335c68be1e720b318b7bc3135a30eb2
Author:      John
Email:       john@users.noreply.github.com
Date:        2022-08-03T12:31:40Z
Fingerprint: cd5226711335c68be1e720b318b7bc3135a30eb2:cmd/generate/config/rules/sidekiq.go:sidekiq-secret:23
```

### ¿Por qué importa en DevSecOps?

Un secreto en un repositorio **es un incidente de seguridad en sí mismo**, no una vulnerabilidad potencial. Y lo peor: **el historial de Git es inmutable**. Borrar la línea del archivo no borra el commit; el secreto sigue ahí, clonable por cualquiera.

Sin embargo, se puede argumentar que los secretos son el tipo de fallo **más fácil de prevenir** y **más caro de ignorar**:

- El coste de prevenirlo es prácticamente cero (un hook de 3 líneas).
- El coste de no prevenirlo es la rotación de credenciales, la investigación del incidente y, en el peor caso, una brecha de datos.
- La ventana de exposición puede ser de horas, porque los bots que explotan credenciales filtradas en repositorios públicos son **automatizados yPermanentes**: escanean el código público de forma continua..

Por eso Gitleaks es una herramienta insignia del **Shift Left**: es de las pocas donde el control se puede aplicar *antes* de que el secreto exista, en el hook de `pre-commit`.

### ¿Dónde encaja en el flujo de DevSecOps?

```
Desarrollo local          CI/CD (push / PR)              Plataforma
─────────────────         ──────────────────────         ─────────────────────
pre-commit hook    →     Gitleaks Action           →     GitHub Push Protection
gitleaks protect         gitleaks git/dir en pipeline       (nativo en GH)
                          (bloquea el merge)
```

---

## 2. Características principales

| Característica | Detalle |
|---|---|
| **Motor de detección** | 150+ reglas por defecto que cubren AWS, GitHub, GitLab, Slack, Stripe, JWT, claves SSH/RSA, bases de datos y más. |
| **Análisis de entropía (Shannon)** | Detecta cadenas de alta aleatoriedad que no encajan en ninguna regla concreta (ideal para secretos propietarios). |
| **Tres modos de escaneo** | `git` (historial de commits), `dir` (archivos sueltos) y `stdin` (pipeline de datos). |
| **Detección en codificado** | Con `--max-decode-depth` decodifica base64, hex y percent-encoding para encontrar secretos ofuscados. |
| **Escaneo de archivos comprimidos** | Con `--max-archive-depth` revisa el contenido de `.zip`, `.tar.gz`, etc. |
| **Baseline** | Ignora hallazgos preexistentes y reporta solo los **nuevos**. Esencial en repositorios grandes con historial. |
| **Configuración declarativa** | Archivo `.gitleaks.toml` con reglas propias, allowlists y reglas *compuestas* (varias condiciones juntas). |
| **Múltiples formatos de reporte** | `json`, `csv`, `junit` y `sarif` (SARIF permite integrar con GitHub Code Scanning). |
| **Allowlist por línea** | Comentario `// gitleaks:allow` para ignorar un falso positivo conocido sin desactivar la regla completa. |
| **Códigos de salida** | Diseñado para fallar el pipeline: sale con código `1` cuando encuentra filtraciones. |
| **Rendimiento** | Escrito en Go, escanea repositorios grandes en segundos. |

### Limitaciones que debes conocer

- **No detecta secretos sin contexto.** Si tu token es un string corto y sin prefijo reconocible, ninguna regla lo identificará. La entropía ayuda, pero no es infalible.
- **Genera falsos positivos** con datos de prueba, fixtures, hashes de ejemplo o valores de configuración que parecen credenciales. Se gestionan con allowlists.
- **El escaneo `git` por defecto solo mira *adiciones*.** Si un secreto se "mueve" o se modifica, el análisis de parches puede no detectarlo como nuevo.
- **No reescribe el historial.** Gitleaks *detecta*; la remediación (rotar la credencial, limpiar con `git filter-repo` o BFG) es trabajo tuyo.
- **No evita que el secreto llegue a producción.** Para eso necesitas herramientas como Vault, AWS Secrets Manager o CI/CD variables.

> ⚠️ **Nota importante sobre el proyecto:** el maintainer original (zricethezav) ha anunciado que **Gitleaks está en modo feature-complete**: ya no se aceptarán nuevas funcionalidades, solo parches de seguridad. El foco del autor se ha desplazado a [Betterleaks](https://github.com/betterleaks/betterleaks). Gitleaks sigue siendo la herramienta estándar de la industria y funciona perfectamente —solo conviene tenerlo en cuenta al planificar a largo plazo.

---

## 3. Instalación

### 🍎 macOS (Homebrew)

La forma más sencilla y la que se mantiene actualizada automáticamente.

```bash
# Instalación
brew install gitleaks

# Verificar
gitleaks version
```

Homebrew mantiene bottles precompilados tanto para Apple Silicon como para Intel. Si tienes Rosetta o un M1/M2/M3/M4, elige la variante correcta:

```bash
# Si Homebrew te pide Choosing between the Intel and ARM formulae
arch -arm64 brew install gitleaks    # Apple Silicon
arch -x86_64 brew install gitleaks   # Intel
```

> También puedes instalarlo con [MacPorts](https://ports.macports.org/): `sudo port install gitleaks`

---

### 🐧 Linux

En Linux hay varias rutas. Elige la que mejor se adapte a tu distribución.

#### Opción A — Binario desde GitHub Releases (recomendado)

```bash
# 1. Detecta tu arquitectura
uname -m
#   x86_64  → x64
#   aarch64 → arm64

# 2. Descarga la última versión (ejemplo con v8.30.1)
wget https://github.com/gitleaks/gitleaks/releases/download/v8.30.1/gitleaks_8.30.1_linux_x64.tar.gz

# 3. Descomprime
tar -xzf gitleaks_8.30.1_linux_x64.tar.gz

# 4. Instala el binario con permisos de ejecución
sudo install -m 0755 gitleaks /usr/local/bin/gitleaks

# 5. Limpia y verifica
rm -rf gitleaks gitleaks_8.30.1_linux_x64.tar.gz
gitleaks version
```

#### Opción B — Gestores de paquetes

```bash
# Debian / Ubuntu
sudo apt install gitleaks
# (si no está en los repos, añade el PPA o usa la opción A)

# Fedora / RHEL
sudo dnf install gitleaks

# Arch / Manjaro
sudo pacman -S gitleaks

# Alpine
apk add gitleaks
```

#### Opción C — Compilar desde el código (requiere Go ≥ 1.22)

```bash
git clone https://github.com/gitleaks/gitleaks.git
cd gitleaks
make build
sudo install -m 0755 gitleaks /usr/local/bin/

# O directamente con Go:
go install github.com/gitleaks/gitleaks/v8@latest
# el binario quedará en $(go env GOPATH)/bin
```

> 💡 En Linux Minimal / contenedores (Alpine, scratch) suele ser más limpio usar la imagen de Docker (ver más abajo).

---

### 🪟 Windows

#### Opción A — `winget` (Windows 10/11, recomendado)

```powershell
winget install gitleaks.gitleaks

# Verificar en PowerShell
gitleaks version
```

#### Opción B — Chocolatey

```powershell
choco install gitleaks
```

#### Opción C — Scoop

```powershell
scoop install gitleaks
```

#### Opción D — Binario manual (MSI / ZIP)

1. Ve a la página de [releases de Gitleaks](https://github.com/gitleaks/gitleaks/releases).
2. Descarga el asset correspondiente a tu arquitectura:
   - `gitleaks_*_windows_x64.zip` (Intel/AMD 64 bits)
   - `gitleaks_*_windows_arm64.zip` (Windows on ARM)
3. Extrae el `.zip` en una carpeta, por ejemplo `C:\Tools\gitleaks`.
4. Añade esa carpeta al **PATH**:

```powershell
# Temporal (solo esta sesión de PowerShell)
$env:Path += ";C:\Tools\gitleaks"

# Permanente (usuario actual) - PowerShell
[Environment]::SetEnvironmentVariable("Path", $this + ";C:\Tools\gitleaks", "User")
```

```cmd
:: Permanente - CMD
setx PATH "%PATH%;C:\Tools\gitleaks"
```

5. Abre **una terminal nueva** y verifica:

```powershell
gitleaks version
```

> 🪟 **Windows + Git Bash:** Gitleaks es un binario nativo `.exe`, por lo que funciona sin problema en Git Bash, WSL y Windows Terminal por igual. Si usas WSL, instala la versión de **Linux** dentro de WSL, no la de Windows.

---

### 🐳 Docker (independiente del sistema operativo)

Si no quieres instalar nada o estás en un entorno contenedorizado, usa la imagen oficial. Funciona igual en Windows, macOS y Linux.

```bash
# Docker Hub
docker pull zricethezav/gitleaks:latest

# GitHub Container Registry (registro oficial)
docker pull ghcr.io/gitleaks/gitleaks:latest

# Ejecutar un escaneo sobre una carpeta local
docker run -v "$(pwd)":/path ghcr.io/gitleaks/gitleaks:latest git /path
```

> ⚠️ **Importante:** el punto de entrada de la imagen es el binario, así que **tienes que pasar el subcomando y la ruta dentro del contenedor** (`git`, `dir`, `stdin`), no solo los argumentos.

---

### ✅ Verificación de la instalación

Ejecuta estos comandos en la terminal. Deberías ver `version`, `git`, `dir` y `stdin`.

```bash
gitleaks version        # nº de versión
gitleaks --help         # ayuda general
gitleaks git --help     # ayuda del subcomando git
gitleaks dir --help     # ayuda del subcomando dir
gitleaks stdin --help   # ayuda del subcomando stdin
```

Si `gitleaks` no se reconoce como comando, el binario no está en tu `PATH`.

---

## 4. Uso básico

### Escaneo del historial de un repositorio

```bash
# Desde dentro del repositorio
gitleaks git

# Con salida detallada (muestra cada hallazgo completo)
gitleaks git -v

# Sobre un repositorio concreto
gitleaks git /ruta/al/repo

# Escanear solo un rango de commits
gitleaks git -v --log-opts="--all HEAD~10..HEAD" /ruta/al/repo
```

### Escaneo de archivos o directorios (sin historial)

```bash
gitleaks dir .
gitleaks dir -v ./fixtures
gitleaks dir -v ./config/database.yml
```

### Escaneo por `stdin`

```bash
cat .env | gitleaks stdin
echo "AKIAIOSFODNN7EXAMPLE" | gitleaks stdin
```

### Generar reportes

```bash
# JSON
gitleaks dir -v . --report-format json --report-path gitleaks-report.json

# SARIF (se sube a GitHub Code Scanning)
gitleaks dir -v . --report-format sarif --report-path gitleaks.sarif
```

### Enmascarar los secretos en la salida

```bash
# Enmascara el 100% del secreto (por defecto)
gitleaks git -v --redact

# Enmascara solo el 50% inicial (útil para comparar tokens parecidos)
gitleaks git -v --redact=50
```

> 🔐 **Regla de oro:** en un entorno compartido o al compartir capturas de pantalla, **siempre** usa `--redact`. Un reporte sin `--redact` en un pipeline público expone los secretos que debía proteger.

### Usar un baseline (ignorar hallazgos previos)

```bash
# 1. Genera el baseline
gitleaks git --report-path gitleaks-baseline.json

# 2. En ejecuciones futuras, solo reporta hallazgos nuevos
gitleaks git --baseline-path gitleaks-baseline.json --report-path findings.json
```

---

## 5. Uso avanzado

### 5.1 Pre-commit hook

La forma más potente de **Shift Left**: impedir que el secreto llegue siquiera al repositorio.

```bash
# Instala pre-commit (https://pre-commit.com/#install)
pip install pre-commit      # macOS / Linux
pipx install pre-commit     # recomendado: aísla el entorno
# Windows: winget install pre-commit

# Crea .pre-commit-config.yaml en la raíz de tu repositorio
```

Contenido del `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.30.1
    hooks:
      - id: gitleaks
```

```bash
# Instala los hooks en tu repositorio
pre-commit install
```

Comportamiento esperado:

```bash
$ git commit -m "este commit contiene un secreto"
Detect hardcoded secrets.................................................Failed
```

> Si necesitas hacer un commit de excepción (por ejemplo, un fixture de test), puedes saltarte el hook:
> ```bash
> SKIP=gitleaks git commit -m "commit con secreto de prueba"
> ```

### 5.2 GitHub Actions

```yaml
# .github/workflows/gitleaks.yml
name: Secret Scanning

on:
  push:
    branches: [main]
  pull_request:

permissions:
  contents: read

jobs:
  gitleaks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0   # necesario para escanear todo el historial

      - name: Ejecutar Gitleaks
        uses: gitleaks/gitleaks-action@v3
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

> Alternativa ligera sin action externa:
> ```yaml
>       - run: |
>           curl -sSfL https://raw.githubusercontent.com/gitleaks/gitleaks/master/install.sh | bash
>           ./gitleaks detect --source . --redact --verbose
> ```

### 5.3 Ignorar falsos positivos

#### Por línea, con `gitleaks:allow`

```python
# Los fixtures de test usan un secreto ficticio
TEST_CLIENT_SECRET = '8dyfuiRyq=vVc3RRr_edRk-fK__JItpZ'  # gitleaks:allow
```

#### Con un archivo `.gitleaksignore`

```bash
# 1. Escanea y genera el reporte
gitleaks dir -v . --report-path leaks.json

# 2. Copia el campo "Fingerprint" de los falsos positivos que quieras ignorar
# 3. Pégalo en .gitleaksignore en la raíz del repo
```

Contenido de `.gitleaksignore`:

```
# Formato en modo `git`:   <commit-sha>:<ruta>:<ruleID>:<línea>
cd5226711335c68be1e720b318b7bc3135a30eb2:tests/fixtures/config.yml:generic-api-key:12
a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0:src/config.py:private-key:4

# Formato en modo `dir`:   <ruta>:<ruleID>:<línea>  (sin el hash de commit)
fixtures/tests/fixtures/config_test.yml:generic-api-key:9
```

#### Con una configuración personalizada `.gitleaks.toml`

```toml
title = "Mi configuración de Gitleaks"

# Extender la configuración por defecto en vez de empezar de cero
[extend]
useDefault = true

# Desactivar las reglas que generan demasiado ruido
disabledRules = ["generic-api-key"]

[[rules]]
id = "mi-token-interno"
description = "Token del sistema interno de facturación"
# Expresión regular de Go (sin lookaheads)
regex = '''INTERNAL-[A-Z0-9]{32}'''
# Grupo que se extrae y se somete a la comprobación de entropía
secretGroup = 0
# Entropía mínima de Shannon
entropy = 3.5
# Filtro rápido por palabras clave
keywords = ["INTERNAL"]

[[rules.allowlists]]
description = "Ignora los archivos de prueba"
paths = ['''tests/fixtures/''']
```

**Orden de precedencia de la configuración:**

1. Flag `--config` / `-c`
2. Variable de entorno `GITLEAKS_CONFIG` (ruta al archivo)
3. Variable de entorno `GITLEAKS_CONFIG_TOML` (contenido directo)
4. Archivo `.gitleaks.toml` dentro de la ruta escaneada

Si no hay ninguna, se usa la configuración por defecto.

### 5.4 Reglas compuestas (composite rules)

Desde la v8.28.0, una regla puede requerir que **otras reglas** también coincidan, y opcionalmente dentro de una ventana de proximidad. Esto reduce falsos positivos y permite patrones más complejos.

```toml
# La regla auxiliar debe estar DEFINIDA en la configuración...
[[rules]]
id = "aws-account-id"
description = "Identificador de cuenta de AWS"
regex = '''account_id\s*=\s*["']?\d{12}'''
keywords = ["account_id"]

# ...y la principal la referencia por su id
[[rules]]
id = "aws-key-con-context"
description = "Clave AWS solo si aparece junto a un identificador de cuenta"
regex = '''AKIA[0-9A-Z]{16}'''
secretGroup = 0
entropy = 3.0

[[rules.required]]
id = "aws-account-id"
withinLines = 5      # la coincidencia debe estar a ≤ 5 líneas
# withinColumns = 80  # opcional: acotar también horizontalmente
```

| Contexto | Sin `required` | Con `required` |
|---|---|---|
| Clave AWS sola en un test | 🟢 se reporta (ruido) | 🔇 se ignora |
| Clave AWS junto a `account_id` | 🟢 se reporta | 🟢 se reporta |

> ⚠️ La regla auxiliar también aparece en el reporte: es una regla válida por derecho propio. Es un comportamiento conocido de las composite rules; su contenido la marca el propio autor como experimental y sujeta a cambios.
>
> Si el `id` de `[[rules.required]]` no existe en la configuración, Gitleaks aborta con `Failed to load config: ... rule ID 'X' does not exist`.


### 5.5 Códigos de salida

```
0   → no se encontraron filtraciones
1   → se encontraron filtraciones o hubo un error
126 → flag desconocido
```

Diseñado para que el pipeline **falle solo** cuando hay un problema:

```bash
gitleaks git . || echo "Se detectaron secretos — bloqueando el pipeline"
```

---

## 6. Códigos de salida y troubleshooting

| Problema | Causa probable | Solución |
|---|---|---|
| `gitleaks: command not found` | El binario no está en el `PATH` | Añade el directorio del binario al `PATH` y abre una terminal nueva. |
| `0 leaks found` pero hay un secreto evidente | El escaneo fue `dir` y el secreto está en un archivo ignorado por `.gitignore` | Usa `gitleaks git` para revisar el historial, o `gitleaks dir --no-git` sobre rutas concretas. |
| Escaneo lento en un repo grande | Estás escaneando todo el historial en cada commit | Crea un `baseline` con `--baseline-path`. |
| Demasiados falsos positivos | Reglas genéricas sobre datos de prueba | Añade `[[allowlists]]` con `paths` o usa `.gitleaksignore`. |
| En Windows: `Access is denied` al ejecutar | Política de ExecutionPolicy o antivirus | Usa `gitleaks.exe` directamente o descarga el `.msi` del release oficial. |
| El hook no bloquea el commit | El hook no está instalado en `.git/hooks` | Ejecuta `pre-commit install` dentro del repositorio. |
| El action de GitHub no detecta nada | `fetch-depth: 0` ausente en el checkout | Añade `with: fetch-depth: 0` (necesario para el historial completo). |

---

## 7. Qué hacer cuando Gitleaks encuentra un secreto

El hallazgo es solo el principio. Sigue esta lista:

1. **Revisa el hallazgo** — confirma que es un secreto real y no un falso positivo.
2. **Si es real, revócalo inmediatamente.** Prioridad máxima: el secreto debe considerarse comprometido desde el momento en que estuvo en un repositorio, aunque lo hayas borrado después.
   - AWS:IAM → rotar las *access keys*
   - GitHub → *Settings → Developer settings → Personal access tokens* → revocar
   - Base de datos → cambiar la contraseña
3. **Elimínalo del historial** con [BFG](https://github.com/rtyley/BFG) o `git filter-repo`.
4. **Añade el hallazgo a `.gitleaksignore`** si era un falso positivo, o a una allowlist si es una excepción conocida.
5. **Cierra el hallazgo con un commit** que documente la rotación, para que quede trazabilidad.
6. **Verifica** con un nuevo `gitleaks git` que el repositorio está limpio.

> 🔑 **Nunca** crees que "ya lo borré, así que no pasa nada". Mientras el secreto estuvo en un commit, pudo haber sido clonado, cacheado o indexado por algún servicio. La rotación de la credencial es obligatoria.

---

## 8. Ejercicios de esta carpeta

| Ejercicio | Tema | Nivel |
|---|---|---|
| `01-reconocimiento/` | Primeros pasos: instalación, verificación y comandos de ayuda | 🟢 Básico |
| `02-escaneo-basico/` | Escanear repositorios, directorios y `stdin`; entender la salida | 🟢 Básico |
| `03-configuracion-allowlists/` | Reducir falsos positivos con `gitleaks:allow`, `.gitleaksignore` y `.gitleaks.toml` | 🟡 Intermedio |
| `04-pre-commit/` | Implementar el hook de `pre-commit` en un repositorio de práctica | 🟡 Intermedio |
| `05-ci-github-actions/` | Integrar Gitleaks en un pipeline de GitHub Actions | 🔴 Avanzado |
| `06-remediacion/` | Revocar un secreto filtrado y limpiar el historial con `git filter-repo` | 🔴 Avanzado |

> 📝 Todos los ejercicios están listos. Los secretos usados en los `fixtures/` son **ficticios** y están diseñados para ser detectados.

> 🧪 **Prueba de humo del curso:** ejecuta esto y deberías obtener 16 hallazgos (los secretos de los fixtures más los ejemplos de los enunciados que aún no están en el `.gitleaksignore`):
> ```bash
> cd gitleaks
> gitleaks dir . --redact -v
> ```
> Este repositorio incluye un `.gitleaksignore` real que ya ignora los ejemplos de los enunciados. Los `fixtures/` **no** están ignorados a propósito: deben seguir detectándose.

---

## 9. Referencias

- **Repositorio oficial:** https://github.com/gitleaks/gitleaks
- **Configuración por defecto (referencia de reglas):** https://github.com/gitleaks/gitleaks/blob/master/config/gitleaks.toml
- **Releases:** https://github.com/gitleaks/gitleaks/releases
- **Blog oficial (configuración avanzada):** https://blog.gitleaks.io/stop-leaking-secrets-configuration-2-3-aeed293b1fbf
- **Artículo sobre el motor de detección:** https://lookingatcomputer.substack.com/p/regex-is-almost-all-you-need
- **gitleaks-action (GitHub Action):** https://github.com/gitleaks/gitleaks-action
- **Cómo se explica el motor de detección:** *Regex is (almost) all you need*
- **Alternativa a considerar a futuro:** https://github.com/betterleaks/betterleaks

---

## 10. Glosario rápido

| Término | Significado |
|---|---|
| **Secret** | Credencial sensible: API key, token, contraseña, clave privada. |
| **Finding** | Hallazgo: un secreto detectado, con su ubicación y metadatos. |
| **RuleID** | Identificador de la regla que disparó el hallazgo (p. ej. `aws-access-token`). |
| **Entropy** | Medida de aleatoriedad (Shannon). Una cadena con entropía alta es más probable que sea un secreto real. |
| **Fingerprint** | Identificador único de un hallazgo: `commit:archivo:ruleID:línea` (sin el commit en modo `dir`). Se usa en `.gitleaksignore`. |
| **Allowlist** | Lista de excepciones: elementos que la herramienta debe ignorar. |
| **Baseline** | Reporte previo usado para ignorar hallazgos ya conocidos y detectar solo los nuevos. |
| **Redact** | Enmascarar el valor del secreto en la salida. |
| **SARIF** | Formato estándar de reporte para integrarse con GitHub Code Scanning. |

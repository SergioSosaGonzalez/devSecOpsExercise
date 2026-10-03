# 🔒 Trivy — Escaneo de vulnerabilidades, secretos y configuraciones

> **Categoría:** SCA / SAST-lite / Secret Scanning / IaC Security · **Etapa del Shift Left:** Commit → CI → CD · **Licencia:** Apache 2.0

## 1. ¿Qué es Trivy?

Trivy es un escáner de seguridad completo y versátil desarrollado por Aqua Security. Detecta vulnerabilidades (CVEs), secretos expuestos, malas configuraciones (IaC), licencias y puede generar SBOMs. Es rápido, sin dependencias del servidor (ejecuta offline con bases de datos descargables) y está diseñado para integrarse fácilmente en workflows de desarrollo.

**Analogía útil:** Piensa en Trivy como un "radar de seguridad" que examina tu código, dependencias, imágenes y configuraciones buscando amenazas antes de que lleguen a producción.

**¿Por qué importa?**

- **Shift Left**: Detecta problemas de seguridad lo antes posible, cuando son más baratos de corregir.
- **Cobertura integral**: Un único binario cubre vulnerabilidades, secretos, IaC y licencias.
- **Ligero y rápido**: No requiere infraestructura compleja (a diferencia de soluciones con servidor).
- **Fácil de automatizar**: Integración nativa con CI/CD, GitHub Actions, IDEs y más.

**Diagrama ASCII del flujo:**

```
┌─────────────────┐
│  Código/FS      │  ──►  Trivy FS  ──►  Hallazgos (Vuln/Secret/Misconfig)
└─────────────────┘
┌─────────────────┐
│  Docker Image   │  ──►  Trivy Image
└─────────────────┘
┌─────────────────┐
│  IaC (TF/Docker)│  ──►  Trivy Config
└─────────────────┘
                ▼
           ┌─────────────┐
           │  Decisión    │
           │  (Ignorar/   │
           │   Corregir)  │
           └─────────────┘
```

## 2. Características principales

| Característica | Descripción |
|---|---|
| **Vulnerability Scanner** | Detecta CVEs en paquetes OS y dependencias (SCA). Soporta múltiples ecosistemas (npm, pip, go, maven, etc.). |
| **Secret Scanner** | Detecta secretos expuestos (tokens, claves, passwords). Habilitado por defecto. |
| **Misconfigurations (IaC)** | Analiza Dockerfile, Kubernetes, Terraform, CloudFormation, etc. Detecta malas prácticas de seguridad. |
| **SBOM Generation** | Genera CycloneDX, SPDX para trazabilidad de dependencias. |
| **Filesystem Scan (`fs`)** | Escanea directorios locales. Ideal para código fuente y pre-commit. |
| **Sin servidor** | Ejecuta localmente. Utiliza bases de datos (`trivy-db`) actualizables. |
| **Múltiples formatos** | Salida en tabla, JSON, SARIF (para Code Scanning), CycloneDX, etc. |
| **Filtros flexibles** | Por severidad, tipo (os/library), ignorar no arreglados (`--ignore-unfixed`). |

### Limitaciones que debes conocer

| Limitación | Explicación |
|---|---|
| **Bases de datos necesarias** | La primera ejecución descarga `trivy-db`. En modo offline (`--offline-scan`) necesita tenerla cacheada. |
| **No corrige automáticamente** | Trivy **detecta**, no repara. La remediación depende del desarrollador. |
| **Falsos positivos/negativos** | Como cualquier escáner basado en signatures, puede tener falsos positivos. Usa `.trivyignore` o `ignore-policy` cuando sea justificado. |
| **Scope limitado** | No hace análisis de flujo (Data Flow Analysis) profundo como SAST completo; es más ligero/focalizado. |
| **Requiere actualización de DB** | Para detectar CVEs recientes, conviene actualizar DB (`--skip-db-update=false` por defecto). |
| **Escaneo de secretos heurístico** | Detecta patrones; puede marcar strings parecidos a secretos (falsos positivos). Esto es intencional por seguridad. |

## 3. Instalación

### macOS

```bash
brew install trivy
```

### Linux (Debian/Ubuntu)

```bash
sudo apt-get install wget gnupg
wget -qO- https://aquasecurity.github.io/trivy-repo/deb/public.key | sudo gpg --dearmor -o /usr/share/keyrings/trivy.gpg
echo "deb [signed-by=/usr/share/keyrings/trivy.gpg] https://aquasecurity.github.io/trivy-repo/deb generic main" | sudo tee /etc/apt/sources.list.d/trivy.list
sudo apt-get update && sudo apt-get install trivy
```

### Linux (RPM)

```bash
sudo rpm -ivh https://aquasecurity.github.io/trivy-repo/rpm/releases/$(. /etc/os-release && echo "$VERSION_ID")/$(uname -m)/trivy-repo-1.0.0-2.$(uname -m).rpm
sudo yum install -y trivy
```

### Windows

```bash
choco install trivy
# o scoop
scoop install trivy
```

### Docker (alternativa)

```bash
docker run -it --rm -v $(pwd):/workdir aquasec/trivy:latest fs /workdir
```

### ✅ Verificación de la instalación

```bash
trivy --version
```

**Salida esperada:** Versión (ej. `Version: 0.56.x` o superior). Trivy 0.50+ es común; el curso usa comandos genéricos (`fs`, `config`, etc.) estables.

## 4. Uso básico

### Escaneo de filesystem (repositorio/código)

Por defecto detecta **vulnerabilidades (vuln)** y **secretos (secret)**.

```bash
trivy fs .
```

### Escanear solo secretos

```bash
trivy fs --scanners secret .
```

### Escanear vulnerabilidades + misconfiguraciones

```bash
trivy fs --scanners vuln,misconfig .
```

### Filtrar por severidad

```bash
trivy fs --severity HIGH,CRITICAL .
```

### Ignorar vulnerabilidades no arregladas

Útil para enfocarse en lo corregible.

```bash
trivy fs --ignore-unfixed .
```

### Salida en JSON (para procesamiento)

```bash
trivy fs --format json -o reporte.json .
```

### Salida SARIF (para GitHub Code Scanning)

```bash
trivy fs --format sarif -o trivy-results.sarif .
```

## 5. Uso avanzado

### 5.1 Secret scanning con configuración personalizada

Trivy busca `trivy-secret.yaml` por defecto. Permite definir reglas, allowlists, skip patterns.

```bash
trivy fs --scanners secret --secret-config trivy-secret.yaml .
```

### 5.2 Uso de .trivyignore

Crear `.trivyignore` en raíz para ignorar hallazgos **justificados** (no se debe abusar).

```text
# Ignorar CVE específica (justificación requerida en PR)
CVE-2024-XXXX-XXXX
```

Formato: un CVE/ID por línea. Comentarios con `#`.

### 5.3 Escaneo de Dockerfile/IaC (misconfigurations)

```bash
trivy config .
```

También específico:

```bash
trivy config Dockerfile
```

### 5.4 Generar SBOM (CycloneDX)

```bash
trivy fs --format cyclonedx -o sbom.cdx.json .
```

### 5.5 Modo offline

```bash
trivy fs --offline-scan .
```

Requiere DB cacheada previamente.

## 6. Códigos de salida y troubleshooting

| Problema | Causa probable | Solución |
|---|---|---|
| `trivy: command not found` | No instalado o PATH incorrecto | Verifica instalación (`which trivy`) o usa Docker. |
| `DB update failed` / lento en 1ª ejecución | Descarga DB inicial | Deja conexión a internet en primer scan. Usa `--cache-dir` para persistir. |
| Muchos falsos positivos (secrets) | Patrones genéricos | Usa `.trivyignore`, `--secret-config`, o ajusta reglas. |
| Detecta secretos en fixtures/tests | Esperado en ejercicios | En producción, usa `--skip-dirs`, `--skip-files` o `.trivyignore` con justificación. |
| Salida truncada | Terminal pequeño | Usa `--format json` + `jq` o redirige a archivo. |
| Java/Go lockfiles no detectados | No parseables o formato raro | Asegura lockfile válido (package-lock.json, go.sum, etc.). |
| Escaneo muy lento | Muchos archivos | Usa `--skip-dirs node_modules,dist,build,.git` para acelerar. |

## 7. Qué hacer cuando Trivy encuentra hallazgos

| Tipo de hallazgo | Acción recomendada |
|---|---|
| **CRITICAL/HIGH (Vulns)** | Priorizar corrección. Actualizar dependencia o aplicar parche. Si no hay fix, evaluar riesgo/compensación. |
| **Secrets expuestos** | **Nunca** commitear. Rotar inmediatamente (aunque sea ficticio en ejercicios). Eliminar del historial si ya subido (git filter-repo). |
| **Misconfigurations** | Corregir IaC según mejores prácticas (principio de menor privilegio, no root, etc.). |
| **LOW/MEDIUM** | Evaluar en contexto (riesgo aceptable vs esfuerzo). Documentar aceptación justificada. |
| **Falsos positivos** | Solo ignorar con justificación documentada (`.trivyignore`, comentario en PR). |

> **Regla de oro:** Los secretos ficticios en `fixtures/` **deben seguir detectándose**. Son material de laboratorio, no un bug.

## 8. Ejercicios de esta carpeta

| Ejercicio | Nivel | Tema | Duración estimada |
|---|---|---|---|
| [01-escaneo-basico](01-escaneo-basico/README.md) | 🟢 Básico | Primer scan FS, detectando secretos y entendiendo salida | 15 min |
| [02-analisis-resultados](02-analisis-resultados/README.md) | 🟡 Intermedio | Interpretar hallazgos, filtrar por severidad, usar .trivyignore | 25 min |
| [03-ci-github-actions](03-ci-github-actions/README.md) | 🔴 Avanzado | Integrar Trivy en GitHub Actions (FS scan + fallo en CRITICAL) | 30 min |

🧪 **Prueba de humo del curso:** ejecuta esto y deberías obtener **16 hallazgos** (conteo basado en fixtures diseñados para este curso):

```bash
cd trivy && trivy fs . --redact -v 2>&1 | grep -c "SECRET\|VULN\|MISCONFIG\|LICENSE\|Detected" || true
```

> **Nota:** El número exacto se verifica ejecutando el comando. Los secretos en `fixtures/` son intencionales y **deben detectarse**. Los ejemplos de comandos en README no se ignoran (no creamos `.trivyignore` para docs aquí por diseño simple).

## 9. Referencias

- [Trivy - Sitio oficial](https://trivy.dev/)
- [Trivy Docs - Filesystem](https://trivy.dev/docs/latest/target/filesystem/)
- [Trivy CLI Reference](https://github.com/aquasecurity/trivy/blob/main/docs/guide/references/configuration/cli/trivy_filesystem.md)
- [Secret Scanning](https://trivy.dev/latest/docs/scanner/secret/)
- [Misconfigurations](https://trivy.dev/latest/docs/scanner/misconfiguration/)
- [Trivy GitHub Action](https://github.com/aquasecurity/trivy-action)
- [.trivyignore](https://aquasecurity.github.io/trivy/v0.55/docs/configuration/filtering/#trivyignore)

## 10. Glosario rápido

| Término | Significado |
|---|---|
| **FS (Filesystem)** | Escaneo del sistema de archivos/local. Ideal para código fuente. |
| **SCA** | Software Composition Analysis (análisis de dependencias). |
| **IaC** | Infrastructure as Code (Terraform, Dockerfile, K8s...). |
| **CVSS/Severidad** | UNKNOWN, LOW, MEDIUM, HIGH, CRITICAL. |
| **SBOM** | Software Bill of Materials (inventario de dependencias). |
| **.trivyignore** | Lista de hallazgos a ignorar (usar con criterio). |
| **trivy-db** | Base de datos de vulnerabilidades utilizada por Trivy. |
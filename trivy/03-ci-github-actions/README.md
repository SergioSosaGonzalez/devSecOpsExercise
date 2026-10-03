# Ejercicio 03 — Integración de Trivy en CI con GitHub Actions

**Nivel:** 🔴 Avanzado · **Duración estimada:** 30 min

## 🎯 Objetivo

Aprender a integrar Trivy en un pipeline de GitHub Actions para escanear el código fuente (filesystem), entender el uso de `exit-code`, `severity`, `ignore-unfixed` y cómo subir resultados a GitHub Security (SARIF).

## 📋 Requisitos previos

- [Ejercicio 02 completado](../02-analisis-resultados/README.md)
- Cuenta de GitHub (para práctica en repo propio)
- Conocimientos básicos de GitHub Actions

---

## Pasos

### 1. Navegar al directorio del ejercicio

```bash
cd trivy/03-ci-github-actions
```

### 2. Inspeccionar los fixtures

Revisa el código y el workflow de ejemplo.

```bash
cat fixtures/src/app.py
cat fixtures/requirements.txt
cat fixtures/workflow-example/trivy-fs.yml
```

**Salida esperada:** Código Python con secretos ficticios, `requirements.txt` con versiones antiguas y un workflow de GitHub Actions usando `trivy-action`.

> 💡 **¿Por qué esto importa?** La integración CI es donde Trivy gana valor: bloquea merges con problemas críticos antes de producción.

### 3. Analizar el workflow de ejemplo

Observa los parámetros clave:

- `scan-type: 'fs'` - Escaneo de filesystem (código fuente)
- `scan-ref: '.'` - Directorio a escanear
- `format: 'sarif'` - Formato para GitHub Code Scanning
- `severity: 'CRITICAL,HIGH'` - Solo fallar en severidades altas
- `exit-code: '1'` - Hace fallar el job si encuentra hallazgos (gate de calidad)
- `ignore-unfixed: true` - Ignora vulnerabilidades sin parche disponible
- Sube SARIF a Security tab con `github/codeql-action/upload-sarif`

**Pregunta a reflexionar mientras lees:** ¿Qué significa que el job falle con `exit-code: 1`?

> 💡 **¿Por qué esto importa?** Un buen gate balancea seguridad (bloquear CRITICAL) con pragmatismo (no bloquear por LOW sin parche).

### 4. Simular un escaneo local equivalente al CI

Ejecuta localmente lo que haría el workflow (FS, solo CRITICAL/HIGH, ignora no arreglados).

```bash
trivy fs --scanners vuln,secret --severity CRITICAL,HIGH --ignore-unfixed .
```

**Salida esperada:** Verás hallazgos (secrets + vulns de requirements.txt) filtrados por severidad. Dependiendo de las versiones, pueden aparecer HIGH/CRITICAL.

> 💡 **¿Por qué esto importa?** Probar localmente antes de subir el workflow evita muchos fallos de CI.

### 5. Probar con salida SARIF (como en CI)

Generar el mismo formato que sube a GitHub.

```bash
trivy fs --scanners vuln,secret --severity CRITICAL,HIGH --format sarif -o trivy-results.sarif .
```

**Comprobar que se generó:**

```bash
ls -lh trivy-results.sarif
head -15 trivy-results.sarif
```

**Salida esperada:** Archivo SARIF creado. SARIF es JSON con esquema específico para herramientas de análisis estático.

> 💡 **¿Por qué esto importa?** SARIF permite visualizar hallazgos directamente en GitHub Security > Code Scanning.

### 6. Copiar el workflow a la ubicación correcta (para estudio)

El workflow de ejemplo está en `fixtures/workflow-example/`. En un repo real, iría a `.github/workflows/trivy.yml`. Copiémoslo para entender la estructura.

```bash
mkdir -p .github/workflows
cp fixtures/workflow-example/trivy-fs.yml .github/workflows/trivy-fs.yml
echo "Workflow copiado a .github/workflows/"
```

**Verificar:**

```bash
ls .github/workflows/
```

> 💡 **¿Por qué esto importa?** En el curso, los workflows viven dentro de las carpetas de ejercicio como material de estudio (ver AGENTS.md). Copiarlos al repo de práctica del alumno es parte del ejercicio.

### 7. Entender cuándo debe fallar el pipeline

Ejecuta con `exit-code 1` para simular fallo de gate.

```bash
trivy fs --scanners vuln,secret --severity CRITICAL,HIGH --ignore-unfixed --exit-code 1 .
```

**Salida esperada:** Trivy devolverá código de salida != 0 si encuentra hallazgos. En terminal verás el resumen y el exit code. Podemos comprobarlo con:

```bash
trivy fs --scanners vuln,secret --severity CRITICAL,HIGH --ignore-unfixed --exit-code 1 .; echo "EXIT:$?"
```

**Salida esperada:** Aparecen hallazgos y al final `EXIT:1` (o el valor configurado). Si no hubiera hallazgos, sería `EXIT:0`.

> 💡 **¿Por qué esto importa?** `exit-code: 1` es lo que convierte un "aviso" en un "gate de calidad" que bloquea el merge.

---

## ✅ Comprobación final

- [ ] Has entendido los parámetros clave del workflow (scan-type, severity, exit-code, format sarif)
- [ ] Has ejecutado localmente el escaneo equivalente al CI
- [ ] Has generado un archivo `trivy-results.sarif`
- [ ] Has copiado el workflow a `.github/workflows/` (estructura correcta)
- [ ] Has probado el comportamiento de `exit-code` (0 vs 1)

---

## 🤔 Preguntas de reflexión

1. **¿Por qué usar `severity: CRITICAL,HIGH` con `exit-code: 1` en lugar de bloquear todas las severidades (LOW-MEDIUM)?** ¿Qué equilibrio buscas entre seguridad y velocidad de desarrollo?

2. **¿Cuál es la diferencia entre escanear en modo `fs` (filesystem) vs. escanear una imagen Docker (`image`)? ¿En qué etapa de un pipeline usarías cada uno?**

3. **Al subir resultados SARIF a GitHub Security, ¿qué beneficio aporta vs. solo hacer fallar el job?** Piensa en visibilidad, trazabilidad y gestión de deuda técnica.

---

## ⏭️ Siguiente

Has completado los 3 ejercicios del módulo Trivy. Revisa la [sección 8 del README del módulo](../../trivy/README.md#8-ejercicios-de-esta-carpeta) para el smoke test global.


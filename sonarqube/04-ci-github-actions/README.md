# Ejercicio 04 — Integración con CI/CD (GitHub Actions)

**Nivel:** 🔴 Avanzado · **Duración estimada:** 50 min

## 🎯 Objetivo

Integrar SonarQube en un pipeline de GitHub Actions para que **el Quality Gate sea la puerta de entrada al repositorio**: si falla, el pull request no se puede mergear.

## 📋 Requisitos previos

- [Ejercicio 03 completado](../03-exclusiones-y-falsos-positivos/README.md)
- Un proyecto de SonarQube con token generado
- El código en un repositorio de GitHub (usa tu fork)

---

## 🧠 Las tres capas de Clean as You Code, y dónde encaja CI

```
  Capa 1 — IDE                    Capa 2 — Pull Request              Capa 3 — Rama principal
  ─────────────                    ─────────────────────              ────────────────────
  SonarQube for VS Code            Workflow en cada PR                 Workflow en push a main
  El issue aparece                 Check del Quality Gate              Quality Gate de la rama
  mientras escribes               en los checks del PR                Tendencias y deuda
  Coste: 0 segundos               Coste: ~2 minutos                   Coste: ~5 minutos
  Quién: el desarrollador           Quién: el pipeline                  Quién: la plataforma
```

> 💡 En la capa 2, el check del Quality Gate funciona con **Community Build**. Los comentarios con el detalle de cada issue en el diff son la *Pull Request decoration* y requieren edición de pago (lo verás en el paso 6).

**Este ejercicio implementa las capas 2 y 3.**

### La diferencia con Gitleaks

| | Gitleaks | SonarQube |
|---|---|---|
| Detecta | Secretos | Bugs, vulnerabilidades, code smells, duplicación, cobertura |
| Modelo | Un único escáner | Servidor + scanner + Quality Gate |
| Estado | Estático por commit | **Histórico y comparado** |
| Puerta | Código de salida ≠ 0 | Quality Gate + `sonar.qualitygate.wait` |
| Red | Sin red | Requiere red hacia el servidor |

> ⚠️ **Ambos se necesitan y se complementan.** Un pipeline maduro ejecuta los dos: Gitleaks primero (rápido y bloqueante), SonarQube después (lento pero profundo). El orden importa: si hay un secreto filtrado, no tiene sentido gastar 4 minutos en un análisis que después se va a bloquear.

---

## Pasos

### 1. Publica los secrets en GitHub

**En SonarQube:**

1. *My Account → Security → Generate Tokens* → nombre `github-actions` → *Generate*.
2. ⚠️ **Usa un token de cuenta con permiso de análisis**, no el token del ejercicio 01 si ese es solo de proyecto.

**En GitHub:**

*Settings → Secrets and variables → Actions → New repository secret*

| Nombre | Tipo | Valor |
|---|---|---|
| `SONAR_TOKEN` | Secret | `squ_...` (el token que acabas de generar) |
| `SONAR_HOST_URL` | Variable | La URL de tu servidor |

> 💡 SonarSource recomienda guardar la **URL** como *variable* (`vars.`) y no como *secret*, porque no es información sensible y así se puede cambiar entre entornos (local, staging, producción) sin tocar todos los repositorios.

Si tu SonarQube usa **certificados propios**, añade además el secreto `SONAR_ROOT_CERT` con el certificado en formato PEM.

### 2. Crea el workflow

El archivo [`sonar.yml`](.github/workflows/sonar.yml) de esta carpeta es la versión base. Cópialo a `.github/workflows/sonar.yml` en tu repositorio de práctica:

```yaml
name: SonarQube

on:
  push:
    branches: [main]
  pull_request:
    types: [opened, synchronize, reopened]
  workflow_dispatch: {}

permissions:
  contents: read

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  sonarqube:
    name: Análisis SonarQube
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v6
        with:
          fetch-depth: 0        # necesario para el análisis de SCM y el blame

      - uses: actions/setup-java@v4
        with:
          distribution: temurin
          java-version: 21      # Java 17 ya no tiene soporte

      - name: Cache de SonarQube
        uses: actions/cache@v5
        with:
          path: ~/.sonar/cache
          key: ${{ runner.os }}-sonar
          restore-keys: ${{ runner.os }}-sonar

      - name: Ejecutar análisis
        uses: SonarSource/sonarqube-scan-action@v8
        env:
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
          SONAR_HOST_URL: ${{ vars.SONAR_HOST_URL }}

      # Bloquea el merge si el Quality Gate falla
      - name: Verificar Quality Gate
        uses: SonarSource/sonarqube-quality-gate-action@v1
        with:
          pollingTimeoutSec: 600
        env:
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
          SONAR_HOST_URL: ${{ vars.SONAR_HOST_URL }}
```

> 🔐 **Desde la v8, el action verifica la firma OpenPGP del binario del scanner** con `gpg` y `dirmngr`. Los runners alojados por GitHub ya los traen; en un runner self-hosted o dentro de un contenedor hay que instalarlos. Si no puedes, desactívalo de forma explícita (y sabiendo qué pierdes):
>
> ```yaml
> - uses: SonarSource/sonarqube-scan-action@v8
>   with:
>     skipSignatureVerification: true
> ```

### 3. ⚠️ Sobre el runner y la red

Un runner público de GitHub **no puede alcanzar** tu `localhost:9000`. Tienes tres opciones:

| Opción | Cuándo usarla |
|---|---|
| **Self-hosted runner** en la misma red que SonarQube | Producción, la solución estándar |
| **SonarQube Cloud** | Si no puedes exponer el servidor |
| **Túnel (ngrok / Cloudflare Tunnel)** | Solo para demos, nunca en producción |

```yaml
# Con self-hosted runner
runs-on: [self-hosted, linux, sonarqube]
```

> 🔐 **Nunca** expongas tu SonarQube a internet sin HTTPS, autenticación y firewall. Contiene el código fuente completo de tu organización y su historial de métricas.

### 4. Ejecuta el primer workflow

```bash
git checkout -b exercise/sonar-ci
mkdir -p .github/workflows
cp <ruta-a>/.github/workflows/sonar.yml .github/workflows/
git add .github/workflows/sonar.yml
git commit -m "ci: add SonarQube analysis workflow"
git push origin exercise/sonar-ci
```

Abre el PR y observa:

- El job **"Análisis SonarQube"** aparece en los checks
- Al terminar, el check **"SonarQube Quality Gate check"** aparece con estado ✅ o ❌
- **Con una edición de pago** y el permiso `pull-requests: write` (ver más abajo), los issues aparecen como comentarios en el PR

### 5. Prueba que el Quality Gate bloquea

Crea un PR que falle deliberadamente:

```bash
git checkout -b test/pr-que-falla
echo "def nueva_funcion_sin_tests(): return 1" >> src/nuevo_codigo.py
git add -A
git commit -m "test: verificar que el Quality Gate bloquea"
git push origin test/pr-que-falla
```

Abre el PR. El check de Quality Gate debe estar **en rojo**.

### 6. Los comentarios en el Pull Request (edición de pago)

> ⚠️ **Con Community Build esta opción no está disponible.** La *Pull Request decoration* es una función de Developer Edition y superiores. Configúralo si tienes una edición de pago; si no, el paso 4 ya te da la señal que necesitas.

Para que los issues aparezcan como **comentarios en el diff** del PR:

1. En SonarQube: *Administration → General Settings → General → SCM Integration → Checks Request*
2. Selecciona la aplicación que usas (GitHub) y ponla en **Enabled**
3. También *Pull Request decoration → Enabled*
4. En *General Settings → Pull Request decoration*, marca tu repositorio

Para que el action pueda escribir comentarios, el workflow necesita permiso:

```yaml
permissions:
  contents: read
  pull-requests: write
  issues: write
```

Con esto, cada PR recibe un comentario como:

```
SonarQube Scan
Quality Gate: FAILED
🟡 Reliability: A | 🟢 Security: B | 🔴 Maintainability: C
Coverage: 45.2% (objetivo 80%)
3 new issues introduced
```

### 7. Versiona correctamente en CI

Este paso es donde la mayoría de equipos fallan. Recuerda lo del ejercicio 02:

```yaml
      - name: Definir la versión del proyecto
        run: |
          # ❌ MAL: el número de build cambia en cada ejecución
          # echo "VERSION=build-${GITHUB_RUN_NUMBER}" >> $GITHUB_ENV

          # ✅ BIEN: la versión sale del código (pyproject.toml, package.json...)
          echo "VERSION=1.2.0" >> $GITHUB_ENV
        shell: bash

      - name: Ejecutar análisis
        uses: SonarSource/sonarqube-scan-action@v8
        env:
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
          SONAR_HOST_URL: ${{ vars.SONAR_HOST_URL }}
          SONAR_PROJECT_VERSION: ${{ env.VERSION }}
```

Si no defines la versión, el scanner puede deducirla del build, lo que rompe la definición de "Previous version".

### 8. Ejecuta los tests y la cobertura antes del análisis

El **orden** importa: primero tests, luego cobertura, luego análisis.

```yaml
      - name: Instalar dependencias
        run: |
          python -m pip install --upgrade pip
          pip install pytest pytest-cov

      - name: Ejecutar tests con cobertura
        run: |
          python -m pytest --cov=. --cov-report=xml:coverage.xml --cov-config=sonar-project.properties

      - name: Ejecutar análisis SonarQube
        uses: SonarSource/sonarqube-scan-action@v8
        env:
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
          SONAR_HOST_URL: ${{ vars.SONAR_HOST_URL }}
          SONAR_PYTHON_COVERAGE_REPORT_PATHS: coverage.xml
```

> 📌 **El scanner no genera la cobertura, solo la lee.** `pytest-cov` escribe `coverage.xml` en formato Cobertura y el escáner lo recoge. Si no defines `SONAR_PYTHON_COVERAGE_REPORT_PATHS`, el escáner buscará por defecto en `.coverage-reports/*coverage-*.xml`. Equivalente sin `pytest-cov`: `coverage run -m pytest` seguido de `coverage xml`.

### 9. Alternativa:Quality Gate como paso del propio scanner

Si no quieres usar el action de verificación:

```yaml
      - name: Ejecutar análisis
        run: |
          sonar-scanner \
            -Dsonar.qualitygate.wait=true \
            -Dsonar.qualitygate.timeout=600
```

| Parámetro | Valor por defecto | Efecto |
|---|---|---|
| `sonar.qualitygate.wait` | `false` | El scanner espera y **falla** si el Quality Gate falla |
| `sonar.qualitygate.timeout` | `300` | Segundos de espera (el action de Gitleaks usaba un concepto parecido) |

> 📌 **Cuándo usar cada opción:** `sonar.qualitygate.wait=true` aumenta la duración del pipeline. SonarSource recomienda usar el action de verificación, y reservar `wait=true` para bloquear un **deployment** si el Quality Gate está rojo.

### 10. Combina Gitleaks + SonarQube en el mismo pipeline

Este es el pipeline que quieres en un proyecto real:

```yaml
name: Security Pipeline

on:
  push: { branches: [main] }
  pull_request: { types: [opened, synchronize, reopened] }

permissions:
  contents: read

jobs:
  # ── Capa 1: rápida y bloqueante (segundos) ──
  secrets:
    name: Secret Scanning (Gitleaks)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
        with:
          fetch-depth: 0
      - name: Detectar secretos
        uses: gitleaks/gitleaks-action@v3
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

  # ── Capa 2: lenta y profunda (minutos) ──
  quality:
    name: Quality Gate (SonarQube)
    needs: secrets          # no analizar si ya hay un secreto filtrado
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
        with:
          fetch-depth: 0
      - uses: actions/setup-java@v4
        with:
          distribution: temurin
          java-version: 21
      - uses: actions/cache@v5
        with:
          path: ~/.sonar/cache
          key: ${{ runner.os }}-sonar
      - uses: SonarSource/sonarqube-scan-action@v8
        env:
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
          SONAR_HOST_URL: ${{ vars.SONAR_HOST_URL }}
      - uses: SonarSource/sonarqube-quality-gate-action@v1
        env:
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
          SONAR_HOST_URL: ${{ vars.SONAR_HOST_URL }}
```

> 🧠 **¿Por qué `needs: secrets`?** El análisis de SonarQube tarda minutos. Si el job de secretos falla, tiene sentido **no gastar ese tiempo**: el PR ya está bloqueado. Es una decisión de eficiencia, no de seguridad.

### 11. Convierte el check en una puerta real

Un workflow que falla es decorativo si el PR se puede mergear igualmente.

**Settings → Rules → Rulesets → New ruleset** (o *Settings → Branches → Branch protection rules*):

```
Branch name pattern: main
☑ Require status checks to pass before merging
    ├─ Análisis SonarQube
    └─ SonarQube Quality Gate check
☑ Require branches to be up to date before merging
☑ Require pull request before merging
```

Ahora el Quality Gate es **bloqueante**, no informativo.

---

## ✅ Comprobación final

- [ ] Tengo `SONAR_TOKEN` como secret y `SONAR_HOST_URL` como variable en GitHub
- [ ] Mi workflow usa `fetch-depth: 0` y Java 21
- [ ] El cache de `~/.sonar/cache` acelera las ejecuciones
- [ ] Los tests y la cobertura se ejecutan **antes** del análisis
- [ ] El check del Quality Gate aparece en el PR y bloquea el merge
- [ ] Sé que la decoración del PR requiere edición de pago y no solo permisos en el workflow
- [ ] `sonar.projectVersion` no usa el número de build
- [ ] Entiendo las diferencias entre `sonarqube-scan-action` v5, v7 y v8
- [ ] Sé combinar Gitleaks y SonarQube en un pipeline con dependencias

---

## 🤔 Preguntas de reflexión

1. El action `sonarqube-scan-action` dejó de usar Docker y pasó a ser composite en la v5. ¿Por qué era un problema ejecutar Docker dentro de un runner de GitHub? Menciona al menos dos razones.
2. ¿Qué pasa si borras `fetch-depth: 0`? ¿Qué errores concretos verás en los logs del scanner?
3. Tu `SONAR_TOKEN` se filtra en un log público del pipeline. ¿Qué haces? *(Repasa el módulo de Gitleaks: mismo protocolo de rotación).*
4. `sonar.qualitygate.wait=true` y `sonarqube-quality-gate-action` resuelven lo mismo. ¿Cuándo elegirías cada uno? ¿Qué pasa con la duración del pipeline?
5. El check del Quality Gate está en verde, pero el PR se puede mergear igual porque nadie configuró la branch protection. ¿De quién es la responsabilidad: del equipo de plataforma, del manager o del desarrollador? ¿Cómo lo evitas en un repo nuevo?
6. Si el runner de GitHub no puede alcanzar tu SonarQube interno, ¿qué tres opciones hay? ¿Cuál aceptarías en una empresa de 500 personas y por qué?
7. ¿Tiene sentido ejecutar SonarQube en **cada commit** en vez de en cada PR? ¿Qué trade-off introduce?

---

## 🏁 Fin del módulo de SonarQube

Has cubierto las tres capas de Clean as You Code:

```
   Detectar  ──▶  Evaluar  ──▶  Bloquear  ──▶  Mejorar
   (IDE)         (Quality      (branch        (deuda
                  Gate)         protection)    técnica
                             congelada)
   (ej. 01)     (ej. 02)      (ej. 04)        (ej. 03)
```

**Siguiente paso recomendado:** elegir la tercera herramienta del curso. Candidates ORDERED por valor didáctico:

| Herramienta | Por qué |
|---|---|
| **Semgrep** | SAST moderno con reglas propias; complementa a SonarQube sin solaparse |
| **Trivy** | SCA + imágenes de contenedor + IaC en una sola herramienta |
| **Checkov** | IaC scanning puro, muy visual en los ejercicios |
| **OWASP ZAP** | DAST: el único escáner que ve tu app como la ve un atacante |

La estructura de cada módulo es siempre la misma: `README.md` de introducción (qué es, cómo se instala en Windows/Mac/Linux) + ejercicios numerados con fixtures verificados.
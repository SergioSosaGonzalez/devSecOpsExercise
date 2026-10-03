# Ejercicio 05 — Integración con CI/CD (GitHub Actions)

**Nivel:** 🔴 Avanzado · **Duración estimada:** 45 min

## 🎯 Objetivo

Añadir una capa de defensa en el servidor: un pipeline que escanea el código **en cada push y en cada pull request**, bloqueando el merge si detecta secretos.

## 📋 Requisitos previos

- [Ejercicio 04 completado](../04-pre-commit/README.md)
- Una cuenta de GitHub con Actions habilitado
- El repositorio de práctica hecho `push` a tu fork

---

## 🧠 La defensa en profundidad

Una buena arquitectura de seguridad **nunca depende de un solo control**:

```
   Capa 1                    Capa 2                     Capa 3
   Local (rápida)            Servidor (obligatoria)     Plataforma
   ─────────────             ──────────────────────      ──────────────
   pre-commit                GitHub Actions              Push Protection
   ~1 segundo                ~2 minutos                  Automática
   avatar: el developer      avatar: el repo             avatar: GitHub

   Si alguien salta la      Si alguien empuja con       Si alguien crea
   capa 1...                 --no-verify...             el repo fuera de
                                                       tu organización...
        │                          │                            │
        └──────────────────────────┴────────────────────────────┘
                                    │
                            Solo entonces estás cubierto
```

> 🎯 **La capa 2 no es opcional.** El pre-commit protege de la buena fe; el pipeline protege de los accidentes, de los `git push --force` y de los colaboradores con el hook desactivado.

---

## Pasos

### 1. Crea el workflow

Crea el archivo `.github/workflows/gitleaks.yml` con el contenido de [`gitleaks.yml`](.github/workflows/gitleaks.yml) que hay en esta carpeta, o usa este:

```yaml
name: Secret Scanning

on:
  push:
    branches: [main, master, develop]
  pull_request:
    branches: [main, master, develop]
  workflow_dispatch:      # permite ejecutarlo manualmente

permissions:
  contents: read

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  gitleaks:
    name: Escanear secretos
    runs-on: ubuntu-latest

    steps:
      - name: Checkout del repositorio
        uses: actions/checkout@v4
        with:
          fetch-depth: 0     # ⚠️ CRÍTICO: sin esto no se ve el historial

      - name: Ejecutar Gitleaks
        uses: gitleaks/gitleaks-action@v3
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

      - name: Publicar resultados en Code Scanning
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: gitleaks.sarif
          category: secret-scanning
```

---

### 2. ⚠️ El detalle que casi todos olvidan: `fetch-depth: 0`

Por defecto, `actions/checkout` hace un **shallow clone** (solo el último commit). Gitleaks en modo `git` necesita el **historial completo**.

```yaml
# ❌ INCORRECTO - el workflow pasa siempre
- uses: actions/checkout@v4

# ✅ CORRECTO
- uses: actions/checkout@v4
  with:
    fetch-depth: 0
```

> 💡 Para escanear solo lo nuevo en un PR, el workflow sería distinto (ver paso 5).

---

### 3. Sube el workflow a tu fork

```bash
git checkout -b exercise/gitleaks-ci
mkdir -p .github/workflows
# ...crea el archivo...
git add .github/workflows/gitleaks.yml
git commit -m "ci: add gitleaks secret scanning workflow"
git push origin exercise/gitleaks-ci
```

Abre el workflow manualmente desde la pestaña **Actions → Secret Scanning → Run workflow** para verificar que funciona.

---

### 4. Verifica que el pipeline falla con un secreto

Crea un Pull Request con un secreto:

```bash
git checkout -b test/pr-con-secreto
echo "GITHUB_TOKEN=ghp_FicticioParaElEjercicio000000000000000" > notas.txt
git add notas.txt
git commit -m "test: verificar que el pipeline detecta el secreto"
git push origin test/pr-con-secreto
```

Abre el PR y observa:

- El check **"Escanear secretos"** aparece en rojo ❌
- Los logs del job muestran el hallazgo
- Si publicaste SARIF, el secreto aparece como **alerta en la pestaña Security** del PR

Ahora **cierra el PR y borra la rama**: ese token es ficticio, pero el principio es que nunca debes dejar un secreto en un PR abierto.

---

### 5. Versión optimizada: escanear solo lo nuevo

En repositorios grandes, escanear todo el historial en cada PR es lento. La estrategia profesional es crear un **baseline** y escanear solo los commits del PR:

```yaml
name: Secret Scanning (solo lo nuevo)

on:
  pull_request:

permissions:
  contents: read

jobs:
  gitleaks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Determinar el rango de commits del PR
        id: range
        run: |
          echo "before=$(git rev-parse HEAD~1)" >> $GITHUB_OUTPUT
          echo "after=$(git rev-parse HEAD)" >> $GITHUB_OUTPUT

      - name: Escanear solo los commits nuevos
        run: |
          gitleaks git \
            --log-opts="--all ${{ steps.range.outputs.before }}..${{ steps.range.outputs.after }}" \
            --redact \
            --verbose \
            --report-path gitleaks.sarif \
            --report-format sarif \
            .
```

---

### 6. Versión ligera (sin action de terceros)

Si en tu organización están prohibidas las actions de terceros por política de supply chain:

```yaml
name: Secret Scanning (sin action externa)

on: [push, pull_request]

permissions:
  contents: read

jobs:
  gitleaks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Descargar Gitleaks
        run: |
          curl -sSfL https://raw.githubusercontent.com/gitleaks/gitleaks/master/install.sh | bash
          chmod +x gitleaks

      - name: Escanear
        run: ./gitleaks git --redact --verbose .
```

> 🔐 **Sobre supply chain:** ejecutar `curl | bash` en un runner tampoco es ideal. La forma más segura es fijar la action a un **SHA de commit** en lugar de una etiqueta de versión:
> ```yaml
> uses: gitleaks/gitleaks-action@<sha-de-40-caracteres>
> ```

---

### 7. Convierte el pipeline en un **branch protection rule**

Un workflow que falla es inútil si el PR se puede mergear de todos modos. Ve a:

**Settings → Branches → Add rule** (o **Settings → Rules → Rules**)

```
Branch name pattern:  main
☑ Require status checks to pass before merging
    └─ Status check: Escanear secretos
☑ Require branches to be up to date before merging
```

A partir de ese momento, **GitHub impide el merge** si Gitleaks no pasa. El control deja de ser informativo y pasa a ser bloqueante.

---

### 8. Activa GitHub Push Protection

Si tienes GitHub Enterprise Cloud o un plan que lo incluya, activa:

**Settings → Code security and analysis → Secret scanning → Push protection**

Esto añade una capa superior: GitHub **rechaza el push directamente** si detecta un segredo de un proveedor conocido, sin necesidad de pipeline. Es la defensa más temprana posible, ya que ocurre antes incluso de que el commit exista en el servidor.

---

### 9. Manejo de falsos positivos en CI

Si un PR legítimo falla por un falso positivo, las opciones son:

| Opción | Cuándo usarla |
|---|---|
| Corregir el código (lo correcto) | Casi siempre |
| `gitleaks:allow` en la línea | Valores de prueba claramente identificados |
| `.gitleaksignore` | Hallazgos concretos ya verificados |
| Allowlist en `.gitleaks.toml` | Patrones estructurales (fixtures, lockfiles) |
| Desactivar la regla | Solo como último recurso, nunca de forma global |

❌ **Nunca** marques el check como "no requerido" para desbloquearte. Eso destruye el control para todo el repositorio.

---

### 10. Mide la eficacia del control

Añade métricas al pipeline. En repositorios maduros esto es habitual:

```yaml
      - name: Resumen de hallazgos
        if: always()
        run: |
          if [ -f gitleaks-report.json ]; then
            TOTAL=$(python3 -c "import json; print(len(json.load(open('gitleaks-report.json'))))")
            echo "### 🔐 Hallazgos de secretos: $TOTAL" >> $GITHUB_STEP_SUMMARY
            echo "| Archivo | Regla | Línea |" >> $GITHUB_STEP_SUMMARY
            echo "|---------|-------|-------|" >> $GITHUB_STEP_SUMMARY
            python3 -c "
            import json
            for h in json.load(open('gitleaks-report.json')):
                print(f\"| {h['File']} | {h['RuleID']} | {h['StartLine']} |\")
            " >> $GITHUB_STEP_SUMMARY
          fi
```

El `GITHUB_STEP_SUMMARY` escribe directamente en la página del run un resumen legible sin abrir los logs.

---

## ✅ Comprobación final

- [ ] Tengo un workflow de Gitleaks en `.github/workflows/`
- [ ] Entiendo por qué `fetch-depth: 0` es imprescindible
- [ ] Mi workflow falla correctamente ante un PR con secreto
- [ ] He configurado un branch protection rule que bloquea el merge
- [ ] Sé generar un reporte SARIF para Code Scanning
- [ ] Conozco las alternativas sin actions de terceros y sus riesgos

---

## 🤔 Preguntas de reflexión

1. ¿Por qué el `--no-verify` en `git commit` no es un problema en CI, pero sí lo sería si solo tuvieras pre-commit?
2. Si un atacante con acceso de escritura al repositorio puede modificar `.github/workflows/`, ¿qué lo impide? ¿Cómo lo previenes? *(Investiga CODEOWNERS)*
3. ¿Cuándo es preferible escanear todo el historial a crear un baseline y escanear solo lo nuevo? ¿Cuándo ocurre al revés?
4. ¿Cómo justificarías ante un jefe la inversión en "perder" 2 minutos por pipeline en un control de seguridad?

---

## ⏭️ Siguiente

[Ejercicio 06 — Remediación de secretos filtrados →](../06-remediacion/README.md)

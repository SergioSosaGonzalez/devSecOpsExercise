---
name: nuevo-modulo-devsecops
description: Use when the user asks to create a new DevSecOps course module or exercise folder for a security tool (trivy, semgrep, checkov, tfsec, OWASP ZAP, dependabot, codeql, grype, falco, nancy, snyk, detect-secrets, trufflehog, terrascan, kube-bench, zap, securityheaders, testssl, sslyze, osv-scanner, seatbelt, prowler, opengrep, bearer, gitguardian). Generates the tool README plus up to 3 numbered exercises with fixtures, in Spanish, matching the existing gitleaks/ and sonarqube/ modules.
---

# Nuevo módulo DevSecOps

Genera un módulo de curso nuevo con la misma estructura que `gitleaks/` y `sonarqube/`.

## Paso 0 — Pregunta la herramienta (obligatorio, antes de escribir nada)

Si el usuario no ha dicho qué herramienta quiere, **pregunta**:

> ¿Qué herramienta quieres añadir al curso? (ej. trivy, semgrep, checkov, OWASP ZAP, CodeQL…)

No adivines ni elijas tú. Si la nombra vagamente ("una de SCA"), pide una concreta.

Después de que responda, **verifica la herramienta antes de escribir**: su instalación real, sus comandos, sus flags y su estado actual en 2026. Usa `websearch`/`webfetch` contra la documentación oficial. No escribas comandos de memoria — el curso entero se apoya en que los comandos funcionen.

## Paso 1 — Planifica (todowrite)

Investiga y responde antes de escribir:

- ¿Qué problema de DevSecOps resuelve? ¿En qué etapa del Shift Left encaja?
- ¿Cuáles son sus **3 conceptos centrales**? (En gitleaks: modos de escaneo, allowlists, fingerprints. En SonarQube: Quality Profile, Quality Gate, New Code.)
- ¿Cuál es la **curva de aprendizaje** para alguien que acaba de empezar?
- ¿Qué tiene que ser **ficticio** en los fixtures (secretos, CVEs, recursos)?

**Máximo 3 ejercicios.** El curso va de menor a mayor dificultad y cada uno se apoya en el anterior:

| # | Nivel | Objetivo típico |
|---|---|---|
| 01 | 🟢 Básico | Instalar, verificar, primer comando, leer la salida |
| 02 | 🟡 Intermedio | El flujo real: analizar → interpretar → decidir |
| 03 | 🔴 Avanzado | Integrar, automatizar o limpiar (CI, tuning, remediación) |

Si la herramienta da para 4 o 5, **corta**. Es preferible 3 ejercicios completos que 5 superficiales.

## Paso 2 — Crea la estructura

```
<herramienta>/
├── README.md                    ← obligatorio, teórico
├── .gitleaksignore              ← solo si el módulo tiene secretos en su doc
└── 01-<tema>/
    ├── README.md
    └── fixtures/                ← material de trabajo
```

- Nombre de carpeta en minúsculas, sin tildes: `owasp-zap`, `semgrep`.
- Ejercicios `NN-tema/` en orden creciente de dificultad.
- `fixtures/`, `scripts/`, `config/` son los únicos carpetas de apoyo permitidas.
- `solucion/` solo si hay algo que comparar.

## Paso 3 — Escribe el README del módulo

Estructura obligatoria, en español, con estos títulos exactos:

```
# <Emoji> <Herramienta> — <subtítulo>
> **Categoría:** ... · **Etapa del Shift Left:** ... · **Licencia:** ...
## 1. ¿Qué es <herramienta>?
## 2. Características principales          ← tabla
   ### Limitaciones que debes conocer       ← obligatorio
## 3. Instalación                            ← macOS / Linux / Windows / Docker
   ### ✅ Verificación de la instalación
## 4. Uso básico
## 5. Uso avanzado                           ← subsectionsnumerados
## 6. Códigos de salida y troubleshooting    ← tabla problema|causa|solución
## 7. Qué hacer cuando <herramienta> encuentra <algo>
## 8. Ejercicios de esta carpeta             ← tabla + smoke test
## 9. Referencias                            ← URLs oficiales reales
## 10. Glosario rápido                       ← tabla
```

Requisitos de contenido:

- **Sección 1**: qué es, analogía útil, por qué importa, dónde encaja en el flujo. Un diagrama ASCII del flujo.
- **Limitaciones**: obligatorias. Sin ellas el curso miente. Ejemplos reales: *no reescribe el historial*, *falsos positivos*, *necesita servidor*.
- **Instalación**: las 4 variantes de SO, con comandos copiables.
- **Troubleshooting**: problemas que un principiante **de verdad** se va a encontrar, no inventados.
- **Sección 8**: la tabla de ejercicios + el **smoke test** (ver más abajo).

Sé factual. Si una característica es de pago, experimental o está en retirada, dilo en la sección de limitaciones con su fecha.

## Paso 4 — Escribe los ejercicios

Cada `NN-<tema>/README.md` sigue esta estructura exacta:

```markdown
# Ejercicio NN — <Título>

**Nivel:** 🟢 Básico | 🟡 Intermedio | 🔴 Avanzado · **Duración estimada:** NN min

## 🎯 Objetivo

## 📋 Requisitos previos

---

## Pasos

### 1. <Paso>
### 2. <Paso>

---

## ✅ Comprobación final

- [ ] ...

---

## 🤔 Preguntas de reflexión

1. ...

---

## ⏭️ Siguiente

[Ejercicio NN+1 — <Título> →](../NN+1-<tema>/README.md)
```

Reglas de los pasos:

- **Numerados**, en imperativo, con el comando exacto en bloque `bash`.
- **Cada paso con salida esperada** en bloque de código. El alumno compara su pantalla con la tuya; si no puede, no puede verificar.
- **Bloques `>` para las advertencias** y el "por qué esto importa". No es relleno: es donde vive el criterio profesional.
- **Cruce entre ejercicios**: `- [Ejercicio 02 completado](../02-escaneo-basico/README.md)`.
- El último ejercicio **no** lleva enlace "Siguiente".
- **Las preguntas de reflexión son la parte más importante.** No preguntes "¿qué hace este comando?". Pregunta cosas donde la respuestaTG no sea evícita y haya un trade-off real:
  - "¿Por qué una allowlist global por ruta es más peligrosa que una por regla?"
  - "Tu compañero añade `tests/` a la allowlist 'para que deje de molestar'. ¿Qué secretos reales podrían colarse?"
- Las tablas de "números verificados" (X hallazgos → Y hallazgos) son muy goodies: obligan al alumno a medir.

## Paso 5 — Fixtures deliberadamente defectuosos

Los fixtures **no son código real: son material de laboratorio con fallos inyectados a propósito.** Esto es lo más importante del módulo y lo que más fácil se ruin por error.

- Secretos **inventados** con formato realista (`ghp_`, `AKIA`, `sk_live_`, `xoxb-`). Los exercise 02 de gitleaks lo blocking.
- Bugs, vulnerabilidades, duplicación, código muerto: entre 5 y 10 por fichero. Cada uno con un comentario `# --- Error N: ... ---`.
- Cabecera en cada fixture declarando que es de prueba.
- Si son Python: deben **compilar y tener tests que pasan**. Es el smoke test del curso.

```bash
python3 -m py_compile <modulo>/*/fixtures/src/*.py <modulo>/*/fixtures/tests/*.py
for d in <modulo>/0[123]*/fixtures; do (cd $d && python3 -m pytest -q); done
```

Si el alumno debe arreglar código (no solo analizarlo), deja los tests **en verde** sobre el código defectuoso: prueban que el programa hace lo que debe, no que esté limpio. Los issues los encuentra la herramienta, no el test.

## Paso 6 — Smoke test (obligatorio)

Añade en la sección 8 del README del módulo, con los **números reales**:

> 🧪 **Prueba de humo del curso:** ejecuta esto y deberías obtener N hallazgos
> ```bash
> cd <herramienta> && <herramienta> <scan> . --redact -v
> ```

**Ejecuta el comando y cuenta. No inventes el número.** Si no lo has ejecutado, el smoke test es una mentira.

## Paso 7 — `.gitleaksignore` (solo si aplica)

Si el README del módulo o los enunciados contienen tokens de ejemplo que la herramienta detecta, crea `<herramienta>/.gitleaksignore`.

**Los fingerprints llevan número de línea:** `<ruta>:<ruleID>:<línea>`. Cualquier edición posterior que añada o quite líneas en esos README invalida la entrada.

Genera con `--report-path reporte.json`, copia el campo `Fingerprint` de lo que sea documentación, y **no** ignores nada de `fixtures/` — los fixtures deben seguir detectándose, son el material del curso.

## Paso 8 — Registra en el README raíz

Añade una fila a la tabla "Índice de herramientas" del `README.md` raíz:

```markdown
| [Nombre](<carpeta>/README.md) | <Categoría> | <Etapa del Shift Left> | ✅ N ejercicios |
```

**Es lo único que se toca en el README raíz.** No lo reformatees ni lo reescribas.

## Paso 9 — Verifica antes de dar por terminado

```bash
# 1. El smoke test del módulo devuelve el número que dice el README
cd <herramienta> && <herramienta> <scan> . --redact -v | tail -3

# 2. Si hay Python: compila y los tests pasan
python3 -m py_compile <modulo>/*/fixtures/src/*.py <modulo>/*/fixtures/tests/*.py
for d in <modulo>/0[123]*/fixtures; do (cd $d && python3 -m pytest -q); done

# 3. Los enlaces entre READMEs resuelven
grep -o '\.\./[0-9][0-9]-[^/]*' <modulo>/*/README.md | while read p; do
  (cd <modulo>/*/ && ls "$p"/README.md) 2>/dev/null || echo "ROTO: $p"
done

# 4. Ningún secreto real se ha colado
gitleaks dir . --report-path /tmp/verificacion.json --redact
```

Si el paso 1 no coincide con el número del README, corrige el README. Si el 2 falla, el fixture está mal.

## Errores que se repiten

- **Escribir comandos sin ejecutarlos.** Cada bloque `bash` del curso debe funcionar tal cual.
- **Inventar el conteo del smoke test.** Es el error más grave: desincroniza el módulo entero.
- **"Arreglar" los fixtures.** Los bugs y los falsos positivos son el contenido del curso.
- **Meter tokens reales por error.** Búscalos con `gitleaks` antes de terminar.
- **Escribir 5 ejercicios.** Pide máximo 3.
- **Hacer el README del módulo un glosario en vez de una guía.** La instalación y el troubleshooting valen más que el Concepto bien explicado.
- **Tocar el README raíz más allá de la tabla.**
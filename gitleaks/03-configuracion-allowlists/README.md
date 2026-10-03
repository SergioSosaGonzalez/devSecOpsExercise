# Ejercicio 03 — Configuración y allowlists

**Nivel:** 🟡 Intermedio · **Duración estimada:** 35 min

## 🎯 Objetivo

Reducir el ruido de Gitleaks hasta que un hallazgo signifique realmente "hay que actuar". Aprenderás las tres mecanismos para hacerlo: `gitleaks:allow`, `.gitleaksignore` y `.gitleaks.toml`.

## 📋 Requisitos previos

- [Ejercicio 02 completado](../02-escaneo-basico/README.md)

> 🧠 **Por qué este ejercicio es crítico:** una herramienta de seguridad que genera 200 falsos positivos por ejecución **no se usa**. El tuning no es opcional: es la diferencia entre un control efectivo y un control ignorado.

---

## 📦 Material de trabajo

`fixtures/` contiene **falsos positivos deliberados**: datos que no son credenciales pero que Gitleaks detecta como si lo fueran.

```bash
cd gitleaks/03-configuracion-allowlists
```

---

## Pasos

### 1. Reproduce el problema

```bash
gitleaks dir -v ./fixtures
```

Cuenta los hallazgos:

```bash
gitleaks dir ./fixtures --report-path antes.json
python3 -c "import json; d=json.load(open('antes.json')); print(len(d), 'hallazgos')"
```

Ahora mira cuántos de ellos son **reales**:

```bash
gitleaks dir ./fixtures -v 2>&1 | grep -E "File:|RuleID:"
```

**Pregunta clave:** ¿qué proporción de los hallazgos son falsos positivos? Esa es la métrica que vamos a reducir.

---

### 2. Mecanismo 1 — `gitleaks:allow` (ignorancia por línea)

Para un secreto o un valor de prueba que está en **una línea concreta y conocida**, lo más limpio es documentarlo en esa misma línea.

Crea el archivo `fixtures/con-solo-local.yaml`:

```yaml
# Valores de prueba - SOLO para el entorno local
local_api_key: "sk_test_FicticiaParaSandbox0000000000"  # gitleaks:allow
```

Vuelve a escanear:

```bash
gitleaks dir -v ./fixtures/con-solo-local.yaml
echo "exit code: $?"
```

Ahora ese hallazgo desaparece.

> ⚠️ **Regla:** `# gitleaks:allow` es una **declaración de intención**. Úsalo solo cuando estés 100% seguro de que el valor no es un secreto. Si te equivocas una vez, has creado un agujero en tu control.
>
> **Nunca** pongas `gitleaks:allow` en un archivo que contenga secretos reales "porque total no lo usamos".

---

### 3. Mecanismo 2 — `.gitleaksignore` (ignorar hallazgos concretos)

`.gitleaksignore` trabaja con **Fingerprints**, no con rutas. Cada fingerprint identifica un hallazgo de forma única y estable.

#### Paso 3.1 — Genera el reporte

```bash
gitleaks dir -v ./fixtures --report-path hallazgos.json
```

#### Paso 3.2 — Extrae los fingerprints

```bash
python3 - <<'EOF'
import json
with open("hallazgos.json") as f:
    for h in json.load(f):
        print(f'{h["File"]}:{h["StartLine"]}  ->  {h["Fingerprint"]}')
EOF
```

#### Paso 3.3 — Crea el `.gitleaksignore`

Copia los fingerprints de los hallazgos que has verificado que son falsos positivos. Estos son los 5 que produces los fixtures de este ejercicio:

```
# .gitleaksignore

# Formato en modo `dir`:    <ruta>:<ruleID>:<línea>
fixtures/app/src/config.py:generic-api-key:8
fixtures/app/src/config.py:stripe-access-token:14
fixtures/app/src/config.py:generic-api-key:20
fixtures/tests/fixtures/config_test.yml:generic-api-key:9
fixtures/tests/fixtures/config_test.yml:stripe-access-token:16
```

> 📌 En modo `git` el formato **incluye el hash del commit** al principio: `<commit-sha>:<ruta>:<ruleID>:<línea>`.

> 💡 Para modo `git` el fingerprint sí incluye el hash del commit:
> ```
> cd5226711335c68be1e720b318b7bc3135a30eb2:app/config.py:generic-api-key:8
> ```

#### Paso 3.4 — Verifica

```bash
gitleaks dir -v ./fixtures --report-path despues.json
python3 -c "import json; print(len(json.load(open('despues.json'))), 'hallazgos restantes')"
```

Los hallazgos ignorados ya no aparecen. **El resto sigue detectándose.**

---

### 4. Mecanismo 3 — `.gitleaks.toml` (configuración por regla)

Cuando los falsos positivos comparten un **patrón estructural** (siempre en `tests/`, siempre en un `package-lock.json`), lo correcto es una allowlist por regla, no ignorar 200 fingerprints uno a uno..

#### Opción A — Allowlist global por rutas

Crea `.gitleaks.toml` en la raíz del ejercicio:

```toml
title = "Configuración de gitleaks para los ejercicios"

[extend]
useDefault = true

# Allowlist global: ignora por ruta, sea cual sea la regla
[[allowlists]]
description = "Los fixtures de pruebas no contienen secretos reales"
paths = [
  '''fixtures/tests/fixtures/''',
  '''fixtures/app/src/config\.py''',
]
```

```bash
gitleaks dir -v -c .gitleaks.toml ./fixtures
```

#### Opción B — Allowlist específica por regla

Más quirúrgica: ignora **solo** la regla `generic-api-key` en ese path, y **mantiene activas todas las demás**.

```toml
title = "Allowlist por regla"

[extend]
useDefault = true

# targetRules (disponible desde v8.25.0) acota la allowlist a reglas concretas
[[allowlists]]
description = "Los placeholders de la documentación no son credenciales"
targetRules = ["generic-api-key"]
paths = [ '''fixtures/app/src/config\.py''' ]
```

**Compruébalo** escaneando el mismo directorio con y sin esta configuración:

```bash
# Sin allowlist por regla  → 5 hallazgos
gitleaks dir ./fixtures -v 2>&1 | tail -1

# Con allowlist por regla  → 3 hallazgos
gitleaks dir ./fixtures -c .gitleaks.toml -v 2>&1 | tail -1
```

Desaparecen los 2 `generic-api-key` de `config.py`, pero el `stripe-access-token` de ese **mismo archivo** se sigue detectando. Eso es justo lo que hace segura esta opción frente a la global por ruta.

> 🧠 **Preferencia general:** usa la **opción B** siempre que sea posible. Una allowlist global por ruta desactiva *todas* las reglas en ese path, y mañana alguien meterá un AWS key real en `tests/` y nadie lo verá.

#### Opción C — Desactivar una regla ruidosa

Si una regla concreta genera demasiado ruido y no te sirve:

```toml
[extend]
useDefault = true

# Desactiva la regla más ruidosa de todas
disabledRules = ["generic-api-key"]
```

> 🚨 **Esta es la opción más peligrosa.** `generic-api-key` es la que detecta contraseñas genéricas de bases de datos — justamente las que más te importan. Desactívala solo si tienes una regla propia que cubra ese hueco, y nunca como primera solución.

---

### 5. Reemplaza la regla genérica por una propia

En vez de desactivar `generic-api-key`, **mejórala**. Así sigues detectando contraseñas pero con menos ruido:

```toml
title = "Regla de contraseñas propia"

[extend]
useDefault = true

# Extiende la regla existente heredando sus atributos
[[rules]]
id = "generic-api-key"
keywords = ["password", "passwd", "pwd", "secret", "token", "apikey", "api_key"]

# Reescribe el regex para exigir formato más estricto
regex = '''(?i)(?:password|passwd|pwd|secret|token|apikey|api_key)\s*[:=]\s*['"]?([a-zA-Z0-9!@#$%^&*_\-]{12,})['"]?'''

secretGroup = 1
# Exige entropía mínima: descarta "password123" y "admin"
entropy = 3.2
```

```bash
gitleaks dir -v -c .gitleaks.toml ./fixtures
```

**Comprueba el efecto:** los 5 hallazgos del paso 1 se reducen a 4. El
`generic-api-key` descartado era el que correspondía a un valor de baja entropía
demasiado parecido a un secreto pero que no lo era.

---

### 6. Reglas compuestas (`required`)

Desde la v8.28.0, una regla puede exigir que **otra regla también coincida** en las líneas cercanas. Es la herramienta más potente contra falsos positivos, porque permite exigir **contexto**, no solo forma.

La sintaxis exige que la regla auxiliar esté **definida** en la configuración y que la principal la referencie por su `id`:

```toml
title = "Regla compuesta"

[extend]
useDefault = true

# 1. La regla AUXILIAR: marca líneas que hablan de producción o staging
[[rules]]
id = "contexto-produccion"
description = "Detecta referencias a entornos productivos"
regex = '''(?i)(prod|production|staging)\b'''
keywords = ["prod", "staging"]

# 2. La regla PRINCIPAL: la clave AWS
[[rules]]
id = "aws-key-en-contexto-de-produccion"
description = "Clave AWS solo si aparece junto a una referencia a producción"
regex = '''AKIA[0-9A-Z]{16}'''
secretGroup = 0
entropy = 3.0

# 3. La condición: la principal SOLO dispara si la auxiliar coincide
#    dentro de las 10 líneas siguientes o anteriores
[[rules.required]]
id = "contexto-produccion"
withinLines = 10
# withinColumns = 80    # opcional: acota también horizontalmente
```

**Qué consigue:** una clave AWS en un fichero de test sin mencionar producción **no se reporta**; la misma clave junto a un `production = true` **sí**.

> ⚠️ **Limitación conocida:** la regla auxiliar (`contexto-produccion`) **también aparece en el reporte**, porque es una regla válida por derecho propio. Es un comportamiento incómodo pero conocido de las composite rules. Soluciones prácticas:
> - Filtrar por `RuleID` al consumir el reporte JSON.
> - Marcar las líneas de contexto con `# gitleaks:allow` si son fijas.
> - Usar una auxiliar cuyo `regex` sea muy específico para reducir el ruido.

> 📌 Si escribes un `id` en `[[rules.required]]` que **no** exista en la configuración, Gitleaks aborta con:
> `Failed to load config: error="<regla>: [[rules.required]] rule ID 'X' does not exist"`

Con esto, una clave AWS en un test no se reporta, pero la misma clave junto a una referencia a `production` sí.


---

### 7. Orden de precedencia de la configuración

Gitleaks carga la configuración en este orden. Verifícalo:

```bash
# 1. Flag (máxima prioridad)
gitleaks dir -c .gitleaks.toml ./fixtures

# 2. Variable de entorno con la RUTA
export GITLEAKS_CONFIG="$PWD/.gitleaks.toml"
gitleaks dir ./fixtures

# 3. Variable de entorno con el CONTENIDO
export GITLEAKS_CONFIG_TOML="$(cat .gitleaks.toml)"
gitleaks dir ./fixtures

# 4. .gitleaks.toml en la raíz de la ruta escaneada (automático)
gitleaks dir ./fixtures
```

---

### 8. Resultado final esperado

Compara el antes y el después:

```bash
gitleaks dir -v ./fixtures \
  --report-path antes.json

gitleaks dir -v -c .gitleaks.toml ./fixtures \
  --report-path despues.json

python3 - <<'EOF'
import json
antes = len(json.load(open("antes.json")))
despues = len(json.load(open("despues.json")))
print(f"Hallazgos: {antes} -> {despues}")
print(f"Falsos positivos eliminados: {antes - despues}")
EOF
```

**Números verificados de esta configuración:**

| Configuración | Hallazgos |
|---|---|
| Sin ningún ajuste (paso 1) | 5 |
| Con `.gitleaksignore` (paso 3) | 0 |
| Con allowlist global por ruta (opción A) | 0 |
| Con allowlist por regla `targetRules` (opción B) | 3 |
| Con `disabledRules = ["generic-api-key"]` (opción C) | 2 |
| Con regla propia de contraseñas + entropía 3.2 (paso 5) | 4 |

Fíjate en que **la opción C da el mejor número (2) y es la peor elección**: ha desactivado justo la regla que detecta contraseñas de base de datos. Este es el ejemplo perfecto de por qué "menos hallazgos" no significa "mejor configuración".

> 🎯 El objetivo no es "0 hallazgos": es que **cada hallazgo restante sea un secreto real**, y que el control siga siendo estricto.

---

## ✅ Comprobación final

- [ ] Sé cuándo usar `gitleaks:allow`, `.gitleaksignore` y `.gitleaks.toml`
- [ ] Entiendo que `.gitleaksignore` trabaja con fingerprints, no con rutas
- [ ] Sé por qué una allowlist global por ruta es más peligrosa que una por regla
- [ ] Sé escribir una regla propia que sustituya a `generic-api-key`
- [ ] Entiendo qué es una regla compuesta y cuándo usarla
- [ ] Conozco el orden de precedencia de la configuración

---

## 🤔 Preguntas de reflexión

1. ¿En qué se diferencian `.gitleaksignore` y una allowlist en `.gitleaks.toml` desde el punto de vista de mantenimiento? ¿Cuál escala mejor en un equipo de 50 personas?
2. Imagina que un compañero añade `tests/` a la allowlist global "para que deje de molestar". ¿Qué clase de secretos reales podrían colarse a partir de ese momento?
3. ¿Por qué el `Fingerprint` incluye el número de línea? ¿Qué pasaría si una línea se inserta arriba y todas las referencias de `.gitleaksignore` dejaran de coincidir?
4. En un proyecto real, ¿qué métrica usarías para decidir si tu configuración está bien ajustada?

---

## ⏭️ Siguiente

[Ejercicio 04 — Pre-commit hook →](../04-pre-commit/README.md)

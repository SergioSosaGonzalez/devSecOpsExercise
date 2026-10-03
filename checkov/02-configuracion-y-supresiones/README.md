# Ejercicio 02 — Configuración y supresiones

**Nivel:** 🟡 Intermedio · **Duración estimada:** 30 min

## 🎯 Objetivo

Decidir qué se escanea y, sobre todo, **dejar escrito por qué**. En este ejercicio el Terraform ya está medio arreglado y el problema es de política: qué checks ejecuta la empresa, dónde se declara esa decisión, qué se silencia con un motivo y qué trade-off acepta cada mecanismo.

Vas a medir el impacto de cada decisión. Al terminar sabrás por qué una allowlist global (`check:`) es más peligrosa que una denylist (`skip-check:`), por qué un `#checkov:skip=` tiene que ir **dentro** del bloque del recurso y por qué Checkov ve un fallo que no aparece escrito en ningún `.tf`.

## 📋 Requisitos previos

- [Ejercicio 01 completado](../01-escaneo-basico/README.md)
- Checkov instalado y con `checkov --version` funcionando

---

## Pasos

### 1. Mid el estado de partida

```bash
cd checkov/02-configuracion-y-supresiones/fixtures
checkov -d . --compact
```

**Salida esperada:**

```
Passed checks: 55, Failed checks: 17, Skipped checks: 1
```

**17 fallos y 1 omitido.** Ese `Skipped: 1` es importante: hay una supresión ya escrita en el código, en `01-almacenamiento.tf`, sobre el bucket de logs. Fíjate en que Checkov **te la enseña**:

```bash
checkov -d . --compact | grep -A3 "SKIPPED for resource"
```

**Salida esperada:**

```
	SKIPPED for resource: aws_s3_bucket.logs
	Suppress comment: los buckets de logs no se replican; la retención se define en lifecycle
	File: /01-almacenamiento.tf:49-62
```

Tres cosas que leer aquí: el recurso afectado, el motivo escrito y el fichero. **Una supresión silenciosa no aparece en la salida; esta sí.** Ese contraste es justo la diferencia entre una supresión que se puede auditar y una que se puede perder.

### 2. Allowlist: el experimento peligroso

Ejecuta solo tres checks concretos:

```bash
checkov -d . --compact --check CKV_AWS_24,CKV_AWS_17,CKV_AWS_20
```

**Salida esperada:**

```
Passed checks: 4, Failed checks: 1, Skipped checks: 0
```

De 17 a **1**. Has apagado más de mil comprobaciones para quedarte con tres. Comprueba qué queda sin mirar nunca más:

```bash
checkov -d . --compact --quiet --check CKV_AWS_24,CKV_AWS_17,CKV_AWS_20 | grep -c "FAILED for resource"
```

**Salida esperada:**

```
1
```

Un único fallo, el del bucket de logs. Los otros 16 no los has arreglado: has decidido que no existen.

> **Una allowlist de checks solo sirve para depurar un check concreto.** Nunca va en `.checkov.yaml` como configuración permanente. Si alguien la usa así y nadie lo detecta durante seis meses, tu pipeline lleva seis meses validando tres reglas.

### 3. Denylist: la opción defendible

```bash
checkov -d . --compact --skip-check CKV_AWS_144,CKV_AWS_145
```

**Salida esperada:**

```
Passed checks: 54, Failed checks: 15, Skipped checks: 0
```

**15 frente a 17.** Bajan los dos checks que has excluido y nada más. El resto del catálogo sigue entero.

> **La diferencia entre las dos estrategias es la diferencia entre ignorance y deuda.** La allowlist dice "no me importa lo que no conozco". La denylist dice "esto no aplica aquí, y aquí está el motivo". Solo la segunda es auditable.

Repite la cuenta con un comodín, que es como se excluye una familia entera de checks:

```bash
checkov -d . --compact --skip-check "CKV_AWS_14*"
```

**Salida esperada:**

```
Passed checks: 54, Failed checks: 15, Skipped checks: 0
```

El mismo resultado con una regla: `CKV_AWS_14*` cubre las 140, 144 y 145. Los comodines son cómodos y peligrosos: nadie recuerda qué había dentro del rango cuando lo escribió.

### 4. Descubre el fichero de configuración

En `config/.checkov.yaml` tienes la configuración candidata de la empresa:

```bash
cat config/.checkov.yaml
```

**Salida esperada:**

```yaml
compact: true
quiet: true

framework:
  - terraform

skip-check:
  - CKV_AWS_144   # replicación entre regiones: no aplica a los buckets de logs
  - CKV_AWS_145   # el cifrado por defecto lo fija la cuenta, no el repositorio

check:
  - CKV_AWS_24    # SSH no puede estar abierto a 0.0.0.0/0
  - CKV_AWS_17    # ninguna base de datos puede ser pública
  - CKV_AWS_20    # ningún bucket con ACL pública

evaluate-variables: true
```

> **Por qué este fichero se llama `.checkov.yaml` pero vive en `config/`.** Checkov carga automáticamente el `.checkov.yaml` que encuentre **en el directorio que escanea**. Si estuviera en la raíz de `fixtures/`, contaminaría desde el paso 1 todas tus mediciones. Aquí está escondido a propósito: solo se carga cuando tú lo pides.

Aplícalo:

```bash
checkov -d . --config-file config/.checkov.yaml
```

**Salida esperada:**

```
Passed checks: 4, Failed checks: 1, Skipped checks: 0
```

**El fichero declara `skip-check:` y aun así el resultado es el de la allowlist.** Compruébalo quitando ese bloque en una copia:

```bash
grep -v -E "^(check:|  - CKV_AWS_24|  - CKV_AWS_17|  - CKV_AWS_20)" config/.checkov.yaml > /tmp/solo-skip.yaml
checkov -d . --config-file /tmp/solo-skip.yaml
```

**Salida esperada:**

```
Passed checks: 54, Failed checks: 15, Skipped checks: 0
```

**No es una intersección: es una sustitución.** Si defines `check:`, ese bloque **reemplaza** al catálogo entero y el `skip-check:` se queda sin efecto. Quien escribió el fichero pensaba que estaba añadiendo tres reglas obligatorias; en realidad había apagado mil.

> **Regla de oro:** si necesitas que tres checks se ejecuten **aunque alguien añada un `skip-check`**, el sitio no es el fichero de configuración. Es una rama protegida, un CODEOWNERS, o una revisión obligatoria. Checkov no tiene "allowlist bloqueada" por diseño: si el fichero se puede editar en un pull request cualquiera, la allowlist se puede vaciar en un pull request cualquiera.

### 5. Congela tu configuración actual

`--create-config` escribe un `.checkov.yaml` con lo que Checkov considera configuración persistente:

```bash
checkov -d . --compact --check CKV_AWS_24 --create-config /tmp/mi-config.yaml
cat /tmp/mi-config.yaml
```

**Salida esperada:**

```yaml
block-list-secret-scan: []
branch: master
custom-tool-name: Checkov
directory:
- .
evaluate-variables: true
external-modules-download-path: .external_modules
mask: []
secrets-history-timeout: 12h
secrets-scan-file-type: []
summary-position: top
```

Fíjate en que **`check` y `compact` no aparecen**: `--create-config` no vuelca los flags de consola, congela la configuración base. Es un punto de partida, no un espejo.

Y para ver qué está usando Checkov ahora mismo, con su origen:

```bash
checkov -d . --show-config
```

**Salida esperada:**

```
Command Line Args:   -d . --show-config
Defaults:
  --branch:          master
  --external-modules-download-path:.external_modules
  --evaluate-variables:True
  --secrets-scan-file-type:[]
  --block-list-secret-scan:[]
  --summary-position:top
  --mask:            []
  --secrets-history-timeout:12h
  --custom-tool-name:Checkov
```

### 6. Escribe una supresión con motivo

Comprueba que la supresión actual funciona. En `01-almacenamiento.tf`, el bucket de logs lleva el comentario **dentro** del bloque:

```bash
cp 01-almacenamiento.tf /tmp/almacenamiento.bak
grep -A12 'resource "aws_s3_bucket" "logs"' 01-almacenamiento.tf
```

**Salida esperada:**

```hcl
resource "aws_s3_bucket" "logs" {
  bucket = "empresa-logs-2024"

  # El recurso no dice "public-read" en ninguna parte: lo hereda
  # del default de variables.tf. Por eso este hallazgo solo aparece
  # si Checkov resuelve variables.
  acl = var.acl_logs

  #checkov:skip=CKV_AWS_144:los buckets de logs no se replican; la retención se define en lifecycle

  tags = {
    Entorno = "produccion"
  }
}
```

Quítala y mide:

```bash
grep -v "checkov:skip" /tmp/almacenamiento.bak > 01-almacenamiento.tf
checkov -d . --compact | grep "Passed checks"
```

**Salida esperada:**

```
Passed checks: 55, Failed checks: 18, Skipped checks: 0
```

**18 fallos, 0 omitidos.** La supresión ha desaparecido: el hallazgo vuelve.

Ahora colócala en el sitio **equivocado**, en la línea anterior al recurso:

```bash
python3 - <<'EOF'
ruta = "01-almacenamiento.tf"
texto = open(ruta).read()
texto = texto.replace(
    "  #checkov:skip=CKV_AWS_144:los buckets de logs no se replican; la retención se define en lifecycle\n",
    "",
)
texto = texto.replace(
    'resource "aws_s3_bucket" "logs" {',
    "#checkov:skip=CKV_AWS_144:los buckets de logs no se replican\nresource \"aws_s3_bucket\" \"logs\" {",
)
open(ruta, "w").write(texto)
EOF
checkov -d . --compact | grep "Passed checks"
```

**Salida esperada:**

```
Passed checks: 55, Failed checks: 18, Skipped checks: 0
```

**Sigue fallando y `Skipped` sigue a 0.** El comentario está fuera de las llaves del recurso y no silencia nada. Lo grave no es que falle: es que quien la escribió va a creer que ha funcionado, porque no hay ningún aviso en la salida.

Pruébalo en la otra posición intuitiva, en la propia línea del `resource`:

```bash
cp /tmp/almacenamiento.bak 01-almacenamiento.tf
python3 - <<'EOF'
ruta = "01-almacenamiento.tf"
texto = open(ruta).read()
texto = texto.replace(
    "  #checkov:skip=CKV_AWS_144:los buckets de logs no se replican; la retención se define en lifecycle\n",
    "",
)
texto = texto.replace(
    'resource "aws_s3_bucket" "logs" {',
    'resource "aws_s3_bucket" "logs" { #checkov:skip=CKV_AWS_144:los buckets no se replican',
)
open(ruta, "w").write(texto)
EOF
checkov -d . --compact | grep "Passed checks"
```

**Salida esperada:**

```
Passed checks: 55, Failed checks: 18, Skipped checks: 0
```

Tampoco funciona. Y una comprobación más, porque la regla real no es la que se intuye: **la sangría es irrelevante**. Con el comentario dentro del bloque pero sin indentar:

```bash
cp /tmp/almacenamiento.bak 01-almacenamiento.tf
python3 - <<'EOF'
ruta = "01-almacenamiento.tf"
texto = open(ruta).read().replace(
    "  #checkov:skip=CKV_AWS_144:",
    "#checkov:skip=CKV_AWS_144:",
)
open(ruta, "w").write(texto)
EOF
checkov -d . --compact | grep "Passed checks"
```

**Salida esperada:**

```
Passed checks: 55, Failed checks: 17, Skipped checks: 1
```

Funciona. **La regla no es "dentro y con sangría", es "en una línea que va dentro de las llaves del recurso".** Indéntalo igual, que el `.tf` queda legible, pero entiende que no es lo que decide.

Restaura el fichero y confirma que vuelves al punto de partida:

```bash
cp /tmp/almacenamiento.bak 01-almacenamiento.tf
checkov -d . --compact | grep "Passed checks"
```

**Salida esperada:**

```
Passed checks: 55, Failed checks: 17, Skipped checks: 1
```

Para silenciar varios checks de una vez, separados por comas y con un único motivo:

```hcl
  #checkov:skip=CKV_AWS_144,CKV_AWS_145:los límites los fija la cuenta, no el repositorio
```

> **El motivo es obligatorio en la práctica, aunque la herramienta no lo exija sintácticamente.** Sin `:motivo`, Checkov no aplica la supresión y el hallazgo sigue apareciendo. Es decir: Checkov te obliga a escribir el porqué justo en el caso en que ibas a aplicarla sin pensarlo. Es la mejor decisión de diseño de todo el módulo de supresiones.

### 7. Descubre por qué Checkov ve un fallo que no está escrito

Mira el bloque del bucket de logs:

```bash
grep -A6 'resource "aws_s3_bucket" "logs"' 01-almacenamiento.tf
```

**Salida esperada:**

```hcl
resource "aws_s3_bucket" "logs" {
  bucket = "empresa-logs-2024"

  # El recurso no dice "public-read" en ninguna parte: lo hereda
  # del default de variables.tf.
  acl = var.acl_logs
```

El valor `"public-read"` **no aparece en el `.tf`**. Está en `variables.tf`, tres ficheros más arriba. Comprueba que Checkov lo ve:

```bash
checkov -d . --compact --check CKV_AWS_20 | grep -E "PASSED for|FAILED for"
```

**Salida esperada:**

```
	PASSED for resource: aws_s3_bucket.datos_clientes
	FAILED for resource: aws_s3_bucket.logs
```

Y el hallazgo viene del default, no del recurso:

```bash
grep -A4 'variable "acl_logs"' variables.tf
```

**Salida esperada:**

```hcl
variable "acl_logs" {
  description = "ACL del bucket de logs"
  type        = string
  default     = "public-read"
}
```

> **Es el valor por defecto de una variable lo que hace inseguro el recurso.** Un default inseguro es un hallazgo que se puede activar sin tocar una sola línea del `.tf` que lo usa. Revisar `variables.tf` con el mismo rigor que los recursos es parte del trabajo.

Ahora comprueba si puedes esconderlo apagando la resolución de variables:

```bash
checkov -d . --compact --check CKV_AWS_20 --evaluate-variables false | grep "Passed checks"
```

**Salida esperada:**

```
Passed checks: 1, Failed checks: 1, Skipped checks: 0
```

**El resultado no cambia.** Ni con `--evaluate-variables false` el fallo desaparece: en Checkov 3.3.x los `default` se resuelven durante el parseo del HCL y esta bandera no los afecta.

> **Mide, no supongas.** El nombre de un flag promete una cosa y la versión instalada puede hacer otra. Este es el motivo por el que este curso insiste tanto en ejecutar y contar: una suposición sobre el comportamiento de la herramienta es una suposición, no un hecho.

### 8. Tablero final

Mide las seis estrategias y compáralas:

| Estrategia | Comando | Fallos |
|---|---|---|
| Sin nada | `checkov -d . --compact` | **17** |
| Allowlist de 3 checks | `--check CKV_AWS_24,CKV_AWS_17,CKV_AWS_20` | **1** |
| Denylist | `--skip-check CKV_AWS_144,CKV_AWS_145` | **15** |
| Denylist con comodín | `--skip-check "CKV_AWS_14*"` | **15** |
| Config con `check:` | `--config-file config/.checkov.yaml` | **1** |
| Config sin `check:` | `--config-file /tmp/solo-skip.yaml` | **15** |
| Supresión fuera del bloque | sin `#checkov:skip=` dentro del recurso | **18** |

El **1** de la allowlist y el **1** de la configuración son el mismo error por dos caminos distintos. El **18** es el precio de una supresión escrita en el sitio equivocado: no es un fallo de Checkov, es un fallo de quien la escribió.

---

## ✅ Comprobación final

- [ ] Sabes distinguir una allowlist de una denylist y por qué la primera es peligrosa
- [ ] Sabes que `check:` **reemplaza** al catálogo entero, no lo amplía
- [ ] Sabes que una supresión `#checkov:skip=` solo funciona **dentro** del bloque del recurso, y que Checkov no avisa si la pones mal
- [ ] Sabes que el valor inseguro puede vivir en un `default` de `variables.tf` y no en el recurso
- [ ] Tienes el tablero final con los seis números medidos, no de memoria
- [ ] `01-almacenamiento.tf` ha quedado como estaba (17 fallos, 1 omitido)

---

## 🤔 Preguntas de reflexión

1. Tu compañero propone añadir `--skip-check "CKV_AWS_*"` al `.checkov.yaml` para "dejar de ver los mismos errores de S3". Solo affectaría a su bucket, dice. **No es cierto**: `CKV_AWS_20` ("bucket con ACL pública") también salta. ¿Qué otros IDs fuera de su intención acabarían silenciados? ¿Qué argumento usarías para convencerlo, con números?

2. En `config/.checkov.yaml` hay tres checks en `check:` y dos en `skip-check:`, y quien lo escribió no llegó a probarlo. Alguien nuevo lo lee y asume que se escanea "todo menos esos dos". Reescribe el fichero para que la intención real quede clara sin perder funcionalidad. ¿De qué tendrías que prescindir?

3. El bucket de logs lleva `#checkov:skip=CKV_AWS_144` (replicación entre regiones). Dos meses después alguien **crea un segundo bucket de datos** sin ese comentario, y Checkov falla la replicación. El equipo asume que "los buckets ya están exentos". ¿Qué propiedad tiene una supresión en el código que un `skip-check` global no tiene? ¿Y a la inversa, qué propiedad tiene el `skip-check` global que el comentario no? ¿Cuál de los dos mecanismo Preventiría el error del nuevo bucket?

4. Si Checkov devuelve 1 fallo con una allowlist de tres checks, ¿cómo lo distinguirías de un repositorio realmente limpio? Nombra dos señales observables en el informe. ¿Se puede construir una tercera señal automática en CI?

5. La variable `acl_logs` no la usa más nadie en el repositorio: solo ese bucket. Aun así, `CKV_AWS_20` falla por su default. ¿Es un falso positivo, un riesgo real, o las dos cosas? Justifica tu respuesta con el contenido de `variables.tf` y con lo que ocurriría si mañana alguien reutilizara esa variable en un bucket de producción.

---

## ⏭️ Siguiente

[Ejercicio 03 — Baseline, políticas propias y CI →](../03-ci-baseline-y-politicas/README.md)

En el siguiente ejercicio el problema ya no es qué escanear sino **cómo meter Checkov en un repositorio que no está limpio** sin romper el despliegue el primer día. Y escribirás tu primera política propia: la regla que Checkov no trae porque es tuya.
# Ejercicio 03 — Baseline, políticas propias y CI

**Nivel:** 🔴 Avanzado · **Duración estimada:** 40 min

## 🎯 Objetivo

Meter Checkov en un repositorio que **no está limpio** sin romper el despliegue el primer día, escribir tu primera política propia (la regla que Checkov no trae porque es de tu empresa) y cerrar el círculo con un workflow de GitHub Actions que sube los resultados a Code Scanning.

Al terminar sabrás qué es un baseline y cuándo regenerarlo, cómo se escribe un check de Checkov 3.x y por qué el repositorio escaneado por su propio escáner es una decisión, no un detalle.

## 📋 Requisitos previos

- [Ejercicio 02 completado](../02-configuracion-y-supresiones/README.md)
- Una cuenta de GitHub para la parte de Actions (opcional: puedes seguir los pasos 1 a 5 en local)

---

## Pasos

### 1. Mid el stack que vamos a congelar

```bash
cd checkov/03-ci-baseline-y-politicas/fixtures
checkov -d infra --compact
```

**Salida esperada:**

```
Passed checks: 33, Failed checks: 21, Skipped checks: 0
```

**21 fallos.** Si hoy metieras este escaneo en el pipeline, el primer push dejaría el CI en rojo y nadie podría mergear nada. Es el escenario real al que te enfrentas en cualquier repositorio heredado.

Mira qué son, agrupados por política:

```bash
checkov -d infra --compact --quiet | grep "^Check:" | sed 's/Check: //' | cut -d: -f1 | sort | uniq -c | sort -k1,1nr -k2 | head -8
```

**Salida esperada:**

```
   2 CKV2_AWS_6
   2 CKV2_AWS_61
   2 CKV2_AWS_62
   2 CKV_AWS_144
   2 CKV_AWS_145
   2 CKV_AWS_18
   1 CKV2_AWS_41
   1 CKV2_AWS_5
```

El doble `sort` de la segunda clave no es cosmetismo: sin él, el orden de los bloques de Checkov cambia entre ejecuciones y no puedes comparar dos escaneos.

Las que se repiten dos veces son las dos clases de buckets: `informes` (que sí tiene etiquetas y versionado) y `respaldos` (que no tiene nada). La mayoría son deuda real, no ruido.

### 2. Crea el baseline

```bash
checkov -d infra --create-baseline
```

**Salida esperada:**

```
Created a checkov baseline file at /ruta/al/repo/checkov/03-ci-baseline-y-politicas/fixtures/infra/.checkov.baseline
```

Fíjate en **dónde** ha caído el fichero:

```bash
ls -a infra/
```

**Salida esperada:**

```
.checkov.baseline  main.tf
```

> **El baseline se escribe en el directorio que escaneas, no en el de trabajo.** Has ejecutado `checkov -d infra --create-baseline` desde `fixtures/`, y el fichero aparece en `fixtures/infra/`. Apuntar mal la ruta al usarlo es el error más habitual con esta herramienta.

Ahora ejecuta contra ese baseline:

```bash
checkov -d infra --baseline infra/.checkov.baseline --compact
```

**Salida esperada:**

- El banner de Checkov
- **Nada más.** Ni resumen, ni hallazgos

```bash
checkov -d infra --baseline infra/.checkov.baseline --compact > /dev/null 2>&1; echo "exit=$?"
```

**Salida esperada:**

```
exit=0
```

**Los 21 fallos han desaparecido y el pipeline pasa.** Eso es exactamente lo que querías: nadie queda bloqueado por deuda que ya existía. Pero no se han arreglado. Lo que ha hecho Checkov es aprenderte de memoria.

> ⚠️ **El baseline no se regenera solo.** Si nadie lo regenera nunca, la deuda se queda congelada para siempre y los hallazgos nuevos siguen entrando. Un `.checkov.baseline` es un artefacto revisable del repositorio, con la misma obligación de comentario que un `.tf`.

### 3. Comprueba que el baseline detecta lo nuevo

Añade un recurso que no comply:

```bash
cat >> infra/main.tf <<'EOF'

resource "aws_sqs_queue" "nuevo" {
  name = "cola-sin-cifrar"
}
EOF

checkov -d infra --baseline infra/.checkov.baseline --compact
```

**Salida esperada:**

```
Passed checks: 0, Failed checks: 1, Skipped checks: 0

Check: CKV_AWS_27: "Ensure all data stored in the SQS queue is encrypted"
	FAILED for resource: aws_sqs_queue.nuevo
	File: /main.tf:...
```

Y el código de salida:

```bash
checkov -d infra --baseline infra/.checkov.baseline --compact > /dev/null 2>&1; echo "exit=$?"
```

**Salida esperada:**

```
exit=1
```

**Solo aparece el nuevo.** Los 21 heredados siguen ocultos a propósito. Eso es exactamente el contrato de un baseline: *no se reporta nada que ya estaba* y *se reporta todo lo que se añade*.

Limpia el recurso de prueba:

```bash
python3 - <<'EOF'
ruta = "infra/main.tf"
texto = open(ruta).read().split(
    '\nresource "aws_sqs_queue" "nuevo" {'
)[0]
open(ruta, "w").write(texto.rstrip() + "\n")
EOF
tail -4 infra/main.tf
```

### 4. Ahora las políticas propias

Los 21 checks que has visto son todos **de la comunidad**: lo que AWS y CIS consideran un error. Tu empresa tiene reglas que nadie más va a publicar:

- Todo bucket debe declarar su entorno con la etiqueta `Entorno`
- Ningún usuario de base de datos puede llamarse `*_admin`

En `checks/` tienes dos políticas escritas:

```bash
ls -a checks/
```

**Salida esperada:**

```
__init__.py  CKV_EMPRESA_001.py  CKV_EMPRESA_002.py
```

Fíjate en `__init__.py`. No es decoración: **Checkov solo carga checks externos de directorios que tengan un `__init__.py`**. Sin él, el escaneo termina con cero resultados y sin ningún error visible. Lo vas a comprobar en el paso 6.

Ejecuta tus políticas junto al catálogo estándar:

```bash
checkov -d infra --external-checks-dir checks --compact
```

**Salida esperada:**

```
Passed checks: 34, Failed checks: 23, Skipped checks: 0
```

De 21 a 23: tus dos checks han añadido dos hallazgos. Mira cuáles:

```bash
checkov -d infra --external-checks-dir checks --check CKV_EMPRESA_001,CKV_EMPRESA_002 --compact
```

**Salida esperada:**

```
Passed checks: 1, Failed checks: 2, Skipped checks: 0

Check: CKV_EMPRESA_001: "Ensure that S3 buckets declare the 'Entorno' tag"
	PASSED for resource: aws_s3_bucket.informes
Check: CKV_EMPRESA_001: "Ensure that S3 buckets declare the 'Entorno' tag"
	FAILED for resource: aws_s3_bucket.respaldos
Check: CKV_EMPRESA_002: "Ensure that DB usernames do not end with _admin or -admin"
	FAILED for resource: aws_db_instance.informes
```

Los tres recursos evaluados, los tres con veredicto. `informes` pasa la política de etiquetas; `respaldos` y la base de datos fallan.

### 5. Arregla un hallazgo de una política propia

Abre `infra/main.tf` y comprueba qué le falta a `respaldos`:

```bash
grep -A6 'resource "aws_s3_bucket" "respaldos"' infra/main.tf
```

**Salida esperada:**

```hcl
resource "aws_s3_bucket" "respaldos" {
  bucket = "respaldos-nocturnos"

  versioning_configuration {
    status = "Enabled"
  }
}
```

No tiene bloque `tags`. Añádelo:

```hcl
resource "aws_s3_bucket" "respaldos" {
  bucket = "respaldos-nocturnos"

  versioning_configuration {
    status = "Enabled"
  }

  tags = {
    Entorno = "produccion"
    Owner   = "equipo-platform"
  }
}
```

Vuelve a pasar tus checks:

```bash
checkov -d infra --external-checks-dir checks --check CKV_EMPRESA_001 --compact
```

**Salida esperada:**

```
Passed checks: 2, Failed checks: 0, Skipped checks: 0
```

> **Este es el ciclo completo del Shift Left:** escribes una regla, la herramienta te dice quién la incumple, arreglas cuatro líneas y vuelve a pasar. Lo que tardas minutos en un `.tf` cuesta horas en AWS, y horas no las arregla un `terraform apply` porque el recurso ya está creado.

### 6. Rompe el directorio de checks a propósito

Este paso parece absurdo y es el que más te va a ahorrar tiempo.

```bash
mv checks/__init__.py /tmp/init-reservado.py
checkov -d infra --external-checks-dir checks --check CKV_EMPRESA_001 --compact
```

**Salida esperada:**

- El banner de Checkov
- **Y nada más.** Ni un check, ni un fallo, ni un mensaje de error

```bash
checkov -d infra --external-checks-dir checks --check CKV_EMPRESA_001 --compact > /dev/null 2>&1; echo "exit=$?"
```

**Salida esperada:**

```
exit=0
```

Cero hallazgos, código 0, **verde**. Un escáner que no escanea y que dice que todo está bien. Es el peor fallo posible de una herramienta de seguridad, y solo lo descubres porque sabes que ese check debería haber dado dos resultados.

Para ver qué pasa por dentro:

```bash
LOG_LEVEL=INFO checkov -d infra --external-checks-dir checks --check CKV_EMPRESA_001 2>&1 | grep -i "__init__"
```

**Salida esperada:**

```
[INFO ] No __init__.py found in checks. Cannot load any check here.
```

Y si además hay un error de sintaxis en el `.py`, esto es lo que se ve:

```bash
echo "def scan(resource_conf)" >> checks/CKV_EMPRESA_001.py
checkov -d infra --external-checks-dir checks --check CKV_EMPRESA_001 --compact 2>&1 | head -3
```

**Salida esperada:**

```
IndentationError: unindent does not match any outer indentation level
```

En stdout, no en stderr, y **el escaneo continúa**. Por eso el paso 5 empieza compilando los checks:

```bash
python3 -m py_compile checks/*.py && echo "sintaxis OK"
```

Restaura y confirma:

```bash
mv /tmp/init-reservado.py checks/__init__.py
python3 - <<'EOF'
ruta = "checks/CKV_EMPRESA_001.py"
texto = open(ruta).read().replace("\ndef scan(resource_conf)\n", "")
open(ruta, "w").write(texto)
EOF
checkov -d infra --external-checks-dir checks --check CKV_EMPRESA_001 --compact 2>&1 | grep "Passed checks"
```

**Salida esperada:**

```
Passed checks: 2, Failed checks: 0, Skipped checks: 0
```

### 7. Escribe una política propia desde cero

Ahora al revés. Crea una tercera política que Checkov no trae: **toda cola SQS debe llevar la etiqueta `Entorno`**, igual que los buckets.

```bash
cat > checks/CKV_EMPRESA_003.py <<'EOF'
from typing import Any, Dict, List

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class ColaConEntorno(BaseResourceCheck):
    def __init__(self) -> None:
        super().__init__(
            name="Ensure that SQS queues declare the 'Entorno' tag",
            id="CKV_EMPRESA_003",
            categories=[CheckCategories.GENERAL_SECURITY],
            supported_resources=["aws_sqs_queue"],
        )

    def scan_resource_conf(self, conf: Dict[str, List[Any]]) -> CheckResult:
        tags = conf.get("tags")
        if not tags:
            return CheckResult.FAILED
        etiquetas = {clave: valor for bloque in tags for clave, valor in bloque.items()}
        return CheckResult.PASSED if "Entorno" in etiquetas else CheckResult.FAILED

    def get_evaluated_keys(self) -> List[str]:
        return ["tags"]


check = ColaConEntorno()
EOF

python3 -m py_compile checks/CKV_EMPRESA_003.py && checkov -d infra --external-checks-dir checks --check CKV_EMPRESA_003 --compact
```

**Salida esperada:**

```
Passed checks: 0, Failed checks: 1, Skipped checks: 0

Check: CKV_EMPRESA_003: "Ensure that SQS queues declare the 'Entorno' tag"
	FAILED for resource: aws_sqs_queue.trabajos
```

Funciona a la primera porque `CKV_EMPRESA_001` ya te enseñó la estructura. Fíjate en tres cosas del fichero:

**1. La forma del `conf` no es la que esperas.** Para un atributo simple, `conf["bucket"]` es una lista con el valor: `["empresa-logs-2024"]`. Para un mapa como `tags`, es una lista que contiene **un diccionario**: `[{"Entorno": "produccion", "Owner": "finanzas"}]`. Por eso `if "Entorno" in tags` devuelve siempre `False` y tu política no falla nunca. Para verlo:

```bash
cat > /tmp/sonda.py <<'EOF'
from typing import Any, Dict, List
from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class Sonda(BaseResourceCheck):
    def __init__(self) -> None:
        super().__init__(
            name="sonda",
            id="CKV_SONDA_1",
            categories=[CheckCategories.GENERAL_SECURITY],
            supported_resources=["aws_sqs_queue"],
        )

    def scan_resource_conf(self, conf: Dict[str, List[Any]]) -> CheckResult:
        print(f"SONDA conf={conf!r}", flush=True)
        return CheckResult.PASSED


check = Sonda()
EOF

cp /tmp/sonda.py checks/CKV_SONDA_1.py
checkov -d infra --external-checks-dir checks --check CKV_SONDA_1 2>&1 | grep SONDA
rm checks/CKV_SONDA_1.py
```

**Salida esperada:**

```
SONDA conf={'name': ['trabajos-cola']}
```

**2. `CheckResult` tiene tres valores útiles:** `PASSED`, `FAILED` y `UNKNOWN`. `UNKNOWN` es "no lo sé": si un check devuelve `UNKNOWN` cuando no puede evaluar, deja de ser un check y pasa a ser ruido. Úsalo solo cuando de verdad no hay información.

**3. El `id` es un espacio de nombres.** `CKV_EMPRESA_001` convive con los `CKV_AWS_*` y `CKV2_AWS_*` de la comunidad. Usa siempre un prefijo propio: si un día Checkov publica un check que se llama igual que el tuyo, la colisión es tuya.

### 8. Prepara el workflow

En `.github/workflows/iac-scan.yml` tienes el workflow terminado:

```bash
cat .github/workflows/iac-scan.yml
```

**Salida esperada:** un workflow con `permissions:` mínimos, `bridgecrewio/checkov-action@v12`, salida `cli,sarif` y un paso que sube el SARIF.

Tres decisiones que no son obvias y que conviene que sepas defender:

| Decisión | Por qué |
|---|---|
| `permissions: contents: read` + `security-events: write` | Solo lo que necesita. Los permisos por defecto del repositorio pueden ser más amplios, y el workflow hereda lo que no le restrinjas |
| `if: success() \|\| failure()` en el paso del SARIF | El paso de Checkov **falla** cuando hay hallazgos. Sin ese `if`, GitHub no ejecuta los pasos siguientes y **el SARIF no se sube nunca**: el check de seguridad que falla es el único que no deja rastro |
| `skip_framework: secrets` | Los secretos los cubre Gitleaks, en otro módulo del curso. Cada herramienta en su sitio |

> ⚠️ **Este workflow no se ejecuta.** Vive dentro de la carpeta del ejercicio para que lo estudies y lo copies a **tu** repositorio de práctica. Copiarlo a `.github/workflows/` de la raíz del repositorio del curso haría que el CI corriera de verdad y fallara por los fixtures, que son deliberadamente inseguros.

Y por cierto: **Checkov escanea su propio workflow.** Framework `github_actions`:

```bash
checkov -d .github --framework github_actions --compact
```

**Salida esperada:**

```
Passed checks: 20, Failed checks: 0, Skipped checks: 0
```

Veinte checks y ninguno en rojo. Dogfooding: el fichero que enseña a los demás a hacer bien los pipelines, lo pasa su propio escáner.

### 9. Reproduce el pipeline en local

Lo que hará el workflow, en tu máquina:

```bash
checkov -d infra \
  --external-checks-dir checks \
  --baseline infra/.checkov.baseline \
  --framework terraform \
  --compact --quiet
```

**Salida esperada:**

- Solo los hallazgos **nuevos** que hayas dejado en el fichero, sin los 23 heredados

Regenera el baseline para recoger el arreglo del paso 5:

```bash
rm -f infra/.checkov.baseline
checkov -d infra --external-checks-dir checks --create-baseline
checkov -d infra --external-checks-dir checks --baseline infra/.checkov.baseline --compact
```

**Salida esperada:**

- El banner y nada más
- `exit=0`

Y genera los dos informes que el workflow sube a la plataforma:

```bash
checkov -d infra --external-checks-dir checks --baseline infra/.checkov.baseline \
  --output sarif --output-file-path ./reportes --quiet
ls reportes/
```

**Salida esperada:**

```
results_sarif.sarif
```

> `--output-file-path` es un **directorio**, no un fichero. Si le pasas `resultado.sarif` te crea una carpeta llamada `resultado.sarif` y el fichero vive dentro. Es el tipo de detalle que te hace perder veinte minutos una vez y luego ya no.

El SARIF es lo que convierte un escaneo en una alerta en el pull request. Comprueba qué lleva dentro:

```bash
jq -r '.runs[0].tool.driver.name, (.runs[0].results | length)' reportes/results_sarif.sarif
```

**Salida esperada:**

```
Checkov
0
```

Y el resumen legible, para un informe o un correo:

```bash
checkov -d infra --external-checks-dir checks --output json --quiet 2>/dev/null \
  | jq -r '(if type=="array" then .[] else . end) | "\(.check_type): \(.summary.failed) fallan de \(.summary.passed + .summary.failed) evaluados"'
```

**Salida esperada** (después del arreglo del paso 5):

```
terraform: 22 fallan de 57 evaluados
```

Dos trampas en esa línea, y las dos te van a parar si no las sabes:

> **`2>/dev/null` no es opcional.** Con `--output json`, Checkov escribe el informe **también en stderr**. Sin él, `jq` recibe el JSON mezclado con el banner y se atasca.

> **La salida es un objeto si solo corre un framework, y un array si corre más de uno.** Aquí solo corre Terraform, así que es un objeto y `.[]` recorre sus claves (cadenas), y `jq` dice `Cannot index string with string "summary"`. En el módulo `01` el escaneo activaba tres frameworks y por eso sí venía un array. El `if type=="array"` resuelve los dos casos; escribir el `jq` sin él es escribir un script que funciona en tu máquina y falla en la de al lado.

Limpia lo que has generado:

```bash
rm -rf reportes infra/.checkov.baseline
```

---

## ✅ Comprobación final

- [ ] Sabes crear un baseline y explicar dónde se escribe el fichero
- [ ] Sabes que un baseline **congela** la deuda y solo reporta lo nuevo
- [ ] Has verificado que un hallazgo nuevo sí sale tras el baseline, y con `exit=1`
- [ ] Sabes escribir un check propio heredando de `BaseResourceCheck` e instanciándolo
- [ ] Sabes que el directorio de checks externos necesita `__init__.py` y lo has visto fallar en silencio
- [ ] Sabes que `conf["tags"]` es una lista con un diccionario dentro, no un mapa plano
- [ ] Sabes por qué el paso que sube el SARIF necesita `if: success() || failure()`
- [ ] Has comprobado que Checkov escanea su propio workflow y lo pasa en verde

---

## 🤔 Preguntas de reflexión

1. Acabas de crear el baseline con 23 hallazgos congelados. Dos meses después el equipo ha arreglado 20 y nadie regenera el fichero. ¿Qué argumento usarías para que se regenere en cada PR que toque `infra/`? ¿Y para que no se regenere a lo bruto, aceptando deuda nueva sin darse cuenta?

2. `CKV_EMPRESA_002` falla en `aws_db_instance.informes` porque el usuario se llama `informes_admin`. La razón real de tu empresa es que ese login es una puerta de atrás para las credenciales de la aplicación. ¿Qué harías con la regla: cambiarla para que solo verifique el sufijo en cuentas específicas, dejarla como está, o silenciarla en el recurso? Justifica cada opción con lo que permite y lo que esconde.

3. El paso 6 deja el escáner en verde sin escanear nada, y sale `exit=0`. ¿Cómo lo conviertes en un fallo visible en CI? Se te ocurren dos: una comprobación explícita, o un diseño que devuelva un número de checks ejecutados distinto del esperado. ¿Cuál prefieres y qué falso positivo te da cada una?

4. `CKV_EMPRESA_001` lee `conf["tags"]` como una lista que contiene un diccionario. Ese detalle viene de cómo Checkov parsea HCL, y podría cambiar en una versión futura. ¿Cómo escribirías el check para que no dependa de esa forma concreta? Razona sobre qué parte de `conf` sí es estable.

5. El workflow sube el SARIF, pero **solo si el paso de Checkov falla o pasa**. ¿Qué pasaría si en seis meses alguien añade `soft_fail: true` al action "para que no bloquee el despliegue"? ¿Seguirías teniendo visibilidad de los hallazgos nuevos? ¿Qué cambio mínimo en el workflow lo evita?

6. Este repositorio de curso tiene tres módulos de seguridad y ninguno se ejecuta en CI. Cada módulo tiene sus fixtures deliberadamente inseguros. Escribe, en tres frases, la política que adoptaría para que los ejercicios del curso se puedan CI con un `/fixtures` excluido, sin que nadie tenga que acordarse cada semana de que los secretos son de mentira.

---

## ⏭️ Siguiente

Fin del módulo de **Checkov**.

Vuelve al [índice del curso](../README.md) y elige el siguiente módulo: los secretos del repositorio ya están cubiertos con [Gitleaks](../gitleaks/README.md), la calidad del código de aplicación con [SonarQube](../sonarqube/README.md) y las CVEs en dependencias e imágenes con [Trivy](../trivy/README.md).
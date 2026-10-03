# 🏗️ Checkov — Análisis estático de infraestructura como código

> **Categoría:** IaC Security / Policy as Code / Shift Left · **Etapa del Shift Left:** Commit → Pull Request → CI · **Licencia:** Apache 2.0

## 1. ¿Qué es Checkov?

Checkov es un escáner de análisis estático (SAST) especializado en **infraestructura como código**. Lee tu Terraform, OpenTofu, CloudFormation, Kubernetes, Helm, Dockerfile, Bicep, OpenAPI o ARM Templates **antes de que se apliquen**, y comprueba cada recurso contra un catálogo de más de mil políticas de seguridad derivadas de CIS, PCI-DSS, NIST y de las guías de cada proveedor cloud.

Lo mantiene Bridgecrew, hoy parte de **Palo Alto Networks** (marca Prisma Cloud). El motor es open source y la versión local es gratuita; lo de pago es la plataforma.

**Analogía útil:** Checkov es un revisor de código que solo sabe de infraestructura. Si el código fuera un contrato, Checkov no sería el abogado que busca un vicio de forma: sería el que busca que alguien firmara sin poder, que la copia se quedara en una caja abierta o que la puerta del servidor no tuviera llave.

**¿Por qué importa?**

- **El error de IaC no se arregla en producción**: un bucket público no es un bug de la aplicación, es un bucket público desde el segundo en que se crea. Corregirlo después significa datos expuestos y una ventana de tiempo que no se cierra.
- **Terraform es código y se reviewea**: si nadie miraba el `.tf` en el pull request, nadie miraba los 30 buckets que creaba.
- **Es determinista y offline**: no necesita desplegar nada, ni credenciales de AWS, ni una cuenta en la nube. Corre igual en tu portátil que en CI.
- **Las políticas se versionan**: un check puede ser un ID (`CKV_AWS_24`) que cualquiera pueda silenciar con un motivo escrito.

**Diagrama ASCII del flujo:**

```
  .tf / .yaml / Dockerfile          ┌──────────────────────┐
  ───────────────────────────────►  │  Parseo (framework)  │
                                    └──────────┬───────────┘
                                               │
             ┌─────────────────────────────────┴──────────────────────┐
             ▼                                                        ▼
  ┌─────────────────────┐                              ┌──────────────────────────┐
  │ Checks de RECURSO   │                              │  Checks de GRAFO         │
  │ CKV_AWS_24          │                              │  CKV2_AWS_5              │
  │ "miran un .tf"      │                              │  "cruzan varios recursos"│
  └──────────┬──────────┘                              └────────────┬─────────────┘
             └────────────────────┬───────────────────────────────────┘
                                  ▼
                    ┌───────────────────────────┐
                    │  PASÓ  o  FALLÓ  (check)  │
                    │  + línea exacta del .tf   │
                    └────────────┬──────────────┘
                                 ▼
              ┌──────────────────────────────────────────┐
              │  Decisión: arreglar · justificar · ignorar│
              │  exit 0 / exit 1  →  CI verde / rojo     │
              └──────────────────────────────────────────┘
```

### Los tres conceptos que importan

Antes de los comandos, estas tres ideas explican el 90 % de la salida de Checkov:

| Concepto | Qué significa | Por qué te importa |
|---|---|---|
| **1. Checks e IDs** | Cada política tiene un identificador estable: `CKV_AWS_24`, `CKV2_AWS_5`, `CKV_GHA_1`. Todos los números del curso son estos IDs | Un ID es lo que silencias, lo que documentas y lo que defiendes en el pull request. "El escáner dijo algo" no es una defensa |
| **2. Recurso vs. grafo** | `CKV_*` evalúa un recurso aislado. `CKV2_*` construye un grafo de referencias y comprueba relaciones: "este grupo de seguridad no está asociado a nada", "este bucket no tiene bloque de acceso público" | Los `CKV2_*` son los que atrapana los errores sistémicos, y también los que más falsos positivos dan: si el módulo viene de un registry y no lo descargas, el grafo está incompleto |
| **3. Supresiones** | Tres niveles: comentario en el código (`#checkov:skip=`), fichero de configuración (`.checkov.yaml`) y baseline (`.checkov.baseline`) | Cada uno deja un rastro distinto. El comentario se ve en el diff; el baseline se ve en el repo; la config se ve... en el repo, pero no en el diff del módulo |

## 2. Características principales

| Característica | Descripción |
|---|---|
| **Multi-framework** | Terraform, OpenTofu, Terraform plan (JSON), CloudFormation, AWS SAM, Kubernetes, Helm, Kustomize, Dockerfile, Serverless, Bicep, ARM, OpenAPI, Ansible, GitHub Actions, GitLab CI, Argo Workflows, Bitbucket Pipelines |
| **Checks de recurso** | `CKV_*`: evalúan un recurso y sus atributos, uno a uno. Rápidos y fáciles de entender |
| **Checks de grafo** | `CKV2_*`: construyen un grafo de dependencias entre recursos y evalúan relaciones. Son los que ven la foto completa |
| **Escaneo de secretos** | Framework `secrets`: patrones de claves, tokens, contraseñas y cadenas de alta entropía. Se activa por defecto al escanear un directorio |
| **Plan de Terraform** | Con `-f tfplan.json` evalúa el plan real, con los valores ya resueltos, en vez del código fuente |
| **Checks propios** | Políticas de tu organización en Python (`--external-checks-dir`) o en YAML de grafo (`--external-checks-git`) |
| **Supresiones** | Comentarios en el código, `.checkov.yaml` y baselines |
| **Formatos de salida** | `cli`, `json`, `csv`, `junitxml`, `sarif`, `cyclonedx`, `spdx`, `gitlab_sast`, `github_failed_only` |
| **Sin servidor** | Todo corre en local. La cuenta de Prisma Cloud solo hace falta para la gestión de políticas y los equipos |

### Limitaciones que debes conocer

| Limitación | Detalle |
|---|---|
| **La severidad no funciona sin cuenta** | `--severity HIGH` no existe como flag y `--check HIGH`, `--hard-fail-on` / `--soft-fail-on` necesitan `--bc-api-key` de Prisma Cloud. En local **no puedes filtrar por severidad**: o ejecutas un check o no lo ejecutas |
| **El grafo se queda corto sin módulos externos** | Un `source = "terraform-aws-modules/vpc/aws"` no se descarga salvo que uses `--download-external-modules`. Sin ese flag verás falsos positivos de `CKV2_*` del tipo "no está asociado a nada" |
| **No evalúa lo que no está escrito** | Checkov lee HCL, no simula AWS. Si el acceso público viene de una policy adjunta en otro repo, de un bucket policy en JSON importado, o de una configuración de cuenta, no lo ve |
| **El framework `secrets` es heurístico** | Marca por alta entropía, así que falsos positivos en hashes, identificadores y cadenas largas. Y al revés: una contraseña débil y corta (`password = "root"`) no la detecta |
| **No reescribe nada** | Detecta, no corrige. Remediá el `.tf` a mano; si tu equipo es grande, mira `terraform plan` + cambios automáticos aparte |
| **`--create-baseline` con `--output json` está roto** | Verificado en la versión 3.3.x (2026): genera un JSON envuelto en un array que `--baseline` no sabe leer (`AttributeError: 'list' object has no attribute 'get'`). Usa `--create-baseline` a secas |
| **`--output-file-path` es un directorio** | No un fichero: `checkov -o json --output-file-path resultados/` escribe `resultados/results_json.json`. Si le pasas `resultados.json` te crea una carpeta con ese nombre |
| **La salida JSON va también a stderr, y cambia de forma** | `checkov --output json --quiet` imprime el JSON por los dos descriptores, y devuelve un **objeto** si solo corrió un framework o un **array** si corrieron varios. Un `jq` escrito para un caso revienta en el otro |
| **El formato antiguo de checks propios ya no se carga** | El ejemplo de `def scan(resource_conf)` que sigue en parte de la documentación en línea no se registra en 3.x. El escaneo acaba con cero resultados **sin ningún error visible** |
| **El plan de Terraform requiere el binario `terraform`** | Además necesita `terraform init` con acceso a red al registry. Sin credenciales de cloud el plan se queda sin datos dinámicos |
| **Licencia y gobierno** | El motor es Apache 2.0, pero los metadatos de severidad, los benchmarks y las políticas escritas desde la plataforma son de pago |

## 3. Instalación

> **Requisito:** Python **>= 3.9 y <= 3.12**. Con Python 3.13 o superior la instalación falla o la ejecución se rompe. Si tu `python3` es 3.13, usa un entorno virtual con 3.11 o el contenedor de Docker.

### macOS (Homebrew)

```bash
brew install checkov
checkov --version
```

### Linux (pip en un entorno virtual — recomendado)

```bash
# Ubuntu/Debian: Python 3.9 a 3.12
sudo apt-get install -y python3.11 python3.11-venv

python3.11 -m venv ~/.venvs/checkov
source ~/.venvs/checkov/bin/activate
pip install --upgrade pip
pip install checkov
checkov --version
```

> Debian 12 y algunas distribuciones con PEP 668 ("externally-managed-environment") **rechazan** un `pip install` global. El entorno virtual no es opcional ahí, es la única forma.

### Windows

```powershell
# Opción A: instalador oficial
winget install -e --id Bridgecrew.Checkov
checkov --version

# Opción B: scoop
scoop install checkov

# Opción C: venv de Python
py -3.11 -m venv %USERPROFILE%\.venvs\checkov
%USERPROFILE%\.venvs\checkov\Scripts\activate
pip install checkov
```

### Docker (la opción que evita todos los problemas de Python)

```bash
docker pull bridgecrew/checkov

docker run --rm \
  --user "$(id -u):$(id -g)" \
  -v "$(pwd):/repo" \
  bridgecrew/checkov \
  --directory /repo --compact
```

> El `--user` no es opcional si escaneas como root dentro del contenedor: los ficheros que escribe (`.checkov.baseline`, informes) quedan en tu máquina como propiedad de root y luego no puedes borrarlos.

### ✅ Verificación de la instalación

```bash
checkov --version
```

**Salida esperada** con Checkov 3.3.x instalado:

```
3.3.22
```

Si no imprime un número con tres componentes, algo no ha ido bien. Lo segundo que conviene comprobar:

```bash
checkov --list --framework terraform | wc -l
```

Debe devolver un número de varios miles de líneas: es el catálogo de checks de Terraform. Si devuelve menos de 100, la instalación está incompleta.

## 4. Uso básico

### Escanear un directorio

```bash
checkov -d .
```

`-d` (o `--directory`) es el parámetro principal: escanea todo lo que reconoce dentro de esa ruta.

### Escanear un solo fichero

```bash
checkov -f main.tf
```

### Las dos banderas que vas a usar todos los días

```bash
checkov -d . --compact --quiet
```

| Bandera | Efecto |
|---|---|
| `--compact` | No imprime los bloques de código del recurso infractor |
| `--quiet` | Imprime solo los checks que fallan, no los que pasan |

Sin ellas, un repositorio medio te escupe cientos de líneas de checks en verde. No es que estén mal: es ruido.

### Limitarse a un framework

```bash
checkov -d . --framework terraform
```

Por defecto, al escanear un directorio Checkov activa **más de un framework a la vez**. Si solo quieres Terraform, dilo: la salida será mucho más legible y los números serán reproducibles.

### Leer un hallazgo

```
Check: CKV_AWS_24: "Ensure no security groups allow ingress from 0.0.0.0:0 to port 22"
	FAILED for resource: aws_security_group.bastion
	File: /03-red-y-computo.tf:7-17
	Guide: https://docs.prismacloud.io/...
```

Cuatro líneas: **qué regla** (`CKV_AWS_24`), **sobre qué recurso**, **en qué fichero y qué rango de líneas**, y **qué hacer** (el `Guide`). Con el `Guide` entras a la documentación de la política y a los recursos que la satisfacen.

### Código de salida

```bash
checkov -d . --compact --quiet > /dev/null; echo "exit=$?"
```

| Código | Significado |
|---|---|
| `0` | Ningún check falló (o usaste `--soft-fail`) |
| `1` | Hay checks fallando |
| `2` | Error de uso: flags que no existen, mutually exclusive, fichero no encontrado |

> El código 1 **no** es un error de Checkov: es el resultado. Es lo que hace que el pipeline se ponga rojo.

## 5. Uso avanzado

### 5.1 Allowlist y denylist de checks

Dos formas opuestas de decidir qué se ejecuta:

```bash
# Allowlist: ejecuta SOLO estos checks
checkov -d . --check CKV_AWS_24,CKV_AWS_17

# Denylist: ejecuta todo MENOS estos
checkov -d . --skip-check CKV_AWS_144,CKV_AWS_145
```

Pueden llevar comodines: `--skip-check CKV_AWS_18*` excluye toda la familia 18.

> Con la allowlist estás apagando mil comprobaciones para quedarte con dos. Úsala para depurar un check concreto, nunca como configuración permanente.

### 5.2 Archivo de configuración `.checkov.yaml`

Todo lo que pasas por flags se puede guardar. Checkov busca `.checkov.yaml` en el directorio que escanea y lo carga **automáticamente**:

```yaml
compact: true
quiet: true
framework:
  - terraform
skip-check:
  - CKV_AWS_144   # con el motivo al lado
check:
  - CKV_AWS_24
```

Forzar un fichero concreto:

```bash
checkov -d . --config-file config/.checkov.yaml
```

Ver qué está resolviendo Checkov y de dónde sale cada valor:

```bash
checkov -d . --show-config
```

Y congelar tu configuración actual:

```bash
checkov -d . --compact --check CKV_AWS_24 --create-config mi-config.yaml
```

> La diferencia entre `check:` y `skip-check:` en el mismo fichero no es "intersección": si defines `check:`, **solo se ejecutan esos**. El `skip-check:` se queda sin efecto.

### 5.3 Supresiones con comentarios en el código

La supresión más transparente: vive junto al recurso, se ve en el diff y viaja con el código.

```hcl
resource "aws_s3_bucket" "logs" {
  bucket = "empresa-logs-2024"

  #checkov:skip=CKV_AWS_144:los buckets de logs no se replican entre regiones
}
```

**El comentario tiene que ir dentro del bloque del recurso**, después de la llave de apertura. Estas dos variantes **no funcionan**:

```hcl
# --- NO funciona: está fuera del bloque ---
#checkov:skip=CKV_AWS_144:no aplica
resource "aws_s3_bucket" "logs" { }
```

```hcl
resource "aws_s3_bucket" "logs" { #checkov:skip=CKV_AWS_144:tampoco funciona
}
```

Para suprimir varios checks de golpe, separados por comas:

```hcl
  #checkov:skip=CKV_AWS_144,CKV_AWS_145:los límites los fija la cuenta, no el repo
```

El motivo es **obligatorio** en la práctica profesional: sin `#checkov:skip=ID:` Checkov no aplica la supresión y el hallazgo sigue apareciendo. La razón es que la supresión sin explicación es indistinguible de un fallo silencioso.

### 5.4 Baseline: arreglar el legado sin bloquear el despliegue

El problema real de introducir Checkov en un repo con 300 hallazgos: si el pipeline falla desde el primer día, nadie lo ejecuta en dos semanas. El baseline congela el estado actual y solo reporta lo **nuevo**.

```bash
# 1. Congelar el estado actual (crea .checkov.baseline junto al código escaneado)
checkov -d . --create-baseline

# 2. En adelante, ejecutar contra el baseline
checkov -d . --baseline .checkov.baseline --compact
```

Cuando todo está baselined, Checkov imprime solo el banner y sale con `0`. Cuando alguien añade un bucket nuevo sin cifrar, aparece **solo** ese y sale con `1`.

> ⚠️ El baseline se escribe en el **directorio que escaneas**, no en el de trabajo. Si haces `checkov -d infra --create-baseline`, el fichero acaba en `infra/.checkov.baseline` y luego hay que apuntar a él con `--baseline infra/.checkov.baseline`.

> ⚠️ Un baseline sin revisión es una lista de debts con amnesia: si nadie lo regenera, los hallazgos nuevos se cuelan y los viejos nunca se cierran. Revísalo como un artefacto del repo, no como un fichero temporal.

### 5.5 Checks propios: la política de tu organización

Los checks de la comunidad cubren lo que AWS cubre. Lo que tu empresa impone (etiquetas obligatorias, nombres prohibidos, cuentas de servicio concretas) lo escribes tú.

```bash
checkov -d . --external-checks-dir checks --check CKV_EMPRESA_001
```

Dos requisitos que no son opcionales:

1. **El directorio necesita un `__init__.py`.** Sin él, Checkov registra el directorio entero como "no se puede cargar" en log y continúa. El escaneo termina con cero resultados y no hay ningún error visible en pantalla.
2. **Desde la versión 3.x el check debe heredar de `BaseResourceCheck`** e instanciarse al final del módulo (`check = MiCheck()`). El formato de función suelta que aparece en ejemplos antiguos ya no se registra.

```python
from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class BucketConEntorno(BaseResourceCheck):
    def __init__(self) -> None:
        super().__init__(
            name="Ensure that S3 buckets declare the 'Entorno' tag",
            id="CKV_EMPRESA_001",
            categories=[CheckCategories.GENERAL_SECURITY],
            supported_resources=["aws_s3_bucket"],
        )

    def scan_resource_conf(self, conf):
        tags = conf.get("tags")
        if not tags:
            return CheckResult.FAILED
        etiquetas = {c: v for bloque in tags for c, v in bloque.items()}
        return CheckResult.PASSED if "Entorno" in etiquetas else CheckResult.FAILED

    def get_evaluated_keys(self):
        return ["tags"]


check = BucketConEntorno()
```

Y para arrancar de cero sin escribir Python:

```bash
checkov -d . --add-check
```

Los checks también se pueden compartir por git, sin directorios locales:

```bash
checkov -d . --external-checks-git https://github.com/<ORG>/checkov-policies
```

### 5.6 Salidas para CI

```bash
# JUnit XML: lo que leen Jenkins, GitLab, CircleCI
checkov -d . --output junitxml --output-file-path reports --quiet

# SARIF: se sube a GitHub Code Scanning y sale como alerta en el PR
checkov -d . --output sarif --output-file-path reports --quiet

# JSON: para procesar con jq o con tu propio script
checkov -d . --output json --quiet 2>/dev/null | jq -r '(if type=="array" then .[] else . end) | .summary'
```

Recuerda: `--output-file-path` es una **carpeta**, y `--output json` escribe **también en stderr**:

```bash
checkov -d . --output json --quiet 2>/dev/null \
  | jq '[((if type=="array" then .[] else . end)) | .results.failed_checks[]?] | length'
```

> El `if type=="array"` no es un remilgo: con un solo framework la salida es un objeto y con varios es un array. Verificado en 3.3.x.

### 5.7 Escaneo del plan de Terraform

El código fuente dice lo que alguien quiso escribir; el plan dice lo que va a pasar de verdad.

```bash
terraform init
terraform plan -out=tfplan.binary
terraform show -json tfplan.binary | jq > tfplan.json
checkov -f tfplan.json --compact
```

Y para que las rutas y los comentarios de supresión del `.tf` se reflejen en el informe:

```bash
checkov -f tfplan.json --repo-root-for-plan-enrichment . --compact
```

> El `tfplan.json` **contiene los valores resueltos**, incluidas las contraseñas que van a la base de datos. Trátalo como un secreto: nunca lo comitees, y escanéalo solo en un entorno controlado.

### 5.8 Other frameworks en 30 segundos

```bash
checkov -d . --framework kubernetes -f k8s/deployment.yaml
checkov -d . --framework dockerfile -f Dockerfile
checkov -d . --framework github_actions -f .github/workflows/deploy.yml
checkov -d . --framework cloudformation -f infra.json
```

Lo que aprendas con Terraform se traslada: mismo modelo de checks, mismas supresiones, mismos formatos de salida.

## 6. Códigos de salida y troubleshooting

| Problema | Causa probable | Solución |
|---|---|---|
| `checkov: command not found` | No está en el `PATH`, o el venv no está activado | `which checkov`; `source ~/.venvs/checkov/bin/activate`; alternativa: usa la imagen de Docker |
| `ERROR: Package 'checkov' requires a different Python` | Python 3.13+ o 3.8 | Crea un venv con 3.11: `python3.11 -m venv ~/.venvs/checkov` |
| `error: externally-managed-environment` (Debian 12) | PEP 668 bloquea el `pip install` global | Instala dentro de un entorno virtual |
| `Passed checks: 0, Failed checks: 0` | No hay ficheros que el framework reconozca, o estás en un directorio equivocado | `ls` y comprueba la extensión; prueba `checkov -f <fichero>` |
| El check propio **no aparece** | Falta `__init__.py` en el directorio, o el formato antiguo de `def scan()` | Añade `__init__.py` y reescribe el check heredando de `BaseResourceCheck` |
| `IndentationError: unindent does not match any outer indentation level` al cargar checks | Error de sintaxis en tu `.py`; se imprime en stdout y se ignora | `python3 -m py_compile checks/*.py` antes de escanear |
| `AttributeError: 'list' object has no attribute 'get'` con `--baseline` | Baseline generado con `--output json` (bug de 3.3.x) | Regenera con `checkov -d . --create-baseline` a secas |
| `jq` se atasca o no encuentra nada tras `checkov --output json` | El JSON se escribe **también** en stderr, y la salida es un objeto si solo corrió un framework o un array si corrieron varios | Añade `2>/dev/null` y envuelve con `(if type=="array" then .[] else . end)` |
| `Cannot index string with string "summary"` en `jq` | Estás haciendo `.[]` sobre un objeto: `.[]` recorre sus claves, que son cadenas | El JSON de un solo framework es un objeto. Usa `if type=="array" then .[] else . end` |
| `--output-file-path` crea una carpeta en vez de un fichero | Es un directorio por diseño | Usa `--output-file-path reports` y luego `reports/results_json.json` |
| Hallazgos `CKV2_*` absurdos ("no está asociado a nada") | Módulo externo no descargado | `--download-external-modules true` |
| El escaneo tarda más de un minuto | Se están descargando módulos externos o hay muchos ficheros | `--skip-path .terraform --skip-path vendor` |
| `File: /x.tf:0` en todos los hallazgos | Estás escaneando el JSON de `terraform show`, que es una sola línea | `terraform show -json tfplan.binary \| jq . > tfplan.json` |
| Falla un check que "estaba bien" | Un default inseguro en `variables.tf` (Checkov resuelve variables) | Revisa los `default` del fichero de variables |
| Sale un `CKV_SECRET_6` que no es un secreto | Framework `secrets` por entropía: hashes e identificadores largos | Saltar framework: `--skip-framework secrets` |

## 7. Qué hacer cuando Checkov encuentra algo

| Tipo de hallazgo | Acción recomendada |
|---|---|
| **Bucket o base de datos público a internet** | **Inmediato.** Falla el pipeline y escala: hay que comprobar si alguien ya lo explotó. Un `CKV_AWS_17` o `CKV_AWS_20` no es una deuda, es una incidente en curso |
| **Cifrado ausente** | Se corrige en el `.tf`, pero recuerda que cifrar un bucket que ya tiene datos requiere **reescribir cada objeto**: cambiar la configuración no cifra el pasado |
| **Wildcards en IAM (`Action = "*"`)** | Sustituir por permisos concretos. Si es un caso legítimo, acotar el `Resource` y escribir el motivo en el pull request |
| **IMDSv1 habilitado** | Cambio barato y de riesgo bajo. Prioridad alta en cualquier instancia |
| **Check duplicado en el mismo recurso** | No es un bug: `CKV_AWS_53/54/55/56` son cuatro interruptores distintos del mismo acceso público. Arréglalo una vez y desaparecen los cuatro |
| **Falso positivo real** | Se silencia con `#checkov:skip=<ID>:<motivo>` **dentro** del bloque del recurso. Nunca borres el check del código |
| **Check que no aplica a tu arquitectura** | Se silencia por check en `.checkov.yaml` con el motivo al lado, para que se vea en cada ejecución |
| **Hallazgo de un módulo de terceros que no controlas** | `--skip-path` para esa ruta, y una issue al módulo. Silenciar el ID globalmente es demasiado: silencia también tus propios recursos |

> **Regla de oro de este curso:** los hallazgos de los `fixtures/` son **intencionales**. No "arregles" el Terraform de los ejercicios para que el escáner quede en verde. Los fixtures están mal porque el material del curso **es** lo que Checkov encuentra.

## 8. Ejercicios de esta carpeta

| Ejercicio | Nivel | Tema | Duración estimada |
|---|---|---|---|
| [01-escaneo-basico](01-escaneo-basico/README.md) | 🟢 Básico | Instalar, primer escaneo, leer la salida, código de salida | 20 min |
| [02-configuracion-y-supresiones](02-configuracion-y-supresiones/README.md) | 🟡 Intermedio | `--check` vs `--skip-check`, `.checkov.yaml`, supresiones con comentario y sus tres límites | 30 min |
| [03-ci-baseline-y-politicas](03-ci-baseline-y-politicas/README.md) | 🔴 Avanzado | Baseline, checks propios de la empresa, workflow de GitHub Actions y SARIF | 40 min |

🧪 **Prueba de humo del curso:** escanea el módulo completo y deberías obtener **79 fallos de Terraform** (más 2 de secretos y 20 checks de GitHub Actions que pasan):

```bash
cd checkov && checkov -d . --framework terraform --compact 2>&1 | grep "Passed checks"
```

**Salida esperada:**

```
Passed checks: 108, Failed checks: 79, Skipped checks: 1
```

Si tu número no es 79, algo se ha desincronizado: normalmente es que has creado un `.checkov.baseline` dentro de la carpeta (el ejercicio 03 te pide crearlo) o que has movido algún fichero. Los números por ejercicio están en el enunciado de cada uno y son la referencia.

## 9. Referencias

- [Checkov — sitio oficial](https://www.checkov.io/)
- [Quick Start](https://www.checkov.io/1.Welcome/Quick%20Start.html)
- [Referencia de la CLI](https://www.checkov.io/2.Basics/CLI%20Command%20Reference.html)
- [Installing Checkov](https://www.checkov.io/2.Basics/Installing%20Checkov.html)
- [Terraform Plan Scanning](https://www.checkov.io/7.Scan%20Examples/Terraform%20Plan%20Scanning.html)
- [Configuración por `.checkov.yaml`](https://www.checkov.io/2.Basics/Configuration%20File.html)
- [Checks personalizados](https://www.checkov.io/6.Custom%20Policies/YAML%20Custom%20Policies.html)
- [Integración con GitHub Actions](https://www.checkov.io/4.Integrations/GitHub%20Actions.html)
- [Repositorio en GitHub](https://github.com/bridgecrewio/checkov)
- [bridgecrewio/checkov-action](https://github.com/bridgecrewio/checkov-action)
- [Imagen de Docker](https://hub.docker.com/r/bridgecrew/checkov)

## 10. Glosario rápido

| Término | Significado |
|---|---|
| **IaC** | Infrastructure as Code: describir la infraestructura en ficheros de texto versionables |
| **CKV_\*** | Check de recurso: evalúa un recurso y sus atributos por separado |
| **CKV2_\*** | Check de grafo: evalúa relaciones entre varios recursos |
| **Framework** | El tipo de fichero que sabe leer un runner: `terraform`, `kubernetes`, `dockerfile`, `github_actions`... |
| **Allowlist (`--check`)** | Lista de checks que **sí** se ejecutan; el resto queda apagado |
| **Denylist (`--skip-check`)** | Lista de checks que **no** se ejecutan; el resto sí |
| **Supresión** | Ignoring justificado de un hallazgo: comentario, config o baseline |
| **Baseline** | Fichero `.checkov.baseline` con el estado heredado; solo se reporta lo nuevo |
| **`--soft-fail`** | Devuelve 0 aunque haya fallos. Para pipelines en modo observación |
| **`--external-checks-dir`** | Directorio con checks propios en Python (necesita `__init__.py`) |
| **`--download-external-modules`** | Descarga los módulos de Terraform del registry para que el grafo esté completo |
| **SARIF** | Formato de intercambio de estáticos que GitHub Code Scanning entiende |
| **JUnit XML** | Formato de resultados de test que casi todas las plataformas de CI leen |
| **CIS / NIST / PCI-DSS** | Estándares de cumplimiento de los que derivan muchas de las políticas |
# Ejercicio 01 — Primer escaneo y lectura de la salida

**Nivel:** 🟢 Básico · **Duración estimada:** 20 min

## 🎯 Objetivo

Instalar Checkov, ejecutar tu primer escaneo sobre Terraform deliberadamente inseguro y aprender a leer una salida de Checkov sin help. Al terminar sabrás distinguir un check de recurso (`CKV_*`) de uno de grafo (`CKV2_*`), entender por qué el escaneo devuelve código 1 y qué significa cada bloque de la salida.

Este ejercicio no arregla nada. Mide.

## 📋 Requisitos previos

- Python 3.9 a 3.12 (`python3 --version`), o Docker
- Terraform no hace falta: Checkov analiza el código sin ejecutarlo
- Git 2.30+ (el repositorio del curso)

---

## Pasos

### 1. Instala Checkov

Si tienes Homebrew:

```bash
brew install checkov
```

Si estás en Linux o la instalación con `pip` falla por la versión de Python, usa un entorno virtual:

```bash
python3.11 -m venv ~/.venvs/checkov
source ~/.venvs/checkov/bin/activate
pip install --upgrade pip && pip install checkov
```

O si prefieres no tocar tu Python, la imagen de Docker:

```bash
docker pull bridgecrew/checkov
```

> **Comprueba tu versión de Python antes de nada.** Checkov requiere Python entre 3.9 y 3.12. Con 3.13 la instalación falla; con 3.8 no hay ruedas disponibles y compilar desde el código fuente es unmartirio.

**Salida esperada:**

```bash
checkov --version
```

```
3.3.22
```

### 2. Sitúate en los fixtures del ejercicio

```bash
cd checkov/01-escaneo-basico/fixtures
ls
```

**Salida esperada:**

```
00-proveedor.tf       02-bases-de-datos.tf   variables.tf
01-almacenamiento.tf  03-red-y-computo.tf     04-identidades.tf
```

Cinco ficheros, seis recursos de AWS. Ninguno se va a aplicar a ninguna cuenta: son ficticios.

### 3. Primer escaneo

```bash
checkov -d .
```

**Salida esperada:** el banner de Checkov, un resumen por framework y decenas de bloques `Check:`. El resumen tiene **dos** líneas porque Checkov activa más de un framework al escanear un directorio:

```
terraform scan results:

Passed checks: 19, Failed checks: 42, Skipped checks: 0

secrets scan results:

Passed checks: 0, Failed checks: 2, Skipped checks: 0
```

Esos números son tu referencia. Si no los tienes, no puedes medir nada en el ejercicio 02.

> **Los 2 fallos del framework `secrets` no son un error de Checkov.** Son las dos contraseñas escritas en el código (`02-bases-de-datos.tf` y `04-identidades.tf`). Los valores son inventados, pero Checkov no sabe que lo son: solo ve cadenas de alta entropía donde no debería haber ninguna. Si esto fuera un repositorio real, esas dos líneas serían una emergencia.

### 4. Escanea solo Terraform

Los dos números juntos confunden. Cuando quieras hablar de "los hallazgos del código de infraestructura", sé explícito:

```bash
checkov -d . --framework terraform --compact
```

**Salida esperada:**

```
Passed checks: 19, Failed checks: 42, Skipped checks: 0
```

**42 fallos. Apunta este número**, es tu línea base.

### 5. Aprende a leer un hallazgo

Abre la salida completa y busca el hallazgo del grupo de seguridad:

```bash
checkov -d . --framework terraform --compact | grep -B1 -A2 "aws_security_group.bastion"
```

**Salida esperada** (el orden de los checks no siempre es el mismo, pero el contenido sí):

```
Check: CKV_AWS_24: "Ensure no security groups allow ingress from 0.0.0.0:0 to port 22"
	FAILED for resource: aws_security_group.bastion
	File: /03-red-y-computo.tf:8-28
```

Y para ver el bloque de código entero que ha fallado (por eso existe `--compact`):

```bash
checkov -d . --framework terraform | grep -A20 "CKV_AWS_24"
```

**Salida esperada:**

```
Check: CKV_AWS_24: "Ensure no security groups allow ingress from 0.0.0.0:0 to port 22"
	FAILED for resource: aws_security_group.bastion
	File: /03-red-y-computo.tf:8-28
	Guide: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws-networking-policies/...
		8  | resource "aws_security_group" "bastion" {
		9  |   name        = "bastion-sg"
		10 |   description = "Acceso al bastion"
		11 |
		12 |   ingress {
		13 |     description = "SSH desde cualquier sitio"
		14 |     from_port   = 22
		15 |     to_port     = 22
		16 |     protocol    = "tcp"
		17 |     cidr_blocks = ["0.0.0.0/0"]
		18 |   }
```

Ese bloque es el motivo por el que existe `--compact`: sin él ves **qué línea exacta** falla sin abrir el fichero. Con 40 hallazgos, esa información es oro. Con 400, ahoga la consola.

Las cuatro líneas son tu guía de lectura:

| Línea | Qué te dice |
|---|---|
| `Check: CKV_AWS_24` | **Qué** regla se incumplió. Este ID es lo que silencias, lo que documentas y lo que defiendes |
| `FAILED for resource: aws_security_group.bastion` | **Sobre qué** recurso concreto. Si salieran 40 fallos sobre 40 recursos distintos, el problema es sistémico |
| `File: /03-red-y-computo.tf:8-28` | **Dónde** está el problema, con líneas. Abre el fichero: es el bloque `ingress` con `0.0.0.0/0` |
| `Guide:` | **Qué hacer**. Enlace directo a la política y a los recursos que sí la satisfacen |

> **El prefijo del ID te dice el tipo de check.** `CKV_AWS_24` mira un recurso. `CKV2_AWS_5` ("los grupos de seguridad están asociados a otro recurso") construye el grafo de referencias y por eso ve que `aws_security_group.bastion` no lo usa nadie. Los `CKV2_*` son los que atrapan los errores sistémicos; también son los que más falsos positivos dan cuando el grafo está incompleto.

### 6. Un recurso, ocho reglas

Busca un recurso con muchos fallos:

```bash
checkov -d . --framework terraform --compact --quiet | grep -B1 "FAILED for resource: aws_s3_bucket.datos_clientes"
```

**Salida esperada:**

```
Check: CKV_AWS_20: "S3 Bucket has an ACL defined which allows public READ access."
	FAILED for resource: aws_s3_bucket.datos_clientes
Check: CKV_AWS_18: "Ensure the S3 bucket has access logging enabled"
	FAILED for resource: aws_s3_bucket.datos_clientes
Check: CKV_AWS_144: "Ensure that S3 bucket has cross-region replication enabled"
	FAILED for resource: aws_s3_bucket.datos_clientes
Check: CKV_AWS_145: "Ensure that S3 buckets are encrypted with KMS by default"
	FAILED for resource: aws_s3_bucket.datos_clientes
Check: CKV_AWS_21: "Ensure all data stored in the S3 bucket have versioning enabled"
	FAILED for resource: aws_s3_bucket.datos_clientes
Check: CKV2_AWS_6: "Ensure that S3 bucket has a Public Access block"
	FAILED for resource: aws_s3_bucket.datos_clientes
Check: CKV2_AWS_61: "Ensure that an S3 bucket has a lifecycle configuration"
	FAILED for resource: aws_s3_bucket.datos_clientes
Check: CKV2_AWS_62: "Ensure S3 buckets should have event notifications enabled"
	FAILED for resource: aws_s3_bucket.datos_clientes
```

Y la línea que más se repite:

```bash
checkov -d . --framework terraform --compact --quiet | grep -c "FAILED for resource: aws_s3_bucket.datos_clientes"
```

**Salida esperada:**

```
8
```

Un recurso, ocho reglas: cinco `CKV_*` (atributos del recurso) y tres `CKV2_*` (relaciones con otros recursos). **No son duplicados**: son atributos distintos que arreglar, y varios comparten causa raíz. Si añades el `aws_s3_bucket_public_access_block` con los cuatro interruptores en `true`, desaparecen de golpe cuatro de ellos.

Comprueba que el bucket seguro del mismo fichero pasa:

```bash
checkov -d . --framework terraform --compact | grep -A2 "aws_kms_key.datos_clientes"
```

**Salida esperada:** `PASSED for resource: aws_kms_key.datos_clientes` en varios checks.

> Los checks que **pasan** también son información. Si `aws_kms_key` pasa la rotación y el bucket no tiene nada, sabes que la política de cifrado de esta cuenta no es uniforme. Eso es un hallazgo aunque Checkov no lo marque como fallo.

### 7. Reproduce el resultado en una línea

Cuando ejecutes Checkov en CI no vas a poder leer 800 líneas. Aprende a resumir:

```bash
checkov -d . --framework terraform --compact 2>&1 | grep "Passed checks"
```

**Salida esperada:**

```
Passed checks: 19, Failed checks: 42, Skipped checks: 0
```

Y el conteo puro, para pipelines:

```bash
checkov -d . --framework terraform --compact --quiet 2>&1 | grep -c "FAILED for"
```

**Salida esperada:**

```
42
```

> `--compact` quita los bloques de código y `--quiet` quita los checks que pasan. Con las dos banderas, una consola de CI legible.

### 8. Comprueba el código de salida

```bash
checkov -d . --framework terraform --compact --quiet > /dev/null 2>&1; echo "exit=$?"
```

**Salida esperada:**

```
exit=1
```

**Ese 1 no es un fallo de Checkov: es el resultado.** Checkov ha hecho su trabajo. Es exactamente el código que pone el pipeline en rojo.

Y la variante para pipelines que solo avisan:

```bash
checkov -d . --framework terraform --compact --quiet --soft-fail > /dev/null 2>&1; echo "exit=$?"
```

**Salida esperada:**

```
exit=0
```

---

## ✅ Comprobación final

- [ ] `checkov --version` imprime un número de tres componentes
- [ ] `checkov -d . --framework terraform --compact` da **42 fallos** y **19 pasos**
- [ ] Sabes explicar qué es un `CKV_*` y qué es un `CKV2_*` sin mirar el README
- [ ] Sabes leer las cuatro líneas de un hallazgo y localizar el problema en el `.tf`
- [ ] Sabes que `exit=1` significa "hay hallazgos", no "Checkov está roto"
- [ ] Has visto que el framework `secrets` detecta las dos contraseñas del fixture

---

## 🤔 Preguntas de reflexión

1. En `01-almacenamiento.tf` hay un `aws_s3_bucket_public_access_block` con los cuatro interruptores en `false`. ¿Es un bucket protegido o desprotegido? ¿Qué le dice a un revisor que ese recurso **exista** en el código si alguien lo lee sin ejecutar Checkov?

2. `04-identidades.tf` define una política con `Action = "*"` y `Resource = "*"`, y Checkov la señala con **siete** checks distintos (`CKV_AWS_1`, `CKV_AWS_40`, `CKV_AWS_61`, `CKV_AWS_62`, `CKV_AWS_355` y varios `CKV2_AWS_*`). Tu jefe pregunta: "si arreglamos uno, ¿cuántos desaparecen?". Investiga y responde con números, no de memoria.

3. El `aws_security_group.bastion` falla `CKV2_AWS_5` ("está asociado a otro recurso") y también `CKV_AWS_24` (ingress abierto). Son el mismo problema. ¿Por qué Checkov los reporta como dos? ¿Qué advantage tiene que estén separados y qué disadvantage tiene para quien lee el informe?

4. Este escaneo lo haría alguien del equipo nuevo en su primer día, sin credenciales de AWS, sin terraform instalado y sin tocar ninguna cuenta. ¿Qué clase de error **no** puede encontrar con esta herramienta? Nombra al menos dos.

5. `04-identidades.tf` crea un `aws_iam_user` para una persona y le pone una contraseña estática. Checkov lo marca (`CKV2_AWS_22`, `CKV_AWS_273`). El módulo de Gitleaks del curso habría detectado también la contraseña. ¿Qué le das a cada herramienta y por qué dos herramientas distintas son mejor que una que lo haga todo?

---

## ⏭️ Siguiente

[Ejercicio 02 — Configuración y supresiones →](../02-configuracion-y-supresiones/README.md)

En el siguiente ejercicio el código ya está medio arreglado y el problema es otro: **qué decides que no se escanea, dónde lo declaras y qué dejas escrito para que la próxima persona entienda por qué**.
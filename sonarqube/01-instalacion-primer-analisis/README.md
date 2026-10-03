# Ejercicio 01 — Instalación y primer análisis

**Nivel:** 🟢 Básico · **Duración estimada:** 45 min

## 🎯 Objetivo

Levantar un servidor SonarQube local, crear un proyecto, generar un token de autenticación y ejecutar tu primer análisis. Interpretar correctamente los resultados.

## 📋 Requisitos previos

- Docker (o Java 21 instalado si prefieres la instalación desde ZIP)
- ~4 GB de RAM disponibles
- Python 3.10+ (para ejecutar los tests de los fixtures)

---

## ⚠️ Antes de empezar: comprueba tu RAM

```bash
# macOS
sysctl -n hw.memsize | awk '{print $1/1024/1024/1024" GB"}'

# Linux
free -h

# Windows (PowerShell)
(Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 1GB
```

**Si tienes menos de 4 GB libres**, tienes dos salidas válidas para este curso:

| Alternativa | Qué puedes hacer | Qué NO puedes hacer |
|---|---|---|
| **SonarQube for IDE** (VS Code / IntelliJ) | Ejercicios 01 y 03 a medias | Ejercicio 02 y 04 (requieren servidor) |
| **SonarQube Cloud** (plan gratuito) | Todo, sin servidor | Solo código público |

Los enunciados de abajo asumen el servidor local.

---

## Pasos

### 1. Levanta el servidor

```bash
docker run -d --name sonarqube -p 9000:9000 sonarqube:community
```

Sigue el arranque:

```bash
docker logs -f sonarqube
```

La primera vez descarga ~1 GB y tarda **1-2 minutos**. Espera a ver:

```
SonarQube is operational
```

> 🐢 **En Linux es común un error de arranque:**
> ```
> java.lang.IllegalStateException: max virtual memory areas vm.max_map_count [65530] is too low
> ```
> Solución:
> ```bash
> sudo sysctl -w vm.max_map_count=524288
> ```

### 2. Verifica el estado y cambia la contraseña

```bash
# Estado de la API
curl -s http://localhost:9000/api/system/status | python3 -m json.tool
# {"status": "UP"}
```

Abre <http://localhost:9000> e inicia sesión con `admin` / `admin`.

> 🔐 **Cambia la contraseña inmediatamente:**
> - Avatar arriba a la derecha → **My Account** → *Change password*
> - El token que generes en el paso 4 **da acceso completo**: trátalo como una credencial real.

### 3. Crea el proyecto

En la UI:

1. **Create new project** → *Manually*
2. Nombre: `DevSecOps Lab 01` · Project key: `devsecops-lab-01` · Main branch: `main`
3. Pulsa **Set up**

### 4. Genera el token

En el asistente de onboarding:

1. **Generate token** → nombre: `lab-01` → **Generate**
2. **Continuar** y copia el token (`squ_...`)
3. Guárdalo en un gestor de secretos o en tu `.env` local (¡**nunca** en un archivo que subas a Git!)

> ⚠️ Lección de seguridad: el token de SonarQube tiene el mismo nivel de permisos que un PAT de GitHub. Si alguien lo obtiene, puede subir análisis falsos a tu servidor.

### 5. Prepara el proyecto de prueba

```bash
cd fixtures/

# Instala las dependencias de test
python3 -m venv .venv && source .venv/bin/activate
pip install pytest

# Ejecuta los tests para ver qué hace el código
python3 -m pytest tests/ -v
```

Los tests pasan, pero el código tiene **muchos problemas** que los tests no detectan. Para eso sirve SonarQube.

### 6. Ejecuta el primer análisis

```bash
export SONAR_HOST_URL=http://localhost:9000
export SONAR_TOKEN=squ_TU_TOKEN_AQUI

sonar-scanner
```

El `sonar-project.properties` que hay en la carpeta ya define `sonar.sources` y `sonar.tests`.

> 💡 **Alternativa con Docker**, si no quieres instalar el scanner localmente:
> ```bash
> docker run --rm \
>   -e SONAR_HOST_URL=http://host.docker.internal:9000 \
>   -e SONAR_TOKEN=squ_TU_TOKEN_AQUI \
>   -v "$(pwd):/usr/src" \
>   sonarsource/sonar-scanner-cli
> ```
> En Linux, sustituye `host.docker.internal` por la IP del host.

### 7. Interpreta el dashboard

Vuelve a <http://localhost:9000> y abre el proyecto. Tu objetivo en este ejercicio es poder responder:

| Métrica | ¿Qué te dice? |
|---|---|
| **Reliability Rating** | Grados A-E. ¿Hay bugs? |
| **Security Rating** | Grados A-E. ¿Hay vulnerabilidades? |
| **Maintainability Rating** | Grados A-E. ¿Hay code smells? |
| **Coverage** | % de líneas cubiertas por tests |
| **Duplications** | % de líneas duplicadas |
| **Security Hotspots** | Puntos que requieren revisión humana |
| **NCLU** | New Code Lines of Code: líneas nuevas analizadas |
| **Overall Code** vs **New Code** | Toda la base de código vs. lo nuevo |

> 🔍 **Ojo con el Overall Code.** En el primer análisis, el 100 % del código es "nuevo". Por eso el Quality Gate fallará. Esto cambia a partir del ejercicio 02.

### 8. Clasifica los hallazgos por tipo

Abre la pestaña **Issues** y filtra por cada tipo. Debes poder identificar al menos:

| Tipo | Ejemplo en los fixtures | Regla típica |
|---|---|---|
| **Bug** | `calcular_pedido_completo` descarta la excepción y devuelve `None` implícito | S110, S2139 |
| **Vulnerability** | `DB_PASSWORD = "S3cr3tFicticio..."` hardcodeada | S2755 |
| **Vulnerability** | SQL construido con `%` en vez de parámetros | S608 |
| **Security Hotspot** | `random.randint()` para generar tokens | S2245 |
| **Code Smell** | `except KeyError: pass` vacío | S110 |
| **Code Smell** | `if True:` / `if False:` | S2589 |
| **Code Smell** | Variables asignadas y nunca usadas | S1481, S1854 |
| **Code Smell** | `if` que debería ser `elif` (descuentos encadenados) | S1871 |
| **Code Smell** | Función demasiado compleja | S3776 |

**Anota el número total de issues de cada tipo. Este es el resultado real de tu instalación** (debería estar en el entorno de los 15-25 issues y 1-3 hotspots).

### 9. Lee un issue con detalle

Abre cualquier issue y localiza:

- **Rule** → qué regla lo detectó
- **Severity** → qué tan grave es
- **Effort** → esfuerzo estimado para arreglarlo (minutos). Suma los Effort de todos los issues: es tu **deuda técnica** en minutos.
- **Issue creation date** → cuándo se introdujo (gracias al blame)
- **Tags** → `sonar:bug`, `sonar:security`, `cognitive-complexity`...
- **Hotspot** → si tiene "Resolve" / "Safe" / "To review"

> 💡 **El campo Effort es la joya de SonarQube para argumentar el coste de la deuda técnica.** El dashboard muestra un "Technical Debt" total. Lleva esa cifra a tu próxima reunión de equipo.

### 10. Analiza la duplicación

En el dashboard, sección **Duplications**, mira `pedidos.py`:

```
procesar_pedido()      ~ 30 líneas duplicadas con
procesar_devolucion()  → detectadas por CPD (Copy-Paste Detector)
```

CPD funciona por **tokens**, no por líneas idénticas: un bloque es duplicado si comparte al menos `sonar.cpd.python.minimumTokens` (default: **100**) tokens y `minimumLines` (default: **10**) líneas.

### 11. Genera la cobertura

La cobertura de Python **no es nativa** en SonarQube. Usa las herramientas de SonarSource:

```bash
pip install pytest-cov coverage

# Ejecuta los tests midiendo cobertura y genera coverage.xml (formato Cobertura)
python -m pytest --cov=. --cov-report=xml:coverage.xml

# Reanaliza. El scanner no genera la cobertura: solo la lee.
sonar-scanner -Dsonar.python.coverage.reportPaths=coverage.xml
```

> 📌 **Detalle importante:** `pytest-cov` escribe el informe directamente en el formato que SonarQube entiende. No hace falta ningún conversor intermedio. Si prefieres separar los pasos, `coverage run -m pytest` + `coverage xml` produce exactamente el mismo `coverage.xml`.

En el dashboard, **Coverage** debería mostrar un valor alrededor del **40 %**: los tests solo cubren 6 funciones de un código que tiene muchas más.

---

## ✅ Comprobación final

- [ ] El servidor está arrancado y `/api/system/status` devuelve `UP`
- [ ] He cambiado la contraseña de `admin`
- [ ] Tengo un proyecto creado y un token guardado de forma segura
- [ ] He ejecutado `sonar-scanner` con éxito
- [ ] Sé explicar la diferencia entre Overall Code y New Code
- [ ] He generado `coverage.xml` con `pytest --cov-report=xml` y lo he pasado al scanner
- [ ] Sé distinguir los 5 tipos de hallazgo de SonarQube
- [ ] Sé lo que significa el campo *Effort*

---

## 🤔 Preguntas de reflexión

1. En los fixtures hay un `API_TOKEN` hardcodeado y una contraseña de base de datos. ¿Por qué SonarQube los detecta pero un linter como `ruff` o `pylint` normalmente no? ¿Qué herramienta de este curso se habría detectado antes?
2. El Quality Gate está en rojo tras el primer análisis. ¿Es razonable? Explica por qué y qué definición de New Code lo arreglaría.
3. `validar_password()` tiene tres ramas que devuelven `True` y luego una `return False` inalcanzable. ¿Por qué un bug así puede sobrevivir tanto tiempo en producción?
4. Si el dashboard dice "Technical Debt: 5h 20min", ¿cómo lo usarías para priorizar el trabajo del sprint siguiente?
5. ¿Qué pasa con la cobertura si analizas el mismo proyecto dos veces sin volver a ejecutar los tests? ¿Por qué es un problema en CI?

---

## ⏭️ Siguiente

[Ejercicio 02 — Clean as You Code →](../02-clean-as-you-code/README.md)
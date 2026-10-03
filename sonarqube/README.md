# 📊 SonarQube — Análisis estático continuo y Quality Gates

> **Categoría:** SAST / Code Quality · **Etapa del Shift Left:** Pre-commit (IDE) + CI/CD · **Licencia:** SonarQube Community Build (gratuita)

---

## 1. ¿Qué es SonarQube?

**SonarQube** es una plataforma de **gestión de la calidad del código**. A diferencia de un linter que comprueba reglas una a una, SonarQube separa el código de todo lo que lo rodea (historial de Git, issues, hotspots, cobertura de tests) y lo convierte en un **sistema de control de calidad continuo** con una puerta de entrada: el **Quality Gate**.

La analogía útil: si un linter es un **humo detector**, SonarQube es la **central de alarma contra incendios** de tu edificio.

### La diferencia con un linter tradicional

| | Linter (ESLint, Pylint…) | SonarQube |
|---|---|---|
| Salida | Lista de problemas en la consola | Dashboard, histórico y tendencias |
| Persistencia | Se olvida al terminar el comando | Guarda el resultado de cada análisis |
| Calidad de diseño | No la mide | Complejidad, duplicación, acoplamiento, deuda técnica |
| Puerta de calidad | No | **Quality Gate** con políticas configurables |
| Distingue "nuevo" de "viejo" | No | **New Code** (Clean as You Code) |
| Informe al revisor | No | Comentarios en el pull request |
| Servidor | No | Sí (centraliza, compara, notifica) |

### Por qué importa en DevSecOps

SonarQube es de las herramientas que mejor materializa el concepto de **Clean as You Code** (limpieza a medida que escribes código), que es la expresión práctica del Shift Left:

> No se trata de arreglar un proyecto heredado entero, sino de **no crear deuda técnica nueva** y dejar la deuda vieja documentada y medida.

El problema clásico que SonarQube resuelve:

```
Enfoque tradicional                 Enfoque Clean as You Code
─────────────────────               ──────────────────────────
"Hay 4.500 problemas"               "Este PR introduce 3 problemas"
"Adiós."                            "Arregla estos 3 y sigue."
                                    La deuda antigua se congela.
```

---

## 2. Arquitectura: servidor + scanner

Este es el punto que más confunde al principio, y es **clave** entenderlo:

```
   Tu máquina o el runner de CI
   ┌────────────────────────────────────┐
   │                                    │
   │  ① SonarScanner CLI               │
   │     - Analiza el código           │
   │     - Sube los resultados          │
   │                                    │
   └──────────────┬─────────────────────┘
                  │  HTTP(S) + token
                  ▼
   ┌────────────────────────────────────┐
   │  ② Servidor SonarQube             │
   │     - Base de datos (análisis      │
   │       históricos)                  │
   │     - Calcula Quality Gate         │
   │     - Web UI con el dashboard      │
   │     - Integra escáneres externos   │
   │       (Gitleaks, dependency-check) │
   │                                    │
   └──────────────┬─────────────────────┘
                  │
                  ▼
   ┌────────────────────────────────────┐
   │  ③ Tu navegador                    │
   │     http://localhost:9000          │
   └────────────────────────────────────┘
```

**Consecuencias prácticas:**

- El **scanner** es una CLI que se instala en tu máquina (o en el runner de CI). Es ligera.
- El **servidor** es una aplicación Java pesada: necesita **4 GB de RAM**, 2 núcleos y ~30 GB de disco.
- Puedes tener **muchos proyectos** en un solo servidor: es el modelo centralizado.
- El servidor **no es necesario para analizar**, solo para guardar resultados. Por eso existen las IDE integrations (SonarQube for VS Code / IntelliJ) que funcionan sin servidor.

### Herramientas del ecosistema

| Pieza | Función |
|---|---|
| **SonarQube Server** | El servidor central (base de datos + UI + Quality Gate) |
| **SonarScanner CLI** | Analizador genérico para proyectos sin build tool específico |
| **SonarScanner for Maven / Gradle / .NET / NPM** | Analizadores integrados en el build |
| **SonarQube for IDE** | Análisis dentro de VS Code / IntelliJ (Shift Left máximo) |
| **SonarQube Cloud** | Servicio SaaS; alternativa al servidor autoalojado |
| **Clean as You Code** | La metodología que da sentido a toda la plataforma |

---

## 3. Los tres conceptos que debes dominar

### 3.1 Quality Profile — *qué* reglas se aplican

Un perfil de calidad es el **conjunto de reglas activas** para un lenguaje en un proyecto. El perfil por defecto y recomendado es **Sonar way**.

Se configura en la UI: *Quality Profiles → Sonar way → Editar reglas*, o mediante la API.

### 3.2 Quality Gate — *cuándo* el código es inaceptable

Un Quality Gate es un conjunto de **condiciones** que el código debe cumplir. Si alguna falla, el Quality Gate queda en **rojo** y el pipeline puede bloquearse.

El Quality Gate por defecto, **Sonar way**, tiene 4 condiciones:

| Condición | Valor |
|---|---|
| No se introducen nuevos issues | 0 en código nuevo |
| Todas las vulnerabilidades de seguridad nuevas revisadas | 100 % |
| Cobertura de tests del código nuevo | ≥ 80 % |
| Duplicación en código nuevo | ≤ 3 % |

> 📌 **Tendencia importante:** SonarSource está retirando el concepto de *Security Hotspot*; muchas reglas que antes generaban hotspots ahora generan vulnerabilidades directamente. Los Quality Gates se van actualizando. Verifica las condiciones reales en tu instancia, que pueden variar con la versión.

### 3.3 New Code — *qué* código cuenta

Este es el corazón de Clean as You Code. La definición se configura en tres niveles:

| Definición | Qué considera "código nuevo" |
|---|---|
| **Previous version** | Todo lo cambiado desde el último incremento de versión |
| **Number of days** | Todo lo cambiado en los últimos X días (por defecto 30, máximo 90) |
| **Specific analysis** | Todo lo cambiado desde un análisis concreto (manual) |
| **Reference branch** | Todo lo que difiere de la rama principal (⚠️ solo SonarQube Server) |

> 🧠 **Por qué esto lo cambia todo:** con `Previous version` + Quality Gate, el Quality Gate **solo mira el código nuevo**. Tu deuda técnica de 2019 no bloquea tu PR de hoy, pero los problemas nuevos sí.

**Fudge factor:** para evitar que cambios pequeños fallen por desproporción, las condiciones de cobertura y duplicación se **ignoran** hasta que haya al menos 20 líneas nuevas. Se puede desactivar si quieres que el control sea estricto desde la primera línea.

---

## 4. Installation

### 4.1 Requisitos del servidor

| Recurso | Instalación pequeña (≤1M LOC) | Instalación grande (≤50M LOC) |
|---|---|---|
| RAM | **4 GB** | 16 GB |
| CPU | 2 núcleos | 8 núcleos |
| Disco | 30 GB (+ 10 % libre) | — |

**Sistemas operativos soportados:** Linux (x64, AArch64), Windows (x64), macOS (x64, AArch64).

> ⚠️ **SonarQube usa Elasticsearch internamente**, y eso impone limitaciones: no funciona bien en entornos como AWS Fargate, Azure App Service o AWS App Runner, porque no se pueden cumplir los requisitos de sistema de Elasticsearch (`vm.max_map_count`, etc.).

> 💡 **Si 4 GB de RAM no están disponibles en tu máquina**, tienes dos alternativas válidas para el curso:
> 1. **SonarQube for IDE** (VS Code / IntelliJ): análisis local sin servidor, gratis, sin Docker. Es la capa 1 de Clean as You Code y funciona sin prácticamente recursos.
> 2. **SonarQube Cloud**: análisis en la nube con plan gratuito para código abierto.

---

### 🍎 macOS (la vía recomendada para el curso)

#### Opción A — Docker (recomendada)

```bash
# Arranca el servidor
docker run -d \
  --name sonarqube \
  -p 9000:9000 \
  sonarqube:community

# Sigue el arranque (tarda 1-2 minutos la primera vez)
docker logs -f sonarqube

# Cuando veas "SonarQube is operational", abre:
# http://localhost:9000
```

**Credenciales por defecto:** usuario `admin`, contraseña `admin`.

> 🔐 **Cambia la contraseña inmediatamente** si el servidor va a quedar accesible desde la red. Se hace **desde la interfaz web**, no por consola: *Log in* como `admin` → clic en tu avatar (arriba a la derecha) → *My Account* → *Change password*.
>
> ⚠️ `admin` es una cuenta real con todos los permisos. Mientras siga usando `admin`/`admin`, cualquiera que alcance el puerto 9000 tiene el control total de tu servidor. Este es exactamente el escenario de *credenciales por defecto* que Gitleaks detecta en el código, pero aquí el problema es la configuración del servidor.

**Variables de entorno útiles:**

```bash
docker run -d --name sonarqube -p 9000:9000 \
  -e SONAR_WEB_JAVA_OPTS="-Xms512m -Xmx2g" \
  sonarqube:community
```

> ⚠️ **No uses `SONAR_ES_BOOTSTRAP_CHECKS_DISABLE=true` como atajo.** Ese flag desactiva las comprobaciones de arranque de Elasticsearch y puede dejar el índice en un estado inconsistente. Si el arranque falla por `vm.max_map_count`, la solución es la de abajo.

> 🐢 **¿El arranque falla con `vm.max_map_count`?** Es el error más común en Linux:
> ```bash
> sudo sysctl -w vm.max_map_count=524288
> ```

#### Opción B — Instalación desde ZIP

```bash
# 1. Instala Java 21 (o 25) — Java 17 ya NO tiene soporte
brew install openjdk@21

# 2. Descarga la edición Community
#    https://docs.sonarsource.com/sonarqube-community-build/server-installation/from-zip-file/

# 3. Descomprime en /opt (nunca como root)
unzip sonarqube-*.zip -d /opt/

# 4. Arranca en primer plano para ver los logs
sudo -u $USER /opt/sonarqube-*/bin/macosx-universal/sonar.sh console
```

Los scripts de arranque disponibles: `sonar.sh` (Linux/macOS), `windows-x86-64/StartSonar.bat` (Windows), y los modos `console` (foreground), `start`, `stop`, `status`, `restart`.

---

### 🐧 Linux

```bash
# Opción A — Docker (igual que macOS)
docker run -d --name sonarqube -p 9000:9000 sonarqube:community

# Requisito crítico de Elasticsearch en Linux
sudo sysctl -w vm.max_map_count=524288
echo "vm.max_map_count=524288" | sudo tee -a /etc/sysctl.conf

# Opción B — ZIP
sudo apt install openjdk-21-jre unzip
unzip sonarqube-*.zip -d /opt/
# Arranca como usuario NO root
/opt/sonarqube-*/bin/linux-x86-64/sonar.sh start
```

---

### 🪟 Windows

#### Opción A — Docker Desktop

```powershell
# Requiere Docker Desktop con al menos 4 GB asignados a la VM
docker run -d --name sonarqube -p 9000:9000 sonarqube:community
```

> 💡 En Docker Desktop: *Settings → Resources → Memory* debe estar en **4 GB o más**.

#### Opción B — ZIP

1. Instala **Java 21 o 25** desde [Adoptium](https://adoptium.net/) (Java 17 ya no tiene soporte).
2. Descarga el ZIP de la edición Community.
3. Descomprime en `C:\sonarqube`.
4. Arranca como **usuario sin privilegios de administrador**:

```powershell
cd C:\sonarqube
.\bin\windows-x86-64\StartSonar.bat
```

---

### 4.2 Instalación del SonarScanner CLI

El scanner es independiente del sistema operativo y del servidor.

```bash
# --- macOS / Linux: vía Homebrew ---
brew install sonar-scanner

# --- Cualquier SO: Docker ---
docker run --rm \
  -e SONAR_HOST_URL="http://localhost:9000" \
  -e SONAR_TOKEN="squ_tu_token" \
  -v "$(pwd):/usr/src" \
  sonarsource/sonar-scanner-cli

# --- Cualquier SO: ZIP ---
# Descarga el binario para tu plataforma y descomprime
export PATH="/ruta/a/sonar-scanner/bin:$PATH"
```

**Requisitos de Java del scanner:**

| Situación | Java requerido |
|---|---|
| Con auto-provisioning de JRE (por defecto) | Java 11+ (desde SonarScanner CLI 7.2) |
| Con auto-provisioning desactivado | **Java 21** (Java 17 se eliminó en 26.8) |

#### ✅ Verificación

```bash
sonar-scanner --version
java -version
docker ps | grep sonarqube
curl -s http://localhost:9000/api/system/status | python3 -m json.tool
```

El último comando debe devolver `{"status": "UP"}`.

---

## 5. Uso básico

### 5.1 Crear un proyecto y un token

En la UI de SonarQube (`http://localhost:9000`):

1. **Create new project** → *Manually* → nombre del proyecto → **Set up**.
2. Elige el lenguaje principal → **Generate token** → nombre del token → **Continue**.
3. Copia el token (`squ_...`). **Guárdalo**: es tu credencial.

### 5.2 Ejecutar el primer análisis

```bash
cd fixtures/
export SONAR_HOST_URL=http://localhost:9000
export SONAR_TOKEN=squ_TU_TOKEN_AQUI

sonar-scanner \
  -Dsonar.projectKey=devsecops-lab-01 \
  -Dsonar.sources=src \
  -Dsonar.tests=tests
```

O define `sonar-project.properties` en la raíz del proyecto:

```properties
sonar.projectKey=devsecops-lab-01
sonar.projectName=DevSecOps Lab 01
sonar.sources=src
sonar.tests=tests
```

Y simplemente:

```bash
sonar-scanner
```

### 5.3 Parámetros de análisis esenciales

**Obligatorios:**

| Parámetro | Variable de entorno | Descripción |
|---|---|---|
| `sonar.token` | `SONAR_TOKEN` | Token de autenticación (reemplaza a `sonar.login`/`sonar.password`, deprecated) |
| `sonar.host.url` | `SONAR_HOST_URL` | URL del servidor |
| `sonar.projectKey` | — | Identificador único del proyecto |

**Alcance del análisis:**

| Parámetro | Descripción |
|---|---|
| `sonar.sources` | Rutas del código principal |
| `sonar.tests` | Rutas del código de test |
| `sonar.projectBaseDir` | Directorio base del análisis |
| `sonar.exclusions` | Ficheros a excluir del análisis |
| `sonar.test.exclusions` | Ficheros de test a excluir |
| `sonar.coverage.exclusions` | Ficheros excluidos de la cobertura |
| `sonar.cpd.exclusions` | Ficheros excluidos de la detección de duplicación |
| `sonar.scm.disabled` | Desactiva el análisis de SCM (acelera, pero pierde issues y blame) |
| `sonar.filesize.limit` | Tamaño máximo (MB) de un fichero analizado. Default `20` |

**Puertas de calidad y CI:**

| Parámetro | Default | Descripción |
|---|---|---|
| `sonar.qualitygate.wait` | `false` | Espera al Quality Gate y **falla el pipeline** si falla |
| `sonar.qualitygate.timeout` | `300` | Segundos de espera del resultado |

**Enlaces mostrados en la UI:**

| Parámetro | Descripción |
|---|---|
| `sonar.links.homepage` | Página del proyecto |
| `sonar.links.scm` | Repositorio de código |
| `sonar.links.ci` | Sistema de CI |
| `sonar.links.issue` | Tracker de issues |

> 🔐 **Regla de oro:** el token **nunca** va hardcodeado en `sonar-project.properties`. Va en variable de entorno o en el secret store de CI. Exactamente el mismo principio que viste en el módulo de Gitleaks.

### 5.4 Configuración declarativa

Además de `sonar-project.properties`, SonarQube soporta JSON:

```json
{
  "sonar": {
    "projectKey": "mi-proyecto",
    "sources": "src",
    "tests": "tests",
    "exclusions": "**/migraciones/**",
    "sonar.coverage.exclusions": "**/*_test.py"
  }
}
```

---

## 6. Las tres capas de Clean as You Code

```
   Capa 1                    Capa 2                     Capa 3
   IDE                       Pull Request                Rama principal
   ───────────               ──────────────────          ──────────────────
   SonarQube for IDE         Análisis del PR             Análisis de main
   El error aparece          Solo código nuevo           Tendencias y
   al escribir la línea      Check del Quality Gate      deuda técnica
   ~0 segundos               ~2 minutos                  ~5 minutos

   El más rápido             El que bloquea el merge     El que da contexto
   y barato                  y da la señal al equipo     histórico
```

SonarSource recomienda implementar las tres. Esta es la materialización más directa del Shift Left que verás en el curso.

---

## 7. Limitaciones que debes conocer

- **La decoración de Pull Requests requiere una edición de pago.** El *análisis* de ramas cortas funciona en Community Build, pero el comentario automático con el desglose de issues en el diff del PR (Pull Request decoration) es una función de Developer Edition y superiores. Con Community Build, el flujo del ejercicio 04 se apoya en el **check del Quality Gate** como señal en el PR, no en los comentarios.
- **Consumo de recursos elevado:** 4 GB de RAM solo para el servidor. En laptops con 8 GB de RAM resulta ajustadísimo.
- **Heavyweight:** para un proyecto pequeño, montar un SonarQube local es mucho más costoso que un `ruff` o un `eslint`. El valor está en la persistencia, la política y el histórico.
- **Gestionar Quality Gates y perfiles** requiere el permiso *Administer Quality Gates* / *Administer Quality Profiles*. El gate integrado **Sonar way** es de solo lectura; para cambiar sus condiciones hay que crear un Quality Gate propio, y para crearlo hace falta ese permiso.
- **Los falsos positivos existen** y hay que gestionarlos, no ignorarlos en bloque. Es el tema central del ejercicio 03.
- **Los issues heredados bloquean la Quality Gate** si usas una definición de nuevo código mal configurada. Un error muy común al arrancar.
- **El análisis de cobertura de Python no es nativo:** hay que ejecutar `coverage.py` antes del escáner, generar `coverage.xml` (formato Cobertura) y apuntar a él con `sonar.python.coverage.reportPaths`. Para Java, Maven y Gradle lo hacen automáticamente.

---

## 8. Ejercicios de esta carpeta

| Ejercicio | Tema | Nivel |
|---|---|---|
| `01-instalacion-primer-analisis/` | Levantar el servidor, generar el token, primer análisis, interpretar los hallazgos | 🟢 Básico |
| `02-clean-as-you-code/` | Quality Profiles, Quality Gates, definición de New Code, pasar de rojo a verde | 🟡 Intermedio |
| `03-exclusiones-y-falsos-positivos/` | Exclusiones, cobertura, duplicación, gestión de falsos positivos sin destruir el control | 🟡 Intermedio |
| `04-ci-github-actions/` | SonarQube en el pipeline, Quality Gate como puerta, branch protection | 🔴 Avanzado |

> 🧪 Todos los ejercicios usan **fixtures de Python deliberadamente defectuosos**: no es código real, es material de laboratorio con bugs, vulnerabilidades, hotspots y duplicación inyectados a propósito.

> 🧪 **Prueba de humo del curso (sin servidor):** los fixtures se analizan sintácticamente y sus tests pasan. El único "secreto" que Gitleaks detecta en este módulo está en un fixture, a propósito.
> ```bash
> # 1. Todo el código Python es válido
> python3 -m py_compile sonarqube/*/fixtures/src/*.py sonarqube/*/fixtures/tests/*.py
>
> # 2. Los tests pasan en los 3 ejercicios con fixtures
> for d in sonarqube/0[123]*/fixtures; do (cd $d && python3 -m pytest -q); done
>
> # 3. Solo queda 1 hallazgo de Gitleaks, y es intencionado
> cd sonarqube && gitleaks dir . --redact
> ```

---

## 9. Referencias

- **Documentación oficial (Community Build):** https://docs.sonarsource.com/sonarqube-community-build
- **Repositorio:** https://github.com/SonarSource/sonarqube
- **Quality Gates:** https://docs.sonarsource.com/sonarqube-community-build/quality-standards-administration/managing-quality-gates/introduction-to-quality-gates.md
- **New Code:** https://docs.sonarsource.com/sonarqube-community-build/user-guide/about-new-code.md
- **Parámetros de análisis:** https://docs.sonarsource.com/sonarqube-community-build/analyzing-source-code/analysis-parameters/parameters-not-settable-in-ui.md
- **SonarScanner CLI:** https://docs.sonarsource.com/sonarqube-community-build/analyzing-source-code/scanners/sonarscanner.md
- **Requisitos del servidor:** https://docs.sonarsource.com/sonarqube-community-build/server-installation/server-host-requirements.md
- **SonarQube Scan GitHub Action:** https://github.com/SonarSource/sonarqube-scan-action
- **Quality Gate Check GitHub Action:** https://github.com/SonarSource/sonarqube-quality-gate-action
- **Integración con GitHub Actions:** https://docs.sonarsource.com/sonarqube-server/analyzing-source-code/ci-integration/github-actions
- **Cobertura de tests en Python:** https://docs.sonarsource.com/sonarqube-server/analyzing-source-code/test-coverage/python-test-coverage
- **Limpieza de hotspots → vulnerancias (migración):** https://docs.sonarsource.com/sonarqube-community-build/server-update-and-maintenance/update/post-update-steps.md

---

## 10. Glosario rápido

| Término | Significado |
|---|---|
| **Issue** | Problema detectado. Según tipo: *Bug*, *Vulnerability*, *Code Smell*. |
| **Security Hotspot** | Punto de código inseguro que requiere revisión humana. En retirada. |
| **Code Smell** | Problema de mantenibilidad, sin impacto directo en ejecución. |
| **Technical Debt** | Esfuerzo estimado para llevar el código a un estándar. |
| **Quality Profile** | Conjunto de reglas activas por lenguaje. |
| **Quality Gate** | Conjunto de condiciones que el código debe cumplir. |
| **New Code** | Definición del código actualmente analizado como "nuevo". |
| **Fudge factor** | Margen de tolerancia para cambios pequeños (< 20 líneas). |
| **Duplication (CPD)** | Copy-Paste Detector: bloques de código duplicados. |
| **Blame** | Seguimiento de qué commit introdujo cada línea. |
| **Scanner** | CLI que analiza el código y sube los resultados al servidor. |
# 🛡️ DevSecOps Exercises

Laboratorio práctico de **DevSecOps** construido como curso autodirigido. Cada carpeta de la raíz contiene una herramienta de seguridad, su introducción teórica y los ejercicios correspondientes para practicarla de forma hands-on.

---

## 📖 Parte 1 — ¿Qué es DevSecOps?

### 1.1 Definición

**DevSecOps** es la práctica de integrar la seguridad (Security) de forma nativa dentro del ciclo de vida de desarrollo de software (**Dev**elopment + **Sec**urity + **Dev**Ops → Operations). No se trata de un producto, una herramienta ni un área aislada del equipo: es una **cultura**, una forma de trabajo en la que las mismas personas que escriben el código también son responsables de la seguridad del software que construyen.

La idea central es simple: **la seguridad no es una etapa final entre desarrollo y producción, es una responsabilidad compartida durante todo el proceso.**

### 1.2 El problema: el modelo tradicional

En los enfoques clásicos, el desarrollo y la seguridad vivían en islas separadas:

```
Desarrollo  ──►  QA / Pruebas  ──►  Seguridad  ──►  Release  ──►  Producción
   (meses)          (semanas)        (días)         (días)        ...
```

Este modelo, conocido como **"security silo"** o *security theater*, produce varios problemas:

- **Cuello de botella:** El equipo de seguridad recibe todo el código al final del ciclo, por lo que la revisión se vuelve lenta y la entrega se ralentiza.
- **Correcciones tardías y costosas:** Un fallo de seguridad detectado en producción cuesta, según estudios de IBM y NIST, entre **10 y 100 veces más** que el mismo fallo detectado en la fase de diseño.
- **Falsas positives y fatiga de alertas:** Un análisis manual de vulnerabilidades sin automatización produce decenas de hallazgos falsos que agotan al equipo.
- **Falta de contexto:** Los analistas de seguridad no conocen la intención del negocio ni la lógica de la aplicación, por lo que sus hallazgos son menos útiles.
- **Desalineación:** Seguridad y desarrollo compiten por recursos. Seguridad pide más tiempo, desarrollo pide ir más rápido.
- **Fuga de secretos:** Sin controles automatizados, las credenciales y tokens terminan en el repositorio, en los logs o en la imagen de contenedor.

### 1.3 ¿Qué es **Shift Left Security**?

**Shift Left** ("desplazar a la izquierda") es la práctica de **mover las actividades de seguridad hacia etapas anteriores del ciclo de desarrollo**, de modo que la seguridad se valida desde el primer momento en que se escribe una línea de código, no al final.

La metáfora proviene de representar el ciclo de vida como una línea de tiempo:

```
ANTES (Security a la derecha)                DESPUÉS (Shift Left)
──────────────────────────────────────────────────────────────────────►
Requisitos → Diseño → Desarrollo → Pruebas → Build → Deploy → Operación
                                                                    ▲
                                                          DETECTAMOS AQUÍ
                                                          (muy tarde,
                                                           muy caro)
     Requisitos → Diseño → Desarrollo ──────────────────────────────►
           ▲
  VALIDAMOS AQUÍ
  (temprano, barato y con contexto)
```

En la práctica, **Shift Left significa**:

1. **Analizar desde el diseño:** Threat modeling y revisión de arquitectura antes de escribir código.
2. **Analizar el código:** SAST (Static Application Security Testing) y Dependency Scanning sobre el repositorio en cada commit o pull request.
3. **Analizar las dependencias:** SCA (Software Composition Analysis) para detectar CVEs conocidas en librerías de terceros.
4. **Analizar la configuración:** IaC scanning para detectar buckets abiertos, grupos de seguridad laxos o credenciales hardcodeadas.
5. **Analizar el binario/entorno:** Escaneo de imágenes de contenedor, DAST y pruebas de infraestructura en despliegue.
6. **Automatizar el conocimiento:** la única forma de que las tareas de seguridad se ejecuten de forma repetible es mediante pipelines: cada hallazgo debe quedar registrado, con responsable y fecha.

#### Los pilares del Shift Left

| Pilar | Qué hace | Ejemplo de herramienta |
|---|---|---|
| **Pre-commit** | Analiza antes de que el cambio llegue al repositorio | `gitleaks`, `detect-secrets` |
| **CI/CD (commit/PR)** | Analiza en cada push o pull request | CodeQL, Semgrep, SonarQube |
| **SCA / Dependencias** | Detecta CVEs en dependencias transitivas | `trivy`, `npm audit`, Dependabot |
| **IaC / Configuración** | Detecta errores de configuración en IaC y secretos | `checkov`, `tfsec`, `trivy config` |
| **Contenedores / Runtime** | Analiza imágenes y entorno desplegado | `trivy image`, `grype`, Falco |
| **DAST** | Analiza la aplicación en ejecución (pruebas dinámicas) | OWASP ZAP, `nikto` |
| **Observabilidad** | Detecta incidentes en producción | SIEM, Grafana, Loki |

> ⚠️ **Shift Left no significa "todo antes".** Significa que **cada control se aplica en el punto más temprano y barato donde ese tipo de fallo puede ser detectado y corregido**.

#### ¿Cuándo no funciona Shift Left?

- **Código heredado sin pruebas:** si no existe una base de pruebas, el análisis dinámico no es confiable y el análisis estático genera demasiado ruido.
- **Falsos positivos no gestionados:** si el equipo no revisa ni ajusta las reglas, los desarrolladores terminan ignorando los hallazgos.
- **Sin responsables:** el Shift Left sin ownership se convierte en reportes que nadie lee.
- **Aplicando Shift Left demasiado tarde en el ciclo:** un SAST sobre un binario ya compilado no es Shift Left, es un escaneo tardío con pasos adicionales.

---

## 📁 Parte 2 — Estructura del repositorio

### 2.1 Organización general

La raíz del repositorio contiene **una carpeta por herramienta/tecnología de DevSecOps**. No existe un único directorio de ejercicios: los ejercicios viven junto a la herramienta que cubren, para que la teoría y la práctica estén siempre en el mismo lugar.

```
devSecOpsExercise/
├── README.md                  ← Este documento (índice general del curso)
├── gitleaks/                  ← Carpeta de la herramienta
│   ├── README.md              ← Introducción teórica a la herramienta
│   ├── .gitleaksignore
│   ├── 01-reconocimiento/     ← Ejercicios
│   ├── 02-escaneo-basico/
│   ├── 03-configuracion-allowlists/
│   ├── 04-pre-commit/
│   ├── 05-ci-github-actions/
│   └── 06-remediacion/
├── sonarqube/                 ← Carpeta de la herramienta
│   ├── README.md              ← Introducción teórica a la herramienta
│   ├── .gitleaksignore
│   ├── 01-instalacion-primer-analisis/
│   ├── 02-clean-as-you-code/
│   ├── 03-exclusiones-y-falsos-positivos/
│   └── 04-ci-github-actions/
└── ...                        ← Nuevas herramientas se añaden aquí
```

### 2.2 Reglas de la estructura

Cada carpeta de herramienta **debe** cumplir con lo siguiente:

1. **Un `README.md` de introducción** (obligatorio):
   - ¿Qué es la herramienta y qué problema resuelve?
   - ¿Cómo encaja en el ciclo de DevSecOps / Shift Left?
   - Casos de uso principales y limitaciones.
   - Instalación y configuración básica.
   - Comandos o flags más usados.
   - Referencias a la documentación oficial.
   - Índice de los ejercicios disponibles en esa carpeta.

2. **Carpetas de ejercicios numeradas** con formato `NN-tema`:
   - `01-` → 02- → 03- en orden de dificultad creciente.
   - Cada carpeta de ejercicio debe tener su propio `README.md` con:
     - Objetivo del ejercicio.
     - Requisitos previos.
     - Pasos numerados.
     - Comandos esperados y su salida correcta.
     - Preguntas de comprensión o reflexión final.

3. **Soluciones** (opcional): se colocan en un subdirectorio `solucion/` dentro del ejercicio, para que puedas comparar tu resultado.

4. **Archivos de apoyo** permitidos dentro de una carpeta de herramienta:
   - `fixtures/` — archivos vulnerables o de prueba (con secretos falsos).
   - `scripts/` — scripts auxiliares.
   - `config/` — archivos de configuración de ejemplo.

5. **Nunca subas secretos reales** al repositorio. Todos los secretos usados en los ejercicios son **ficticios**, están rotulados como tales y están diseñados para ser detectados por las herramientas (eso es justamente lo que se practica en los ejercicios).

### 2.3 Ejemplo de referencia: carpeta `gitleaks/`

```
gitleaks/
├── README.md              ← Introducción a Gitleaks
├── .gitleaksignore        ← Ignora los falsos positivos de los enunciados
├── 01-reconocimiento/
│   ├── README.md
│   └── fixtures/
│       └── app-basico/
└── 05-ci-github-actions/
    ├── README.md
    └── .github/
        └── workflows/
            └── gitleaks.yml
```

### 2.4 Ejemplo de referencia: carpeta `sonarqube/`

```
sonarqube/
├── README.md              ← Introducción a SonarQube
├── .gitleaksignore
├── 01-instalacion-primer-analisis/
│   ├── README.md
│   └── fixtures/
│       ├── sonar-project.properties
│       ├── src/
│       └── tests/
├── 02-clean-as-you-code/
│   └── fixtures/
├── 03-exclusiones-y-falsos-positivos/
│   └── fixtures/
│       ├── sonar-project.properties
│       ├── sonar-project.final.properties   ← la solución
│       ├── src/
│       ├── vendor/                          ← código generado
│       └── tests/
└── 04-ci-github-actions/
    ├── README.md
    └── .github/
        └── workflows/
            ├── sonar.yml
            └── security-pipeline.yml        ← Gitleaks + SonarQube
```

---

## 🍴 Parte 3 — Cómo trabajar con este repositorio

### 3.1 Fork obligatorio

**Este repositorio es de solo lectura. Debes trabajo con una `fork` en tu propia cuenta de GitHub.**

```
             ┌──────────────────┐
             │  Repo original   │  (upstream — SOLO LECTURA)
             │  DevSecOpsCourse │
             └────────┬─────────┘
                      │  git fetch upstream
                      ▼
             ┌──────────────────┐
             │  Tu fork         │  (origin — TU cuenta)
             │  @tu-usuario     │
             └────────┬─────────┘
                      │  git push
                      ▼
             ┌──────────────────┐
             │  Pull Request    │  (upstream ← tu fork)
             └──────────────────┘
```

**Motivo:** los ejercicios están pensados para que los modifiques, rompas, experimentes y completes. Trabajar sobre tu propio fork garantiza que:

- Tus soluciones, notas y experimentos **nunca afectan** el repositorio principal compartido con el resto de alumnos.
- Puedes organizar tu progreso con commits, ramas y tu propio historial.
- Al final, puedes enviar un **Pull Request** con tus soluciones o mejoras hacia el repo principal (suele ser buena práctica y parte de la evaluación).

### 3.2 Configuración inicial

```bash
# 1. Haz click en "Fork" arriba a la derecha en GitHub

# 2. Clona TU fork
git clone https://github.com/<TU_USUARIO>/devSecOpsExercise.git
cd devSecOpsExercise

# 3. Añade el repositorio original como "upstream"
git remote add upstream https://github.com/<ORGANIZACION>/devSecOpsExercise.git

# 4. Verifica los remotos
git remote -v
# origin    https://github.com/<TU_USUARIO>/devSecOpsExercise.git (fetch/push)
# upstream  https://github.com/<ORGANIZACION>/devSecOpsExercise.git (fetch/push)
```

### 3.3 Flujo de trabajo recomendado

```bash
# Mantener tu fork sincronizado con el upstream
git fetch upstream
git checkout main
git merge upstream/main

# Trabajar en una rama por ejercicio o por herramienta
git checkout -b exercise/gitleaks-01-basico

# ... resuelve el ejercicio ...

git add .
git commit -m "feat(gitleaks): resuelve ejercicio 01 - escaneo básico"
git push origin exercise/gitleaks-01-basico
```

### 3.4 Reglas de contribución

- ✅ Trabaja siempre en **ramas**, nunca directamente en `main`.
- ✅ Usa **mensajes de commit descriptivos**, preferiblemente siguiendo [Conventional Commits](https://www.conventionalcommits.org/):
  `feat(scope): descripción` · `fix(scope): descripción` · `docs(scope): descripción` · `chore(scope): descripción`
- ✅ **Nunca** subas credenciales, tokens o claves reales.
- ✅ Si encuentras un error en el material, envíalo como Pull Request al upstream.
- ❌ No modifiques el `README.md` raíz salvo que añadas contenido a la sección de índice.

---

## 📚 Índice de herramientas

| Herramienta | Categoría | Etapa del Shift Left | Estado |
|---|---|---|---|
| [Gitleaks](gitleaks/README.md) | Secret Scanning | Pre-commit / CI | ✅ 6 ejercicios |
| [SonarQube](sonarqube/README.md) | SAST / Code Quality | IDE + CI/CD | ✅ 4 ejercicios |
| _Próximamente..._ | | | |

---

## 🧰 Requisitos generales

- **Git** ≥ 2.30
- **Docker** (para los ejercicios que usan imágenes)
- **GitHub CLI (`gh`)** — opcional, para la parte de Pull Requests
- Conocimientos básicos de línea de comandos y de Git

---

## 📄 Licencia

Este material es de uso educativo. Consulta el archivo de licencia del repositorio para más detalles.

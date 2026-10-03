# AGENTS.md

Curso autodirigido de DevSecOps. Cada carpeta raíz (`gitleaks/`, `sonarqube/`) es un módulo: un `README.md` teórico en español + ejercicios numerados `NN-tema/`. No hay código de aplicación, ni build, ni lint, ni gestor de paquetes. La documentación **es** el producto.

## Verificación (smoke tests documentados en los READMEs raíz de cada módulo)

Sin servidor ni Docker, desde la raíz del repo:

```bash
# Gitleaks: debe reportar 16 hallazgos (ficticios, por diseño)
cd gitleaks && gitleaks dir . --redact -v

# SonarQube: sintaxis Python válida
python3 -m py_compile sonarqube/*/fixtures/src/*.py sonarqube/*/fixtures/tests/*.py

# SonarQube: los 3 conjuntos de fixtures pasan (6 + 7 + 6 tests)
for d in sonarqube/0[123]*/fixtures; do (cd $d && python3 -m pytest -q); done

# SonarQube: debe reportar 1 solo hallazgo (LEGACY_DB_PASSWORD en 02, intencionado)
cd sonarqube && gitleaks dir . --redact
```

Si cualquiera de estos números cambia, el contenido de un módulo se ha desincronizado de su `.gitleaksignore` o de sus enunciados.

## Los secretos falsos son intencionales

`fixtures/` contiene credenciales ficticias **que deben seguir detectándose**. Los hallazgos de Gitleaks no son un bug: son el material de los ejercicios. No los "arregles" ni los muevas a allowlists.

Los `.gitleaksignore` (`gitleaks/.gitleaksignore`, `sonarqube/.gitleaksignore`) ignoran **solo hallazgos dentro de READMEs** — ejemplos de comandos en la documentación. Sus entradas son fingerprints `<ruta>:<ruleID>:<línea>`, o sea **incluyen número de línea**: cualquier edición que añada o quite líneas en esos README invalida la entrada y el smoke test de arriba devuelve más hallazgos de los esperados. Si cambia el conteo, regenera con `gitleaks dir . --report-path reporte.json` y actualiza los fingerprints.

## Estructura al añadir un módulo o ejercicio

- Carpeta de herramienta en la raíz, con `README.md` propio y `.gitleaksignore`.
- Ejercicios `NN-tema/` en orden de dificultad, cada uno con su `README.md` (objetivo, requisitos, pasos numerados, salida esperada, preguntas).
- Material de apoyo solo en `fixtures/`, `scripts/`, `config/`. Soluciones en `solucion/`.
- Registra el módulo nuevo en la tabla "Índice de herramientas" del `README.md` raíz. Esa tabla es lo único que se toca en el README raíz (README.md:265).

Los archivos Python de `sonarqube/*/fixtures/src/` son **deliberadamente defectuosos** (bugs, vulnerabilidades, duplicación inyectados). No los "arregles": el ejercicio 03 mide el delta de issues antes/después.

## Los workflows no se ejecutan

Los `.github/workflows/*.yml` viven **dentro de las carpetas de ejercicio** (`gitleaks/05-ci-github-actions/`, `sonarqube/04-ci-github-actions/`), no en `.github/workflows/` de la raíz. Son material de estudio: copiarlos al repo de práctica del alumno es parte del ejercicio. Si los movieras a la raíz, CI empezaría a correr de verdad y fallaría por los secretos ficticios y por los fixtures con bugs.

## Fixtures de SonarQube: el scanner no corre los tests

El orden es obligatorio y es el punto que más se olvida: `pytest` debe terminar **antes** de `sonar-scanner`. El scanner solo lee un `coverage.xml` en formato Cobertura ya existente.

```bash
cd sonarqube/02-clean-as-you-code/fixtures
python3 -m pytest --cov=src/nuevo_codigo --cov-report=xml:coverage.xml
sonar-scanner -Dsonar.python.coverage.reportPaths=coverage.xml
```

`sonar-scanner` requiere Java 21+ (17 sin soporte). El token va en `SONAR_TOKEN`, nunca hardcodeado en `sonar-project.properties`.

## Git

Trabajo en ramas, nunca en `main`. Commits estilo Conventional Commits con el scope del módulo: `feat(gitleaks): ...`. El repo tiene un solo commit (`initial README`); `gitleaks/`, `sonarqube/` y `.gitignore` están sin trackear todavía.

## Entorno local verificado

Instalado: `gitleaks` 8.30.1, Docker, Python 3.8 (`python3`, no `python`).
Ausente: `sonar-scanner`, `pre-commit`, `git-filter-repo`, servidor SonarQube. Los ejercicios 04 (pre-commit), 06 (remediación) y los 4 de SonarQube requieren instalarlos; no asumas que un comando de los READMEs correrá tal cual.
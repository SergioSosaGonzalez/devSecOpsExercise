# Ejercicio 01 — Reconocimiento y primeros pasos

**Nivel:** 🟢 Básico · **Duración estimada:** 20 min

## 🎯 Objetivo

Verificar que Gitleaks está correctamente instalado, conocer su interfaz de ayuda y entender la estructura básica del repositorio de ejercicios.

## 📋 Requisitos previos

- Gitleaks instalado. Si aún no lo tienes, revisa la sección **3. Instalación** del [README principal](../README.md).
- Un repositorio Git inicializado en tu máquina.

---

## Pasos

### 1. Verifica tu instalación

```bash
gitleaks version
```

**Salida esperada:**

```
8.30.0
```

> Si obtienes `command not found` (o "'gitleaks' no se reconoce como comando" en Windows), vuelve a la sección de instalación y revisa el `PATH`.

### 2. Explora la ayuda general

```bash
gitleaks --help
```

Identifica en la salida:

- Los **subcomandos disponibles**: `completion`, `dir`, `git`, `help`, `stdin`, `version`
- Las **banderas globales** más útiles:
  - `-v, --verbose` → salida detallada
  - `--redact` → enmascara los secretos
  - `-c, --config` → archivo de configuración
  - `-f, --report-format` y `-r, --report-path` → reportes
  - `-b, --baseline-path` → baseline
  - `--exit-code` → código de salida cuando hay hallazgos

### 3. Explora la ayuda de cada modo de escaneo

Gitleaks tiene **tres modos** y cada uno tiene su propio conjunto de opciones:

```bash
gitleaks git --help      # escanea el historial de commits
gitleaks dir --help      # escanea archivos y directorios
gitleaks stdin --help    # escanea datos que llegan por la tubería
```

Presta atención a las diferencias:

| Modo | Fuente de los datos | ¿Detecta secretos en el historial? |
|---|---|---|
| `git` | Parches generados con `git log -p` | ✅ Sí |
| `dir` | Archivos del sistema de archivos | ❌ No |
| `stdin` | Flujo de entrada estándar | ❌ No |

### 4. Comprueba que estás dentro de un repositorio Git

```bash
cd /ruta/a/tu/repositorio
git rev-parse --is-inside-work-tree
```

Debe imprimir `true`. Si imprime `false` o da error, primero ejecuta `git init`.

### 5. Genera el autocompletado de tu shell

Gitleaks incluye autocompletado nativo. Esto es opcional, pero muy cómodo:

```bash
# Bash (agrega esto a ~/.bashrc)
source <(gitleaks completion bash)

# Zsh (agrega esto a ~/.zshrc)
source <(gitleaks completion zsh)

# Fish
gitleaks completion fish | source

# PowerShell (agrega a tu $PROFILE)
gitleaks completion powershell | Out-String | Invoke-Expression
```

Verifica que en tu terminal funcione `gitleaks <TAB>`.

---

## ✅ Comprobación final

Antes de pasar al siguiente ejercicio, confirma que puedes responder **sí** a todo esto:

- [ ] `gitleaks version` devuelve un número de versión
- [ ] `gitleaks --help` lista los subcomandos `git`, `dir` y `stdin`
- [ ] Sabes explicar la diferencia entre los tres modos de escaneo
- [ ] Tienes Gitleaks disponible dentro de un repositorio Git

---

## 🤔 Preguntas de reflexión

1. ¿Por qué existe un modo `dir` si `git` ya escanea todos los archivos del repositorio? ¿En qué situación real usarías `dir`?
2. Mira la bandera `--exit-code`. ¿Por qué es importante poder configurarla? ¿Qué pasaría en un pipeline si Gitleaks devolviera siempre `0`?
3. El modo `stdin` parece poco útil por sí solo. ¿En qué tipo de arquitectura de seguridad se integraría para cobrar sentido?

---

## ⏭️ Siguiente

[Ejercicio 02 — Escaneo básico →](../02-escaneo-basico/README.md)

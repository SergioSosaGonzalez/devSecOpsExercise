# 🕷️ ZAP (Zed Attack Proxy) — DAST para aplicaciones web

> **Categoría:** DAST (Dynamic Application Security Testing) · **Etapa del Shift Left:** Desarrollo/Integración Continua (CI) · **Licencia:** Apache License 2.0

## 1. ¿Qué es ZAP?

[ZAP](https://www.zaproxy.org/) (Zed Attack Proxy), actualmente **ZAP by Checkmarx**, es un escáner de seguridad de aplicaciones web de código abierto, gratuito y ampliamente utilizado. Actúa como proxy HTTP(S) entre navegador y aplicación, permitiendo inspeccionar, modificar y analizar el tráfico en tiempo real.

**Analogía útil:** ZAP es como un "detector de tráfico" que observa cómo habla tu aplicación web. Mientras SAST lee el código fuente (lo que escribes), **DAST prueba la aplicación en ejecución** (lo que realmente responde).

**¿Por qué importa en DevSecOps?**

- **Detecta vulnerabilidades en tiempo de ejecución** (configuraciones erróneas, problemas de sesión, headers de seguridad, etc.) que SAST no siempre ve.
- **Ideal para Shift Left**: con `zap-baseline.py` podemos obtener un primer diagnóstico rápido en CI sin realizar ataques activos.
- **Fácil de automatizar** y generar reportes accionables (HTML/Markdown/XML/JSON).
- **Sin coste de licencia** y con gran ecosistema de extensiones ([Marketplace](https://www.zaproxy.org/addons/)).

**Diagrama ASCII del flujo (DAST con ZAP):**

```text
Navegador/Cliente
  └─> Tráfico HTTP(S)
       └─> ZAP Proxy (Intercept/Spider/Passive Scan)
            └─> Aplicación Web (Target)
                 └─> Respuestas
                      └─> ZAP analiza (Passive/Active)
                           └─> Alertas + Reportes (HTML/MD/XML/JSON)
```

## 2. Características principales

| Característica | Explicación |
|---|---|
| **Proxy intercepting** | Permite inspeccionar y modificar peticiones/respuestas HTTP(S). |
| **Spidering** | Descubre automáticamente URLs (Traditional, AJAX, Client Spider). |
| **Passive Scanning** | Analiza tráfico sin modificarlo (no envía payloads de ataque). Seguro para entornos sensibles. |
| **Active Scanning** | Envía payloads para probar vulnerabilidades conocidas (ataques controlados). Requiere autorización explícita del objetivo. |
| **CLI Headless** | Scripts Python para CI/CD: `zap-baseline.py`, `zap-full-scan.py`, `zap-api-scan.py`. |
| **Reportes múltiples** | Genera HTML, Markdown (Wiki), XML y JSON listos para integrar. |
| **Tuning por reglas** | Configurable vía fichero `.conf` para marcar reglas como `INFO`, `IGNORE`, `WARN` o `FAIL`. |
| **Docker Ready** | Imágenes oficiales `ghcr.io/zaproxy/zaproxy` (stable, weekly, bare, etc.). |
| **Extensible** | Marketplace de add-ons para ampliar capacidades. |

### Limitaciones que debes conocer

> **Importante:** ZAP es una herramienta poderosa, pero tiene límites reales que debes tener en cuenta.

| Limitación | Explicación |
|---|---|
| **Requiere aplicación en ejecución** | A diferencia de SAST, **DAST necesita un target accesible** (URL/puerto). No analiza código fuente. |
| **Active Scan puede ser intrusivo** | El escaneo activo envía payloads. **Nunca** ejecutes `zap-full-scan.py` contra producción sin autorización escrita. |
| **Cobertura depende del descubrimiento** | Si el spider no descubre rutas (auth, JS complejo, formularios dinámicos), esas rutas no se escanean. Requiere tuning (contexto, autenticación). |
| **Falsos positivos/negativos** | Es esperable. El tuning (config de reglas) es parte imprescindible del flujo profesional. |
| **ZAP ya no es OWASP** | Desde agosto de 2023, ZAP dejó de ser proyecto OWASP ([más info](https://www.zaproxy.org/docs/nowaspzap/)). El nombre correcto es **ZAP by Checkmarx**. |
| **Requiere Java (modo Desktop/CLI local)** | Las versiones CLI locales usan ZAP Core (Java). Con **Docker** evitamos ese requisito local. |
| **Tiempo de ejecución** | Full scan puede ser largo (minutos-horas) dependiendo del tamaño de la app. Baseline es corto (por diseño). |

## 3. Instalación

ZAP puede ejecutarse de varias formas. En este curso se prioriza **Docker** (reproducible y no requiere Java local). También se incluyen otras opciones.

### Opción A: Docker (recomendada para CI y ejercicios)

Las imágenes oficiales están en [GHCR](https://github.com/zaproxy/zaproxy/pkgs/container/zaproxy):

```bash
docker pull ghcr.io/zaproxy/zaproxy:stable
```

Verificación:

```bash
docker run --rm ghcr.io/zaproxy/zaproxy:stable zap.sh -version
```

### Opción B: macOS

Con Homebrew (si disponible):

```bash
brew install --cask zap
```

O descarga desde [zaproxy.org/download](https://www.zaproxy.org/download/).

### Opción C: Linux

Descarga el `.tar.gz` desde [Descargas](https://www.zaproxy.org/download/) o usa paquetes de tu distro. Scripts: `zap.sh` (CLI/headless).

```bash
# Tras descomprimir
./zap.sh -version
```

### Opción D: Windows

Descarga instalador `.exe` desde [Descargas](https://www.zaproxy.org/download/). Usa `zap.bat` para CLI.

### ✅ Verificación de la instalación

```bash
# Con Docker (más fiable en entornos CI)
docker run --rm ghcr.io/zaproxy/zaproxy:stable zap-baseline.py -h 2>&1 | head -5
```

**Salida esperada:** Debe mostrar la ayuda de `zap-baseline.py` (Usage: zap-baseline.py ...).

## 4. Uso básico

ZAP CLI incluye 3 scripts principales (imágenes Docker):

| Script | Uso | Notas |
|---|---|---|
| [`zap-baseline.py`](https://www.zaproxy.org/docs/docker/baseline-scan/) | Escaneo **rápido, sin ataques activos** (passive + spider). | Ideal para CI, puertas de calidad ligeras, PRs. No intrusivo. |
| [`zap-full-scan.py`](https://www.zaproxy.org/docs/docker/full-scan/) | Escaneo **completo** (passive + spider + active). | Más profundo. **Solo con autorización explícita** del objetivo. |
| [`zap-api-scan.py`](https://www.zaproxy.org/docs/docker/api-scan/) | Escaneo orientado a APIs (OpenAPI/Swagger, SOAP). | Útil cuando target es API REST. |

**Parámetros comunes (baseline/full):**

| Opción | Significado |
|---|---|
| `-t <target>` | URL objetivo (incluye protocolo: `https://...`) |
| `-r <html>` | Reporte HTML |
| `-w <md>` | Reporte Markdown (Wiki) |
| `-x <xml>` | Reporte XML |
| `-J <json>` | Reporte JSON (documento completo) |
| `-c <conf>` | Fichero de config para INFO/IGNORE/FAIL reglas |
| `-g <gen>` | Genera config por defecto (`all rules WARN`) |
| `-j` | Usa spider moderno (AJAX/Client) además del tradicional |
| `-l <level>` | Nivel mínimo a mostrar: `PASS`, `IGNORE`, `INFO`, `WARN`, `FAIL` |
| `-s` | Salida corta (oculta PASS y URLs de ejemplo) |
| `-I` | No devuelve fallo por warnings (útil en CI exploratorio) |
| `-a` | Incluye reglas alpha (passive/active según script) |

## 5. Uso avanzado

### 5.1 Servir fixtures localmente (reproducible)

Para ejercicios sin depender de internet, servimos HTML estático local:

```bash
# Desde carpeta fixtures
python3 -m http.server 8080
```

Target: `http://localhost:8080/`

### 5.2 Generar configuración de tuning

```bash
docker run --rm -v "$PWD":/zap/wrk/:rw \
  ghcr.io/zaproxy/zaproxy:stable \
  zap-baseline.py -t http://example.com -g /zap/wrk/zap-baseline.conf
```

Esto genera un `.conf` donde **todas las reglas** están en `WARN`. Puedes cambiar a `INFO`, `IGNORE` o `FAIL` por regla (ID de alerta). Esto es clave para reducir ruido.

### 5.3 Ejecutar con config y múltiples reportes

```bash
docker run --rm -v "$PWD":/zap/wrk/:rw \
  ghcr.io/zaproxy/zaproxy:stable \
  zap-baseline.py \
    -t http://host.docker.internal:8080 \
    -c /zap/wrk/zap-baseline-config.conf \
    -r /zap/wrk/report.html \
    -w /zap/wrk/report.md \
    -J /zap/wrk/report.json \
    -s
```

> En macOS/Windows con Docker Desktop, usa `host.docker.internal` para acceder al host. En Linux con Docker nativo, puedes usar `--network host` o `172.17.0.1`.

### 5.4 Diferencia Baseline vs Full (importante)

- **Baseline (`zap-baseline.py`)**: ejecuta spider + **passive scanning**. **No realiza ataques activos**. Ideal para integración continua y para primeras verificaciones. Menor riesgo, menor tiempo.
- **Full (`zap-full-scan.py`)**: añade **active scanning**. Detecta más vulnerabilidades, pero es **intrusivo**. Requiere **autorización explícita** del propietario del sistema objetivo.

### 5.5 Códigos de salida

ZAP CLI devuelve códigos de salida útiles en CI:

| Código | Significado |
|---|---|
| `0` | Sin alertas que superen umbral (o todas IGNORE/INFO) |
| `1` | Se encontraron alertas con nivel `FAIL` (según config) |
| `2` | Error de uso/comando |
| Otros | Errores de ejecución/ZAP |

## 6. Códigos de salida y troubleshooting

| Problema | Causa probable | Solución |
|---|---|
| `zap-baseline.py: command not found` (local) | ZAP no está en PATH o usas Java directo | Usa Docker (`ghcr.io/zaproxy/zaproxy:stable`) o ejecuta `zap.sh` desde ruta correcta. |
| Contenedor no accede a `localhost:8080` | Docker aislado de red host | Usa `http://host.docker.internal:8080` (macOS/Windows Docker Desktop) o `--network host`/`172.17.0.1` (Linux nativo). |
| "ZAP failed to start" / timeout | Puerto ocupado o recursos limitados | Aumenta timeout (`-T <mins>`) o cierra otros procesos. Revisa logs con `-d` (debug). |
| Spider no descubre rutas | Páginas dinámicas (JS), formularios con auth | Añade `-j` (modern spider/AJAX) o define `context_file` (`-n`) y autenticación (`-U`). |
| Demasiadas alertas (ruido) | Reglas genéricas contra contenido estático | Usa `-c <config.conf>` para pasar reglas a `IGNORE/INFO`. Genera con `-g`. |
| Reporte no se escribe | Permisos/ruta montaje volumen | Monta volumen con `-v "$PWD":/zap/wrk/:rw` y escribe en `/zap/wrk/`. |
| Escaneo lento | Full scan contra app grande | Limita con `-m` (minutos spider) o usa baseline primero. Optimiza scope (exclusiones). |

## 7. Qué hacer cuando ZAP encuentra alertas

ZAP clasifica alertas por **riesgo** (Low/Medium/High/Informational) y **confianza**. El fichero de config permite decidir umbral por regla:

1. **Leer y entender**: Revisa reporte HTML (más visual) o MD/JSON. Cada alerta incluye URL afectada, evidencia, solución recomendada.
2. **Verificar si es falso positivo**: No todas las alertas son explotables. Valida contexto (entorno de pruebas vs real, contenido estático vs dinámico).
3. **Clasificar con tuning**: Si es ruido conocido y aceptado (documentado), márcalo `IGNORE` con **justificación** en config/comentarios. Si requiere corrección, márcalo `FAIL` para bloquear CI.
4. **Corregir en origen**: Lo ideal: mitigar en aplicación (headers de seguridad, CSP, etc.) y volver a escanear.
5. **Documentar criterio**: En equipos, el `.conf` de tuning vive en repo y refleja **decisión de riesgo aceptado**.

> **Regla de oro:** Nunca ignores alertas sin entender por qué. El tuning profesional se basa en **criterio justificado**, no en silenciar.

## 8. Ejercicios de esta carpeta

La tabla de ejercicios muestra el recorrido de menor a mayor dificultad.

| Ejercicio | Nivel | Tema | Duración estimada |
|---|---|---|---|
| [01 — Introducción y verificación](./01-introduccion-y-verificacion/README.md) | 🟢 Básico | Qué es ZAP, CLI, Docker, primer escaneo contra fixture local | 15–20 min |
| [02 — Escaneo básico y interpretación](./02-escaneo-basico-y-interpretacion/README.md) | 🟡 Intermedio | Passive vs Active, spider, reportes, interpretación de alertas | 20–30 min |
| [03 — Automatización y tuning (CI)](./03-automatizacion-y-tuning/README.md) | 🔴 Avanzado | Config de reglas (INFO/IGNORE/FAIL), reportes múltiples, criterios de fallo en CI | 20–30 min |

### 🧪 Prueba de humo del curso

Ejecuta esto desde la raíz del repo. Deberías obtener **7 hallazgos** (alertas WARN-NEW) contra los fixtures estáticos de este módulo.

> **Nota:** En este entorno (macOS + Docker Desktop), usa `host.docker.internal` para acceder al servidor local desde el contenedor. El conteo 7 es el resultado de `zap-baseline.py` contra `01-introduccion-y-verificacion/fixtures` tal como está configurado.

```bash
# 1. Levantar servidor HTTP local con fixtures del ejercicio 01 (background)
cd owasp-zap/01-introduccion-y-verificacion/fixtures && python3 -m http.server 18080 >/tmp/zap-fixtures.log 2>&1 &
ZAP_FIX_PID=$!
sleep 1

# 2. Ejecutar zap-baseline.py vía Docker contra host.docker.internal:18080
docker run --rm \
  ghcr.io/zaproxy/zaproxy:stable \
  zap-baseline.py -t http://host.docker.internal:18080 -s 2>&1 | tail -5

# 3. Limpiar servidor
kill $ZAP_FIX_PID 2>/dev/null; wait $ZAP_FIX_PID 2>/dev/null
```

**Conteo esperado (verificado):** `7` alertas `WARN-NEW`, `0` `FAIL-NEW`. El script `zap-baseline.py` finaliza con código 0 para este target estático.

## 9. Referencias

- [ZAP - Sitio oficial](https://www.zaproxy.org/)
- [ZAP Docs - Baseline Scan (Docker)](https://www.zaproxy.org/docs/docker/baseline-scan/)
- [ZAP Docs - Full Scan (Docker)](https://www.zaproxy.org/docs/docker/full-scan/)
- [ZAP Docs - API Scan (Docker)](https://www.zaproxy.org/docs/docker/api-scan/)
- [ZAP - Command Line / CLI](https://www.zaproxy.org/docs/desktop/cmdline/)
- [ZAP - N⛔WASP ZAP (contexto de salida de OWASP)](https://www.zaproxy.org/docs/nowaspzap/)
- [ZAP Marketplace (Add-ons)](https://www.zaproxy.org/addons/)
- [OWASP DAST Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Dynamic_Application_Security_Testing_Cheat_Sheet.html)

## 10. Glosario rápido

| Término | Definición |
|---|---|
| **DAST** | Dynamic Application Security Testing. Analiza aplicación en ejecución. |
| **SAST** | Static Application Security Testing. Analiza código fuente. |
| **Passive Scan** | Escaneo sin enviar payloads (no intrusivo). Analiza tráfico observado. |
| **Active Scan** | Envía payloads para probar vulnerabilidades (potencialmente intrusivo). Requiere autorización. |
| **Spider** | Descubrimiento automático de URLs (crawling). |
| **Baseline** | Escaneo ligero (passive+spider), sin ataques activos. Ideal CI. |
| **Full Scan** | Passive+Spider+Active. Cobertura máxima, más tiempo. |
| **Tuning** | Ajuste de reglas (WARN/FAIL/IGNORE/INFO) para reducir falsos positivos. |
| **Context** | Alcance/definición de qué URLs forman parte del objetivo a escanear. |

# Ejercicio 01 — Introducción y verificación

**Nivel:** 🟢 Básico · **Duración estimada:** 15–20 min

## 🎯 Objetivo

- Entender qué es ZAP, DAST vs SAST y cuándo usar baseline vs full scan.
- Verificar que Docker + imagen `ghcr.io/zaproxy/zaproxy:stable` funcionan correctamente.
- Ejecutar tu primer `zap-baseline.py` contra un fixture local (servido con `python3 -m http.server`).
- Identificar salida esperada, código de salida y diferencia entre passive/active scan.

## 📋 Requisitos previos

- Tener Docker instalado y funcionando (`docker --version`).
- Tener Python 3 disponible (`python3 --version`).
- Haber leído la introducción del módulo [owasp-zap/README.md](../README.md).
- Acceso a red local (localhost).

> **Por qué esto importa:** Antes de automatizar en CI, debes validar que el entorno funciona y que comprendes la distinción entre escaneo pasivo (seguro) y activo (intrusivo).

## Pasos

### 1. Verifica Docker e imagen de ZAP

Ejecuta:

```bash
docker run --rm ghcr.io/zaproxy/zaproxy:stable zap.sh -version
```

**Salida esperada:** Versión de ZAP (ej. `ZAP 2.x.x`).

### 2. Comprueba ayuda de zap-baseline.py

```bash
docker run --rm ghcr.io/zaproxy/zaproxy:stable zap-baseline.py -h 2>&1 | head -8
```

**Salida esperada:** Muestra `Usage: zap-baseline.py -t <target> [options]` y lista de opciones.

> **Nota:** Los scripts CLI de ZAP vienen incluidos en la imagen Docker oficial.

### 3. Sirve los fixtures localmente

Desde el directorio de este ejercicio:

```bash
cd owasp-zap/01-introduccion-y-verificacion/fixtures
python3 -m http.server 18081 >/tmp/zap-01.log 2>&1 &
echo $! > /tmp/zap-01.pid
sleep 1
curl -s http://localhost:18081/ | head -2
```

**Salida esperada:** Debe mostrar las primeras líneas del `index.html` (título o contenido HTML).

> **Por qué esto importa:** Usar fixtures locales hace el ejercicio reproducible sin depender de sitios externos.

### 4. Ejecuta zap-baseline.py contra el fixture

```bash
docker run --rm \
  ghcr.io/zaproxy/zaproxy:stable \
  zap-baseline.py -t http://host.docker.internal:18081 -s
```

**Salida esperada:** Mensajes de ZAP indicando inicio, spider, passive scan y resumen final. Con estos fixtures, verás alertas según el entorno (en macOS/Docker Desktop verás WARNs de headers).

> **Importante:** En macOS/Windows con Docker Desktop usa `host.docker.internal`. En Linux nativo puedes usar `--network host` o `172.17.0.1`.

### 5. Para el servidor local

```bash
kill $(cat /tmp/zap-01.pid) 2>/dev/null; wait $(cat /tmp/zap-01.pid) 2>/dev/null; rm /tmp/zap-01.pid /tmp/zap-01.log 2>/dev/null
```

**Salida esperada:** Sin errores.

## ✅ Comprobación final

- [ ] Docker funciona y muestra versión de ZAP.
- [ ] `zap-baseline.py -h` muestra ayuda correcta.
- [ ] Servidor local responde con HTML del fixture.
- [ ] `zap-baseline.py` completa sin error contra `http://localhost:18081`.
- [ ] Comprendes diferencia entre **Passive Scan** (sin ataques) vs **Active Scan** (con payloads).
- [ ] Sabes por qué **baseline** es apto para CI y **full scan** requiere autorización explícita.

## 🤔 Preguntas de reflexión

1. **DAST vs SAST:** ¿En qué caso concreto detectarías un problema con DAST que difícilmente verías con SAST? Justifica con ejemplo realista.
2. **Baseline vs Full:** Si tienes que integrar ZAP en un pipeline de Pull Request, ¿por qué elegirías `zap-baseline.py` en lugar de `zap-full-scan.py`? ¿Qué trade-off aceptas (cobertura vs seguridad vs velocidad)?
3. **Passive vs Active:** ¿Por qué el passive scanning se considera "más seguro" para entornos no autorizados? ¿En qué escenarios **sí** estaría justificado ejecutar active scan?

## ⏭️ Siguiente

[Ejercicio 02 — Escaneo básico y interpretación →](../02-escaneo-basico-y-interpretacion/README.md)

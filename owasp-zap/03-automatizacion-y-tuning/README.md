# Ejercicio 03 — Automatización y tuning (CI)

**Nivel:** 🔴 Avanzado · **Duración estimada:** 20–30 min

## 🎯 Objetivo

- Generar un fichero de configuración por defecto (`-g`) para hacer tuning de reglas.
- Clasificar reglas (INFO/WARN/FAIL/IGNORE) con criterio justificado.
- Ejecutar `zap-baseline.py` con config y múltiples reportes.
- Entender criterios de fallo en CI (códigos de salida) y cuándo usar `-I`.
- Aplicar buenas prácticas: tuning documentado, scope controlado, evitar active scan sin autorización.

## 📋 Requisitos previos

- [Ejercicio 02 completado](../02-escaneo-basico-y-interpretacion/README.md)
- Docker funcionando.
- Python 3 para servir HTTP.

> **Por qué esto importa:** Automatizar sin **tuning** genera ruido y hace que los equipos ignoren alertas. Un `.conf` versionado refleja **decisiones de riesgo aceptado** y permite usar umbrales de fallo coherentes en CI.

## Pasos

### 1. Sirve fixtures localmente

```bash
cd owasp-zap/03-automatizacion-y-tuning/fixtures
python3 -m http.server 18083 >/tmp/zap-03.log 2>&1 &
echo $! > /tmp/zap-03.pid
sleep 1
curl -s http://localhost:18083/ | head -1
```

**Salida esperada:** Muestra título de `index.html`.

### 2. Genera configuración por defecto (-g)

Generamos `zap-baseline.conf` en la carpeta actual (fixtures):

```bash
docker run --rm -v "$PWD":/zap/wrk/:rw \
  ghcr.io/zaproxy/zaproxy:stable \
  zap-baseline.py -t http://example.com -g /zap/wrk/zap-baseline.conf 2>&1 | tail -2
```

**Salida esperada:** Confirma generación del fichero `.conf`.

Comprueba su contenido:

```bash
head -20 zap-baseline.conf
```

**Salida esperada:** Muestra comentarios y líneas tipo `<ruleid>=WARN` (todas las reglas en WARN por defecto).

> **Por qué esto importa:** Partimos de base consistente. Ajustamos **por regla** con justificación, nunca a nivel global sin entender.

### 3. Edita config con criterio de tuning (didáctico)

Abre `zap-baseline.conf` y añade comentarios explicativos + ajustes razonados. Para este **fixture estático de laboratorio**, un enfoque didáctico es documentar intención (no silenciar ciegamente).

Ejemplo de edición (comentarios útiles):

```bash
cat >> zap-baseline.conf << 'EOF'

# --- Tuning didáctico (justificado) ---
# Objetivo: fixture HTML estático de laboratorio. Ajustes razonados para reducir ruido.
# NOTA: Estas decisiones son específicas de ENTORNO DE PRUEBAS y deben revisarse por regla.
EOF
```

> **Regla de oro:** Cada cambio a `IGNORE` debe tener justificación escrita. En este ejercicio **no es obligatorio** cambiar niveles, pero **sí es obligatorio** entender el proceso.

### 4. Ejecuta baseline con config + reportes múltiples

Usamos volumen para guardar reportes fuera del contenedor:

```bash
mkdir -p ../out
docker run --rm -v "$PWD":/zap/wrk/:rw -v "$PWD/../out":/zap/reports/:rw \
  ghcr.io/zaproxy/zaproxy:stable \
  zap-baseline.py \
    -t http://host.docker.internal:18083 \
    -c /zap/wrk/zap-baseline-config.conf \
    -r /zap/reports/report-03.html \
    -w /zap/reports/report-03.md \
    -J /zap/reports/report-03.json \
    -s
```

**Salida esperada:** Ejecución completa. Comprueba reportes generados:

```bash
ls -la ../out/
```

**Salida esperada:** `report-03.html`, `report-03.md`, `report-03.json` (y opcionalmente reportes ejercicio 02).

### 5. Comprueba códigos de salida en CI (práctica)

Ejecuta de nuevo y captura código de salida:

```bash
docker run --rm -v "$PWD":/zap/wrk/:rw \
  ghcr.io/zaproxy/zaproxy:stable \
  zap-baseline.py -t http://host.docker.internal:18083 -c /zap/wrk/zap-baseline-config.conf -s >/tmp/zap-03.out 2>&1; echo "CODE:$?"
```

**Salida esperada:** `CODE:0` (sin alertas FAIL/WARN que superen umbral). Explica qué significa cada código:

| Código | Significado |
|---|---|
| `0` | OK (sin FAILs según config) |
| `1` | Hay alertas con nivel `FAIL` |
| `2` | Error de uso/parámetros |

> **Nota útil:** Si quieres que **warnings no rompan CI** (fase exploratoria), puedes usar `-I` (no devuelve fallo por warnings). Úsalo con criterio, no para esconder problemas.

### 6. Para el servidor local

```bash
kill $(cat /tmp/zap-03.pid) 2>/dev/null; wait $(cat /tmp/zap-03.pid) 2>/dev/null; rm /tmp/zap-03.pid /tmp/zap-03.log 2>/dev/null
```

**Salida esperada:** Sin errores.

## ✅ Comprobación final

- [ ] Generaste `zap-baseline.conf` correctamente con `-g`.
- [ ] Comprendes formato `<ruleid>=<level>` (IGNORE/INFO/WARN/FAIL).
- [ ] Ejecutaste baseline con `-c` y generaste reportes HTML/MD/JSON.
- [ ] Interpretaste código de salida (0/1/2) y cuándo usar `-I`.
- [ ] Has justificado conceptualmente **al menos un ajuste** de tuning (criterio, no acción ciega).
- [ ] Entiendes que el `.conf` de tuning debe **versionarse** y **documentarse** en equipo.

## 🤔 Preguntas de reflexión

1. **Tuning profesional:** En un proyecto real con muchas alertas, ¿cómo evitarías el "tuning por fatiga" (ignorar todo)? ¿Qué proceso mínimo exigirías para aceptar un `IGNORE`?
2. **CI Gate:** Quieres que el pipeline **falle** si aparecen nuevas vulnerabilidades High/Medium. ¿Qué estrategia usarías con baseline + config? ¿Dónde marcarías `FAIL` vs `WARN`?
3. **Seguridad vs pragmatismo:** ¿Por qué el curso insiste en **no ejecutar active scan sin autorización explícita**? ¿Qué riesgos legales/técnicos hay (más allá del técnico)?

## ⏮️ Anterior

[← Ejercicio 02 — Escaneo básico y interpretación](../02-escaneo-basico-y-interpretacion/README.md)

**Fin de los ejercicios de este módulo.**

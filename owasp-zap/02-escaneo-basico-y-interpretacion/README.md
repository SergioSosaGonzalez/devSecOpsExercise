# Ejercicio 02 — Escaneo básico y interpretación

**Nivel:** 🟡 Intermedio · **Duración estimada:** 20–30 min

## 🎯 Objetivo

- Servir fixtures con múltiples páginas (index + about + formulario).
- Ejecutar `zap-baseline.py` observando spidering, passive scan y resumen.
- Generar reportes en distintos formatos (HTML, Markdown, JSON) montando volumen.
- Aprender a interpretar alertas: riesgo, confianza, evidencia, solución recomendada.
- Entender por qué el tuning existe (falsos positivos) sin "silenciar" sin criterio.

## 📋 Requisitos previos

- [Ejercicio 01 completado](../01-introduccion-y-verificacion/README.md)
- Docker funcionando.
- Python 3 para servir HTTP local.

> **Por qué esto importa:** Saber **leer** un reporte de ZAP es tan importante como saber ejecutarlo. Un buen analista distingue ruido aceptable de hallazgos reales y documenta su criterio.

## Pasos

### 1. Sirve fixtures con varias páginas

Desde este ejercicio:

```bash
cd owasp-zap/02-escaneo-basico-y-interpretacion/fixtures
python3 -m http.server 18082 >/tmp/zap-02.log 2>&1 &
echo $! > /tmp/zap-02.pid
sleep 1
curl -s http://localhost:18082/ && echo "---" && curl -s http://localhost:18082/about.html | head -1
```

**Salida esperada:** Muestra contenido de `index.html` y primera línea de `about.html` (incluye formulario).

> **Observa:** Ahora hay 2 páginas enlazadas. El spider debería descubrir `about.html` desde `index.html`.

### 2. Ejecuta baseline con salida corta (-s) y observa descubrimiento

```bash
docker run --rm \
  ghcr.io/zaproxy/zaproxy:stable \
  zap-baseline.py -t http://host.docker.internal:18082 -s
```

**Salida esperada:** Verás fases:
- `Spidering target` / URLs descubiertas
- `Scanning target` (Passive Scan)
- `WARN-NEW`, `PASS`, resumen final y código de salida

**Qué buscar:**
- ¿Descubrió `about.html`?
- ¿Aparecen alertas `WARN`/`FAIL`? (Con este fixture estático, suele ser 0 o muy bajo)

> **Por qué esto importa:** La **cobertura** depende del descubrimiento. Si el spider no encuentra rutas, el escaneo no las cubre.

### 3. Genera reportes (HTML, MD, JSON) montando volumen

Creamos carpeta `out/` para guardar reportes:

```bash
mkdir -p out
docker run --rm -v "$PWD/out:/zap/wrk/:rw" \
  ghcr.io/zaproxy/zaproxy:stable \
  zap-baseline.py \
    -t http://host.docker.internal:18082 \
    -r /zap/wrk/report.html \
    -w /zap/wrk/report.md \
    -J /zap/wrk/report.json \
    -s
```

**Salida esperada:** El comando termina correctamente. Deben aparecer 3 ficheros en `out/`:

```bash
ls -la out/
```

**Salida esperada:** `report.html`, `report.md`, `report.json`

### 4. Inspecciona los reportes

Abre/lee cada uno para entender estructura:

```bash
head -30 out/report.md
echo "---JSON HEAD---"
head -c 200 out/report.json; echo "..."
```

**Salida esperada:** `report.md` muestra resumen + alertas (si existen). `report.json` contiene estructura con `alerts`, `site`, `spider` etc.

> **Por qué esto importa:** HTML es visual para revisión; JSON ideal para parseo/CI; MD útil para PRs. Saber leer evidencia (URL, parámetro, evidencia HTTP, solución) es clave.

### 5. Interpreta: ¿ruido o hallazgo real?

Responde mentalmente estas preguntas al revisar reportes:
- ¿Qué regla (alerta) aparece? ¿Riesgo (Low/Med/High/Informational)?
- ¿Es aplicable a **este fixture estático** (HTML puro) o parece genérico?
- ¿Requiere cambio en código/app o es configuración de servidor?
- ¿Sería razonable marcarlo `IGNORE` con justificación, o `FAIL`?

> **Regla práctica:** Un falso positivo aceptado debe estar **documentado** (comentario en config + razón). Nunca "silenciar por comodidad".

### 6. Para el servidor local

```bash
kill $(cat /tmp/zap-02.pid) 2>/dev/null; wait $(cat /tmp/zap-02.pid) 2>/dev/null; rm /tmp/zap-02.pid /tmp/zap-02.log 2>/dev/null
```

**Salida esperada:** Sin errores.

## ✅ Comprobación final

- [ ] El spider descubrió `about.html` desde `index.html`.
- [ ] Generaste `report.html`, `report.md`, `report.json` correctamente.
- [ ] Has leído al menos una alerta completa (evidencia + solución recomendada).
- [ ] Entiendes la diferencia entre riesgo y confianza.
- [ ] Has identificado criterio para decidir IGNORE/INFO/WARN/FAIL.
- [ ] Comprendes por qué **montar volumen** (`-v`) es necesario para guardar reportes fuera del contenedor.

## 🤔 Preguntas de reflexión

1. **Descubrimiento:** Si `about.html` **no** se hubiese descubierto, ¿qué opciones reales tendrías para mejorar cobertura sin ejecutar active scan? (Piensa en spider moderno, contexto, o listar rutas conocidas).
2. **Interpretación crítica:** Imagina que ZAP reporta "X-Frame-Options Header Not Set" (Low/Informational) contra un **HTML estático puro** servido en laboratorio. ¿Es un hallazgo accionable? ¿Por qué sí/no? ¿Qué justificación usarías para IGNORE?
3. **Falsos positivos vs riesgo aceptado:** Tu equipo quiere pasar CI "limpio". ¿Cuándo es **profesionalmente correcto** añadir una regla a `IGNORE` en config? ¿Cuándo es **incorrecto** hacerlo?

## ⏮️ Anterior / ⏭️ Siguiente

[← Ejercicio 01 — Introducción y verificación](../01-introduccion-y-verificacion/README.md) | [Ejercicio 03 — Automatización y tuning (CI) →](../03-automatizacion-y-tuning/README.md)

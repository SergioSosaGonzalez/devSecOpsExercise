# Ejercicio 02 — Análisis de resultados con Trivy

**Nivel:** 🟡 Intermedio · **Duración estimada:** 25 min

## 🎯 Objetivo

Aprender a interpretar los hallazgos de Trivy, filtrar por tipo y severidad, generar salida JSON para análisis, y usar `.trivyignore` de forma responsable.

## 📋 Requisitos previos

- [Ejercicio 01 completado](../01-escaneo-basico/README.md)
- Trivy instalado y funcionando

---

## Pasos

### 1. Navegar al directorio del ejercicio

```bash
cd trivy/02-analisis-resultados
```

### 2. Inspeccionar los fixtures

Ver qué vamos a escanear.

```bash
cat fixtures/package.json
cat fixtures/.env
```

**Salida esperada:** Un `package.json` con versiones antiguas (lodash 4.17.20, minimist 0.2.1, express 4.17.1) y un `.env` con secretos ficticios.

> 💡 **¿Por qué esto importa?** Combinar SCA (vulnerabilidades en dependencias) + secretos nos muestra la cobertura integral de Trivy.

### 3. Escaneo completo con formato tabla

```bash
trivy fs .
```

**Salida esperada:** Verás hallazgos de tipo **VULN** (vulnerabilidades en dependencias) y **SECRET** (en `.env`). Observa Target, Library/Rule, Severity, CVE/ID.

> 💡 **¿Por qué esto importa?** Aprender a leer la tabla correctamente es fundamental para priorizar correcciones.

### 4. Separar por tipo de escaneo

Escanear solo vulnerabilidades.

```bash
trivy fs --scanners vuln .
```

Escanear solo secretos.

```bash
trivy fs --scanners secret .
```

**Salida esperada:** Diferentes conjuntos de hallazgos. Esto ayuda a asignar el hallazgo al equipo correcto.

> 💡 **¿Por qué esto importa?** Seguridad no es monolítico: vulns suelen ir a desarrollo, secretos requieren rotación inmediata.

### 5. Filtrar por severidad crítica/alta

```bash
trivy fs --scanners vuln --severity HIGH,CRITICAL .
```

**Salida esperada:** Solo vulnerabilidades HIGH/CRITICAL. En proyectos con miles de deps, esto evita la fatiga de alertas.

> 💡 **¿Por qué esto importa?** Priorización basada en riesgo: arreglar CRITICAL primero, documentar/planificar el resto.

### 6. Generar reporte JSON para análisis

Útil para CI, reporting o procesar programáticamente.

```bash
trivy fs --format json -o reporte.json .
```

**Comprobar el reporte generado:**

```bash
head -30 reporte.json
```

**Salida esperada:** JSON con estructura que incluye `Results`, `Vulnerabilities`, etc.

> 💡 **¿Por qué esto importa?** Los formatos estructurados permiten integrar Trivy con otras herramientas.

### 7. Crear .trivyignore para ignorar un hallazgo justificado

```bash
cat > .trivyignore << 'EOF'
# Justificación pedagógica: Ejercicio 02 - enfocarnos en HIGH/CRITICAL
# LOW/MEDIUM documentados para aprendizaje
EOF
```

> 💡 **¿Por qué esto importa?** `.trivyignore` existe para excepciones razonadas y documentadas.

---

## ✅ Comprobación final

- [ ] Has identificado hallazgos VULN y SECRET en el mismo scan
- [ ] Has filtrado correctamente por `--scanners` y `--severity`
- [ ] Has generado `reporte.json` con `--format json`
- [ ] Has creado un `.trivyignore` con justificación

---

## 🤔 Preguntas de reflexión

1. **¿Qué ventajas tiene JSON frente a tabla para CI/CD?**

2. **¿Cuándo NO debería usarse `.trivyignore`?** Da al menos 2 ejemplos.

3. **Tienes un CRITICAL sin parche. ¿Qué mitigaciones compensatorias propondrías?**

---

## ⏭️ Siguiente

[Ejercicio 03 — Integración en CI con GitHub Actions →](../03-ci-github-actions/README.md)

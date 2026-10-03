# Ejercicio 01 — Escaneo básico con Trivy

**Nivel:** 🟢 Básico · **Duración estimada:** 15 min

## 🎯 Objetivo

Aprender a ejecutar Trivy en modo filesystem (`fs`) y comprender su salida básica, detectando secretos y entendiendo los diferentes tipos de hallazgos.

## 📋 Requisitos previos

- [Trivy instalado](../../trivy/README.md#3-instalación) (`trivy --version` funciona)
- Conocimientos básicos de línea de comandos

---

## Pasos

### 1. Navegar al directorio del ejercicio

```bash
cd trivy/01-escaneo-basico
```

### 2. Inspeccionar los fixtures

Observa qué contiene el archivo de ejemplo.

```bash
cat fixtures/app.js
```

**Salida esperada:** Verás credenciales ficticias (AWS, GitHub, Stripe). Estos son **intencionales** para que Trivy los detecte.

> 💡 **¿Por qué esto importa?** Practicar con datos ficticios nos permite aprender a detectar secretos sin riesgo de exponer credenciales reales.

### 3. Ejecutar Trivy en modo filesystem (escaneo básico)

Ejecuta Trivy sobre el directorio actual. Por defecto detecta vulnerabilidades y secretos.

```bash
trivy fs .
```

**Salida esperada:** Trivy mostrará una tabla con hallazgos encontrados (SECRETOS principalmente en este fixture). Verás columnas como: Type, Target, Rule ID, Secret, Severity, Title.

> 💡 **¿Por qué esto importa?** El primer escaneo nos da una visión general de los problemas de seguridad en nuestro código.

### 4. Escanear únicamente secretos

A veces queremos centrarnos solo en secretos expuestos.

```bash
trivy fs --scanners secret .
```

**Salida esperada:** Solo aparecerán hallazgos de tipo SECRET. Esto es más limpio cuando buscamos credenciales filtradas.

> 💡 **¿Por qué esto importa?** Filtrar por scanner nos ayuda a reducir ruido y centrarnos en un tipo concreto de riesgo.

### 5. Filtrar por severidad

Enfócate en lo más crítico.

```bash
trivy fs --scanners secret --severity HIGH,CRITICAL .
```

**Salida esperada:** En este caso, los secretos suelen reportarse con severidad relevante. Observa cómo el filtro reduce la salida.

> 💡 **¿Por qué esto importa?** En proyectos reales hay muchos hallazgos; priorizar por severidad es clave para actuar eficientemente.

---

## ✅ Comprobación final

- [ ] Has ejecutado `trivy fs .` y has visto hallazgos
- [ ] Has identificado al menos 2-3 secretos detectados (AWS, GitHub, Stripe)
- [ ] Has probado `--scanners secret` para filtrar
- [ ] Has probado el filtro `--severity`

---

## 🤔 Preguntas de reflexión

1. **¿Qué tipos de hallazgos detecta Trivy por defecto en `trivy fs .`?** ¿Por qué crees que es útil este comportamiento por defecto?

2. **En un proyecto real con `node_modules`, `dist`, `.git`, ¿por qué tendría sentido añadir `--skip-dirs` o `--skip-files`?** ¿Qué trade-off existe (seguridad vs velocidad)?

3. **Trivy marca cadenas que "parecen" secretos. Esto puede generar falsos positivos. ¿Cuándo estaría justificado ignorar un hallazgo con `.trivyignore` vs. corregirlo realmente?**

---

## ⏭️ Siguiente

[Ejercicio 02 — Análisis de resultados →](../02-analisis-resultados/README.md)

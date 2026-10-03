# Ejercicio 02 — Clean as You Code

**Nivel:** 🟡 Intermedio · **Duración estimada:** 60 min

## 🎯 Objetivo

Aprender la metodología central de SonarQube: **no intentar arreglar la deuda técnica heredada, sino congelarla y garantizar que el código nuevo no la aumente**. Configurar Quality Profiles, Quality Gates y la definición de New Code, y llevar un Quality Gate de rojo a verde.

## 📋 Requisitos previos

- [Ejercicio 01 completado](../01-instalacion-primer-analisis/README.md)
- Un proyecto de prueba con **historial de versiones** (lo construiremos aquí)

---

## 🧠 El problema que resuelve Clean as You Code

```
  Situación real de una organización             El enfoque que NO funciona
  ────────────────────────────────────            ─────────────────────────────
  Overall Code: 4.812 issues                     "Hay 4.812 issues. Arregladlos."
  Reliability: D                                 El equipo se bloquea.
  Security: C                                   El coste es inabordable.
  Coverage: 12%                                 Nadie empieza. El projeto no avanza.
  Duplications: 31%                              La deuda técnica sigue igual 6 meses
                                                 después, solo que ahora hay críticas.

  El enfoque que SÍ funciona (Clean as You Code)
  ───────────────────────────────────────────────
  Overall Code: 4.812 issues      → se ACEPTA y se documenta
  New Code:     0 issues          → se EXIGE
  Coverage:     82% (solo nuevo)  → se EXIGE
  Duplications: 2% (solo nuevo)   → se EXIGE

  Resultado: cada sprint la deuda técnica baja. Y nadie pierde weeks.
```

---

## 📦 Material de trabajo

```
fixtures/
├── src/
│   ├── legacy.py        ← deuda técnica heredada (no la toques)
│   └── nuevo_codigo.py  ← código nuevo con errores que TÚ vas a arreglar
└── tests/
    └── test_nuevo_codigo.py
```

---

## Pasos

### 1. Analiza el estado inicial

```bash
cd fixtures/
export SONAR_HOST_URL=http://localhost:9000
export SONAR_TOKEN=squ_TU_TOKEN_AQUI

sonar-scanner
```

Abre el proyecto y anota el estado de **Overall Code** (casi seguro: todo rojo y ❌).

### 2. Entiende la definición de New Code

Ve a *Project Settings → New Code Definition* (o *General Settings → Issue Tracking* según versión) y selecciona:

| Opción | Qué hace | Cuándo usarla |
|---|---|---|
| **Previous version** | Considera nuevo el código desde el último incremento de `sonar.projectVersion` | Apps con releases versionadas |
| **Number of days** | Considera nuevo el código modificado en los últimos X días (default **30**, máx **90**) | Proyectos sin versiones formales |
| **Specific analysis** | Considera nuevo el código desde un análisis que tú eliges | 데Modos de arranque manual |
| **Reference branch** | Compara con la rama principal | ⚠️ Solo SonarQube Server |

**Para este ejercicio usa `Previous version`.**

### 3. Incrementa la versión y vuelve a analizar

`Previous version` necesita que el número de versión cambie para detectar código nuevo:

```bash
sonar-scanner -Dsonar.projectVersion=1.0.0
# primer análisis: todo el código es "nuevo"

# Arregla un archivo
echo "# comentario" >> src/nuevo_codigo.py

sonar-scanner -Dsonar.projectVersion=1.0.1
# ahora solo lo modificado desde 1.0.0 cuenta como "código nuevo"
```

> ⚠️ **Trampa frecuente:** poner `sonar.projectVersion=$CI_BUILD_NUMBER` (el número de build de CI) hace que **cada build sea una versión nueva**, y por tanto todo el código_modified se marque como nuevo. La propia documentación de SonarSource advierte de esto. Usa la versión de release real.

### 4. Activa el Fudge Factor

*Project Settings → General Settings → Fudge factor*: **activado**.

Comprueba su efecto:

- Con el fudge factor **activado**, los cambios de menos de 20 líneas no evaluan cobertura ni duplicación.
- **Desactivado**, un cambio de 3 líneas sin tests ya hace fallar el Quality Gate.

> 🧠 **¿Es bueno o malo?** Es un trade-off real. El fudge factor reduce el ruido en cambios triviales, pero deja pasar código sin tests en cambios pequeños. Algunos equipos lo desactivan; otros suben el umbral. Lo importante es que **la decisión sea explícita y consciente**.

### 5. Analiza solo el código nuevo

Mira en el dashboard la comparación:

| Panel | Qué muestra |
|---|---|
| **Overall Code** | El proyecto entero: deuda técnica histórica incluida |
| **New Code** | Solo lo añadido/modificado desde la última versión |

En un proyecto con `Previous version` correctamente configurado, verás:

- Overall Code: ❌ (rojo, con muchos issues)
- New Code: depende de lo que hayas escrito

**Ese contraste es exactamente la metodología Clean as You Code.**

### 6. Configura el Quality Profile

*Quality Profiles → Sonar way → Editar reglas*.

#### Ejercicio 6.1 — Activa una regla que está desactivada

Busca la regla **`python:S1192`** (*"String literals should not be duplicated"*) y actívala. Vuelve a analizar y observa los nuevos issues.

#### Ejercicio 6.2 — Desactiva una regla ruidosa

Busca una regla que genere falsos positivos en tu proyecto y desactívala **solo en ese proyecto**.

> ⚠️ Preferencia: usa una **Quality Profile derivado** en lugar de modificar `Sonar way`. Así puedes comparar ambos y revertir sin consecuencias:
> *Quality Profiles → Create → Duplicate "Sonar way" → "Sonar way — mi proyecto"*
> Luego en *Project Settings → Quality Profiles* asigna el derivado al proyecto.

### 7. Crea un Quality Gate personalizado

*Quality Gates → Create → Duplicar "Sonar way"* y y llámalo "Curso DevSecOps".

Cambia las condiciones:

| Condición | Sonar way (default) | Propuesta para el curso |
|---|---|---|
| Issues en código nuevo | > 0 | > 0 |
| Cobertura en código nuevo | < 80% | **< 90%** |
| Duplicación en código nuevo | > 3% | > 1% |
| Revisión de hotspots de seguridad | < 100% | 100% |

> 🔐 Crear Quality Gates requiere el permiso **Administer Quality Gates** (disponible con `admin`).

Asigna el Quality Gate a tu proyecto:
*Project Settings → General Settings → Quality Gate → "Curso DevSecOps"*.

### 8. Arregla el código nuevo hasta pasar el Quality Gate

Abre `src/nuevo_codigo.py` y encuentra los errores que tú mismo introdujiste:

```python
# ERROR 1: multiplica por 2 en lugar de usar el subtotal
def calcular_total(self, pedido):
    total = pedido.subtotal * 2      # ← debería ser pedido.subtotal
    ...

# ERROR 2: la función "valida" pero no valida nada
def validar_pedido(pedido):
    return True                     # ← debería validar subtotal > 0, cupón válido...

# ERROR 3: variables sin usar
def notificaciones(pedido, canal=None):
    mensaje = "Pedido procesado"
    aviso = "Aviso"                 # ← `aviso` nunca se usa
    return mensaje, aviso

# ERROR 4: falta anotación de tipo de retorno y no hay cobertura
def aplicar_puntos(pedido, puntos):
    ...
```

Arregla cada uno de los cuatro y vuelve a analizar:

```bash
sonar-scanner -Dsonar.projectVersion=1.0.2
```

### 9. Completa la cobertura del código nuevo

La condición es **80-90 % de cobertura en código nuevo**. Los tests existentes cubren `aplicar_puntos` y `notificaciones`, pero apenas rozan `validar_pedido`.

```bash
pip install pytest-cov

python -m pytest --cov=src/nuevo_codigo --cov-report=xml:coverage.xml

sonar-scanner \
  -Dsonar.projectVersion=1.0.3 \
  -Dsonar.python.coverage.reportPaths=coverage.xml
```

> 📌 El scanner **no ejecuta tus tests ni genera la cobertura**: solo lee el informe que ya existe en disco. El orden es obligatorio: `pytest` debe terminar **antes** de que arranque el escáner.

Añade los tests que falten hasta llegar al umbral.

> 💡 **Consejo de Clean as You Code:** escribe el test **antes** de arreglar el código. Si el test falla primero y pasa después, sabes que el test verifica algo real.

### 10. Comprueba el Quality Gate en verde

```bash
# Desde el propio scanner, bloqueando el pipeline
sonar-scanner \
  -Dsonar.projectVersion=1.0.4 \
  -Dsonar.python.coverage.reportPaths=coverage.xml \
  -Dsonar.qualitygate.wait=true
```

Salida esperada:

```
INFO: Quality gate status: SUCCESS
```

Y el código de salida del scanner será `0`.

Si el Quality Gate falla:

```bash
echo $?    # != 0
```

Consulta el detalle vía API:

```bash
curl -s -u "$SONAR_TOKEN:" \
  "http://localhost:9000/api/qualitygates/project_status?projectKey=devsecops-lab-02" \
  | python3 -m json.tool
```

Verás exactamente qué condición falló y en qué métrica.

### 11. El resultado final que deberías ver

```
   Overall Code                    New Code
   ────────────                    ─────────
   Reliability: D  ❌              Reliability: A  ✅
   Security:     C  ❌              Security:     A  ✅
   Maintainab.:  D  ❌              Maintainab.:  A  ✅
   Coverage:     12% ❌             Coverage:    91% ✅
   Duplication:  31% ❌             Duplication:  1% ✅

   DEUDA ACEPTADA                  CERO DEUDA NUEVA
   (congelada)                     (garantizada)
```

**Ese contraste es el entregable de este ejercicio.**

---

## ✅ Comprobación final

- [ ] Entiendo la diferencia conceptual entre "arreglar la deuda" y "congelarla"
- [ ] He configurado la definición de New Code como `Previous version`
- [ ] Sé para qué sirve el Fudge Factor y cuándo desactivarlo
- [ ] He creado un Quality Profile derivado
- [ ] He creado un Quality Gate personalizado con condiciones más estrictas
- [ ] He arreglado los 4 errores del código nuevo
- [ ] He completado la cobertura del código nuevo hasta el umbral
- [ ] El Quality Gate devuelve `SUCCESS` con `sonar.qualitygate.wait=true`

---

## 🤔 Preguntas de reflexión

1. Tu jefe pide "deja el proyecto en verde antes del trimestre". ¿Qué le responderías con lo aprendido aquí?
2. El fudge factor está activado y un desarrollador añade 15 líneas de código sin tests. El Quality Gate pasa. ¿Es aceptable? ¿Qué harías?
3. Si subes demasiado el listón del Quality Gate (cobertura 95 %, 0 duplicación, 0 issues), ¿qué efectos secundarios tiene en el equipo?
4. ¿Por qué SonarSource desaconseja explícitamente usar el número de build como `sonar.projectVersion`?
5. En un proyecto con `Number of days = 30`, un issue de hoy pasa a formar parte del código viejo en 30 días. ¿Qué implica eso para la deuda técnica?

---

## ⏭️ Siguiente

[Ejercicio 03 — Exclusiones y falsos positivos →](../03-exclusiones-y-falsos-positivos/README.md)
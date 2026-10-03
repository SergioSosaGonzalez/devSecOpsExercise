# Ejercicio 03 — Exclusiones y falsos positivos

**Nivel:** 🟡 Intermedio · **Duración estimada:** 50 min

## 🎯 Objetivo

Aprender a reducir el ruido de SonarQube **sin debilitar el control de calidad**, usando las herramientas correctas: exclusiones por ruta, exclusiones por métrica, `NOSONAR` justificado y perfiles de calidad. Saber cuándo **no** excluir.

## 📋 Requisitos previos

- [Ejercicio 02 completado](../02-clean-as-you-code/README.md)

---

## 🧠 Por qué esto decide si tu SonarQube sirve o no

```
   Un SonarQube con 600 issues donde solo 20 son reales:

     → El equipo silencia el panel.
     → Nadie mira los dashboards.
     → El Quality Gate se "salta" con excusas.
     → You've paid 4 GB of RAM for a noise generator.
```

El tuning no es opcional: es la diferencia entre un control que se respeta y uno que se ignora. Pero tiene un límite: **excluir es una decisión que se paga después**.

---

## 📦 Material de trabajo

```
fixtures/
├── src/
│   └── falsos_positivos.py    ← 4 falsos positivos + 3 problemas REALES
├── vendor/
│   └── generado_automaticamente.py   ← código generado: exclusión legítima
├── tests/
│   └── test_falsos_positivos.py
├── sonar-project.properties          ← configuración "sucia" (sin exclusiones)
└── sonar-project.final.properties    ← la solución
```

> ⚠️ **El ejercicio NO consiste en copiar la solución final.** Consiste en decidir, para cada hallazgo, si es un falso positivo o un problema real, y elegir la herramienta adecuada.

---

## Pasos

### 1. Analiza el estado "sucio"

```bash
cd fixtures/
export SONAR_HOST_URL=http://localhost:9000
export SONAR_TOKEN=squ_TU_TOKEN_AQUI

sonar-scanner
```

Anota el total de issues y su distribución por fichero. Vas a necesitar estos números para el paso 8.

### 2. Clasifica cada hallazgo: ¿real o falso positivo?

Abre `src/falsos_positivos.py` y revisa los hallazgos de SonarQube. Completa esta tabla mental (y anótala):

| Hallazgo | ¿Real o falso positivo? | Herramienta correcta |
|---|---|---|
| MD5 para deduplicar contenido | Falso positivo | `NOSONAR` justificado |
| Comparación de firmas con `==` | Falso positivo | `NOSONAR` justificado o regla |
| `json.loads()` sobre fichero propio | Falso positivo | Exclusión de regla / `NOSONAR` |
| `API_ENDPOINT` con "api" en el nombre | Falso positivo | `NOSONAR` justificado |
| **SQL con concatenación de entrada** | **REAL** | Arreglar el código |
| **Credenciales hardcodeadas** | **REAL** | Arreglar el código |
| **`except:` vacío** | **REAL** | Arreglar el código |
| `if False:` | REAL | Arreglar el código |
| Nombres `x`, `y`, `z` | REAL | Arreglar el código |

> 🔴 **Punto clave:** el fichero está lleno de comentarios `# NOSONAR` que son **malos ejemplos**. `NOSONAR` sin justificación es exactamente lo contrario de una buena práctica: silencia la regla **para siempre, en todas las líneas siguientes**, sin dejar constancia de por qué.

### 3. Aprende cómo funciona `NOSONAR` (y sus límites)

```python
# ✅ SINÓNAR para una línea concreta
valor = hashlib.md5(contenido.encode()).hexdigest()  # NOSONAR

# ✅ NOSONAR con justificación explícita
valor = hashlib.md5(contenido.encode()).hexdigest()  # NOSONAR - MD5 usado solo para deduplicar, no para secretos

# ❌ SINÓNAR para "quitarme el issue de encima" sin motivo
if firma == esperado:  # NOSONAR
```

**Reglas de uso correcto:**

| Regla | Motivo |
|---|---|
| Siempre con justificación tras `# NOSONAR - ` | Quien lo lea dentro de 6 meses debe entender por qué |
| Solo en la línea exacta | Aplica a la línea, no al bloque |
| Con issue tracker cuando sea posible | Deja trazabilidad de por qué se silenció |
| Con fecha y revisor | Para poder revisarlo después |

> 🚨 **El peligro de `NOSONAR`:** silencia **todas** las reglas de esa línea. Si además de MD5 la línea tuviera otro problema, nadie lo verá jamás. Úsalo con extrema moderación.

**Alternativa moderna preferible:** en lugar de `NOSONAR`, desactivar **la regla concreta** en el Quality Profile para ese proyecto. Es más auditable:

*Quality Profiles → tu perfil → Editar reglas → busca la regla → Desactivar*

### 4. Excluye el código generado

`vendor/generado_automaticamente.py` simula código generado. Nadie va a arreglar `if True:` en un fichero que se regenera.

```properties
# sonar-project.properties
sonar.exclusions=**/vendor/**
```

Vuelve a analizar y compara los números.

> 💡 **Alternativa mejor que la exclusión por ruta:** si el fichero es generado, lo ideal es **no incluirlo en `sonar.sources`**. La exclusión es el parche; excluir la ruta de origen es la solución.

**Regla de oro:** *excluye lo generado, lo que no es código (ficheros de datos, migraciones, protos compilados) y lo que nadie va a mantener.*

### 5. Usa exclusiones por patrón de fichero

Además de las rutas:

```properties
sonar.exclusions=**/*.min.js,**/*.min.css,**/*_pb2.py,**/*.generated.ts
```

| Patrón | Caso típico |
|---|---|
| `**/*.min.js` | Bundle minificado |
| `**/*_pb2.py` | Código generado por Protobuf |
| `**/*.generated.*` | Salida de un generador |
| `**/node_modules/**` | Dependencias (ya se excluye por defecto) |

### 6. Excluye de la cobertura (no del análisis)

Este es un matiz que mucha gente pasa por alto: **excluir un fichero del análisis es distinto de excluirlo de la cobertura**.

```properties
sonar.coverage.exclusions=**/vendor/**,**/config/**,**/*_pb2.py,**/setup.py,**/__main__.py
```

| Fichero | ¿Tiene sentido medir su cobertura? |
|---|---|
| `vendor/generado.py` | ❌ No se testea ni se puede testear |
| `config/settings.py` | ⚠️ Discutable: a veces sí conviene testearlo |
| `setup.py` | ❌ Boilerplate |
| `__main__.py` | ❌ Solo 2 líneas de arranque |
| `src/validators.py` | ✅ **Sí**, y no debe excluirse |

> 🚫 **Error grave frecuente:** añadir `sonar.coverage.exclusions=**/*` para que el Quality Gate pase. Eso destruye la única métrica que obliga a testear. Si te ves tentado, recuerda: **la cobertura no es una métrica de calidad del código, es una métrica de inversión en tests.**

### 7. Excluye de la duplicación (CPD)

Los tests legítimamente repetitivos y los ficheros de datos generan duplicación que no es deuda técnica:

```properties
sonar.cpd.exclusions=**/vendor/**,**/tests/**,**/fixtures/**,**/*_pb2.py

# Opcional: excluir los tests de la prueba de duplicación en Python
sonar.cpd.python.tests.exclusions=**/tests/**
```

> 🧠 **Por qué `**/tests/**`?** Un fichero `test_payments.py` con métodos de test estructuralmente parecidos **no** es duplicación que debas corregir: los tests DEBEN parecerse entre sí. Por eso SonarQube tiene un ajuste específico para ello.

### 8. Mide el resultado

```bash
# Estado inicial
sonar-scanner --report-path antes.json
python3 -c "import json; print(len(json.load(open('antes.json'))), 'issues antes')"

# Con la configuración correcta
sonar-scanner -c sonar-project.final.properties --report-path despues.json
python3 -c "import json; print(len(json.load(open('despues.json'))), 'issues después')"
```

Ahora completa la tabla del paso 2 **usando las herramientas correctas** y vuelve a analizar.

**Criterio de éxito:**

| Métrica | Antes | Después objetivo |
|---|---|---|
| Issues totales | (lo que midas) | Reducidos ~40 % |
| Falsos positivos | Todos visibles | Todos justificados o silenciados con `NOSONAR` documentado |
| **Problemas reales** | **Visibles** | **Visibles y arreglados** |
| Cobertura | Incorrecta (cuenta código generado) | Real |
| Duplicación | Inflada por tests y vendor | Real |

### 9. Arregla los problemas reales

La exclusión no es una excusa. Los hallazgos reales del fichero **se arreglan**:

```python
# ❌ Inyección SQL
def construir_consulta(usuario_id):
    consulta = "SELECT * FROM usuarios WHERE id = '" + str(usuario_id) + "'"
    return consulta

# ✅ Parámetros preparados
def construir_consulta(usuario_id):
    return "SELECT * FROM usuarios WHERE id = ?", (usuario_id,)
```

```python
# ❌ Credenciales hardcodeadas
PASSWORD = "mIConTraSeNaFicticia2024"

# ✅ Variables de entorno (como viste en el módulo de Gitleaks)
import os
PASSWORD = os.environ["DB_PASSWORD"]
```

```python
# ❌ Except vacío
try:
    int(codigo)
    return True
except:
    return False

# ✅ Excepción concreta
try:
    int(codigo)
    return True
except ValueError:
    return False
```

```python
# ❌ Código muerto
if False:
    resultados.append(None)

# ✅ Simply no existe
```

### 10. Configura exclusiones como código, no como clicks

**Punto clave para equipos:** las exclusiones deben vivir en el repositorio, versionadas y revisadas.

```
✅  sonar-project.properties en Git, con pull request para cambiarlo
❌  Exclusiones configuradas en la UI que nadie más ve
```

Comprueba qué hay en tu repositorio:

```bash
cat sonar-project.final.properties
```

Cada exclusión debe poder responder a tres preguntas:

| Pregunta | Ejemplo válido |
|---|---|
| **¿Por qué**? | "Código generado, se regenera en cada build" |
| **¿Hasta cuándo**? | "Hasta que el generador emita código limpio" |
| **¿Quién lo revisa**? | "Revisado por el equipo de plataforma cada trimestre" |

Una exclusión sin esas tres respuestas es deuda técnica disfrazada de configuración.

### 11. Auditoría: ¿cuánto has silenciado?

```properties
# Comprueba la proporción
sonar.issue.ignore.multicriteria=e1,e2
sonar.issue.ignore.multicriteria.e1.ruleKey=python:S110
sonar.issue.ignore.multicriteria.e1.name=No placeholder
```

Para una auditoría sencilla:

```bash
# Issues ignorados en la base de datos del servidor
curl -s -u "$SONAR_TOKEN:" \
  "http://localhost:9000/api/issues/search?componentKeys=devsecops-lab-03&resolved=true" \
  | python3 -c "import sys,json; print(len(json.load(sys.stdin)['issues']), 'issues ignorados')"
```

> 📊 **Métrica de salud de un SonarQube:** si tienes más del 5 % de tus issues en estado "ignored", tienes un problema de calidad de reglas, no de código. Es el mismo principio que aprendiste con `.gitleaksignore`.

---

## ✅ Comprobación final

- [ ] Sé distinguir entre los 5 tipos de exclusión y cuándo usar cada una
- [ ] Entiendo por qué `sonar.coverage.exclusions` **no** es lo mismo que `sonar.exclusions`
- [ ] Sé cuándo `NOSONAR` es aceptable y cuándo es un abuse
- [ ] He justificado con un motivo escrito cada uso de `NOSONAR`
- [ ] He arreglado (no excluido) los problemas reales de inyección SQL y credenciales
- [ ] Sé por qué `**/tests/**` va en `sonar.cpd.exclusions` pero no en `sonar.exclusions`
- [ ] Entiendo por qué las exclusiones deben estar en Git y no en la UI
- [ ] Puedo auditar cuánto he silenciado

---

## 🤔 Preguntas de reflexión

1. `# NOSONAR` silencia **todas** las reglas de esa línea. ¿Qué regla importante podría quedar oculta sin que nadie lo note? ¿Hay alguna forma más segura de lograr lo mismo?
2. Un compañero añade `sonar.exclusions=**/*` a `sonar-project.properties` para que su PR pase. El Quality Gate se pone en verde en 5 minutos. ¿Qué hiciste mal tú? ¿Cómo lo previenes?
3. `sonar.coverage.exclusions=**/tests/**` es un error de principiantes muy común. ¿Por qué? ¿Qué métrica quedaría sin ningún dato?
4. ¿Cuándo es legítimo excluir código del análisis? Escribe las 3 categorías válidas y una inválida.
5. El equipo lleva 6 meses con SonarQube y tiene el 30 % de los issues en "ignored". ¿Es un problema de los desarrolladores o del Quality Profile? ¿Qué harías primero?
6. Un fichero generado tiene un problema de seguridad **real** (uso de MD5 para una contraseña). ¿Lo excluirías? Justifica tu respuesta.

---

## ⏭️ Siguiente

[Ejercicio 04 — Integración con CI/CD →](../04-ci-github-actions/README.md)
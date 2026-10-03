# Ejercicio 06 — Remediación de secretos filtrados

**Nivel:** 🔴 Avanzado · **Duración estimada:** 45 min

## 🎯 Objetivo

Aprender el procedimiento real que se sigue cuando Gitleaks (o cualquier otro mecanismo) confirma que un secreto ha sido filtrado: **rotar, limpiar el historial y verificar**.

## 📋 Requisitos previos

- [Ejercicio 05 completado](../05-ci-github-actions/README.md)
- `git-filter-repo` instalado (opcionalmente `bfg`)
- Java instalado (solo para BFG)

---

## 🚨 El error número uno

> **Borrar el archivo NO es remediar. Revocar la credencial SÍ.**

Un secreto que estuvo en un commit debe considerarse **comprometido** desde el primer segundo, aunque lo elimines un minuto después. Los bots que extraen credenciales de repositorios públicos **escanean de forma continua** (y también indexan repositorios privados filtrados, caches, mirrors y backups).

El orden correcto es siempre:

```
  1. DETECTAR   →  2. REVOCAR  →  3. NOTIFICAR  →  4. LIMPIAR  →  5. VERIFICAR
                     ▲
                     │
              PRIORIDAD ABSOLUTA
```

---

## Pasos

### 1. Reproduce el escenario en un repositorio aislado

```bash
mkdir -p /tmp/demo-remediacion && cd /tmp/demo-remediacion
git init

# Commit 1: configuración "segura"
echo "# App de pagos" > README.md
git add . && git commit -m "commit inicial"

# Commit 2: alguien pega su clave por accidente
echo "STRIPE_SECRET_KEY=sk_live_FicticiaParaElEjercicio123456789" > config.py
git add . && git commit -m "config inicial"

# Commit 3: "arreglo" rápido
rm config.py
git add -A && git commit -m "eliminar config"
```

Detecta el problema:

```bash
gitleaks git -v .
```

---

### 2. Evalúa la exposición

Antes de actuar, responde estas preguntas:

```bash
# ¿En qué commits aparece?
git log --all --oneline -S "sk_live_"

# ¿Quién lo añadió?
git log --all -p -S "sk_live_" | grep "^Author:"

# ¿Cuándo se publicó el repositorio?
git log --reverse --format="%ci %h %s" | head -1

# ¿Cuánto tiempo lleva el secreto en el historial?
# (fecha actual - fecha del commit con el secreto)
```

Documenta estas respuestas: en un incidente real habrá que escribir un post-mortem.

---

### 3. ⚠️ PASO CRÍTICO — Revoca la credencial

**Antes de tocar el historial**, revoca la credencial en el proveedor:

| Proveedor | Dónde revocarla |
|---|---|
| **AWS** | IAM → Access keys → *Deactivate* / *Delete* → crea una nueva |
| **GitHub PAT** | Settings → Developer settings → Personal access tokens → *Revoke* |
| **Stripe** | Dashboard → Developers → API keys → *Roll* key |
| **Slack** | api.slack.com/apps → tu app → *Revoke* |
| **Base de datos** | `ALTER USER app_user WITH PASSWORD 'nueva-clave-generada';` |

También hay que **buscar en toda la organización** si esa credencial se usaba en otros servicios, y rotarla allí también.

> 🔑 Crea siempre la credencial nueva **antes** de borrar la vieja, para no dejar el sistema sin acceso durante la transición. Y guarda la nueva en un gestor de secretos, nunca en un archivo.

---

### 4. Limpia el historial con `git filter-repo`

`git filter-repo` es la herramienta moderna y recomendada. Instálala:

```bash
# macOS
brew install git-filter-repo

# Linux
pipx install git-filter-repo
# o descarga el script:
curl -o ~/.local/bin/git-filter-repo https://raw.githubusercontent.com/newren/git-filter-repo/main/git-filter-repo
chmod +x ~/.local/bin/git-filter-repo

# Windows
pip install git-filter-repo
```

#### Opción A — Reemplazar el secreto en todos los commits

```bash
cd /tmp/demo-remediacion

# Sustituye el texto del secreto en todo el historial
git filter-repo --replace-text <(echo 'sk_live_FicticiaParaElEjercicio123456789==>***ROTADO***')
```

#### Opción B — Eliminar un archivo del historial completo

```bash
# Elimina config.py de TODOS los commits, pasados y futuros
git filter-repo --path config.py --invert-paths
```

#### Opción C — Eliminar solo los commits con el secreto

```bash
# Útil cuando el commit afectado no debe existir en absoluto
git filter-repo --commit-callback '
  return commit if b"sk_live_" not in commit.message else None
'
```

> ⚠️ **`git filter-repo` reescribe todos los hashes.** No funciona en un repositorio con clones ya existentes: tendrás que hacer `git push --force` y que todos los colaboradores hagan `git fetch && git reset --hard origin/main`.

---

### 5. Alternativa clásica: BFG

```bash
# Requiere Java
bfg --delete-files config.py
```

BFG es más rápido en repositorios enormes, pero `git filter-repo` es la opción mantenida y con más opciones. **Usa `git filter-repo`.**

---

### 6. Fuerza el push y notifica

```bash
# ⚠️ DESTRUCTIVO:Coordinate con tu equipo ANTES
git push --force --mirror
```

Después:

1. **Notifica a todo el equipo**: "el historial ha sido reescrito, ejecuta `git fetch && git reset --hard origin/main`".
2. **Protege las ramas**: activa la protección contra force-push para que esto no vuelva a pasar sin revisión.
3. **Considera el repo "filtrado"**: aunque limpies el historial, un fork existente, una copia en caché o un mirror seguirá teniendo el secreto. Por eso el paso 3 (revocar) no es opcional.

---

### 7. Verifica que el historial está limpio

```bash
# 1. Gitleaks ya no encuentra nada
gitleaks git -v .
# Salida esperada: "no leaks found"

# 2. Confirmación manual
git log --all -p | grep "sk_live_"
# No debe devolver nada

# 3. Busca en todas las ramas y tags
git rev-list --all | while read commit; do
  git grep -l "sk_live_" "$commit" 2>/dev/null && echo "ENCONTRADO en $commit"
done
```

---

### 8. Cierra el ciclo: evita la repetición

Un incidente sin causa raíz corregida se repite. Completa estas acciones:

#### a) Añade el control que faltaba

```bash
# ¿Tenías pre-commit? ¿CI? ¿Branch protection?
# Si no, este es el momento de añadirlos (ejercicios 04 y 05)
```

#### b) Reduce el alcance del secreto

- Usa **permisos mínimos** en cada credencial: una key de solo lectura no puede hacer lo mismo que una de administración.
- Usa **credenciales temporales** siempre que el proveedor lo permita (AWS STS, GitHub Actions OIDC en vez de tokens de larga duración).

#### c) Sustituye el archivo de secretos

Nunca más hardcodeado. Opciones por orden de coste:

```
  1. Variables de entorno          (gratis, ideal para CI)
  2. .env + .gitignore             (gratis, solo desarrollo local)
  3. SOPS / git-crypt              (cifrado en el repo, para equipos pequeños)
  4. HashiCorp Vault               (industria, rotación automática)
  5. Gestor cloud (AWS Secrets Manager, Azure Key Vault, GCP Secret Manager)
```

#### d) Documenta el incidente

Escribe un post-mortem corto:
- Qué pasó y cuándo
- Cómo se detectó
- Blast radius: a qué sistemas se accedió
- Qué se rotó
- Qué control falta y quién lo va a añadir

---

### 9. Checklist de verificación

```bash
# 1. La credencial está revocada  → selecciónalo tú en el proveedor
# 2. El historial está limpio      → gitleaks git -v .  == "no leaks found"
# 3. No quedan copias              → revisa forks, releases, artefactos, caches
# 4. El equipo está sincronizado   → todos ejecutaron git reset --hard
# 5. Existen controles nuevos      → pre-commit + CI + branch protection
# 6. Hay post-mortem documentado
```

---

## ✅ Comprobación final

- [ ] Entiendo por qué revocar es más importante que limpiar
- [ ] Sé usar `git filter-repo` con sus tres modos principales
- [ ] Sé reescribir el historial y forzar el push con sus consecuencias
- [ ] Sé verificar que el repositorio quedó limpio
- [ ] Sé qué medidas evitan que el incidente se repita
- [ ] Entiendo el coste y los riesgos de reescribir el historial

---

## 🤔 Preguntas de reflexión

1. ¿Por qué reescribir el historial **no** es un sustituto de revocar la credencial? Escribe una frase que se pudrías decir a un jefe que pregunte "¿no lo borraste ya?".
2. ¿Qué pasa con los **tags** y las **releases** de GitHub cuando reescribes el historial? Investiga y explica por qué eso es un problema.
3. ¿Por qué el ejercicio 05 usa `fetch-depth: 0`? ¿Qué pasaría si un secreto se filtró en un commit de hace 2 años y el pipeline solo revisa el último commit?
4. ¿En qué se diferencia la exposición de un secreto en un repositorio **privado** frente a uno **público**? ¿Cambia la prioridad de la respuesta?
5. ¿Qué harías si descubrieras que el secreto se filtró en un repositorio público, ya está indexado por un motor de búsqueda y **no puedes eliminarlo**? ¿Cuál es el siguiente paso?

---

## 🏁 Fin del módulo de Gitleaks

Has cubierto el ciclo completo de secret scanning:

```
 Detectar  →  Alertar  →  Bloquear  →  Remediar
  (01,02)     (03)        (04,05)       (06)
```

**Siguiente paso recomendado:** elegir la segunda herramienta del curso (Trivy, Semgrep, Checkov...) y crear la carpeta correspondiente siguiendo el mismo esquema: `README.md` de introducción + ejercicios numerados.

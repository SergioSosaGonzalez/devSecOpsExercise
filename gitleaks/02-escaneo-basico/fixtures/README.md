# ⚠️ FIXTURES DE PRUEBA — SEGREGOS FICTICIOS

Esta carpeta contiene **secretos deliberadamente falsos** utilisé únicamente para
los ejercicios del curso.

## ✅ Todos los valores de aquí son ficticios

- **No son credenciales reales** y **no dan acceso a ningún sistema**.
- Están publicados aquí con la única intención de que Gitleaks los detecte.
- Los patrones siguen el formato de los proveedores reales, por eso las
  herramientas los consideran "secretos válidos".

## 🚨 Regla de oro del curso

> **Nunca** subas secretos reales a un repositorio, ni siquiera a uno privado.
> Si ocurre, trátalo como un incidente: revoca la credencial **inmediatamente**.

## Archivos

| Archivo | Qué contiene | Reglas que dispara |
|---|---|---|
| `.env.ejemplo` | API keys de AWS, GitHub, Stripe, Slack y contraseñas | `aws-access-token`, `github-pat`, `stripe-access-token`, `slack-bot-token`, `generic-api-key` |
| `config/database.yml` | Contraseñas de PostgreSQL, SMTP y Redis | `generic-api-key` |
| `app-basico/main.py` | Token JWT y clave privada RSA hardcodeados | `jwt`, `private-key` |
| `script-implementado.sh` | Ejemplo de cómo **no** subir secretos | ninguna (es el ejemplo correcto) |

**Total esperado al ejecutar `gitleaks dir -v ./fixtures`: 11 hallazgos.**

## Nota sobre `.env.ejemplo`

El sufijo `.ejemplo` es intencional: representa el error clásico de "subo mi
`.env` de producción al repo porque solo son valores de ejemplo". Gitleaks lo
detectará, y está bien que lo haga: así es como se ven los errores en la vida
real.

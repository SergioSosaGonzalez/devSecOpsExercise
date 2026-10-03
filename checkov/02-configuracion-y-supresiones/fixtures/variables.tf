# ============================================================
# FIXTURE DE LABORATORIO — Checkov · variables (v2)
# ============================================================

variable "nombre_bucket" {
  description = "Nombre del bucket de datos"
  type        = string
  default     = "empresa-datos-clientes-2024"
}

# --- Sin default, y marcada como sensible ---
# Que no tenga default no la hace segura: si alguien la define
# con un valor débil en un .tfvars, el error sigue ahí. Lo que
# protege de verdad es no hacer login con contraseña.
variable "password_pedidos" {
  description = "Contraseña de la base de datos de pedidos"
  type        = string
  sensitive   = true
  default     = null
}

# --- Este default SÍ es un problema ---
# El bucket de logs hereda una ACL pública sin que nadie lo
# escriba explícitamente en el recurso.
variable "acl_logs" {
  description = "ACL del bucket de logs"
  type        = string
  default     = "public-read"
}
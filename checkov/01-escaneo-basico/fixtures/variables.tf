# ============================================================
# FIXTURE DE LABORATORIO — Checkov · variables
# ============================================================
# Checkov resuelve las variables de Terraform usando sus valores
# por defecto (evaluate-variables está activo por defecto). Eso
# significa que un default inseguro en este fichero aparece como
# hallazgo, aunque el `.tf` que lo usa solo ponga `var.acl`.
# ============================================================

variable "nombre_bucket" {
  description = "Nombre del bucket de datos"
  type        = string
  default     = "empresa-datos-clientes-2024"
}

# --- Misconfiguración 14: el default de la ACL es público ---
# Aunque el recurso escriba `acl = var.acl_bucket`, Checkov ve el
# default y falla CKV_AWS_20.
variable "acl_bucket" {
  description = "ACL del bucket (¡no debería ser public-read!)"
  type        = string
  default     = "public-read"
}

variable "rango_ip_admin" {
  description = "Rango de IP desde el que se administra lainfra"
  type        = string
  default     = "0.0.0.0/0"
}
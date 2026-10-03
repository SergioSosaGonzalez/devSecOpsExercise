# ============================================================
# FIXTURE DE LABORATORIO — Checkov · red (v2)
# ============================================================

resource "aws_security_group" "web" {
  name        = "web-sg"
  description = "Tráfico web de la aplicación"

  ingress {
    description = "HTTPS desde la red corporativa"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/8"]
  }

  # --- Salida hacia el peering: la VPC de destino ---
  egress {
    description = "Salida al peering de datos"
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["10.1.0.0/16"]
  }
}

# --- Este grupo existe pero no lo usa nadie ---
# Es el error clásico que un check de grafo (CKV2_AWS_5) sí ve
# y un check de recurso no.
resource "aws_security_group" "huerfano" {
  name        = "huerfano-sg"
  description = "Grupo de seguridad sin usar (laboratorio)"

  ingress {
    description = "Ping desde dentro de la VPC"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["10.0.0.0/8"]
  }
}
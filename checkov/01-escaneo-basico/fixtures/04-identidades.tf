# ============================================================
# FIXTURE DE LABORATORIO — Checkov · identidades
# ============================================================

# --- Misconfiguración 12: política con permisos de administrador ---
# Action "*" y Resource "*": la política equivalente a root.
# Falla CKV_AWS_1, CKV_AWS_40, CKV_AWS_61, CKV_AWS_62,
# CKV_AWS_355 y varios checks de grafo CKV2_AWS_*.
resource "aws_iam_policy" "operaciones" {
  name        = "operaciones-acceso-total"
  description = "Permisos para el equipo de operaciones"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "Todo"
        Effect = "Allow"
        Action = "*"
        Resource = "*"
      },
    ]
  })
}

# --- Misconfiguración 13: usuario humano con clave estática ---
resource "aws_iam_user" "deploy" {
  name = "usuario-deploy"
  path = "/humanos/"
}

resource "aws_iam_user_login_profile" "deploy" {
  user                    = aws_iam_user.deploy.name
  password                = "D3pl0y-Estatico-Ficticio-2024"
  password_reset_required = false
}
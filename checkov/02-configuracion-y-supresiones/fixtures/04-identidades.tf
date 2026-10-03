# ============================================================
# FIXTURE DE LABORATORIO — Checkov · identidades (v2)
# ============================================================

# --- Remediado: la política ya no es "todo para todos" ---
# Se limita a lectura sobre buckets concretos. Comprueba que
# CKV_AWS_1, CKV_AWS_61 y CKV_AWS_355 pasan.
resource "aws_iam_policy" "lectura_datos" {
  name        = "lectura-datos-clientes"
  description = "Solo lectura sobre los buckets de clientes"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid      = "ListarBuckets"
        Effect   = "Allow"
        Action   = ["s3:ListAllMyBuckets"]
        Resource = "*"
      },
      {
        Sid      = "LeerObjetos"
        Effect   = "Allow"
        Action   = ["s3:GetObject"]
        Resource = "arn:aws:s3:::empresa-datos-clientes-2024/*"
      },
    ]
  })
}

# --- Sin usuario humano: solo roles, que es lo correcto ---
resource "aws_iam_role" "app" {
  name = "rol-aplicacion"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Service = "ec2.amazonaws.com"
      }
      Action = "sts:AssumeRole"
    }]
  })
}
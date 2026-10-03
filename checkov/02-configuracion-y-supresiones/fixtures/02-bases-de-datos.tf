# ============================================================
# FIXTURE DE LABORATORIO — Checkov · base de datos (v2)
# ============================================================
# La instancia legacy se ha reemplazado por una con la
# configuración recomendada. Sirve de contraste: lo que se ve
# aquí es un recurso que pasa todos los checks aplicables.
# ============================================================

resource "aws_db_instance" "pedidos" {
  identifier     = "pedidos-2025"
  engine         = "mysql"
  engine_version = "8.0.39"
  instance_class = "db.t3.small"
  allocated_storage = 50

  username = "pedidos_admin"
  # Sin contraseña en el código: se inyecta con variable sensible.
  password = var.password_pedidos

  publicly_accessible = false

  storage_encrypted     = true
  kms_key_id            = aws_kms_key.pedidos.arn
  backup_retention_period = 7
  deletion_protection    = true
  skip_final_snapshot    = false
  final_snapshot_identifier = "pedidos-final"
  multi_az               = true
  auto_minor_version_upgrade = true

  enabled_cloudwatch_logs_exports = ["audit", "error", "general", "slowquery"]
}

resource "aws_kms_key" "pedidos" {
  description             = "Cifrado de la base de datos de pedidos"
  enable_key_rotation     = true
  deletion_window_in_days = 30
}
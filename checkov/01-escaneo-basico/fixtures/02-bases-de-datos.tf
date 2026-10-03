# ============================================================
# FIXTURE DE LABORATORIO — Checkov · base de datos
# ============================================================
# Una instancia RDS heredada de 2019 que nadie ha tocado.
# ============================================================

# --- Misconfiguración 4: contraseña de RDS escrita en el código ---
# El valor es FICTICIO y existe solo para que Checkov tenga una
# credencial que señalar. En un repo real, esto además lo habría
# detectado el módulo de Gitleaks del curso.
# --- Misconfiguración 5: base de datos abierta a internet ---
# --- Misconfiguración 6: sin cifrado, sin backups, sin borrado protegido ---
resource "aws_db_instance" "pedidos" {
  identifier     = "pedidos-legacy"
  engine         = "mysql"
  engine_version = "5.7.44"
  instance_class = "db.t3.micro"
  allocated_storage = 20

  username = "pedidos_admin"
  password = "P3d1d0s-L3gacy-2024-Ficticio"

  publicly_accessible = true

  backup_retention_period = 0
  deletion_protection      = false
  skip_final_snapshot      = true
  multi_az                = false
}
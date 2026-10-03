# ============================================================
# FIXTURE DE LABORATORIO — Checkov · almacenamiento (v2)
# ============================================================
# Segunda versión del bucket: la remediación del ejercicio 01 está
# a medias. Aquí se ve lo que pasa cuando se arregla parte.
# ============================================================

resource "aws_s3_bucket" "datos_clientes" {
  bucket = var.nombre_bucket

  # --- Remediado: cifrado, versionado y acceso público bloqueado ---
  tags = {
    Entorno = "produccion"
  }
}

resource "aws_s3_bucket_versioning" "datos_clientes" {
  bucket = aws_s3_bucket.datos_clientes.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "datos_clientes" {
  bucket = aws_s3_bucket.datos_clientes.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "aws:kms"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "datos_clientes" {
  bucket = aws_s3_bucket.datos_clientes.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# --- El único bucket que se ha dejado como estaba ---
# CKV_AWS_18 (access logging), CKV2_AWS_61 (ciclo de vida) y
# CKV2_AWS_62 (notificaciones) siguen fallando. Sin embargo la
# replicación entre regiones no aplica a un bucket de logs:
# aquí va una supresión justificada y con motivo.
resource "aws_s3_bucket" "logs" {
  bucket = "empresa-logs-2024"

  # El recurso no dice "public-read" en ninguna parte: lo hereda
  # del default de variables.tf. Por eso este hallazgo solo aparece
  # si Checkov resuelve variables.
  acl = var.acl_logs

  #checkov:skip=CKV_AWS_144:los buckets de logs no se replican; la retención se define en lifecycle

  tags = {
    Entorno = "produccion"
  }
}
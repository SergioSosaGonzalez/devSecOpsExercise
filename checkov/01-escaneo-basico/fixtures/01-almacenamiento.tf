# ============================================================
# FIXTURE DE LABORATORIO — Checkov · almacenamiento
# ============================================================
# Un bucket "de producción" que en realidad es un descuido.
# ============================================================

# --- Misconfiguración 1: bucket sin cifrado propio ---
# Falla CKV_AWS_145 (KMS por defecto), CKV_AWS_21 (versionado),
# CKV_AWS_18 (access logging), CKV_AWS_144 (replicación) y
# los checks de grafo CKV2_AWS_6 / 61 / 62.
resource "aws_s3_bucket" "datos_clientes" {
  bucket = "empresa-datos-clientes-2024"
}

# --- Misconfiguración 2: el guardián que deja pasar todo ---
# La idea del recurso es bloquear el acceso público. Aquí está
# presente pero con los cuatro interruptores en false, que es
# exactamente igual a no tenerlo (CKV_AWS_53/54/55/56).
resource "aws_s3_bucket_public_access_block" "datos_clientes" {
  bucket = aws_s3_bucket.datos_clientes.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

# --- Misconfiguración 3: ACL pública explícita ---
# CKV_AWS_20: el bucket queda legible por "Everyone".
resource "aws_s3_bucket_acl" "datos_clientes" {
  bucket = aws_s3_bucket.datos_clientes.id
  acl    = "public-read"
}

# --- Esto sí está bien hecho, para contrastar ---
resource "aws_kms_key" "datos_clientes" {
  description             = "Cifrado de datos de clientes (laboratorio)"
  enable_key_rotation     = true
  deletion_window_in_days = 30
}
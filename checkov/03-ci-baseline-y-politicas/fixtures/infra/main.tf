# ============================================================
# FIXTURE DE LABORATORIO — Checkov · ejercicio 03
# ============================================================
# Stack pequeño a propósito: el baseline que se crea en el
# ejercicio tiene que caber en una pantalla. Seis recursos,
# 21 hallazgos de Terraform y 2 de las políticas internas
# CKV_EMPRESA_001/002 del directorio ../checks.
# ============================================================

terraform {
  required_version = ">= 1.5"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "eu-west-1"
}

# --- Recurso 1: bucket correcto salvo por el nombre ---
resource "aws_s3_bucket" "informes" {
  bucket = "informes-financieros"

  tags = {
    Entorno = "produccion"
    Owner   = "equipo-finanzas"
  }
}

resource "aws_s3_bucket_versioning" "informes" {
  bucket = aws_s3_bucket.informes.id

  versioning_configuration {
    status = "Enabled"
  }
}

# --- Recurso 2: bucket sin etiqueta de entorno ---
# Además lo detectará la política interna CKV_EMPRESA_001.
resource "aws_s3_bucket" "respaldos" {
  bucket = "respaldos-nocturnos"

  versioning_configuration {
    status = "Enabled"
  }
}

# --- Recurso 3: base de datos casi bien, con usuario prohibido ---
resource "aws_db_instance" "informes" {
  identifier     = "informes-mysql"
  engine         = "mysql"
  engine_version = "8.0.39"
  instance_class = "db.t3.small"
  allocated_storage = 50

  username = "informes_admin"

  publicly_accessible    = false
  storage_encrypted      = true
  backup_retention_period = 7
  deletion_protection     = true
  skip_final_snapshot     = false
  final_snapshot_identifier = "informes-final"
  multi_az               = true
  auto_minor_version_upgrade = true
}

# --- Recurso 4: grupo de seguridad abierto a todo ---
resource "aws_security_group" "salt" {
  name        = "salt-publico"
  description = "Cola de mensajes sinRegular"

  ingress {
    description = "MySQL desde cualquier sitio"
    from_port   = 3306
    to_port     = 3306
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    description = "Salida libre"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# --- Recurso 5: instancia bien configurada ---
resource "aws_instance" "bastion" {
  ami           = "ami-0c1d2e3f4a5b6c7d8" # AMI ficticia
  instance_type = "t3.small"

  metadata_options {
    http_endpoint = "enabled"
    http_tokens   = "required"
  }

  ebs_optimized = true
  monitoring    = true

  root_block_device {
    encrypted   = true
    volume_type = "gp3"
  }
}

# --- Recurso 6: cola de mensajes sin cifrado ---
resource "aws_sqs_queue" "trabajos" {
  name = "trabajos-cola"
}

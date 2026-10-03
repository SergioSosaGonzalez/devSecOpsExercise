# ============================================================
# FIXTURE DE LABORATORIO — Checkov
# ============================================================
# Este Terraform NO se aplica a AWS. Es material de curso y está
# deliberadamente mal configurado para que Checkov tenga algo que
# encontrar. Las cuentas de AWS son ficticias y no existen.
#
# Expectativas del ejercicio 01: leer la salida de `checkov -d .`
# y entender por qué cada recurso falla.
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

# Sin credenciales en el código: este bloque es un ejemplo de lo
# que hay que hacer. Checkov lo evalúa y lo marca como PASSED.
provider "aws" {
  region = "eu-west-1"
}
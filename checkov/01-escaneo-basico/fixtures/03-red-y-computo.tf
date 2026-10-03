# ============================================================
# FIXTURE DE LABORATORIO — Checkov · red y cómputo
# ============================================================

# --- Misconfiguración 7: SSH abierto a todo el mundo ---
# CKV_AWS_24 y, como el grupo no se asocia a nada,
# también el check de grafo CKV2_AWS_5.
resource "aws_security_group" "bastion" {
  name        = "bastion-sg"
  description = "Acceso al bastion"

  ingress {
    description = "SSH desde cualquier sitio"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # --- Misconfiguración 8: salida sin restricción a ningún sitio ---
  egress {
    description = "Salida libre"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# --- Misconfiguración 9: instancia sin cifrado de volumen ---
# --- Misconfiguración 10: IMDSv1 habilitado (SSRF a metadatos) ---
# --- Misconfiguración 11: sin monitorización detallada ---
resource "aws_instance" "web" {
  ami           = "ami-0c1d2e3f4a5b6c7d8" # AMI ficticia
  instance_type = "t3.micro"

  metadata_options {
    http_endpoint = "enabled"
    http_tokens   = "optional"
  }

  monitoring = false
}
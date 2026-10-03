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
  region = var.region
}

variable "region" {
  description = "Región de AWS"
  type        = string
  default     = "us-east-1"
}

variable "proyecto" {
  description = "Prefijo para nombrar los recursos"
  type        = string
  default     = "datacorp"
}

locals {
  etiquetas = {
    Proyecto = "DataCorp Analytics"
    Gestion  = "Terraform"
  }
}

# Bucket S3 para datos de staging (privado y cifrado)
resource "aws_s3_bucket" "staging" {
  bucket = "${var.proyecto}-staging-datos"
  tags   = merge(local.etiquetas, { Entorno = "staging" })
}

resource "aws_s3_bucket_public_access_block" "staging" {
  bucket                  = aws_s3_bucket.staging.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "staging" {
  bucket = aws_s3_bucket.staging.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Instancia EC2 para DEV
data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }
}

resource "aws_instance" "dev" {
  ami                  = data.aws_ami.amazon_linux.id
  instance_type        = "t3.medium"
  iam_instance_profile = aws_iam_instance_profile.dev.name
  tags                 = merge(local.etiquetas, { Entorno = "dev", Name = "${var.proyecto}-dev" })
}

# Base de datos RDS para PROD
resource "aws_db_instance" "prod" {
  identifier                  = "${var.proyecto}-prod-db"
  engine                      = "postgres"
  engine_version              = "16"
  instance_class              = "db.t3.medium"
  allocated_storage           = 50
  db_name                     = "ventas"
  username                    = "datacorp_admin"
  manage_master_user_password = true
  multi_az                    = true
  storage_encrypted           = true
  backup_retention_period     = 7
  deletion_protection         = true
  skip_final_snapshot         = false
  final_snapshot_identifier   = "${var.proyecto}-prod-final"
  publicly_accessible         = false
  tags                        = merge(local.etiquetas, { Entorno = "prod" })
}

# Rol IAM con permisos restringidos: DEV solo puede LEER muestras de staging
data "aws_iam_policy_document" "asumir_ec2" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "dev" {
  name               = "${var.proyecto}-rol-dev"
  assume_role_policy = data.aws_iam_policy_document.asumir_ec2.json
  tags               = local.etiquetas
}

data "aws_iam_policy_document" "solo_lectura_staging" {
  statement {
    sid       = "LeerMuestrasStaging"
    actions   = ["s3:GetObject", "s3:ListBucket"]
    resources = [aws_s3_bucket.staging.arn, "${aws_s3_bucket.staging.arn}/muestras/*"]
  }
}

resource "aws_iam_role_policy" "dev_lectura" {
  name   = "${var.proyecto}-lectura-staging"
  role   = aws_iam_role.dev.id
  policy = data.aws_iam_policy_document.solo_lectura_staging.json
}

resource "aws_iam_instance_profile" "dev" {
  name = "${var.proyecto}-perfil-dev"
  role = aws_iam_role.dev.name
}

output "bucket_staging" {
  value = aws_s3_bucket.staging.bucket
}

output "endpoint_db_prod" {
  value = aws_db_instance.prod.endpoint
}
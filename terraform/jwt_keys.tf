# JWT RSA Keypair generation and storage in AWS Secrets Manager

resource "tls_private_key" "jwt" {
  algorithm = "RSA"
  rsa_bits  = 2048
}

resource "aws_secretsmanager_secret" "jwt_private_key" {
  name        = "incident_cmd_jwt_private_key"
  description = "RSA private key for JWT signing (incident-cmd)"
}

resource "aws_secretsmanager_secret_version" "jwt_private_key_version" {
  secret_id     = aws_secretsmanager_secret.jwt_private_key.id
  secret_string = tls_private_key.jwt.private_key_pem
}

resource "aws_secretsmanager_secret" "jwt_public_key" {
  name        = "incident_cmd_jwt_public_key"
  description = "RSA public key for JWT verification (incident-cmd)"
}

resource "aws_secretsmanager_secret_version" "jwt_public_key_version" {
  secret_id     = aws_secretsmanager_secret.jwt_public_key.id
  secret_string = tls_private_key.jwt.public_key_pem
}

output "launchdarkly_environment_api_key" {
  description = "LaunchDarkly API key for server-side SDKs (Lambda)."
  value       = data.launchdarkly_environment.production.api_key
  sensitive   = true
}

output "launchdarkly_environment_client_side_id" {
  description = "LaunchDarkly client-side ID for frontend SDKs."
  value       = data.launchdarkly_environment.production.client_side_id
  sensitive   = true
}

output "ws_api_url" {
  description = "Base URL for the deployed WebSockets API using the custom domain."
  value       = "https://${aws_apigatewayv2_domain_name.custom.domain_name}"
}

output "rest_api_url" {
  description = "Base URL for the deployed REST API using the custom domain."
  value       = "https://${aws_api_gateway_domain_name.custom.domain_name}"
}

output "jwt_public_key_pem" {
  value = tls_private_key.jwt.public_key_pem
}

output "jwt_private_key_secret_arn" {
  value = aws_secretsmanager_secret.jwt_private_key.arn
}

output "jwt_public_key_secret_arn" {
  value = aws_secretsmanager_secret.jwt_public_key.arn
}

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

output "api_url" {
  description = "Base URL for the deployed API using the custom domain."
  value       = "https://${aws_apigatewayv2_domain_name.custom.domain_name}"
}

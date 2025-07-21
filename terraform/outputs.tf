output "api_url" {
  description = "Base URL for the deployed API using the custom domain."
  value       = "https://${aws_api_gateway_domain_name.custom.domain_name}/${aws_api_gateway_stage.v1.stage_name}"
}

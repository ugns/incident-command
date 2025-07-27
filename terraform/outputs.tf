output "launchdarkly_admin_access_flag_key" {
  description = "Key for the LaunchDarkly admin-access feature flag."
  value       = launchdarkly_feature_flag.admin_access.key
}

output "api_url" {
  description = "Base URL for the deployed API using the custom domain."
  value       = "https://${aws_api_gateway_domain_name.custom.domain_name}"
}

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

output "launchdarkly_super_admin_access_flag_key" {
  description = "Key for the LaunchDarkly super-admin-access feature flag."
  value       = launchdarkly_feature_flag.super_admin_access.key
}

output "launchdarkly_admin_access_flag_key" {
  description = "Key for the LaunchDarkly admin-access feature flag."
  value       = launchdarkly_feature_flag.admin_access.key
}

output "launchdarkly_show_radio_resources_flag_key" {
  description = "Key for the LaunchDarkly show-radio-resources feature flag."
  value       = launchdarkly_feature_flag.show_radio_resources.key
}

output "api_url" {
  description = "Base URL for the deployed API using the custom domain."
  value       = "https://${aws_api_gateway_domain_name.custom.domain_name}"
}

variable "launchdarkly_access_token" {
  description = "LaunchDarkly API access token for Terraform."
  type        = string
}


variable "gh_action_role" {
  description = "AWS IAM ARN for Terraform GitHub Actions"
  type        = string
}

variable "lambda_runtime" {
  description = "Runtime for Lambda functions"
  type        = string
  default     = "python3.13"
}

variable "domain_name" {
  description = "The root domain name (e.g., example.com) for Route53 lookup."
  type        = string
}

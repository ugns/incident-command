variable "gh_action_role" {
  description = "AWS IAM ARN for Terraform GitHub Actions"
  type        = string
}

variable "google_client_id" {
  description = "Google OAuth Client ID for frontend authentication"
  type        = string
  default     = null
}

variable "google_client_ids" {
  description = "Comma-delimited Google OAuth Client IDs for backend authentication"
  type        = string
  default     = null
}

variable "admin_emails" {
  description = "Comma-delimited list of admin emails for the application"
  type        = string
  default     = ""
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

variable "api_subdomain" {
  description = "The full API subdomain (e.g., api.example.com) for the custom domain."
  type        = string
}

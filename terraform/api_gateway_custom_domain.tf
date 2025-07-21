# Look up the Route53 hosted zone
# (Assumes var.domain_name is your root domain, e.g., example.com)
data "aws_route53_zone" "api" {
  name         = var.domain_name
  private_zone = false
}

# Look up the ACM certificate for the custom domain
# (Assumes var.api_subdomain is e.g., api.example.com)
data "aws_acm_certificate" "api" {
  domain      = var.domain_name
  statuses    = ["ISSUED"]
  types       = ["AMAZON_ISSUED"]
  most_recent = true
}

# API Gateway custom domain
resource "aws_api_gateway_domain_name" "custom" {
  domain_name              = var.api_subdomain
  regional_certificate_arn = data.aws_acm_certificate.api.arn
  endpoint_configuration {
    types = ["REGIONAL"]
  }
}

# Base path mapping for /v1 stage
resource "aws_api_gateway_base_path_mapping" "custom" {
  api_id      = aws_api_gateway_rest_api.incident_cmd.id
  stage_name  = "v1"
  domain_name = aws_api_gateway_domain_name.custom.domain_name
}

# Route53 record for the custom domain
resource "aws_route53_record" "api" {
  zone_id = data.aws_route53_zone.api.zone_id
  name    = var.api_subdomain
  type    = "A"
  alias {
    name                   = aws_api_gateway_domain_name.custom.regional_domain_name
    zone_id                = aws_api_gateway_domain_name.custom.regional_zone_id
    evaluate_target_health = false
  }
}

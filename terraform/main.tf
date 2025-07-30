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

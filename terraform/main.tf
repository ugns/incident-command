# Look up the Route53 hosted zone
data "aws_route53_zone" "api" {
  name         = var.domain_name
  private_zone = false
}

# Look up the ACM certificate for the custom domain
data "aws_acm_certificate" "api" {
  domain      = var.domain_name
  statuses    = ["ISSUED"]
  types       = ["AMAZON_ISSUED"]
  most_recent = true
}

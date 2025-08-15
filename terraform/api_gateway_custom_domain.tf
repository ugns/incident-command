# API Gateway custom domain
resource "aws_api_gateway_domain_name" "custom" {
  domain_name              = "api.${var.domain_name}"
  regional_certificate_arn = data.aws_acm_certificate.api.arn
  endpoint_configuration {
    types = ["REGIONAL"]
  }
}

# Base path mapping for /v1 stage
resource "aws_api_gateway_base_path_mapping" "custom" {
  api_id      = module.api.id
  stage_name  = var.stage_name
  domain_name = aws_api_gateway_domain_name.custom.domain_name
  # depends_on  = [aws_api_gateway_stage.v1]
}

# Route53 record for the custom domain
resource "aws_route53_record" "rest_api" {
  zone_id = data.aws_route53_zone.api.zone_id
  name    = aws_api_gateway_domain_name.custom.domain_name
  type    = "A"
  alias {
    name                   = aws_api_gateway_domain_name.custom.regional_domain_name
    zone_id                = aws_api_gateway_domain_name.custom.regional_zone_id
    evaluate_target_health = true
  }
}
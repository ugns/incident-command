# WebSocket and REST API custom domain using API Gateway v2

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

# API Gateway v2 custom domain
resource "aws_apigatewayv2_domain_name" "custom" {
  domain_name              = var.api_subdomain
  domain_name_configuration {
    certificate_arn = data.aws_acm_certificate.api.arn
    endpoint_type   = "REGIONAL"
    security_policy = "TLS_1_2"
  }
}

# Base path mapping for REST API (v1)
resource "aws_apigatewayv2_api_mapping" "rest" {
  api_id      = aws_api_gateway_rest_api.incident_cmd.id
  domain_name = aws_apigatewayv2_domain_name.custom.domain_name
  stage       = aws_api_gateway_stage.v1.stage_name
  api_mapping_key = "v1"
}

# Base path mapping for WebSocket API (ws)
resource "aws_apigatewayv2_api_mapping" "ws" {
  api_id      = aws_apigatewayv2_api.ws_api.id
  domain_name = aws_apigatewayv2_domain_name.custom.domain_name
  stage       = aws_apigatewayv2_stage.ws_api_stage.name
  api_mapping_key = "ws"
}

# Route53 record for the custom domain
resource "aws_route53_record" "api" {
  zone_id = data.aws_route53_zone.api.zone_id
  name    = var.api_subdomain
  type    = "A"
  alias {
    name                   = aws_apigatewayv2_domain_name.custom.domain_name_configuration[0].target_domain_name
    zone_id                = aws_apigatewayv2_domain_name.custom.domain_name_configuration[0].hosted_zone_id
    evaluate_target_health = true
  }
}

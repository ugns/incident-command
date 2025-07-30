# WebSocket and REST API custom domain using API Gateway v2

# API Gateway v2 custom domain
resource "aws_apigatewayv2_domain_name" "custom" {
  domain_name = "ws.${var.domain_name}"
  domain_name_configuration {
    certificate_arn = data.aws_acm_certificate.api.arn
    endpoint_type   = "REGIONAL"
    security_policy = "TLS_1_2"
  }
}

# Base path mapping for WebSocket API (ws)
resource "aws_apigatewayv2_api_mapping" "ws" {
  api_id          = aws_apigatewayv2_api.ws_api.id
  domain_name     = aws_apigatewayv2_domain_name.custom.domain_name
  stage           = aws_apigatewayv2_stage.ws_api_stage.name
  api_mapping_key = "ws"
}

# Route53 record for the custom domain
resource "aws_route53_record" "ws_api" {
  zone_id = data.aws_route53_zone.api.zone_id
  name    = aws_apigatewayv2_domain_name.custom.domain_name
  type    = "A"
  alias {
    name                   = aws_apigatewayv2_domain_name.custom.domain_name_configuration[0].target_domain_name
    zone_id                = aws_apigatewayv2_domain_name.custom.domain_name_configuration[0].hosted_zone_id
    evaluate_target_health = true
  }
}

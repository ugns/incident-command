# WebSocket Lambda Integrations
resource "aws_apigatewayv2_integration" "ws_connect" {
  api_id                 = aws_apigatewayv2_api.ws_api.id
  integration_type       = "AWS_PROXY"
  integration_uri        = module.ws_lambda["ws_connect"].invoke_arn
  integration_method     = "POST"
  payload_format_version = "1.0"
}

resource "aws_apigatewayv2_integration" "ws_disconnect" {
  api_id                 = aws_apigatewayv2_api.ws_api.id
  integration_type       = "AWS_PROXY"
  integration_uri        = module.ws_lambda["ws_disconnect"].invoke_arn
  integration_method     = "POST"
  payload_format_version = "1.0"
}

resource "aws_apigatewayv2_integration" "ws_default" {
  api_id                 = aws_apigatewayv2_api.ws_api.id
  integration_type       = "AWS_PROXY"
  integration_uri        = module.ws_lambda["ws_default"].invoke_arn
  integration_method     = "POST"
  payload_format_version = "1.0"
}

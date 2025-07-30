# Radios API Gateway integration

resource "aws_api_gateway_resource" "radios" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_rest_api.api.root_resource_id
  path_part   = "radios"
}

resource "aws_api_gateway_resource" "radios_id" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_resource.radios.id
  path_part   = "{radioId}"
}

locals {
  radios_methods = ["GET", "POST"]
  radios_id_methods = ["GET", "PUT", "DELETE"]
}

resource "aws_api_gateway_method" "radios_methods" {
  for_each    = toset(local.radios_methods)
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.radios.id
  http_method = each.key
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "radios_methods" {
  for_each    = toset(local.radios_methods)
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.radios.id
  http_method = each.key
  integration_http_method = "POST"
  type        = "AWS_PROXY"
  uri         = aws_lambda_function.radios.invoke_arn
}

resource "aws_api_gateway_method" "radios_id_methods" {
  for_each    = toset(local.radios_id_methods)
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.radios_id.id
  http_method = each.key
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "radios_id_methods" {
  for_each    = toset(local.radios_id_methods)
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.radios_id.id
  http_method = each.key
  integration_http_method = "POST"
  type        = "AWS_PROXY"
  uri         = aws_lambda_function.radios.invoke_arn
}

# CORS OPTIONS for /radios
resource "aws_api_gateway_method" "radios_options" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.radios.id
  http_method = "OPTIONS"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "radios_options" {
  depends_on  = [aws_api_gateway_method.radios_options]
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.radios.id
  http_method = aws_api_gateway_method.radios_options.http_method
  type        = "MOCK"
  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}
resource "aws_api_gateway_method_response" "radios_options" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.radios.id
  http_method = aws_api_gateway_method.radios_options.http_method
  status_code = "200"
  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = true
    "method.response.header.Access-Control-Allow-Methods" = true
    "method.response.header.Access-Control-Allow-Origin"  = true
  }
}
resource "aws_api_gateway_integration_response" "radios_options" {
  depends_on  = [aws_api_gateway_integration.radios_options]
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.radios.id
  http_method = aws_api_gateway_method.radios_options.http_method
  status_code = aws_api_gateway_method_response.radios_options.status_code
  response_templates = {
    "application/json" = ""
  }
  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,Authorization'"
    "method.response.header.Access-Control-Allow-Methods" = "'GET,POST,OPTIONS'"
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
  }
}

# CORS OPTIONS for /radios/{radioId}
resource "aws_api_gateway_method" "radios_id_options" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.radios_id.id
  http_method = "OPTIONS"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "radios_id_options" {
  depends_on  = [aws_api_gateway_method.radios_id_options]
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.radios_id.id
  http_method = aws_api_gateway_method.radios_id_options.http_method
  type        = "MOCK"
  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}
resource "aws_api_gateway_method_response" "radios_id_options" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.radios_id.id
  http_method = aws_api_gateway_method.radios_id_options.http_method
  status_code = "200"
  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = true
    "method.response.header.Access-Control-Allow-Methods" = true
    "method.response.header.Access-Control-Allow-Origin"  = true
  }
}
resource "aws_api_gateway_integration_response" "radios_id_options" {
  depends_on  = [aws_api_gateway_integration.radios_id_options]
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.radios_id.id
  http_method = aws_api_gateway_method.radios_id_options.http_method
  status_code = aws_api_gateway_method_response.radios_id_options.status_code
  response_templates = {
    "application/json" = ""
  }
  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,Authorization'"
    "method.response.header.Access-Control-Allow-Methods" = "'GET,PUT,DELETE,OPTIONS'"
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
  }
}

resource "aws_lambda_permission" "apigw_radios" {
  statement_id  = "AllowAPIGatewayInvokeRadios"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.radios.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.api.execution_arn}/*/*/radios*"
}

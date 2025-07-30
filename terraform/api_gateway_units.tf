# Units API Gateway integration

# /units resource
resource "aws_api_gateway_resource" "units" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_rest_api.api.root_resource_id
  path_part   = "units"
}

# /units/{unitId} resource
resource "aws_api_gateway_resource" "units_id" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_resource.units.id
  path_part   = "{unitId}"
}

# Methods for /units
locals {
  units_methods = ["GET", "POST"]
  units_id_methods = ["GET", "PUT", "DELETE"]
}

resource "aws_api_gateway_method" "units_methods" {
  for_each    = toset(local.units_methods)
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.units.id
  http_method = each.key
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "units_methods" {
  for_each    = toset(local.units_methods)
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.units.id
  http_method = each.key
  integration_http_method = "POST"
  type        = "AWS_PROXY"
  uri         = aws_lambda_function.units.invoke_arn
}

resource "aws_api_gateway_method" "units_id_methods" {
  for_each    = toset(local.units_id_methods)
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.units_id.id
  http_method = each.key
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "units_id_methods" {
  for_each    = toset(local.units_id_methods)
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.units_id.id
  http_method = each.key
  integration_http_method = "POST"
  type        = "AWS_PROXY"
  uri         = aws_lambda_function.units.invoke_arn
}

# CORS OPTIONS for /units
resource "aws_api_gateway_method" "units_options" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.units.id
  http_method = "OPTIONS"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "units_options" {
  depends_on  = [aws_api_gateway_method.units_options]
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.units.id
  http_method = aws_api_gateway_method.units_options.http_method
  type        = "MOCK"
  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}
resource "aws_api_gateway_method_response" "units_options" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.units.id
  http_method = aws_api_gateway_method.units_options.http_method
  status_code = "200"
  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = true
    "method.response.header.Access-Control-Allow-Methods" = true
    "method.response.header.Access-Control-Allow-Origin"  = true
  }
}
resource "aws_api_gateway_integration_response" "units_options" {
  depends_on  = [aws_api_gateway_integration.units_options]
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.units.id
  http_method = aws_api_gateway_method.units_options.http_method
  status_code = aws_api_gateway_method_response.units_options.status_code
  response_templates = {
    "application/json" = ""
  }
  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,Authorization'"
    "method.response.header.Access-Control-Allow-Methods" = "'GET,POST,OPTIONS'"
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
  }
}

# CORS OPTIONS for /units/{unitId}
resource "aws_api_gateway_method" "units_id_options" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.units_id.id
  http_method = "OPTIONS"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "units_id_options" {
  depends_on  = [aws_api_gateway_method.units_id_options]
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.units_id.id
  http_method = aws_api_gateway_method.units_id_options.http_method
  type        = "MOCK"
  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}
resource "aws_api_gateway_method_response" "units_id_options" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.units_id.id
  http_method = aws_api_gateway_method.units_id_options.http_method
  status_code = "200"
  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = true
    "method.response.header.Access-Control-Allow-Methods" = true
    "method.response.header.Access-Control-Allow-Origin"  = true
  }
}
resource "aws_api_gateway_integration_response" "units_id_options" {
  depends_on  = [aws_api_gateway_integration.units_id_options]
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.units_id.id
  http_method = aws_api_gateway_method.units_id_options.http_method
  status_code = aws_api_gateway_method_response.units_id_options.status_code
  response_templates = {
    "application/json" = ""
  }
  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,Authorization'"
    "method.response.header.Access-Control-Allow-Methods" = "'GET,PUT,DELETE,OPTIONS'"
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
  }
}

# Lambda permission for API Gateway to invoke Units Lambda
resource "aws_lambda_permission" "apigw_units" {
  statement_id  = "AllowAPIGatewayInvokeUnits"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.units.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.api.execution_arn}/*/*/units*"
}

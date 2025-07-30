# Locations API Gateway integration

resource "aws_api_gateway_resource" "locations" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_rest_api.api.root_resource_id
  path_part   = "locations"
}

resource "aws_api_gateway_resource" "locations_id" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_resource.locations.id
  path_part   = "{locationId}"
}

locals {
  locations_methods = ["GET", "POST"]
  locations_id_methods = ["GET", "PUT", "DELETE"]
}

resource "aws_api_gateway_method" "locations_methods" {
  for_each    = toset(local.locations_methods)
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.locations.id
  http_method = each.key
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "locations_methods" {
  for_each    = toset(local.locations_methods)
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.locations.id
  http_method = each.key
  integration_http_method = "POST"
  type        = "AWS_PROXY"
  uri         = aws_lambda_function.locations.invoke_arn
}

resource "aws_api_gateway_method" "locations_id_methods" {
  for_each    = toset(local.locations_id_methods)
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.locations_id.id
  http_method = each.key
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "locations_id_methods" {
  for_each    = toset(local.locations_id_methods)
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.locations_id.id
  http_method = each.key
  integration_http_method = "POST"
  type        = "AWS_PROXY"
  uri         = aws_lambda_function.locations.invoke_arn
}

# CORS OPTIONS for /locations
resource "aws_api_gateway_method" "locations_options" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.locations.id
  http_method = "OPTIONS"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "locations_options" {
  depends_on  = [aws_api_gateway_method.locations_options]
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.locations.id
  http_method = aws_api_gateway_method.locations_options.http_method
  type        = "MOCK"
  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}
resource "aws_api_gateway_method_response" "locations_options" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.locations.id
  http_method = aws_api_gateway_method.locations_options.http_method
  status_code = "200"
  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = true
    "method.response.header.Access-Control-Allow-Methods" = true
    "method.response.header.Access-Control-Allow-Origin"  = true
  }
}
resource "aws_api_gateway_integration_response" "locations_options" {
  depends_on  = [aws_api_gateway_integration.locations_options]
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.locations.id
  http_method = aws_api_gateway_method.locations_options.http_method
  status_code = aws_api_gateway_method_response.locations_options.status_code
  response_templates = {
    "application/json" = ""
  }
  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,Authorization'"
    "method.response.header.Access-Control-Allow-Methods" = "'GET,POST,OPTIONS'"
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
  }
}

# CORS OPTIONS for /locations/{locationId}
resource "aws_api_gateway_method" "locations_id_options" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.locations_id.id
  http_method = "OPTIONS"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "locations_id_options" {
  depends_on  = [aws_api_gateway_method.locations_id_options]
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.locations_id.id
  http_method = aws_api_gateway_method.locations_id_options.http_method
  type        = "MOCK"
  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}
resource "aws_api_gateway_method_response" "locations_id_options" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.locations_id.id
  http_method = aws_api_gateway_method.locations_id_options.http_method
  status_code = "200"
  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = true
    "method.response.header.Access-Control-Allow-Methods" = true
    "method.response.header.Access-Control-Allow-Origin"  = true
  }
}
resource "aws_api_gateway_integration_response" "locations_id_options" {
  depends_on  = [aws_api_gateway_integration.locations_id_options]
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.locations_id.id
  http_method = aws_api_gateway_method.locations_id_options.http_method
  status_code = aws_api_gateway_method_response.locations_id_options.status_code
  response_templates = {
    "application/json" = ""
  }
  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,Authorization'"
    "method.response.header.Access-Control-Allow-Methods" = "'GET,PUT,DELETE,OPTIONS'"
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
  }
}

resource "aws_lambda_permission" "apigw_locations" {
  statement_id  = "AllowAPIGatewayInvokeLocations"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.locations.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.api.execution_arn}/*/*/locations*"
}

# Incidents API Gateway integration

# /incidents resource
resource "aws_api_gateway_resource" "incidents" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_rest_api.api.root_resource_id
  path_part   = "incidents"
}

# /incidents/{incidentId} resource
resource "aws_api_gateway_resource" "incidents_id" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_resource.incidents.id
  path_part   = "{incidentId}"
}

# Methods for /incidents
locals {
  incidents_methods = ["GET", "POST"]
  incidents_id_methods = ["GET", "PUT", "DELETE"]
}

resource "aws_api_gateway_method" "incidents_methods" {
  for_each    = toset(local.incidents_methods)
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.incidents.id
  http_method = each.key
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "incidents_methods" {
  for_each    = toset(local.incidents_methods)
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.incidents.id
  http_method = each.key
  integration_http_method = "POST"
  type        = "AWS_PROXY"
  uri         = aws_lambda_function.incidents.invoke_arn
}

resource "aws_api_gateway_method" "incidents_id_methods" {
  for_each    = toset(local.incidents_id_methods)
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.incidents_id.id
  http_method = each.key
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "incidents_id_methods" {
  for_each    = toset(local.incidents_id_methods)
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.incidents_id.id
  http_method = each.key
  integration_http_method = "POST"
  type        = "AWS_PROXY"
  uri         = aws_lambda_function.incidents.invoke_arn
}

# CORS OPTIONS for /incidents
resource "aws_api_gateway_method" "incidents_options" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.incidents.id
  http_method = "OPTIONS"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "incidents_options" {
  depends_on  = [aws_api_gateway_method.incidents_options]
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.incidents.id
  http_method = aws_api_gateway_method.incidents_options.http_method
  type        = "MOCK"
  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}
resource "aws_api_gateway_method_response" "incidents_options" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.incidents.id
  http_method = aws_api_gateway_method.incidents_options.http_method
  status_code = "200"
  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = true
    "method.response.header.Access-Control-Allow-Methods" = true
    "method.response.header.Access-Control-Allow-Origin"  = true
  }
}
resource "aws_api_gateway_integration_response" "incidents_options" {
  depends_on  = [aws_api_gateway_integration.incidents_options]
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.incidents.id
  http_method = aws_api_gateway_method.incidents_options.http_method
  status_code = aws_api_gateway_method_response.incidents_options.status_code
  response_templates = {
    "application/json" = ""
  }
  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,Authorization'"
    "method.response.header.Access-Control-Allow-Methods" = "'GET,POST,OPTIONS'"
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
  }
}

# CORS OPTIONS for /incidents/{incidentId}
resource "aws_api_gateway_method" "incidents_id_options" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.incidents_id.id
  http_method = "OPTIONS"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "incidents_id_options" {
  depends_on  = [aws_api_gateway_method.incidents_id_options]
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.incidents_id.id
  http_method = aws_api_gateway_method.incidents_id_options.http_method
  type        = "MOCK"
  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}
resource "aws_api_gateway_method_response" "incidents_id_options" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.incidents_id.id
  http_method = aws_api_gateway_method.incidents_id_options.http_method
  status_code = "200"
  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = true
    "method.response.header.Access-Control-Allow-Methods" = true
    "method.response.header.Access-Control-Allow-Origin"  = true
  }
}
resource "aws_api_gateway_integration_response" "incidents_id_options" {
  depends_on  = [aws_api_gateway_integration.incidents_id_options]
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.incidents_id.id
  http_method = aws_api_gateway_method.incidents_id_options.http_method
  status_code = aws_api_gateway_method_response.incidents_id_options.status_code
  response_templates = {
    "application/json" = ""
  }
  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,Authorization'"
    "method.response.header.Access-Control-Allow-Methods" = "'GET,PUT,DELETE,OPTIONS'"
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
  }
}

# Lambda permission for API Gateway to invoke Incidents Lambda
resource "aws_lambda_permission" "apigw_incidents" {
  statement_id  = "AllowAPIGatewayInvokeIncidents"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.incidents.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.api.execution_arn}/*/*/incidents*"
}

# Auth API Gateway resource and methods

# /auth resource
resource "aws_api_gateway_resource" "auth" {
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  parent_id   = data.aws_api_gateway_resource.root.id
  path_part   = "auth"
}

# /auth/login resource
resource "aws_api_gateway_resource" "auth_login" {
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  parent_id   = aws_api_gateway_resource.auth.id
  path_part   = "login"
}

# /.well-known resource
resource "aws_api_gateway_resource" "auth_well_known" {
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  parent_id   = data.aws_api_gateway_resource.root.id
  path_part   = ".well-known"
}

# /.well-known/jwks.json resource
resource "aws_api_gateway_resource" "auth_jwks_json" {
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  parent_id   = aws_api_gateway_resource.auth_well_known.id
  path_part   = "jwks.json"
}

# GET /.well-known/jwks.json
resource "aws_api_gateway_method" "auth_jwks_json_get" {
  rest_api_id   = aws_api_gateway_rest_api.incident_cmd.id
  resource_id   = aws_api_gateway_resource.auth_jwks_json.id
  http_method   = "GET"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "auth_jwks_json_get" {
  depends_on              = [aws_api_gateway_method.auth_jwks_json_get]
  rest_api_id             = aws_api_gateway_rest_api.incident_cmd.id
  resource_id             = aws_api_gateway_resource.auth_jwks_json.id
  http_method             = aws_api_gateway_method.auth_jwks_json_get.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.jwks.invoke_arn
}
resource "aws_lambda_permission" "apigw_jwks" {
  statement_id  = "AllowAPIGatewayInvokeJWKS"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.jwks.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.incident_cmd.execution_arn}/*/GET/.well-known/jwks.json"
}

# POST /auth/login
resource "aws_api_gateway_method" "auth_login_post" {
  rest_api_id   = aws_api_gateway_rest_api.incident_cmd.id
  resource_id   = aws_api_gateway_resource.auth_login.id
  http_method   = "POST"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "auth_login_post" {
  depends_on              = [aws_api_gateway_method.auth_login_post]
  rest_api_id             = aws_api_gateway_rest_api.incident_cmd.id
  resource_id             = aws_api_gateway_resource.auth_login.id
  http_method             = aws_api_gateway_method.auth_login_post.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.auth_callback.invoke_arn
}
resource "aws_lambda_permission" "apigw_auth_callback" {
  statement_id  = "AllowAPIGatewayInvokeAuthCallback"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.auth_callback.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.incident_cmd.execution_arn}/*/POST/auth/login"
}

# CORS OPTIONS for /.well-known/jwks.json
resource "aws_api_gateway_method" "auth_jwks_json_options" {
  rest_api_id   = aws_api_gateway_rest_api.incident_cmd.id
  resource_id   = aws_api_gateway_resource.auth_jwks_json.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "auth_jwks_json_options" {
  depends_on  = [aws_api_gateway_method.auth_jwks_json_options]
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  resource_id = aws_api_gateway_resource.auth_jwks_json.id
  http_method = aws_api_gateway_method.auth_jwks_json_options.http_method
  type        = "MOCK"
  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}
resource "aws_api_gateway_method_response" "auth_jwks_json_options" {
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  resource_id = aws_api_gateway_resource.auth_jwks_json.id
  http_method = aws_api_gateway_method.auth_jwks_json_options.http_method
  status_code = "200"
  response_models = {
    "application/json" = "Empty"
  }
  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = true
    "method.response.header.Access-Control-Allow-Methods" = true
    "method.response.header.Access-Control-Allow-Origin"  = true
  }
}
resource "aws_api_gateway_integration_response" "auth_jwks_json_options" {
  depends_on  = [aws_api_gateway_integration.auth_jwks_json_options]
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  resource_id = aws_api_gateway_resource.auth_jwks_json.id
  http_method = aws_api_gateway_method.auth_jwks_json_options.http_method
  status_code = "200"
  response_templates = {
    "application/json" = ""
  }
  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,Authorization'"
    "method.response.header.Access-Control-Allow-Methods" = "'GET,OPTIONS'"
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
  }
}

# CORS OPTIONS for /auth/login
resource "aws_api_gateway_method" "auth_login_options" {
  rest_api_id   = aws_api_gateway_rest_api.incident_cmd.id
  resource_id   = aws_api_gateway_resource.auth_login.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "auth_login_options" {
  depends_on  = [aws_api_gateway_method.auth_login_options]
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  resource_id = aws_api_gateway_resource.auth_login.id
  http_method = aws_api_gateway_method.auth_login_options.http_method
  type        = "MOCK"
  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}
resource "aws_api_gateway_method_response" "auth_login_options" {
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  resource_id = aws_api_gateway_resource.auth_login.id
  http_method = aws_api_gateway_method.auth_login_options.http_method
  status_code = "200"
  response_models = {
    "application/json" = "Empty"
  }
  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = true
    "method.response.header.Access-Control-Allow-Methods" = true
    "method.response.header.Access-Control-Allow-Origin"  = true
  }
}
resource "aws_api_gateway_integration_response" "auth_login_options" {
  depends_on  = [aws_api_gateway_integration.auth_login_options]
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  resource_id = aws_api_gateway_resource.auth_login.id
  http_method = aws_api_gateway_method.auth_login_options.http_method
  status_code = "200"
  response_templates = {
    "application/json" = ""
  }
  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,Authorization'"
    "method.response.header.Access-Control-Allow-Methods" = "'POST,OPTIONS'"
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
  }
}

locals {
  auth_integrations = [
    aws_api_gateway_integration.auth_login_post,
    aws_api_gateway_integration.auth_login_options,
    aws_api_gateway_integration.auth_jwks_json_options,
    aws_api_gateway_integration.auth_jwks_json_get,
  ]
}

# Activity Logs API Gateway resources and methods

# /activitylogs resource
resource "aws_api_gateway_resource" "activitylogs" {
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  parent_id   = data.aws_api_gateway_resource.root.id
  path_part   = "activitylogs"
}

# /activitylogs/{volunteerId} resource
resource "aws_api_gateway_resource" "activitylogs_id" {
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  parent_id   = aws_api_gateway_resource.activitylogs.id
  path_part   = "{volunteerId}"
}

# GET /activitylogs
resource "aws_api_gateway_method" "activitylogs_get" {
  rest_api_id   = aws_api_gateway_rest_api.incident_cmd.id
  resource_id   = aws_api_gateway_resource.activitylogs.id
  http_method   = "GET"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "activitylogs_get" {
  depends_on              = [aws_api_gateway_method.activitylogs_get]
  rest_api_id             = aws_api_gateway_rest_api.incident_cmd.id
  resource_id             = aws_api_gateway_resource.activitylogs.id
  http_method             = aws_api_gateway_method.activitylogs_get.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.activitylogs.invoke_arn
}
resource "aws_lambda_permission" "apigw_activitylogs_get" {
  statement_id  = "AllowAPIGatewayInvokeActivityLogsGet"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.activitylogs.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.incident_cmd.execution_arn}/*/GET/activitylogs"
}

# GET /activitylogs/{volunteerId}
resource "aws_api_gateway_method" "activitylogs_id_get" {
  rest_api_id   = aws_api_gateway_rest_api.incident_cmd.id
  resource_id   = aws_api_gateway_resource.activitylogs_id.id
  http_method   = "GET"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "activitylogs_id_get" {
  depends_on              = [aws_api_gateway_method.activitylogs_id_get]
  rest_api_id             = aws_api_gateway_rest_api.incident_cmd.id
  resource_id             = aws_api_gateway_resource.activitylogs_id.id
  http_method             = aws_api_gateway_method.activitylogs_id_get.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.activitylogs.invoke_arn
}
resource "aws_lambda_permission" "apigw_activitylogs_id_get" {
  statement_id  = "AllowAPIGatewayInvokeActivityLogsGetId"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.activitylogs.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.incident_cmd.execution_arn}/*/GET/activitylogs/*"
}

# CORS OPTIONS for /activitylogs
resource "aws_api_gateway_method" "activitylogs_options" {
  rest_api_id   = aws_api_gateway_rest_api.incident_cmd.id
  resource_id   = aws_api_gateway_resource.activitylogs.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "activitylogs_options" {
  depends_on  = [aws_api_gateway_method.activitylogs_options]
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  resource_id = aws_api_gateway_resource.activitylogs.id
  http_method = aws_api_gateway_method.activitylogs_options.http_method
  type        = "MOCK"
  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}
resource "aws_api_gateway_method_response" "activitylogs_options" {
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  resource_id = aws_api_gateway_resource.activitylogs.id
  http_method = aws_api_gateway_method.activitylogs_options.http_method
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
resource "aws_api_gateway_integration_response" "activitylogs_options" {
  depends_on  = [aws_api_gateway_integration.activitylogs_options]
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  resource_id = aws_api_gateway_resource.activitylogs.id
  http_method = aws_api_gateway_method.activitylogs_options.http_method
  status_code = aws_api_gateway_method_response.activitylogs_options.status_code
  response_templates = {
    "application/json" = ""
  }
  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"
    "method.response.header.Access-Control-Allow-Methods" = "'GET,POST,OPTIONS'"
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
  }
}
# CORS OPTIONS for /activitylogs/{volunteerId}
resource "aws_api_gateway_method" "activitylogs_id_options" {
  rest_api_id   = aws_api_gateway_rest_api.incident_cmd.id
  resource_id   = aws_api_gateway_resource.activitylogs_id.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "activitylogs_id_options" {
  depends_on  = [aws_api_gateway_method.activitylogs_id_options]
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  resource_id = aws_api_gateway_resource.activitylogs_id.id
  http_method = aws_api_gateway_method.activitylogs_id_options.http_method
  type        = "MOCK"
  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}
resource "aws_api_gateway_method_response" "activitylogs_id_options" {
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  resource_id = aws_api_gateway_resource.activitylogs_id.id
  http_method = aws_api_gateway_method.activitylogs_id_options.http_method
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
resource "aws_api_gateway_integration_response" "activitylogs_id_options" {
  depends_on  = [aws_api_gateway_integration.activitylogs_id_options]
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  resource_id = aws_api_gateway_resource.activitylogs_id.id
  http_method = aws_api_gateway_method.activitylogs_id_options.http_method
  status_code = aws_api_gateway_method_response.activitylogs_id_options.status_code
  response_templates = {
    "application/json" = ""
  }
  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"
    "method.response.header.Access-Control-Allow-Methods" = "'GET,OPTIONS'"
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
  }
}

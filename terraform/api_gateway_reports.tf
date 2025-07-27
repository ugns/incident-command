# Reports API Gateway resources and methods

# /reports resource
resource "aws_api_gateway_resource" "reports" {
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  parent_id   = data.aws_api_gateway_resource.root.id
  path_part   = "reports"
}

# /reports/{reportType} resource
resource "aws_api_gateway_resource" "report_type" {
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  parent_id   = aws_api_gateway_resource.reports.id
  path_part   = "{reportType}"
}

# GET /reports
resource "aws_api_gateway_method" "reports_get" {
  rest_api_id   = aws_api_gateway_rest_api.incident_cmd.id
  resource_id   = aws_api_gateway_resource.reports.id
  http_method   = "GET"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "reports_get" {
  depends_on              = [aws_api_gateway_method.reports_get]
  rest_api_id             = aws_api_gateway_rest_api.incident_cmd.id
  resource_id             = aws_api_gateway_resource.reports.id
  http_method             = aws_api_gateway_method.reports_get.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.reports.invoke_arn
}
resource "aws_lambda_permission" "apigw_reports_get" {
  statement_id  = "AllowAPIGatewayInvokeReportsGet"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.reports.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.incident_cmd.execution_arn}/*/GET/reports"
}

# POST /reports/{reportType}
resource "aws_api_gateway_method" "report_type_post" {
  rest_api_id   = aws_api_gateway_rest_api.incident_cmd.id
  resource_id   = aws_api_gateway_resource.report_type.id
  http_method   = "POST"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "report_type_post" {
  depends_on              = [aws_api_gateway_method.report_type_post]
  rest_api_id             = aws_api_gateway_rest_api.incident_cmd.id
  resource_id             = aws_api_gateway_resource.report_type.id
  http_method             = aws_api_gateway_method.report_type_post.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.reports.invoke_arn
}
resource "aws_lambda_permission" "apigw_reports_post" {
  statement_id  = "AllowAPIGatewayInvokeReportsPost"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.reports.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.incident_cmd.execution_arn}/*/POST/reports/*"
}

# CORS OPTIONS for /reports
resource "aws_api_gateway_method" "reports_options" {
  rest_api_id   = aws_api_gateway_rest_api.incident_cmd.id
  resource_id   = aws_api_gateway_resource.reports.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "reports_options" {
  depends_on  = [aws_api_gateway_method.reports_options]
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  resource_id = aws_api_gateway_resource.reports.id
  http_method = aws_api_gateway_method.reports_options.http_method
  type        = "MOCK"
  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}
resource "aws_api_gateway_method_response" "reports_options" {
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  resource_id = aws_api_gateway_resource.reports.id
  http_method = aws_api_gateway_method.reports_options.http_method
  status_code = "200"
  response_models = {
    "application/json" = "Empty"
  }
  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin"  = true,
    "method.response.header.Access-Control-Allow-Headers" = true,
    "method.response.header.Access-Control-Allow-Methods" = true
  }
}
resource "aws_api_gateway_integration_response" "reports_options" {
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  resource_id = aws_api_gateway_resource.reports.id
  http_method = aws_api_gateway_method.reports_options.http_method
  status_code = "200"
  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin"  = "'*'",
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,Authorization'",
    "method.response.header.Access-Control-Allow-Methods" = "'GET,OPTIONS'"
  }
  response_templates = {
    "application/json" = ""
  }
}

# CORS OPTIONS for /reports/{reportType}
resource "aws_api_gateway_method" "report_type_options" {
  rest_api_id   = aws_api_gateway_rest_api.incident_cmd.id
  resource_id   = aws_api_gateway_resource.report_type.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "report_type_options" {
  depends_on  = [aws_api_gateway_method.report_type_options]
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  resource_id = aws_api_gateway_resource.report_type.id
  http_method = aws_api_gateway_method.report_type_options.http_method
  type        = "MOCK"
  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}
resource "aws_api_gateway_method_response" "report_type_options" {
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  resource_id = aws_api_gateway_resource.report_type.id
  http_method = aws_api_gateway_method.report_type_options.http_method
  status_code = "200"
  response_models = {
    "application/json" = "Empty"
  }
  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin"   = true,
    "method.response.header.Access-Control-Allow-Headers"  = true,
    "method.response.header.Access-Control-Allow-Methods"  = true,
    "method.response.header.Access-Control-Expose-Headers" = true,
  }
}
resource "aws_api_gateway_integration_response" "report_type_options" {
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  resource_id = aws_api_gateway_resource.report_type.id
  http_method = aws_api_gateway_method.report_type_options.http_method
  status_code = "200"
  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin"   = "'*'",
    "method.response.header.Access-Control-Allow-Headers"  = "'Content-Type,Authorization'",
    "method.response.header.Access-Control-Allow-Methods"  = "'POST,OPTIONS'",
    "method.response.header.Access-Control-Expose-Headers" = "'Content-Disposition'"
  }
  response_templates = {
    "application/json" = ""
  }
}

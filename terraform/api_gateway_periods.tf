# Periods API Gateway resources and methods

# /periods resource
resource "aws_api_gateway_resource" "periods_list" {
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  parent_id   = data.aws_api_gateway_resource.root.id
  path_part   = "periods"
}

# /periods/{periodId} resource
resource "aws_api_gateway_resource" "period_id" {
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  parent_id   = aws_api_gateway_resource.periods_list.id
  path_part   = "{periodId}"
}

# GET /periods
resource "aws_api_gateway_method" "periods_get" {
  rest_api_id   = aws_api_gateway_rest_api.incident_cmd.id
  resource_id   = aws_api_gateway_resource.periods_list.id
  http_method   = "GET"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "periods_get" {
  depends_on              = [aws_api_gateway_method.periods_get]
  rest_api_id             = aws_api_gateway_rest_api.incident_cmd.id
  resource_id             = aws_api_gateway_resource.periods_list.id
  http_method             = aws_api_gateway_method.periods_get.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.periods.invoke_arn
}
resource "aws_lambda_permission" "apigw_periods_get" {
  statement_id  = "AllowAPIGatewayInvokePeriodsGet"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.periods.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.incident_cmd.execution_arn}/*/GET/periods"
}

# POST /periods
resource "aws_api_gateway_method" "periods_post" {
  rest_api_id   = aws_api_gateway_rest_api.incident_cmd.id
  resource_id   = aws_api_gateway_resource.periods_list.id
  http_method   = "POST"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "periods_post" {
  depends_on              = [aws_api_gateway_method.periods_post]
  rest_api_id             = aws_api_gateway_rest_api.incident_cmd.id
  resource_id             = aws_api_gateway_resource.periods_list.id
  http_method             = aws_api_gateway_method.periods_post.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.periods.invoke_arn
}
resource "aws_lambda_permission" "apigw_periods_post" {
  statement_id  = "AllowAPIGatewayInvokePeriodsPost"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.periods.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.incident_cmd.execution_arn}/*/POST/periods"
}

# PUT /periods/{periodId}
resource "aws_api_gateway_method" "period_id_put" {
  rest_api_id   = aws_api_gateway_rest_api.incident_cmd.id
  resource_id   = aws_api_gateway_resource.period_id.id
  http_method   = "PUT"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "period_id_put" {
  depends_on              = [aws_api_gateway_method.period_id_put]
  rest_api_id             = aws_api_gateway_rest_api.incident_cmd.id
  resource_id             = aws_api_gateway_resource.period_id.id
  http_method             = aws_api_gateway_method.period_id_put.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.periods.invoke_arn
}
resource "aws_lambda_permission" "apigw_period_id_put" {
  statement_id  = "AllowAPIGatewayInvokePeriodIdPut"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.periods.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.incident_cmd.execution_arn}/*/PUT/periods/*"
}

# DELETE /periods/{periodId}
resource "aws_api_gateway_method" "period_id_delete" {
  rest_api_id   = aws_api_gateway_rest_api.incident_cmd.id
  resource_id   = aws_api_gateway_resource.period_id.id
  http_method   = "DELETE"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "period_id_delete" {
  depends_on              = [aws_api_gateway_method.period_id_delete]
  rest_api_id             = aws_api_gateway_rest_api.incident_cmd.id
  resource_id             = aws_api_gateway_resource.period_id.id
  http_method             = aws_api_gateway_method.period_id_delete.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.periods.invoke_arn
}
resource "aws_lambda_permission" "apigw_period_id_delete" {
  statement_id  = "AllowAPIGatewayInvokePeriodIdDelete"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.periods.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.incident_cmd.execution_arn}/*/DELETE/periods/*"
}

# GET /periods/{periodId}
resource "aws_api_gateway_method" "period_id_get" {
  rest_api_id   = aws_api_gateway_rest_api.incident_cmd.id
  resource_id   = aws_api_gateway_resource.period_id.id
  http_method   = "GET"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "period_id_get" {
  depends_on              = [aws_api_gateway_method.period_id_get]
  rest_api_id             = aws_api_gateway_rest_api.incident_cmd.id
  resource_id             = aws_api_gateway_resource.period_id.id
  http_method             = aws_api_gateway_method.period_id_get.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.periods.invoke_arn
}
resource "aws_lambda_permission" "apigw_period_id_get" {
  statement_id  = "AllowAPIGatewayInvokePeriodIdGet"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.periods.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.incident_cmd.execution_arn}/*/GET/periods/*"
}

# CORS OPTIONS for /periods
resource "aws_api_gateway_method" "periods_options" {
  rest_api_id   = aws_api_gateway_rest_api.incident_cmd.id
  resource_id   = aws_api_gateway_resource.periods_list.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "periods_options" {
  depends_on  = [aws_api_gateway_method.periods_options]
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  resource_id = aws_api_gateway_resource.periods_list.id
  http_method = aws_api_gateway_method.periods_options.http_method
  type        = "MOCK"
  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}
resource "aws_api_gateway_method_response" "periods_options" {
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  resource_id = aws_api_gateway_resource.periods_list.id
  http_method = aws_api_gateway_method.periods_options.http_method
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
resource "aws_api_gateway_integration_response" "periods_options" {
  depends_on  = [aws_api_gateway_integration.periods_options]
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  resource_id = aws_api_gateway_resource.periods_list.id
  http_method = aws_api_gateway_method.periods_options.http_method
  status_code = aws_api_gateway_method_response.periods_options.status_code
  response_templates = {
    "application/json" = ""
  }
  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"
    "method.response.header.Access-Control-Allow-Methods" = "'GET,POST,OPTIONS'"
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
  }
}

# CORS OPTIONS for /periods/{periodId}
resource "aws_api_gateway_method" "period_id_options" {
  rest_api_id   = aws_api_gateway_rest_api.incident_cmd.id
  resource_id   = aws_api_gateway_resource.period_id.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "period_id_options" {
  depends_on  = [aws_api_gateway_method.period_id_options]
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  resource_id = aws_api_gateway_resource.period_id.id
  http_method = aws_api_gateway_method.period_id_options.http_method
  type        = "MOCK"
  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}
resource "aws_api_gateway_method_response" "period_id_options" {
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  resource_id = aws_api_gateway_resource.period_id.id
  http_method = aws_api_gateway_method.period_id_options.http_method
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
resource "aws_api_gateway_integration_response" "period_id_options" {
  depends_on  = [aws_api_gateway_integration.period_id_options]
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  resource_id = aws_api_gateway_resource.period_id.id
  http_method = aws_api_gateway_method.period_id_options.http_method
  status_code = aws_api_gateway_method_response.period_id_options.status_code
  response_templates = {
    "application/json" = ""
  }
  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"
    "method.response.header.Access-Control-Allow-Methods" = "'GET,PUT,DELETE,OPTIONS'"
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
  }
}

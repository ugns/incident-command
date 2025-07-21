# ICS-214 API Gateway resources and methods

# /ics214 resource
resource "aws_api_gateway_resource" "ics214" {
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  parent_id   = data.aws_api_gateway_resource.root.id
  path_part   = "ics214"
}

# /ics214/periods resource
resource "aws_api_gateway_resource" "ics214_periods_list" {
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  parent_id   = aws_api_gateway_resource.ics214.id
  path_part   = "periods"
}

# /ics214/periods/{periodId} resource
resource "aws_api_gateway_resource" "ics214_period_id" {
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  parent_id   = aws_api_gateway_resource.ics214_periods_list.id
  path_part   = "{periodId}"
}

# POST /ics214/periods
resource "aws_api_gateway_method" "ics214_periods_post" {
  rest_api_id   = aws_api_gateway_rest_api.incident_cmd.id
  resource_id   = aws_api_gateway_resource.ics214_periods_list.id
  http_method   = "POST"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "ics214_periods_post" {
  depends_on = [aws_api_gateway_method.ics214_periods_post]
  rest_api_id             = aws_api_gateway_rest_api.incident_cmd.id
  resource_id             = aws_api_gateway_resource.ics214_periods_list.id
  http_method             = aws_api_gateway_method.ics214_periods_post.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.ics214.invoke_arn
}
resource "aws_lambda_permission" "apigw_ics214_periods_post" {
  statement_id  = "AllowAPIGatewayInvokeIcs214PeriodsPost"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.ics214.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.incident_cmd.execution_arn}/*/POST/ics214/periods"
}

# PUT /ics214/periods/{periodId}
resource "aws_api_gateway_method" "ics214_period_id_put" {
  rest_api_id   = aws_api_gateway_rest_api.incident_cmd.id
  resource_id   = aws_api_gateway_resource.ics214_period_id.id
  http_method   = "PUT"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "ics214_period_id_put" {
  depends_on = [aws_api_gateway_method.ics214_period_id_put]
  rest_api_id             = aws_api_gateway_rest_api.incident_cmd.id
  resource_id             = aws_api_gateway_resource.ics214_period_id.id
  http_method             = aws_api_gateway_method.ics214_period_id_put.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.ics214.invoke_arn
}
resource "aws_lambda_permission" "apigw_ics214_period_id_put" {
  statement_id  = "AllowAPIGatewayInvokeIcs214PeriodIdPut"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.ics214.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.incident_cmd.execution_arn}/*/PUT/ics214/periods/*"
}

# DELETE /ics214/periods/{periodId}
resource "aws_api_gateway_method" "ics214_period_id_delete" {
  rest_api_id   = aws_api_gateway_rest_api.incident_cmd.id
  resource_id   = aws_api_gateway_resource.ics214_period_id.id
  http_method   = "DELETE"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "ics214_period_id_delete" {
  depends_on = [aws_api_gateway_method.ics214_period_id_delete]
  rest_api_id             = aws_api_gateway_rest_api.incident_cmd.id
  resource_id             = aws_api_gateway_resource.ics214_period_id.id
  http_method             = aws_api_gateway_method.ics214_period_id_delete.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.ics214.invoke_arn
}
resource "aws_lambda_permission" "apigw_ics214_period_id_delete" {
  statement_id  = "AllowAPIGatewayInvokeIcs214PeriodIdDelete"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.ics214.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.incident_cmd.execution_arn}/*/DELETE/ics214/periods/*"
}

# GET /ics214/periods
resource "aws_api_gateway_method" "ics214_periods_get" {
  rest_api_id   = aws_api_gateway_rest_api.incident_cmd.id
  resource_id   = aws_api_gateway_resource.ics214_periods_list.id
  http_method   = "GET"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "ics214_periods_get" {
  depends_on = [aws_api_gateway_method.ics214_periods_get]
  rest_api_id             = aws_api_gateway_rest_api.incident_cmd.id
  resource_id             = aws_api_gateway_resource.ics214_periods_list.id
  http_method             = aws_api_gateway_method.ics214_periods_get.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.ics214.invoke_arn
}
resource "aws_lambda_permission" "apigw_ics214_periods_get" {
  statement_id  = "AllowAPIGatewayInvokeIcs214PeriodsGet"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.ics214.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.incident_cmd.execution_arn}/*/GET/ics214/periods"
}

# GET /ics214/periods/{periodId}
resource "aws_api_gateway_method" "ics214_period_id_get" {
  rest_api_id   = aws_api_gateway_rest_api.incident_cmd.id
  resource_id   = aws_api_gateway_resource.ics214_period_id.id
  http_method   = "GET"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "ics214_period_id_get" {
  depends_on = [aws_api_gateway_method.ics214_period_id_get]
  rest_api_id             = aws_api_gateway_rest_api.incident_cmd.id
  resource_id             = aws_api_gateway_resource.ics214_period_id.id
  http_method             = aws_api_gateway_method.ics214_period_id_get.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.ics214.invoke_arn
}
resource "aws_lambda_permission" "apigw_ics214_period_id_get" {
  statement_id  = "AllowAPIGatewayInvokeIcs214PeriodIdGet"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.ics214.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.incident_cmd.execution_arn}/*/GET/ics214/periods/*"
}

# GET /ics214
resource "aws_api_gateway_method" "ics214_get" {
  rest_api_id   = aws_api_gateway_rest_api.incident_cmd.id
  resource_id   = aws_api_gateway_resource.ics214.id
  http_method   = "GET"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "ics214_get" {
  depends_on = [aws_api_gateway_method.ics214_get]
  rest_api_id             = aws_api_gateway_rest_api.incident_cmd.id
  resource_id             = aws_api_gateway_resource.ics214.id
  http_method             = aws_api_gateway_method.ics214_get.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.ics214.invoke_arn
}
resource "aws_lambda_permission" "apigw_ics214_get" {
  statement_id  = "AllowAPIGatewayInvokeICS214Get"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.ics214.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.incident_cmd.execution_arn}/*/GET/ics214"
}

# CORS OPTIONS for /ics214
resource "aws_api_gateway_method" "ics214_options" {
  rest_api_id   = aws_api_gateway_rest_api.incident_cmd.id
  resource_id   = aws_api_gateway_resource.ics214.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "ics214_options" {
  depends_on = [aws_api_gateway_method.ics214_options]
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  resource_id = aws_api_gateway_resource.ics214.id
  http_method = aws_api_gateway_method.ics214_options.http_method
  type        = "MOCK"
  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}
resource "aws_api_gateway_method_response" "ics214_options" {
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  resource_id = aws_api_gateway_resource.ics214.id
  http_method = aws_api_gateway_method.ics214_options.http_method
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
resource "aws_api_gateway_integration_response" "ics214_options" {
  depends_on = [aws_api_gateway_integration.ics214_options]
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  resource_id = aws_api_gateway_resource.ics214.id
  http_method = aws_api_gateway_method.ics214_options.http_method
  status_code = aws_api_gateway_method_response.ics214_options.status_code
  response_templates = {
    "application/json" = ""
  }
  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"
    "method.response.header.Access-Control-Allow-Methods" = "'GET,OPTIONS'"
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
  }
}

# CORS OPTIONS for /ics214/periods
resource "aws_api_gateway_method" "ics214_periods_options" {
  rest_api_id   = aws_api_gateway_rest_api.incident_cmd.id
  resource_id   = aws_api_gateway_resource.ics214_periods_list.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "ics214_periods_options" {
  depends_on = [aws_api_gateway_method.ics214_periods_options]
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  resource_id = aws_api_gateway_resource.ics214_periods_list.id
  http_method = aws_api_gateway_method.ics214_periods_options.http_method
  type        = "MOCK"
  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}
resource "aws_api_gateway_method_response" "ics214_periods_options" {
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  resource_id = aws_api_gateway_resource.ics214_periods_list.id
  http_method = aws_api_gateway_method.ics214_periods_options.http_method
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
resource "aws_api_gateway_integration_response" "ics214_periods_options" {
  depends_on = [aws_api_gateway_integration.ics214_periods_options]
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  resource_id = aws_api_gateway_resource.ics214_periods_list.id
  http_method = aws_api_gateway_method.ics214_periods_options.http_method
  status_code = aws_api_gateway_method_response.ics214_periods_options.status_code
  response_templates = {
    "application/json" = ""
  }
  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"
    "method.response.header.Access-Control-Allow-Methods" = "'GET,POST,OPTIONS'"
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
  }
}

# CORS OPTIONS for /ics214/periods/{periodId}
resource "aws_api_gateway_method" "ics214_period_id_options" {
  rest_api_id   = aws_api_gateway_rest_api.incident_cmd.id
  resource_id   = aws_api_gateway_resource.ics214_period_id.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "ics214_period_id_options" {
  depends_on = [aws_api_gateway_method.ics214_period_id_options]
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  resource_id = aws_api_gateway_resource.ics214_period_id.id
  http_method = aws_api_gateway_method.ics214_period_id_options.http_method
  type        = "MOCK"
  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}
resource "aws_api_gateway_method_response" "ics214_period_id_options" {
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  resource_id = aws_api_gateway_resource.ics214_period_id.id
  http_method = aws_api_gateway_method.ics214_period_id_options.http_method
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
resource "aws_api_gateway_integration_response" "ics214_period_id_options" {
  depends_on = [aws_api_gateway_integration.ics214_period_id_options]
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  resource_id = aws_api_gateway_resource.ics214_period_id.id
  http_method = aws_api_gateway_method.ics214_period_id_options.http_method
  status_code = aws_api_gateway_method_response.ics214_period_id_options.status_code
  response_templates = {
    "application/json" = ""
  }
  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"
    "method.response.header.Access-Control-Allow-Methods" = "'GET,PUT,DELETE,OPTIONS'"
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
  }
}

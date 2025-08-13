# /units resource
resource "aws_api_gateway_resource" "units_list" {
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  parent_id   = data.aws_api_gateway_resource.root.id
  path_part   = "units"
}

# /units/{unitId} resource
resource "aws_api_gateway_resource" "unit_id" {
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  parent_id   = aws_api_gateway_resource.units_list.id
  path_part   = "{unitId}"
}

# GET /units
resource "aws_api_gateway_method" "units_get" {
  rest_api_id   = aws_api_gateway_rest_api.incident_cmd.id
  resource_id   = aws_api_gateway_resource.units_list.id
  http_method   = "GET"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "units_get" {
  depends_on              = [aws_api_gateway_method.units_get]
  rest_api_id             = aws_api_gateway_rest_api.incident_cmd.id
  resource_id             = aws_api_gateway_resource.units_list.id
  http_method             = aws_api_gateway_method.units_get.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.units.invoke_arn
}
resource "aws_lambda_permission" "apigw_units_get" {
  statement_id  = "AllowAPIGatewayInvokeUnitsGet"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.units.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.incident_cmd.execution_arn}/*/GET/units"
}

# POST /units
resource "aws_api_gateway_method" "units_post" {
  rest_api_id   = aws_api_gateway_rest_api.incident_cmd.id
  resource_id   = aws_api_gateway_resource.units_list.id
  http_method   = "POST"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "units_post" {
  depends_on              = [aws_api_gateway_method.units_post]
  rest_api_id             = aws_api_gateway_rest_api.incident_cmd.id
  resource_id             = aws_api_gateway_resource.units_list.id
  http_method             = aws_api_gateway_method.units_post.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.units.invoke_arn
}
resource "aws_lambda_permission" "apigw_units_post" {
  statement_id  = "AllowAPIGatewayInvokeUnitsPost"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.units.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.incident_cmd.execution_arn}/*/POST/units"
}

# GET /units/{unitId}
resource "aws_api_gateway_method" "unit_id_get" {
  rest_api_id   = aws_api_gateway_rest_api.incident_cmd.id
  resource_id   = aws_api_gateway_resource.unit_id.id
  http_method   = "GET"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "unit_id_get" {
  depends_on              = [aws_api_gateway_method.unit_id_get]
  rest_api_id             = aws_api_gateway_rest_api.incident_cmd.id
  resource_id             = aws_api_gateway_resource.unit_id.id
  http_method             = aws_api_gateway_method.unit_id_get.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.units.invoke_arn
}
resource "aws_lambda_permission" "apigw_unit_id_get" {
  statement_id  = "AllowAPIGatewayInvokeUnitIdGet"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.units.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.incident_cmd.execution_arn}/*/GET/units/*"
}

# PUT /units/{unitId}
resource "aws_api_gateway_method" "unit_id_put" {
  rest_api_id   = aws_api_gateway_rest_api.incident_cmd.id
  resource_id   = aws_api_gateway_resource.unit_id.id
  http_method   = "PUT"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "unit_id_put" {
  depends_on              = [aws_api_gateway_method.unit_id_put]
  rest_api_id             = aws_api_gateway_rest_api.incident_cmd.id
  resource_id             = aws_api_gateway_resource.unit_id.id
  http_method             = aws_api_gateway_method.unit_id_put.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.units.invoke_arn
}
resource "aws_lambda_permission" "apigw_unit_id_put" {
  statement_id  = "AllowAPIGatewayInvokeUnitIdPut"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.units.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.incident_cmd.execution_arn}/*/PUT/units/*"
}

# DELETE /units/{unitId}
resource "aws_api_gateway_method" "unit_id_delete" {
  rest_api_id   = aws_api_gateway_rest_api.incident_cmd.id
  resource_id   = aws_api_gateway_resource.unit_id.id
  http_method   = "DELETE"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "unit_id_delete" {
  depends_on              = [aws_api_gateway_method.unit_id_delete]
  rest_api_id             = aws_api_gateway_rest_api.incident_cmd.id
  resource_id             = aws_api_gateway_resource.unit_id.id
  http_method             = aws_api_gateway_method.unit_id_delete.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.units.invoke_arn
}
resource "aws_lambda_permission" "apigw_unit_id_delete" {
  statement_id  = "AllowAPIGatewayInvokeUnitIdDelete"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.units.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.incident_cmd.execution_arn}/*/DELETE/units/*"
}

# CORS OPTIONS for /units
resource "aws_api_gateway_method" "units_options" {
  rest_api_id   = aws_api_gateway_rest_api.incident_cmd.id
  resource_id   = aws_api_gateway_resource.units_list.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "units_options" {
  depends_on  = [aws_api_gateway_method.units_options]
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  resource_id = aws_api_gateway_resource.units_list.id
  http_method = aws_api_gateway_method.units_options.http_method
  type        = "MOCK"
  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}
resource "aws_api_gateway_method_response" "units_options" {
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  resource_id = aws_api_gateway_resource.units_list.id
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
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  resource_id = aws_api_gateway_resource.units_list.id
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
resource "aws_api_gateway_method" "unit_id_options" {
  rest_api_id   = aws_api_gateway_rest_api.incident_cmd.id
  resource_id   = aws_api_gateway_resource.unit_id.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "unit_id_options" {
  depends_on  = [aws_api_gateway_method.unit_id_options]
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  resource_id = aws_api_gateway_resource.unit_id.id
  http_method = aws_api_gateway_method.unit_id_options.http_method
  type        = "MOCK"
  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}
resource "aws_api_gateway_method_response" "unit_id_options" {
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  resource_id = aws_api_gateway_resource.unit_id.id
  http_method = aws_api_gateway_method.unit_id_options.http_method
  status_code = "200"
  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = true
    "method.response.header.Access-Control-Allow-Methods" = true
    "method.response.header.Access-Control-Allow-Origin"  = true
  }
}
resource "aws_api_gateway_integration_response" "unit_id_options" {
  depends_on  = [aws_api_gateway_integration.unit_id_options]
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  resource_id = aws_api_gateway_resource.unit_id.id
  http_method = aws_api_gateway_method.unit_id_options.http_method
  status_code = aws_api_gateway_method_response.unit_id_options.status_code
  response_templates = {
    "application/json" = ""
  }
  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,Authorization'"
    "method.response.header.Access-Control-Allow-Methods" = "'GET,PUT,DELETE,OPTIONS'"
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
  }
}

# Radios API Gateway integration
# /radios resource
resource "aws_api_gateway_resource" "radios_list" {
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  parent_id   = data.aws_api_gateway_resource.root.id
  path_part   = "radios"
}

# /radios/{radioId} resource
resource "aws_api_gateway_resource" "radio_id" {
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  parent_id   = aws_api_gateway_resource.radios_list.id
  path_part   = "{radioId}"
}

# GET /radios
resource "aws_api_gateway_method" "radios_get" {
  rest_api_id   = aws_api_gateway_rest_api.incident_cmd.id
  resource_id   = aws_api_gateway_resource.radios_list.id
  http_method   = "GET"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "radios_get" {
  depends_on              = [aws_api_gateway_method.radios_get]
  rest_api_id             = aws_api_gateway_rest_api.incident_cmd.id
  resource_id             = aws_api_gateway_resource.radios_list.id
  http_method             = aws_api_gateway_method.radios_get.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.radios.invoke_arn
}
resource "aws_lambda_permission" "apigw_radios_get" {
  statement_id  = "AllowAPIGatewayInvokeRadiosGet"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.radios.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.incident_cmd.execution_arn}/*/GET/radios"
}

# POST /radios
resource "aws_api_gateway_method" "radios_post" {
  rest_api_id   = aws_api_gateway_rest_api.incident_cmd.id
  resource_id   = aws_api_gateway_resource.radios_list.id
  http_method   = "POST"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "radios_post" {
  depends_on              = [aws_api_gateway_method.radios_post]
  rest_api_id             = aws_api_gateway_rest_api.incident_cmd.id
  resource_id             = aws_api_gateway_resource.radios_list.id
  http_method             = aws_api_gateway_method.radios_post.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.radios.invoke_arn
}
resource "aws_lambda_permission" "apigw_radios_post" {
  statement_id  = "AllowAPIGatewayInvokeRadiosPost"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.radios.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.incident_cmd.execution_arn}/*/POST/radios"
}

# GET /radios/{radioId}
resource "aws_api_gateway_method" "radio_id_get" {
  rest_api_id   = aws_api_gateway_rest_api.incident_cmd.id
  resource_id   = aws_api_gateway_resource.radio_id.id
  http_method   = "GET"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "radio_id_get" {
  depends_on              = [aws_api_gateway_method.radio_id_get]
  rest_api_id             = aws_api_gateway_rest_api.incident_cmd.id
  resource_id             = aws_api_gateway_resource.radio_id.id
  http_method             = aws_api_gateway_method.radio_id_get.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.radios.invoke_arn
}
resource "aws_lambda_permission" "apigw_radio_id_get" {
  statement_id  = "AllowAPIGatewayInvokeRadioIdGet"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.radios.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.incident_cmd.execution_arn}/*/GET/radios/*"
}

# PUT /radios/{radioId}
resource "aws_api_gateway_method" "radio_id_put" {
  rest_api_id   = aws_api_gateway_rest_api.incident_cmd.id
  resource_id   = aws_api_gateway_resource.radio_id.id
  http_method   = "PUT"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "radio_id_put" {
  depends_on              = [aws_api_gateway_method.radio_id_put]
  rest_api_id             = aws_api_gateway_rest_api.incident_cmd.id
  resource_id             = aws_api_gateway_resource.radio_id.id
  http_method             = aws_api_gateway_method.radio_id_put.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.radios.invoke_arn
}
resource "aws_lambda_permission" "apigw_radio_id_put" {
  statement_id  = "AllowAPIGatewayInvokeRadioIdPut"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.radios.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.incident_cmd.execution_arn}/*/PUT/radios/*"
}

# DELETE /radios/{radioId}
resource "aws_api_gateway_method" "radio_id_delete" {
  rest_api_id   = aws_api_gateway_rest_api.incident_cmd.id
  resource_id   = aws_api_gateway_resource.radio_id.id
  http_method   = "DELETE"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "radio_id_delete" {
  depends_on              = [aws_api_gateway_method.radio_id_delete]
  rest_api_id             = aws_api_gateway_rest_api.incident_cmd.id
  resource_id             = aws_api_gateway_resource.radio_id.id
  http_method             = aws_api_gateway_method.radio_id_delete.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.radios.invoke_arn
}
resource "aws_lambda_permission" "apigw_radio_id_delete" {
  statement_id  = "AllowAPIGatewayInvokeRadioIdDelete"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.radios.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.incident_cmd.execution_arn}/*/DELETE/radios/*"
}

# CORS OPTIONS for /radios
resource "aws_api_gateway_method" "radios_options" {
  rest_api_id   = aws_api_gateway_rest_api.incident_cmd.id
  resource_id   = aws_api_gateway_resource.radios_list.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "radios_options" {
  depends_on  = [aws_api_gateway_method.radios_options]
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  resource_id = aws_api_gateway_resource.radios_list.id
  http_method = aws_api_gateway_method.radios_options.http_method
  type        = "MOCK"
  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}
resource "aws_api_gateway_method_response" "radios_options" {
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  resource_id = aws_api_gateway_resource.radios_list.id
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
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  resource_id = aws_api_gateway_resource.radios_list.id
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
resource "aws_api_gateway_method" "radio_id_options" {
  rest_api_id   = aws_api_gateway_rest_api.incident_cmd.id
  resource_id   = aws_api_gateway_resource.radio_id.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "radio_id_options" {
  depends_on  = [aws_api_gateway_method.radio_id_options]
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  resource_id = aws_api_gateway_resource.radio_id.id
  http_method = aws_api_gateway_method.radio_id_options.http_method
  type        = "MOCK"
  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}
resource "aws_api_gateway_method_response" "radio_id_options" {
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  resource_id = aws_api_gateway_resource.radio_id.id
  http_method = aws_api_gateway_method.radio_id_options.http_method
  status_code = "200"
  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = true
    "method.response.header.Access-Control-Allow-Methods" = true
    "method.response.header.Access-Control-Allow-Origin"  = true
  }
}
resource "aws_api_gateway_integration_response" "radio_id_options" {
  depends_on  = [aws_api_gateway_integration.radio_id_options]
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  resource_id = aws_api_gateway_resource.radio_id.id
  http_method = aws_api_gateway_method.radio_id_options.http_method
  status_code = aws_api_gateway_method_response.radio_id_options.status_code
  response_templates = {
    "application/json" = ""
  }
  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,Authorization'"
    "method.response.header.Access-Control-Allow-Methods" = "'GET,PUT,DELETE,OPTIONS'"
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
  }
}

locals {
  radios_integrations = [
    aws_api_gateway_integration.radios_get,
    aws_api_gateway_integration.radios_post,
    aws_api_gateway_integration.radio_id_get,
    aws_api_gateway_integration.radio_id_put,
    aws_api_gateway_integration.radio_id_delete,
    aws_api_gateway_integration.radios_options,
    aws_api_gateway_integration.radio_id_options,
  ]
}

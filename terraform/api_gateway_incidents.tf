
# /incidents resource
resource "aws_api_gateway_resource" "incidents_list" {
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  parent_id   = data.aws_api_gateway_resource.root.id
  path_part   = "incidents"
}

# /incidents/{incidentId} resource
resource "aws_api_gateway_resource" "incident_id" {
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  parent_id   = aws_api_gateway_resource.incidents_list.id
  path_part   = "{incidentId}"
}

# GET /incidents
resource "aws_api_gateway_method" "incidents_get" {
  rest_api_id   = aws_api_gateway_rest_api.incident_cmd.id
  resource_id   = aws_api_gateway_resource.incidents_list.id
  http_method   = "GET"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "incidents_get" {
  depends_on              = [aws_api_gateway_method.incidents_get]
  rest_api_id             = aws_api_gateway_rest_api.incident_cmd.id
  resource_id             = aws_api_gateway_resource.incidents_list.id
  http_method             = aws_api_gateway_method.incidents_get.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.incidents.invoke_arn
}
resource "aws_lambda_permission" "apigw_incidents_get" {
  statement_id  = "AllowAPIGatewayInvokeIncidentsGet"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.incidents.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.incident_cmd.execution_arn}/*/GET/incidents"
}

# POST /incidents
resource "aws_api_gateway_method" "incidents_post" {
  rest_api_id   = aws_api_gateway_rest_api.incident_cmd.id
  resource_id   = aws_api_gateway_resource.incidents_list.id
  http_method   = "POST"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "incidents_post" {
  depends_on              = [aws_api_gateway_method.incidents_post]
  rest_api_id             = aws_api_gateway_rest_api.incident_cmd.id
  resource_id             = aws_api_gateway_resource.incidents_list.id
  http_method             = aws_api_gateway_method.incidents_post.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.incidents.invoke_arn
}
resource "aws_lambda_permission" "apigw_incidents_post" {
  statement_id  = "AllowAPIGatewayInvokeIncidentsPost"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.incidents.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.incident_cmd.execution_arn}/*/POST/incidents"
}

# GET /incidents/{incidentId}
resource "aws_api_gateway_method" "incident_id_get" {
  rest_api_id   = aws_api_gateway_rest_api.incident_cmd.id
  resource_id   = aws_api_gateway_resource.incident_id.id
  http_method   = "GET"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "incident_id_get" {
  depends_on              = [aws_api_gateway_method.incident_id_get]
  rest_api_id             = aws_api_gateway_rest_api.incident_cmd.id
  resource_id             = aws_api_gateway_resource.incident_id.id
  http_method             = aws_api_gateway_method.incident_id_get.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.incidents.invoke_arn
}
resource "aws_lambda_permission" "apigw_incident_id_get" {
  statement_id  = "AllowAPIGatewayInvokeIncidentIdGet"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.incidents.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.incident_cmd.execution_arn}/*/GET/incidents/*"
}

# PUT /incidents/{incidentId}
resource "aws_api_gateway_method" "incident_id_put" {
  rest_api_id   = aws_api_gateway_rest_api.incident_cmd.id
  resource_id   = aws_api_gateway_resource.incident_id.id
  http_method   = "PUT"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "incident_id_put" {
  depends_on              = [aws_api_gateway_method.incident_id_put]
  rest_api_id             = aws_api_gateway_rest_api.incident_cmd.id
  resource_id             = aws_api_gateway_resource.incident_id.id
  http_method             = aws_api_gateway_method.incident_id_put.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.incidents.invoke_arn
}
resource "aws_lambda_permission" "apigw_incident_id_put" {
  statement_id  = "AllowAPIGatewayInvokeIncidentIdPut"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.incidents.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.incident_cmd.execution_arn}/*/PUT/incidents/*"
}

# DELETE /incidents/{incidentId}
resource "aws_api_gateway_method" "incident_id_delete" {
  rest_api_id   = aws_api_gateway_rest_api.incident_cmd.id
  resource_id   = aws_api_gateway_resource.incident_id.id
  http_method   = "DELETE"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "incident_id_delete" {
  depends_on              = [aws_api_gateway_method.incident_id_delete]
  rest_api_id             = aws_api_gateway_rest_api.incident_cmd.id
  resource_id             = aws_api_gateway_resource.incident_id.id
  http_method             = aws_api_gateway_method.incident_id_delete.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.incidents.invoke_arn
}
resource "aws_lambda_permission" "apigw_incident_id_delete" {
  statement_id  = "AllowAPIGatewayInvokeIncidentIdDelete"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.incidents.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.incident_cmd.execution_arn}/*/DELETE/incidents/*"
}

# CORS OPTIONS for /incidents
resource "aws_api_gateway_method" "incidents_options" {
  rest_api_id   = aws_api_gateway_rest_api.incident_cmd.id
  resource_id   = aws_api_gateway_resource.incidents_list.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "incidents_options" {
  depends_on  = [aws_api_gateway_method.incidents_options]
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  resource_id = aws_api_gateway_resource.incidents_list.id
  http_method = aws_api_gateway_method.incidents_options.http_method
  type        = "MOCK"
  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}
resource "aws_api_gateway_method_response" "incidents_options" {
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  resource_id = aws_api_gateway_resource.incidents_list.id
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
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  resource_id = aws_api_gateway_resource.incidents_list.id
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
resource "aws_api_gateway_method" "incident_id_options" {
  rest_api_id   = aws_api_gateway_rest_api.incident_cmd.id
  resource_id   = aws_api_gateway_resource.incident_id.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "incident_id_options" {
  depends_on  = [aws_api_gateway_method.incident_id_options]
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  resource_id = aws_api_gateway_resource.incident_id.id
  http_method = aws_api_gateway_method.incident_id_options.http_method
  type        = "MOCK"
  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}
resource "aws_api_gateway_method_response" "incident_id_options" {
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  resource_id = aws_api_gateway_resource.incident_id.id
  http_method = aws_api_gateway_method.incident_id_options.http_method
  status_code = "200"
  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = true
    "method.response.header.Access-Control-Allow-Methods" = true
    "method.response.header.Access-Control-Allow-Origin"  = true
  }
}
resource "aws_api_gateway_integration_response" "incident_id_options" {
  depends_on  = [aws_api_gateway_integration.incident_id_options]
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  resource_id = aws_api_gateway_resource.incident_id.id
  http_method = aws_api_gateway_method.incident_id_options.http_method
  status_code = aws_api_gateway_method_response.incident_id_options.status_code
  response_templates = {
    "application/json" = ""
  }
  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,Authorization'"
    "method.response.header.Access-Control-Allow-Methods" = "'GET,PUT,DELETE,OPTIONS'"
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
  }
}

# Locations API Gateway integration
# /locations resource
resource "aws_api_gateway_resource" "locations_list" {
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  parent_id   = data.aws_api_gateway_resource.root.id
  path_part   = "locations"
}

# /locations/{locationId} resource
resource "aws_api_gateway_resource" "location_id" {
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  parent_id   = aws_api_gateway_resource.locations_list.id
  path_part   = "{locationId}"
}

# GET /locations
resource "aws_api_gateway_method" "locations_get" {
  rest_api_id   = aws_api_gateway_rest_api.incident_cmd.id
  resource_id   = aws_api_gateway_resource.locations_list.id
  http_method   = "GET"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "locations_get" {
  depends_on              = [aws_api_gateway_method.locations_get]
  rest_api_id             = aws_api_gateway_rest_api.incident_cmd.id
  resource_id             = aws_api_gateway_resource.locations_list.id
  http_method             = aws_api_gateway_method.locations_get.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.locations.invoke_arn
}
resource "aws_lambda_permission" "apigw_locations_get" {
  statement_id  = "AllowAPIGatewayInvokeLocationsGet"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.locations.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.incident_cmd.execution_arn}/*/GET/locations"
}

# POST /locations
resource "aws_api_gateway_method" "locations_post" {
  rest_api_id   = aws_api_gateway_rest_api.incident_cmd.id
  resource_id   = aws_api_gateway_resource.locations_list.id
  http_method   = "POST"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "locations_post" {
  depends_on              = [aws_api_gateway_method.locations_post]
  rest_api_id             = aws_api_gateway_rest_api.incident_cmd.id
  resource_id             = aws_api_gateway_resource.locations_list.id
  http_method             = aws_api_gateway_method.locations_post.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.locations.invoke_arn
}
resource "aws_lambda_permission" "apigw_locations_post" {
  statement_id  = "AllowAPIGatewayInvokeLocationsPost"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.locations.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.incident_cmd.execution_arn}/*/POST/locations"
}

# GET /locations/{locationId}
resource "aws_api_gateway_method" "location_id_get" {
  rest_api_id   = aws_api_gateway_rest_api.incident_cmd.id
  resource_id   = aws_api_gateway_resource.location_id.id
  http_method   = "GET"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "location_id_get" {
  depends_on              = [aws_api_gateway_method.location_id_get]
  rest_api_id             = aws_api_gateway_rest_api.incident_cmd.id
  resource_id             = aws_api_gateway_resource.location_id.id
  http_method             = aws_api_gateway_method.location_id_get.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.locations.invoke_arn
}
resource "aws_lambda_permission" "apigw_location_id_get" {
  statement_id  = "AllowAPIGatewayInvokeLocationIdGet"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.locations.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.incident_cmd.execution_arn}/*/GET/locations/*"
}

# PUT /locations/{locationId}
resource "aws_api_gateway_method" "location_id_put" {
  rest_api_id   = aws_api_gateway_rest_api.incident_cmd.id
  resource_id   = aws_api_gateway_resource.location_id.id
  http_method   = "PUT"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "location_id_put" {
  depends_on              = [aws_api_gateway_method.location_id_put]
  rest_api_id             = aws_api_gateway_rest_api.incident_cmd.id
  resource_id             = aws_api_gateway_resource.location_id.id
  http_method             = aws_api_gateway_method.location_id_put.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.locations.invoke_arn
}
resource "aws_lambda_permission" "apigw_location_id_put" {
  statement_id  = "AllowAPIGatewayInvokeLocationIdPut"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.locations.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.incident_cmd.execution_arn}/*/PUT/locations/*"
}

# DELETE /locations/{locationId}
resource "aws_api_gateway_method" "location_id_delete" {
  rest_api_id   = aws_api_gateway_rest_api.incident_cmd.id
  resource_id   = aws_api_gateway_resource.location_id.id
  http_method   = "DELETE"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "location_id_delete" {
  depends_on              = [aws_api_gateway_method.location_id_delete]
  rest_api_id             = aws_api_gateway_rest_api.incident_cmd.id
  resource_id             = aws_api_gateway_resource.location_id.id
  http_method             = aws_api_gateway_method.location_id_delete.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.locations.invoke_arn
}
resource "aws_lambda_permission" "apigw_location_id_delete" {
  statement_id  = "AllowAPIGatewayInvokeLocationIdDelete"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.locations.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.incident_cmd.execution_arn}/*/DELETE/locations/*"
}

# CORS OPTIONS for /locations
resource "aws_api_gateway_method" "locations_options" {
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  resource_id = aws_api_gateway_resource.locations_list.id
  http_method = "OPTIONS"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "locations_options" {
  depends_on  = [aws_api_gateway_method.locations_options]
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  resource_id = aws_api_gateway_resource.locations_list.id
  http_method = aws_api_gateway_method.locations_options.http_method
  type        = "MOCK"
  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}
resource "aws_api_gateway_method_response" "locations_options" {
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  resource_id = aws_api_gateway_resource.locations_list.id
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
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  resource_id = aws_api_gateway_resource.locations_list.id
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
resource "aws_api_gateway_method" "location_id_options" {
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  resource_id = aws_api_gateway_resource.location_id.id
  http_method = "OPTIONS"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "location_id_options" {
  depends_on  = [aws_api_gateway_method.location_id_options]
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  resource_id = aws_api_gateway_resource.location_id.id
  http_method = aws_api_gateway_method.location_id_options.http_method
  type        = "MOCK"
  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}
resource "aws_api_gateway_method_response" "location_id_options" {
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  resource_id = aws_api_gateway_resource.location_id.id
  http_method = aws_api_gateway_method.location_id_options.http_method
  status_code = "200"
  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = true
    "method.response.header.Access-Control-Allow-Methods" = true
    "method.response.header.Access-Control-Allow-Origin"  = true
  }
}
resource "aws_api_gateway_integration_response" "location_id_options" {
  depends_on  = [aws_api_gateway_integration.location_id_options]
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  resource_id = aws_api_gateway_resource.location_id.id
  http_method = aws_api_gateway_method.location_id_options.http_method
  status_code = aws_api_gateway_method_response.location_id_options.status_code
  response_templates = {
    "application/json" = ""
  }
  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,Authorization'"
    "method.response.header.Access-Control-Allow-Methods" = "'GET,PUT,DELETE,OPTIONS'"
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
  }
}

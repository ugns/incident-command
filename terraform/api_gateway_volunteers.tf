# Volunteers API Gateway resources and methods

# /volunteers resource
resource "aws_api_gateway_resource" "volunteers" {
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  parent_id   = data.aws_api_gateway_resource.root.id
  path_part   = "volunteers"
}

# /volunteers/{volunteerId} resource
resource "aws_api_gateway_resource" "volunteer_id" {
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  parent_id   = aws_api_gateway_resource.volunteers.id
  path_part   = "{volunteerId}"
}

# GET /volunteers
resource "aws_api_gateway_method" "volunteers_get" {
  rest_api_id   = aws_api_gateway_rest_api.incident_cmd.id
  resource_id   = aws_api_gateway_resource.volunteers.id
  http_method   = "GET"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "volunteers_get" {
  depends_on              = [aws_api_gateway_method.volunteers_get]
  rest_api_id             = aws_api_gateway_rest_api.incident_cmd.id
  resource_id             = aws_api_gateway_resource.volunteers.id
  http_method             = aws_api_gateway_method.volunteers_get.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.volunteers.invoke_arn
}
resource "aws_lambda_permission" "apigw_volunteers_get" {
  statement_id  = "AllowAPIGatewayInvokeVolunteersGet"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.volunteers.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.incident_cmd.execution_arn}/*/GET/volunteers"
}

# POST /volunteers
resource "aws_api_gateway_method" "volunteers_post" {
  rest_api_id   = aws_api_gateway_rest_api.incident_cmd.id
  resource_id   = aws_api_gateway_resource.volunteers.id
  http_method   = "POST"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "volunteers_post" {
  depends_on              = [aws_api_gateway_method.volunteers_post]
  rest_api_id             = aws_api_gateway_rest_api.incident_cmd.id
  resource_id             = aws_api_gateway_resource.volunteers.id
  http_method             = aws_api_gateway_method.volunteers_post.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.volunteers.invoke_arn
}
resource "aws_lambda_permission" "apigw_volunteers_post" {
  statement_id  = "AllowAPIGatewayInvokeVolunteersPost"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.volunteers.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.incident_cmd.execution_arn}/*/POST/volunteers"
}

# GET /volunteers/{volunteerId}
resource "aws_api_gateway_method" "volunteer_id_get" {
  rest_api_id   = aws_api_gateway_rest_api.incident_cmd.id
  resource_id   = aws_api_gateway_resource.volunteer_id.id
  http_method   = "GET"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "volunteer_id_get" {
  depends_on              = [aws_api_gateway_method.volunteer_id_get]
  rest_api_id             = aws_api_gateway_rest_api.incident_cmd.id
  resource_id             = aws_api_gateway_resource.volunteer_id.id
  http_method             = aws_api_gateway_method.volunteer_id_get.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.volunteers.invoke_arn
}
resource "aws_lambda_permission" "apigw_volunteer_id_get" {
  statement_id  = "AllowAPIGatewayInvokeVolunteerIdGet"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.volunteers.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.incident_cmd.execution_arn}/*/GET/volunteers/*"
}

# PUT /volunteers/{volunteerId}
resource "aws_api_gateway_method" "volunteer_id_put" {
  rest_api_id   = aws_api_gateway_rest_api.incident_cmd.id
  resource_id   = aws_api_gateway_resource.volunteer_id.id
  http_method   = "PUT"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "volunteer_id_put" {
  depends_on              = [aws_api_gateway_method.volunteer_id_put]
  rest_api_id             = aws_api_gateway_rest_api.incident_cmd.id
  resource_id             = aws_api_gateway_resource.volunteer_id.id
  http_method             = aws_api_gateway_method.volunteer_id_put.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.volunteers.invoke_arn
}
resource "aws_lambda_permission" "apigw_volunteer_id_put" {
  statement_id  = "AllowAPIGatewayInvokeVolunteerIdPut"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.volunteers.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.incident_cmd.execution_arn}/*/PUT/volunteers/*"
}

# DELETE /volunteers/{volunteerId}
resource "aws_api_gateway_method" "volunteer_id_delete" {
  rest_api_id   = aws_api_gateway_rest_api.incident_cmd.id
  resource_id   = aws_api_gateway_resource.volunteer_id.id
  http_method   = "DELETE"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "volunteer_id_delete" {
  depends_on              = [aws_api_gateway_method.volunteer_id_delete]
  rest_api_id             = aws_api_gateway_rest_api.incident_cmd.id
  resource_id             = aws_api_gateway_resource.volunteer_id.id
  http_method             = aws_api_gateway_method.volunteer_id_delete.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.volunteers.invoke_arn
}
resource "aws_lambda_permission" "apigw_volunteer_id_delete" {
  statement_id  = "AllowAPIGatewayInvokeVolunteerIdDelete"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.volunteers.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.incident_cmd.execution_arn}/*/DELETE/volunteers/*"
}

# PUT /volunteers/{volunteerId}/dispatch
resource "aws_api_gateway_resource" "volunteer_id_dispatch" {
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  parent_id   = aws_api_gateway_resource.volunteer_id.id
  path_part   = "dispatch"
}
resource "aws_api_gateway_method" "volunteer_id_dispatch_put" {
  rest_api_id   = aws_api_gateway_rest_api.incident_cmd.id
  resource_id   = aws_api_gateway_resource.volunteer_id_dispatch.id
  http_method   = "PUT"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "volunteer_id_dispatch_put" {
  depends_on              = [aws_api_gateway_method.volunteer_id_dispatch_put]
  rest_api_id             = aws_api_gateway_rest_api.incident_cmd.id
  resource_id             = aws_api_gateway_resource.volunteer_id_dispatch.id
  http_method             = aws_api_gateway_method.volunteer_id_dispatch_put.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.volunteers.invoke_arn
}
resource "aws_lambda_permission" "apigw_volunteer_id_dispatch_put" {
  statement_id  = "AllowAPIGatewayInvokeVolunteerIdDispatchPost"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.volunteers.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.incident_cmd.execution_arn}/*/PUT/volunteers/*/dispatch"
}

# PUT /volunteers/{volunteerId}/checkout
resource "aws_api_gateway_resource" "volunteer_id_checkout" {
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  parent_id   = aws_api_gateway_resource.volunteer_id.id
  path_part   = "checkout"
}
resource "aws_api_gateway_method" "volunteer_id_checkout_put" {
  rest_api_id   = aws_api_gateway_rest_api.incident_cmd.id
  resource_id   = aws_api_gateway_resource.volunteer_id_checkout.id
  http_method   = "PUT"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "volunteer_id_checkout_put" {
  depends_on              = [aws_api_gateway_method.volunteer_id_checkout_put]
  rest_api_id             = aws_api_gateway_rest_api.incident_cmd.id
  resource_id             = aws_api_gateway_resource.volunteer_id_checkout.id
  http_method             = aws_api_gateway_method.volunteer_id_checkout_put.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.volunteers.invoke_arn
}
resource "aws_lambda_permission" "apigw_volunteer_id_checkout_put" {
  statement_id  = "AllowAPIGatewayInvokeVolunteerIdCheckoutPost"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.volunteers.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.incident_cmd.execution_arn}/*/PUT/volunteers/*/checkout"
}

# PUT /volunteers/{volunteerId}/checkin
resource "aws_api_gateway_resource" "volunteer_id_checkin" {
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  parent_id   = aws_api_gateway_resource.volunteer_id.id
  path_part   = "checkin"
}

resource "aws_api_gateway_method" "volunteer_id_checkin_put" {
  rest_api_id   = aws_api_gateway_rest_api.incident_cmd.id
  resource_id   = aws_api_gateway_resource.volunteer_id_checkin.id
  http_method   = "PUT"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "volunteer_id_checkin_put" {
  depends_on              = [aws_api_gateway_method.volunteer_id_checkin_put]
  rest_api_id             = aws_api_gateway_rest_api.incident_cmd.id
  resource_id             = aws_api_gateway_resource.volunteer_id_checkin.id
  http_method             = aws_api_gateway_method.volunteer_id_checkin_put.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.volunteers.invoke_arn
}
resource "aws_lambda_permission" "apigw_volunteer_id_checkin_put" {
  statement_id  = "AllowAPIGatewayInvokeVolunteerIdCheckinPost"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.volunteers.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.incident_cmd.execution_arn}/*/PUT/volunteers/*/checkin"
}

# CORS OPTIONS for /volunteers
resource "aws_api_gateway_method" "volunteers_options" {
  rest_api_id   = aws_api_gateway_rest_api.incident_cmd.id
  resource_id   = aws_api_gateway_resource.volunteers.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "volunteers_options" {
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  resource_id = aws_api_gateway_resource.volunteers.id
  http_method = aws_api_gateway_method.volunteers_options.http_method
  type        = "MOCK"
  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}
resource "aws_api_gateway_method_response" "volunteers_options" {
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  resource_id = aws_api_gateway_resource.volunteers.id
  http_method = aws_api_gateway_method.volunteers_options.http_method
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
resource "aws_api_gateway_integration_response" "volunteers_options" {
  depends_on  = [aws_api_gateway_integration.volunteers_options]
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  resource_id = aws_api_gateway_resource.volunteers.id
  http_method = aws_api_gateway_method.volunteers_options.http_method
  status_code = aws_api_gateway_method_response.volunteers_options.status_code
  response_templates = {
    "application/json" = ""
  }
  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"
    "method.response.header.Access-Control-Allow-Methods" = "'GET,POST,PUT,OPTIONS'"
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
  }
}

# CORS OPTIONS for /volunteers/{volunteerId}
resource "aws_api_gateway_method" "volunteer_id_options" {
  rest_api_id   = aws_api_gateway_rest_api.incident_cmd.id
  resource_id   = aws_api_gateway_resource.volunteer_id.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "volunteer_id_options" {
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  resource_id = aws_api_gateway_resource.volunteer_id.id
  http_method = aws_api_gateway_method.volunteer_id_options.http_method
  type        = "MOCK"
  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}
resource "aws_api_gateway_method_response" "volunteer_id_options" {
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  resource_id = aws_api_gateway_resource.volunteer_id.id
  http_method = aws_api_gateway_method.volunteer_id_options.http_method
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
resource "aws_api_gateway_integration_response" "volunteer_id_options" {
  depends_on  = [aws_api_gateway_integration.volunteer_id_options]
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  resource_id = aws_api_gateway_resource.volunteer_id.id
  http_method = aws_api_gateway_method.volunteer_id_options.http_method
  status_code = aws_api_gateway_method_response.volunteer_id_options.status_code
  response_templates = {
    "application/json" = ""
  }
  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"
    "method.response.header.Access-Control-Allow-Methods" = "'GET,PUT,DELETE,OPTIONS'"
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
  }
}

# CORS OPTIONS for /volunteers/{volunteerId}/dispatch
resource "aws_api_gateway_method" "volunteer_id_dispatch_options" {
  rest_api_id   = aws_api_gateway_rest_api.incident_cmd.id
  resource_id   = aws_api_gateway_resource.volunteer_id_dispatch.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "volunteer_id_dispatch_options" {
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  resource_id = aws_api_gateway_resource.volunteer_id_dispatch.id
  http_method = aws_api_gateway_method.volunteer_id_dispatch_options.http_method
  type        = "MOCK"
  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}
resource "aws_api_gateway_method_response" "volunteer_id_dispatch_options" {
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  resource_id = aws_api_gateway_resource.volunteer_id_dispatch.id
  http_method = aws_api_gateway_method.volunteer_id_dispatch_options.http_method
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
resource "aws_api_gateway_integration_response" "volunteer_id_dispatch_options" {
  depends_on  = [aws_api_gateway_integration.volunteer_id_dispatch_options]
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  resource_id = aws_api_gateway_resource.volunteer_id_dispatch.id
  http_method = aws_api_gateway_method.volunteer_id_dispatch_options.http_method
  status_code = aws_api_gateway_method_response.volunteer_id_dispatch_options.status_code
  response_templates = {
    "application/json" = ""
  }
  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"
    "method.response.header.Access-Control-Allow-Methods" = "'PUT,OPTIONS'"
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
  }
}

# CORS OPTIONS for /volunteers/{volunteerId}/checkin
resource "aws_api_gateway_method" "volunteer_id_checkin_options" {
  rest_api_id   = aws_api_gateway_rest_api.incident_cmd.id
  resource_id   = aws_api_gateway_resource.volunteer_id_checkin.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "volunteer_id_checkin_options" {
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  resource_id = aws_api_gateway_resource.volunteer_id_checkin.id
  http_method = aws_api_gateway_method.volunteer_id_checkin_options.http_method
  type        = "MOCK"
  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}
resource "aws_api_gateway_method_response" "volunteer_id_checkin_options" {
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  resource_id = aws_api_gateway_resource.volunteer_id_checkin.id
  http_method = aws_api_gateway_method.volunteer_id_checkin_options.http_method
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
resource "aws_api_gateway_integration_response" "volunteer_id_checkin_options" {
  depends_on  = [aws_api_gateway_integration.volunteer_id_checkin_options]
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  resource_id = aws_api_gateway_resource.volunteer_id_checkin.id
  http_method = aws_api_gateway_method.volunteer_id_checkin_options.http_method
  status_code = aws_api_gateway_method_response.volunteer_id_checkin_options.status_code
  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"
    "method.response.header.Access-Control-Allow-Methods" = "'PUT,OPTIONS'"
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
  }
  response_templates = {
    "application/json" = ""
  }
}

# CORS OPTIONS for /volunteers/{volunteerId}/checkout
resource "aws_api_gateway_method" "volunteer_id_checkout_options" {
  rest_api_id   = aws_api_gateway_rest_api.incident_cmd.id
  resource_id   = aws_api_gateway_resource.volunteer_id_checkout.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "volunteer_id_checkout_options" {
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  resource_id = aws_api_gateway_resource.volunteer_id_checkout.id
  http_method = aws_api_gateway_method.volunteer_id_checkout_options.http_method
  type        = "MOCK"
  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}
resource "aws_api_gateway_method_response" "volunteer_id_checkout_options" {
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  resource_id = aws_api_gateway_resource.volunteer_id_checkout.id
  http_method = aws_api_gateway_method.volunteer_id_checkout_options.http_method
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
resource "aws_api_gateway_integration_response" "volunteer_id_checkout_options" {
  depends_on  = [aws_api_gateway_integration.volunteer_id_checkout_options]
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  resource_id = aws_api_gateway_resource.volunteer_id_checkout.id
  http_method = aws_api_gateway_method.volunteer_id_checkout_options.http_method
  status_code = aws_api_gateway_method_response.volunteer_id_checkout_options.status_code
  response_templates = {
    "application/json" = ""
  }
  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"
    "method.response.header.Access-Control-Allow-Methods" = "'PUT,OPTIONS'"
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
  }
}

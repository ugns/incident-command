# API Gateway REST API for Incident Command
resource "aws_api_gateway_rest_api" "incident_cmd" {
  name                         = "incident-cmd-api"
  description                  = "API for Security Incident Command Application"
  disable_execute_api_endpoint = true
  endpoint_configuration {
    types = ["REGIONAL"]
  }
  # binary_media_types = ["application/pdf", "*/*"]
  binary_media_types = [
    "application/pdf",
    "application/octet-stream",
    "application/zip",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "image/*"
  ]
}

data "aws_api_gateway_resource" "root" {
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  path        = "/"
}

# /openapi.json resource for OpenAPI spec
resource "aws_api_gateway_resource" "openapi_json" {
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  parent_id   = data.aws_api_gateway_resource.root.id
  path_part   = "openapi.json"
}

# GET /openapi.json
resource "aws_api_gateway_method" "openapi_json_get" {
  rest_api_id   = aws_api_gateway_rest_api.incident_cmd.id
  resource_id   = aws_api_gateway_resource.openapi_json.id
  http_method   = "GET"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "openapi_json_get" {
  depends_on              = [aws_api_gateway_method.openapi_json_get]
  rest_api_id             = aws_api_gateway_rest_api.incident_cmd.id
  resource_id             = aws_api_gateway_resource.openapi_json.id
  http_method             = aws_api_gateway_method.openapi_json_get.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.openapi.invoke_arn
}
resource "aws_lambda_permission" "apigw_openapi_json_get" {
  statement_id  = "AllowAPIGatewayInvokeOpenAPI"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.openapi.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.incident_cmd.execution_arn}/*/GET/openapi.json"
}

# API Gateway deployment and stage
resource "aws_api_gateway_deployment" "incident_cmd" {
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  triggers = {
    redeploy = timestamp()
  }
  lifecycle {
    create_before_destroy = true
  }
  depends_on = [
    aws_api_gateway_integration.volunteers_post,
    aws_api_gateway_integration.volunteers_options,
    aws_api_gateway_integration.volunteers_get,
    aws_api_gateway_integration.volunteer_id_put,
    aws_api_gateway_integration.volunteer_id_options,
    aws_api_gateway_integration.volunteer_id_get,
    aws_api_gateway_integration.volunteer_id_dispatch_put,
    aws_api_gateway_integration.volunteer_id_dispatch_options,
    aws_api_gateway_integration.volunteer_id_delete,
    aws_api_gateway_integration.volunteer_id_checkout_put,
    aws_api_gateway_integration.volunteer_id_checkout_options,
    aws_api_gateway_integration.volunteer_id_checkin_put,
    aws_api_gateway_integration.volunteer_id_checkin_options,
    aws_api_gateway_integration.report_type_post,
    aws_api_gateway_integration.report_type_options,
    aws_api_gateway_integration.reports_options,
    aws_api_gateway_integration.reports_get,
    aws_api_gateway_integration.periods_post,
    aws_api_gateway_integration.periods_options,
    aws_api_gateway_integration.periods_get,
    aws_api_gateway_integration.period_id_put,
    aws_api_gateway_integration.period_id_options,
    aws_api_gateway_integration.period_id_get,
    aws_api_gateway_integration.period_id_delete,
    aws_api_gateway_integration.organizations_root,
    aws_api_gateway_integration.organizations_options,
    aws_api_gateway_integration.organizations_id_options,
    aws_api_gateway_integration.organizations_id,
    aws_api_gateway_integration.openapi_json_get,
    aws_api_gateway_integration.auth_login_post,
    aws_api_gateway_integration.auth_login_options,
    aws_api_gateway_integration.activitylogs_post,
    aws_api_gateway_integration.activitylogs_options,
    aws_api_gateway_integration.activitylogs_get,
    aws_api_gateway_integration.activitylog_id_options,
    aws_api_gateway_integration.activitylog_id_get,
  ]
}

resource "aws_api_gateway_stage" "v1" {
  deployment_id = aws_api_gateway_deployment.incident_cmd.id
  rest_api_id   = aws_api_gateway_rest_api.incident_cmd.id
  stage_name    = "v1"
}

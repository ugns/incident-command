# API Gateway REST API for Incident Command
# resource "aws_api_gateway_rest_api" "incident_cmd" {
#   name                         = "incident-cmd-api"
#   description                  = "API for Security Incident Command Application"
#   disable_execute_api_endpoint = true
#   endpoint_configuration {
#     types = ["REGIONAL"]
#   }
#   binary_media_types = [
#     "application/pdf",
#     "application/octet-stream",
#     "application/zip",
#     "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
#     "application/msword",
#     "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
#     "image/*"
#   ]
# }

# data "aws_api_gateway_resource" "root" {
#   rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
#   path        = "/"
# }

# # /openapi.json resource for OpenAPI spec
# resource "aws_api_gateway_resource" "openapi_json" {
#   rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
#   parent_id   = data.aws_api_gateway_resource.root.id
#   path_part   = "openapi.json"
# }

# # GET /openapi.json
# resource "aws_api_gateway_method" "openapi_json_get" {
#   rest_api_id   = aws_api_gateway_rest_api.incident_cmd.id
#   resource_id   = aws_api_gateway_resource.openapi_json.id
#   http_method   = "GET"
#   authorization = "NONE"
# }
# resource "aws_api_gateway_integration" "openapi_json_get" {
#   depends_on              = [aws_api_gateway_method.openapi_json_get]
#   rest_api_id             = aws_api_gateway_rest_api.incident_cmd.id
#   resource_id             = aws_api_gateway_resource.openapi_json.id
#   http_method             = aws_api_gateway_method.openapi_json_get.http_method
#   integration_http_method = "POST"
#   type                    = "AWS_PROXY"
#   uri                     = aws_lambda_function.openapi.invoke_arn
# }
# resource "aws_lambda_permission" "apigw_openapi_json_get" {
#   statement_id  = "AllowAPIGatewayInvokeOpenAPI"
#   action        = "lambda:InvokeFunction"
#   function_name = aws_lambda_function.openapi.function_name
#   principal     = "apigateway.amazonaws.com"
#   source_arn    = "${aws_api_gateway_rest_api.incident_cmd.execution_arn}/*/GET/openapi.json"
# }

# API Gateway deployment and stage
# resource "aws_api_gateway_deployment" "incident_cmd" {
#   rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
#   triggers = {
#     redeploy = timestamp()
#   }
#   lifecycle {
#     create_before_destroy = true
#   }
#   # depends_on = [
#   #   aws_api_gateway_integration.openapi_json_get, # /openapi.json API endpoint
#   #   local.auth_integrations,                      # /auth API endpoints
#   #   local.organizations_integrations,             # /organizations API endpoints
#   #   local.incidents_integrations,                 # /incidents API endpoints
#   #   local.units_integrations,                     # /units API endpoints
#   #   local.locations_integrations,                 # /locations API endpoints
#   #   local.periods_integrations,                   # /periods API endpoints
#   #   local.volunteers_integrations,                # /volunteers API endpoints
#   #   local.radios_integrations,                    # /radios API endpoints
#   #   local.activitylogs_integrations,              # /activitylogs API endpoints
#   #   local.reports_integrations,                   # /reports API endpoints
#   # ]
# }

# resource "aws_api_gateway_stage" "v1" {
#   deployment_id = aws_api_gateway_deployment.incident_cmd.id
#   rest_api_id   = aws_api_gateway_rest_api.incident_cmd.id
#   stage_name    = "v1"
# }

moved {
  from = aws_api_gateway_rest_api.incident_cmd
  to   = module.api.aws_api_gateway_rest_api.this[0]
}

moved {
  from = aws_api_gateway_stage.v1
  to   = module.api.aws_api_gateway_stage.this[0]
}

moved {
  from = aws_api_gateway_deployment.incident_cmd
  to   = module.api.aws_api_gateway_deployment.this[0]
}

module "api" {
  source  = "cloudposse/api-gateway/aws"
  version = "0.9.0"

  openapi_config       = templatefile("${path.module}/openapi.tftpl", merge({}, local.lambda_invoke_arn_map))
  stage_name           = var.stage_name
  xray_tracing_enabled = true
  context              = module.this.context
}
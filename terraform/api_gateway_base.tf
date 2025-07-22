# API Gateway REST API for Incident Command
resource "aws_api_gateway_rest_api" "incident_cmd" {
  name        = "incident-cmd-api"
  description = "API for Security Incident Command Application"
  endpoint_configuration {
    types = ["REGIONAL"]
  }
}

data "aws_api_gateway_resource" "root" {
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  path        = "/"
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
    # ICS214 integrations
    aws_api_gateway_integration.ics214_periods_post,
    aws_api_gateway_integration.ics214_periods_options,
    aws_api_gateway_integration.ics214_periods_get,
    aws_api_gateway_integration.ics214_period_id_put,
    aws_api_gateway_integration.ics214_period_id_options,
    aws_api_gateway_integration.ics214_period_id_get,
    aws_api_gateway_integration.ics214_period_id_delete,
    aws_api_gateway_integration.ics214_options,
    aws_api_gateway_integration.ics214_get,
    # Auth integrations
    aws_api_gateway_integration.auth_login_post,
    aws_api_gateway_integration.auth_login_options,
    # Activitylogs integrations
    aws_api_gateway_integration.activitylogs_options,
    aws_api_gateway_integration.activitylogs_id_options,
    aws_api_gateway_integration.activitylogs_id_get,
    aws_api_gateway_integration.activitylogs_get,
    # Volunteers integrations
    aws_api_gateway_integration.volunteers_post,
    aws_api_gateway_integration.volunteers_options,
    aws_api_gateway_integration.volunteers_get,
    aws_api_gateway_integration.volunteer_id_put,
    aws_api_gateway_integration.volunteer_id_options,
    aws_api_gateway_integration.volunteer_id_get,
    aws_api_gateway_integration.volunteer_id_dispatch_post,
    aws_api_gateway_integration.volunteer_id_dispatch_options,
    aws_api_gateway_integration.volunteer_id_delete,
    aws_api_gateway_integration.volunteer_id_checkout_post,
    aws_api_gateway_integration.volunteer_id_checkout_options,
    aws_api_gateway_integration.volunteer_id_checkin_post,
    aws_api_gateway_integration.volunteer_id_checkin_options,
  ]
}

resource "aws_api_gateway_stage" "v1" {
  deployment_id = aws_api_gateway_deployment.incident_cmd.id
  rest_api_id   = aws_api_gateway_rest_api.incident_cmd.id
  stage_name    = "v1"
}

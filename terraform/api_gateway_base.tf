# API Gateway REST API for Incident Command
resource "aws_api_gateway_rest_api" "incident_cmd" {
  name        = "incident-cmd-api"
  description = "API for Security Incident Command Application"
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
}

resource "aws_api_gateway_stage" "v1" {
  deployment_id = aws_api_gateway_deployment.incident_cmd.id
  rest_api_id   = aws_api_gateway_rest_api.incident_cmd.id
  stage_name    = "v1"
}

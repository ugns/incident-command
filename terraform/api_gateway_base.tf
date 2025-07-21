# API Gateway REST API for Incident Command
resource "aws_api_gateway_rest_api" "incident_cmd" {
  name        = "incident-cmd-api"
  description = "API for Security Incident Command Application"
}

data "aws_api_gateway_resource" "root" {
  rest_api_id = aws_api_gateway_rest_api.incident_cmd.id
  path        = "/"
}

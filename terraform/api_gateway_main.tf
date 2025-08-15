module "api" {
  source  = "cloudposse/api-gateway/aws"
  version = "0.9.0"

  openapi_config       = templatefile("${path.module}/openapi.tftpl", merge({}, local.lambda_invoke_arn_map))
  stage_name           = var.stage_name
  xray_tracing_enabled = true
  endpoint_type        = "REGIONAL"
  logging_level        = "OFF"
  context              = module.this.context
}

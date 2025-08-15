locals {
  ws_lambdas = {
    ws_connect = {
      handler = null
      environment = {
        LOG_LEVEL            = "INFO"
        WS_CONNECTIONS_TABLE = aws_dynamodb_table.ws_connections.name
        JWKS_URL             = "https://${aws_api_gateway_domain_name.custom.domain_name}/.well-known/jwks.json"
      }
      source_arn = "${aws_apigatewayv2_api.ws_api.execution_arn}/*/$connect"
    }
    ws_disconnect = {
      handler = null
      environment = {
        LOG_LEVEL            = "INFO"
        WS_CONNECTIONS_TABLE = aws_dynamodb_table.ws_connections.name
      }
      source_arn = "${aws_apigatewayv2_api.ws_api.execution_arn}/*/$disconnect"
    }
    ws_default = {
      handler = null
      environment = {
        LOG_LEVEL            = "INFO"
        WS_CONNECTIONS_TABLE = aws_dynamodb_table.ws_connections.name
      }
      source_arn = "${aws_apigatewayv2_api.ws_api.execution_arn}/*/$default"
    }
    notify_ws_stream = {
      handler = null
      environment = {
        LOG_LEVEL            = "INFO"
        WS_CONNECTIONS_TABLE = aws_dynamodb_table.ws_connections.name
        WS_API_ENDPOINT      = "https://${aws_apigatewayv2_domain_name.custom.domain_name}/ws"
      }
      source_arn = null
    }
  }
}

# Lambda function archive ZIP files
data "archive_file" "ws_lambda" {
  for_each    = local.ws_lambdas
  type        = "zip"
  source_dir  = "../lambda/${each.key}"
  output_path = "../lambda/${each.key}.zip"
}

module "ws_lambda_label" {
  source   = "cloudposse/label/null"
  version  = "0.25.0"
  for_each = local.ws_lambdas

  name    = each.key
  context = module.this.context
}

# Lambda functions for WebSocket API
module "ws_lambda" {
  source   = "cloudposse/lambda-function/aws"
  version  = "0.6.1"
  for_each = local.ws_lambdas

  function_name                      = module.ws_lambda_label[each.key].id
  handler                            = each.value.handler != null ? each.value.handler : "handler.lambda_handler"
  filename                           = data.archive_file.ws_lambda[each.key].output_path
  source_code_hash                   = data.archive_file.ws_lambda[each.key].output_base64sha256
  timeout                            = 30
  layers                             = [aws_lambda_layer_version.shared.arn]
  lambda_environment                 = each.value.environment != null ? { variables = each.value.environment } : null
  invoke_function_permissions        = each.value.source_arn != null ? [{ principal = "apigateway.amazonaws.com", source_arn = each.value.source_arn }] : []
  cloudwatch_logs_retention_in_days  = 14
  cloudwatch_lambda_insights_enabled = true
  tracing_config_mode                = "Active"
  runtime                            = var.lambda_runtime
  attributes                         = ["handler"]
  context                            = module.ws_lambda_label[each.key].context
}

resource "aws_iam_role_policy_attachment" "ws_dynamodb" {
  for_each   = local.ws_lambdas
  policy_arn = aws_iam_policy.ws_lambda_dynamodb_policy.arn
  role       = module.ws_lambda[each.key].role_name
}

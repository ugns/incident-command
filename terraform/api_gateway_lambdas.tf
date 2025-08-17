locals {
  lambda_invoke_arn_map = {
    for name, _ in local.lambdas :
    "${name}_invoke_arn" => module.lambda[name].invoke_arn
  }

  api_gateway_source_arn = "arn:aws:execute-api:${data.aws_region.current.region}:${data.aws_caller_identity.current.account_id}:*/*/*"

  lambdas = {
    openapi = {
      handler     = null
      environment = null
    }
    login = {
      handler = null
      environment = {
        LOG_LEVEL                  = "DEBUG"
        JWT_PRIVATE_KEY_SECRET_ARN = aws_secretsmanager_secret.jwt_private_key.arn
        JWT_ISSUER                 = "https://${aws_api_gateway_domain_name.custom.domain_name}"
        LAUNCHDARKLY_SDK_KEY       = data.launchdarkly_environment.production.api_key
      }
    }
    authorizer = {
      handler = null
      environment = {
        LOG_LEVEL            = "DEBUG"
        JWKS_URL             = "https://${aws_api_gateway_domain_name.custom.domain_name}/.well-known/jwks.json"
        LAUNCHDARKLY_SDK_KEY = data.launchdarkly_environment.production.api_key
      }
    }
    well_known = {
      handler = "jwks.lambda_handler"
      environment = {
        JWT_PUBLIC_KEY_SECRET_ARN = aws_secretsmanager_secret.jwt_public_key.arn
      }
    }
    volunteers = {
      handler = null
      environment = {
        LOG_LEVEL            = "INFO"
        VOLUNTEERS_TABLE     = aws_dynamodb_table.volunteers.name
        JWKS_URL             = "https://${aws_api_gateway_domain_name.custom.domain_name}/.well-known/jwks.json"
        LAUNCHDARKLY_SDK_KEY = data.launchdarkly_environment.production.api_key
      }
    }
    activitylogs = {
      handler = null
      environment = {
        LOG_LEVEL            = "INFO"
        ACTIVITY_LOGS_TABLE  = aws_dynamodb_table.activity_logs.name
        JWKS_URL             = "https://${aws_api_gateway_domain_name.custom.domain_name}/.well-known/jwks.json"
        LAUNCHDARKLY_SDK_KEY = data.launchdarkly_environment.production.api_key
      }
    }
    periods = {
      handler = null
      environment = {
        LOG_LEVEL            = "INFO"
        ICS_PERIODS_TABLE    = aws_dynamodb_table.periods.name
        JWKS_URL             = "https://${aws_api_gateway_domain_name.custom.domain_name}/.well-known/jwks.json"
        LAUNCHDARKLY_SDK_KEY = data.launchdarkly_environment.production.api_key
      }
    }
    reports = {
      handler = null
      environment = {
        LOG_LEVEL            = "INFO"
        ICS214_TEMPLATE_PDF  = "ICS-214-v31.pdf"
        ICS214_FIELDS_JSON   = "ICS-214-v31.json"
        JWKS_URL             = "https://${aws_api_gateway_domain_name.custom.domain_name}/.well-known/jwks.json"
        LAUNCHDARKLY_SDK_KEY = data.launchdarkly_environment.production.api_key
      }
    }
    organizations = {
      handler = null
      environment = {
        LOG_LEVEL            = "INFO"
        ORGANIZATIONS_TABLE  = aws_dynamodb_table.organizations.name
        JWKS_URL             = "https://${aws_api_gateway_domain_name.custom.domain_name}/.well-known/jwks.json"
        LAUNCHDARKLY_SDK_KEY = data.launchdarkly_environment.production.api_key
      }
    }
    locations = {
      handler = null
      environment = {
        LOG_LEVEL            = "INFO"
        LOCATIONS_TABLE      = aws_dynamodb_table.locations.name
        JWKS_URL             = "https://${aws_api_gateway_domain_name.custom.domain_name}/.well-known/jwks.json"
        LAUNCHDARKLY_SDK_KEY = data.launchdarkly_environment.production.api_key
      }
    }
    radios = {
      handler = null
      environment = {
        LOG_LEVEL            = "INFO"
        RADIOS_TABLE         = aws_dynamodb_table.radios.name
        JWKS_URL             = "https://${aws_api_gateway_domain_name.custom.domain_name}/.well-known/jwks.json"
        LAUNCHDARKLY_SDK_KEY = data.launchdarkly_environment.production.api_key
      }
    }
    units = {
      handler = null
      environment = {
        LOG_LEVEL            = "INFO"
        UNITS_TABLE          = aws_dynamodb_table.units.name
        JWKS_URL             = "https://${aws_api_gateway_domain_name.custom.domain_name}/.well-known/jwks.json"
        LAUNCHDARKLY_SDK_KEY = data.launchdarkly_environment.production.api_key
      }
    }
    incidents = {
      handler = null
      environment = {
        LOG_LEVEL            = "INFO"
        INCIDENTS_TABLE      = aws_dynamodb_table.incidents.name
        JWKS_URL             = "https://${aws_api_gateway_domain_name.custom.domain_name}/.well-known/jwks.json"
        LAUNCHDARKLY_SDK_KEY = data.launchdarkly_environment.production.api_key
      }
    }
  }
}

# Shared Layer for Python dependencies
data "archive_file" "shared_layer" {
  type        = "zip"
  source_dir  = "../shared"
  output_path = "../lambda/shared.zip"
}

resource "aws_lambda_layer_version" "shared" {
  filename            = data.archive_file.shared_layer.output_path
  layer_name          = "event_coord_shared"
  compatible_runtimes = [var.lambda_runtime]
  source_code_hash    = data.archive_file.shared_layer.output_base64sha256
  description         = "Shared Python dependencies and code for Event Coordination Lambdas"
}

# Lambda function archive ZIP files
data "archive_file" "lambda" {
  for_each    = local.lambdas
  type        = "zip"
  source_dir  = "../lambda/${each.key}"
  output_path = "../lambda/${each.key}.zip"
}

module "lambda_label" {
  source   = "cloudposse/label/null"
  version  = "0.25.0"
  for_each = local.lambdas

  name    = each.key
  context = module.this.context
}

# Lambda Functions for REST API
module "lambda" {
  source   = "cloudposse/lambda-function/aws"
  version  = "0.6.1"
  for_each = local.lambdas

  function_name                      = module.lambda_label[each.key].id
  handler                            = each.value.handler != null ? each.value.handler : "handler.lambda_handler"
  filename                           = data.archive_file.lambda[each.key].output_path
  source_code_hash                   = data.archive_file.lambda[each.key].output_base64sha256
  timeout                            = 120
  layers                             = [aws_lambda_layer_version.shared.arn]
  lambda_environment                 = each.value.environment != null ? { variables = each.value.environment } : null
  invoke_function_permissions        = [{ principal = "apigateway.amazonaws.com", source_arn = local.api_gateway_source_arn }]
  cloudwatch_logs_retention_in_days  = 14
  cloudwatch_lambda_insights_enabled = true
  tracing_config_mode                = "Active"
  runtime                            = var.lambda_runtime
  attributes                         = ["handler"]
  context                            = module.lambda_label[each.key].context
}

resource "aws_iam_role_policy_attachment" "dynamodb" {
  for_each   = local.lambdas
  policy_arn = aws_iam_policy.lambda_dynamodb_policy.arn
  role       = module.lambda[each.key].role_name
}

resource "aws_iam_role_policy_attachment" "apigateway" {
  for_each   = local.lambdas
  policy_arn = aws_iam_policy.lambda_apigateway_policy.arn
  role       = module.lambda[each.key].role_name
}

resource "aws_iam_role_policy_attachment" "secretsmanager" {
  for_each   = local.lambdas
  policy_arn = aws_iam_policy.lambda_secretsmanager_policy.arn
  role       = module.lambda[each.key].role_name
}

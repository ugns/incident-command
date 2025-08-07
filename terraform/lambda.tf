# API Gateway resources and methods for /incidents and /incidents/{incidentId}
data "aws_region" "current" {}

# Lambda IAM Role
resource "aws_iam_role" "lambda_exec" {
  name = "incident_cmd_lambda_exec"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

# Lambda IAM Policies
resource "aws_iam_role_policy" "lambda_basic_execution" {
  name = "incident_cmd_lambda_basic_execution"
  role = aws_iam_role.lambda_exec.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ]
      Resource = "arn:aws:logs:*:*:*"
    }]
  })
}

resource "aws_iam_role_policy" "lambda_dynamodb_policy" {
  name = "incident_cmd_lambda_dynamodb_policy"
  role = aws_iam_role.lambda_exec.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:DeleteItem",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:GetItem",
          "dynamodb:Scan",
          "dynamodb:Query"
        ]
        Resource = [
          aws_dynamodb_table.units.arn,
          "${aws_dynamodb_table.units.arn}/index/*",
          aws_dynamodb_table.periods.arn,
          "${aws_dynamodb_table.periods.arn}/index/*",
          aws_dynamodb_table.incidents.arn,
          "${aws_dynamodb_table.incidents.arn}/index/*",
          aws_dynamodb_table.volunteers.arn,
          "${aws_dynamodb_table.volunteers.arn}/index/*",
          aws_dynamodb_table.activity_logs.arn,
          "${aws_dynamodb_table.activity_logs.arn}/index/*",
          aws_dynamodb_table.organizations.arn,
          "${aws_dynamodb_table.organizations.arn}/index/*",
          aws_dynamodb_table.locations.arn,
          "${aws_dynamodb_table.locations.arn}/index/*",
          aws_dynamodb_table.radios.arn,
          "${aws_dynamodb_table.radios.arn}/index/*",
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "dynamodb:BatchGetItem",
          "dynamodb:BatchWriteItem"
        ]
        Resource = [
          aws_dynamodb_table.units.arn,
          "${aws_dynamodb_table.units.arn}/index/*",
          aws_dynamodb_table.periods.arn,
          "${aws_dynamodb_table.periods.arn}/index/*",
          aws_dynamodb_table.incidents.arn,
          "${aws_dynamodb_table.incidents.arn}/index/*",
          aws_dynamodb_table.volunteers.arn,
          "${aws_dynamodb_table.volunteers.arn}/index/*",
          aws_dynamodb_table.activity_logs.arn,
          "${aws_dynamodb_table.activity_logs.arn}/index/*",
          aws_dynamodb_table.organizations.arn,
          "${aws_dynamodb_table.organizations.arn}/index/*",
          aws_dynamodb_table.locations.arn,
          "${aws_dynamodb_table.locations.arn}/index/*",
          aws_dynamodb_table.radios.arn,
          "${aws_dynamodb_table.radios.arn}/index/*",
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy" "lambda_apigateway_policy" {
  name = "incident_cmd_lambda_apigateway_policy"
  role = aws_iam_role.lambda_exec.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "apigateway:GET"
        ]
        Resource = [
          format(
            "arn:aws:apigateway:%s::/restapis/%s/stages/*/exports/*",
            data.aws_region.current.region,
            aws_api_gateway_rest_api.incident_cmd.id
          )
        ]
      }
    ]
  })
}

# Lambda Secrets Manager Policy
resource "aws_iam_role_policy" "lambda_secretsmanager_policy" {
  name = "incident_cmd_lambda_secretsmanager_policy"
  role = aws_iam_role.lambda_exec.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret",
          "secretsmanager:ListSecretVersionIds"
        ]
        Resource = [
          aws_secretsmanager_secret.jwt_private_key.arn,
          aws_secretsmanager_secret.jwt_public_key.arn
        ]
      }
    ]
  })
}

# Lambda Functions

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

# OpenAPI Export Lambda
data "archive_file" "openapi" {
  type        = "zip"
  source_dir  = "../lambda/openapi"
  output_path = "../lambda/openapi.zip"
}

resource "aws_lambda_function" "openapi" {
  function_name    = "openapi_export"
  filename         = data.archive_file.openapi.output_path
  handler          = "handler.lambda_handler"
  runtime          = var.lambda_runtime
  role             = aws_iam_role.lambda_exec.arn
  source_code_hash = data.archive_file.openapi.output_base64sha256
  layers           = [aws_lambda_layer_version.shared.arn]

  environment {
    variables = {
      REST_API_ID = aws_api_gateway_rest_api.incident_cmd.id
      # TODO: Remember to set the stage name when it changes
      # STAGE_NAME  = aws_api_gateway_stage.v1.stage_name
      STAGE_NAME = "v1"
    }
  }
}

# Auth: single zip for callback handler
data "archive_file" "auth" {
  type        = "zip"
  source_dir  = "../lambda/auth"
  output_path = "../lambda/auth.zip"
}
resource "aws_lambda_function" "auth_callback" {
  function_name    = "auth_callback"
  filename         = data.archive_file.auth.output_path
  handler          = "handler.lambda_handler"
  runtime          = var.lambda_runtime
  role             = aws_iam_role.lambda_exec.arn
  source_code_hash = data.archive_file.auth.output_base64sha256
  layers           = [aws_lambda_layer_version.shared.arn]

  environment {
    variables = {
      LOG_LEVEL                  = "DEBUG"
      JWT_PRIVATE_KEY_SECRET_ARN = aws_secretsmanager_secret.jwt_private_key.arn
      JWT_ISSUER                 = "https://${aws_api_gateway_domain_name.custom.domain_name}"
      LAUNCHDARKLY_SDK_KEY       = data.launchdarkly_environment.production.api_key
    }
  }
}

# Add JWKS Lambda deployment
data "archive_file" "jwks" {
  type        = "zip"
  source_dir  = "../lambda/auth"
  output_path = "../lambda/jwks.zip"
}

resource "aws_lambda_function" "jwks" {
  function_name    = "jwks"
  filename         = data.archive_file.jwks.output_path
  handler          = "jwks.lambda_handler"
  runtime          = var.lambda_runtime
  role             = aws_iam_role.lambda_exec.arn
  source_code_hash = data.archive_file.jwks.output_base64sha256
  layers           = [aws_lambda_layer_version.shared.arn]

  environment {
    variables = {
      JWT_PUBLIC_KEY_SECRET_ARN = aws_secretsmanager_secret.jwt_public_key.arn
    }
  }
}


# Volunteers: single zip, single handler
data "archive_file" "volunteers" {
  type        = "zip"
  source_dir  = "../lambda/volunteers"
  output_path = "../lambda/volunteers.zip"
}
resource "aws_lambda_function" "volunteers" {
  function_name    = "volunteers"
  filename         = data.archive_file.volunteers.output_path
  handler          = "handler.lambda_handler"
  runtime          = var.lambda_runtime
  role             = aws_iam_role.lambda_exec.arn
  source_code_hash = data.archive_file.volunteers.output_base64sha256
  layers           = [aws_lambda_layer_version.shared.arn]

  environment {
    variables = {
      LOG_LEVEL            = "DEBUG"
      VOLUNTEERS_TABLE     = aws_dynamodb_table.volunteers.name
      JWKS_URL             = "https://${aws_api_gateway_domain_name.custom.domain_name}/.well-known/jwks.json"
      LAUNCHDARKLY_SDK_KEY = data.launchdarkly_environment.production.api_key
    }
  }
}

# Activity Logs: single zip, single handler
data "archive_file" "activitylogs" {
  type        = "zip"
  source_dir  = "../lambda/activitylogs"
  output_path = "../lambda/activitylogs.zip"
}
resource "aws_lambda_function" "activitylogs" {
  function_name    = "activitylogs"
  filename         = data.archive_file.activitylogs.output_path
  handler          = "handler.lambda_handler"
  runtime          = var.lambda_runtime
  role             = aws_iam_role.lambda_exec.arn
  source_code_hash = data.archive_file.activitylogs.output_base64sha256
  layers           = [aws_lambda_layer_version.shared.arn]

  environment {
    variables = {
      LOG_LEVEL            = "DEBUG"
      ACTIVITY_LOGS_TABLE  = aws_dynamodb_table.activity_logs.name
      JWKS_URL             = "https://${aws_api_gateway_domain_name.custom.domain_name}/.well-known/jwks.json"
      LAUNCHDARKLY_SDK_KEY = data.launchdarkly_environment.production.api_key
    }
  }
}



# Periods: single zip, single handler
data "archive_file" "periods" {
  type        = "zip"
  source_dir  = "../lambda/periods"
  output_path = "../lambda/periods.zip"
}
resource "aws_lambda_function" "periods" {
  function_name    = "periods"
  filename         = data.archive_file.periods.output_path
  handler          = "handler.lambda_handler"
  runtime          = var.lambda_runtime
  role             = aws_iam_role.lambda_exec.arn
  source_code_hash = data.archive_file.periods.output_base64sha256
  layers           = [aws_lambda_layer_version.shared.arn]

  environment {
    variables = {
      LOG_LEVEL            = "DEBUG"
      ICS_PERIODS_TABLE    = aws_dynamodb_table.periods.name
      JWKS_URL             = "https://${aws_api_gateway_domain_name.custom.domain_name}/.well-known/jwks.json"
      LAUNCHDARKLY_SDK_KEY = data.launchdarkly_environment.production.api_key
    }
  }
}

# Reports: single zip, single handler
data "archive_file" "reports" {
  type        = "zip"
  source_dir  = "../lambda/reports"
  output_path = "../lambda/reports.zip"
}
resource "aws_lambda_function" "reports" {
  function_name    = "reports"
  filename         = data.archive_file.reports.output_path
  handler          = "handler.lambda_handler"
  runtime          = var.lambda_runtime
  role             = aws_iam_role.lambda_exec.arn
  source_code_hash = data.archive_file.reports.output_base64sha256
  timeout          = 30
  layers           = [aws_lambda_layer_version.shared.arn]

  environment {
    variables = {
      LOG_LEVEL            = "DEBUG"
      ICS214_TEMPLATE_PDF  = "ICS-214-v31.pdf"
      ICS214_FIELDS_JSON   = "ICS-214-v31.json"
      JWKS_URL             = "https://${aws_api_gateway_domain_name.custom.domain_name}/.well-known/jwks.json"
      LAUNCHDARKLY_SDK_KEY = data.launchdarkly_environment.production.api_key
    }
  }
}

# Organizations: single zip, single handler
data "archive_file" "organizations" {
  type        = "zip"
  source_dir  = "../lambda/organizations"
  output_path = "../lambda/organizations.zip"
}

resource "aws_lambda_function" "organizations" {
  function_name    = "organizations"
  filename         = data.archive_file.organizations.output_path
  handler          = "handler.lambda_handler"
  runtime          = var.lambda_runtime
  role             = aws_iam_role.lambda_exec.arn
  source_code_hash = data.archive_file.organizations.output_base64sha256
  layers           = [aws_lambda_layer_version.shared.arn]

  environment {
    variables = {
      LOG_LEVEL            = "DEBUG"
      ORGANIZATIONS_TABLE  = aws_dynamodb_table.organizations.name
      JWKS_URL             = "https://${aws_api_gateway_domain_name.custom.domain_name}/.well-known/jwks.json"
      LAUNCHDARKLY_SDK_KEY = data.launchdarkly_environment.production.api_key
    }
  }
}

# Archive and Lambda for Locations
data "archive_file" "locations_lambda" {
  type        = "zip"
  source_dir  = "../lambda/locations"
  output_path = "../lambda/locations.zip"
}

resource "aws_lambda_function" "locations" {
  function_name    = "locations-handler"
  handler          = "handler.lambda_handler"
  runtime          = var.lambda_runtime
  filename         = data.archive_file.locations_lambda.output_path
  source_code_hash = data.archive_file.locations_lambda.output_base64sha256
  role             = aws_iam_role.lambda_exec.arn
  layers           = [aws_lambda_layer_version.shared.arn]
  environment {
    variables = {
      LOG_LEVEL            = "DEBUG"
      LOCATIONS_TABLE      = aws_dynamodb_table.locations.name
      JWKS_URL             = "https://${aws_api_gateway_domain_name.custom.domain_name}/.well-known/jwks.json"
      LAUNCHDARKLY_SDK_KEY = data.launchdarkly_environment.production.api_key
    }
  }
}

# Archive and Lambda for Radios
data "archive_file" "radios_lambda" {
  type        = "zip"
  source_dir  = "../lambda/radios"
  output_path = "../lambda/radios.zip"
}

resource "aws_lambda_function" "radios" {
  function_name    = "radios-handler"
  handler          = "handler.lambda_handler"
  runtime          = var.lambda_runtime
  filename         = data.archive_file.radios_lambda.output_path
  source_code_hash = data.archive_file.radios_lambda.output_base64sha256
  role             = aws_iam_role.lambda_exec.arn
  layers           = [aws_lambda_layer_version.shared.arn]
  environment {
    variables = {
      LOG_LEVEL            = "DEBUG"
      RADIOS_TABLE         = aws_dynamodb_table.radios.name
      JWKS_URL             = "https://${aws_api_gateway_domain_name.custom.domain_name}/.well-known/jwks.json"
      LAUNCHDARKLY_SDK_KEY = data.launchdarkly_environment.production.api_key
    }
  }
}
# Archive and Lambda for Incidents
data "archive_file" "incidents_lambda" {
  type        = "zip"
  source_dir  = "../lambda/incidents"
  output_path = "../lambda/incidents.zip"
}

resource "aws_lambda_function" "incidents" {
  function_name    = "incidents-handler"
  handler          = "handler.lambda_handler"
  runtime          = var.lambda_runtime
  filename         = data.archive_file.incidents_lambda.output_path
  source_code_hash = data.archive_file.incidents_lambda.output_base64sha256
  role             = aws_iam_role.lambda_exec.arn
  layers           = [aws_lambda_layer_version.shared.arn]
  environment {
    variables = {
      LOG_LEVEL            = "DEBUG"
      INCIDENTS_TABLE      = aws_dynamodb_table.incidents.name
      JWKS_URL             = "https://${aws_api_gateway_domain_name.custom.domain_name}/.well-known/jwks.json"
      LAUNCHDARKLY_SDK_KEY = data.launchdarkly_environment.production.api_key
    }
  }
}

# Archive and Lambda for Units
data "archive_file" "units_lambda" {
  type        = "zip"
  source_dir  = "../lambda/units"
  output_path = "../lambda/units.zip"
}

resource "aws_lambda_function" "units" {
  function_name    = "units-handler"
  handler          = "handler.lambda_handler"
  runtime          = var.lambda_runtime
  filename         = data.archive_file.units_lambda.output_path
  source_code_hash = data.archive_file.units_lambda.output_base64sha256
  role             = aws_iam_role.lambda_exec.arn
  layers           = [aws_lambda_layer_version.shared.arn]
  environment {
    variables = {
      LOG_LEVEL            = "DEBUG"
      UNITS_TABLE          = aws_dynamodb_table.units.name
      JWKS_URL             = "https://${aws_api_gateway_domain_name.custom.domain_name}/.well-known/jwks.json"
      LAUNCHDARKLY_SDK_KEY = data.launchdarkly_environment.production.api_key
    }
  }
}

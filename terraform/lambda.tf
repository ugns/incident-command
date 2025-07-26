data "aws_region" "current" {}

# Generate a random JWT secret
resource "random_password" "jwt_secret" {
  length  = 32
  special = false
}

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
          aws_dynamodb_table.volunteers.arn,
          aws_dynamodb_table.activity_logs.arn,
          "${aws_dynamodb_table.activity_logs.arn}/index/*",
          aws_dynamodb_table.periods.arn
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "dynamodb:BatchGetItem",
          "dynamodb:BatchWriteItem"
        ]
        Resource = [
          aws_dynamodb_table.volunteers.arn,
          aws_dynamodb_table.activity_logs.arn,
          "${aws_dynamodb_table.activity_logs.arn}/index/*",
          aws_dynamodb_table.periods.arn
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
            data.aws_region.current.name,
            aws_api_gateway_rest_api.incident_cmd.id
          )
        ]
      }
    ]
  })
}

# Lambda Functions


# OpenAPI Export Lambda
data "archive_file" "openapi" {
  type        = "zip"
  source_dir  = "../lambda/docs"
  output_path = "../lambda/openapi.zip"
}

resource "aws_lambda_function" "openapi" {
  function_name    = "openapi_export"
  filename         = data.archive_file.openapi.output_path
  handler          = "openapi.lambda_handler"
  runtime          = var.lambda_runtime
  role             = aws_iam_role.lambda_exec.arn
  source_code_hash = data.archive_file.openapi.output_base64sha256
  environment {
    variables = {
      REST_API_ID = aws_api_gateway_rest_api.incident_cmd.id
      # TODO: Remember to set the stage name when it changes
      # STAGE_NAME  = aws_api_gateway_stage.v1.stage_name
      STAGE_NAME  = "v1"
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
  handler          = "callback.lambda_handler"
  runtime          = var.lambda_runtime
  role             = aws_iam_role.lambda_exec.arn
  source_code_hash = data.archive_file.auth.output_base64sha256
  environment {
    variables = {
      GOOGLE_CLIENT_IDS = var.google_client_ids
      JWT_SECRET        = random_password.jwt_secret.result
      ADMIN_EMAILS      = var.admin_emails
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
  handler          = "volunteers.lambda_handler"
  runtime          = var.lambda_runtime
  role             = aws_iam_role.lambda_exec.arn
  source_code_hash = data.archive_file.volunteers.output_base64sha256
  environment {
    variables = {
      VOLUNTEERS_TABLE    = aws_dynamodb_table.volunteers.name
      ACTIVITY_LOGS_TABLE = aws_dynamodb_table.activity_logs.name
      JWT_SECRET          = random_password.jwt_secret.result
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
  handler          = "activitylogs.lambda_handler"
  runtime          = var.lambda_runtime
  role             = aws_iam_role.lambda_exec.arn
  source_code_hash = data.archive_file.activitylogs.output_base64sha256
  environment {
    variables = {
      ACTIVITY_LOGS_TABLE = aws_dynamodb_table.activity_logs.name
      JWT_SECRET          = random_password.jwt_secret.result
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
  handler          = "periods.lambda_handler"
  runtime          = var.lambda_runtime
  role             = aws_iam_role.lambda_exec.arn
  source_code_hash = data.archive_file.periods.output_base64sha256
  environment {
    variables = {
      ICS_PERIODS_TABLE = aws_dynamodb_table.periods.name
      JWT_SECRET        = random_password.jwt_secret.result
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
  handler          = "reports.lambda_handler"
  runtime          = var.lambda_runtime
  role             = aws_iam_role.lambda_exec.arn
  source_code_hash = data.archive_file.reports.output_base64sha256
  environment {
    variables = {
      ICS214_TEMPLATE_PDF = "ICS-214-v31.pdf"
      ICS214_FIELDS_JSON  = "ICS-214-v31.json"
      JWT_SECRET          = random_password.jwt_secret.result
    }
  }
}

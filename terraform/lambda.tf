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
          aws_dynamodb_table.ics214_periods.arn
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      }
    ]
  })
}

# Lambda Functions


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



# ICS-214: single zip, single handler
data "archive_file" "ics214" {
  type        = "zip"
  source_dir  = "../lambda/ics214"
  output_path = "../lambda/ics214.zip"
}
resource "aws_lambda_function" "ics214" {
  function_name    = "ics214"
  filename         = data.archive_file.ics214.output_path
  handler          = "ics214.lambda_handler"
  runtime          = var.lambda_runtime
  role             = aws_iam_role.lambda_exec.arn
  source_code_hash = data.archive_file.ics214.output_base64sha256
  environment {
    variables = {
      ICS214_PERIODS_TABLE = aws_dynamodb_table.ics214_periods.name
      ACTIVITY_LOGS_TABLE  = aws_dynamodb_table.activity_logs.name
      JWT_SECRET           = random_password.jwt_secret.result
    }
  }
}

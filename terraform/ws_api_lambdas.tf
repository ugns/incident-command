# Dedicated IAM policy for WebSocket Lambda functions
resource "aws_iam_role_policy" "ws_lambda_dynamodb_policy" {
  name = "incident_cmd_ws_lambda_dynamodb_policy"
  role = aws_iam_role.lambda_exec.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:PutItem",
          "dynamodb:DeleteItem",
          "dynamodb:UpdateItem",
          "dynamodb:GetItem",
          "dynamodb:Query",
          "dynamodb:Scan"
        ]
        Resource = [
          aws_dynamodb_table.ws_connections.arn,
          "${aws_dynamodb_table.ws_connections.arn}/index/*"
        ]
      }
    ]
  })
}

# Lambda functions for WebSocket API

data "archive_file" "ws_connect" {
  type        = "zip"
  source_dir  = "../lambda/ws_connect"
  output_path = "../lambda/ws_connect.zip"
}
resource "aws_lambda_function" "ws_connect" {
  function_name    = "ws_connect"
  filename         = data.archive_file.ws_connect.output_path
  handler          = "handler.lambda_handler"
  runtime          = var.lambda_runtime
  role             = aws_iam_role.lambda_exec.arn
  source_code_hash = data.archive_file.ws_connect.output_base64sha256
  environment {
    variables = {
      WS_CONNECTIONS_TABLE = aws_dynamodb_table.ws_connections.name
      JWT_SECRET           = random_password.jwt_secret.result
    }
  }
  layers = [aws_lambda_layer_version.shared.arn]
}

data "archive_file" "ws_disconnect" {
  type        = "zip"
  source_dir  = "../lambda/ws_disconnect"
  output_path = "../lambda/ws_disconnect.zip"
}
resource "aws_lambda_function" "ws_disconnect" {
  function_name    = "ws_disconnect"
  filename         = data.archive_file.ws_disconnect.output_path
  handler          = "handler.lambda_handler"
  runtime          = var.lambda_runtime
  role             = aws_iam_role.lambda_exec.arn
  source_code_hash = data.archive_file.ws_disconnect.output_base64sha256
  environment {
    variables = {
      WS_CONNECTIONS_TABLE = aws_dynamodb_table.ws_connections.name
    }
  }
  layers = [aws_lambda_layer_version.shared.arn]
}

data "archive_file" "ws_default" {
  type        = "zip"
  source_dir  = "../lambda/ws_default"
  output_path = "../lambda/ws_default.zip"
}
resource "aws_lambda_function" "ws_default" {
  function_name    = "ws_default"
  filename         = data.archive_file.ws_default.output_path
  handler          = "handler.lambda_handler"
  runtime          = var.lambda_runtime
  role             = aws_iam_role.lambda_exec.arn
  source_code_hash = data.archive_file.ws_default.output_base64sha256
  environment {
    variables = {
      WS_CONNECTIONS_TABLE = aws_dynamodb_table.ws_connections.name
    }
  }
  layers = [aws_lambda_layer_version.shared.arn]
}

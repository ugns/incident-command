# Allow Lambda to manage WebSocket connections (for PostToConnection)
data "aws_caller_identity" "current" {}

# Event source mappings for DynamoDB Streams to notify_ws_stream Lambda
resource "aws_lambda_event_source_mapping" "notify_ws_stream_volunteers" {
  event_source_arn  = aws_dynamodb_table.volunteers.stream_arn
  function_name     = aws_lambda_function.notify_ws_stream.arn
  starting_position = "LATEST"
  batch_size        = 10
  enabled           = true
}

resource "aws_lambda_event_source_mapping" "notify_ws_stream_periods" {
  event_source_arn  = aws_dynamodb_table.periods.stream_arn
  function_name     = aws_lambda_function.notify_ws_stream.arn
  starting_position = "LATEST"
  batch_size        = 10
  enabled           = true
}

resource "aws_lambda_event_source_mapping" "notify_ws_stream_units" {
  event_source_arn  = aws_dynamodb_table.units.stream_arn
  function_name     = aws_lambda_function.notify_ws_stream.arn
  starting_position = "LATEST"
  batch_size        = 10
  enabled           = true
}

resource "aws_lambda_event_source_mapping" "notify_ws_stream_incidents" {
  event_source_arn  = aws_dynamodb_table.incidents.stream_arn
  function_name     = aws_lambda_function.notify_ws_stream.arn
  starting_position = "LATEST"
  batch_size        = 10
  enabled           = true
}

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
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetRecords",
          "dynamodb:GetShardIterator",
          "dynamodb:DescribeStream",
          "dynamodb:ListStreams"
        ]
        Resource = [
          aws_dynamodb_table.volunteers.stream_arn,
          aws_dynamodb_table.periods.stream_arn,
          aws_dynamodb_table.units.stream_arn,
          aws_dynamodb_table.incidents.stream_arn
        ]
      }
      ,
      {
        Effect = "Allow"
        Action = [
          "execute-api:ManageConnections"
        ]
        Resource = [
          format(
            "arn:aws:execute-api:%s:%s:%s/*/POST/@connections/*",
            data.aws_region.current.region,
            data.aws_caller_identity.current.account_id,
            aws_apigatewayv2_api.ws_api.id
          )
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
  function_name    = "EventCoord-ws_connect_handler"
  filename         = data.archive_file.ws_connect.output_path
  handler          = "handler.lambda_handler"
  runtime          = var.lambda_runtime
  role             = aws_iam_role.lambda_exec.arn
  source_code_hash = data.archive_file.ws_connect.output_base64sha256
  timeout          = 10
  layers           = [aws_lambda_layer_version.shared.arn]
  environment {
    variables = {
      WS_CONNECTIONS_TABLE = aws_dynamodb_table.ws_connections.name
      JWKS_URL             = "https://${aws_api_gateway_domain_name.custom.domain_name}/.well-known/jwks.json"
      LOG_LEVEL            = "DEBUG"
    }
  }
  tracing_config {
    mode = "Active"
  }
}

data "archive_file" "ws_disconnect" {
  type        = "zip"
  source_dir  = "../lambda/ws_disconnect"
  output_path = "../lambda/ws_disconnect.zip"
}
resource "aws_lambda_function" "ws_disconnect" {
  function_name    = "EventCoord-ws_disconnect_handler"
  filename         = data.archive_file.ws_disconnect.output_path
  handler          = "handler.lambda_handler"
  runtime          = var.lambda_runtime
  role             = aws_iam_role.lambda_exec.arn
  source_code_hash = data.archive_file.ws_disconnect.output_base64sha256
  timeout          = 10
  layers           = [aws_lambda_layer_version.shared.arn]
  environment {
    variables = {
      WS_CONNECTIONS_TABLE = aws_dynamodb_table.ws_connections.name
      LOG_LEVEL            = "DEBUG"
    }
  }
  tracing_config {
    mode = "Active"
  }
}

data "archive_file" "ws_default" {
  type        = "zip"
  source_dir  = "../lambda/ws_default"
  output_path = "../lambda/ws_default.zip"
}
resource "aws_lambda_function" "ws_default" {
  function_name    = "EventCoord-ws_default_handler"
  filename         = data.archive_file.ws_default.output_path
  handler          = "handler.lambda_handler"
  runtime          = var.lambda_runtime
  role             = aws_iam_role.lambda_exec.arn
  source_code_hash = data.archive_file.ws_default.output_base64sha256
  timeout          = 10
  layers           = [aws_lambda_layer_version.shared.arn]
  environment {
    variables = {
      WS_CONNECTIONS_TABLE = aws_dynamodb_table.ws_connections.name
      LOG_LEVEL            = "DEBUG"
    }
  }
  tracing_config {
    mode = "Active"
  }
}

# Archive and Lambda for notify_ws_stream (DynamoDB Streams handler)
data "archive_file" "notify_ws_stream" {
  type        = "zip"
  source_dir  = "../lambda/notify_ws_stream"
  output_path = "../lambda/notify_ws_stream.zip"
}

resource "aws_lambda_function" "notify_ws_stream" {
  function_name    = "EventCoord-notify_ws_stream_handler"
  filename         = data.archive_file.notify_ws_stream.output_path
  handler          = "handler.lambda_handler"
  runtime          = var.lambda_runtime
  role             = aws_iam_role.lambda_exec.arn
  source_code_hash = data.archive_file.notify_ws_stream.output_base64sha256
  timeout          = 10
  layers           = [aws_lambda_layer_version.shared.arn]
  environment {
    variables = {
      WS_CONNECTIONS_TABLE = aws_dynamodb_table.ws_connections.name
      WS_API_ENDPOINT      = "https://${aws_apigatewayv2_domain_name.custom.domain_name}/ws"
      LOG_LEVEL            = "DEBUG"
    }
  }
  tracing_config {
    mode = "Active"
  }
}

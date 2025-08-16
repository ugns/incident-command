# Lambda DynamoDB Policy
resource "aws_iam_policy" "lambda_dynamodb_policy" {
  name = format("%s_lambda_dynamodb_policy", module.this.id)
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

# Lambda API Gateway Policy
resource "aws_iam_policy" "lambda_apigateway_policy" {
  name = format("%s_lambda_apigateway_policy", module.this.id)
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
            module.api.id
          )
        ]
      }
    ]
  })
}

# Lambda Secrets Manager Policy
resource "aws_iam_policy" "lambda_secretsmanager_policy" {
  name = format("%s_lambda_secretsmanager_policy", module.this.id)
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

# IAM policy for WebSocket Lambda functions
resource "aws_iam_policy" "ws_lambda_dynamodb_policy" {
  name = format("%s_ws_lambda_dynamodb_policy", module.this.id)
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
          "${aws_dynamodb_table.ws_connections.arn}/index/*",
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

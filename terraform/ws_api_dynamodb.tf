# DynamoDB table for WebSocket connections
resource "aws_dynamodb_table" "ws_connections" {
  name         = "WebSocketConnections"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "orgId"
  range_key    = "connectionId"

  attribute {
    name = "orgId"
    type = "S"
  }
  attribute {
    name = "connectionId"
    type = "S"
  }

  global_secondary_index {
    name            = "ConnectionIdIndex"
    hash_key        = "connectionId"
    projection_type = "ALL"
  }
}

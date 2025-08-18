# WebSocket API Gateway
resource "aws_apigatewayv2_api" "ws_api" {
  name                         = "incident-cmd-ws-api"
  description                  = "WebSockets API for Event Coordination Application"
  disable_execute_api_endpoint = true
  protocol_type                = "WEBSOCKET"
  route_selection_expression   = "$request.body.action"
}

resource "aws_apigatewayv2_stage" "ws_api_stage" {
  api_id      = aws_apigatewayv2_api.ws_api.id
  name        = "v1"
  auto_deploy = true
}

resource "aws_apigatewayv2_authorizer" "ws_auth" {
  api_id           = aws_apigatewayv2_api.ws_api.id
  authorizer_type  = "REQUEST"
  authorizer_uri   = module.lambda["authorizer"].invoke_arn
  identity_sources = ["route.request.querystring.token"]
  name             = "WebSocketTokenAuthorizer"
}

# WebSocket routes
resource "aws_apigatewayv2_route" "ws_connect" {
  api_id             = aws_apigatewayv2_api.ws_api.id
  route_key          = "$connect"
  authorization_type = "CUSTOM"
  authorizer_id      = aws_apigatewayv2_authorizer.ws_auth.id
  target             = "integrations/${aws_apigatewayv2_integration.ws_connect.id}"
}
resource "aws_apigatewayv2_route" "ws_disconnect" {
  api_id    = aws_apigatewayv2_api.ws_api.id
  route_key = "$disconnect"
  target    = "integrations/${aws_apigatewayv2_integration.ws_disconnect.id}"
}
resource "aws_apigatewayv2_route" "ws_default" {
  api_id    = aws_apigatewayv2_api.ws_api.id
  route_key = "$default"
  target    = "integrations/${aws_apigatewayv2_integration.ws_default.id}"
}

# Event source mappings for DynamoDB Streams to notify_ws_stream Lambda
resource "aws_lambda_event_source_mapping" "notify_ws_stream_volunteers" {
  event_source_arn  = aws_dynamodb_table.volunteers.stream_arn
  function_name     = module.ws_lambda["notify_ws_stream"].function_name
  starting_position = "LATEST"
  batch_size        = 10
  enabled           = true
}

resource "aws_lambda_event_source_mapping" "notify_ws_stream_periods" {
  event_source_arn  = aws_dynamodb_table.periods.stream_arn
  function_name     = module.ws_lambda["notify_ws_stream"].function_name
  starting_position = "LATEST"
  batch_size        = 10
  enabled           = true
}

resource "aws_lambda_event_source_mapping" "notify_ws_stream_units" {
  event_source_arn  = aws_dynamodb_table.units.stream_arn
  function_name     = module.ws_lambda["notify_ws_stream"].function_name
  starting_position = "LATEST"
  batch_size        = 10
  enabled           = true
}

resource "aws_lambda_event_source_mapping" "notify_ws_stream_incidents" {
  event_source_arn  = aws_dynamodb_table.incidents.stream_arn
  function_name     = module.ws_lambda["notify_ws_stream"].function_name
  starting_position = "LATEST"
  batch_size        = 10
  enabled           = true
}

resource "aws_lambda_event_source_mapping" "notify_ws_stream_locations" {
  event_source_arn  = aws_dynamodb_table.locations.stream_arn
  function_name     = module.ws_lambda["notify_ws_stream"].function_name
  starting_position = "LATEST"
  batch_size        = 10
  enabled           = true
}

resource "aws_lambda_event_source_mapping" "notify_ws_stream_radios" {
  event_source_arn  = aws_dynamodb_table.radios.stream_arn
  function_name     = module.ws_lambda["notify_ws_stream"].function_name
  starting_position = "LATEST"
  batch_size        = 10
  enabled           = true
}

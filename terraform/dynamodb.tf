# DynamoDB Tables for Incident Command App

# ICS-214 Operating Periods Table
# This table stores ICS-214 operating periods, indexed by period_id
# It allows querying periods by their unique period_id.
# The period_id is a unique identifier for each operating period.
# The table also includes an org_id to scope periods to a specific organization.
# The org_id is used to associate periods with their respective organizations.
resource "aws_dynamodb_table" "ics214_periods" {
  name         = "ics214_periods"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "org_id"
  range_key    = "periodId"

  attribute {
    name = "org_id"
    type = "S"
  }
  attribute {
    name = "periodId"
    type = "S"
  }
  # attribute {
  #   name = "startTime"
  #   type = "S"
  # }
  # attribute {
  #   name = "endTime"
  #   type = "S"
  # }
  # attribute {
  #   name = "name"
  #   type = "S"
  # }
  tags = {
    Name = "ics214_periods"
  }
}

# Volunteers Table
# This table stores volunteer information, indexed by volunteerId
# It allows querying volunteers by their unique volunteerId.
# The volunteerId is a unique identifier for each volunteer.
# The table also includes an org_id to scope volunteers to a specific organization.
# The org_id is used to associate volunteers with their respective organizations.
resource "aws_dynamodb_table" "volunteers" {
  name         = "volunteers"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "org_id"
  range_key    = "volunteerId"

  attribute {
    name = "org_id"
    type = "S"
  }
  attribute {
    name = "volunteerId"
    type = "S"
  }
  # attribute {
  #   name = "name"
  #   type = "S"
  # }
  tags = {
    Name = "volunteers"
  }
}

# Activity Logs Table
# This table stores activity logs for volunteers
# It allows querying logs by volunteerId for efficient retrieval
# The table uses a hash key of logId and a global secondary index on volunteerId
# to support queries based on volunteerId.
# The logId is a unique identifier for each activity log entry.
# The volunteerId is used to associate logs with specific volunteers.
# The table also includes a global secondary index on periodId to support queries
# based on operating periods.
# The org_id is used to scope the logs to a specific organization.
# The periodId is used to associate logs with specific operating periods.
resource "aws_dynamodb_table" "activity_logs" {
  name         = "activity_logs"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "org_id"
  range_key    = "logId"

  attribute {
    name = "org_id"
    type = "S"
  }
  attribute {
    name = "logId"
    type = "S"
  }
  attribute {
    name = "volunteerId"
    type = "S"
  }
  attribute {
    name = "periodId"
    type = "S"
  }
  # attribute {
  #   name = "timestamp"
  #   type = "S"
  # }
  tags = {
    Name = "activity_logs"
  }

  global_secondary_index {
    name            = "VolunteerIdIndex"
    hash_key        = "org_id"
    range_key       = "volunteerId"
    projection_type = "ALL"
  }

  global_secondary_index {
    name            = "PeriodIdIndex"
    hash_key        = "org_id"
    range_key       = "periodId"
    projection_type = "ALL"
  }
}

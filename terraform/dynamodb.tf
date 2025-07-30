# Units Table
# This table stores unit information, indexed by unitId and scoped to an organization by org_id.
resource "aws_dynamodb_table" "units" {
  name         = "units"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "org_id"
  range_key    = "unitId"

  attribute {
    name = "org_id"
    type = "S"
  }
  attribute {
    name = "unitId"
    type = "S"
  }
  stream_enabled   = true
  stream_view_type = "NEW_AND_OLD_IMAGES"
  tags = {
    Name = "units"
  }
}
# DynamoDB Tables for Incident Command App

# ICS-214 Operating Periods Table
# This table stores ICS-214 operating periods, indexed by period_id
# It allows querying periods by their unique period_id.
# The period_id is a unique identifier for each operating period.
# The table also includes an org_id to scope periods to a specific organization.
# The org_id is used to associate periods with their respective organizations.
resource "aws_dynamodb_table" "periods" {
  name         = "periods"
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
  attribute {
    name = "incidentId"
    type = "S"
  }
  attribute {
    name = "unitId"
    type = "S"
  }
  global_secondary_index {
    name            = "incidentId-index"
    hash_key        = "org_id"
    range_key       = "incidentId"
    projection_type = "ALL"
  }
  global_secondary_index {
    name            = "unitId-index"
    hash_key        = "org_id"
    range_key       = "unitId"
    projection_type = "ALL"
  }
  stream_enabled   = true
  stream_view_type = "NEW_AND_OLD_IMAGES"
  tags = {
    Name = "periods"
  }
}

# Incidents Table
# This table stores incident information, indexed by incidentId and scoped to an organization by org_id.
resource "aws_dynamodb_table" "incidents" {
  name         = "incidents"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "org_id"
  range_key    = "incidentId"

  attribute {
    name = "org_id"
    type = "S"
  }
  attribute {
    name = "incidentId"
    type = "S"
  }
  stream_enabled   = true
  stream_view_type = "NEW_AND_OLD_IMAGES"
  tags = {
    Name = "incidents"
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
  attribute {
    name = "email"
    type = "S"
  }

  global_secondary_index {
    name            = "email-index"
    hash_key        = "org_id"
    range_key       = "email"
    projection_type = "ALL"
  }
  stream_enabled   = true
  stream_view_type = "NEW_AND_OLD_IMAGES"
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
  name                        = "activity_logs"
  billing_mode                = "PAY_PER_REQUEST"
  hash_key                    = "org_id"
  range_key                   = "logId"
  deletion_protection_enabled = true

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

# Organizations Table
# This table stores organization information, indexed by org_id
# It allows querying organizations by their unique org_id.
# The org_id is a unique identifier for each organization.
# The table also includes an aud attribute to scope organizations to a specific audience.
# The aud attribute is used to associate organizations with their respective audiences.
# The table supports a global secondary index on the aud attribute for efficient querying.
# The aud attribute is used to scope organizations to a specific audience.
resource "aws_dynamodb_table" "organizations" {
  name         = "organizations"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "org_id"

  attribute {
    name = "org_id"
    type = "S"
  }
  attribute {
    name = "aud"
    type = "S"
  }

  global_secondary_index {
    name            = "aud-index"
    hash_key        = "aud"
    projection_type = "ALL"
  }

  tags = {
    Name = "organizations"
  }
}

# DynamoDB table for Locations

resource "aws_dynamodb_table" "locations" {
  name         = "locations"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "org_id"
  range_key    = "locationId"
  attribute {
    name = "org_id"
    type = "S"
  }
  attribute {
    name = "locationId"
    type = "S"
  }
  tags = {
    Name = "locations"
  }
}

# DynamoDB table for Radios

resource "aws_dynamodb_table" "radios" {
  name         = "radios"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "org_id"
  range_key    = "radioId"
  attribute {
    name = "org_id"
    type = "S"
  }
  attribute {
    name = "radioId"
    type = "S"
  }
  tags = {
    Name = "radios"
  }
}

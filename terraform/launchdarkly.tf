# LaunchDarkly Terraform Setup for Incident Command

# Provider Configuration

provider "launchdarkly" {
  access_token = var.launchdarkly_access_token
}

# Project with environment defined inline
resource "launchdarkly_project" "incident_cmd" {
  key  = "incident-cmd"
  name = "Event Coordination"
  environments {
    key  = "production"
    name = "Production"
    color = "#0073e6"
  }
}

# Lookup environment for API key and client_side_id
data "launchdarkly_environment" "production" {
  project_key = launchdarkly_project.incident_cmd.key
  key         = "production"
}

# Feature Flag: admin-access
resource "launchdarkly_feature_flag" "admin_access" {
  project_key = launchdarkly_project.incident_cmd.key
  key         = "admin-access"
  name        = "Admin Access"
  description = "Controls admin access for users via feature flag."
  variations  = [
    { value = true, name = "Enabled" },
    { value = false, name = "Disabled" }
  ]
  tags        = ["access", "admin"]
  temporary   = false
  client_side = true
  environments {
    production {
      fallthrough = { variation = true }
      off_variation = false
      # Optionally, add targeting rules here
    }
  }
}

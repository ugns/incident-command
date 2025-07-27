# LaunchDarkly Terraform Setup for Incident Command

# 1. Provider Configuration
provider "launchdarkly" {
  access_token = var.launchdarkly_access_token
}

# 2. Project and Environment (optional, if not already created)
resource "launchdarkly_project" "incident_cmd" {
  key  = "incident-cmd"
  name = "Incident Command"
}

resource "launchdarkly_environment" "production" {
  project_key = launchdarkly_project.incident_cmd.key
  key         = "production"
  name        = "Production"
}

# 3. Feature Flag: admin-access
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

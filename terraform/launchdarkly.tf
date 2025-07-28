# Project with environment defined inline
resource "launchdarkly_project" "incident_cmd" {
  key  = "incident-cmd"
  name = "Event Coordination"

  environments {
    key   = "production"
    name  = "Production"
    color = "0073e6"
  }

  default_client_side_availability {
    using_environment_id = true
    using_mobile_key     = false
  }
}

# Lookup environment for API key and client_side_id
data "launchdarkly_environment" "production" {
  project_key = launchdarkly_project.incident_cmd.key
  key         = "production"
}

# Feature Flag: admin-access
resource "launchdarkly_feature_flag" "admin_access" {
  project_key    = launchdarkly_project.incident_cmd.key
  key            = "admin-access"
  name           = "Admin Access"
  description    = "Controls admin access for users via feature flag."
  tags           = ["access", "admin", "managed-by-terraform"]
  temporary      = false
  variation_type = "boolean"

  variations {
    value = true
    name  = "Enabled"
  }

  variations {
    value = false
    name  = "Disabled"
  }

  defaults {
    on_variation  = 0
    off_variation = 1
  }

  client_side_availability {
    using_environment_id = true
    using_mobile_key     = false
  }
}

resource "launchdarkly_feature_flag" "show_radio_resources" {
  project_key    = launchdarkly_project.incident_cmd.key
  key            = "show-radio-resources"
  name           = "Show Radio Resources"
  description    = "Controls visibility of radio resources."
  tags           = ["features", "radios", "resources", "managed-by-terraform"]
  temporary      = false
  variation_type = "boolean"

  variations {
    value = true
    name  = "Enabled"
  }

  variations {
    value = false
    name  = "Disabled"
  }

  defaults {
    on_variation  = 0
    off_variation = 1
  }

  client_side_availability {
    using_environment_id = true
    using_mobile_key     = false
  }
}

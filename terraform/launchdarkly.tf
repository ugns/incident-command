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

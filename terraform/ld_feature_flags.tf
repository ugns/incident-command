# Feature Flag: show-agency-resources
resource "launchdarkly_feature_flag" "show_agency_resources" {
  project_key    = launchdarkly_project.incident_cmd.key
  key            = "show-agency-resources"
  name           = "Show Agency Resources"
  description    = "Controls visibility of agency resources."
  tags           = ["features", "agencies", "resources", "managed-by-terraform"]
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

# Feature Flag: show-radio-resources
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

# Feature Flag: show-radio-resources
resource "launchdarkly_feature_flag" "show_assignment_board" {
  project_key    = launchdarkly_project.incident_cmd.key
  key            = "show-assignment-board"
  name           = "Show Assignment Board"
  description    = "Controls visibility of the assignment board."
  tags           = ["features", "assignments", "boards", "managed-by-terraform"]
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

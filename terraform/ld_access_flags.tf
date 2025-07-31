# Feature Flag: super-admin-access
resource "launchdarkly_feature_flag" "super_admin_access" {
  project_key    = launchdarkly_project.incident_cmd.key
  key            = "super-admin-access"
  name           = "Super Admin Access"
  description    = "Controls super admin access for users via feature flag."
  tags           = ["access", "super", "admin", "managed-by-terraform"]
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

# Feature Flag: dispatch-access
resource "launchdarkly_feature_flag" "dispatch_access" {
  project_key    = launchdarkly_project.incident_cmd.key
  key            = "dispatch-access"
  name           = "Dispatch Access"
  description    = "Controls AssignmentBoard dispatch access for users via feature flag."
  tags           = ["access", "dispatch", "assignment-board", "managed-by-terraform"]
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

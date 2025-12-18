terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "6.27.0"
    }
    launchdarkly = {
      source  = "launchdarkly/launchdarkly"
      version = "2.26.0-beta.1"
    }
  }
  required_version = ">= 1.0"
}

provider "aws" {
  region = "us-east-1"
  assume_role {
    role_arn = var.gh_action_role
  }
}

provider "launchdarkly" {
  access_token = var.launchdarkly_access_token
}

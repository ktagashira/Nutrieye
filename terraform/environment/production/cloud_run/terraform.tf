terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 5.7.0"
    }

    google-beta = {
      source  = "hashicorp/google-beta"
      version = ">= 5.7.0"
    }
  }

  cloud {
    organization = "Nutrieye"

    workspaces {
      name = "nutrieye-google-cloud-run"
    }
  }
}

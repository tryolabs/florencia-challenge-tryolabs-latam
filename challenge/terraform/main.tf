provider "google" {
  project = var.project_id
  region  = var.region
}

resource "google_cloud_run_service" "latam_challenge_service" {
  name     = "latam-challenge"
  location = var.region

  template {
    spec {
      containers {
        image = var.image_url

        ports {
          container_port = 8000
        }
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}

resource "google_cloud_run_service_iam_policy" "noauth" {
  location    = google_cloud_run_service.latam_challenge_service.location
  project     = google_cloud_run_service.latam_challenge_service.project
  service     = google_cloud_run_service.latam_challenge_service.name

  policy_data = data.google_iam_policy.noauth.policy_data
}

data "google_iam_policy" "noauth" {
  binding {
    role = "roles/run.invoker"

    members = [
      "allUsers",
    ]
  }
}

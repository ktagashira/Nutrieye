resource "google_cloud_run_v2_service" "cloud_run__nutrieye" {
  name     = "nutrieye"
  location = "asia-northeast1"
  template {
    containers {
      args       = []
      command    = []
      depends_on = []
      image      = "asia-northeast1-docker.pkg.dev/nutrieye/nutrieye/nutrieye:latest"
      name       = "nutrieye"
      env {
        name = "LINE_CHANNEL_ACCESS_TOKEN"
        value_source {
          secret_key_ref {
            secret  = "LINE_CHANNEL_ACCESS_TOKEN"
            version = "latest"
          }
        }
      }
      env {
        name = "LINE_CHANNEL_SECRET"
        value_source {
          secret_key_ref {
            secret  = "LINE_CHANNEL_SECRET"
            version = "latest"
          }
        }
      }
      ports {
        container_port = 8080
        name           = "http1"
      }
      resources {
        cpu_idle = true
        limits = {
          cpu    = "1000m"
          memory = "512Mi"
        }
        startup_cpu_boost = true
      }
      startup_probe {
        failure_threshold     = 1
        initial_delay_seconds = 0
        period_seconds        = 240
        timeout_seconds       = 240
        tcp_socket {
          port = 8080
        }
      }
    }
  }
}

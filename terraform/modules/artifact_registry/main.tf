resource "google_artifact_registry_repository" "nutrieye" {
  repository_id          = "nutrieye"
  format                 = "DOCKER"
  cleanup_policy_dry_run = true
  docker_config {
    immutable_tags = false
  }
}

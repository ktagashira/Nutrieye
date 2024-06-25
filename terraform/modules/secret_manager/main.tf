resource "google_secret_manager_secret" "line_channel_access_token" {
  secret_id = "LINE_CHANNEL_ACCESS_TOKEN"
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret" "line_channel_secret" {
  secret_id = "LINE_CHANNEL_SECRET"
  replication {
    auto {}
  }
}

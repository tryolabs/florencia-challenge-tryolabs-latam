variable "project_id" {
  description = "The ID of the project to deploy to"
  type        = string
  default     = "florencia-tryolabs-latam"
}

variable "region" {
  description = "The region to deploy to"
  type        = string
  default     = "us-central1"
}

variable "image_url" {
  description = "The URL of the Docker image in GCR"
  type        = string
  default     = "us-docker.pkg.dev/florencia-tryolabs-latam/florencia-repo-latam-challenge/latam-challenge"
}

variable "bucket_name" {
  description = "Bucket to save model"
  type        = string
  default     = "latam-model-challenge"
}

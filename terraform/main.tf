terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0.2"
    }
  }
}

provider "docker" {}

resource "docker_image" "fastapi_image" {
  name = var.image_name

  build {
    context = "../app"
  }
}

resource "docker_container" "fastapi_container" {
  name  = var.container_name
  image = docker_image.fastapi_image.image_id

  ports {
    internal = 8000
    external = 8000
  }
}
output "container_name" {
  value = docker_container.fastapi_container.name
}

output "image_name" {
  value = docker_image.fastapi_image.name
}
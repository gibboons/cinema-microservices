output "alb_dns_name" {
  description = "Publiczny DNS Application Load Balancera"
  value       = aws_lb.main.dns_name
}

output "api_endpoints" {
  description = "Endpointy REST API mikroserwisów przez ALB"
  value = {
    film_upload = "http://${aws_lb.main.dns_name}/films"
    reviews     = "http://${aws_lb.main.dns_name}/reviews"
    ratings     = "http://${aws_lb.main.dns_name}/ratings"
    recommendations = "http://${aws_lb.main.dns_name}/recommendations"
  }
}

output "swagger_urls" {
  description = "Adresy Swagger UI dostępne po deploymencie"
  value = {
    film_upload = "http://${aws_lb.main.dns_name}/films/../docs"
    review      = "http://${aws_lb.main.dns_name}/reviews/../docs"
    rating      = "http://${aws_lb.main.dns_name}/ratings/../docs"
  }
}

output "ecs_cluster_name" {
  value = aws_ecs_cluster.main.name
}

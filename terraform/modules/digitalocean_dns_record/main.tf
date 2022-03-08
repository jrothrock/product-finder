terraform {
  required_providers {
    digitalocean = {
      source = "digitalocean/digitalocean"
      version = "~> 2.17.1"
    }
  }
}

# Add an A record to the domain for www.example.com.
resource "digitalocean_record" "www" {
  domain = "jackrothrock.com"
  type   = "A"
  name   = var.subdomain_name
  value  = var.droplet_ipv4
}


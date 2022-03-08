output "droplet_id" {
  value = digitalocean_droplet.finder.id
}

output "droplet_ipv4" {
  value = digitalocean_droplet.finder.ipv4_address
}

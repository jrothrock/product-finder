terraform {
  required_providers {
    digitalocean = {
      source = "digitalocean/digitalocean"
      version = "~> 2.17.1"
    }
  }
}

resource "digitalocean_droplet" "finder" {
  image  = "ubuntu-18-04-x64"
  name   = var.droplet_name
  region = "sfo1"
  size   = "s-1vcpu-1gb"
  ssh_keys = var.ssh_keys
  ipv6 = true
  user_data = file("{path.root}/../../production/provision.sh")
}

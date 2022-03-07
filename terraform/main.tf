terraform {
  required_providers {
    digitalocean = {
      source = "digitalocean/digitalocean"
      version = "~> 2.17.1"
    }
  }
}

module "ssh_key" {
  source = "./modules/ssh_key"
}

module "droplet" {
  source = "./modules/droplet"

  droplet_name = var.droplet_name
  ssh_keys = [module.ssh_key.fingerprint]
}

module "firewall" {
  source = "./modules/firewall"

  firewall_name = var.firewall_name
  droplet_ids = [module.droplet.droplet_id]
}
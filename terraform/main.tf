terraform {
  required_providers {
    digitalocean = {
      source = "digitalocean/digitalocean"
      version = "~> 2.17.1"
    }
  }
}

module "digitalocean_ssh_key" {
  source = "./modules/digitalocean_ssh_keys"
}

module "digitalocean_droplet" {
  source = "./modules/digitalocean_droplet"

  droplet_name = var.droplet_name
  ssh_keys = [module.digitalocean_ssh_key.personal_fingerprint, module.digitalocean_ssh_key.deploy_fingerprint]
}

module "digitalocean_firewall" {
  source = "./modules/digitalocean_firewall"

  firewall_name = var.firewall_name
  droplet_ids = [module.digitalocean_droplet.droplet_id]
}

module "digitalocean_dns_record" {
  source = "./modules/digitalocean_dns_record"

  droplet_ipv4 = module.digitalocean_droplet.droplet_ipv4
  subdomain_name = var.subdomain_name
}

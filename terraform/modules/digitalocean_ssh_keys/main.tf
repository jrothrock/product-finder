terraform {
  required_providers {
    digitalocean = {
      source = "digitalocean/digitalocean"
      version = "~> 2.17.1"
    }
  }
}

resource "digitalocean_ssh_key" "personal_finder" {
  name       = "Finder Personal SSH Key"
  public_key = file("/Users/jackrothrock/.ssh/finder.pub")
}

resource "digitalocean_ssh_key" "deploy_finder" {
  name       = "Finder Deploy SSH Key"
  public_key = file("/Users/jackrothrock/.ssh/finder.deploy.pub")
}
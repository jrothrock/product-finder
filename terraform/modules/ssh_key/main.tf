terraform {
  required_providers {
    digitalocean = {
      source = "digitalocean/digitalocean"
      version = "~> 2.17.1"
    }
  }
}

resource "digitalocean_ssh_key" "finder" {
  name       = "Finder SSH Key"
  public_key = file("/Users/jackrothrock/.ssh/finder.pub")
}

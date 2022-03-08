output "personal_fingerprint" {
  value = digitalocean_ssh_key.personal_finder.fingerprint
}

output "deploy_fingerprint" {
  value = digitalocean_ssh_key.deploy_finder.fingerprint
}

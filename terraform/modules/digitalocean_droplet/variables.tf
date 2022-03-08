variable "ssh_keys" {
  type    = list
  description = "List of ssh_keys to apply to the droplet."
}

variable "droplet_name" {
  type = string
  description = "Name for the droplet."
}

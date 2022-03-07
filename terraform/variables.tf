# Set the variable value in *.tfvars file
# or using -var="do_token=..." CLI option
variable "do_token" {
  type = string
  description = "Your private DO token."
}

variable "droplet_name" {
  type = string
  description = "Name for the droplet."
}

variable "firewall_name" {
  type = string
  description = "Name for the firewall."
}
